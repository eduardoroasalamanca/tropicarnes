import streamlit as st
import urllib.parse
import json
import os
import unicodedata
import base64
from difflib import SequenceMatcher

# =====================================================================
# 1. CONFIGURACIÓN INICIAL
# =====================================================================
st.set_page_config(page_title="Tropicarnes Digital", layout="wide")

# Estilo para limpiar la interfaz
st.markdown("""
    <style>
    div[data-testid="stDecoration"] { display: none !important; }
    footer { display: none !important; visibility: hidden !important; }
    .stApp { margin-bottom: 0px !important; padding-bottom: 0px !important; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. CARGA DE DATOS (IMPORTANTE: Primero esto)
# =====================================================================
ARCHIVO_INVENTARIO = "inventario.json"

def cargar_inventario():
    if os.path.exists(ARCHIVO_INVENTARIO):
        try:
            with open(ARCHIVO_INVENTARIO, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
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

inventario_local = cargar_inventario()

def guardar_inventario(inventario):
    with open(ARCHIVO_INVENTARIO, "w", encoding="utf-8") as f:
        json.dump(inventario, f, ensure_ascii=False, indent=4)

# =====================================================================
# 3. LÓGICA Y FUNCIONES DE INTERFAZ
# =====================================================================
def normalizar_cadena(texto):
    texto = unicodedata.normalize('NFD', texto)
    return ''.join([c for c in texto if unicodedata.category(c) != 'Mn']).lower()

def coincide_busqueda(termino_usuario, nombre_articulo):
    if not termino_usuario: return True
    term_limpio = normalizar_cadena(termino_usuario)
    art_limpio = normalizar_cadena(nombre_articulo)
    if term_limpio in art_limpio: return True
    for c in ["(", ")", "/", ",", "."]: art_limpio = art_limpio.replace(c, " ")
    palabras = art_limpio.split()
    for p in palabras:
        if SequenceMatcher(None, term_limpio, p).ratio() >= 0.75: return True
    return False

# =====================================================================
# 4. CUERPO DE LA APP
# =====================================================================
st.markdown("<h1 style='text-align: center; color: #D32F2F;'>TROPICARNES</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar administrativo
with st.sidebar:
    clave_acceso = st.text_input("Contraseña Administrativa:", type="password")
    modo_admin = (clave_acceso == "tropicarnes2026")

# Generador de Pedidos
buscar_vecino = st.text_input("🔍 ¿Qué busca hoy?", placeholder="Ej: carne, pollo...")
st.markdown("---")

for categoria, productos in inventario_local.items():
    productos_filtrados = [p for p in sorted(productos) if coincide_busqueda(buscar_vecino, p)]
    if productos_filtrados:
        with st.expander(categoria, expanded=bool(buscar_vecino)):
            for prod in productos_filtrados:
                st.markdown(f"🔹 **{prod}**")
                # Aquí iría el input de cantidad (lo mantuve simple para evitar errores)