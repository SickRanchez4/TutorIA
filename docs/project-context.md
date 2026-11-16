# TutorIA — Contexto del proyecto

**Última actualización:** 2026-11-15.

**Referencia de código:** baseline `35c6f3dc5da5369ce9d40de08da1dc7d800f2a47` más la implementación PostgreSQL y el seed descritos en [SPEC-008](specs/spec-008-postgresql/spec.md); consultar el historial Git para la revisión vigente.

**Versión declarada del producto:** v0.1.0; existen incrementos posteriores versionados, sin nueva versión de producto declarada.

**Uso:** punto de entrada para comprender, preparar y continuar el desarrollo del proyecto.

## 1. Cómo utilizar este documento

Este documento proporciona el contexto funcional y técnico necesario para empezar a trabajar en **TutorIA**: qué producto se construye, para quién, cómo se organiza, qué existe y cómo desarrollar lo pendiente. Es una referencia autónoma; no requiere leer documentos anteriores para comprender el proyecto.

TutorIA tiene una base implementada. Empezar a trabajar significa incorporarse a ella y evolucionarla, no inicializar una aplicación desde cero ni sustituir su stack.

**Recorrido recomendado:**

1. Comprender el producto, sus actores y límites en §2–§3.
2. Ubicar el código y seguir el flujo de incorporación de §4.
3. Consultar funcionalidades e interfaces en §5 y arquitectura/datos en §6.
4. Revisar defectos y condiciones operativas en §7 antes de cambiar comportamiento.
5. Elegir un incremento de §8 y resolver sus decisiones de §9 mediante una spec aprobada.

### Convenciones de alcance y evidencia

Se distinguen cuatro estados:

- **Implementado:** existe código o un artefacto que realiza la función descrita; no implica que todos sus escenarios estén probados.
- **Verificado en alcance acotado:** hay evidencia de ejecución identificable, con sus límites y modalidad.
- **Parcial:** existe una base funcional, pero faltan capacidades del objetivo o garantías necesarias.
- **Pendiente / propuesto:** no está construido, o es una propuesta que requiere especificación y aprobación.

Ante diferencias, el código y los artefactos describen lo construido; los registros describen lo efectivamente probado; una spec aprobada define el objetivo, no demuestra su cumplimiento. Las divergencias se registran, no se resuelven declarando que la implementación satisface por sí sola el requisito.

Los resultados de pruebas citados corresponden a sus registros de ejecución, no a una nueva certificación derivada de este documento. Antes de trabajar contra servicios desplegados, comprobar su versión y configuración: los workflows activos pueden diferir de los exports del repositorio.

## 2. Producto, propósito y alcance

TutorIA es una **plataforma web de tutoría académica B2B SaaS multiinstitucional**. Permite a las instituciones organizar sus cursos y estudiantes, proporcionar asistencia académica con IA y supervisar el uso de los recursos contratados.

Su propuesta de valor es acercar el material oficial al estudiante mediante un tutor contextualizado, centralizando la operación en coordinación académica y manteniendo visibilidad institucional del consumo y los costos.

El producto abarca cuatro áreas:

- **Administración de la plataforma:** instituciones, coordinadores, planes, suscripciones y acceso.
- **Operación académica:** estructura de cursos, estudiantes, matrículas, configuración del tutor y material.
- **Aprendizaje:** consulta fundamentada, práctica guiada, recursos de estudio y agenda.
- **Gobierno y automatización:** consumo/costos, sincronización de fuentes y recordatorios.

### Punto de partida para el desarrollo

Existe un MVP con administración institucional y comercial básica, cursos y matrículas, tutor mediante n8n, carga de PDF para RAG, agenda de lectura y analíticas de consumo.

El estado global es **MVP implementado con verificación parcial y brechas funcionales/operativas**:

1. La base funcional está registrada retrospectivamente en Spec-000.
2. SPEC-001 construyó un proyecto de pruebas y cerró su evaluación **con defectos**, no con certificación integral.
3. SPEC-002 tiene **cierre funcional acotado**: C1–C4 implementados, Claro/Oscuro/Sistema y verificaciones mínimas de Edge. La evaluación integral y las tareas expresamente diferidas siguen pendientes; no es certificación de los 28 requisitos.
4. Están pendientes la jerarquía académica completa, la sincronización de fuentes de Drive, la integración Calendar y las notificaciones automáticas.
5. El tutor y el RAG tienen infraestructura y flujos existentes, pero no está acreditado el ciclo completo de recuperación con citas obligatorias, calidad pedagógica, recursos específicos y limpieza consistente.
6. El control comercial requiere completar presupuesto monetario, almacenamiento y garantías ante concurrencia. La operación necesita recuperación durable, migraciones y validación de despliegue.
7. PostgreSQL 18.x sustituye SQL Server como base transaccional. La base externa configurada fue inicializada y ampliada con datos de simulación el 2026-11-15: 13 instituciones, 530 usuarios y 62 cursos. Se verificaron disponibilidad, login y consultas de los tres roles contra la base real. La integración completa sigue pendiente. No se migran datos de la base anterior.

La hoja de ruta de §8 delimita la evolución hacia el producto completo. El avance se controla por requisitos y evidencia de cada spec, no mediante un porcentaje global sin base de cálculo.

## 3. Actores, responsabilidades y reglas de producto

| Actor | Responsabilidad | Límite |
|---|---|---|
| Super Admin | Administrar instituciones clientes, planes, suscripciones y coordinadores | Sus rutas globales no lo convierten implícitamente en coordinador de una institución |
| Coordinador | Administrar la operación académica, cuentas de estudiantes, matrículas, tutor, material y analíticas institucionales | Opera únicamente sobre su institución |
| Estudiante | Consultar sus cursos, conversar con el tutor, practicar, solicitar recursos y consultar la agenda | Requiere matrícula activa y solo accede a sus conversaciones |
| Sistema | Ejecutar integraciones y automatizaciones | Es un actor técnico, no un cuarto rol humano; sincronización y recordatorios completos siguen pendientes |

### Reglas que deben guiar los cambios

