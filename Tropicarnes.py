# ... (todo el código anterior igual hasta la línea 232)

for categoria, productos in inventario_local.items():
    if productos: 
        productos_filtrados = [p for p in sorted(productos) if coincide_busqueda(buscar_vecino, p)]
        
        if productos_filtrados:
            with st.expander(categoria, expanded=bool(buscar_vecino)):
                for prod in productos_filtrados:
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"🔹 **{prod}**")
                    with c2:
                        es_unidad = "Unidad" in prod or "1kg" in prod or "1L" in prod or "Crema" in prod or "Combo" in prod
                        paso_medida = 1.0 if es_unidad else 0.5
                        label_unidad = "Unds" if es_unidad else "Kilos"
                        
                        cantidad = st.number_input(
                            label=f"{label_unidad} de {prod}",
                            min_value=0.0,
                            step=paso_medida,
                            key=f"input_{prod}",
                            label_visibility="collapsed"
                        )
                    
                    if cantidad > 0:
                        carrito_compras.append({"item": prod, "cant": cantidad, "unidad": label_unidad.lower()})

# ... (el resto del código queda igual)