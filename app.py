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

# --- FUNCIÓN PARA CARGAR DATOS (NIVEL TÉCNICO) ---
def cargar_datos(nombre):
    try:
        # Intentamos leer la hoja por nombre
        return conn.read(worksheet=nombre, ttl=0)
    except Exception as e:
        return None

# --- 1. PANTALLAS ---
if choice == "🔍 Consultar Pantallas":
    st.header("Buscador de Compatibilidades")
    df = cargar_datos("Pantallas")
    
    if df is not None:
        df = df.dropna(how='all')
        busqueda = st.text_input("Buscar modelo...")
        if busqueda:
            mask = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
            st.dataframe(df[mask], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.error("No se pudo cargar la hoja 'Pantallas'.")

# --- 2. AGREGAR PANTALLA ---
elif choice == "➕ Agregar Nueva":
    st.header("Registrar Nueva")
    with st.form("f1"):
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo Base")
        compat = st.text_input("Compatibles")
        notas = st.text_area("Notas")
        if st.form_submit_button("Guardar"):
            df_act = cargar_datos("Pantallas")
            nuevo = pd.DataFrame([{"Marca": marca, "Modelo": modelo, "Compatibles": compat, "Notas": notas}])
            updated = pd.concat([df_act, nuevo], ignore_index=True)
            conn.update(worksheet="Pantallas", data=updated)
            st.success("Guardado.")

# --- 3. HUESARIO (SISTEMA DE DIAGNÓSTICO) ---
elif choice == "🦴 Huesario / Partes":
    st.header("Inventario de Partes")
    
    df_h = cargar_datos("Huesario")
    
    if df_h is not None:
        st.dataframe(df_h, use_container_width=True, hide_index=True)
    else:
        st.error("⚠️ Error técnico: La hoja 'Huesario' no responde.")
        st.info("💡 **Monkey Fix Tips para solucionar esto:**")
        st.write("1. **Escribe algo en el Excel:** Google a veces no entrega hojas que están vacías. Escribe un modelo de prueba en la segunda hoja.")
        st.write("2. **Revisa el nombre:** Asegúrate que no tenga un espacio al final: 'Huesario ' vs 'Huesario'.")
        st.write("3. **El Secreto:** Ve a Streamlit Cloud > Settings > Secrets y asegúrate de que el link NO termine en `#gid=...`. Debe terminar en `/edit?usp=sharing`.")
