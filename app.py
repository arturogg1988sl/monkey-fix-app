# --- SECCIÓN 3: HUESARIO ---
elif choice == "🦴 Huesario":
    st.header("Inventario de Huesario")
    try:
        # Lee el link directo de huesario
        df_h = conn.read(spreadsheet=st.secrets["links"]["huesario"], ttl=0)
        df_h = df_h.dropna(how='all')
        
        tab1, tab2 = st.tabs(["📋 Ver Inventario", "✍️ Registrar Equipo"])
        with tab1:
            st.dataframe(df_h, use_container_width=True, hide_index=True)
            
        with tab2:
            with st.form("f2"):
                m = st.text_input("Marca")
                mo = st.text_input("Modelo")
                # El usuario ve "ID / Color", pero lo guardaremos bajo la columna "ID"
                id_e = st.text_input("ID / Color") 
                
                if st.form_submit_button("Agregar al Huesario"):
                    if m and mo:
                        fecha = datetime.now().strftime("%d/%m/%Y")
                        # AQUÍ ESTÁ EL TRUCO: El nombre "ID" debe ser igual al del Excel
                        nueva_f = pd.DataFrame([{
                            "Marca": m, 
                            "Modelo": mo, 
                            "ID": id_e, 
                            "Historial": f"[{fecha}] Ingreso."
                        }])
                        
                        df_final_h = pd.concat([df_h, nueva_f], ignore_index=True)
                        
                        # Guardamos en la hoja Huesario
                        conn.update(
                            spreadsheet="https://docs.google.com/spreadsheets/d/1Qh7YQO_piMgikZEKY8VNVsMIyudfklLu7D0wKFDz2Fc/edit", 
                            worksheet="Huesario", 
                            data=df_final_h
                        )
                        st.success("✅ Equipo registrado en el Huesario.")
                        st.rerun()
                    else:
                        st.error("⚠️ La Marca y el Modelo son obligatorios.")
    except Exception as e:
        st.error(f"Error en Huesario: {e}")
