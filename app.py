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

menu = ["🔍 Compatibilidades", "➕ Registrar/Editar", "🦴 Huesario", "📜 Historial Movimientos"]
choice = st.sidebar.radio("Panel de Control", menu)

# --- FUNCIÓN PARA REGISTRAR HISTORIAL GENERAL ---
def registrar_historial_general(accion, marca, modelo, detalles):
    try:
        df_hist = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Historial_Huesario", ttl=0)
        nueva_entrada = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Acción": accion, "Marca": marca, "Modelo": modelo, "Detalles": detalles
        }])
        df_f_h = pd.concat([df_hist, nueva_entrada], ignore_index=True)
        conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Historial_Huesario", data=df_f_h)
    except:
        pass

# --- 1. COMPATIBILIDADES ---
if choice == "🔍 Compatibilidades":
    st.header("Buscador de Compatibilidades")
    df = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", ttl=0)
    bus = st.text_input("Buscar modelo:")
    if bus:
        mask = df.apply(lambda row: row.astype(str).str.contains(bus, case=False).any(), axis=1)
        st.dataframe(df[mask], use_container_width=True, hide_index=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 2. REGISTRAR / EDITAR STOCK ---
elif choice == "➕ Registrar/Editar":
    tab_reg, tab_edit = st.tabs(["🆕 Registrar Nuevo", "✏️ Editar Existente"])
    df_stock = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", ttl=0)
    with tab_reg:
        with st.form("f_reg"):
            ma, mo, co, no = st.text_input("Marca"), st.text_input("Modelo Base"), st.text_input("Compatibles"), st.text_area("Notas")
            if st.form_submit_button("Guardar"):
                nuevo = pd.DataFrame([{"Marca": ma, "Modelo": mo, "Compatibles": co, "Notas": no}])
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", data=pd.concat([df_stock, nuevo], ignore_index=True))
                st.success("Guardado")

    with tab_edit:
        modelo_editar = st.selectbox("Selecciona equipo", df_stock["Modelo"].unique())
        idx = df_stock[df_stock["Modelo"] == modelo_editar].index[0]
        with st.form("f_edit"):
            n_ma, n_mo = st.text_input("Marca", value=df_stock.at[idx, "Marca"]), st.text_input("Modelo", value=df_stock.at[idx, "Modelo"])
            n_co, n_no = st.text_input("Compatibles", value=df_stock.at[idx, "Compatibles"]), st.text_area("Notas", value=df_stock.at[idx, "Notas"])
            c1, c2 = st.columns(2)
            if c1.form_submit_button("Actualizar"):
                df_stock.loc[idx] = [n_ma, n_mo, n_co, n_no]
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", data=df_stock)
                st.success("Actualizado")
            if c2.form_submit_button("🚨 Eliminar"):
                conn.update(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Stock", data=df_stock.drop(idx))
                st.rerun()

# --- 3. HUESARIO (CON BUSCADOR Y NOTAS) ---
elif choice == "🦴 Huesario":
    st.header("Gestión de Huesario")
    df_h = conn.read(spreadsheet=st.secrets["links"]["huesario"], worksheet="Partes", ttl=0)
    df_h = df_h.dropna(how='all')
    
    t_ver, t_reg, t_upd, t_del = st.tabs(["📋 Ver / Buscar", "➕ Agregar", "🔧 Actualizar Notas", "🗑️ Eliminar"])
    
    with t_ver:
        bus_h = st.text_input("🔍 Buscar pieza o modelo en Huesario:")
        if bus_h:
            mask_h = df_h.apply(lambda row: row.astype(str).str.contains(bus_h, case=False).any(), axis=1)
            st.dataframe(df_h[mask_h], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
    
    with t_reg:
        with st.form("f_h_reg"):
            m, mo, id_v = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("ID/Estado Inicial")
            if st.form_submit_button("Guardar"):
                nueva_h = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_v, "Historial": f"[{datetime.now().strftime('%d/%m/%Y')}] Ingreso: {id_v}"}])
                conn.update(spreadsheet=st.secrets["links"]["huesario"], worksheet="Partes", data=pd.concat([df_h, nueva_h], ignore_index=True))
                registrar_historial_general("AGREGAR", m, mo, f"ID: {id_v}")
                st.success("Agregado")
                st.rerun()

    with t_upd:
        st.subheader("Anotar piezas retiradas")
        if not df_h.empty:
            seleccion = st.selectbox("Selecciona el equipo que desarmaste:", 
                                    df_h.apply(lambda x: f"{x['Marca']} {x['Modelo']} (ID: {x['ID']})", axis=1))
            idx_u = df_h[df_h.apply(lambda x: f"{x['Marca']} {x['Modelo']} (ID: {x['ID']})", axis=1) == seleccion].index[0]
            
            st.info(f"**Historial actual:** {df_h.at[idx_u, 'Historial']}")
            
            with st.form("f_notas"):
                nota_nueva = st.text_input("¿Qué pieza le quitaste?", placeholder="Ej: Se retiró bocina y centro de carga")
                if st.form_submit_button("Actualizar Historial"):
                    fecha_n = datetime.now().strftime("%d/%m/%Y")
                    # Concatenamos la nota nueva al historial viejo
                    historial_viejo = str(df_h.at[idx_u, 'Historial'])
                    nuevo_historial = f"{historial_viejo} | [{fecha_n}] {nota_nueva}"
                    
                    df_h.at[idx_u, 'Historial'] = nuevo_historial
                    conn.update(spreadsheet=st.secrets["links"]["huesario"], worksheet="Partes", data=df_h)
                    registrar_historial_general("EDITAR NOTAS", df_h.at[idx_u, 'Marca'], df_h.at[idx_u, 'Modelo'], nota_nueva)
                    st.success("Notas actualizadas")
                    st.rerun()

    with t_del:
        if not df_h.empty:
            equipo_del = st.selectbox("Equipo a eliminar", df_h.apply(lambda x: f"{x['Marca']} {x['Modelo']} (ID: {x['ID']})", axis=1))
            if st.button("Confirmar Baja"):
                idx_d = df_h[df_h.apply(lambda x: f"{x['Marca']} {x['Modelo']} (ID: {x['ID']})", axis=1) == equipo_del].index[0]
                m_d, mo_d = df_h.at[idx_d, "Marca"], df_h.at[idx_d, "Modelo"]
                conn.update(spreadsheet=st.secrets["links"]["huesario"], worksheet="Partes", data=df_h.drop(idx_d))
                registrar_historial_general("ELIMINAR", m_d, mo_d, "Baja de inventario")
                st.error("Eliminado")
                st.rerun()

# --- 4. HISTORIAL DE MOVIMIENTOS ---
elif choice == "📜 Historial Movimientos":
    st.header("Registro de Actividad")
    try:
        df_hist = conn.read(spreadsheet=st.secrets["links"]["pantallas"], worksheet="Historial_Huesario", ttl=0)
        st.dataframe(df_hist.sort_index(ascending=False), use_container_width=True, hide_index=True)
    except:
        st.warning("Pestaña 'Historial_Huesario' no encontrada.")
