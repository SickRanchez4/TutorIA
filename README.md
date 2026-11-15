
# TutorIA

Plataforma web para la gestión académica de cursos, estudiantes y asistencia con IA.

## Versión actual

**v0.1.0 — 2026-09-30:** primera versión funcional.

Consulte el historial de versiones en [CHANGELOG.md](CHANGELOG.md).

## Especificaciones y pruebas

Estado documental actualizado el **2026-11-14**. Para empezar a trabajar, consulte el [contexto del proyecto](docs/project-context.md): producto, actores, organización del repositorio, arquitectura, funcionalidades, criterios de trabajo y hoja de ruta. La versión declarada sigue siendo v0.1.0; los incrementos posteriores no certifican el MVP completo.

| Documento | Aprobación / referencia | Construcción | Verificación |
|---|---|---|---|
| [Spec-000](docs/specs/spec-000-mvp/Spec-000-mvp.md) | Baseline retrospectivo cerrado de v0.1.0 | MVP existente | Describe alcance y límites; no certificación integral |
| [SPEC-001](docs/specs/spec-001-tests/spec.md) | Spec y plan aprobados | Proyecto de pruebas implementado; evaluación cerrada con defectos | [Registro](docs/specs/spec-001-tests/test.md): 23 aislados y 53 controles; integración/sistema históricos. RF-5/RNF-6 fallidos |
| [SPEC-002](docs/specs/spec-002-ui-ux/spec.md) | Spec aprobada; [plan y paleta aprobados el 2026-10-31](docs/specs/spec-002-ui-ux/plan.md) | C0 preparado y refactor frontend previo a C1 implementado; C1–C5 pendientes de completar | [Registro](docs/specs/spec-002-ui-ux/test.md): 28 requisitos no ejecutados integralmente; lint/build posteriores satisfactorios, revisión visual y Excel con API simulada; S-2 real pendiente |
| [SPEC-008](docs/specs/spec-008-postgresql/spec.md) | Cambio PostgreSQL 18.x y credenciales separadas autorizado | Base nueva externa; configuración, modelos, scripts y soporte adaptados | Solo configuración/compilación por decisión del desarrollador; sin tests ni integración real |

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
docker compose up --build -d
```

La aplicación queda expuesta en `http://localhost:8080` por defecto. Para cambiarlo, define `APP_PORT` en `.env.docker`.

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
docker compose up --build -d
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
```

Use URLs de producción de n8n (`/webhook/...`), nunca `/webhook-test/...`. No codifique la contraseña como URL. Configure la CA confiable para `verify-full` y verifique que el firewall y `pg_hba.conf` de PostgreSQL permitan el acceso desde el backend; no publique el puerto de la base indiscriminadamente.

### 3. Aplicar migraciones y desplegar

Para una instalación nueva, ejecute sobre PostgreSQL 18.x [database/001-initial-schema.sql](database/001-initial-schema.sql) y después [database/001-seed-data.sql](database/001-seed-data.sql), según la sección de instalación inicial. En producción use el modo sin ejemplos y cambie la contraseña pública de administración antes de publicar. No vuelva a ejecutar el esquema inicial sobre una base existente: los cambios futuros requieren una migración específica.

Después, construya e inicie los contenedores desde `/opt/tutoria`:

```bash
docker compose -f docker-compose.yml -f docker-compose.production.yml up --build -d
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
docker compose -f docker-compose.yml -f docker-compose.production.yml up --build -d
docker image prune -f
```

No ejecute `docker compose down -v` durante una actualización: elimina los volúmenes persistentes de Caddy y obligará a emitir nuevamente los certificados HTTPS.

## Operación de la base de conocimiento RAG

El esquema de instalación [database/001-initial-schema.sql](database/001-initial-schema.sql) incluye la tabla de trabajos de ingestión RAG y sus índices para el historial de cargas, estado, documentos recibidos y métricas devueltas por n8n. Las bases anteriores deben incorporar esa tabla mediante una migración, no volviendo a ejecutar la instalación completa.

El detalle de cada curso muestra un resumen compacto de documentos indexados, fecha de indexación y trabajos que requieren atención. Los PDF se conservan únicamente mientras viva el contenedor backend; el historial y las métricas permanecen registrados en PostgreSQL.

Para eliminar un PDF específico o vaciar la base de conocimiento de un curso, importe y active [automation/workflows/knowledge-index-admin.json](automation/workflows/knowledge-index-admin.json) en n8n. Configure `N8N_KNOWLEDGE_ADMIN_WEBHOOK_URL` con su única URL de producción. El flujo recibe `action` con `delete_document` o `clear_course`, junto con el curso, institución y —solo para eliminar un PDF— `archivo`. El agente elimina los vectores en Pinecone y el backend actualiza después su historial local.
