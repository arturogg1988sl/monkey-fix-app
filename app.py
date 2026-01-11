import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="Monkey Fix System", page_icon="🐒", layout="wide")

# --- LOGO ---
try:
    st.image("monkey_logo.png", width=150)
except:
    st.title("🐒 MONKEY FIX / CELULARES 653")

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVEGACIÓN ---
menu = ["🔍 Consultar Pantallas", "➕ Agregar Nueva", "🦴 Huesario"]
choice = st.sidebar.radio("Menú", menu)

# --- 1. CONSULTA ---
if choice == "🔍 Consultar Pantallas":
    st.header("Buscador de Compatibilidades")
    # Leemos usando el link directo de los Secrets
    df = conn.read(spreadsheet=st.secrets["links"]["pantallas"], ttl=0)
    df = df.dropna(how='all')
    
    busqueda = st.text_input("Escribe el modelo:")
    if busqueda:
        mask = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
        st.dataframe(df[mask], use_container_width=True, hide_index=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 2. AGREGAR ---
elif choice == "➕ Agregar Nueva":
    st.header("Registrar Nueva")
    with st.form("f_add"):
        marca, modelo, comp, notas = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("Compatibles"), st.text_area("Notas")
        if st.form_submit_button("Guardar"):
            df_actual = conn.read(spreadsheet=st.secrets["links"]["pantallas"], ttl=0)
            nuevo = pd.DataFrame([{"Marca": marca, "Modelo": modelo, "Compatibles": comp, "Notas": notas}])
            updated = pd.concat([df_actual, nuevo], ignore_index=True)
            conn.update(spreadsheet=st.secrets["links"]["pantallas"], data=updated)
            st.success("Guardado exitosamente.")

# --- 3. HUESARIO (MÉTODO DIRECTO) ---
elif choice == "🦴 Huesario":
    st.header("Inventario de Huesario")
    try:
        # Usamos el link específico del Huesario que tiene su propio GID
        df_h = conn.read(spreadsheet=st.secrets["links"]["huesario"], ttl=0)
        df_h = df_h.dropna(how='all')
        
        tab_v, tab_r = st.tabs(["📋 Ver Inventario", "✍️ Registrar"])
        
        with tab_v:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
            
        with tab_r:
            with st.form("f_h"):
                m, mo, id_e = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("ID")
                if st.form_submit_button("Agregar"):
                    fecha = datetime.now().strftime("%d/%m/%Y")
                    fila = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_e, "Historial": f"[{fecha}] Ingreso."}])
                    updated_h = pd.concat([df_h, fila], ignore_index=True)
                    conn.update(spreadsheet=st.secrets["links"]["huesario"], data=updated_h)
                    st.success("Hueso registrado.")
    except Exception as e:
        st.error("Error al cargar Huesario. Revisa el link en Secrets.")
