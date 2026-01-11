import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Monkey Fix System", page_icon="🐒", layout="wide")

# Estilos personalizados (Color Amarillo/Negro de Monkey Fix)
st.markdown("""
    <style>
    .stButton>button { background-color: #FFD700; color: black; font-weight: bold; width: 100%; }
    .stHeader { background-color: #121212; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ENCABEZADO Y LOGO ---
try:
    logo = Image.open("monkey_logo.png")
    st.image(logo, width=150)
except:
    st.title("🐒 MONKEY FIX / CELULARES 653")

# --- MENÚ ---
menu = ["🔍 Consultar", "➕ Agregar Pantalla", "🦴 Huesario", "💾 Respaldos"]
choice = st.sidebar.radio("Menú Principal", menu)

# --- 1. CONSULTA ---
if choice == "🔍 Consultar":
    st.header("Buscador de Compatibilidades")
    df = conn.read(worksheet="Pantallas", ttl="0") # ttl=0 para que refresque siempre
    
    busqueda = st.text_input("Escribe el modelo (ej: A10, G8 Power...)", placeholder="Buscar...")
    
    if busqueda:
        # Filtro inteligente
        mask = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
        resultado = df[mask]
        if not resultado.empty:
            st.dataframe(resultado, use_container_width=True, hide_index=True)
        else:
            st.error("No se encontró compatibilidad registrada.")
    else:
        st.info("Escribe arriba para buscar. Mostrando todos los registros:")
        st.dataframe(df, use_container_width=True, hide_index=True)

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
                new_data = pd.DataFrame([{"Marca": m, "Modelo": mo, "Compatibles": comp, "Notas": notas}])
                old_data = conn.read(worksheet="Pantallas")
                updated_df = pd.concat([old_data, new_data], ignore_index=True)
                conn.update(worksheet="Pantallas", data=updated_df)
                st.success("¡Guardado correctamente!")
            else:
                st.warning("Marca y Modelo son obligatorios.")

# --- 3. HUESARIO ---
elif choice == "🦴 Huesario":
    st.header("Inventario de Partes")
    tab1, tab2 = st.tabs(["Registrar Entrada", "Ver/Editar Historial"])
    
    with tab1:
        with st.form("form_hueso"):
            m = st.text_input("Marca")
            mo = st.text_input("Modelo")
            id_eq = st.text_input("Color / ID")
            if st.form_submit_button("Registrar Equipo"):
                fecha = datetime.now().strftime("%d/%m/%Y")
                new_h = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_eq, "Historial": f"[{fecha}] Ingreso."}])
                old_h = conn.read(worksheet="Huesario")
                updated_h = pd.concat([old_h, new_h], ignore_index=True)
                conn.update(worksheet="Huesario", data=updated_h)
                st.success("Registrado en el huesario.")

    with tab2:
        df_h = conn.read(worksheet="Huesario", ttl="0")
        for index, row in df_h.iterrows():
            with st.expander(f"{row['Marca']} {row['Modelo']} - {row['ID']}"):
                nuevo_hist = st.text_area("Historial de partes retiradas", value=row['Historial'], key=f"h_{index}")
                if st.button("Guardar Cambios", key=f"btn_{index}"):
                    df_h.at[index, 'Historial'] = nuevo_hist
                    conn.update(worksheet="Huesario", data=df_h)
                    st.success("Historial actualizado.")

# --- 4. RESPALDOS ---
elif choice == "💾 Respaldos":
    st.header("Descargar Datos")
    df_p = conn.read(worksheet="Pantallas")
    st.download_button("Descargar Excel Pantallas (CSV)", df_p.to_csv(index=False), "pantallas_monkey.csv")
