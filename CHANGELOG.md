# Changelog

## [Unreleased]

### Added
- Seed de simulación ampliado y aplicado a PostgreSQL: 12 instituciones, 36 coordinadores, 480 estudiantes y 60 cursos adicionales; exactamente dos planes nuevos, sin añadir administradores. Incluye historial académico, tarifas y fallos RAG/notificaciones explícitamente sintéticos, sin invocar proveedores. Repetición idempotente y preservación de registros existentes verificadas.
- Constitución, especificaciones y plantillas SDD consolidadas como documentación posterior al baseline de v0.1.0.
- Proyecto independiente de pruebas de SPEC-001, con procedimientos y evidencia histórica preservada; evaluación cerrada con RF-5/RNF-6 fallidos, no certificación del MVP.
- Entregables de preparación C0 de SPEC-002: inventario, casos, recursos y baseline lint/build; sin implementación UI/UX ni requisitos funcionales aprobados por ejecución.
- Contexto del proyecto al 2026-11-15 como punto de entrada al desarrollo: producto, actores, organización del repositorio, arquitectura, trazabilidad CU/HU, brechas y specs propuestas para completar el producto, con SPEC-002 funcionalmente cerrada en alcance acotado.
- Apariencia Claro/Oscuro/Sistema con tokens canónicos, resolución previa a Vue, sincronización de sistema/pestañas y almacenamiento tolerante a fallos; selector exclusivo de Perfil de los tres roles, retirado del sidebar y login. Primitivas compartidas de confirmación, edición pendiente, estados de región, paginación, lecturas vigentes y resumen seguro de importación.
- Evidencia mínima de cierre de SPEC-002: build/lint satisfactorios y muestra visual/funcional propia en Edge 157.0.4341.46 con API controlada. T87, T89–T91, T92–T93 y T94–T98 diferidas; lector real y zoom/dispositivo exhaustivos no ejecutados, sin certificación integral.

