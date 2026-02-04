# Guia de Contribucion: DS-PSet-1

Hola, esta guia describe la forma en que trabajamos y como mantenemos el orden en el proyecto. El objetivo es que todos estemos alineados para evitar conflictos de codigo.

## Metodologia de Trabajo

Nuestra organizacion se basa en tres cosas:

1. **Issues como Prioridad:** Utilizamos los Issues de GitHub para listar las tareas pendientes. Antes de empezar algo, revisamos que este documentado ahi para enfocarnos en lo que realmente falta.
2. **Uso de Ramas (Branches):** No trabajamos directamente sobre la rama principal. Cada vez que implementamos una funcionalidad, creamos una rama nueva (por ejemplo, `feature/nueva-funcionalidad`).
3. **Commits Claros:** Los mensajes de commit deben ser lo mas entendibles posibles para que cualquiera pueda leer el historial y saber que se cambio sin necesidad de revisar linea por linea.

---

## Organizacion por Roles

El proyecto se dividio en cuatro areas de responsabilidad para cubrir todo el flujo de datos:

### Persona 1 (Santiago Reategui): Backend de Zonas
Responsable de la logica central de ubicaciones:
* Implementacion de CRUD completo para `/zones` (POST, GET, PUT, DELETE).
* Creacion de filtros para las consultas de zonas.
* Definicion de Schemas de validacion: `ZoneCreate` y `ZoneUpdate`.
* Ejecucion y mantenimiento de los tests de zonas.

### Persona 2 (Raymond Portilla): Backend de Rutas
Responsable de la logica de trayectos y validaciones de negocio:
* Endpoints de `/routes` con filtros y CRUD.
* Validacion de integridad: asegurar que el `pickup_zone_id` existe antes de crear la ruta.
* Validacion de logica: impedir que el origen y el destino sean iguales (`pickup != dropoff`).
* Creacion de tests especificos para rutas.

### Persona 3 (Maria Emilia Cueva): Frontend de Zonas
Responsable de la experiencia de usuario y navegacion inicial:
* Configuracion de `Home.py` y el sistema de navegacion en Streamlit.
* Interfaz de usuario (UI) completa para la gestion de zonas y rutas
* Gestion de estados de error en la interfaz para informar al usuario.
* Implementacion de las peticiones HTTP desde el frontend hacia el backend.

### Persona 4 (Liam Huang): DevOps y Carga Masiva (Parquet)
Responsable de la infraestructura, integracion y despliegue:
* Configuracion y mantenimiento de `docker-compose.yml` y los `Dockerfiles`.
* Implementacion del proceso de ingesta: endpoint `POST /uploads/trips-parquet`.
* Creacion de la pagina de carga de archivos Parquet en Streamlit con resumen de resultados.
* Redaccion del `README.md`, `CONTRIBUTING.MD` del proyecto.

---
## Evidencias
No olvidarse de subir algunas evidencias de su trabajo (capturas, logs, etc). 
Las imagenes deben ser subidas a la carpeta de evidence_images.


## Estandares de Codigo

* **Docker:** Antes de subir cambios, asegurense de que los contenedores levantan correctamente con `docker compose up --build`.
* **Ramas:** Al terminar una tarea, abran un Pull Request para que el resto del equipo pueda revisar los cambios antes de integrarlos.