- **Aislamiento institucional:** la pertenencia se comprueba en backend y debe mantenerse también en archivos, vectores y workflows. La interfaz no es una frontera de autorización.
- **Gestión centralizada:** coordinación configura el entorno académico y los asistentes; no existe un rol Docente implementado ni debe añadirse por inferencia.
- **Contexto académico:** el curso es hoy la unidad que vincula matrícula, tutor, conversación, agenda y conocimiento. Cambiarla exige preservar esas asociaciones.
- **Acceso y licencia:** cuenta e institución deben estar activas; las operaciones IA también comprueban vigencia y saldo. El plan limita cuentas activas, incluidos coordinadores y estudiantes, no únicamente alumnos.
- **Fundamentación:** el objetivo es responder con material oficial y citas verificables de archivo/página. La recepción de citas no certifica por sí sola su calidad; falta conciliar esa política con `extender_conocimiento`.
- **Transparencia financiera:** el costo IA estimado, la cuota de tokens y el precio comercial de la suscripción son conceptos distintos.
- **Simplicidad:** evolucionar el stack y los patrones existentes; no añadir roles, proveedores, dependencias o abstracciones sin necesidad aprobada.

## 4. Organización del repositorio y forma de trabajo

### 4.1 Mapa del repositorio

| Ubicación | Responsabilidad |
|---|---|
| [frontend](../frontend) | SPA Vue: vistas por rol, componentes, estado, navegación y servicios HTTP |
| [backend](../backend) | API Flask, autorización, modelos y servicios de negocio/integración |
| [database](../database) | Esquema de instalación y carga inicial de PostgreSQL 18.x |
| [automation/workflows](../automation/workflows) | Exports n8n de chat, ingestión y administración del conocimiento |
| [testing](../testing) | Proyecto independiente de pruebas, integración optativa, sistema y limpieza de datos propios |
| [docs/specs](specs) | Constitución, requisitos, planes, tareas y evidencia por incremento |
| [docker-compose.yml](../docker-compose.yml) y [overlay de producción](../docker-compose.production.yml) | Servicios de aplicación y proxy HTTPS; PostgreSQL 18.x y n8n son externos |

### 4.2 Primeros pasos para incorporarse

**Modelo de trabajo y delimitación metodológica:**

- **Scrum (gestión ágil):** metodología utilizada para organizar el desarrollo incremental del MVP. Puede seguir organizando iteraciones y entregas; no se presupone que cada actividad actual constituya una ceremonia formal de Scrum.
- **SDD (Spec Driven Development):** enfoque de especificación y control adoptado después del MVP v0.1.0. Una spec aprobada establece el alcance antes del plan y del código; planes, tareas, implementación y evidencia mantienen trazabilidad.
- **PUDS (solo disciplina de Pruebas):** la referencia es `guia-pruebas-puds-dev-ai.md`, adaptación del capítulo 11, «Prueba», del *Proceso Unificado de Desarrollo de Software* para desarrollador y copiloto IA. No se adopta PUDS como proceso completo ni se reemplazan Scrum o SDD.

**Primeros pasos:**

1. Leer la [Constitución](specs/constitution.md) y localizar la spec del cambio. Spec-000 documenta el MVP; las modificaciones posteriores requieren alcance aprobado.

   Antes de elaborar el plan de una spec, el desarrollador decide y registra en ella si se realizarán pruebas y cuál será su alcance. La IA puede proponerlas; el desarrollador aprueba la decisión. El plan desarrolla el alcance acordado, no incorpora pruebas por defecto. Si se decide no realizarlas, se documentan los límites de verificación sin declarar los requisitos probados.

2. Preparar el entorno con el [README](../README.md): configuración local de secretos, PostgreSQL 18.x externo y webhooks n8n. La conexión utiliza campos `DB_*`, no una URI completa. No copiar credenciales a código, documentación ni reportes.
3. Identificar si se usará una instalación nueva o una base existente. Los scripts iniciales solo sirven para instalación; una base con datos requiere una migración específica.
4. Revisar el estado del árbol de trabajo y los defectos de §7. Elegir pruebas según el impacto utilizando [REGRESSION.md](../testing/REGRESSION.md), sin asumir que una ejecución histórica cubre cambios nuevos.
5. Implementar un incremento acotado: mantener reglas en backend, presentación en frontend e integraciones encapsuladas; coordinar todos los consumidores cuando cambie un contrato.
6. Ejecutar las comprobaciones pertinentes y registrar resultados reales, defectos y limpieza. Actualizar spec/tareas, evidencia y documentación afectada antes de dar el trabajo por terminado.

**Aplicación de Pruebas de PUDS cuando estén incluidas en la spec:** la IA propone el plan y los casos derivados de requisitos/casos de uso o diseño; el desarrollador aprueba el alcance, los criterios y los resultados esperados. La IA implementa y ejecuta los tests, registra defectos antes de corregirlos y presenta la salida real de ejecución. En integración se comprueba cada construcción pertinente; las pruebas de sistema, si están previstas y cumplen los criterios de entrada, se evalúan al final de la iteración mediante automatización y verificación manual del desarrollador. La evaluación registra compleción, fiabilidad y defectos; el desarrollador decide el cierre. No se modifican resultados esperados sin su aprobación ni se extiende el alcance para corregir defectos ajenos a la spec. Los artefactos se integran en el esquema documental existente, sin imponer rutas duplicadas solo porque la guía muestre ejemplos.

Para frontend se dispone de `npm run dev`, `npm run lint` y `npm run build`, ejecutados desde su carpeta. Para pruebas backend, seguir [testing/README.md](../testing/README.md): la suite predeterminada es aislada y las modalidades con SQL real exigen preparación y autorización propias. No usar IA, indexación ni notificaciones reales para comprobar cambios puramente visuales.

### 4.3 Specs de referencia y estado de construcción

| Spec | Entregable | Estado y evidencia |
|---|---|---|
| [Spec-000](specs/spec-000-mvp/Spec-000-mvp.md) | Baseline retrospectivo del MVP v0.1.0 | Cerrado como descripción de la versión, no como certificación integral |
| [SPEC-001](specs/spec-001-tests/spec.md) | Pruebas esenciales de capacidad, estudiantes y conversaciones, con control del destino y limpieza | Evaluación cerrada con defectos; resultados en su [registro](specs/spec-001-tests/test.md) |
| [SPEC-002](specs/spec-002-ui-ux/spec.md) | Sistema visual, navegación, interacción, accesibilidad y adaptación por dispositivo | C1–C4 funcionales; C5 mínimo y Edge comprobados. Cierre acotado para continuar SPEC-003; [pendientes diferidos](specs/spec-002-ui-ux/tasks.md) sin ejecutar |
| [SPEC-008](specs/spec-008-postgresql/spec.md) | PostgreSQL 18.x externo y credenciales separadas | Esquema y seed instalados por autorización posterior; disponibilidad y tres logins verificados. Sin suites ni certificación integral PostgreSQL |

La existencia de componentes reutilizables es una base para continuar SPEC-002, no un cierre automático de tareas o requisitos. Los detalles de cada implementación y su evidencia permanecen en la spec correspondiente.

