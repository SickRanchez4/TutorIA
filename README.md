
# TutorIA

Plataforma web para la gestión académica de cursos, estudiantes y asistencia con IA.

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

Antes de publicar la versión, ejecute sobre SQL Server el script principal [database/script-tutoria.sql](database/script-tutoria.sql) para aplicar el esquema base y los ajustes de compatibilidad incluidos en ese archivo. Luego aplique [database/populate-tutoria.sql](database/populate-tutoria.sql) para cargar los datos iniciales.

Después, construya e inicie los contenedores desde `/opt/tutoria`:

```bash
docker compose -f docker-compose.yml -f docker-compose.production.yml up --build -d
docker compose -f docker-compose.yml -f docker-compose.production.yml ps
docker compose -f docker-compose.yml -f docker-compose.production.yml logs -f
```

Caddy deja el frontend interno y publica exclusivamente HTTP/HTTPS. Redirige el tráfico a Nginx del servicio `frontend`, que a su vez entrega la SPA y reenvía `/api/*` al backend. Los PDF de RAG quedan en el volumen Docker `rag_uploads`, persistente entre reinicios y actualizaciones.

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

No ejecute `docker compose down -v` durante una actualización: elimina los volúmenes persistentes, incluidos los PDF usados por RAG y los certificados de Caddy.

## Operación de la base de conocimiento RAG

Antes de desplegar esta versión, asegúrese de que [database/script-tutoria.sql](database/script-tutoria.sql) haya sido ejecutado una vez, ya que incluye la tabla de trabajos de ingestión RAG y sus índices para el historial de cargas, estado, documentos recibidos y métricas devueltas por n8n.

El detalle de cada curso muestra un resumen compacto de documentos indexados, fecha de indexación y trabajos que requieren atención. Los PDF se conservan en el volumen `rag_uploads` para permitir reintentos; en un despliegue con varias réplicas sustituya ese volumen por almacenamiento de objetos o un volumen compartido.

Para eliminar un PDF específico o vaciar la base de conocimiento de un curso, importe y active [automation/workflows/knowledge-index-admin.json](automation/workflows/knowledge-index-admin.json) en n8n. Configure `N8N_KNOWLEDGE_ADMIN_WEBHOOK_URL` con su única URL de producción. El flujo recibe `action` con `delete_document` o `clear_course`, junto con el curso, institución y —solo para eliminar un PDF— `archivo`. El agente elimina los vectores en Pinecone y el backend actualiza después su historial local.
