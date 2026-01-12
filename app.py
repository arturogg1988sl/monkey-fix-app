import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN
st.set_page_config(page_title="Monkey Fix Pro", page_icon="🐒", layout="wide")

# CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

# LOGO / TÍTULO
try:
    st.image("Monkey_logo.png", width=150)
except:
    st.title("🐒 MONKEY FIX / CELULARES 653")

# CAMBIO DE NOMBRE EN EL MENÚ: De 'Stock Pantallas' a 'Compatibilidades'
menu = ["🔍 Compatibilidades", "➕ Registrar/Editar", "🦴 Huesario", "📜 Historial Huesario"]
choice = st.sidebar.radio("Panel de Control", menu)

# --- FUNCIÓN PARA REGISTRAR HISTORIAL ---
def registrar_historial(accion, marca, modelo, detalles):
    try:
        df_hist = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Historial_Huesario", ttl=0)
        nueva_entrada = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Acción": accion,
            "Marca": marca,
            "Modelo": modelo,
            "Detalles": detalles
        }])
        df_final_hist = pd.concat([df_hist, nueva_entrada], ignore_index=True)
        conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Historial_Huesario", data=df_final_hist)
    except:
        st.error("No se pudo actualizar el historial.")

# --- 1. SECCIÓN: COMPATIBILIDADES ---
if choice == "🔍 Compatibilidades":
    st.header("Buscador de Compatibilidades")
    try:
        # Seguimos leyendo la pestaña 'Stock' del Excel, pero el título dice Compatibilidades
        df = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", ttl=0)
        df = df.dropna(how='all')
        bus = st.text_input("Buscar modelo o compatibilidad:")
        if bus:
            mask = df.apply(lambda row: row.astype(str).str.contains(bus, case=False).any(), axis=1)
            st.dataframe(df[mask], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error al cargar compatibilidades: {e}")

# --- 2. REGISTRAR / EDITAR ---
elif choice == "➕ Registrar/Editar":
    tab_reg, tab_edit = st.tabs(["🆕 Registrar Nuevo", "✏️ Editar Existente"])
    
    # Leemos la pestaña 'Stock'
    df_stock = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", ttl=0)

    with tab_reg:
        st.subheader("Agregar Nueva Compatibilidad")
        with st.form("f_reg"):
            ma, mo, co, no = st.text_input("Marca"), st.text_input("Modelo Base"), st.text_input("Compatibles"), st.text_area("Notas")
            if st.form_submit_button("Guardar"):
                nueva_p = pd.DataFrame([{"Marca": ma, "Modelo": mo, "Compatibles": co, "Notas": no}])
                df_final = pd.concat([df_stock, nueva_p], ignore_index=True)
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", data=df_final)
                st.success("Guardado exitosamente")

    with tab_edit:
        st.subheader("Editar Datos de Compatibilidad")
        modelo_editar = st.selectbox("Selecciona equipo", df_stock["Modelo"].unique())
        idx = df_stock[df_stock["Modelo"] == modelo_editar].index[0]
        
        with st.form("f_edit"):
            nueva_ma = st.text_input("Marca", value=df_stock.at[idx, "Marca"])
            nueva_mo = st.text_input("Modelo", value=df_stock.at[idx, "Modelo"])
            nueva_co = st.text_input("Compatibles", value=df_stock.at[idx, "Compatibles"])
            nueva_no = st.text_area("Notas", value=df_stock.at[idx, "Notas"])
            
            col1, col2 = st.columns(2)
            if col1.form_submit_button("Actualizar"):
                df_stock.at[idx, "Marca"] = nueva_ma
                df_stock.at[idx, "Modelo"] = nueva_mo
                df_stock.at[idx, "Compatibles"] = nueva_co
                df_stock.at[idx, "Notas"] = nueva_no
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", data=df_stock)
                st.success("Información actualizada")
            
            if col2.form_submit_button("🚨 Eliminar Registro"):
                df_stock = df_stock.drop(idx)
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", data=df_stock)
                st.warning("Registro eliminado")
                st.rerun()

# --- 3. HUESARIO ---
elif choice == "🦴 Huesario":
    st.header("Gestión de Huesario")
    df_h = conn.read(spreadsheet=st.secrets["links"]["huesario"], worksheet="Partes", ttl=0)
    df_h = df_h.dropna(how='all')
    
    t_ver, t_reg, t_del = st.tabs(["📋 Ver", "➕ Agregar", "🗑️ Eliminar"])
    
    with t_ver:
        st.dataframe(df_h, use_container_width=True, hide_index=True)
    
    with t_reg:
        with st.form("f_h_reg"):
            m, mo, id_v = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("ID")
            if st.form_submit_button("Guardar en Huesario"):
                nueva_h = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_v, "Historial": f"[{datetime.now().strftime('%d/%m/%Y')}] Ingreso."}])
                df_f = pd.concat([df_h, nueva_h], ignore_index=True)
                conn.update(spreadsheet=st.secrets["links"]["huesario"], worksheet="Partes", data=df_f)
                registrar_historial("AGREGAR", m, mo, f"ID: {id_v}")
                st.success("Equipo agregado al Huesario")
                st.rerun()

    with t_del:
        if not df_h.empty:
            equipo_del = st.selectbox("Equipo a retirar", 
                                     df_h.apply(lambda x: f"{x['Marca']} {x['Modelo']} (ID: {x['ID']})", axis=1))
            if st.button("Confirmar Baja"):
                idx_h = df_h[df_h.apply(lambda x: f"{x['Marca']} {x['Modelo']} (ID: {x['ID']})", axis=1) == equipo_del].index[0]
                m_h, mo_h = df_h.at[idx_h, "Marca"], df_h.at[idx_h, "Modelo"]
                
                df_h = df_h.drop(idx_h)
                conn.update(spreadsheet=st.secrets["links"]["huesario"], worksheet="Partes", data=df_h)
                registrar_historial("ELIMINAR", m_h, mo_h, "Retirado del inventario")
                st.error("Equipo eliminado del inventario")
                st.rerun()

# --- 4. HISTORIAL ---
elif choice == "📜 Historial Huesario":
    st.header("Registro de Movimientos")
    try:
        df_hist = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Historial_Huesario", ttl=0)
        st.dataframe(df_hist.sort_index(ascending=False), use_container_width=True, hide_index=True)
    except:
        st.warning("Pestaña de Historial no detectada.")