### 4.4 Estructura frontend que debe reutilizarse

Los principales patrones disponibles son:

- **Estructura compartida:** `RoleLayout` concentra fondo, sidebar, barra superior y avisos; `PageHeader` y `StatCard` unifican patrones repetidos.
- **Separación funcional:** el panel de estudiante delega chat y agenda a vistas específicas y mantiene el perfil como sección.
- **Fondo continuo:** `AppBackdrop` es una capa fija, con ruido en mosaico y `v-app` transparente.
- **Compatibilidad Vuetify 4:** tipografía MD3, reset mínimo, breakpoints alineados y listas transparentes. Evitar overrides globales que anulen estilos de los controles.
- **Perfil y sesión:** servicios comunes en `authService`, actualización del usuario sin perder el rol y conservación del teléfono editado ante respuestas que no lo incluyen.
- **Avisos y formatos:** toast reactivo compartido, fallbacks de error en español y utilidades de fechas, números, tamaño de archivo y selección `File`/lista de archivos.
- **Excel:** `firstFile` admite el valor del selector simple en importaciones de cursos y alumnos.
- **Mermaid:** las respuestas académicas pueden incluir flowcharts, mapas mentales, secuencias, estados, clases/ER, Gantt/timeline, gráficos cuantitativos y otros tipos Mermaid 11.16.1. El SVG sanitizado conserva su tamaño intrínseco con desplazamiento horizontal y zoom, sin reducir diagramas anchos hasta volver ilegible el texto; el renderizador ajusta el espaciado por tipo, evita el marcador de hoy fuera del rango de un Gantt y el generador prioriza síntesis y etiquetas breves. Se oculta la sección de fuente y se conserva un estado de error visible ante fallos de carga/render.
- **Respuestas del tutor:** todas las respuestas del asistente se renderizan como Markdown con fórmulas LaTeX (`\( \)`, `\[ \]`, `$ $`, `$$ $$`) mediante KaTeX, sin HTML crudo y sanitizadas; los bloques ```` ```mermaid ```` se dibujan también en respuestas de chat. El agente produce el formato; el frontend solo lo pinta.
- **Robustez de vistas:** error con reintento en detalle de curso, confirmación al retirar matrícula, protección ante respuestas atrasadas al abrir conversaciones y envío unificado por modo.
- **Agenda y presentación:** cuadrícula propia, lista mensual de actividades y ajustes responsivos de chat y paneles.

Fuentes principales: [componentes](../frontend/src/components), [vistas de estudiante](../frontend/src/views/estudiante), [vistas de coordinación](../frontend/src/views/coordinador), [formatos](../frontend/src/utils/format.js), [auth store](../frontend/src/stores/auth.js) y [estilos](../frontend/src/style.css).

La evidencia histórica registra lint/build con código 0 y revisión visual en Edge headless con API simulada a 390, 1024, 1280, 1440 y 1920 px de ancho. Los dos diálogos Excel enviaron multipart al mock. No fue una prueba con SQL/n8n ni ejecutó la matriz formal UI-xx.

## 5. Inventario funcional y trazabilidad del producto

Los identificadores CU/HU permiten vincular las capacidades de producto con las specs de desarrollo. La tabla distingue disponibilidad y trabajo pendiente; no sustituye los criterios de aceptación ni la evidencia de cada spec.

| CU / HU | Estado actual | Existente | Brecha para completar el objetivo | Continuidad |
|---|---|---|---|---|
| CU-01 / HU-01 | Implementado, verificación parcial | CRUD institucional, estado y coordinadores | Validar ciclo completo y eliminación/retención entre sistemas | SPEC-007 propuesta |
| CU-02 / HU-02 | Parcial | Planes, suscripciones, vigencia, cuentas y tokens | Presupuesto USD, almacenamiento efectivo, concurrencia y definición de precio comercial | SPEC-006 propuesta |
| CU-03 / HU-03 | Implementado, verificación parcial | JWT, RBAC, usuario/institución activos, perfil y contraseña | Recuperación de acceso y ciclo de sesión operable; matriz de aislamiento completa | SPEC-007 propuesta |
| CU-04 / HU-05 | Parcial | PDF manual, ingestión, Pinecone, trabajos, reintento y limpieza | Carpeta Drive vinculada, sincronización incremental, fuentes durables, trazabilidad y recuperación verificadas | SPEC-004 propuesta |
| CU-05 / HU-04 | Parcial | Cursos, estudiantes, matrículas e importaciones | Facultades/carreras/materias-grupos/periodos y migración compatible; S-2 real pendiente | SPEC-003 propuesta |
| CU-06 / HU-06 | Parcial | Prompt, temperatura, modos y extensión por curso | Modelo/proveedor configurable de extremo a extremo y política pedagógica coherente | SPEC-004 propuesta |
| CU-07 / HU-11 | Parcial | Tokens, tarifas versionadas, costo estimado y analíticas de coordinación | Presupuesto exigible, cobertura de operaciones IA y visión financiera global necesaria para Super Admin | SPEC-006 propuesta |
| CU-08 / HU-07 | Parcial | Chat por curso, historial, sesión y citas recibidas | PDF/página verificables, respuesta fundamentada y negativa explícita sin evidencia suficiente | SPEC-004 propuesta |
| CU-09 / HU-08 | Parcial | Agenda de lectura desde SQL y filtros | Fuente Calendar sincronizada, gestión de vínculo, cambios/cancelaciones y zona horaria | SPEC-005 propuesta |
| CU-10 / HU-09 | Parcial | Endpoint/modo recursos, recuperación RAG con salida explícita aun sin coincidencias, generación Mermaid según solicitud y política de conocimiento del curso, explicación Markdown y render sanitizado | Quizzes, flashcards y resúmenes con contratos y criterios de calidad definidos; validar calidad/atribución en distintas materias | SPEC-004 propuesta |
| CU-11 / HU-10 | Parcial | Modo práctica y configuración enviada al agente | Verificar guía socrática multivuelta, sin entregar directamente la solución | SPEC-004 propuesta |
| CU-12 / HU-12 | Pendiente | Tabla de logs y actividades como base | Programación, entrega, reintento y deduplicación de avisos de 7 días/24 h | SPEC-005 propuesta |

**Actores:** Super Admin, Coordinador y Estudiante tienen rutas e interfaces. El Sistema sigue siendo el actor automatizado del objetivo; no es un cuarto rol de usuario ni un worker de recordatorios ya disponible. No existe rol Docente implementado: la mención «Coordinador/Docente» de HU-06 no lo incorpora automáticamente.

### 5.1 Interfaces disponibles

- Público: `/login`.
- Superadministración: `/super-admin`, con secciones internas para instituciones, planes, suscripciones, coordinadores y perfil.
- Coordinación: `/coordinador/cursos`, detalle `cursos/:id`, `cuentas`, `institucion`, `analytics` y `perfil`.
- Estudiante: `/estudiante`, con asistente, agenda y perfil como secciones internas.
- API: `/api/auth`, `/api/admin`, `/api/coordinador` y `/api/estudiante`; JSON y multipart según operación.

La navegación conserva guards por rol y autenticación; las rutas desconocidas redirigen a login. Las reglas autorizantes se ejecutan en backend, no en el guard del cliente. Fuentes: [router](../frontend/src/router/index.js), [auth](../backend/routes/auth_multi_tenant.py), [administración](../backend/routes/instituciones.py), [coordinación](../backend/routes/coordinador.py) y [estudiante](../backend/routes/estudiante.py).

## 6. Arquitectura, stack y modelo de datos

### 6.1 Componentes y responsabilidades

| Capa | Tecnologías y decisiones vigentes |
|---|---|
| Frontend | Vue 3, JavaScript, Vuetify 4, Pinia, Vue Router y Axios; Vite para desarrollo/build y ESLint para lint; Tailwind configurado |
| Contenido educativo | Mermaid y DOMPurify para diagramas sanitizados; markdown-it, markdown-it-texmath y KaTeX para respuestas con fórmulas |
| Backend | Python, Flask, SQLAlchemy, Flask-JWT-Extended y Flask-Limiter |
| Datos | PostgreSQL 18.x mediante SQLAlchemy/psycopg; esquema `public`. Pinecone para vectores a través de n8n; no se introduce pgvector |
| Integraciones | n8n, OpenAI y Google Drive; Calendar es parte de la hoja de ruta, no de la integración actual |
| Sesión | Access JWT de 24 h, almacenamiento cliente en `localStorage` y hashes compatibles con Werkzeug; seed PBKDF2-SHA256. Sin refresh implementado |
| Calidad | `unittest` en proyecto independiente, lint/build y procedimientos de integración/sistema |
| Despliegue | Docker Compose, Gunicorn, Nginx y Caddy/HTTPS en el overlay de producción |

La [Constitución](specs/constitution.md) exige conservar esta base salvo una spec aprobada que justifique el cambio. No es necesario sustituir el stack para desarrollar las funcionalidades pendientes.

```text
Navegador: Vue + Vuetify + Pinia
    -> Caddy HTTPS (overlay de producción)
    -> Nginx: SPA y proxy /api
    -> Flask / Gunicorn
        -> PostgreSQL 18.x: datos transaccionales e historial
        -> n8n: tutor, ingestión y administración de conocimiento
            -> OpenAI, Pinecone y Google Drive según workflow
