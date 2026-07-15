import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import json
import os
import unicodedata
from difflib import SequenceMatcher

# =====================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA E ÍCONO DE PESTAÑA
# =====================================================================
# Si el archivo "logo.png" existe, lo adopta en la pestaña del navegador
if os.path.exists("logo.png"):
    icono_app = "logo.png"
else:
    icono_app = "🥩"

st.set_page_config(
    page_title="Tropicarnes Digital", 
    layout="wide", 
    page_icon=icono_app
)

# ---- COMPONENTE DE ESTILO PARA OCULTAR ELEMENTOS SIN DAÑAR EL SIDEBAR ----
# Ocultamos solo lo innecesario, pero dejamos libre y funcional el botón del sidebar izquierdo
hide_streamlit_style = """
    <style>
    /* Ocultar el menú de los 3 puntos superior derecho */
    #MainMenu {visibility: hidden; display: none !important;}
    
    /* Ocultar el pie de página de Streamlit */
    footer {visibility: hidden; display: none !important;}
    
    /* Ocultar la línea roja/decorativa superior */
    div[data-testid="stDecoration"] {display: none !important;}
    
    /* Ocultar el botón de Deploy (Share) */
    .stAppDeployButton {display: none !important;}
    
    /* Ocultar el estatus de conexión */
    #stConnectionStatus {display: none !important;}
    
    /* Hacer la cabecera invisible pero activa para que el botón de abrir sidebar siga funcionando */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        background: transparent !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---- HACK JAVASCRIPT PARA ELIMINAR LOS BOTONES FLOTANTES DEL CONTENEDOR PADRE ----
# Elimina de raíz tu foto, la corona de "Manage app" y la marca de agua de Streamlit abajo a la derecha
components.html(
    """
    <script>
        const hideStreamlitBranding = () => {
            if (window.top && window.top.document) {
                const targets = window.top.document.querySelectorAll(
                    '[href*="streamlit.io"], [class*="viewerBadge"], [class*="StatusWidget"], [data-testid="stStatusWidget"], iframe[title="Manage app"], button[data-testid="manage-app-button"]'
                );
                targets.forEach(e => e.style.setProperty("display", "none", "important"));
            }
        };
        // Intentamos ocultarlo inmediatamente y con intervalos de tiempo mientras carga la página
        hideStreamlitBranding();
        setTimeout(hideStreamlitBranding, 500);
        setTimeout(hideStreamlitBranding, 1500);
        setTimeout(hideStreamlitBranding, 3000);
        setTimeout(hideStreamlitBranding, 5000);
    </script>
    """,
    height=0,
)


# =====================================================================
# 2. GESTIÓN DE PERSISTENCIA DE DATOS (INVENTARIO JSON)
# =====================================================================
ARCHIVO_INVENTARIO = "inventario.json"

def cargar_inventario():
    """
    Carga el inventario real desde el archivo local o genera el inicial.
    Mantiene estrictamente el orden de inserción de las categorías.
    """
    if os.path.exists(ARCHIVO_INVENTARIO):
        try:
            with open(ARCHIVO_INVENTARIO, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # Inventario inicial por defecto (La categoría de Ofertas va de primera)
    return {
        "🔥 Ofertas del Día": ["Combo Sopera (3Kg x $10)", "Queso Llanero en Promoción (Kg)"],
        "Res": ["Pulpa Negra (Bistec/Para Guisar)", "Carne Molida de Primera", "Lagarto con Hueso", "Costilla de Res"],
        "Aves": ["Pollo Entero Limpio", "Pechuga de Pollo", "Milanesas de Pollo"],
        "Cerdo": ["Chuleta de Cerdo", "Costilla de Cerdo", "Pulpa de Cerdo"],
        "Charcutería y Quesos": ["Queso Blanco Duro (Llanero)", "Queso Blanco Semiduro", "Queso Amarillo", "Jamón Fiambre"],
        "Víveres Esenciales": ["Harina de Maíz Harina P.A.N. 1kg", "Arroz Blanco Primor 1kg", "Pasta Alimenticia 1kg", "Aceite Vegetal 1L", "Café Molido Local"],
        "Panadería Artesanal": ["Pan Canilla (Unidad)", "Pan Campesino (Unidad)"],
        "Limpieza y Aseo": ["Jabón en Polvo 1kg", "Cloro Líquido 1L", "Lavaplatos en Crema"]
    }

def guardar_inventario(inventario):
    """Guarda los cambios directamente en el archivo JSON."""
    with open(ARCHIVO_INVENTARIO, "w", encoding="utf-8") as f:
        json.dump(inventario, f, ensure_ascii=False, indent=4)

# Carga global limpia de datos
inventario_local = cargar_inventario()


# =====================================================================
# 3. MOTOR DE INTELIGENCIA LINGÜÍSTICA (FUZZY MATCHING TOLERANTE)
# =====================================================================
def normalizar_cadena(texto):
    """Elimina acentos y estandariza a minúsculas."""
    texto = unicodedata.normalize('NFD', texto)
    return ''.join([c for c in texto if unicodedata.category(c) != 'Mn']).lower()

def coincide_busqueda(termino_usuario, nombre_articulo):
    """Evalúa coincidencia elástica (Cubre 'javon', 'polo', 'carne')."""
    if not termino_usuario:
        return True
        
    term_limpio = normalizar_cadena(termino_usuario)
    art_limpio = normalizar_cadena(nombre_articulo)
    
    if term_limpio in art_limpio:
        return True
        
    for caracter in ["(", ")", "/", ",", "."]:
        art_limpio = art_limpio.replace(caracter, " ")
        
    palabras_articulo = art_limpio.split()
    for palabra in palabras_articulo:
        umbral_tolerancia = 0.75 if len(term_limpio) >= 4 else 0.85
        if SequenceMatcher(None, term_limpio, palabra).ratio() >= umbral_tolerancia:
            return True
            
    return False


# =====================================================================
# 4. IDENTIDAD VISUAL: LOGO CENTRADO COMPACTO Y MARCA
# =====================================================================
# Encapsulamos el logo en columnas balanceadas para reducir su tamaño visual
if os.path.exists("logo.png"):
    col_izq, col_centro, col_der = st.columns([4.5, 1, 4.5])
    with col_centro:
        # Se muestra nítido, centrado y con un ancho estilizado de 95px (20% más pequeño)
        st.image("logo.png", width=95)

st.markdown("<h1 style='text-align: center; color: #D32F2F; font-family: Arial, sans-serif; letter-spacing: 2px; margin-top: 0px;'>TROPICARNES</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555555; font-style: italic;'>Calidad, frescura y conveniencia en su celular o PC</h4>", unsafe_allow_html=True)
st.markdown("---")


# =====================================================================
# 5. SIDEBAR: CONTROL DE UBICACIÓN Y ACCESO ADMINISTRATIVO
# =====================================================================
with st.sidebar:
    st.markdown("### 🏪 Panel de Control")
    st.markdown("**Tropicarnes** | Atendido por sus dueños")
    st.write("📍 San Cristóbal, Estado Táchira")
    st.markdown("---")
    
    st.markdown("#### ⚙️ Modificar Inventario")
    clave_acceso = st.text_input("Contraseña Administrativa:", type="password", key="clave_admin_sidebar")
    
    modo_admin = (clave_acceso == "tropicarnes2026")
    if clave_acceso and not modo_admin:
        st.error("Contraseña incorrecta")


# =====================================================================
# 6. MÓDULO ADMINISTRATIVO (EDICIÓN EN TIEMPO REAL)
# =====================================================================
if modo_admin:
    st.warning("🚧 MODO ADMINISTRATIVO ACTIVO: Modificando el menú de Tropicarnes")
    
    cat_seleccionada = st.selectbox("1. Seleccione la categoría a modificar:", list(inventario_local.keys()), key="sel_cat_admin")
    col_adm1, col_adm2 = st.columns(2)
    
    with col_adm1:
        st.markdown("##### Add Producto")
        nuevo_prod = st.text_input("Nombre del nuevo artículo:", placeholder="Ej: Mortadela Especial 1kg", key="input_nuevo_prod").strip()
        if st.button("➕ Registrar Producto", key="btn_registrar_prod"):
            if nuevo_prod and nuevo_prod not in inventario_local[cat_seleccionada]:
                inventario_local[cat_seleccionada].append(nuevo_prod)
                guardar_inventario(inventario_local)
                st.success(f"Agregado: {nuevo_prod}")
                st.rerun()
                
    with col_adm2:
        st.markdown("##### Eliminar / Agotar Producto")
        buscar_admin = st.text_input("🔍 Filtrar artículo para eliminar:", placeholder="Ej: pulpa, pollo...", key="input_buscar_admin").strip()
        
        productos_ordenados_admin = sorted(inventario_local[cat_seleccionada])
        if buscar_admin:
            productos_ordenados_admin = [p for p in productos_ordenados_admin if coincide_busqueda(buscar_admin, p)]
        
        if productos_ordenados_admin:
            prod_a_borrar = st.selectbox("Seleccione el producto a retirar:", productos_ordenados_admin, key="sel_prod_borrar")
            if st.button("🗑️ Eliminar Producto", key="btn_eliminar_prod"):
                if prod_a_borrar in inventario_local[cat_seleccionada]:
                    inventario_local[cat_seleccionada].remove(prod_a_borrar)
                    guardar_inventario(inventario_local)
                    st.success(f"Retirado: {prod_a_borrar}")
                    st.rerun()
        else:
            st.info("No se encontraron coincidencias.")
    st.markdown("---")


# =====================================================================
# 7. INTERFAZ OPERATIVA DEL CLIENTE (VECINO)
# =====================================================================
st.subheader("🛒 Generador de Pedidos Express")
st.write("Seleccione sus productos abajo y envíe su lista directo a nuestro WhatsApp sin hacer colas, ni esperar.")
st.markdown("---")

# Buscador elástico blindado en dos columnas con botón táctil para teléfonos
col_busqueda, col_boton = st.columns([4, 1])

with col_busqueda:
    buscar_vecino = st.text_input(
        "🔍 ¿Qué está buscando hoy? Escriba aquí:", 
        placeholder="Ej: carne, jabón, pollo...", 
        key="input_buscar_vecino"
    ).strip()

with col_boton:
    st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
    ejecutar_busqueda = st.button("🔎 Filtrar", use_container_width=True, key="btn_filtrar_vecino")

carrito_compras = []

st.markdown("---")
st.subheader("👇 Arme su Pedido Aquí")

# Despliegue del menú respetando el orden del diccionario local (Ofertas siempre primero)
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


# =====================================================================
# 8. RESUMEN DE COMPRA Y ENLACE LOGÍSTICO DE WHATSAPP
# =====================================================================
st.markdown("---")
st.subheader("📋 Revisión de su Bolsa")

if not carrito_compras:
    st.info("Su bolsa está vacía. Seleccione la cantidad en los productos de arriba para armar el pedido.")
else:
    for pedido in carrito_compras:
        st.write(f"✅ **{pedido['cant']} {pedido['unidad']}** de {pedido['item']}")
        
    st.markdown("---")
    nombre_vecino = st.text_input("Introduzca su Nombre (Opcional):", placeholder="Ej. Sra. Carmen (Piso 2)", key="input_nombre_vecino")
    notes_pedido = st.text_area(
        "📝 Instrucciones Especiales (Opcional):", 
        placeholder="Ej: La carne en bistec delgado, el pollo picado para guisar, o si desea un gramaje específico de queso.",
        key="input_notas_pedido"
    )
    
    # RUTA LOGÍSTICA EXCLUSIVA PARA SUGEY
    TELEFONO_SUGEY = "584140766601"  # <- Colocar aquí el número real de Sugey para producción
    
    if st.button("🚀 Enviar Pedido Listo por WhatsApp", type="primary", key="btn_enviar_pedido"):
        texto_wa = "*¡Hola Tropicarnes!* Aquí tengo listo mi pedido Express para retirar:\n\n"
        for pedido in carrito_compras:
            texto_wa += f"- {pedido['cant']} {pedido['unidad']} de {pedido['item']}\n"
        
        if notas_limpias := notes_pedido.strip():
            texto_wa += f"\n*Notas especiales:* {notas_limpias}\n"
        
        texto_wa += "\n*Nota:* Por favor, me avisan por aquí mismo cuando lo tengan listo para pasar pagando y retirando de una vez. ¡Muchas gracias!"
        if nombre_vecino:
            texto_wa += f"\n\n*Cliente:* {nombre_vecino}"
            
        texto_codificado = urllib.parse.quote(texto_wa)
        url_final = f"https://wa.me/{TELEFONO_SUGEY}?text={texto_codificado}"
        
        st.success("¡Estructura de pedido acoplada!")
        st.markdown(f"[📲 HACER CLIC AQUÍ PARA ENVIAR EL PEDIDO]({url_final})")