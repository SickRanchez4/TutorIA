
# TutorIA

Plataforma web para la gestión académica de cursos, estudiantes y asistencia con IA.

## Versión actual

**v0.1.0 — 2026-09-30:** primera versión funcional.

Consulte el historial de versiones en [CHANGELOG.md](CHANGELOG.md).

## Instalación inicial de la base de datos

En SQL Server, ejecutar los archivos completos en este orden, usando SSMS:

1. [database/001-initial-schema.sql](database/001-initial-schema.sql): crea la base `tutoria-webapp` si no existe y sus 16 tablas. Requiere una base vacía y se ejecuta una sola vez; no es una migración para bases con datos. Si el usuario SQL no puede crear bases, un administrador debe crear primero la base vacía con ese nombre.
2. [database/001-seed-data.sql](database/001-seed-data.sql): carga roles, cuenta de administración, tarifa IA y ejemplos académicos. Puede repetirse sin duplicar los datos ni sobrescribir contraseñas o suscripciones existentes.

No hay que activar SQLCMD, suministrar hashes externamente ni definir variables de entorno para **ejecutar estos scripts**. Los valores editables están al principio del seed: administración, institución, dominio, plan, cuota, tarifa y personas. Mantener el bloque completo, sin insertar separadores `GO` entre sus constantes y su uso.

El seed incluye una institución, un coordinador, 12 estudiantes con nombres naturales, dos cursos, matrículas, conversaciones, agenda y consumo histórico. La suscripción inicial dura 12 meses desde la instalación. Para empezar sin ejemplos académicos, cambiar `@CargarEjemplos` a `0`: solo se cargarán roles, administración y tarifa IA. No se inventan fuentes RAG, ingestiones completadas ni notificaciones enviadas.

| Cuenta inicial | Contraseña inicial pública |
|---|---|
| Administración: `administracion@demo.com` | `password` |
| Coordinación: `coordinador@demo.com` | `password` |
| Estudiante: `estudiante@demo.com` y demás estudiantes | `password` |

**Cambiar estas contraseñas desde Perfil antes de exponer la aplicación.** La base almacena hashes PBKDF2-SHA256 compatibles con Werkzeug; cambiar el texto de una contraseña en un comentario no actualiza su hash. Para una instalación real, usar el modo sin ejemplos y cambiar inmediatamente la contraseña de administración; las demás cuentas se crean desde la app.

Los scripts no crean el usuario de conexión de SQL Server ni pueden configurar por sí solos la aplicación: el backend sigue necesitando `DATABASE_URL` apuntando a `tutoria-webapp`, `JWT_SECRET_KEY` y los webhooks n8n para IA. Son configuración del despliegue, no requisitos extra del seed. No usar `db.create_all()` para inicializar estas tablas, porque los UUID nativos de SQL Server se representan como strings en el ORM.

## Despliegue con Docker

El despliegue crea dos servicios:

- `frontend`: Nginx sirve la aplicación Vue y redirige `/api/*` al backend.
- `backend`: Flask se ejecuta con Gunicorn y se conecta al SQL Server configurado externamente.

### 1. Configurar secretos

En PowerShell, crea el archivo de variables locales a partir del ejemplo:

```powershell
Copy-Item .env.docker.example .env.docker
```

Completa `JWT_SECRET_KEY`, `DATABASE_URL` y las URL de n8n en [.env.docker.example](.env.docker.example). No subas `.env.docker` al repositorio.

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
- `http://localhost:8080/api/readyz`: confirma también conectividad con SQL Server.

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
- El backend utiliza ODBC Driver 17 para SQL Server dentro de su imagen Docker.
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
DATABASE_URL=mssql+pyodbc://USUARIO:CONTRASENA@HOST:1433/BASE_DE_DATOS?driver=ODBC+Driver+17+for+SQL+Server
N8N_CHAT_WEBHOOK_URL=https://tu-n8n.example/webhook/course-chat
N8N_EMBEDDINGS_WEBHOOK_URL=https://tu-n8n.example/webhook/upload-knowledge
N8N_KNOWLEDGE_ADMIN_WEBHOOK_URL=https://tu-n8n.example/webhook/knowledge-admin
```

Use URLs de producción de n8n (`/webhook/...`), nunca `/webhook-test/...`. Si la contraseña de SQL Server contiene caracteres reservados (`@`, `:`, `/` o `?`), codifíquelos en formato URL. Verifique además que el firewall de SQL Server permita conexiones desde la IP pública del Cloud Server.

### 3. Aplicar migraciones y desplegar

Para una instalación nueva, ejecute sobre SQL Server [database/001-initial-schema.sql](database/001-initial-schema.sql) y después [database/001-seed-data.sql](database/001-seed-data.sql), según la sección de instalación inicial. En producción use el modo sin ejemplos y cambie la contraseña pública de administración antes de publicar. No vuelva a ejecutar el esquema inicial sobre una base existente: los cambios futuros requieren una migración específica.

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

`/healthz` confirma el frontend, `/api/healthz` el proceso Flask y `/api/readyz` también la conexión a SQL Server. Si el certificado no se emite, confirme primero DNS, puertos 80/443 y los logs del contenedor `caddy`.

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

El detalle de cada curso muestra un resumen compacto de documentos indexados, fecha de indexación y trabajos que requieren atención. Los PDF se conservan únicamente mientras viva el contenedor backend; el historial y las métricas permanecen registrados en SQL Server.

Para eliminar un PDF específico o vaciar la base de conocimiento de un curso, importe y active [automation/workflows/knowledge-index-admin.json](automation/workflows/knowledge-index-admin.json) en n8n. Configure `N8N_KNOWLEDGE_ADMIN_WEBHOOK_URL` con su única URL de producción. El flujo recibe `action` con `delete_document` o `clear_course`, junto con el curso, institución y —solo para eliminar un PDF— `archivo`. El agente elimina los vectores en Pinecone y el backend actualiza después su historial local.
