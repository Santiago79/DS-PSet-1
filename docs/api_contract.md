# API Contract - DS-PSet-1

Este documento establece las especificaciones técnicas para la comunicación entre el Backend (FastAPI) y el Frontend (Streamlit), definiendo los modelos de datos y los puntos de acceso del sistema.

## Estándares de Comunicación

- **URL Base:** http://localhost:8000  
- **Formato de Intercambio:** JSON  
- **Convención de Nombres:** `snake_case` para atributos y parámetros  
- **Códigos de Estado HTTP:**
  - **200 OK:** Operación exitosa con retorno de datos
  - **201 Created:** Recurso creado exitosamente
  - **400 Bad Request:** Error en los datos de entrada o validación de negocio
  - **404 Not Found:** El recurso solicitado no existe en la base de datos
  - **500 Internal Server Error:** Error no controlado en el servidor

---

## 1. Gestión de Zonas (Zones)

### GET /zones
Recupera el listado de zonas registradas.

**Parámetros de consulta (opcionales):**
- `borough` (string): Filtrar por distrito

**Respuesta exitosa (200 OK):**
```
[
  {
    "id": 1,
    "name": "Newark Airport",
    "borough": "EWR"
  }
]

```

### POST /zones

Registra una nueva zona en el sistema.

**Cuerpo de la petición (JSON):**
```
{
  "name": "string",
  "borough": "string"
}

```
Respuesta (201 Created):
Objeto de zona completo con ID generado.

## 2. Gestión de Rutas (Routes)

### POST /routes
Crea una nueva conexión entre dos zonas existentes.

**Cuerpo de la petición (JSON):**
```
{
  "pickup_zone_id": 1,
  "dropoff_zone_id": 10,
  "distance": 5.4,
  "frecuency": 1
}
```
**Reglas de validación:**
- `pickup_zone_id` debe ser distinto de `dropoff_zone_id`

### GET /routes
Consulta el listado de rutas procesadas.

**Parámetros de consulta (opcionales):**
- `pickup_id`
- `dropoff_id`

## 3. Ingesta de Datos (Parquet)

### POST /uploads/trips-parquet
Endpoint especializado para la carga masiva de archivos.

**Tipo de contenido:**  
`multipart/form-data`

**Campos requeridos:**
- `file`: Archivo binario en formato `.parquet`
- `top_n` (integer): Número de rutas con mayor frecuencia a procesar
- `mode` (string): Método de inserción (`"upsert"` o `"create"`)

**Respuesta exitosa (200 OK):**
```
{
  "status": "success",
  "summary": {
    "rows_processed": 1000,
    "routes_created": 45,
    "routes_updated": 5,
    "zones_created_placeholder": 2
  }
}
```
## 4. Verificación de Sistema (Health)

### GET /health
Verifica la disponibilidad de la API y la conexión a la base de datos.

**Respuesta (200 OK):**
```
{
  "status": "active",
  "version": "1.0.0",
  "database": "connected"
}
```