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

menu = ["🔍 Stock Pantallas", "➕ Registrar/Editar Stock", "🦴 Huesario", "📜 Historial Huesario"]
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
        st.error("No se pudo actualizar el historial. Revisa que exista la pestaña 'Historial_Huesario'")

# --- 1. STOCK PANTALLAS (VER) ---
if choice == "🔍 Stock Pantallas":
    st.header("Inventario de Pantallas")
    df = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", ttl=0)
    df = df.dropna(how='all')
    bus = st.text_input("Buscar modelo:")
    if bus:
        mask = df.apply(lambda row: row.astype(str).str.contains(bus, case=False).any(), axis=1)
        st.dataframe(df[mask], use_container_width=True, hide_index=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 2. REGISTRAR / EDITAR STOCK ---
elif choice == "➕ Registrar/Editar Stock":
    tab_reg, tab_edit = st.tabs(["🆕 Registrar Nuevo", "✏️ Editar Existente"])
    
    df_stock = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", ttl=0)

    with tab_reg:
        with st.form("f_reg"):
            ma, mo, co, no = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("Compatibles"), st.text_area("Notas")
            if st.form_submit_button("Guardar Nuevo"):
                nueva_p = pd.DataFrame([{"Marca": ma, "Modelo": mo, "Compatibles": co, "Notas": no}])
                df_final = pd.concat([df_stock, nueva_p], ignore_index=True)
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", data=df_final)
                st.success("Registrado con éxito")

    with tab_edit:
        modelo_editar = st.selectbox("Selecciona modelo para editar/eliminar compatibilidades", df_stock["Modelo"].unique())
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
                st.success("Actualizado con éxito")
            
            if col2.form_submit_button("🚨 Eliminar de Stock"):
                df_stock = df_stock.drop(idx)
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", data=df_stock)
                st.warning("Eliminado de Stock")
                st.rerun()

# --- 3. HUESARIO (VER / REGISTRAR / ELIMINAR) ---
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
            if st.form_submit_button("Guardar"):
                nueva_h = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_v, "Historial": f"[{datetime.now().strftime('%d/%m/%Y')}] Ingreso."}])
                df_f = pd.concat([df_h, nueva_h], ignore_index=True)
                conn.update(spreadsheet=st.secrets["links"]["huesario"], worksheet="Partes", data=df_f)
                registrar_historial("AGREGAR", m, mo, f"ID: {id_v}")
                st.success("Agregado")
                st.rerun()

    with t_del:
        if not df_h.empty:
            equipo_del = st.selectbox("Selecciona equipo a eliminar del Huesario", 
                                     df_h.apply(lambda x: f"{x['Marca']} {x['Modelo']} (ID: {x['ID']})", axis=1))
            if st.button("Confirmar Eliminación"):
                idx_h = df_h.index[st.session_state.get('last_idx', 0)] # Simplificado para el ejemplo
                # Buscamos el índice real
                idx_h = df_h[df_h.apply(lambda x: f"{x['Marca']} {x['Modelo']} (ID: {x['ID']})", axis=1) == equipo_del].index[0]
                marca_h, modelo_h = df_h.at[idx_h, "Marca"], df_h.at[idx_h, "Modelo"]
                
                df_h = df_h.drop(idx_h)
                conn.update(spreadsheet=st.secrets["links"]["huesario"], worksheet="Partes", data=df_h)
                registrar_historial("ELIMINAR", marca_h, modelo_h, "Retirado del inventario")
                st.error("Eliminado")
                st.rerun()

# --- 4. HISTORIAL DE EDICIÓN ---
elif choice == "📜 Historial Huesario":
    st.header("Historial de Movimientos de Huesario")
    try:
        df_hist = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Historial_Huesario", ttl=0)
        st.dataframe(df_hist.sort_index(ascending=False), use_container_width=True, hide_index=True)
    except:
        st.warning("Crea la pestaña 'Historial_Huesario' en tu Excel para ver los movimientos.")
