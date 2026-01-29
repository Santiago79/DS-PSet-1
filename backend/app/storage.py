# Diccionario para almacenar las zonas [cite: 17, 27]
# Formato: {id_zona (int): objeto_zone (dict)}
zones_db = {}

# Diccionario para almacenar las rutas [cite: 17, 35]
# Formato: {id_ruta (int/uuid): objeto_route (dict)}
routes_db = {}

# Contador opcional para generar IDs de rutas si el compañero de Routes lo necesita
route_id_counter = 1