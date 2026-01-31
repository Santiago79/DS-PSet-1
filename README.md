# Demand Prediction Service - PSet 01
# Integrantes: Maria Emilia, Santiago Reategui, Raymond Portilla, Liam Huang

Este sistema permite gestionar zonas y rutas de transporte.

## Instrucciones de Uso

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
* [ ] Docker Compose levanta api y app correctamente.
* [ ] Home muestra health del backend y navegacion. 
* [ ] CRUD Zones funciona completo desde la UI. 
* [ ] CRUD Routes funciona completo desde la UI. 
* [ ] Upload parquet procesa y hace create/update via endpoints. 
* [ ] README explica funcionamiento y despliegue. 
* [ ] Evidencia en GitHub (issues/PR/tags) disponible.

---

## Reglas de Contribucion 
Se utiliza un flujo de trabajo basado en GitFlow simplificado. Cada persona tiene un rol asignado. Todo cambio debe ingresar mediante Pull Request a la rama main. Revisar `CONTRIBUTING.md` para mas detalles.