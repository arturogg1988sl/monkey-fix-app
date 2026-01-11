import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="Monkey Fix System", page_icon="🐒", layout="wide")

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGO ---
try:
    logo = Image.open("monkey_logo.png")
    st.image(logo, width=150)
except:
    st.title("🐒 MONKEY FIX / CELULARES 653")

# --- MENÚ ---
menu = ["🔍 Consultar Pantallas", "➕ Agregar Nueva", "🦴 Huesario / Partes"]
choice = st.sidebar.radio("Menú", menu)

# --- 1. PANTALLAS ---
if choice == "🔍 Consultar Pantallas":
    st.header("Buscador de Compatibilidades")
    try:
        # Leemos la primera hoja sin importar el nombre
        df = conn.read(ttl=0) 
        df = df.dropna(how='all')
        busqueda = st.text_input("Buscar modelo...")
        if busqueda:
            mask = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
            st.dataframe(df[mask], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error al conectar con Google: {e}")

# --- 2. AGREGAR PANTALLA ---
elif choice == "➕ Agregar Nueva":
    st.header("Registrar Nueva")
    with st.form("f1"):
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo Base")
        compat = st.text_input("Compatibles")
        notas = st.text_area("Notas")
        if st.form_submit_button("Guardar"):
            if marca and modelo:
                df_act = conn.read(ttl=0)
                nuevo = pd.DataFrame([{"Marca": marca, "Modelo": modelo, "Compatibles": compat, "Notas": notas}])
                updated = pd.concat([df_act, nuevo], ignore_index=True)
                conn.update(data=updated) # Actualiza la primera hoja por defecto
                st.success("Guardado en la nube.")
            else:
                st.warning("Marca y Modelo obligatorios.")

# --- 3. HUESARIO (CON AUTO-DETECCIÓN) ---
elif choice == "🦴 Huesario / Partes":
    st.header("Inventario de Partes")
    
    try:
        # TRUCO MAESTRO: Intentamos forzar la lectura de la hoja "Huesario"
        # Si falla, el bloque 'except' nos dirá qué está pasando.
        df_h = conn.read(worksheet="Huesario", ttl=0)
        
        if df_h is not None:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
            
            with st.expander("➕ Registrar nuevo en Huesario"):
                with st.form("h2"):
                    m, mo, id_e = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("ID")
                    if st.form_submit_button("Agregar"):
                        fecha = datetime.now().strftime("%d/%m/%Y")
                        nueva_fila = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_e, "Historial": f"[{fecha}] Ingreso."}])
                        df_updated = pd.concat([df_h, nueva_fila], ignore_index=True)
                        conn.update(worksheet="Huesario", data=df_updated)
                        st.success("Agregado al Huesario.")
        
    except Exception as e:
        st.error("No se pudo acceder a la pestaña 'Huesario'.")
        st.info("🔎 **Diagnóstico para Monkey Fix:**")
        st.write("Google Sheets envió este error: ", e)
        st.write("---")
        st.warning("⚠️ **Casi siempre es el link de los Secrets.**")
        st.write("Asegúrate de que el link en Streamlit Cloud > Settings > Secrets sea el link de **COMPARTIR** (el que obtienes al darle al botón azul en Google Sheets) y que NO tenga el `#gid=0` al final.")
