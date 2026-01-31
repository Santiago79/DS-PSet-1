import streamlit as st
import requests
import os

#Lista de Rutas
# Configuracion de URL desde variables de entorno 
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Gestion de Rutas", layout="wide")

st.title("Gestion de Rutas (Routes)")

# Funciones de ayuda para conectar con el Backend
def get_zones():
    try:
        response = requests.get(f"{API_URL}/zones")
        return response.json() if response.status_code == 200 else []
    except:
        return []
    
def get_routes(active=None, pickup=None, dropoff=None):
    # Parametros
    params = {
        "active": active,
        "pickup_zone_id": pickup,
        "dropoff_zone_id": dropoff
    }
    
    # Filtramos solo los valores que no son None o 0
    clean_params = {k: v for k, v in params.items() if v is not None and v != 0}
    
    try:
        response = requests.get(f"{API_URL}/routes", params=clean_params)
        response.raise_for_status() # Lanza una excepción si hay error (4xx o 5xx)
        return response.json()
    except (requests.RequestException, ValueError):
        return []

# Seccion de Filtros 
st.sidebar.header("Filtros de Busqueda")
f_active = st.sidebar.selectbox("Estado", [None, True, False], format_func=lambda x: "Todos" if x is None else ("Activo" if x else "Inactivo"))
f_pickup = st.sidebar.number_input("ID Zona Origen", min_value=0, step=1)
f_dropoff = st.sidebar.number_input("ID Zona Destino", min_value=0, step=1)

# Listado de Rutas
routes_data = get_routes(active=f_active, 
                         pickup=f_pickup if f_pickup > 0 else None, 
                         dropoff=f_dropoff if f_dropoff > 0 else None)
if routes_data:
    st.subheader("Rutas Registradas")
    st.dataframe(routes_data, use_container_width=True)
else:
    st.info("No se encontraron rutas con los filtros seleccionados.")

st.divider()

# Formulario de Creacion 
st.subheader("Crear Nueva Ruta")
with st.form("create_route_form"):
    zones = get_zones()
    zone_options = {z['id']: f"{z['id']} - {z['zone_name']}" for z in zones}
    
    col1, col2 = st.columns(2)
    with col1:
        pu_id = st.selectbox("Zona de Origen (Pickup)", options=list(zone_options.keys()), format_func=lambda x: zone_options[x])
    with col2:
        do_id = st.selectbox("Zona de Destino (Dropoff)", options=list(zone_options.keys()), format_func=lambda x: zone_options[x])
    
    r_name = st.text_input("Nombre de la Ruta (Min. 3 caracteres)")
    r_active = st.checkbox("Activa", value=True)
    
    submitted = st.form_submit_button("Guardar Ruta")
    
    if submitted:
        if pu_id == do_id:
            st.error("Error: La zona de origen y destino no pueden ser iguales[Error 400].")
        elif len(r_name) < 3:
            st.error("Error: El nombre debe tener al menos 3 caracteres[Error 400].")
        else:
            new_route = {
                "pickup_zone_id": pu_id,
                "dropoff_zone_id": do_id,
                "name": r_name,
                "active": r_active
            }
            res = requests.post(f"{API_URL}/routes", json=new_route)
            if res.status_code == 200 or res.status_code == 201:
                st.success("Ruta creada exitosamente.")
                st.rerun()
            else:
                st.error(f"Error al crear: {res.json().get('detail', 'Error desconocido')}")