### Changed
- Generación de recursos académicos: TutorIA pasa al subworkflow Mermaid el permiso de conocimiento general y el presupuesto de tokens. La recuperación RAG ahora entrega contexto vacío explícito; el generador ofrece un catálogo cerrado de 21 tipos Mermaid validados en Edge, con sintaxis guiada para mindmap, journey y C4. El frontend rechaza cabeceras fuera del catálogo y normaliza la etiqueta reservada `mindmap` y los dos puntos de títulos `journey`; se mantiene la salida Mermaid, explicación y citas sin reintento en modo chat.
- Legibilidad de diagramas: el SVG mantiene dimensiones intrínsecas y se desplaza en lugar de encogerse; el zoom ampliado conserva esa escala. Se afinó el espaciado de los tipos Mermaid más densos, se evita que el marcador actual expanda fuera de escala los Gantt y el generador limita complejidad y longitud de etiquetas.
- Paleta verde/blanca adaptada: fondo Claro `#E6F4DF`, Oscuro verde suave `#405C4E` y superficies/control/texto según tokens. Sustituye las iteraciones topo/eucalipto/oliva preservadas en la evidencia histórica; Tailwind, Vuetify, formularios, overlays y diagramas sincronizados. Tarjetas institucionales con las mismas proporciones que los paneles inferiores y analíticas con 7 días como período inicial.
- Login siempre Oscuro con fondo petróleo `#182D2A`, sin sobrescribir la preferencia de los perfiles. Red decorativa más clara/densa (52–150 nodos según área), líneas de 1,5 px y deriva sostenida sin cursor; chat conserva su comportamiento y ambos respetan movimiento reducido.
- Perfil compartido separa presentación/HTTP; formularios conservan edición ante fallo y evitan envíos repetidos. Chat protege borrador/imagen, respeta IME/Mayús+Enter y scroll de lectura; imágenes de cuatro formatos hasta 4 MiB. PDF con límites orientativos existentes y Excel con resumen sin filas/razones privadas, sin cambios de contratos.
- Barra superior eliminada de los paneles de administración, coordinación y estudiantes, sin dejar su espacio reservado. Se conserva un botón de menú en móvil y la navegación/perfil/cierre de sesión laterales.
- Coordinación: búsqueda de cursos por nombre; ajustes bloqueados y distintivos grises para cursos inhabilitados; matrícula visual coherente con el estado de la cuenta. Institución encabeza la navegación, muestra totales de cursos/cuentas y presenta sus datos como texto hasta pulsar Editar. Analíticas permite cerrar el detalle del curso seleccionado. Verificación focalizada de navegador con API simulada y de los contadores institucionales con PostgreSQL, sin modificar datos reales.
- Administración: altas de instituciones y asignación de suscripciones en diálogos, listados a ancho completo y búsquedas por nombre institucional; selector de Coordinadores ordenado alfabéticamente. Verificación focalizada de navegador con API simulada, lint y build.
- PostgreSQL 18.x externo sustituye SQL Server para instalaciones nuevas (SPEC-008): driver psycopg, UUID nativos conservados como strings en API, scripts PostgreSQL de esquema/seed y soporte dependiente adaptado. Sin migración de datos ni servicio de base en Compose.
- Configuración mediante `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` y `DB_SSLMODE`; URL construida internamente y rechazo explícito de `DATABASE_URL`. Imagen backend sin ODBC; documentación y ejemplos alineados. Verificación inicial de configuración/compilación sin suites; instalación y comprobación operativa real autorizadas posteriormente, con disponibilidad y tres logins correctos, sin certificación integral.
- Corrección editorial de los enlaces de Spec-000 tras su traslado y de las cuentas/cantidades del seed descritas en README, sin modificar SQL ni el producto.
- Aprobación explícita del plan y paleta de SPEC-002 registrada el 2026-10-31; T01 respaldada y discrepancia C0-G01 resuelta sin retrodatación ni autorización para implementar C1–C5 en esta limpieza.
- Refactor frontend histórico previo a C1 de SPEC-002: shell, encabezados, indicadores, perfil, avisos y formatos compartidos; separación del chat y agenda del estudiante; adaptación tipográfica y responsiva a Vuetify 4. Reutilizado en el cierre funcional actual; por sí solo no implementaba temas ni completaba C1–C5.
- Sincronización de resúmenes documentales con el refactor ya incorporado, preservando los resultados históricos y distinguiendo corrección implementada de verificación real pendiente.

### Fixed
- Al generar diagramas, una búsqueda Pinecone sin resultados ya no deja el webhook sin cuerpo: respeta la política de conocimiento del curso y da una respuesta clara o genera el recurso permitido. Se retiró “Ver definición del diagrama”; fórmulas/texto de explicación siguen renderizados con rich text.
- Chat del estudiante: respuestas con Markdown y fórmulas LaTeX renderizadas con KaTeX (antes texto plano) y diagramas Mermaid también en respuestas de chat.
- Etiquetas flotantes recortadas al editar planes: mayor espacio vertical de la fila. Switches compartidos con pista opaca y contraste visible en ambos estados/temas. Se retira el marco de foco duplicado del input interno, conservando el borde enfocado de Vuetify y los indicadores de teclado de otros controles.
- Página retenida de cursos restablecida durante carga inicial; `aria-invalid` de formularios y selección accesible del periodo analítico; foco/raíz nativa del drawer móvil y aviso que tapaba sus controles.
- Recorte de nodos Mermaid por viewBox, zoom que no cambiaba tamaño real y pérdida del disparador/foco al cambiar tema con ampliación abierta.
- Inicio con almacenamiento bloqueado/sin matchMedia; sesión solo en memoria con aviso explícito si no puede persistirse. 401 de una solicitud antigua no expulsa una sesión distinta; expiración limpia estado privado sin bloqueo por edición pendiente.
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
