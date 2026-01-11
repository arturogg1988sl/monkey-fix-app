import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN
st.set_page_config(page_title="Monkey Fix System", page_icon="🐒", layout="wide")

# CONEXIÓN PROFESIONAL
conn = st.connection("gsheets", type=GSheetsConnection)

# LOGO / TÍTULO
try:
    st.image("monkey_logo.png", width=150)
except:
    st.title("🐒 MONKEY FIX / CELULARES 653")

menu = ["🔍 Stock Pantallas", "➕ Registrar Stock", "🦴 Huesario"]
choice = st.sidebar.radio("Panel de Control", menu)

# --- 1. STOCK PANTALLAS (Pestaña 'Stock') ---
if choice == "🔍 Stock Pantallas":
    st.header("Inventario de Pantallas")
    try:
        df = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", ttl=0)
        df = df.dropna(how='all')
        
        bus = st.text_input("Buscar por modelo o marca:")
        if bus:
            mask = df.apply(lambda row: row.astype(str).str.contains(bus, case=False).any(), axis=1)
            st.dataframe(df[mask], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error al cargar Stock: {e}")

# --- 2. REGISTRAR STOCK ---
elif choice == "➕ Registrar Stock":
    st.header("Nuevo Ingreso a Pantallas")
    with st.form("form_stock"):
        ma, mo, co, no = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("Compatibles"), st.text_area("Notas")
        if st.form_submit_button("Guardar en Google Sheets"):
            if ma and mo:
                df_act = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", ttl=0)
                nueva_p = pd.DataFrame([{"Marca": ma, "Modelo": mo, "Compatibles": co, "Notas": no}])
                df_final = pd.concat([df_act, nueva_p], ignore_index=True)
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", data=df_final)
                st.success(f"✅ {mo} agregado correctamente.")
            else:
                st.error("Marca y Modelo son obligatorios.")

# --- 3. HUESARIO (Pestaña 'Partes') ---
elif choice == "🦴 Huesario":
    st.header("Inventario de Huesario")
    try:
        df_h = conn.read(spreadsheet=st.secrets["links"]["huesario"], worksheet="Partes", ttl=0)
        df_h = df_h.dropna(how='all')
        
        t1, t2 = st.tabs(["📋 Ver Inventario", "➕ Registrar Equipo"])
        with t1:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
        with t2:
            with st.form("form_hueso"):
                m, mo, id_v = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("ID")
                if st.form_submit_button("Registrar en Huesario"):
                    if m and mo:
                        fecha = datetime.now().strftime("%d/%m/%Y")
                        nueva_h = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_v, "Historial": f"[{fecha}] Ingreso."}])
                        df_final_h = pd.concat([df_h, nueva_h], ignore_index=True)
                        conn.update(spreadsheet=st.secrets["links"]["huesario"], worksheet="Partes", data=df_final_h)
                        st.success("✅ Registrado en Huesario.")
                        st.rerun()
                    else:
                        st.error("Datos incompletos.")
    except Exception as e:
        st.error(f"Error en Huesario: {e}")
