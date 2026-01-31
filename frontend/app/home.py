"""
Home.py - Página principal (versión limpia)
Muestra título, estado del backend y navegación básica.
"""

import streamlit as st
import requests
import os

# ============================================
# CONFIGURACIÓN
# ============================================
st.title("🚕 Demand Prediction Service")

# ============================================
# DESCRIPCIÓN DE LA PÁGINA (MARKDOWN)
# ============================================
st.markdown("""
**Sistema para gestionar zonas y rutas de taxis NYC**

Esta aplicación permite crear, editar y visualizar zonas de taxis 
y rutas entre ellas, además de cargar datos reales desde archivos .parquet.
""")

st.markdown("---")  

# ============================================
# CONFIGURACIÓN DE URL
# ============================================
API_URL = os.environ.get("API_URL", "http://localhost:8000")
HEALTH_ENDPOINT = f"{API_URL}/health"

# ============================================
# MISMA FUNCIÓN PARA VERIFICAR BACKEND
# ============================================
def check_backend_health():
    """
    Verifica si el backend está disponible llamando a GET /health
    Misma función que antes pero solo devuelve estado simple
    """
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            return {
                "status": "healthy",
                "message": "Backend funcionando correctamente",
                "details": response.json() if response.json() else {}
            }
        else:
            return {
                "status": "error",
                "message": f"Backend respondió con error: {response.status_code}",
                "details": response.text[:100] if response.text else ""
            }
    except requests.exceptions.ConnectionError:
        return {
            "status": "offline",
            "message": "No se puede conectar al backend",
            "details": f"URL: {HEALTH_ENDPOINT}"
        }
    except requests.exceptions.Timeout:
        return {
            "status": "timeout", 
            "message": "El backend no respondió a tiempo",
            "details": "Timeout después de 5 segundos"
        }
    except Exception as e:
        return {
            "status": "unknown_error",
            "message": f"Error inesperado: {str(e)}",
            "details": str(e)
        }


# ============================================
# ESTADO DEL BACKEND
# ============================================
st.markdown("### 🔍 Estado del Backend")

# Verificar estado
health_status = check_backend_health()

# Mostrar según estado
if health_status["status"] == "healthy":
    st.success("✅ **CONECTADO** - " + health_status["message"])
elif health_status["status"] == "offline":
    st.error("❌ **DESCONECTADO** - " + health_status["message"])
elif health_status["status"] == "timeout":
    st.warning("⏰ **TIMEOUT** - " + health_status["message"])
else:
    st.error("⚠️ **ERROR** - " + health_status["message"])

# Mostrar URL que se está usando
st.caption(f"URL del backend: `{HEALTH_ENDPOINT}`")

# ============================================
# NAVEGACIÓN 
# ============================================
st.markdown("---")
st.markdown("### 📱 Navegación")

# Tres botones en columnas
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗺️ Zonas", use_container_width=True):
        st.switch_page("pages/1_Zones.py")
    st.caption("Gestionar zonas")

with col2:
    if st.button("🚕 Rutas", use_container_width=True):
        st.switch_page("pages/2_Routes.py")
    st.caption("Administrar rutas")

with col3:
    if st.button("📤 Cargar Datos", use_container_width=True):
        st.switch_page("pages/3_Upload_Parquet.py")
    st.caption("Subir .parquet")
