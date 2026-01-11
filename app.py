import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Monkey Fix System", page_icon="🐒", layout="wide")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Intentamos conectar. Si falla el Secreto, esto dará aviso.
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Error de configuración: Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- ENCABEZADO ---
try:
    logo = Image.open("monkey_logo.png")
    st.image(logo, width=150)
except:
    st.title("🐒 MONKEY FIX / CELULARES 653")

# --- MENÚ ---
menu = ["🔍 Consultar", "➕ Agregar Pantalla", "🦴 Huesario"]
choice = st.sidebar.radio("Menú Principal", menu)

# --- 1. CONSULTA ---
if choice == "🔍 Consultar":
    st.header("Buscador de Compatibilidades")
    
    try:
        # ttl=0 (número, no texto) para refrescar siempre los datos
        df = conn.read(worksheet="Pantallas", ttl=0)
        
        busqueda = st.text_input("Escribe el modelo (ej: A10, G8 Power...)", placeholder="Buscar...")
        
        if busqueda:
            mask = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
            resultado = df[mask]
            if not resultado.empty:
                st.dataframe(resultado, use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontró compatibilidad.")
        else:
            st.info("Mostrando base de datos completa:")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
    except Exception as e:
        st.error("No se pudo leer la hoja 'Pantallas'. Verifica que el nombre sea idéntico en Google Sheets.")
        st.info("Detalle técnico: " + str(e))

# --- 2. AGREGAR PANTALLA ---
elif choice == "➕ Agregar Pantalla":
    st.header("Nueva Compatibilidad")
    with st.form("form_pantalla"):
        m = st.text_input("Marca")
        mo = st.text_input("Modelo Base")
        comp = st.text_input("Modelos Compatibles")
        notas = st.text_area("Notas Técnicas")
        
        if st.form_submit_button("Guardar en la Nube"):
            if m and mo:
                try:
                    old_data = conn.read(worksheet="Pantallas", ttl=0)
                    new_row = pd.DataFrame([{"Marca": m, "Modelo": mo, "Compatibles": comp, "Notas": notas}])
                    updated_df = pd.concat([old_data, new_row], ignore_index=True)
                    conn.update(worksheet="Pantallas", data=updated_df)
                    st.success("¡Datos guardados en Google Sheets!")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Marca y Modelo son obligatorios.")

# --- 3. HUESARIO ---
elif choice == "🦴 Huesario":
    st.header("Inventario de Partes")
    try:
        df_h = conn.read(worksheet="Huesario", ttl=0)
        
        tab1, tab2 = st.tabs(["Registrar Entrada", "Ver Historial"])
        
        with tab1:
            with st.form("form_hueso"):
                m, mo, id_eq = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("Color / ID")
                if st.form_submit_button("Registrar"):
                    fecha = datetime.now().strftime("%d/%m/%Y")
                    new_h = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_eq, "Historial": f"[{fecha}] Ingreso."}])
                    updated_h = pd.concat([df_h, new_h], ignore_index=True)
                    conn.update(worksheet="Huesario", data=updated_h)
                    st.success("Registrado.")

        with tab2:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
    except:
        st.error("Asegúrate de tener una pestaña llamada 'Huesario' en tu Excel.")