```

- El frontend separa vistas, componentes, composables, store y servicios HTTP.
- Flask organiza blueprints, modelos y servicios de validación, cuota, tarifas, tokens e ingestión. Parte de la lógica sigue en rutas; no se declara Clean Architecture completa.
- PostgreSQL 18.x y n8n son dependencias externas: Compose no los instala.
- FullCalendar está entre las dependencias, pero la agenda actual utiliza una cuadrícula propia.
- [Tokens canónicos](../frontend/public/tokens.css) para Claro verde muy claro/blanco y Oscuro verde suave; Vuetify deriva sus colores de esta fuente. Sistema es el valor inicial y la única preferencia persistente nueva es `tutoria.appearance`. El selector está únicamente en Perfil de cada rol, no en la navegación lateral ni login; no hay barra superior de panel. Login usa siempre Oscuro con fondo petróleo, sin modificar la preferencia de los perfiles; su red decorativa es más clara/densa y mantiene deriva sin cursor, salvo movimiento reducido.
- Navegación compartida, borradores solo en memoria, confirmaciones, estados recuperables, errores persistentes, perfil controlado, paginación local y protección de lecturas obsoletas. Chat conserva borrador ante fallo, controla IME/imagen/dictado y ofrece diagramas saneados con fuente/zoom; agenda mantiene todas las actividades del período.

Fuentes: [dependencias frontend](../frontend/package.json), [dependencias backend](../backend/requirements.txt), [tema](../frontend/src/plugins/vuetify.js), [app](../backend/app.py) y [Compose](../docker-compose.yml).

### 6.2 Modelo de datos

El [esquema inicial](../database/001-initial-schema.sql) contiene **16 tablas**:

| Área | Tablas |
|---|---|
| Identidad | `users`, `roles`, `user_roles` |
| Institución y licencia | `instituciones`, `planes`, `suscripciones` |
| Academia | `cursos`, `estudiante_cursos`, `configuracion_ia` |
| Chat | `sesiones_chat`, `mensajes_chat` |
| Agenda | `actividades_agenda`, `log_notificaciones` |
| Consumo | `precios_modelo_ia`, `consumo_tokens` |
| RAG | `rag_ingestion_jobs` |

Los documentos y chunks vectoriales no se almacenan en tablas SQL específicas: el historial de ingestión queda en SQL y los vectores en Pinecone. El modelo académico actual contiene cursos y matrícula directa, sin tablas de facultades, carreras, grupos ni periodos.

Los UUID son nativos de PostgreSQL y el ORM utiliza `Uuid(as_uuid=False)` para conservar strings en la API; cursos, roles, planes y tarifas usan enteros generados por identidad. Las fechas conservan el contrato UTC sin zona del backend; cada transacción fija UTC y `search_path=public` sin opciones de inicio incompatibles con poolers. La pertenencia institucional puede derivarse de curso, usuario o sesión; no todas las tablas tienen columna institucional propia. El aislamiento depende de autorización y filtros de aplicación; el esquema inicial no define políticas SQL de Row-Level Security. Su verificación debe cubrir esas relaciones y también Pinecone/Drive.

La instalación utiliza [001-initial-schema.sql](../database/001-initial-schema.sql) sobre una base vacía y [001-seed-data.sql](../database/001-seed-data.sql) para la carga idempotente y ejemplos opcionales. No se debe ejecutar de nuevo el esquema inicial sobre una base con datos ni sustituirlo por `db.create_all()`. No existe una cadena de migraciones de actualización implementada.

El seed ampliado conserva un administrador y los tres roles, añade solo dos planes y utiliza identidades inspiradas en la filosofía con dominios `.test` para 12 instituciones ficticias adicionales. Sus matrículas, conversaciones, agenda y consumo sintético permiten simular volumen y estados de negocio sin introducir datos personales reales. Los ejemplos RAG y notificaciones son fallos identificados como `[SIMULACIÓN SEED]`, con cero archivos procesados/vectores y sin acciones externas. La repetición de la carga se verificó contra la base desplegada sin duplicados ni cambios en filas existentes; esto no certifica seguridad, concurrencia ni integraciones externas.

### 6.3 Tutor, RAG y fuentes externas

- PDF: hasta 10 archivos por carga, 20 MiB por archivo; validación inicial, almacenamiento temporal por trabajo y llamada síncrona a n8n.
- Trabajos: estados `queued`, `processing`, `completed`, `failed`, `unknown`; métricas y reintento mientras existan fuentes locales.
- Namespace vectorial: `inst_{institucion_id}_curso_{curso_id}`.
- Chat: valida sesión propia, matrícula, modo y cuota; envía contexto/configuración a n8n y persiste intercambio, citas y consumo cuando corresponde.
- Memoria del agente e historial SQL no son lo mismo; no se transmite todo el historial SQL en cada petición.
- Consulta/práctica registran indisponibilidad mediante `service_unavailable`; recursos puede devolver `502`. No se debe presentar ese comportamiento como disponibilidad garantizada.
- Recursos: el backend invoca una sola vez el modo `recursos`; no cambia a `chat` como reintento. El contrato de n8n devuelve título, explicación, Mermaid y citas, o un error explícito.
- Imágenes: backend admite PNG/JPEG/WEBP/GIF hasta 4 MiB; el selector frontend actual ofrece PNG/JPEG. El dictado depende del navegador.

Los exports son [TutorIA](../automation/workflows/students-agent-chatbot.json), [generación Mermaid](../automation/workflows/tool-generador-mermaid.json), [RAG de chat](../automation/workflows/tool-rag-chat.json), [ingestión](../automation/workflows/upload-to-pinecone.json) y [administración de índice](../automation/workflows/knowledge-index-admin.json). Los flujos principales/subordinados se mantienen versionados en n8n y en estos exports.

La generación de recursos recupera primero material del namespace institucional/curso. Una recuperación vacía se convierte en contexto explícito y nunca corta silenciosamente la respuesta. Si la extensión de conocimiento está deshabilitada, se informa que faltan fuentes; si está habilitada, el generador puede complementar con conocimiento general y lo declara en la explicación. El catálogo Mermaid controlado por la app y el subworkflow incluye flowchart, mindmap, sequence, state, class, ER, Gantt, timeline, pie, quadrant, journey, requirements, gitGraph, Sankey, XY, block, architecture, packet, Kanban y C4Context/C4Container. La app solo renderiza tipos del catálogo y normaliza dos convenciones ambiguas de Mermaid: la etiqueta aislada `mindmap` dentro de un mapa mental y dos puntos en títulos de sección de journey.

Persisten diferencias documentadas de metadatos: ingestión identifica `sourceFile`, eliminación usa `archivo`, y el enriquecimiento toma datos del primer elemento del lote. La atribución, página y eliminación de varios documentos deben demostrarse antes de dar el RAG por completo. Un trabajo marcado `completed` o una cita recibida no prueban recuperación correcta.

### 6.4 Consumo y contratos

El control actual calcula tokens mensuales desde el inicio del mes UTC, comprueba saldo antes de invocar IA y registra tokens/costo estimado según tarifas. Usa información de n8n si llega; de lo contrario estima con `tiktoken`. **La comprobación no reserva saldo atómicamente.** Tampoco el conteo previo de cuentas constituye una reserva ante altas concurrentes.

No existe una API pública versionada ni catálogo OpenAPI completo. Los contratos actuales deben conservarse o migrarse coordinadamente. La contabilidad no debe confundirse con facturación real del proveedor ni con cobro de la suscripción.

Fuentes: [cuotas](../backend/services/subscription_quota.py), [tarifas](../backend/services/model_pricing.py), [modelos de licencia](../backend/models/institucion.py), [modelos IA/chat](../backend/models/ia_chat.py) e [ingestión](../backend/services/rag_ingestion.py).

## 7. Calidad, defectos y límites vigentes

### 7.1 Qué acredita la evidencia disponible

| Evidencia | Resultado registrado | Lo que no demuestra |
|---|---|---|
| SPEC-001, suite aislada | 23/23, repetida el 2026-10-31 | SQL real, UI, IA o todo el backend |
| SPEC-001, controles simulados | 53/53, repetidos el 2026-10-31 | Seguridad integral del despliegue ni nueva integración SQL |
| SPEC-001, integración histórica | I-1 a I-4 aprobados, datos propios limpiados | Regresión actual completa ni resto de las funciones |
| SPEC-001, sistema histórico | S-1/S-3/S-3b aprobados; S-2 fallido | Importación corregida extremo a extremo |
| SPEC-002, refactor | Lint/build código 0; revisión visual y multipart con mock | Matriz UI-xx, contraste, lector de pantalla, rendimiento o persistencia real |
| SPEC-002, cierre acotado | Temas, navegación/formularios, chat/agenda/diagramas, límites de archivos y muestra de contraste comprobados en Edge con HTTP interceptado | Sin lector real, matriz completa de navegadores/zoom, medidas de rendimiento ni regresión backend/SQL/proveedores; no aprobación integral de 20 RF/8 RNF |

Las evidencias consolidadas están en [SPEC-001](specs/spec-001-tests/evidence.md) y [SPEC-002](specs/spec-002-ui-ux/evidence.md). Los reportes/journals locales anteriores fueron retirados por decisión registrada; no se debe prometer que siguen disponibles para reproducción. Existen runners y procedimientos para nuevas ejecuciones.

La integración histórica de SPEC-001 corresponde a SQL Server, no a PostgreSQL. SPEC-008 adapta el soporte existente al nuevo dialecto sin ejecutar sus suites. La instalación y comprobación operativa posterior verifican disponibilidad y tres logins reales, no la integración completa; no reutilizar aquellos resultados históricos como certificación de la base nueva.

### 7.2 Seguimiento de brechas

| Referencia | Estado al corte / tratamiento |
|---|---|
| S-001 / C0-K01: importación Excel | Corrección frontend implementada y comprobada con mock. **Pendiente reejecutar S-2 real** antes de cerrar el defecto funcional. Se conserva su fallo histórico |
| H-004: idioma del runner | Abierto en SPEC-001; no reparado por la refactorización UI |
| C0-B01: variable sin uso | Resuelto por el refactor; lint satisfactorio registrado |
| C0-B02: chunk Mermaid >500 kB | Aviso previo todavía registrado; medir antes de dividir o cambiar límites |
| C0-K03: `.xls` ofrecido | UI ofrece `.xls/.xlsx`, lector usa `openpyxl`; compatibilidad/ayuda pendientes |
| C0-K04: `skipped.row` | Puede contener datos sensibles de importación; no guardar ni mostrar filas crudas en evidencias/resultados |
| C0-K06: formatos de imagen | Diferencia UI/backend pendiente de completar y verificar |
| Inventario C0 | Describe fuente previa al refactor; sus referencias por línea y decisiones de extracción son históricas, no la estructura vigente |
| Persistencia RAG | Compose no monta volumen de PDF; recrear el backend puede impedir reintentos |
| Recuperación e integración | Faltan reproducción completa de subworkflows y prueba del ciclo carga/consulta/borrado entre SQL, Pinecone y Drive |
| Concurrencia y finanzas | Sin reserva atómica de cuentas/tokens ni presupuesto monetario exigible; almacenamiento declarado no equivale a cuota integral aplicada |
| Operación | Sin cadena de migraciones, CI/CD ni recuperación backup/restore certificada; rate limiting en memoria por defecto |
| Sesión y protección de integraciones | Token accesible desde JavaScript; sin refresh/revocación individual ni protocolo backend-webhook de firma/replay en el baseline |

Los últimos puntos son límites conocidos del diseño/MVP, no resultados de una auditoría integral de vulnerabilidades.

### 7.3 Condiciones de operación

La [guía operativa](../README.md) documenta Docker, SQL externo, n8n y despliegue con Caddy. Hay healthchecks de proceso y SQL, logs JSON e identificadores de solicitud. Esto no sustituye pruebas de entrega ni de recuperación.

Configuración indispensable: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_SSLMODE`, `JWT_SECRET_KEY`, orígenes frontend y URLs de los tres webhooks n8n. Se construye una URL SQLAlchemy internamente sin concatenar credenciales; se rechaza `DATABASE_URL`. Los proveedores requieren credenciales administradas fuera del código. No incluir sus valores en documentación ni reportes. La imagen usa psycopg sin ODBC.

