import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import json
import os
import unicodedata
import base64
from difflib import SequenceMatcher
import requests

# =====================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA E ÍCONO DE PESTAÑA
# =====================================================================
if os.path.exists("logo.png"):
    icono_app = "logo.png"
else:
    icono_app = "🥩"

st.set_page_config(
    page_title="Tropicarnes Digital", 
    layout="wide", 
    page_icon=icono_app
)

# ---- COMPONENTE DE ESTILO CSS QUIRÚRGICO (CLIENTES) ----
hide_streamlit_style = """
    <style>
    /* Ocultar por completo la cabecera (Fork, GitHub, 3 puntos) */
    [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Ocultar pie de página y línea roja decorativa */
    footer {visibility: hidden; display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    #stConnectionStatus {display: none !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---- HACK JAVASCRIPT EXTREMO PARA EL CONTENEDOR PADRE ----
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
# 2. GESTIÓN DE PERSISTENCIA DE DATOS (NUBE VÍA GITHUB GIST)
# =====================================================================
@st.cache_data(ttl=5)
def cargar_inventario():
    token = st.secrets.get("GITHUB_TOKEN")
    gist_id = st.secrets.get("GIST_ID")
    
    inventario_defecto = {
        "🔥 Ofertas del Día": ["Combo Sopera (3Kg x $10)", "Queso Llanero en Promoción (Kg)"],
        "Res": ["Pulpa Negra (Bistec/Para Guisar)", "Carne Molida de Primera", "Lagarto con Hueso", "Costilla de Res"],
        "Aves": ["Pollo Entero Limpio", "Pechuga de Pollo", "Milanesas de Pollo"],
        "Cerdo": ["Chuleta de Cerdo", "Costilla de Cerdo", "Pulpa de Cerdo"],
        "Charcutería y Quesos": ["Queso Blanco Duro (Llanero)", "Queso Blanco Semiduro", "Queso Amarillo", "Jamón Fiambre"],
        "Víveres Esenciales": ["Harina de Maíz Harina P.A.N. 1kg", "Arroz Blanco Primor 1kg", "Pasta Alimenticia 1kg", "Aceite Vegetal 1L", "Café Molido Local"],
        "Panadería Artesanal": ["Pan Canilla (Unidad)", "Pan Campesino (Unidad)"],
        "Limpieza y Aseo": ["Jabón en Polvo 1kg", "Cloro Líquido 1L", "Lavaplatos en Crema"]
    }
    
    if not token or not gist_id:
        # Fallback local si no hay secrets configurados
        if os.path.exists("inventario.json"):
            try:
                with open("inventario.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return inventario_defecto
    
    try:
        headers = {"Authorization": f"token {token}"}
        response = requests.get(f"https://api.github.com/gists/{gist_id}", headers=headers, timeout=5)
        if response.status_code == 200:
            gist_data = response.json()
            contenido_archivo = gist_data["files"]["inventario.json"]["content"]
            return json.loads(contenido_archivo)
    except Exception as e:
        pass
            
    return inventario_defecto

inventario_local = cargar_inventario()


# =====================================================================
# 3. MOTOR DE INTELIGENCIA LINGÜÍSTICA (FUZZY MATCHING TOLERANTE)
# =====================================================================
def normalizar_cadena(texto):
    texto = unicodedata.normalize('NFD', texto)
    return ''.join([c for c in texto if unicodedata.category(c) != 'Mn']).lower()

def coincide_busqueda(termino_usuario, nombre_articulo):
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
# 4. IDENTIDAD VISUAL: LOGO RESPONSIVO 100% CENTRADO
# =====================================================================
def renderizar_logo_centrado(ruta_img):
    try:
        with open(ruta_img, "rb") as f:
            datos_binarios = f.read()
        codificado = base64.b64encode(datos_binarios).decode()
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px; width: 100%;">
                <img src="data:image/png;base64,{codificado}" style="width: 95px; max-width: 100%; height: auto; display: block; margin: 0 auto;">
            </div>
            """, 
            unsafe_allow_html=True
        )
    except Exception as e:
        pass

if os.path.exists("logo.png"):
    renderizar_logo_centrado("logo.png")

st.markdown("<h1 style='text-align: center; color: #D32F2F; font-family: Arial, sans-serif; letter-spacing: 2px; margin-top: 0px;'>TROPICARNES</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555555; font-style: italic;'>Calidad, frescura y conveniencia en su celular o PC</h4>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777777;'>📍 San Cristóbal, Estado Táchira | Atendido por sus dueños</p>", unsafe_allow_html=True)
st.markdown("---")


# =====================================================================
# 5. INTERFAZ OPERATIVA DEL CLIENTE (VECINO)
# =====================================================================
st.subheader("🛒 Generador de Pedidos Express")
st.write("Seleccione sus productos abajo y envíe su lista directo a nuestro WhatsApp sin hacer colas, ni esperar.")
st.markdown("---")

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

# --- MEMORIA PERSISTENTE DEL CARRITO ---
# El carrito ya NO se arma leyendo solo lo que está visible en pantalla
# (eso es lo que causaba que se "perdiera" un producto al cambiar de
# categoría a búsqueda o viceversa). Ahora vive en session_state y se
# actualiza mediante on_change cada vez que el cliente toca una cantidad,
# sin importar si ese producto sigue visible en el siguiente rerun.
if "carrito_state" not in st.session_state:
    st.session_state.carrito_state = {}

def _actualizar_carrito(prod, unidad):
    valor = st.session_state.get(f"input_{prod}", 0.0)
    if valor and valor > 0:
        st.session_state.carrito_state[prod] = {"item": prod, "cant": valor, "unidad": unidad}
    else:
        st.session_state.carrito_state.pop(prod, None)

st.markdown("---")
st.subheader("👇 Arme su Pedido Aquí")

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
                        
                        st.number_input(
                            label=f"{label_unidad} de {prod}",
                            min_value=0.0,
                            step=paso_medida,
                            key=f"input_{prod}",
                            label_visibility="collapsed",
                            on_change=_actualizar_carrito,
                            args=(prod, label_unidad.lower())
                        )

# El carrito final se construye SIEMPRE desde la memoria persistente,
# nunca desde el bucle de renderizado filtrado.
carrito_compras = list(st.session_state.carrito_state.values())


# =====================================================================
# 6. RESUMEN DE COMPRA Y ENLACE LOGÍSTICO DE WHATSAPP
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
    
    TELEFONO_SUGEY = "584140766601"
    
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
