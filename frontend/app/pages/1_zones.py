import streamlit as st
import requests
import os
import pandas as pd

# Configuración de URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Gestión de Zonas", layout="wide")

st.title("Gestión de Zonas (Zones)")

# Funciones para conectar con el Backend
@st.cache_data(ttl=10)
def get_all_zones_cached():
    """Obtiene TODAS las zonas (sin filtros, con cache)"""
    return get_all_zones()

def get_all_zones():
    """Obtiene TODAS las zonas sin filtros"""
    try:
        response = requests.get(f"{API_URL}/zones", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("No se puede conectar al backend. Asegúrate de que esté ejecutándose.")
        return []
    except Exception as e:
        st.error(f"Error al cargar zonas: {str(e)}")
        return []

def get_filtered_zones(active=None, borough=None):
    """Obtiene zonas con filtros opcionales (solo para la tabla)"""
    params = {}
    if active is not None:
        params["active"] = active
    if borough and borough != "Todos":
        params["borough"] = borough
    
    try:
        response = requests.get(f"{API_URL}/zones", params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except:
        return []

# Verificar estado del backend en sidebar
try:
    health_response = requests.get(f"{API_URL}/health", timeout=2)
    if health_response.status_code == 200:
        st.sidebar.success("Backend conectado")
    else:
        st.sidebar.error("Backend con problemas")
except:
    st.sidebar.error("Backend no disponible")

#FILTROS DE BÚSQUEDA
st.subheader("Buscar Zonas")

# Obtener todas las zonas para los borough options
all_zones_data = get_all_zones_cached()

# Contenedor para filtros
with st.container():
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        @st.cache_data(ttl=2)  # Cache corto para que se actualice rápido
        def get_boroughs():
            zones = get_all_zones()
            boroughs = list(set([z.get("borough") for z in zones if z.get("borough")]))
            return sorted([b for b in boroughs if b])
        
        boroughs_list = get_boroughs()
        borough_options = ["Todos"] + boroughs_list if boroughs_list else ["Todos"]
        
        selected_borough = st.selectbox(
            "Municipio (Borough)",
            borough_options,
            help="Filtrar por municipio",
            key="borough_filter_select"
        )
    
    with col2:
        selected_status = st.selectbox(
            "Estado",
            ["Todos", "Activas", "Inactivas"],
            help="Filtrar por estado activo/inactivo",
            key="status_filter_select"
        )
    
    with col3:
        st.write("")
        search_button = st.button("Buscar", type="primary", use_container_width=True, key="search_button")
    
    with col4:
        st.write("")
        refresh_button = st.button("🔄", use_container_width=True, key="refresh_button")

# Convertir filtros a parámetros de API
active_filter = None
if selected_status == "Activas":
    active_filter = True
elif selected_status == "Inactivas":
    active_filter = False

borough_filter = selected_borough if selected_borough != "Todos" else None

# Botón de búsqueda o refrescar
if search_button or refresh_button:
    st.rerun()


# TABLA DE ZONAS
st.subheader("Zonas Registradas")

# Obtener datos con filtros
filtered_zones_data = get_filtered_zones(active=active_filter, borough=borough_filter)

if filtered_zones_data:
    # Preparar datos para la tabla
    table_data = []
    for zone in filtered_zones_data:
        table_data.append({
            "ID": zone.get("id", ""),
            "Nombre": zone.get("zone_name", ""),
            "Municipio": zone.get("borough", ""),
            "Zona Servicio": zone.get("service_zone", ""),
            "Estado": "Activa" if zone.get("active", False) else "Inactiva",
            "Creada": zone.get("created_at", "").split("T")[0] if zone.get("created_at") else ""
        })
    
    # Mostrar tabla
    df = pd.DataFrame(table_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn(format="%d"),
            "Estado": st.column_config.TextColumn(width="small"),
        }
    )

    st.caption(f"Mostrando {len(filtered_zones_data)} de {len(all_zones_data)} zonas totales")
    
else:
    if all_zones_data:
        st.info("No se encontraron zonas con los filtros seleccionados.")
        st.caption(f"Hay {len(all_zones_data)} zonas en el sistema")
    else:
        st.info("No hay zonas en el sistema. Crea la primera zona usando el formulario abajo.")

st.markdown("---")


# CREAR/EDITAR/ELIMINAR
st.subheader("Gestionar Zonas")

tab_options = ["Crear Zona", "Editar Zona", "Eliminar Zona"]
selected_tab = st.radio(
    "Selecciona una acción:",
    tab_options,
    horizontal=True,
    key="zone_management_tab"
)

# CREAR ZONA
if selected_tab == "Crear Zona":
    with st.container():
        st.markdown("### Crear Nueva Zona")
        
        with st.form("create_zone_form", clear_on_submit=True):
            col_id, col_name = st.columns(2)
            
            with col_id:
                zone_id = st.number_input(
                    "ID de Zona *",
                    min_value=1,
                    step=1,
                    value=100,
                    help="Número positivo único",
                    key="create_zone_id"
                )
            
            with col_name:
                zone_name = st.text_input(
                    "Nombre de Zona *",
                    placeholder="Ej: Upper East Side",
                    help="Nombre de la zona",
                    key="create_zone_name"
                )
            
            col_borough, col_service = st.columns(2)
            
            with col_borough:
                borough = st.text_input(
                    "Municipio (Borough) *",
                    placeholder="Ej: Manhattan",
                    help="Uno de los 5 boroughs de NYC",
                    key="create_borough"
                )
            
            with col_service:
                service_zone = st.text_input(
                    "Zona de Servicio",
                    value="Unknown",
                    placeholder="Dejar vacío para 'Unknown'",
                    help="Clasificación de la zona (default: 'Unknown')",
                    key="create_service_zone"
                )
            
            active = st.checkbox("Activa", value=True, help="Zona disponible para uso", key="create_active")
            
            # Botón de submit
            submitted = st.form_submit_button(
                "Crear Zona", 
                type="primary", 
                use_container_width=True,
                key="create_zone_button"
            )
            
            if submitted:
                # Validaciones
                errors = []
                if not borough.strip():
                    errors.append("El municipio (borough) es obligatorio")
                if not zone_name.strip():
                    errors.append("El nombre de zona es obligatorio")
                if zone_id <= 0:
                    errors.append("El ID debe ser un número positivo")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Preparar datos para enviar
                    new_zone = {
                        "id": int(zone_id),
                        "borough": borough.strip(),
                        "zone_name": zone_name.strip(),
                        "service_zone": service_zone.strip() if service_zone.strip() else "Unknown",
                        "active": active
                    }
                    
                    # Enviar al backend
                    try:
                        with st.spinner("Creando zona..."):
                            response = requests.post(
                                f"{API_URL}/zones", 
                                json=new_zone,
                                timeout=10
                            )
                        
                        if response.status_code == 201:
                            st.success("Zona creada exitosamente!")
                            st.balloons()
                            st.rerun()
                        elif response.status_code == 400:
                            error_detail = response.json().get('detail', 'Error desconocido')
                            st.error(f"Error: {error_detail}")
                        else:
                            st.error(f"Error inesperado: {response.status_code}")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("No se puede conectar al backend. Verifica que esté ejecutándose.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# EDITAR ZONA
elif selected_tab == "Editar Zona":
    with st.container():
        st.markdown("### Editar Zona Existente")
        
        all_zones_for_edit = get_all_zones()
        
        if not all_zones_for_edit:
            st.info("No hay zonas disponibles para editar.")
        else:
            # Selector de zona
            zone_options = {z['id']: f"ID: {z['id']} | {z['zone_name']} ({z['borough']})" 
                           for z in all_zones_for_edit}
            
            selected_id = st.selectbox(
                "Selecciona una zona para editar",
                options=list(zone_options.keys()),
                format_func=lambda x: zone_options[x],
                key="edit_zone_selector_main"
            )
            
            selected_zone = next((z for z in all_zones_for_edit if z['id'] == selected_id), None)
            
            if selected_zone:
                st.info(f"Editando: **{selected_zone['zone_name']}**")
                
                with st.form(key=f"edit_form_{selected_id}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_zone_name = st.text_input(
                            "Nombre de Zona",
                            value=selected_zone.get('zone_name', ''),
                            key=f"name_{selected_id}"
                        )
                        new_borough = st.text_input(
                            "Municipio (Borough)",
                            value=selected_zone.get('borough', ''),
                            key=f"boro_{selected_id}"
                        )
                    
                    with col2:
                        new_service_zone = st.text_input(
                            "Zona de Servicio",
                            value=selected_zone.get('service_zone', 'Unknown'),
                            key=f"serv_{selected_id}"
                        )
                        new_active = st.checkbox(
                            "Activa",
                            value=bool(selected_zone.get('active', True)),
                            key=f"act_{selected_id}"
                        )
                    
                    update_submitted = st.form_submit_button("Guardar Cambios", type="primary")
                    
                    if update_submitted:
                        payload = {
                            "zone_name": new_zone_name.strip(),
                            "borough": new_borough.strip(),
                            "service_zone": new_service_zone.strip() if new_service_zone.strip() else "Unknown",
                            "active": new_active
                        }
                        
                        try:
                            response = requests.put(
                                f"{API_URL}/zones/{selected_id}",
                                json=payload,
                                timeout=10
                            )
                            if response.status_code == 200:
                                st.success("¡Zona actualizada!")
                                get_all_zones_cached.clear()
                                st.rerun()
                            else:
                                st.error(f"Error: {response.text}")
                        except Exception as e:
                            st.error(f"Error de conexión: {e}")

# ELIMINAR ZONA 
else:
    with st.container():
        st.markdown("### Eliminar Zona")
        
        # Obtener TODAS las zonas para eliminar
        all_zones_for_delete = get_all_zones()
        
        if not all_zones_for_delete:
            st.info("No hay zonas disponibles para eliminar.")
        else:
            # Selector de zona para eliminar
            zone_options_del = {z['id']: f"{z['id']} - {z['zone_name']} ({z['borough']}) - {'Activa' if z.get('active') else 'Inactiva'}" 
                               for z in all_zones_for_delete}
            selected_id_del = st.selectbox(
                "Selecciona una zona para eliminar",
                options=list(zone_options_del.keys()),
                format_func=lambda x: zone_options_del[x],
                key="delete_zone_select",
                index=0 if zone_options_del else None
            )
            
            selected_zone_del = next((z for z in all_zones_for_delete if z['id'] == selected_id_del), None)
            
            if selected_zone_del:
                # Mostrar información de la zona a eliminar
                st.warning("**Zona seleccionada para eliminar:**")
                
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.metric("ID", selected_id_del)
                    st.metric("Nombre", selected_zone_del.get('zone_name', ''))
                with col_info2:
                    st.metric("Municipio", selected_zone_del.get('borough', ''))
                    st.metric("Estado", "Activa" if selected_zone_del.get('active') else "Inactiva")
                
                # Botón de eliminación directa
                st.divider()
                st.markdown("### Confirmar eliminación")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("Eliminar Zona", 
                               type="primary",
                               use_container_width=True,
                               key="delete_zone_button"):
                        
                        try:
                            with st.spinner("Eliminando zona..."):
                                response = requests.delete(
                                    f"{API_URL}/zones/{selected_id_del}",
                                    timeout=10
                                )
                            
                            if response.status_code == 204:
                                st.success("Zona eliminada exitosamente!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"Error al eliminar: {response.status_code}")
                        except Exception as e:
                            st.error(f"Error de conexión: {str(e)}")
                
                with col_btn2:
                    if st.button("Cancelar", use_container_width=True, key="cancel_delete"):
                        st.rerun()

