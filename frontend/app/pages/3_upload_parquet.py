import streamlit as st
import requests
import os

# Configuración de URL y Página
API_URL = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="Carga de Datos Parquet", layout="wide")

st.title("Carga de parquet")

# Verificar estado del backend en sidebar 
try:
    health_response = requests.get(f"{API_URL}/health", timeout=2)
    if health_response.status_code == 200:
        st.sidebar.success("Backend conectado")
    else:
        st.sidebar.error("Backend con problemas")
except:
    st.sidebar.error("Backend no disponible")

st.subheader("Configuración de Ingesta")

with st.container():
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        uploaded_file = st.file_uploader("Selecciona un archivo .parquet", type=["parquet"])
    with col2:
        limit_rows = st.number_input("Límite filas", 
                                     min_value=1000, 
                                     max_value=200000, 
                                     value=50000, 
                                     step=1000,
                                     help="Máximo de filas a procesar (default: 50,000)")
    with col3:
        top_n = st.number_input("Top N rutas", min_value=1, max_value=200, value=50)
    with col4:
        mode = st.selectbox("Modo", options=["create", "update"])

if st.button("Iniciar Procesamiento", type="primary", use_container_width=True):
    if uploaded_file is None:
        st.warning("Por favor, selecciona un archivo.")
    else:
        with st.spinner("Procesando datos..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/octet-stream")}
             
                payload = {"top_n_routes": top_n, "mode": mode}
                
                response = requests.post(
                    f"{API_URL}/uploads/trips-parquet", 
                    files=files, 
                    data=payload,  
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("¡Archivo procesado!")
                    
                    st.markdown("---")
                    st.subheader("Resumen de la Operación")
                    
                    m1, m2, m3, m4, m5 = st.columns(5)
                    with m1:
                        # 'rows_read' viene del backend: rows_read = len(df)
                        st.metric("Filas Leídas", f"{data.get('rows_read', 0):,}")
                    with m2:
                        st.metric("Rutas Detectadas", data.get("routes_detected", 0))

                    with m3:
                        # Rutas nuevas creadas
                        st.metric("Rutas Creadas", data.get("routes_created", 0))
                    
                    with m4:
                        # Rutas que ya existían y se activaron
                        st.metric("Rutas Actualizadas", data.get("routes_updated", 0))
                    
                    with m5:
                        # Conteo de la lista de errores
                        error_list = data.get("errors", [])
                        st.metric("Errores", len(error_list))
                    
                    # Segunda fila para Zonas 
                    st.write("")
                    z1, z2 = st.columns(2)
                    with z1:
                        st.info(f"Zonas Creadas: {data.get('zones_created', 0)}")
                    with z2:
                        st.info(f"Zonas Actualizadas: {data.get('zones_updated', 0)}")

                    # Manejo de errores (backend devuelve una lista en 'errors')
                    error_list = data.get("errors", [])
                    if error_list:
                        with st.expander(f"Ver {len(error_list)} detalle(s) de errores"):
                            for error in error_list:
                                st.error(error)
                                
                else:
                    st.error(f"Error: {response.json().get('detail', 'Error desconocido')}")
            except Exception as e:
                st.error(f"Error de conexión: {str(e)}")