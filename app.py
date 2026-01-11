import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
from datetime import datetime

# 1. Configuración de la página (lo primero que ve el navegador)
st.set_page_config(page_title="Monkey Fix System", page_icon="🐒", layout="wide")

# 2. AQUÍ VA LA CONEXIÓN (El "puente" profesional)
# Esta línea le dice a Streamlit que use la Service Account de tus Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Logo y Título
try:
    st.image("monkey_logo.png", width=150)
except:
    st.title("🐒 MONKEY FIX / CELULARES 653")

# 4. Menú de Navegación
menu = ["🔍 Consultar Pantallas", "➕ Agregar Nueva", "🦴 Huesario"]
choice = st.sidebar.radio("Menú Principal", menu)

# --- SECCIÓN 1: CONSULTA ---
if choice == "🔍 Consultar Pantallas":
    st.header("Buscador de Compatibilidades")
    try:
        df = conn.read(spreadsheet=st.secrets["links"]["pantallas"], ttl=0)
        df = df.dropna(how='all')
        bus = st.text_input("Ingresa modelo:")
        if bus:
            mask = df.apply(lambda row: row.astype(str).str.contains(bus, case=False).any(), axis=1)
            st.dataframe(df[mask], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error al cargar: {e}")

# --- SECCIÓN 2: AGREGAR PANTALLA ---
elif choice == "➕ Agregar Nueva":
    st.header("Registrar Nueva Pantalla")
    with st.form("f1"):
        marca, modelo, comp, notas = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("Compatibles"), st.text_area("Notas")
        if st.form_submit_button("Guardar en Google Sheets"):
            if marca and modelo:
                df_act = conn.read(spreadsheet=st.secrets["links"]["pantallas"], ttl=0)
                nuevo = pd.DataFrame([{"Marca": marca, "Modelo": modelo, "Compatibles": comp, "Notas": notas}])
                df_final = pd.concat([df_act, nuevo], ignore_index=True)
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], data=df_final)
                st.success("✅ ¡Guardado en la nube!")
            else:
                st.error("Faltan datos obligatorios.")

# --- SECCIÓN 3: HUESARIO ---
elif choice == "🦴 Huesario":
    st.header("Inventario de Huesario")
    try:
        df_h = conn.read(spreadsheet=st.secrets["links"]["huesario"], ttl=0)
        df_h = df_h.dropna(how='all')
        
        t1, t2 = st.tabs(["📋 Ver Inventario", "✍️ Registrar Equipo"])
        with t1:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
        with t2:
            with st.form("f2"):
                m, mo = st.text_input("Marca"), st.text_input("Modelo")
                # Aquí dice "ID" para que coincida con tu Excel
                id_val = st.text_input("ID") 
                if st.form_submit_button("Agregar al Huesario"):
                    if m and mo:
                        fecha = datetime.now().strftime("%d/%m/%Y")
                        nueva_f = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_val, "Historial": f"[{fecha}] Ingreso."}])
                        df_final_h = pd.concat([df_h, nueva_f], ignore_index=True)
                        conn.update(spreadsheet=st.secrets["links"]["huesario"], data=df_final_h)
                        st.success("✅ Equipo registrado.")
                        st.rerun()
                    else:
                        st.error("Marca y Modelo son obligatorios.")
    except Exception as e:
        st.error(f"Error técnico: {e}")
