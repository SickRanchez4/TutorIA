
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

## Operación de la base de conocimiento RAG

Antes de desplegar esta versión, aplique una vez la migración [database/migrations/20260731_rag_ingestion_jobs.sql](database/migrations/20260731_rag_ingestion_jobs.sql). Crea el historial de cargas, su estado, los documentos recibidos y las métricas devueltas por n8n.

El detalle de cada curso muestra un resumen compacto de documentos indexados, fecha de indexación y trabajos que requieren atención. Los PDF se conservan en el volumen `rag_uploads` para permitir reintentos; en un despliegue con varias réplicas sustituya ese volumen por almacenamiento de objetos o un volumen compartido.

Para eliminar un PDF específico o vaciar la base de conocimiento de un curso, importe y active [automation/workflows/knowledge-index-admin.json](automation/workflows/knowledge-index-admin.json) en n8n. Configure `N8N_KNOWLEDGE_ADMIN_WEBHOOK_URL` con su única URL de producción. El flujo recibe `action` con `delete_document` o `clear_course`, junto con el curso, institución y —solo para eliminar un PDF— `archivo`. El agente elimina los vectores en Pinecone y el backend actualiza después su historial local.
