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

# --- FUNCIÓN DE LECTURA ROBUSTA ---
def cargar_datos_seguro(nombre_hoja, indice_hoja):
    try:
        # Intento 1: Por nombre exacto
        return conn.read(worksheet=nombre_hoja, ttl=0)
    except:
        try:
            # Intento 2: Por posición (0 es la primera, 1 es la segunda)
            # Nota: Algunas versiones de la librería requieren leer todo y filtrar
            all_sheets = conn.read(ttl=0) 
            return conn.read(worksheet=indice_hoja, ttl=0)
        except:
            return pd.DataFrame() # Devuelve tabla vacía si nada funciona

# --- 1. CONSULTA PANTALLAS ---
if choice == "🔍 Consultar Pantallas":
    st.header("Buscador de Compatibilidades")
    df = cargar_datos_seguro("Pantallas", 0)
    df = df.dropna(how='all')

    busqueda = st.text_input("Ingresa modelo a buscar:", placeholder="Ejemplo: iPhone 11...")
    if busqueda:
        mask = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
        resultado = df[mask]
        st.dataframe(resultado, use_container_width=True, hide_index=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 2. AGREGAR PANTALLA ---
elif choice == "➕ Agregar Nueva":
    st.header("Registrar Compatibilidad")
    with st.form("form_registro"):
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo Base")
        compat = st.text_input("Compatibles")
        notas = st.text_area("Observaciones")
        if st.form_submit_button("Guardar en la Nube"):
            if marca and modelo:
                df_actual = cargar_datos_seguro("Pantallas", 0)
                nuevo = pd.DataFrame([{"Marca": marca, "Modelo": modelo, "Compatibles": compat, "Notas": notas}])
                df_final = pd.concat([df_actual, nuevo], ignore_index=True)
                conn.update(worksheet="Pantallas", data=df_final)
                st.success(f"¡{modelo} guardado!")
            else:
                st.error("Faltan datos.")

# --- 3. HUESARIO (CORREGIDO) ---
elif choice == "🦴 Huesario / Partes":
    st.header("Inventario de Partes (Huesario)")
    
    # Intentamos cargar la segunda pestaña (índice 1)
    df_h = cargar_datos_seguro("Huesario", 1)
    
    if df_h.empty:
        st.warning("⚠️ No se pudieron cargar datos del Huesario.")
        st.info("Asegúrate de que tu Google Sheets tenga una SEGUNDA pestaña con los títulos: Marca, Modelo, ID, Historial.")
    else:
        df_h = df_h.dropna(how='all')
        
        tab_ver, tab_reg = st.tabs(["📋 Ver Inventario", "✍️ Registrar Entrada"])
        
        with tab_ver:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
            
        with tab_reg:
            with st.form("hueso_nuevo"):
                m = st.text_input("Marca")
                mo = st.text_input("Modelo")
                id_e = st.text_input("Color / ID único")
                if st.form_submit_button("Agregar al Huesario"):
                    if m and mo:
                        fecha = datetime.now().strftime("%d/%m/%Y")
                        nueva_fila = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_e, "Historial": f"[{fecha}] Ingreso."}])
                        df_final_h = pd.concat([df_h, nueva_fila], ignore_index=True)
                        conn.update(worksheet="Huesario", data=df_final_h)
                        st.success("Equipo agregado al huesario.")
                        st.rerun()
                    else:
                        st.error("Marca y Modelo son obligatorios.")
