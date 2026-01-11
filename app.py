import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Prueba de Conexión Monkey Fix")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Intentamos leer la primera hoja por defecto sin nombre
    df = conn.read(ttl=0)
    st.success("✅ ¡Conexión exitosa al archivo!")
    st.write("Datos encontrados en la primera hoja:")
    st.dataframe(df.head())
    
except Exception as e:
    st.error("❌ Error de conexión")
    st.write(str(e))
