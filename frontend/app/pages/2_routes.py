import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime

# Configuración de URL desde variables de entorno 
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Gestión de Rutas", layout="wide")

st.title("Gestión de Rutas (Routes)")

# Funciones de ayuda para conectar con el Backend
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
            # Ordenar por nombre para mejor visualización
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

# ============================================
# SECCIÓN 1: FILTROS DE BÚSQUEDA
# ============================================
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
            refresh_button = st.button("Refrescar", use_container_width=True, key="refresh_button")

# Convertir filtros
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

# ============================================
# SECCIÓN 2: TABLA DE RUTAS
# ============================================
st.subheader("Rutas Registradas")

# Obtener datos con filtros
filtered_routes_data = get_filtered_routes(active=active_filter, pickup=pickup_filter, dropoff=dropoff_filter)

if filtered_routes_data:
    # Enriquecer datos con información de zonas
    enriched_data = []
    for route in filtered_routes_data:
        pickup_zone = get_zone_info(route.get("pickup_zone_id"))
        dropoff_zone = get_zone_info(route.get("dropoff_zone_id"))
        
        enriched_data.append({
            "ID": route.get("id", ""),
            "Nombre": route.get("name", ""),
            "Origen": f"{pickup_zone.get('zone_name', 'N/A') if pickup_zone else 'N/A'} (ID: {route.get('pickup_zone_id')})",
            "Destino": f"{dropoff_zone.get('zone_name', 'N/A') if dropoff_zone else 'N/A'} (ID: {route.get('dropoff_zone_id')})",
            "Activa": "Sí" if route.get("active", False) else "No",
            "Creada": route.get("created_at", "").split("T")[0] if route.get("created_at") else ""
        })
    
    # Mostrar tabla
    df = pd.DataFrame(enriched_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.TextColumn(width="medium"),
            "Activa": st.column_config.TextColumn(width="small"),
        }
    )
    
    st.caption(f"Total: {len(filtered_routes_data)} rutas encontradas")
    
else:
    all_routes = get_all_routes_cached()
    if all_routes:
        st.info("No se encontraron rutas con los filtros seleccionados.")
        st.caption(f"Hay {len(all_routes)} rutas en el sistema")
    else:
        st.info("No hay rutas en el sistema. Crea la primera ruta usando el formulario abajo.")

st.markdown("---")

# ============================================
# SECCIÓN 3: CREAR/EDITAR/ELIMINAR
# ============================================
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
            # Preparar opciones para dropdown
            route_options = {}
            for route in all_routes:
                pickup_zone = get_zone_info(route.get("pickup_zone_id"))
                dropoff_zone = get_zone_info(route.get("dropoff_zone_id"))
                pickup_name = pickup_zone.get('zone_name', 'N/A') if pickup_zone else 'N/A'
                dropoff_name = dropoff_zone.get('zone_name', 'N/A') if dropoff_zone else 'N/A'
                
                route_options[route['id']] = f"{route['name']} ({pickup_name} → {dropoff_name})"
            
            selected_id = st.selectbox(
                "Selecciona una ruta para editar",
                options=list(route_options.keys()),
                format_func=lambda x: route_options[x],
                key="edit_route_select"
            )
            
            selected_route = next((r for r in all_routes if r['id'] == selected_id), None)
            
            if selected_route:
                st.info(f"Editando ruta: {selected_route['name']}")
                
                with st.form("edit_route_form"):
                    zones = get_zones()
                    zone_options = {z['id']: f"{z['zone_name']} (ID: {z['id']})" for z in zones}
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        pu_id = st.selectbox(
                            "Zona de Origen", 
                            options=list(zone_options.keys()), 
                            format_func=lambda x: zone_options[x],
                            index=list(zone_options.keys()).index(selected_route['pickup_zone_id']) 
                            if selected_route['pickup_zone_id'] in zone_options else 0,
                            key="edit_pickup"
                        )
                    with col2:
                        do_id = st.selectbox(
                            "Zona de Destino", 
                            options=list(zone_options.keys()), 
                            format_func=lambda x: zone_options[x],
                            index=list(zone_options.keys()).index(selected_route['dropoff_zone_id']) 
                            if selected_route['dropoff_zone_id'] in zone_options else 0,
                            key="edit_dropoff"
                        )
                    
                    r_name = st.text_input(
                        "Nombre de la Ruta",
                        value=selected_route.get('name', ''),
                        key="edit_route_name"
                    )
                    r_active = st.checkbox(
                        "Activa",
                        value=selected_route.get('active', True),
                        key="edit_route_active"
                    )
                    
                    update_submitted = st.form_submit_button(
                        "Guardar Cambios",
                        type="secondary",
                        use_container_width=True,
                        key="update_route_button"
                    )
                    
                    if update_submitted:
                        errors = []
                        if pu_id == do_id:
                            errors.append("Error: Origen y destino no pueden ser iguales.")
                        if len(r_name.strip()) < 3:
                            errors.append("Error: Nombre mínimo 3 caracteres.")
                        
                        if errors:
                            for error in errors:
                                st.error(error)
                        else:
                            update_data = {}
                            if pu_id != selected_route.get('pickup_zone_id'):
                                update_data["pickup_zone_id"] = pu_id
                            if do_id != selected_route.get('dropoff_zone_id'):
                                update_data["dropoff_zone_id"] = do_id
                            if r_name.strip() != selected_route.get('name'):
                                update_data["name"] = r_name.strip()
                            if r_active != selected_route.get('active'):
                                update_data["active"] = r_active
                            
                            if update_data:
                                try:
                                    with st.spinner("Actualizando..."):
                                        response = requests.put(
                                            f"{API_URL}/routes/{selected_id}",
                                            json=update_data,
                                            timeout=10
                                        )
                                    
                                    if response.status_code == 200:
                                        st.success("Ruta actualizada!")
                                        st.rerun()
                                    else:
                                        error_detail = response.json().get('detail', 'Error')
                                        st.error(f"Error: {error_detail}")
                                except Exception as e:
                                    st.error(f"Error de conexión: {str(e)}")
                            else:
                                st.info("No se realizaron cambios.")

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