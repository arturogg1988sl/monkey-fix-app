import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="Monkey Fix System", page_icon="🐒", layout="wide")

# CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    st.image("monkey_logo.png", width=150)
except:
    st.title("🐒 MONKEY FIX / CELULARES 653")

menu = ["🔍 Consultar Pantallas", "➕ Agregar Nueva", "🦴 Huesario"]
choice = st.sidebar.radio("Menú", menu)

# --- SECCIÓN 1: PANTALLAS ---
if choice == "🔍 Consultar Pantallas":
    st.header("Buscador de Pantallas")
    try:
        # Intento de lectura robusta
        df = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Pantallas", ttl=0)
        df = df.dropna(how='all')
        bus = st.text_input("Modelo:")
        if bus:
            mask = df.apply(lambda row: row.astype(str).str.contains(bus, case=False).any(), axis=1)
            st.dataframe(df[mask], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error en Pantallas: Revisa que la pestaña se llame 'Pantallas'")

# --- SECCIÓN 2: AGREGAR PANTALLA ---
elif choice == "➕ Agregar Nueva":
    st.header("Registrar Nueva")
    with st.form("f1"):
        marca, modelo, comp, notas = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("Compatibles"), st.text_area("Notas")
        if st.form_submit_button("Guardar"):
            if marca and modelo:
                df_act = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Pantallas", ttl=0)
                nuevo = pd.DataFrame([{"Marca": marca, "Modelo": modelo, "Compatibles": comp, "Notas": notas}])
                df_final = pd.concat([df_act, nuevo], ignore_index=True)
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Pantallas", data=df_final)
                st.success("✅ Guardado.")
            else:
                st.error("Faltan datos.")

# --- SECCIÓN 3: HUESARIO ---
elif choice == "🦴 Huesario":
    st.header("Inventario de Huesario")
    try:
        # LLAMADA CLAVE: Usamos el URL y el nombre exacto
        df_h = conn.read(spreadsheet=st.secrets["links"]["huesario"], worksheet="Huesario", ttl=0)
        df_h = df_h.dropna(how='all')
        
        t1, t2 = st.tabs(["📋 Ver", "✍️ Registrar"])
        with t1: st.dataframe(df_h, use_container_width=True, hide_index=True)
        with t2:
            with st.form("f2"):
                m, mo, id_v = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("ID")
                if st.form_submit_button("Agregar"):
                    fecha = datetime.now().strftime("%d/%m/%Y")
                    nueva_f = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_v, "Historial": f"[{fecha}] Ingreso."}])
                    df_final_h = pd.concat([df_h, nueva_f], ignore_index=True)
                    conn.update(spreadsheet=st.secrets["links"]["huesario"], worksheet="Huesario", data=df_final_h)
                    st.success("✅ Registrado.")
                    st.rerun()
    except Exception as e:
        st.error("Error 400: Google no reconoce la pestaña 'Huesario'.")
        st.info("💡 **Solución rápida:** Asegúrate que en tu Excel la pestaña de abajo se llame exactamente 'Huesario' (sin espacios al final).")