El plan define capacidad de cuentas y almacenamiento declarado; la suscripción define tokens y vigencia. No existen presupuesto mensual USD ni precio comercial en esos modelos actuales: su incorporación corresponde a SPEC-006.

Para un entorno real: cambiar credenciales públicas del seed, restringir puertos, usar HTTPS y secretos gestionados, verificar backups y retención, y documentar responsables de SQL/n8n/proveedores. Si se usan varias réplicas, resolver primero almacenamiento de archivos/trabajos y límites de tasa compartidos.

## 8. Hoja de ruta mínima de specs para completar el producto

### 8.1 Alcance y reglas de planificación

Se propone **continuar desde el cierre funcional acotado de SPEC-002 y añadir cinco specs funcionales/técnicas**, no una spec por pantalla, endpoint, tabla o prueba. Los identificadores SPEC-003 a SPEC-007 están **propuestos**, no creados ni aprobados. SPEC-008 registra por separado el cambio transversal PostgreSQL ya solicitado; no sustituye esas capacidades pendientes. Se reutilizan las capacidades actuales; no se propone reescribir el MVP.

La referencia de producto completo son las capacidades de §5, con calidad y operación suficientes para su uso institucional. Las decisiones de alcance pendientes se resolverán explícitamente al aprobar cada spec.

