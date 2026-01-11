import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Monkey Fix System", page_icon="🐒", layout="wide")

# 2. Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Logo y Título
try:
    st.image("monkey_logo.png", width=150)
except:
    st.title("🐒 MONKEY FIX / CELULARES 653")

# 4. Menú de Navegación (Sidebar)
menu = ["🔍 Consultar Pantallas", "➕ Agregar Nueva", "🦴 Huesario"]
choice = st.sidebar.radio("Menú Principal", menu)

# --- SECCIÓN 1: CONSULTA DE PANTALLAS ---
if choice == "🔍 Consultar Pantallas":
    st.header("Buscador de Compatibilidades")
    try:
        # Usa el link de pantallas de tus Secrets
        df = conn.read(spreadsheet=st.secrets["links"]["pantallas"], ttl=0)
        df = df.dropna(how='all')
        
        busqueda = st.text_input("Escribe el modelo que buscas:")
        if busqueda:
            mask = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
            st.dataframe(df[mask], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error al cargar Pantallas: {e}")

# --- SECCIÓN 2: AGREGAR NUEVA PANTALLA ---
elif choice == "➕ Agregar Nueva":
    st.header("Registrar Nueva Compatibilidad")
    with st.form("f_pantalla"):
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo Base")
        comp = st.text_input("Modelos Compatibles")
        notas = st.text_area("Notas Técnicas")
        
        if st.form_submit_button("Guardar en la Nube"):
            if marca and modelo:
                df_act = conn.read(spreadsheet=st.secrets["links"]["pantallas"], ttl=0)
                nuevo = pd.DataFrame([{"Marca": marca, "Modelo": modelo, "Compatibles": comp, "Notas": notas}])
                df_final = pd.concat([df_act, nuevo], ignore_index=True)
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], data=df_final)
                st.success("¡Guardado correctamente!")
            else:
                st.error("Marca y Modelo son obligatorios.")

# --- SECCIÓN 3: HUESARIO ---
elif choice == "🦴 Huesario":
    st.header("Inventario de Huesario")
    try:
        # Usa el link de huesario de tus Secrets (el que termina en gid=...)
        df_h = conn.read(spreadsheet=st.secrets["links"]["huesario"], ttl=0)
        df_h = df_h.dropna(how='all')
        
        tab_v, tab_r = st.tabs(["📋 Ver Inventario", "✍️ Registrar"])
        
        with tab_v:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
            
        with tab_r:
            with st.form("f_hueso"):
                m = st.text_input("Marca")
                mo = st.text_input("Modelo")
                id_e = st.text_input("ID / Color / Detalle")
                if st.form_submit_button("Agregar al Huesario"):
                    if m and mo:
                        fecha = datetime.now().strftime("%d/%m/%Y")
                        nueva_fila = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_e, "Historial": f"[{fecha}] Ingreso."}])
                        df_final_h = pd.concat([df_h, nueva_fila], ignore_index=True)
                        conn.update(spreadsheet=st.secrets["links"]["huesario"], data=df_final_h)
                        st.success("Registrado en el Huesario.")
                        st.rerun()
                    else:
                        st.error("Marca y Modelo son obligatorios.")
    except Exception as e:
        st.error("Hubo un problema con la hoja de Huesario.")
        st.info(f"🔍 Error Técnico: {e}")
