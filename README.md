# Demand Prediction Service - PSet 01
# Integrantes: Maria Emilia Cueva, Santiago Reategui, Raymond Portilla, Liam Huang

Este sistema permite gestionar zonas y rutas de transporte.

## Funcionamiento

Este proyecto es una plataforma de gestión de datos de transporte orquestada con Docker Compose, donde un Backend (FastAPI) y un Frontend (Streamlit) se integran para procesar y administrar rutas urbanas. El sistema permite realizar cargas masivas de archivos Parquet mediante un flujo ETL que filtra las rutas más frecuentes, garantiza la integridad de los datos creando zonas automáticamente y ofrece una interfaz completa para el control de registros (CRUD) bajo reglas de validación de negocio.

## Instrucciones de Uso y despliegue

| Accion | Comando |
| :--- | :--- |
| **Levantar todo** | `docker compose up --build` |
| **Bajar servicios** | `docker compose down` |
| **Correr Tests** | `docker compose exec api env PYTHONPATH=. pytest` |
| **Ver Logs** | `docker compose logs -f` |

---

## Estructura del Proyecto 
* **Backend:** FastAPI en puerto 8000. Gestiona CRUD de Zones, Routes y procesamiento Parquet. 
* **Frontend:** Streamlit en puerto 8501. Interfaz para gestion de datos y carga de archivos. 

---

## Especificacion de API (Endpoints) 
* `GET /health`: Verifica el estado del backend. 
* `GET /zones`: Lista zonas con filtros opcionales de active y borough. 
* `POST /routes`: Crea rutas validando que origen y destino existan en Zones. 
* `POST /uploads/trips-parquet`: Ingesta masiva desde archivos .parquet.

---

## Checklist de Requisitos (V hecho, F no hecho) 
* [V] Docker Compose levanta api y app correctamente.
* [V] Home muestra health del backend y navegacion. 
* [V] CRUD Zones funciona completo desde la UI. 
* [V] CRUD Routes funciona completo desde la UI. 
* [V] Upload parquet procesa y hace create/update via endpoints. 
* [V] README explica funcionamiento y despliegue. 
* [V] Evidencia en GitHub (issues/PR/tags) disponible.

---

## Reglas de Contribucion 
Se utiliza un flujo de trabajo basado en GitFlow simplificado. Cada persona tiene un rol asignado. Todo cambio debe ingresar mediante Pull Request a la rama main. Revisar `CONTRIBUTING.md` para mas detalles.