- Scrum fue la metodología ágil del desarrollo incremental original; puede organizar iteraciones y entregas futuras. SDD gobierna los requisitos, la aprobación de alcance y la trazabilidad de los incrementos posteriores. La disciplina de Pruebas de PUDS se aplica únicamente al alcance de pruebas previamente decidido en cada spec; no sustituye a las otras dos prácticas.
- Cada spec entrega cortes verticales —datos, reglas, API/workflow, UI y las pruebas que el desarrollador haya decidido incluir antes del plan—, con pocas construcciones coherentes. Si se incluyen pruebas, el plan especifica trazabilidad a casos de uso/diseño, criterios medibles, roles de IA/desarrollador y evaluación por iteración, según la sección IV de la Constitución.
- Seguridad, aislamiento, privacidad y accesibilidad son criterios transversales; su verificación por pruebas se acota y registra conforme a la decisión de cada spec, sin afirmar cobertura donde no hubo ejecución.
- Las decisiones pendientes de §9 no son autorización para elegir proveedores, cambiar contratos, migrar datos o ejecutar escrituras reales.
- Los IDs de CU/HU se conservan; los RF/RNF nuevos se califican por spec para evitar colisiones.

### 8.2 SPEC-002 existente — Cierre funcional acotado

**Resultado vigente:** alcance funcional C1–C4 completado aprovechando el refactor; comprobaciones mínimas acordadas y [evidencia](specs/spec-002-ui-ux/evidence.md). Se puede iniciar la definición de SPEC-003, sin asumir su aprobación.

**Trabajo implementado:**

- Conciliar el plan/inventario con `RoleLayout`, componentes compartidos y separación chat/agenda; reutilizarlos y completar sus contratos, no crear un segundo shell.
- Implementar paleta verde/blanca y tokens de ambos temas, selector Claro/Oscuro/Sistema, persistencia tolerante a fallos e inicialización sin destello.
- Completar navegación/foco, formularios, confirmaciones, cambios sin guardar, estados de región y avisos accesibles.
- Adaptar pantallas administrativas, chat, agenda, Mermaid y estados de archivos; alinear ayuda Excel y formatos de imagen con lo soportado.
- Verificación mínima de Edge, contraste, teclado/semántica y viewports; no la matriz exhaustiva original.

**Dependencias:** base actual y decisiones del plan aprobado; registrar la adaptación de tareas antes de cerrarlas. La refactorización previa no satisface automáticamente T19/T24/T29 ni los RF asociados.

**Pendientes futuros:** T87, T89–T91, T92–T93 y T94–T98; lector real y extensión de zoom/dispositivos no ejecutados. S-2 requiere entorno real autorizado para cerrar S-001; se conserva el fallo histórico. La aceptación integral RF/RNF no se deriva del cierre acotado.

### 8.3 SPEC-003 propuesta — Organización académica y matrícula completa

**Objetivo:** cubrir CU-05/HU-04 y organizar los cursos para el uso institucional completo.

**Trabajo necesario:**

- Definir facultades/sedes, carreras/programas, materia, grupo/oferta y periodo académico con la mínima estructura que permita los casos reales.
- Reutilizar el identificador de curso como contexto estable del tutor o definir una migración explícita de su identidad; no perder matrículas, historial, agenda, consumo ni namespace RAG.
- Implementar gestión institucional, filtros, activación/cierre de periodos y matrícula en la oferta correcta.
- Adaptar altas e importaciones Excel con formato soportado, duplicados, conflictos, resultados parciales y protección de datos de cada fila.
- Establecer qué implica mover/desactivar una entidad y cómo conserva el estudiante su historial.

