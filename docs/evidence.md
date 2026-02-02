# Evidencias de Implementación - Proyecto DS-PSet-1

Este documento centraliza las pruebas de funcionamiento de los módulos desarrollados por el equipo, así como la gestión del flujo de trabajo en GitHub.

---

## Gestión del Proyecto (GitHub)

En esta sección se documenta el uso de herramientas de colaboración para el desarrollo del proyecto.

* **Issues:** Evidencia del uso de tickets para el seguimiento de tareas pendientes y objetivos.

![Issues abiertos hasta 5:58pm del 01/02/26](evidence_images/Captura-evidencia-issues-558pm.png)
![Issues cerrados hasta 6:00pm del 01/02/26](evidence_images/Evidencia-closed-issues-600pm.png)

* **Pull Requests:** Evidencia de la integración de ramas y revisión de código por parte del equipo.
![Pull Requests abiertos](evidence_images/Evidencia-pr-601pm.png)
![Pull Requests cerrados](evidence_images/Evidencia-closed-pr-607pm.png)


---

## Evidencias por Integrante

Cada miembro del equipo es responsable de elegir y subir las capturas o logs que mejor representen el cumplimiento de sus objetivos técnicos.

### Persona 1: Backend de Zonas
*Espacio reservado para evidencias de: CRUD de zonas, Schemas de validación y resultados de tests unitarios.*
![Creación del esquema base del proyecto](evidence_images/estructuraBaseProyecto.png)
![Comprobar funcionamiento de backend con postman](evidence_images/postman.png)
![Actualizar por medio de postman una zona](evidence_images/postmanPUTreal.png)
![Verificar que la actualización de postman se ve en la página web](evidence_images/verificacionPostmanEnPagina.png)
![Tests correctos y sin errores al correrlos en consola](evidence_images/testsCorrectos.png)
![Datos sobre los tests ejecutados en consola](evidence_images/outputTestsParquet.png)
![Muestra de datos de zonas del parquet en la pagina web](evidence_images/listaPostParquetZones.png)
![Muestra de datos de routes del parquet en la pagina web](evidence_images/listaPostParquetRoutes.png)
---

### Persona 2: Backend de Rutas
*Espacio reservado para evidencias de: Validación de integridad de rutas (pickup/dropoff), testing de API con endpoints relacionado a rutas y schemas.*

**Testing de Health**
![Postman Health GET](evidence_images/health_GET.png)

**Testing de Endpoints para Routes:**
![Postman Routes GET 1](evidence_images/routes_GET.png)
![Postman Routes GET 2](evidence_images/routes:1_GET.png)
![Postman Routes POST](evidence_images/routes_POST.png)
![Postman Routes PUT](evidence_images/routes:1_PUT.png)
![Postman Routes DELETE](evidence_images/routes:1_DELETE.png)

**Testing de Parquet Uploads:**
![Postman Uploads Parquet GET 1](evidence_images/uploads:trips-parquet_POST-create.png)
![Postman Uploads Parquet GET 2](evidence_images/uploads:trips-parquet_POST-update.png)

**Schemas para Validaciones y Routes:**
![Schemas](evidence_images/Schemas_Validaciones-Routes-Uploads.png)

---

### Persona 3: Frontend de Zonas
*Espacio reservado para evidencias de: Interfaz de usuario en Streamlit, navegación de la app, formularios de gestión de zonas y manejo de alertas/errores.*
**Wireframe Frontend:**
![Wireframe Home](evidence_images/wireframe_home.png)
![Wireframe Zonas](evidence_images/wireframe_zonas.png)
![Wireframe Rutas](evidence_images/wireframe_rutas.png)
![Wireframe Parquet](evidence_images/wireframe_parquet.png)
**Capturas de Pantalla Frontend:** 
Home
![Frontend Home](evidence_images/frontend_home.png)
Zonas
![Frontend Buscar Zona](evidence_images/frontend_buscarzonas.png)
![Frontend Crear Zona](evidence_images/frontend_crearzona.png)
![Frontend Editar Zona](evidence_images/frontend_editarzona.png)
![Frontend Eliminar Zona](evidence_images/frontend_eliminarzona.png)
Rutas
![Frontend Buscar Ruta](evidence_images/frontend_buscarrutas.png)
![Frontend Crear Ruta](evidence_images/frontend_crearruta.png)
![Frontend Editar Ruta](evidence_images/frontend_editarruta.png)
![Frontend Eliminar Ruta](evidence_images/frontend_eliminarruta.png)
Parquet
![Frontend Parquet](evidence_images/frontend_parquet.png)
![Frontend Parquet Subido](evidence_images/frontend_parquet_subido.png)
**Capturas Manejo de Errores Frontend:** 
![Error Campos Vacios](evidence_images/frontend_errorvacios.png)
![Error Origen Destino Igual](evidence_images/frontend_error_origendestino.png)
![Error Longitud Input](evidence_images/frontend_error_longitud.png)
---

### Persona 4: DevOps y Carga Masiva (Parquet)
*Espacio reservado para evidencias de: Infraestructura Docker (contenedores activos), proceso de ingesta de archivos Parquet con resumen de métricas y visualización de la página de Rutas.*

**Infraestructura Docker:**
![Contenedores activos 1](evidence_images/docker-compose-running-1.png)
![Contenedores activos 2](evidence_images/docker-compose-running-2.png)
![Health check ok](evidence_images/get-health-parquet-ok.png)

**Ingesta de Datos Parquet:**
![Interfaz de carga](evidence_images/frontend-carga-parquet.png)
![Resumen de procesamiento](evidence_images/procesamiento-parquet-resumen.png)
---
