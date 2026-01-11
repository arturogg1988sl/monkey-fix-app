import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Monkey Fix System", page_icon="🐒", layout="wide")

# 2. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. LOGO Y TÍTULO
try:
    st.image("monkey_logo.png", width=150)
except:
    st.title("🐒 MONKEY FIX / CELULARES 653")

# 4. MENÚ LATERAL
menu = ["🔍 Consultar Pantallas", "➕ Agregar Nueva", "🦴 Huesario"]
choice = st.sidebar.radio("Menú Principal", menu)

# --- SECCIÓN 1: CONSULTAR PANTALLAS ---
if choice == "🔍 Consultar Pantallas":
    st.header("Buscador de Compatibilidades")
    try:
        df = conn.read(spreadsheet=st.secrets["links"]["pantallas"], ttl=0)
        df = df.dropna(how='all')
        busqueda = st.text_input("Ingresa modelo a buscar:", placeholder="Ej: A10, iPhone 11...")
        if busqueda:
            mask = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
            st.dataframe(df[mask], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error al cargar Pantallas: {e}")

# --- SECCIÓN 2: AGREGAR PANTALLA ---
elif choice == "➕ Agregar Nueva":
    st.header("Registrar Nueva")
    with st.form("f1"):
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo Base")
        comp = st.text_input("Compatibles")
        notas = st.text_area("Notas")
        if st.form_submit_button("Guardar en la Nube"):
            if marca and modelo:
                df_act = conn.read(spreadsheet=st.secrets["links"]["pantallas"], ttl=0)
                nuevo = pd.DataFrame([{"Marca": marca, "Modelo": modelo, "Compatibles": comp, "Notas": notas}])
                df_final = pd.concat([df_act, nuevo], ignore_index=True)
                # Actualización usando el link del archivo principal
                conn.update(spreadsheet="https://docs.google.com/spreadsheets/d/1Qh7YQO_piMgikZEKY8VNVsMIyudfklLu7D0wKFDz2Fc/edit", worksheet="Pantallas", data=df_final)
                st.success("¡Guardado correctamente!")
            else:
                st.error("Datos incompletos.")

# --- SECCIÓN 3: HUESARIO ---
elif choice == "🦴 Huesario":
    st.header("Inventario de Huesario")
    try:
        # Lee directamente el link de la pestaña Huesario (gid=1412559761)
        df_h = conn.read(spreadsheet=st.secrets["links"]["huesario"], ttl=0)
        df_h = df_h.dropna(how='all')
        
        tab1, tab2 = st.tabs(["📋 Ver Inventario", "✍️ Registrar Equipo"])
        with tab1:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
        with tab2:
            with st.form("f2"):
                m = st.text_input("Marca")
                mo = st.text_input("Modelo")
                # El usuario ve ID/Color, pero en el Excel se guarda como "ID"
                id_e = st.text_input("ID / Color") 
                if st.form_submit_button("Agregar al Huesario"):
                    if m and mo:
                        fecha = datetime.now().strftime("%d/%m/%Y")
                        # Mapeo exacto: "ID" es el nombre de tu columna en Google Sheets
                        nueva_f = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_e, "Historial": f"[{fecha}] Ingreso."}])
                        df_final_h = pd.concat([df_h, nueva_f], ignore_index=True)
                        # Guardar directo en la pestaña Huesario
                        conn.update(spreadsheet="https://docs.google.com/spreadsheets/d/1Qh7YQO_piMgikZEKY8VNVsMIyudfklLu7D0wKFDz2Fc/edit", worksheet="Huesario", data=df_final_h)
                        st.success("✅ Registrado en el Huesario.")
                        st.rerun()
                    else:
                        st.error("⚠️ Marca y Modelo obligatorios.")
    except Exception as e:
        st.error(f"Error técnico: {e}")