**Datos y contratos:** migración SQL versionada con mapeo de cursos existentes, compatibilidad de rutas/payloads y reconciliación de identidades externas si cambia su significado. Evitar entidades redundantes sin uso.

**Dependencias:** decisión explícita sobre jerarquía académica (§9). Puede aprovechar SPEC-002 sin bloquear el modelado por el tema visual.

**Aceptación:** un coordinador organiza una oferta completa y matricula/importa sin duplicados; el estudiante ve solo su oferta; se rechazan relaciones de otra institución. Regresión de cursos previos, Excel, conversaciones y acceso con datos migrados.

### 8.4 SPEC-004 propuesta — Conocimiento sincronizado y tutor académico verificable

**Objetivo:** completar CU-04/06/08/10/11 y HU-05/06/07/09/10 como una experiencia integrada de material y aprendizaje.

**Trabajo necesario:**

- Vincular una carpeta Drive a un contexto académico autorizado y sincronizar PDF nuevos, modificados y eliminados, conservando la carga manual útil del MVP.
- Definir permisos Google mínimos y credenciales por institución, metadatos de documento/versión/página, identidad estable y estrategia de actualización de vectores.
- Hacer durable el trabajo y sus fuentes mientras sea necesario para reintento; procesamiento fuera de la petición HTTP, con estados consultables, deduplicación y recuperación ante timeout/reinicio.
- Unificar contratos de metadatos entre carga, recuperación y borrado; incluir o documentar reproduciblemente los subworkflows requeridos.
- Completar configuración de modelo/proveedor por curso: empezar por la integración existente; añadir otros proveedores solo si el alcance aprobado los exige, sin framework genérico anticipado.
- Separar conocimiento oficial y extensión externa: respuesta académica fundamentada con archivo/página y aviso explícito cuando no exista evidencia; no fabricar citas.
- Definir salidas y UX necesarias para resumen, quiz y flashcards; evaluar guía socrática multivuelta, además de mapas Mermaid existentes.
- Completar el ciclo de actualización/borrado en SQL, Pinecone y Drive según retención acordada.

**Datos y contratos:** identidad fuente/versión/chunk y esquema de citas; payloads backend/n8n y consumo atribuible a cada operación. Reutilizar `rag_ingestion_jobs`; ampliar solo lo necesario.

**Dependencias:** identidad académica estable de SPEC-003 para la asociación final de carpetas. Persistencia y corrección de metadatos actuales pueden abordarse antes sin esperar toda esa spec. Usa reglas de consumo vigentes; las garantías finales de presupuesto se integran con SPEC-006.

**Aceptación:** con PDF conocidos de dos instituciones y varios cursos, se demuestra sincronización, recuperación correcta con página, ausencia de cruces, respuesta sin fuentes, reemplazo/borrado y recuperación tras reinicio. Pruebas de recursos y tutoría con rúbrica/dataset pequeño revisable, no solo respuestas visualmente plausibles. Registrar uso/costo y distinguir mocks de proveedor real.

### 8.5 SPEC-005 propuesta — Agenda académica y recordatorios automáticos

**Objetivo:** completar CU-09/12 y HU-08/12 sin convertir la app en un gestor de calendarios general.

**Trabajo necesario:**

- Asociar Calendar al contexto académico, definir quién administra el calendario y sincronizar eventos de forma incremental hacia SQL.
- Resolver fechas con zona horaria, eventos de día completo, cambios, cancelaciones y recurrencias relevantes.
- Mantener agenda de lectura para el estudiante y mostrar frescura/errores de sincronización.
- Programar avisos a 7 días y 24 horas, con reglas para eventos creados tarde, ediciones y ventanas ya vencidas.
- Implementar al menos un canal acordado —correo y/o plataforma— con entrega registrable, reintentos acotados, deduplicación y preferencias mínimas.
- Reutilizar/ampliar actividades y logs existentes; incorporar el ejecutor más sencillo compatible con n8n y los requisitos de durabilidad.

**Datos y contratos:** identificador externo y versión del evento, vínculo Calendar, zona horaria y registro inequívoco de intento/entrega. No confundir «programado» con «enviado».

**Dependencias:** identidad académica de SPEC-003; puede avanzar en paralelo con SPEC-004. Compartir la autorización Google cuando proceda sin acoplar los dos procesos.

**Aceptación:** un evento real sincronizado aparece solo a matriculados, se actualiza/cancela y genera cada aviso como máximo una vez según la política aprobada. Probar límites temporales con reloj controlado, caída del proveedor, reinicio y recuperación; validar al menos una entrega real autorizada.

### 8.6 SPEC-006 propuesta — Gobierno de planes, consumo y costos

**Objetivo:** completar CU-02/07 y HU-02/11 con límites comprobables y analíticas útiles.

**Trabajo necesario:**

- Consolidar semántica de capacidad: cuentas activas frente a estudiantes, almacenamiento, tokens, presupuesto mensual USD y vigencia.
- Definir precio comercial si debe registrarse; separarlo del costo IA y no añadir pasarela de pago para administrar una licencia.
- Resolver altas y solicitudes IA concurrentes con reservas/controles transaccionales, confirmación y liberación ante fallos.
- Registrar consumo de chat, recursos, visión, embeddings y otras llamadas facturables del pipeline; atribuir modelo/proveedor/tarifa y distinguir medición de estimación.
- Aplicar cuota de almacenamiento según qué archivos se conserven y dónde; mostrar saldo/uso real, no capacidad decorativa.
- Completar panel financiero institucional y vista global de administración, alertas y comportamiento ante límite, vencimiento o suspensión.

**Datos y contratos:** migraciones de límites/presupuesto y movimientos/reservas solo si son necesarios; acordar reportes de uso con n8n. Conservar snapshots históricos de tarifa.

**Dependencias:** reglas comerciales aprobadas y contratos de operaciones de SPEC-004; definir los controles antes de habilitar cargas o automatizaciones que puedan excederlos. No requiere que SPEC-005 esté terminada.

**Aceptación:** pruebas concurrentes muestran que no se rebasa la política acordada, no hay doble cargo por reintento y los fallos liberan reservas apropiadamente. Totales de panel concilian con registros; probar cambio de mes UTC, tarifa, plan, expiración y ausencia de precio.

### 8.7 SPEC-007 propuesta — Acceso, operación y entrega confiable

