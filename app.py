import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("🔍 Diagnóstico de Pestañas Monkey Fix")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 1. Intentamos conectar al archivo
    url = st.secrets["links"]["pantallas"]
    st.write(f"Conectando al archivo: `{url}`")
    
    # 2. Listar todas las pestañas disponibles
    # Usamos una función interna para ver qué nombres detecta Google
    client = conn._instance.client
    spreadsheet = client.open_by_key(url.split('/')[-2]) if "docs.google.com" in url else client.open_by_key(url)
    worksheets = spreadsheet.worksheets()
    
    nombres_reales = [ws.title for ws in worksheets]
    
    st.write("### Pestañas encontradas en tu Excel:")
    for nombre in nombres_reales:
        st.code(f"'{nombre}'")
    
    # 3. Verificación automática
    if "Partes" in nombres_reales:
        st.success("✅ ¡El sistema SÍ detecta la pestaña 'Partes'!")
        df = conn.read(spreadsheet=url, worksheet="Partes", ttl=0)
        st.write("Vista previa de los datos:")
        st.dataframe(df.head())
    else:
        st.error("❌ El sistema NO detecta ninguna pestaña llamada exactamente 'Partes'")
        st.info("Copia uno de los nombres que aparecen arriba (en los cuadros grises) y úsalo en tu código.")

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Asegúrate de que el correo de la Service Account sea Editor en el Excel.")
