
# TutorIA

Plataforma web de tutoría académica **B2B SaaS multiinstitucional**. Centraliza cursos, matrículas, material PDF y asistencia con IA para que cada estudiante aprenda con el conocimiento de su materia, mientras coordinación configura el tutor y supervisa el consumo.

## Contenido

- [Funcionalidades y alcance](#funcionalidades-y-alcance)
- [Arquitectura y tecnologías](#arquitectura-y-tecnologías)
- [Desarrollo local](#desarrollo-local)
- [Integración con n8n](#integración-con-n8n)
- [Especificaciones y pruebas](#especificaciones-y-pruebas)
- [Instalación inicial de la base de datos](#instalación-inicial-de-la-base-de-datos)
- [Despliegue con Docker](#despliegue-con-docker)
- [Despliegue en DonWeb](#despliegue-en-cloud-server-donweb)
- [Operación del conocimiento RAG](#operación-de-la-base-de-conocimiento-rag)
- [Validación y límites](#validación-y-límites)

## Funcionalidades y alcance

| Rol | Capacidades implementadas |
|---|---|
| Super Admin | Instituciones, coordinadores, planes, suscripciones, estado de acceso y analíticas globales |
| Coordinador | Cursos, estudiantes, matrículas e importación Excel; búsqueda de alumnos institucionales; configuración de modos, prompt, temperatura y extensión de conocimiento; carga y administración de PDF; analíticas institucionales |
| Estudiante | Cursos matriculados, conversaciones propias, imágenes adjuntas, tutoría en chat, práctica guiada, recursos visuales y consulta de agenda |

El backend aplica autenticación JWT, roles, pertenencia institucional y matrícula activa. El curso es la unidad del conocimiento y las conversaciones; no hay un rol Docente implementado. Los modos del tutor son:

- **Chat:** explicaciones progresivas, ejemplos y resolución de dudas.
- **Práctica** (`practicar` en el contrato): desafíos, pistas y retroalimentación sobre el razonamiento.
- **Recursos** (`recursos`): diagramas Mermaid con título y explicación didáctica, elegidos de un catálogo compatible con la interfaz.

Coordinación decide si permite **Extender conocimiento**. Desactivado, se exige respaldo en los fragmentos recuperados del curso; activado, se permite complementar con conocimiento académico general. PostgreSQL conserva usuarios, configuración e historial; Pinecone almacena los vectores, no sustituye a la base transaccional.

El producto es un **MVP con verificación parcial**, no una plataforma completamente certificada. La jerarquía académica ampliada, sincronización incremental desde Drive, integración Google Calendar y notificaciones automáticas siguen pendientes. Subir un respaldo a Drive no implementa sincronización. El alcance detallado y la hoja de ruta están en [docs/project-context.md](docs/project-context.md).

## Arquitectura y tecnologías

```text
Navegador: Vue + Vuetify
         | HTTP /api + JWT
         v
API Flask ----------------------------> PostgreSQL 18.x
         |                                  configuración, matrículas,
         | webhooks                         conversaciones, consumo y trabajos
         v
n8n: tutor, recuperación, recursos, ingestión y limpieza
         |                 |                      |
         v                 v                      v
      OpenAI            Pinecone              Google Drive
   modelos/embeddings   vectores por curso    respaldo de PDF
```

En Docker, Nginx sirve la SPA y reenvía `/api` a Flask/Gunicorn; el overlay de producción añade Caddy para HTTPS. **PostgreSQL, n8n, OpenAI, Pinecone y Google Drive son servicios externos**: Compose no los instala ni crea sus credenciales. La API valida acceso y reglas de negocio; n8n orquesta las llamadas de IA e integraciones; el frontend renderiza respuestas, fórmulas y diagramas.

| Capa | Tecnologías y responsabilidad |
|---|---|
| Frontend | Vue 3, JavaScript ESM, Vite 8, Vuetify 4, Vue Router 4, Pinia 2, Axios y estilos Tailwind/CSS |
| Contenido académico | Markdown-it, KaTeX y Mermaid; DOMPurify sanitiza el contenido renderizado. FullCalendar está incluido entre las dependencias de calendario |
| API | Python 3.13, Flask 3.1, Flask-SQLAlchemy/SQLAlchemy, Flask-JWT-Extended, Flask-CORS y Flask-Limiter |
| Datos y utilidades | PostgreSQL 18.x mediante `psycopg[binary]`, `openpyxl` para Excel, `requests` para webhooks y `tiktoken` para estimación de tokens |
| Automatización | n8n con nodos de IA/LangChain, ejecución de subworkflows, extracción PDF, OpenAI, Pinecone y Google Drive |
| Operación | Docker Compose, Gunicorn, Nginx y Caddy; logs JSON, identificador de solicitud y comprobaciones de disponibilidad |
| Pruebas | `unittest` y mocks para contratos backend, `node:test` para lógica de workflows, ESLint y compilación Vite |

Las versiones instalables se definen en [backend/requirements.txt](backend/requirements.txt), [frontend/package.json](frontend/package.json) y [frontend/package-lock.json](frontend/package-lock.json). Los modelos y parámetros de IA se configuran en los exports n8n, no en el navegador. Actualmente el tutor y la comprobación de respaldo usan `gpt-5.4-mini`, el generador visual `gpt-5.3-codex` y los embeddings `text-embedding-3-small` con **512 dimensiones**. La cuenta OpenAI conectada debe tener acceso a ellos; un cambio de modelo requiere revisar compatibilidad, límites y tarifas, no solo el nombre.

### Organización

| Ruta | Contenido |
|---|---|
| [frontend/src](frontend/src) | Vistas por rol, componentes compartidos, servicios HTTP, estado y estilos |
| [backend](backend) | Factoría Flask, configuración, rutas, modelos y servicios |
| [database](database) | Esquema de instalación y seed PostgreSQL |
| [automation/workflows](automation/workflows) | Cinco exports n8n y pruebas de sus contratos/lógica |
| [testing](testing) | Pruebas aisladas y herramientas optativas de integración/sistema |
| [docs](docs) | Contexto de producto, specs, decisiones y evidencia |
| [docker](docker) | Configuración del proxy de producción |

## Desarrollo local

Requisitos: Git, **Python 3.13**, **Node.js 22.12 o posterior compatible con Vite 8** y npm; PostgreSQL 18.x accesible. Para IA se necesitan además los servicios descritos en [Integración con n8n](#integración-con-n8n). Docker es una alternativa de despliegue, no un requisito para ejecutar los servidores de desarrollo.

1. Clonar el repositorio y preparar una base según [Instalación inicial](#instalación-inicial-de-la-base-de-datos). No ejecutar el esquema sobre una base existente.
2. Desde PowerShell en la raíz, crear el entorno backend e instalar sus dependencias:

   ```powershell
   py -3.13 -m venv .\backend\_venv
   if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno.' }
   & .\backend\_venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
   if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias.' }
   if (-not (Test-Path .\backend\.env)) { Copy-Item .\backend\.env.example .\backend\.env }
   ```

3. Completar en el archivo local los campos `DB_*`, un `JWT_SECRET_KEY` aleatorio y las URL de producción n8n. No sobrescribir una configuración existente ni compartir su contenido.
4. Iniciar Flask desde la carpeta backend:

   ```powershell
   Set-Location .\backend
   & .\_venv\Scripts\python.exe -m flask --app app:create_app run --host 127.0.0.1 --port 5000
   ```

5. En otra terminal, desde la raíz:

   ```powershell
   Set-Location .\frontend
   npm ci
   if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias.' }
   $env:VITE_API_URL = 'http://localhost:5000/api'
   npm run dev -- --host localhost --port 5173
   ```

Abrir `http://localhost:5173`. La API queda en `http://localhost:5000/api`; sus probes directos son `/healthz` y `/readyz` (sin `/api`). Si se cambia el origen del frontend, configurar `FRONTEND_URL` en el backend; no abrir CORS indiscriminadamente. El servidor Flask de desarrollo no es un servidor de producción.

### Configuración por entorno

| Variables | Uso |
|---|---|
| `JWT_SECRET_KEY`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_SSLMODE` | Acceso y conexión transaccional; obligatorios según el entorno |
| `FRONTEND_URL` | Orígenes CORS permitidos, separados por comas |
| `N8N_CHAT_WEBHOOK_URL` | Tutor: `/webhook/course-chat` |
| `N8N_EMBEDDINGS_WEBHOOK_URL` | Carga multipart PDF: `/webhook/upload-knowledge` |
| `N8N_KNOWLEDGE_ADMIN_WEBHOOK_URL`, `N8N_KNOWLEDGE_ADMIN_TOKEN` | Limpieza: `/webhook/knowledge-admin`, autenticada con `X-TutorIA-Token` |
| `RAG_UPLOAD_STORAGE_PATH` | Directorio temporal backend; por defecto `backend/storage/rag_uploads` |
| `MAX_CONTENT_LENGTH` | Límite total del cuerpo HTTP; por defecto 64 MiB |
| `RATELIMIT_STORAGE_URI`, `TRUSTED_PROXY_COUNT`, `LOG_LEVEL` | Almacenamiento del limitador, proxies de confianza y nivel de logs |
| `ALLOW_PUBLIC_REGISTRATION` | Registro público desactivado por defecto |
| `VITE_API_URL` | URL pública de API incorporada al compilar frontend; nunca colocar secretos en variables `VITE_*` |

Los ejemplos completos están en [backend/.env.example](backend/.env.example) y [.env.docker.example](.env.docker.example). Los webhooks Excel opcionales no sustituyen las importaciones existentes del backend. Las claves OpenAI, Pinecone y OAuth de Drive se vinculan como **credenciales de n8n**, no se envían al navegador ni se escriben en los exports.

## Integración con n8n

El repositorio versiona la lógica de automatización; importar JSON no instala n8n ni transfiere sus credenciales. Utilizar una versión de n8n que admita las versiones de nodos incluidas en los exports, especialmente los nodos de IA; el repositorio no fija una imagen ni una versión de servidor n8n.

| Export | Función y contrato |
|---|---|
| [students-agent-chatbot.json](automation/workflows/students-agent-chatbot.json) | Flujo principal TutorIA. `POST /webhook/course-chat`; recibe institución/curso, mensaje, modo, permiso de extensión, historial y catálogo, con imagen opcional. Devuelve respuesta o recurso, citas y modo aplicado |
| [tool-rag-chat.json](automation/workflows/tool-rag-chat.json) | Subflujo RAG. Recibe `query` y `namespace`; recupera candidatos, comprueba respaldo semántico y devuelve `context`, `citations` y `hasContext` |
| [tool-generador-mermaid.json](automation/workflows/tool-generador-mermaid.json) | Subflujo visual. Recibe `query`, `namespace`, `allowGeneralKnowledge` y `maxTokens`; entrega gráfico, título, explicación y citas o un error explícito |
| [upload-to-pinecone.json](automation/workflows/upload-to-pinecone.json) | `POST /webhook/upload-knowledge`. Recibe PDF multipart y datos de institución/curso/trabajo; extrae, fragmenta e indexa, respalda en Drive y confirma archivos procesados y catálogo |
| [knowledge-index-admin.json](automation/workflows/knowledge-index-admin.json) | `POST /webhook/knowledge-admin`. Elimina un documento o vacía un namespace; exige Header Auth y confirmación de acción/destino |

### Preparación de una instancia

1. Crear las credenciales de OpenAI, Pinecone y Google Drive en n8n. La cuenta de Drive debe poder buscar, crear carpetas y subir archivos bajo una carpeta raíz propia.
2. Preparar el índice Pinecone `tutoria-app` con **dimensión 512**, compatible con los embeddings configurados. Ingesta y consulta deben compartir índice, modelo, dimensiones y namespace `inst_{institucionId}_curso_{cursoId}`. Cambiar solo el modelo o dimensión no convierte vectores anteriores.
3. Importar los cinco exports y asignar las credenciales locales a todos sus nodos correspondientes. Los identificadores y nombres de credenciales del export son referencias de la instancia de origen, no claves reutilizables.
4. Reemplazar la carpeta raíz de Google Drive en los nodos de búsqueda y creación del flujo de ingestión; no asumir que la cuenta conectada puede acceder a la carpeta de la instancia original.
5. Revisar **todas** las referencias de ejecución a subworkflows: TutorIA llama al RAG y a Mermaid; Mermaid llama al RAG; la herramienta de búsqueda adicional del tutor también debe apuntar al RAG importado. Los IDs pueden cambiar al importar.
6. Crear la credencial Header Auth «TutorIA Backend» con cabecera `X-TutorIA-Token`, vincularla al webhook administrador y configurar el mismo valor en `N8N_KNOWLEDGE_ADMIN_TOKEN` del backend.
7. Publicar/activar los subflujos y después los flujos de entrada. Copiar las URL de producción a la configuración backend; no usar URL de prueba. Reiniciar el backend si se modificaron sus variables.

El contrato del tutor lo construye el backend a partir del curso y la sesión autorizados, no de permisos elegidos por el estudiante. Al exponer n8n, proteger el acceso a su editor y restringir los webhooks al backend mediante la infraestructura disponible: chat e ingestión no incorporan Header Auth en estos exports. La autenticación de la API de TutorIA no convierte por sí sola un webhook público de n8n en privado.

### Recorridos de datos

- **Carga:** coordinación envía hasta 10 PDF, de hasta 20 MiB cada uno y sujetos además al límite HTTP total. El backend registra el trabajo y conserva fuentes temporales; n8n procesa cada PDF individualmente, inserta sus vectores y respalda el original en Drive. Solo una confirmación válida permite marcarlo completado.
- **Consulta:** el backend comprueba acceso y cuota, envía el catálogo y hasta seis mensajes recientes; n8n recupera evidencia del curso, verifica pertinencia y aplica la política de extensión antes de responder. El modelo verificador no enseña ni habilita permisos.
- **Presentación:** el frontend muestra Markdown, fórmulas LaTeX con KaTeX y bloques Mermaid sanitizados, con desplazamiento/zoom para diagramas grandes y errores visibles si no se pueden dibujar.
- **Limpieza:** coordinación solicita la acción; el backend exige confirmación autenticada del namespace/documento antes de modificar su historial. Los respaldos Drive no se borran con esta acción.

## Versión actual

**v0.1.0 — 2026-09-30:** primera versión funcional.

Consulte el historial de versiones en [CHANGELOG.md](CHANGELOG.md).

## Especificaciones y pruebas

Estado documental actualizado el **2026-11-18**. Para empezar a trabajar, consulte el [contexto del proyecto](docs/project-context.md): producto, actores, organización del repositorio, arquitectura, funcionalidades, criterios de trabajo y hoja de ruta. La versión declarada sigue siendo v0.1.0; los incrementos posteriores no certifican el MVP completo.

| Documento | Aprobación / referencia | Construcción | Verificación |
|---|---|---|---|
| [Spec-000](docs/specs/spec-000-mvp/Spec-000-mvp.md) | Baseline retrospectivo cerrado de v0.1.0 | MVP existente | Describe alcance y límites; no certificación integral |
| [SPEC-001](docs/specs/spec-001-tests/spec.md) | Spec y plan aprobados | Proyecto de pruebas implementado; evaluación cerrada con defectos | [Registro](docs/specs/spec-001-tests/test.md): 23 aislados y 53 controles; integración/sistema históricos. RF-5/RNF-6 fallidos |
| [SPEC-002](docs/specs/spec-002-ui-ux/spec.md) | Spec aprobada; [plan y paleta aprobados el 2026-10-31](docs/specs/spec-002-ui-ux/plan.md) | C1–C4 funcionales; C5 mínimo, con tareas diferidas | [Registro](docs/specs/spec-002-ui-ux/test.md): cierre funcional acotado y muestra Edge; no certificación integral de los 28 requisitos; S-2 real pendiente |
| [SPEC-008](docs/specs/spec-008-postgresql/spec.md) | Cambio PostgreSQL 18.x y credenciales separadas autorizado | Base externa, configuración, modelos, scripts y soporte adaptados; esquema/seed instalados por autorización posterior | Disponibilidad, login y consultas de tres roles comprobados; sin certificación integral de PostgreSQL |

**Aprobada** significa que el responsable aceptó el alcance o diseño, no que exista código. **Implementada** indica que existe el entregable. **Verificada** exige evidencia satisfactoria de los criterios aplicables. **Cerrada con defectos** significa que terminó la evaluación, pero siguen requisitos fallidos o pendientes; no equivale a cumplimiento íntegro.

S-001 tiene una corrección de frontend incorporada en el refactor de SPEC-002, comprobada con API simulada. Su fallo histórico de SPEC-001 se conserva y el cierre funcional requiere reejecutar S-2 con el sistema real autorizado. H-004 continúa abierto.

La [Constitución](docs/specs/constitution.md) gobierna los cambios posteriores al baseline. Los registros de cada spec son la fuente de resultados y defectos; las [plantillas](docs/templates/prompts.md) son ejemplos, no requisitos aprobados. Para reproducir las pruebas, seguir [testing/README.md](testing/README.md) y [testing/REGRESSION.md](testing/REGRESSION.md).

Cada spec resume su evidencia en un único `evidence.md`. Los reportes y journals `ownership.json` que generan los runners son locales y quedan fuera de Git; los reportes y doce journals anteriores se retiraron el 2026-10-31 por decisión del responsable. Entornos, cachés, PDF temporales, Excel de sistema y secretos también quedan fuera de Git. La autorización histórica de SQL no habilita nuevas operaciones; integración y sistema requieren confirmación nueva del destino y limpieza de datos propios.

## Instalación inicial de la base de datos

Se requiere **PostgreSQL 18.x externo**. No se incluye una base de datos en Docker Compose ni se migran datos de SQL Server. Crear primero un usuario y una base vacía UTF-8 cuyo propietario sea ese usuario (por ejemplo, `tutoria` y `tutoria-webapp`) mediante pgAdmin o la administración del proveedor. Conectarse a esa base y ejecutar los archivos completos:

1. [database/001-initial-schema.sql](database/001-initial-schema.sql): crea las 16 tablas e índices en `public`, dentro de una transacción. Exige PostgreSQL 18.x y esquema vacío; no crea la base ni es una migración para bases con datos.
2. [database/001-seed-data.sql](database/001-seed-data.sql): carga roles, cuenta de administración, tarifa IA y ejemplos académicos. Puede repetirse sin duplicar los datos ni sobrescribir contraseñas o suscripciones existentes.

Desde PowerShell, con el cliente PostgreSQL instalado (se solicita la contraseña sin incluirla en argumentos):

```powershell
psql -h localhost -p 5432 -U tutoria -d tutoria-webapp -W -v ON_ERROR_STOP=1 -f .\database\001-initial-schema.sql
if ($LASTEXITCODE -ne 0) { throw 'No se pudo instalar el esquema.' }
psql -h localhost -p 5432 -U tutoria -d tutoria-webapp -W -v ON_ERROR_STOP=1 -f .\database\001-seed-data.sql
if ($LASTEXITCODE -ne 0) { throw 'No se pudo cargar el seed.' }
```

Los valores editables están al principio del bloque `DO` del seed: administración, institución, dominio, plan, cuota, tarifa y personas. `v_schools` y `v_philosophers` contienen las instituciones ficticias y las identidades inspiradas en la filosofía de la carga ampliada. Ejecutar el bloque completo, sin separadores `GO` ni comandos SQL Server.

Con sus valores actuales, el seed conserva Universidad C-137 y añade 12 instituciones ficticias con dominios reservados `.test`. En total crea **13 instituciones, 3 planes, 530 usuarios (1 administrador, 38 coordinadores y 491 estudiantes), 62 cursos y 1.462 matrículas**. Incluye 4.336 conversaciones, 17.312 mensajes, 482 actividades y 17.396 consumos sintéticos repartidos en varios meses, además de cuatro versiones históricas de tarifa con los mismos valores de la vigente. Estas cifras corresponden al seed, no a altas posteriores hechas desde la app.

La carga ampliada incluye estudiantes desactivados, una institución inactiva y una suscripción vencida para comprobar esos estados; las cuentas activas y los consumos mensuales respetan sus cuotas. La suscripción inicial de Universidad C-137 dura 12 meses. Las fechas ampliadas se anclan a la creación de esa institución: repetir la carga no desplaza el calendario ni sobrescribe contraseñas, suscripciones o estados.

Hay **120 trabajos RAG fallidos y 11.520 notificaciones fallidas de simulación**, identificados con `[SIMULACIÓN SEED]` en el error del trabajo o la descripción de la actividad relacionada. No se suben archivos, no se crean vectores/citas, no se llama a n8n ni se envían notificaciones. Los nombres de PDF son metadatos ficticios, sin archivos físicos; para usar RAG se deben subir PDFs reales en una nueva ingestión, no reintentar esos ejemplos. No se registran ingestiones completadas ni envíos exitosos ficticios.

Para empezar sin ejemplos académicos, cambiar `v_load_examples` a `false`: solo se cargarán roles, administración y tarifa IA; no se crearán los planes ni el conjunto ampliado.

| Cuenta inicial | Contraseña inicial pública |
|---|---|
| Administración: `administracion@demo.com` | `password` |
| Coordinación: `coordinador.alfa@demo.com` y `coordinador.beta@demo.com` | `password` |
| Estudiantes de ejemplo: `estudiante.alfa@demo.com`, `estudiante.beta@demo.com` y otras nueve cuentas | `password` |
| Coordinación de la Academia del Pórtico: `lucio.seneca@portico.test` | `password` |
| Estudiante de la Academia del Pórtico: `socrates.atenas@portico.test` | `password` |

Estas cuentas corresponden a los valores actuales de `v_admin_email`, `v_domain`, `v_people`, `v_schools` y `v_philosophers` del seed; si se editan, sus correos cambian. No representan personas ni organizaciones reales. No se crean `coordinador@demo.com` ni `estudiante@demo.com` con la configuración actual. La carga idempotente no renombra ni elimina cuentas existentes.

**Cambiar estas contraseñas desde Perfil antes de exponer la aplicación.** La base almacena hashes PBKDF2-SHA256 compatibles con Werkzeug; cambiar el texto de una contraseña en un comentario no actualiza su hash. Para una instalación real, usar el modo sin ejemplos y cambiar inmediatamente la contraseña de administración; las demás cuentas se crean desde la app.

Los scripts no crean el usuario de conexión ni configuran la aplicación: el backend necesita los campos `DB_*`, `JWT_SECRET_KEY` y los webhooks n8n para IA. No usar `db.create_all()` como sustituto del esquema versionado: no instala todos sus índices y restricciones.

### Credenciales separadas

Para ejecución local, copiar [backend/.env.example](backend/.env.example) a `backend/.env` si todavía no existe; Docker usa `.env.docker` a partir de [.env.docker.example](.env.docker.example). No sobrescribir archivos reales existentes. En ambos casos:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tutoria-webapp
DB_USER=tutoria
DB_PASSWORD='completar-con-la-contrasena-real'
DB_SSLMODE=prefer
```

No usar `DATABASE_URL` ni variables `MSSQL_*`. SQLAlchemy construye la URL con los valores separados: no codificar `@`, `:`, `/`, `?` ni otros caracteres como URL. Usar comillas simples dotenv cuando haya `$` o `#` y las reglas de escape dotenv si la contraseña contiene comillas. El backend lee dotenv sin interpolación `${...}`. Las variables del proceso tienen precedencia sobre el archivo; eliminar cualquier `DATABASE_URL` heredada, que se rechaza explícitamente.

En Docker Desktop, usar `DB_HOST=host.docker.internal` para PostgreSQL instalado en Windows; `localhost` dentro del contenedor apunta al propio backend. Para un servidor externo usar su DNS/IP accesible desde el contenedor. En Linux configurar una dirección alcanzable del host o del proveedor.

`DB_SSLMODE` admite `disable`, `allow`, `prefer`, `require`, `verify-ca` y `verify-full`. En producción usar el modo exigido por el proveedor, preferiblemente `verify-full` con CA confiable instalada. `prefer` permite conexiones sin TLS; no asumir que cifra la conexión. Cada transacción fija UTC y `search_path=public`, sin parámetros de inicio `options`, para admitir conexiones mediante poolers. Los UUID se almacenan como `uuid` nativos y siguen siendo strings en la API.

## Despliegue con Docker

El despliegue crea dos servicios:

- `frontend`: Nginx sirve la aplicación Vue y redirige `/api/*` al backend.
- `backend`: Flask se ejecuta con Gunicorn y se conecta al PostgreSQL 18.x configurado externamente.

### 1. Configurar secretos

En PowerShell, crea el archivo de variables locales a partir del ejemplo:

```powershell
if (-not (Test-Path .env.docker)) { Copy-Item .env.docker.example .env.docker }
```

Completa `JWT_SECRET_KEY`, los campos `DB_*` y las URL de n8n en tu `.env.docker`, siguiendo [.env.docker.example](.env.docker.example). No subas `.env.docker` al repositorio.

Para generar un secreto JWT seguro:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Construir e iniciar

```powershell
docker compose --env-file .env.docker up --build -d
```

La aplicación queda expuesta en `http://localhost:8080`, ligada a loopback por defecto. Para cambiarlo, define `APP_PORT` en `.env.docker`. `--env-file` permite que Compose también lea las variables de interpolación como `APP_PORT`; `env_file` del servicio configura el contenedor, no sustituye esa opción.

### 3. Verificar el estado

```powershell
docker compose ps
docker compose logs -f backend
```

- `http://localhost:8080/healthz`: disponibilidad del frontend.
- `http://localhost:8080/api/healthz`: disponibilidad del backend.
- `http://localhost:8080/api/readyz`: confirma conectividad con PostgreSQL y versión 18.x.

Los logs del backend se emiten en JSON a `stdout` e incluyen `X-Request-ID` para correlacionar solicitudes.

### Operación

```powershell
# Detener servicios
docker compose down

# Reconstruir después de cambios
docker compose --env-file .env.docker up --build -d
```

## Requisitos de producción

- Use secretos administrados por el proveedor, no un archivo `.env` incluido en la imagen.
- Configure los webhooks n8n de producción con `/webhook/...`, no `/webhook-test/...`.
- Rote cualquier secreto que haya sido expuesto y use una clave JWT aleatoria.
- El backend utiliza `psycopg[binary]`, sin ODBC ni drivers Microsoft. PostgreSQL debe ser accesible desde el contenedor y permitir al usuario de aplicación operar sobre las tablas/secuencias de `public`.
- Para límites de tasa persistentes entre réplicas, configure Redis como almacenamiento de Flask-Limiter antes de escalar el backend.

## Despliegue en Cloud Server DonWeb

La instancia Ubuntu 24.04 con Docker y Docker Compose ejecuta los dos servicios de la aplicación definidos en [docker-compose.yml](docker-compose.yml). Para producción se añade [docker-compose.production.yml](docker-compose.production.yml), que incorpora Caddy como proxy inverso y obtiene/renueva automáticamente el certificado HTTPS.

### 1. Preparar el servidor y el dominio

1. En el panel de DonWeb, cree el Cloud Server con la imagen Docker/Ubuntu 24.04 y anote su IP pública. DonWeb ofrece acceso `root`, consola web, firewall virtual y Docker Compose preinstalado.
2. En el proveedor DNS, cree un registro `A` para el dominio de la aplicación (por ejemplo, `app.tudominio.com`) apuntando a la IP pública del Cloud Server. Espere a que resuelva antes de iniciar Caddy; HTTPS requiere que el dominio llegue al servidor por los puertos 80 y 443.
3. En el firewall virtual de DonWeb permita TCP `22`, `80` y `443`; no exponga `5000` ni `8080` a Internet.
4. Conéctese por SSH y confirme las herramientas instaladas:

```bash
ssh root@IP_DEL_SERVIDOR
docker --version
docker compose version
```

5. Opcionalmente, configure el firewall del sistema como segunda capa:

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 2. Copiar el proyecto y configurar secretos

En el servidor, clone el repositorio en una ubicación persistente:

```bash
git clone URL_DEL_REPOSITORIO /opt/tutoria
cd /opt/tutoria
cp .env.docker.example .env.docker
chmod 600 .env.docker
```

Edite `.env.docker` con valores reales. Para producción configure al menos:

```dotenv
APP_PORT=127.0.0.1:8080
DOMAIN=app.tudominio.com
FRONTEND_URL=https://app.tudominio.com
JWT_SECRET_KEY=secreto-aleatorio-largo
DB_HOST=postgres.tudominio.com
DB_PORT=5432
DB_NAME=tutoria-webapp
DB_USER=tutoria
DB_PASSWORD='completar-con-la-contrasena-real'
DB_SSLMODE=verify-full
N8N_CHAT_WEBHOOK_URL=https://tu-n8n.example/webhook/course-chat
N8N_EMBEDDINGS_WEBHOOK_URL=https://tu-n8n.example/webhook/upload-knowledge
N8N_KNOWLEDGE_ADMIN_WEBHOOK_URL=https://tu-n8n.example/webhook/knowledge-admin
N8N_KNOWLEDGE_ADMIN_TOKEN=mismo-secreto-que-la-credencial-header-auth-de-n8n
```

Use URLs de producción de n8n (`/webhook/...`), nunca `/webhook-test/...`. No codifique la contraseña como URL. Configure la CA confiable para `verify-full` y verifique que el firewall y `pg_hba.conf` de PostgreSQL permitan el acceso desde el backend; no publique el puerto de la base indiscriminadamente.

### 3. Aplicar migraciones y desplegar

Para una instalación nueva, ejecute sobre PostgreSQL 18.x [database/001-initial-schema.sql](database/001-initial-schema.sql) y después [database/001-seed-data.sql](database/001-seed-data.sql), según la sección de instalación inicial. En producción use el modo sin ejemplos y cambie la contraseña pública de administración antes de publicar. No vuelva a ejecutar el esquema inicial sobre una base existente: los cambios futuros requieren una migración específica.

Después, construya e inicie los contenedores desde `/opt/tutoria`:

```bash
docker compose --env-file .env.docker -f docker-compose.yml -f docker-compose.production.yml up --build -d
docker compose -f docker-compose.yml -f docker-compose.production.yml ps
docker compose -f docker-compose.yml -f docker-compose.production.yml logs -f
```

Caddy deja el frontend interno y publica exclusivamente HTTP/HTTPS. Redirige el tráfico a Nginx del servicio `frontend`, que a su vez entrega la SPA y reenvía `/api/*` al backend. Los archivos RAG se guardan solo de forma temporal dentro del contenedor backend y se eliminan cuando este se reemplaza o se recrea.

### 4. Verificar

Cuando el certificado se haya emitido, compruebe:

```bash
curl -I https://app.tudominio.com/healthz
curl -I https://app.tudominio.com/api/healthz
curl -I https://app.tudominio.com/api/readyz
```

`/healthz` confirma el frontend, `/api/healthz` el proceso Flask y `/api/readyz` también la conexión a PostgreSQL 18.x. Si el certificado no se emite, confirme primero DNS, puertos 80/443 y los logs del contenedor `caddy`.

### Actualizar la aplicación

```bash
cd /opt/tutoria
git pull
docker compose --env-file .env.docker -f docker-compose.yml -f docker-compose.production.yml up --build -d
docker image prune -f
```

No ejecute `docker compose down -v` durante una actualización: elimina los volúmenes persistentes de Caddy y obligará a emitir nuevamente los certificados HTTPS.

## Operación de la base de conocimiento RAG

El esquema de instalación [database/001-initial-schema.sql](database/001-initial-schema.sql) incluye la tabla de trabajos de ingestión RAG y sus índices para el historial de cargas, estado, documentos recibidos y métricas devueltas por n8n. Las bases anteriores deben incorporar esa tabla mediante una migración, no volviendo a ejecutar la instalación completa.

El detalle de cada curso muestra un resumen compacto de documentos indexados, fecha de indexación y trabajos que requieren atención. Los PDF locales son temporales: se eliminan al confirmar una carga completada; los conservados para diagnóstico/reintento se pierden al recrear el contenedor si no hay almacenamiento persistente configurado. El historial y los datos de procesamiento permanecen en PostgreSQL; los respaldos confirmados permanecen en Drive.

Para eliminar un PDF específico o vaciar la base de conocimiento de un curso, importe y active [automation/workflows/knowledge-index-admin.json](automation/workflows/knowledge-index-admin.json) en n8n. Configure `N8N_KNOWLEDGE_ADMIN_WEBHOOK_URL` con su única URL de producción y `N8N_KNOWLEDGE_ADMIN_TOKEN` con el mismo valor de la credencial Header Auth «TutorIA Backend» (cabecera `X-TutorIA-Token`); reinicie el backend tras configurar estas variables. Vincule en n8n esa credencial y la de Pinecone del índice `tutoria-app`. No guarde el token en el export ni en Git.

El flujo recibe `action` con `delete_document` o `clear_course`, junto con el curso, institución y —solo para eliminar un PDF— `archivo`. Obtiene el host del índice con la credencial Pinecone y usa `POST /vectors/delete` limitado al namespace institucional/curso. Confirma la operación, incluido un namespace ya inexistente, antes de que el backend elimine su historial local. No elimina los respaldos de Google Drive. «Vaciar base» está disponible en el estado del conocimiento aunque no haya PDFs completados en el historial.

La ingestión conserva el binario original después de extraer texto para que el cargador PDF pueda indexarlo por página. La carpeta raíz de respaldo debe ser accesible por la cuenta de Drive conectada; volver a autenticar una cuenta distinta puede invalidar ese acceso. Una respuesta vacía, no JSON o sin confirmación explícita de indexación deja el trabajo en `unknown` y conserva sus archivos temporales; no se registra como completado.

El tutor recupera material antes de responder en chat/práctica, utiliza los últimos mensajes de esa sesión para interpretar seguimientos y puede reformular búsquedas insuficientes sin cambiar de namespace. Explica desde los fundamentos con ejemplos concretos y un tono docente natural, sin repetir fórmulas como «según el libro». Las citas estructuradas conservan la página del PDF; cuando se incluyen referencias en el texto, se agrupan discretamente al final. La conversación identifica el curso, pero no muestra documentos ni avisos sobre la ausencia de material. Cargar un libro en otra materia no lo hace accesible desde esta conversación.

**Extender conocimiento** se aplica como permiso explícito, no por la veracidad de una cadena: `"false"` no activa la extensión. La recuperación compartida comprueba semánticamente si los fragmentos respaldan la consulta, selecciona sus fuentes y descarta coincidencias incidentales. Con la extensión desactivada, una consulta sin respaldo no llega al generador de chat/práctica ni al de recursos; devuelve una explicación breve del límite. Con la extensión activada se conserva la posibilidad de complementar con conocimiento general. Una verificación malformada o con fuentes inexistentes detiene la ejecución: no autoriza la respuesta por defecto. El control de pertinencia añade una llamada de modelo cuando hay fragmentos; se omite si la recuperación está vacía.

Las instrucciones pedagógicas se construyen en un único punto, por encima de formatos incompatibles del coordinador o heredados del historial. **Chat** desarrolla explicaciones y ejemplos, sin secciones «Esquema» ni árboles ASCII automáticos. **Práctica** distingue actividades, respuestas, pistas y soluciones solicitadas, y explica los aciertos y errores. **Recursos** sintetiza una relación o proceso en un diagrama del catálogo compatible, con una explicación de cómo interpretarlo; recibe también la imagen actual y referencias conversacionales recientes. Se mantienen los permisos de conocimiento externo y el aislamiento entre cursos.

La orientación del coordinador se entrega como contexto separado, sin incorporarla a las reglas principales. La continuidad utiliza el historial persistido enviado por el backend, sin una segunda memoria de n8n que acumule prompts, material recuperado y formatos antiguos.

Recursos requiere título y explicación didáctica además del gráfico. Sus instrucciones priorizan un objetivo de aprendizaje, el tipo visual adecuado y relaciones respaldadas; distinguen causas concurrentes, condiciones y resultados en lugar de encadenar conceptos indiscriminadamente. La explicación orienta la lectura y propone una conclusión o comprobación de comprensión. La pertinencia y la calidad conceptual siguen dependiendo de modelos: este control no constituye una prueba formal de todas las afirmaciones o flechas.

Las nuevas cargas usan fragmentos de hasta **3.200 caracteres** con **150 de solapamiento**, respetando los límites de página del cargador PDF; no son tokens ni un tamaño óptimo universal. Cada archivo se indexa en una iteración independiente para evitar que los subnodos reutilicen los metadatos del primer PDF de un lote. Se conserva una ficha descriptiva (título/autor disponibles, páginas, extracto inicial y posibles encabezados) en el historial existente, sin migración. No es un resumen completo ni garantiza detectar todos los capítulos.

Estos ajustes no reindexan libros existentes: la recuperación y las citas mejoran inmediatamente, pero el nuevo fragmentado y la ficha ampliada requieren una nueva carga. Para reemplazar un libro, elimina primero ese documento desde el curso y después súbelo de nuevo; no repitas cargas sobre sus vectores anteriores porque pueden duplicarse. Reinicia el backend tras actualizar el código. Los resúmenes se limitan al material efectivamente recuperado; no se presentan unos fragmentos como una lectura exhaustiva del libro. No se añade infraestructura de métricas o evaluación.

## Validación y límites

### Comprobaciones de los cambios RAG y frontend

Desde la raíz, con las dependencias ya instaladas:

```powershell
node --test .\automation\workflows\rag-workflows.test.mjs
& .\backend\_venv\Scripts\python.exe -m unittest testing.test_rag_ingestion -v
Set-Location .\frontend
npm run lint
npm run build
```

La suite RAG Python usa aislamiento con SQL, red y lectura dotenv bloqueados; no carga la configuración real ni sube PDF. Las pruebas Node ejecutan la lógica de los exports con fixtures: no llaman a OpenAI/Pinecone ni publican workflows. El 2026-11-18 pasaron **15 pruebas Node y 9 pruebas Python**, además del lint y build frontend; este último conserva un aviso de chunks mayores de 500 kB. Estos resultados no certifican el comportamiento universal de los modelos ni una instalación n8n distinta.

La suite histórica y sus modalidades están documentadas en [testing/README.md](testing/README.md) y [testing/REGRESSION.md](testing/REGRESSION.md). Las pruebas con escrituras SQL, limpieza, indexación o proveedores reales necesitan destino confirmado y autorización propia; no ejecutarlas como si fueran pruebas unitarias.

### Límites operativos conocidos

- **PDF y cobertura:** se requiere texto extraíble; no existe OCR integrado para escaneos. Recuperar hasta 20 candidatos con contexto acotado no equivale a leer exhaustivamente un libro. Citas y verificación semántica mejoran la fundamentación, pero siguen dependiendo de modelos.
- **Procesamiento síncrono:** la carga espera a n8n; los timeouts o respuestas ambiguas quedan en `unknown`. No hay cola durable ni idempotencia completa entre PostgreSQL, Pinecone y Drive. Una carga parcialmente completada puede dejar vectores aunque falle el respaldo; revisar antes de reintentar.
- **Retención:** guardar PDF en Drive no habilita automáticamente la recuperación de archivos temporales ni sincronización. Definir políticas de respaldo, restauración y borrado para PostgreSQL, Pinecone, Drive y ejecuciones n8n por separado.
- **Consumo:** el límite de tokens y el costo estimado no son facturación real del proveedor. La comprobación de saldo no reserva atómicamente el consumo ante concurrencia; llamadas internas adicionales de IA no deben asumirse completamente reflejadas en la estimación actual.
- **Despliegue:** no hay migrador automático para bases existentes ni certificación integral de aislamiento, accesibilidad o escalabilidad. Proteger webhooks, configurar TLS, permisos mínimos, backups y almacenamiento compartido del limitador antes de escalar.
- **Datos académicos:** los textos y conversaciones pasan por los servicios configurados. Usar material con autorización, evaluar las políticas de los proveedores y no almacenar secretos ni datos personales de prueba en exports, evidencias o Git.

## Licencia y documentación relacionada

Consultar [LICENSE](LICENSE) para las condiciones del código y las licencias propias de sus dependencias. La licencia del repositorio no concede derechos sobre PDF o contenido de terceros.

- [Contexto y hoja de ruta](docs/project-context.md)
- [Historial de versiones](CHANGELOG.md)
- [Constitución de desarrollo](docs/specs/constitution.md)
- [Pruebas y regresión](testing/README.md)
