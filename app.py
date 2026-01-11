import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Monkey Fix - Sistema Técnico", page_icon="🐒", layout="wide")

# 2. Conexión Profesional (Usa la Service Account de tus Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Logo y Título
try:
    st.image("monkey_logo.png", width=150)
except:
    st.title("🐒 MONKEY FIX / CELULARES 653")
st.write(f"Sistemas de Control de Inventario - San Luis Río Colorado")

# 4. Menú de Navegación Lateral
menu = ["🔍 Consultar Pantallas", "➕ Agregar Nueva", "🦴 Huesario"]
choice = st.sidebar.radio("Panel de Control", menu)

# --- SECCIÓN 1: CONSULTAR PANTALLAS ---
if choice == "🔍 Consultar Pantallas":
    st.header("Buscador de Compatibilidades")
    try:
        # Lee la pestaña "Pantallas" usando el ID de los Secrets
        df = conn.read(
            spreadsheet=st.secrets["links"]["pantallas"], 
            worksheet="Pantallas", 
            ttl=0
        )
        df = df.dropna(how='all')
        
        busqueda = st.text_input("Ingresa modelo a buscar:", placeholder="Ejemplo: iPhone 11, G8 Power...")
        
        if busqueda:
            # Filtro inteligente en todas las columnas
            mask = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
            resultado = df[mask]
            if not resultado.empty:
                st.success(f"Se encontraron {len(resultado)} resultados")
                st.dataframe(resultado, use_container_width=True, hide_index=True)
            else:
                st.warning("No tenemos ese modelo registrado todavía.")
        else:
            st.info("Lista completa de pantallas:")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")

# --- SECCIÓN 2: AGREGAR PANTALLA ---
elif choice == "➕ Agregar Nueva":
    st.header("Registrar Nueva Compatibilidad")
    
    with st.form("form_pantalla"):
        col1, col2 = st.columns(2)
        marca = col1.text_input("Marca (Ej: Samsung)")
        modelo = col2.text_input("Modelo Base (Ej: A10)")
        compat = st.text_input("Modelos que usan la misma pantalla")
        notas = st.text_area("Observaciones Técnicas")
        
        if st.form_submit_button("Guardar en la Nube"):
            if marca and modelo:
                # Obtenemos datos actuales
                df_actual = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Pantallas", ttl=0)
                
                # Creamos el nuevo registro
                nuevo_registro = pd.DataFrame([{"Marca": marca, "Modelo": modelo, "Compatibles": compat, "Notas": notas}])
                
                # Unimos y subimos
                df_final = pd.concat([df_actual, nuevo_registro], ignore_index=True)
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Pantallas", data=df_final)
                
                st.success(f"✅ ¡{modelo} guardado exitosamente en la base de datos!")
            else:
                st.error("⚠️ La Marca y el Modelo son obligatorios.")

# --- SECCIÓN 3: HUESARIO ---
elif choice == "🦴 Huesario":
    st.header("Inventario de Partes (Huesario)")
    try:
        # Lee la pestaña "Huesario" usando el ID de los Secrets
        df_h = conn.read(
            spreadsheet=st.secrets["links"]["huesario"], 
            worksheet="Huesario", 
            ttl=0
        )
        df_h = df_h.dropna(how='all')
        
        tab_ver, tab_reg = st.tabs(["📋 Ver Inventario", "✍️ Registrar Equipo"])
        
        with tab_ver:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
            
        with tab_reg:
            with st.form("form_hueso"):
                m = st.text_input("Marca")
                mo = st.text_input("Modelo")
                # El campo dice ID para coincidir con tu Excel
                id_val = st.text_input("ID") 
                
                if st.form_submit_button("Agregar al Huesario"):
                    if m and mo:
                        fecha = datetime.now().strftime("%d/%m/%Y")
                        nueva_fila = pd.DataFrame([{
                            "Marca": m, 
                            "Modelo": mo, 
                            "ID": id_val, 
                            "Historial": f"[{fecha}] Ingreso al taller."
                        }])
                        
                        df_final_h = pd.concat([df_h, nueva_fila], ignore_index=True)
                        
                        # Actualizamos la pestaña Huesario
                        conn.update(spreadsheet=st.secrets["links"]["huesario"], worksheet="Huesario", data=df_final_h)
                        
                        st.success("✅ Equipo registrado correctamente en el huesario.")
                        st.rerun()
                    else:
                        st.error("⚠️ Marca y Modelo son obligatorios.")
                        
    except Exception as e:
        st.error(f"Error técnico en el Huesario: {e}")
