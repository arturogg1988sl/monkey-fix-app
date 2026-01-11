import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("🔍 Verificador de Conexión Monkey Fix")

# 1. Intentar conectar
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Verificamos qué tipo de cliente cargó Streamlit
    tipo_cliente = type(conn._instance).__name__
    
    if "ServiceAccount" in tipo_cliente:
        st.success("✅ ¡CONECTADO COMO ADMINISTRADOR!")
        st.info("La llave se leyó correctamente. Ahora sí podemos ver las pestañas.")
        
        # Intentamos leer la pestaña Partes
        df = conn.read(spreadsheet=st.secrets["links"]["huesario"], worksheet="Partes", ttl=0)
        st.write("### Datos encontrados en 'Partes':")
        st.dataframe(df)
        
    else:
        st.error("❌ MODO PÚBLICO DETECTADO")
        st.warning("Streamlit no está usando tu llave. Revisa que el bloque [connections.gsheets] en los Secrets sea igual al que te envié.")
        st.write(f"Cliente actual: `{tipo_cliente}`")

except Exception as e:
    st.error(f"Error técnico: {e}")
