import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import json
import os
import unicodedata
import base64
from difflib import SequenceMatcher

# Configuración
if os.path.exists("logo.png"):
    icono_app = "logo.png"
else:
    icono_app = "🥩"

st.set_page_config(page_title="Tropicarnes Digital", layout="wide", page_icon=icono_app)

# Estilo CSS para ocultar menús
hide_streamlit_style = """
    <style>
    #MainMenu, footer, header {visibility: hidden; display: none !important;}
    [data-testid="stHeader"] {background: transparent !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Carga de datos
ARCHIVO_INVENTARIO = "inventario.json"
def cargar_inventario():
    if os.path.exists(ARCHIVO_INVENTARIO):
        try:
            with open(ARCHIVO_INVENTARIO, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {}

inventario_local = cargar_inventario()

# Motor de búsqueda
def normalizar_cadena(texto):
    texto = unicodedata.normalize('NFD', texto)
    return ''.join([c for c in texto if unicodedata.category(c) != 'Mn']).lower()

def coincide_busqueda(termino_usuario, nombre_articulo):
    if not termino_usuario: return True
    term_limpio = normalizar_cadena(termino_usuario)
    art_limpio = normalizar_cadena(nombre_articulo)
    if term_limpio in art_limpio: return True
    for c in ["(", ")", "/", ",", "."]: art_limpio = art_limpio.replace(c, " ")
    for palabra in art_limpio.split():
        if SequenceMatcher(None, term_limpio, palabra).ratio() >= (0.75 if len(term_limpio) >= 4 else 0.85): return True
    return False

# Interfaz
st.markdown("<h1 style='text-align: center; color: #D32F2F;'>TROPICARNES</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555555;'>Calidad y frescura en su celular</h4>", unsafe_allow_html=True)
st.markdown("---")

buscar_vecino = st.text_input("🔍 ¿Qué busca hoy?", placeholder="Ej: carne, jabón...", key="input_buscar").strip()
st.markdown("---")

for categoria, productos in inventario_local.items():
    if productos:
        productos_filtrados = [p for p in sorted(productos) if coincide_busqueda(buscar_vecino, p)]
        if productos_filtrados:
            with st.expander(categoria, expanded=bool(buscar_vecino)):
                for prod in productos_filtrados:
                    c1, c2 = st.columns([3, 1])
                    with c1: st.markdown(f"🔹 **{prod}**")
                    with c2:
                        cantidad = st.number_input(f"Cant {prod}", min_value=0.0, step=0.5, key=f"input_{prod}", label_visibility="collapsed")
                        if cantidad > 0: st.session_state[f"carro_{prod}"] = cantidad

# Resumen y WhatsApp
st.markdown("---")
if st.button("🚀 Enviar Pedido por WhatsApp"):
    texto_wa = "*¡Hola Tropicarnes!* Mi pedido:\n"
    for key, val in st.session_state.items():
        if key.startswith("carro_") and val > 0:
            texto_wa += f"- {val} de {key.replace('carro_', '')}\n"
    st.markdown(f"[📲 Enviar](https://wa.me/584140766601?text={urllib.parse.quote(texto_wa)})")