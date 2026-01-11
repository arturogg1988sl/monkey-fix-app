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

# --- 1. CONSULTA ---
if choice == "🔍 Consultar Pantallas":
    st.header("Buscador de Compatibilidades")
    try:
        # Cargamos los datos. Si falla el nombre 'Pantallas', intenta cargar la primera hoja
        df = conn.read(worksheet="Pantallas", ttl=0)
        
        busqueda = st.text_input("Ingresa modelo a buscar:", placeholder="Ejemplo: iPhone 11, G8 Power...")
        
        if busqueda:
            # Filtro que busca en todas las columnas
            mask = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
            resultado = df[mask]
            if not resultado.empty:
                st.success(f"Se encontraron {len(resultado)} resultados")
                st.dataframe(resultado, use_container_width=True, hide_index=True)
            else:
                st.warning("No tenemos ese modelo registrado todavía.")
        else:
            st.info("Escribe arriba para buscar. Aquí tienes la lista completa:")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
    except Exception as e:
        st.error("Error: No se pudo encontrar la pestaña 'Pantallas'.")
        st.info("Revisa que en tu Google Sheets la pestaña de abajo se llame exactamente: Pantallas")

# --- 2. AGREGAR ---
elif choice == "➕ Agregar Nueva":
    st.header("Registrar Compatibilidad")
    st.write("Completa los datos para alimentar la base de datos de San Luis Río Colorado.")
    
    with st.form("form_registro"):
        col1, col2 = st.columns(2)
        marca = col1.text_input("Marca (Ej: Samsung)")
        modelo = col2.text_input("Modelo Base (Ej: A10)")
        compat = st.text_input("Modelos que usan la misma pantalla (Separa con comas)")
        notas = st.text_area("Observaciones (Ej: Versión de 30 o 40 pines)")
        
        if st.form_submit_button("Guardar en la Nube"):
            if marca and modelo:
                # Obtenemos datos actuales, añadimos el nuevo y subimos
                df_actual = conn.read(worksheet="Pantallas", ttl=0)
                nuevo_registro = pd.DataFrame([{"Marca": marca, "Modelo": modelo, "Compatibles": compat, "Notas": notas}])
                df_final = pd.concat([df_actual, nuevo_registro], ignore_index=True)
                
                conn.update(worksheet="Pantallas", data=df_final)
                st.success(f"¡{modelo} guardado exitosamente!")
            else:
                st.error("La Marca y el Modelo son obligatorios.")

# --- 3. HUESARIO ---
elif choice == "🦴 Huesario / Partes":
    st.header("Inventario de Partes (Huesario)")
    try:
        df_h = conn.read(worksheet="Huesario", ttl=0)
        
        opcion_h = st.radio("Acción:", ["Ver Inventario", "Registrar Nuevo Hueso"], horizontal=True)
        
        if opcion_h == "Registrar Nuevo Hueso":
            with st.form("hueso_nuevo"):
                m, mo, id_e = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("Color o ID")
                if st.form_submit_button("Agregar al Huesario"):
                    fecha = datetime.now().strftime("%d/%m/%Y")
                    fila = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_e, "Historial": f"[{fecha}] Ingreso."}])
                    conn.update(worksheet="Huesario", data=pd.concat([df_h, fila], ignore_index=True))
                    st.success("Registrado.")
        else:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
            st.info("Para editar el historial, puedes hacerlo directamente en el archivo de Google Sheets.")
            
    except:
        st.error("Crea una pestaña llamada 'Huesario' en tu Google Sheets para usar esta función.")
