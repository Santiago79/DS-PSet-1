import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime

# Configuración de URL 
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Gestión de Rutas", layout="wide")

st.title("Gestión de Rutas (Routes)")

# Funciones para conectar con el Backend
@st.cache_data(ttl=10)
def get_all_routes_cached():
    return get_all_routes()

def get_all_routes():
    try:
        response = requests.get(f"{API_URL}/routes", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_filtered_routes(active=None, pickup=None, dropoff=None):
    params = {}
    if active is not None:
        params["active"] = active
    if pickup is not None and pickup != "Todos":
        params["pickup_zone_id"] = pickup
    if dropoff is not None and dropoff != "Todos":
        params["dropoff_zone_id"] = dropoff
    
    try:
        response = requests.get(f"{API_URL}/routes", params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_zones():
    try:
        response = requests.get(f"{API_URL}/zones", timeout=5)
        if response.status_code == 200:
            zones = response.json()
            return sorted(zones, key=lambda x: x.get('zone_name', ''))
        return []
    except:
        return []

def get_zone_info(zone_id):
    try:
        response = requests.get(f"{API_URL}/zones/{zone_id}", timeout=3)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Verificar estado del backend
try:
    health_response = requests.get(f"{API_URL}/health", timeout=2)
    if health_response.status_code == 200:
        st.sidebar.success("Backend conectado")
    else:
        st.sidebar.error("Backend con problemas")
except:
    st.sidebar.error("Backend no disponible")

# FILTROS DE BÚSQUEDA
st.subheader("Buscar Rutas")

# Obtener todas las zonas para los dropdowns
zones = get_zones()

# Contenedor para filtros
with st.container():
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        selected_status = st.selectbox(
            "Estado",
            ["Todos", "Activas", "Inactivas"],
            help="Filtrar por estado activo/inactivo",
            key="status_filter_select"
        )
    
    with col2:
        # Preparar opciones para dropdown de pickup
        pickup_options = ["Todos"] + [{"id": z["id"], "name": f"{z['zone_name']} (ID: {z['id']})"} for z in zones]
        selected_pickup = st.selectbox(
            "Zona Origen",
            options=["Todos"] + [z["id"] for z in zones],
            format_func=lambda x: "Todos" if x == "Todos" else next((f"{z['zone_name']} (ID: {z['id']})" for z in zones if z["id"] == x), f"ID: {x}"),
            key="pickup_filter_select"
        )
    
    with col3:
        # Preparar opciones para dropdown de dropoff
        selected_dropoff = st.selectbox(
            "Zona Destino",
            options=["Todos"] + [z["id"] for z in zones],
            format_func=lambda x: "Todos" if x == "Todos" else next((f"{z['zone_name']} (ID: {z['id']})" for z in zones if z["id"] == x), f"ID: {x}"),
            key="dropoff_filter_select"
        )
    
    with col4:
        st.write("")
        col_search, col_refresh = st.columns(2)
        with col_search:
            search_button = st.button("Buscar", type="primary", use_container_width=True, key="search_button")
        with col_refresh:
            refresh_button = st.button("🔄", use_container_width=True, key="refresh_button")

active_filter = None
if selected_status == "Activas":
    active_filter = True
elif selected_status == "Inactivas":
    active_filter = False

pickup_filter = selected_pickup if selected_pickup != "Todos" else None
dropoff_filter = selected_dropoff if selected_dropoff != "Todos" else None

# Botón de búsqueda o refrescar
if search_button or refresh_button:
    st.rerun()

# TABLA DE RUTAS
st.subheader("Rutas Registradas")

filtered_routes_data = get_filtered_routes(active=active_filter, pickup=pickup_filter, dropoff=dropoff_filter)

if filtered_routes_data:
    enriched_data = []
    for route in filtered_routes_data:
        pickup_zone = get_zone_info(route.get("pickup_zone_id"))
        dropoff_zone = get_zone_info(route.get("dropoff_zone_id"))
        
        enriched_data.append({
            "ID": route.get("id", ""),
            "Nombre": route.get("name", ""),
            "Origen": f"{pickup_zone.get('zone_name', 'N/A') if pickup_zone else 'N/A'} (ID: {route.get('pickup_zone_id')})",
            "Destino": f"{dropoff_zone.get('zone_name', 'N/A') if dropoff_zone else 'N/A'} (ID: {route.get('dropoff_zone_id')})",
            "Estado": "Activa" if route.get("active", False) else "Inactiva",
            "Creada": route.get("created_at", "").split("T")[0] if route.get("created_at") else ""
        })
    
    df = pd.DataFrame(enriched_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.TextColumn(width="medium"),
            "Estado": st.column_config.TextColumn(width="small"), 
        }
    )
    st.caption(f"Total: {len(filtered_routes_data)} rutas encontradas")


# CREAR/EDITAR/ELIMINAR
st.subheader("Gestionar Rutas")

# Usar radio buttons
tab_options = ["Crear Ruta", "Editar Ruta", "Eliminar Ruta"]
selected_tab = st.radio(
    "Selecciona una acción:",
    tab_options,
    horizontal=True,
    key="route_management_tab"
)
# TAB 1: CREAR RUTA
if selected_tab == "Crear Ruta":
    with st.container():
        st.markdown("### Crear Nueva Ruta")
        
        zones = get_zones()
        
        if not zones:
            st.warning("No hay zonas disponibles. Crea zonas primero en la página de Zonas.")
        
        else:
            with st.form("create_route_form", clear_on_submit=True):
                zone_options = {z['id']: f"{z['zone_name']} (ID: {z['id']}, {z['borough']})" for z in zones}
                
                col1, col2 = st.columns(2)
                with col1:
                    pu_id = st.selectbox(
                        "Zona de Origen *", 
                        options=list(zone_options.keys()), 
                        format_func=lambda x: zone_options[x],
                        key="create_pickup"
                    )
                with col2:
                    do_id = st.selectbox(
                        "Zona de Destino *", 
                        options=list(zone_options.keys()), 
                        format_func=lambda x: zone_options[x],
                        key="create_dropoff"
                    )
                
                r_name = st.text_input(
                    "Nombre de la Ruta *", 
                    placeholder="Ej: Manhattan to Brooklyn Express",
                    help="Mínimo 3 caracteres",
                    key="create_route_name"
                )
                r_active = st.checkbox("Activa", value=True, key="create_route_active")
                
                submitted = st.form_submit_button("Crear Ruta", type="primary", use_container_width=True)
                
                if submitted:
                    errors = []
                    if pu_id == do_id:
                        errors.append("Error: La zona de origen y destino no pueden ser iguales.")
                    if len(r_name.strip()) < 3:
                        errors.append("Error: El nombre debe tener al menos 3 caracteres.")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        new_route = {
                            "pickup_zone_id": int(pu_id),
                            "dropoff_zone_id": int(do_id),
                            "name": r_name.strip(),
                            "active": r_active
                        }
                        
                        try:
                            with st.spinner("Creando ruta..."):
                                response = requests.post(f"{API_URL}/routes", json=new_route, timeout=10)
                            
                            if response.status_code in [200, 201]:
                                st.success("Ruta creada exitosamente!")
                                st.rerun()
                            elif response.status_code == 400:
                                error_detail = response.json().get('detail', 'Error de validación')
                                st.error(f"Error de validación: {error_detail}")
                            elif response.status_code == 404:
                                st.error("Error: Una de las zonas no existe.")
                            else:
                                st.error(f"Error del servidor: {response.status_code}")
                        except requests.exceptions.ConnectionError:
                            st.error("No se puede conectar al backend.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

# TAB 2: EDITAR RUTA
elif selected_tab == "Editar Ruta":
    with st.container():
        st.markdown("### Editar Ruta Existente")
        
        all_routes = get_all_routes()
        
        if not all_routes:
            st.info("No hay rutas disponibles para editar.")
        else:
            route_options = {}
            for route in all_routes:
                route_options[route['id']] = f"ID {route['id']}: {route['name']}"
            
            selected_id = st.selectbox(
                "Selecciona una ruta para editar",
                options=list(route_options.keys()),
                format_func=lambda x: route_options[x],
                key="edit_route_selector_main"
            )
            
            selected_route = next((r for r in all_routes if r['id'] == selected_id), None)
            
            if selected_route:
                st.info(f"Editando ruta: **{selected_route['name']}**")
                
                with st.form(key=f"edit_form_route_{selected_id}"):
                    zones = get_zones()
                    zone_options = {z['id']: f"{z['zone_name']} (ID: {z['id']})" for z in zones}
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        # Buscamos el índice actual para el origen
                        pu_index = 0
                        ids_list = list(zone_options.keys())
                        if selected_route['pickup_zone_id'] in ids_list:
                            pu_index = ids_list.index(selected_route['pickup_zone_id'])

                        pu_id = st.selectbox(
                            "Zona de Origen", 
                            options=ids_list, 
                            format_func=lambda x: zone_options[x],
                            index=pu_index,
                            key=f"pu_{selected_id}" 
                        )
                    with col2:
                        # Buscamos el índice actual para el destino
                        do_index = 0
                        if selected_route['dropoff_zone_id'] in ids_list:
                            do_index = ids_list.index(selected_route['dropoff_zone_id'])

                        do_id = st.selectbox(
                            "Zona de Destino", 
                            options=ids_list, 
                            format_func=lambda x: zone_options[x],
                            index=do_index,
                            key=f"do_{selected_id}"
                        )
                    
                    r_name = st.text_input(
                        "Nombre de la Ruta",
                        value=selected_route.get('name', ''),
                        key=f"name_{selected_id}"
                    )
                    
                    r_active = st.checkbox(
                        "Activa",
                        value=bool(selected_route.get('active', True)),
                        key=f"active_{selected_id}" 
                    )
                    
                    update_submitted = st.form_submit_button(
                        "Guardar Cambios",
                        type="primary",
                        use_container_width=True
                    )
                    
                    if update_submitted:
                        # Validaciones
                        if pu_id == do_id:
                            st.error("Error: Origen y destino no pueden ser iguales.")
                        elif len(r_name.strip()) < 3:
                            st.error("Error: El nombre debe tener al menos 3 caracteres.")
                        else:
                            update_data = {
                                "pickup_zone_id": int(pu_id),
                                "dropoff_zone_id": int(do_id),
                                "name": r_name.strip(),
                                "active": r_active
                            }
                            
                            try:
                                with st.spinner("Actualizando ruta..."):
                                    response = requests.put(
                                        f"{API_URL}/routes/{selected_id}",
                                        json=update_data,
                                        timeout=10
                                    )
                                
                                if response.status_code == 200:
                                    st.success("¡Ruta actualizada exitosamente!")
                                    get_all_routes_cached.clear() # Limpiar cache de la tabla
                                    st.rerun()
                                else:
                                    st.error(f"Error: {response.text}")
                            except Exception as e:
                                st.error(f"Error de conexión: {str(e)}")

# TAB 3: ELIMINAR RUTA
else:
    with st.container():
        st.markdown("### Eliminar Ruta")
        
        all_routes = get_all_routes()
        
        if not all_routes:
            st.info("No hay rutas disponibles para eliminar.")
        else:
            route_options = {r['id']: f"{r['name']} (ID: {r['id']})" for r in all_routes}
            selected_id = st.selectbox(
                "Selecciona una ruta para eliminar",
                options=list(route_options.keys()),
                format_func=lambda x: route_options[x],
                key="delete_route_select"
            )
            
            selected_route = next((r for r in all_routes if r['id'] == selected_id), None)
            
            if selected_route:
                st.warning(f"¿Eliminar ruta: {selected_route['name']}?")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Eliminar", type="primary", use_container_width=True, key="delete_button"):
                        try:
                            with st.spinner("Eliminando..."):
                                response = requests.delete(f"{API_URL}/routes/{selected_id}", timeout=10)
                            
                            if response.status_code == 204:
                                st.success("Ruta eliminada!")
                                st.rerun()
                            else:
                                st.error(f"Error: {response.status_code}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                with col2:
                    if st.button("Cancelar", use_container_width=True, key="cancel_button"):
                        st.rerun()