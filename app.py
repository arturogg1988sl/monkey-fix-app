# --- 3. HUESARIO (ACTUALIZADO PARA DETECTAR ERRORES) ---
elif choice == "🦴 Huesario":
    st.header("Inventario de Huesario")
    try:
        # Cargamos los datos
        df_h = conn.read(spreadsheet=st.secrets["links"]["huesario"], ttl=0)
        df_h = df_h.dropna(how='all')
        
        tab_v, tab_r = st.tabs(["📋 Ver Inventario", "✍️ Registrar"])
        
        with tab_v:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
            
        with tab_r:
            with st.form("f_h"):
                m, mo, id_e = st.text_input("Marca"), st.text_input("Modelo"), st.text_input("ID / Color")
                if st.form_submit_button("Agregar"):
                    if m and mo:
                        fecha = datetime.now().strftime("%d/%m/%Y")
                        # CREAMOS LA FILA: Asegúrate que estos nombres coincidan con tu Excel
                        nueva_fila = pd.DataFrame([{"Marca": m, "Modelo": mo, "ID": id_e, "Historial": f"[{fecha}] Ingreso."}])
                        df_final_h = pd.concat([df_h, nueva_fila], ignore_index=True)
                        
                        # INTENTO DE GUARDAR
                        conn.update(spreadsheet=st.secrets["links"]["huesario"], data=df_final_h)
                        st.success("Hueso registrado exitosamente.")
                        st.rerun()
                    else:
                        st.error("Marca y Modelo son obligatorios.")
    except Exception as e:
        st.error("Hubo un problema con la hoja de Huesario.")
        st.info(f"🔍 **Error Técnico Real:** {e}")
        st.warning("Revisa que el link de Huesario en Secrets termine en #gid=... (el número de la segunda pestaña)")
