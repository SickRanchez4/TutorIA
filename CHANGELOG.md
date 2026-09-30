# Changelog

## [Unreleased]

## [0.1.0] - 2026-09-30

### Added
- Primera versión funcional de TutorIA, con frontend Vue y Vuetify, backend Flask y base de datos SQL Server.
- Autenticación con JWT y paneles diferenciados para administración, coordinación y estudiantes.
- Gestión multiinstitución con roles y aislamiento de datos por institución.
- Administración de instituciones, cuentas, planes y suscripciones con cuotas de cuentas y tokens IA.
- Gestión de cursos, estudiantes y matrículas, con importación masiva desde Excel.
- Edición de perfil y cambio de contraseña desde la aplicación.
- Chat de asistencia académica por curso, con sesiones, historial de mensajes y envío de imágenes.
- Modos de interacción para consultas, práctica y generación de recursos de estudio mediante n8n.
- Configuración del agente por curso: instrucciones, temperatura, modos permitidos y uso de la base de conocimiento.
- Base de conocimiento RAG con carga de PDF, ingestión mediante n8n e indexación en Pinecone por institución y curso.
- Historial de trabajos de ingestión, estados, métricas, reintentos y operaciones para eliminar documentos o vaciar el índice de un curso.
- Consulta de agenda académica del estudiante con actividades y fechas de sus cursos.
- Registro y analíticas de consumo de tokens IA, con cálculo de costos según las tarifas de los modelos.
- Tres workflows n8n para el chatbot de estudiantes, la carga de conocimiento y la administración del índice RAG.
- Scripts de instalación de SQL Server y carga inicial idempotente, con datos de demostración opcionales.
- Despliegue con Docker Compose, Nginx y Gunicorn, y configuración de producción con Caddy y HTTPS automático.
- Endpoints de disponibilidad y conectividad con la base de datos, y logs JSON con identificadores de solicitud.
- Documentación de instalación, configuración, despliegue en DonWeb y operación de la base de conocimiento RAG.

### Changed
- No aplica: primera versión publicada, sin una versión anterior de referencia.

### Fixed
- No aplica: las correcciones realizadas durante el desarrollo inicial forman parte de esta primera versión.

### Known Issues
- Los PDF cargados para RAG no tienen almacenamiento persistente en el despliegue Docker actual: se pierden al reemplazar o recrear el contenedor backend, aunque el historial y las métricas permanecen en SQL Server.
- Los límites de tasa no cuentan con almacenamiento compartido entre réplicas; es necesario configurar Redis antes de escalar el backend.
- No se incluye un sistema automático de migraciones de base de datos; las actualizaciones de una base existente requieren scripts SQL específicos.
- No se incluye una suite de pruebas automatizadas en el repositorio para esta versión.
