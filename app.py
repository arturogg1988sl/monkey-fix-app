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
    st.image("monkey_logo.png", width=150)
except:
    st.title("🐒 MONKEY FIX / CELULARES 653")

# --- MENÚ ---
menu = ["🔍 Consultar Pantallas", "➕ Agregar Nueva", "🦴 Huesario"]
choice = st.sidebar.radio("Menú Principal", menu)

# --- 1. CONSULTAR PANTALLAS ---
if choice == "🔍 Consultar Pantallas":
    st.header("Buscador de Compatibilidades")
    try:
        # Lee directamente el link de pantallas
        df = conn.read(spreadsheet=st.secrets["links"]["pantallas"], ttl=0)
        df = df.dropna(how='all')
        
        busqueda = st.text_input("Ingresa modelo:")
        if busqueda:
            mask = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
            st.dataframe(df[mask], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error al cargar Pantallas: {e}")

# --- 2. AGREGAR PANTALLA ---
elif choice == "➕ Agregar Nueva":
    st.header("Registrar Nueva")
    with st.form("f1"):
        marca, modelo, comp, notas = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("Compatibles"), st.text_area("Notas")
        if st.form_submit_button("Guardar"):
            if marca and modelo:
                df_act = conn.read(spreadsheet=st.secrets["links"]["pantallas"], ttl=0)
                nuevo = pd.DataFrame([{"Marca": marca, "Modelo": modelo, "Compatibles": comp, "Notas": notas}])
                df_final = pd.concat([df_act, nuevo], ignore_index=True)
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], data=df_final)
                st.success("Guardado en la nube.")
            else:
                st.error("Datos incompletos.")

# --- 3. HUESARIO ---
elif choice == "🦴 Huesario":
    st.header("Inventario de Huesario")
    try:
        # Lee directamente el link de huesario (con su propio gid)
        df_h = conn.read(spreadsheet=st.secrets["links"]["huesario"], ttl=0)
        df_h = df_h.dropna(how='all')
        
        tab1, tab2 = st.tabs(["📋 Ver Inventario", "✍️ Registrar Equipo"])
        with tab1:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
        with tab2:
            with st.form("f2"):
                m, mo, id_e = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("ID/Color")
                if st.form_submit_button("Agregar"):
                    if m and mo:
                        fecha = datetime.now().strftime("%d/%m/%Y")
                        nueva_f = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_e, "Historial": f"[{fecha}] Ingreso."}])
                        # Es vital que los nombres Marca, Modelo, ID coincidan con tu Excel
                        df_final_h = pd.concat([df_h, nueva_f], ignore_index=True)
                        conn.update(spreadsheet=st.secrets["links"]["huesario"], data=df_final_h)
                        st.success("Registrado correctamente.")
                        st.rerun()
    except Exception as e:
        st.error(f"Error en Huesario: {e}")
