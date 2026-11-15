# Changelog

## [Unreleased]

### Added
- Seed de simulación ampliado y aplicado a PostgreSQL: 12 instituciones, 36 coordinadores, 480 estudiantes y 60 cursos adicionales; exactamente dos planes nuevos, sin añadir administradores. Incluye historial académico, tarifas y fallos RAG/notificaciones explícitamente sintéticos, sin invocar proveedores. Repetición idempotente y preservación de registros existentes verificadas.
- Constitución, especificaciones y plantillas SDD consolidadas como documentación posterior al baseline de v0.1.0.
- Proyecto independiente de pruebas de SPEC-001, con procedimientos y evidencia histórica preservada; evaluación cerrada con RF-5/RNF-6 fallidos, no certificación del MVP.
- Entregables de preparación C0 de SPEC-002: inventario, casos, recursos y baseline lint/build; sin implementación UI/UX ni requisitos funcionales aprobados por ejecución.
- Contexto del proyecto al 2026-11-14 como punto de entrada al desarrollo: producto, actores, organización del repositorio, arquitectura, trazabilidad CU/HU, brechas y cinco specs propuestas para completar el producto, además de SPEC-002.

### Changed
- Administración: altas de instituciones y asignación de suscripciones en diálogos, listados a ancho completo y búsquedas por nombre institucional; selector de Coordinadores ordenado alfabéticamente. Verificación focalizada de navegador con API simulada, lint y build.
- PostgreSQL 18.x externo sustituye SQL Server para instalaciones nuevas (SPEC-008): driver psycopg, UUID nativos conservados como strings en API, scripts PostgreSQL de esquema/seed y soporte dependiente adaptado. Sin migración de datos ni servicio de base en Compose.
- Configuración mediante `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` y `DB_SSLMODE`; URL construida internamente y rechazo explícito de `DATABASE_URL`. Imagen backend sin ODBC; documentación y ejemplos alineados. Verificación inicial de configuración/compilación sin suites; instalación y comprobación operativa real autorizadas posteriormente, con disponibilidad y tres logins correctos, sin certificación integral.
- Corrección editorial de los enlaces de Spec-000 tras su traslado y de las cuentas/cantidades del seed descritas en README, sin modificar SQL ni el producto.
- Aprobación explícita del plan y paleta de SPEC-002 registrada el 2026-10-31; T01 respaldada y discrepancia C0-G01 resuelta sin retrodatación ni autorización para implementar C1–C5 en esta limpieza.
- Refactor frontend previo a C1 de SPEC-002: shell, encabezados, indicadores, perfil, avisos y formatos compartidos; separación del chat y agenda del estudiante; adaptación tipográfica y responsiva a Vuetify 4. No implementa los temas ni completa C1–C5.
- Sincronización de resúmenes documentales con el refactor ya incorporado, preservando los resultados históricos y distinguiendo corrección implementada de verificación real pendiente.

### Fixed
- Compatibilidad de conexión PostgreSQL con poolers que rechazan `search_path` en las opciones de inicio: UTC y esquema `public` se fijan dentro de cada transacción.
- Fondos cortados en los paneles, etiquetas Mermaid eliminadas por sanitización, carga indefinida ante errores de render y acceso a datos nulos tras fallo de carga de curso.
- Lectura del archivo seleccionado en importaciones Excel (S-001), variable sin uso que impedía lint (C0-B01), conservación de rol/teléfono al actualizar perfil y fallbacks de error en español.
- La verificación histórica del refactor incluye lint/build satisfactorios y revisión visual/envío multipart con API simulada; no cierra S-2 real ni acredita los 28 requisitos de SPEC-002.

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
