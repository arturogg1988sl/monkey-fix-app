import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Monkey Fix - Admin", layout="wide")

# CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🐒 Sistema Monkey Fix")

menu = ["🔍 Stock Pantallas", "➕ Registrar", "🦴 Huesario"]
choice = st.sidebar.radio("Menú", menu)

# --- FUNCIÓN PARA CARGAR DATOS SIN ERRORES ---
def cargar_datos(nombre_pestaña):
    try:
        # Intentamos leer la pestaña por nombre
        return conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet=nombre_pestaña, ttl=0)
    except Exception as e:
        st.error(f"❌ No se encontró la pestaña: '{nombre_pestaña}'")
        st.info("Revisa que en tu Excel el nombre sea EXACTO (sin espacios).")
        return None

# --- 1. STOCK PANTALLAS ---
if choice == "🔍 Stock Pantallas":
    df = cargar_datos("Stock")
    if df is not None:
        df = df.dropna(how='all')
        bus = st.text_input("Buscar modelo:")
        if bus:
            mask = df.apply(lambda row: row.astype(str).str.contains(bus, case=False).any(), axis=1)
            st.dataframe(df[mask], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

# --- 2. REGISTRAR PANTALLA ---
elif choice == "➕ Registrar":
    st.subheader("Nuevo Ingreso a Stock")
    with st.form("f1"):
        marca, modelo, comp, notas = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("Compatibles"), st.text_area("Notas")
        if st.form_submit_button("Guardar"):
            df_act = cargar_datos("Stock")
            if df_act is not None:
                nuevo = pd.DataFrame([{"Marca": marca, "Modelo": modelo, "Compatibles": comp, "Notas": notas}])
                df_final = pd.concat([df_act, nuevo], ignore_index=True)
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", data=df_final)
                st.success("¡Guardado!")

# --- 3. HUESARIO ---
elif choice == "🦴 Huesario":
    st.subheader("Control de Huesario")
    df_h = cargar_datos("Partes")
    
    if df_h is not None:
        df_h = df_h.dropna(how='all')
        t1, t2 = st.tabs(["📋 Ver Partes", "➕ Agregar Hueso"])
        
        with t1:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
        
        with t2:
            with st.form("f2"):
                m, mo, id_v = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("ID")
                if st.form_submit_button("Registrar Hueso"):
                    fecha = datetime.now().strftime("%d/%m/%Y")
                    nueva_f = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_v, "Historial": f"[{fecha}] Ingreso."}])
                    df_final_h = pd.concat([df_h, nueva_f], ignore_index=True)
                    conn.update(spreadsheet=st.secrets["links"]["huesario"], worksheet="Partes", data=df_final_h)
                    st.success("✅ Hueso registrado.")
                    st.rerun()