**Objetivo:** consolidar CU-01/03 y HU-01/03 y habilitar una entrega institucional mantenible del conjunto.

**Trabajo necesario:**

- Completar recuperación de acceso y ciclo de sesión: expiración, renovación si se adopta, invalidación y estrategia de almacenamiento del token explícita. Verificación de correo solo cuando el circuito acordado la requiera.
- Verificar aislamiento y permisos en todos los recursos/relaciones; proteger comunicaciones de webhooks y evitar exposición de secretos/datos personales en errores y logs.
- Definir retención, exportación/borrado necesarios y limpieza externa al eliminar curso/institución.
- Establecer migraciones repetibles sobre bases existentes, backups/restore probados y recuperación de trabajos/archivos/n8n.
- Configurar límites compartidos cuando la topología lo requiera; no introducir clústeres ni múltiples servicios solo por previsión.
- Incorporar CI con lint/build y suites aisladas; mantener integración y sistema optativos en destinos autorizados. Tratar H-004 y los defectos vigentes sin reescribir su evidencia.
- Documentar despliegue/rollback, versiones compatibles de servicios, monitoreo/alertas y procedimientos del operador.

**Dependencias:** las tareas de protección y recuperación acompañan cada incremento desde el inicio. La aceptación final integra SPEC-002 a SPEC-006; no se difieren bloqueantes de integridad hasta este cierre.

**Aceptación:** instalación limpia y actualización de una copia de la versión anterior sin pérdida; restore y rollback ensayados; sesiones/permisos comprobados; CI reproducible; recorrido completo de los tres roles y del Sistema en entorno controlado, incluyendo errores externos y limpieza. Revisión de preparación operativa con limitaciones residuales aceptadas explícitamente.

### 8.8 Orden recomendado y criterio común de cierre

1. Definir SPEC-003 desde la base UI funcional y sus límites documentados; programar por separado las verificaciones diferidas de SPEC-002 y la comprobación real de S-001.
2. Aprobar el modelo académico y entregar SPEC-003 para evitar rehacer asociaciones de Drive/Calendar.
3. Desarrollar SPEC-004 y SPEC-005 como frentes independientes una vez establecida esa identidad.
4. Diseñar SPEC-006 junto con los contratos IA/almacenamiento de SPEC-004 y activar sus controles antes de liberar consumo automatizado.
5. Aplicar prácticas de SPEC-007 durante todos los incrementos y cerrar con aceptación integrada.

Cada spec se cierra con requisitos trazados a código y evidencia disponible, la decisión previa del desarrollador sobre pruebas y los resultados de las incluidas, decisiones sobre fallos y documentación de operación/migración cuando corresponda. Integración y sistema siguen PUDS cuando estén dentro del alcance acordado; las propuestas de pruebas de esta hoja de ruta se concretan antes del plan de cada spec. Toda escritura real requiere confirmación del destino, datos propios y limpieza/recuperación; las autorizaciones anteriores no se reutilizan.

**No se consideran imprescindibles para esta hoja de ruta:** app móvil nativa, rol docente nuevo, pagos automáticos, facturación fiscal, SSO/MFA, microservicios, API pública ni soporte simultáneo de todos los proveedores LLM. Requieren necesidad de negocio y aprobación propia; no se incorporan por interpretar «proyecto completo» como alcance ilimitado.

## 9. Decisiones que deben resolverse al aprobar las siguientes specs

| Decisión | Base actual y recomendación de partida | Momento |
|---|---|---|
| Jerarquía académica | Cursos directos están implementados. Para completar la organización académica, proponer facultad/carrera/materia/oferta-periodo; aprobar la simplificación y migración antes de diseñar tablas | SPEC-003 |
| Fuente oficial y conocimiento externo | El objetivo de fundamentación convive con `extender_conocimiento`; definir respuestas permitidas, avisos y comportamiento sin contexto | SPEC-004 |
| Acceso Google | Determinar cuenta de servicio o consentimiento institucional, permisos mínimos, titularidad y revocación; no asumir que el Drive del workflow actual resuelve Calendar | SPEC-004/005 |
| Modelos IA | Acordar modelos permitidos, configuración por curso y si se necesitan otros proveedores además del existente | SPEC-004/006 |
| Recursos de estudio | Definir resultado mínimo usable de quiz/flashcard/resumen; no incluir seguimiento de notas o gamificación sin requerimiento | SPEC-004 |
| Recordatorios | Canal, zona horaria institucional, reglas de envío tardío/preferencias y responsable operativo | SPEC-005 |
| Planes y límites | Confirmar cuentas versus estudiantes, presupuesto USD, precio comercial y política de exceso/cambio de plan | SPEC-006 |
| Privacidad y operación | Retención por dato/proveedor, acceso a archivos, ubicación, topología, responsables y objetivos de recuperación/disponibilidad medibles | SPEC-007, antes de producción |

Estas decisiones deben quedar resueltas en la spec correspondiente antes de implementar el comportamiento afectado; no son reglas de negocio ya aprobadas.

## 10. Referencias y mantenimiento del contexto

- Este archivo es el **contexto de entrada al proyecto**; orienta el trabajo sin reemplazar contratos, specs ni registros de evidencia.
- [Spec-000](specs/spec-000-mvp/Spec-000-mvp.md): baseline v0.1.0 cerrado; no actualizarlo como si describiera incrementos posteriores.
- [Constitución](specs/constitution.md): gobernanza vigente.
- [SPEC-001](specs/spec-001-tests/spec.md) y [SPEC-002](specs/spec-002-ui-ux/spec.md): objetivos y estados detallados en sus tareas/resultados.
- [README](../README.md): entrada al proyecto e instalación; [CHANGELOG](../CHANGELOG.md): cambios de producto/documentación, sin inventar releases.
- [Pruebas](../testing/README.md), [regresión](../testing/REGRESSION.md) y [sistema](../testing/SYSTEM.md): ejecución y límites de cada modalidad.
- `guia-pruebas-puds-dev-ai.md`: documento metodológico proporcionado por el responsable; adaptación de la disciplina de Pruebas (capítulo 11) de PUDS al trabajo desarrollador–copiloto IA. Su ubicación dentro del repositorio no está acreditada por este contexto y no se incorpora como archivo nuevo en esta actualización.

Con cada incremento, actualizar en conjunto: estado de spec/tareas, evidencia con modalidad real, defectos, documentación operativa y las secciones afectadas de este contexto. Mantener fecha y referencia de código y separar «propuesto», «aprobado», «implementado» y «verificado». No borrar resultados históricos fallidos al registrar una corrección posterior.
