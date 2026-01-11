import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
from datetime import datetime

# Configuración profesional
st.set_page_config(page_title="Monkey Fix - Sistema Técnico", page_icon="🐒", layout="wide")

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGO Y TÍTULO ---
try:
    logo = Image.open("monkey_logo.png")
    st.image(logo, width=150)
except:
    st.title("🐒 MONKEY FIX / CELULARES 653")
st.write("---")

# --- MENÚ LATERAL ---
menu = ["🔍 Consultar Pantallas", "➕ Agregar Nueva", "🦴 Huesario / Partes"]
choice = st.sidebar.radio("Menú de Trabajo", menu)

# --- FUNCIÓN PARA LEER DATOS SIN ERRORES ---
def cargar_datos(nombre_hoja):
    try:
        # Intentamos leer por nombre
        return conn.read(worksheet=nombre_hoja, ttl=0)
    except:
        # Si falla, leemos la primera hoja disponible (índice 0)
        return conn.read(ttl=0)

# --- 1. CONSULTA ---
if choice == "🔍 Consultar Pantallas":
    st.header("Buscador de Compatibilidades")
    
    df = cargar_datos("Pantallas")
    
    # Limpiar filas vacías que Google Sheets suele enviar
    df = df.dropna(how='all')

    busqueda = st.text_input("Ingresa modelo a buscar:", placeholder="Ejemplo: iPhone 11, G8 Power...")
    
    if busqueda:
        mask = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
        resultado = df[mask]
        if not resultado.empty:
            st.success(f"Se encontraron {len(resultado)} resultados")
            st.dataframe(resultado, use_container_width=True, hide_index=True)
        else:
            st.warning("No tenemos ese modelo registrado todavía.")
    else:
        st.info("Lista de compatibilidades actual:")
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 2. AGREGAR ---
elif choice == "➕ Agregar Nueva":
    st.header("Registrar Compatibilidad")
    
    with st.form("form_registro"):
        col1, col2 = st.columns(2)
        marca = col1.text_input("Marca")
        modelo = col2.text_input("Modelo Base")
        compat = st.text_input("Modelos Compatibles")
        notas = st.text_area("Observaciones")
        
        if st.form_submit_button("Guardar en la Nube"):
            if marca and modelo:
                df_actual = cargar_datos("Pantallas")
                nuevo_registro = pd.DataFrame([{"Marca": marca, "Modelo": modelo, "Compatibles": compat, "Notas": notas}])
                df_final = pd.concat([df_actual, nuevo_registro], ignore_index=True)
                
                # Intentamos actualizar
                try:
                    conn.update(worksheet="Pantallas", data=df_final)
                    st.success(f"¡{modelo} guardado exitosamente!")
                except:
                    conn.update(data=df_final) # Intento sin nombre de hoja
                    st.success(f"¡{modelo} guardado en la hoja principal!")
            else:
                st.error("La Marca y el Modelo son obligatorios.")

# --- 3. HUESARIO ---
elif choice == "🦴 Huesario / Partes":
    st.header("Inventario de Partes (Huesario)")
    st.info("Nota: Para el Huesario, usa la segunda pestaña de tu Google Sheets.")
    try:
        df_h = conn.read(worksheet="Huesario", ttl=0)
        st.dataframe(df_h, use_container_width=True, hide_index=True)
    except:
        st.warning("Para usar el Huesario, asegúrate de que sea la segunda pestaña de tu archivo.")
