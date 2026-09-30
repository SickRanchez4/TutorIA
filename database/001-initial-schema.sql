/*
  TutorIA — esquema de instalación inicial (SQL Server 2016 o posterior).
  1. Ejecutar este archivo una sola vez sobre una base vacía.
  2. Ejecutar 001-seed-data.sql para crear las cuentas iniciales.
*/
IF DB_ID(N'tutoria-webapp') IS NULL
    EXEC(N'CREATE DATABASE [tutoria-webapp]');
GO
USE [tutoria-webapp];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET NUMERIC_ROUNDABORT OFF;

IF EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID(N'dbo'))
    THROW 50000, N'El esquema inicial requiere una base vacía. No ejecutarlo sobre datos existentes.', 1;

BEGIN TRY
    BEGIN TRANSACTION;

    CREATE TABLE dbo.roles (
        id int IDENTITY(1,1) NOT NULL PRIMARY KEY,
        name nvarchar(50) NOT NULL CONSTRAINT uq_roles_name UNIQUE,
        CONSTRAINT chk_role_name CHECK (name IN (N'estudiante', N'coordinador', N'super_admin'))
    );

    CREATE TABLE dbo.planes (
        id int IDENTITY(1,1) NOT NULL PRIMARY KEY,
        nombre nvarchar(100) NOT NULL CONSTRAINT uq_planes_nombre UNIQUE,
        -- NULL = ilimitado, 0 = sin capacidad, igual que en la app.
        max_cuentas int NULL,
        max_almacenamiento_gb decimal(5,2) NULL,
        is_active bit NOT NULL DEFAULT 1,
        created_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT ck_planes_limites CHECK (
            (max_cuentas IS NULL OR max_cuentas >= 0)
            AND (max_almacenamiento_gb IS NULL OR max_almacenamiento_gb >= 0))
    );

    CREATE TABLE dbo.instituciones (
        id uniqueidentifier NOT NULL DEFAULT NEWID() PRIMARY KEY,
        nombre nvarchar(255) NOT NULL,
        dominio_permitido nvarchar(100) NULL,
        is_active bit NOT NULL DEFAULT 1,
        created_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME()
    );

    CREATE TABLE dbo.suscripciones (
        id uniqueidentifier NOT NULL DEFAULT NEWID() PRIMARY KEY,
        institucion_id uniqueidentifier NOT NULL CONSTRAINT uq_suscripciones_institucion UNIQUE,
        plan_id int NOT NULL,
        limite_tokens_mensual bigint NOT NULL,
        fecha_inicio datetime2(7) NOT NULL,
        fecha_fin datetime2(7) NOT NULL,
        is_active bit NOT NULL DEFAULT 1,
        created_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT fk_suscripciones_institucion FOREIGN KEY (institucion_id) REFERENCES dbo.instituciones(id) ON DELETE CASCADE,
        CONSTRAINT fk_suscripciones_plan FOREIGN KEY (plan_id) REFERENCES dbo.planes(id),
        CONSTRAINT ck_suscripciones_limites CHECK (limite_tokens_mensual >= 0 AND fecha_fin > fecha_inicio)
    );

    CREATE TABLE dbo.users (
        id uniqueidentifier NOT NULL DEFAULT NEWID() PRIMARY KEY,
        institucion_id uniqueidentifier NULL,
        email nvarchar(255) NOT NULL CONSTRAINT uq_users_email UNIQUE,
        email_verified bit NOT NULL DEFAULT 0,
        password_hash nvarchar(255) NOT NULL,
        first_name nvarchar(100) NOT NULL,
        last_name nvarchar(100) NOT NULL,
        phone nvarchar(20) NULL,
        is_active bit NOT NULL DEFAULT 1,
        created_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT fk_users_institucion FOREIGN KEY (institucion_id) REFERENCES dbo.instituciones(id) ON DELETE CASCADE
    );

    CREATE TABLE dbo.user_roles (
        user_id uniqueidentifier NOT NULL,
        role_id int NOT NULL,
        assigned_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        PRIMARY KEY (user_id, role_id),
        CONSTRAINT fk_user_roles_user FOREIGN KEY (user_id) REFERENCES dbo.users(id) ON DELETE CASCADE,
        CONSTRAINT fk_user_roles_role FOREIGN KEY (role_id) REFERENCES dbo.roles(id) ON DELETE CASCADE
    );

    CREATE TABLE dbo.cursos (
        id int IDENTITY(1,1) NOT NULL PRIMARY KEY,
        institucion_id uniqueidentifier NOT NULL,
        nombre nvarchar(255) NOT NULL,
        codigo nvarchar(50) NULL,
        descripcion nvarchar(1000) NULL,
        is_active bit NOT NULL DEFAULT 1,
        CONSTRAINT fk_cursos_institucion FOREIGN KEY (institucion_id) REFERENCES dbo.instituciones(id) ON DELETE CASCADE
    );

    CREATE TABLE dbo.estudiante_cursos (
        id uniqueidentifier NOT NULL DEFAULT NEWID() PRIMARY KEY,
        -- Se conserva la nulabilidad del ORM; las altas de la app requieren ambos.
        user_id uniqueidentifier NULL,
        curso_id int NULL,
        is_active bit NOT NULL DEFAULT 1,
        fecha_inscripcion datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT uq_estudiante_curso UNIQUE (user_id, curso_id),
        CONSTRAINT FK_estudiante_cursos_user FOREIGN KEY (user_id) REFERENCES dbo.users(id),
        CONSTRAINT FK_estudiante_cursos_curso FOREIGN KEY (curso_id) REFERENCES dbo.cursos(id)
    );

    CREATE TABLE dbo.configuracion_ia (
        curso_id int NOT NULL PRIMARY KEY,
        system_prompt nvarchar(2000) NOT NULL,
        temperatura decimal(3,2) NOT NULL DEFAULT 0.2,
        modos_permitidos nvarchar(200) NOT NULL DEFAULT N'chat,practicar,recursos',
        extender_conocimiento bit NOT NULL DEFAULT 0,
        updated_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT fk_configuracion_ia_curso FOREIGN KEY (curso_id) REFERENCES dbo.cursos(id) ON DELETE CASCADE,
        CONSTRAINT ck_configuracion_ia_temperatura CHECK (temperatura BETWEEN 0 AND 2)
    );

    CREATE TABLE dbo.sesiones_chat (
        id uniqueidentifier NOT NULL DEFAULT NEWID() PRIMARY KEY,
        user_id uniqueidentifier NOT NULL,
        curso_id int NOT NULL,
        titulo nvarchar(200) NULL DEFAULT N'Nueva Conversación',
        is_active bit NOT NULL DEFAULT 1,
        created_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        -- NO ACTION en usuario evita dos rutas de cascada desde institución.
        -- Los endpoints eliminan las conversaciones antes de eliminar la cuenta.
        CONSTRAINT fk_sesiones_chat_user FOREIGN KEY (user_id) REFERENCES dbo.users(id),
        CONSTRAINT fk_sesiones_chat_curso FOREIGN KEY (curso_id) REFERENCES dbo.cursos(id) ON DELETE CASCADE
    );

    CREATE TABLE dbo.mensajes_chat (
        id uniqueidentifier NOT NULL DEFAULT NEWID() PRIMARY KEY,
        sesion_chat_id uniqueidentifier NOT NULL,
        rol nvarchar(20) NOT NULL,
        contenido nvarchar(max) NOT NULL,
        citas_contexto_json nvarchar(max) NULL,
        imagen_nombre nvarchar(255) NULL,
        tipo_interaccion nvarchar(50) NOT NULL DEFAULT N'consulta',
        created_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT fk_mensajes_chat_sesion FOREIGN KEY (sesion_chat_id) REFERENCES dbo.sesiones_chat(id) ON DELETE CASCADE,
        CONSTRAINT chk_rol_chat CHECK (rol IN (N'assistant', N'user'))
    );

    CREATE TABLE dbo.actividades_agenda (
        id uniqueidentifier NOT NULL DEFAULT NEWID() PRIMARY KEY,
        curso_id int NOT NULL,
        titulo nvarchar(255) NOT NULL,
        descripcion nvarchar(max) NULL,
        tipo nvarchar(50) NOT NULL,
        fecha_limite datetime2(7) NOT NULL,
        estado nvarchar(50) NULL DEFAULT N'vigente',
        created_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT fk_actividades_agenda_curso FOREIGN KEY (curso_id) REFERENCES dbo.cursos(id) ON DELETE CASCADE
    );

    CREATE TABLE dbo.log_notificaciones (
        id uniqueidentifier NOT NULL DEFAULT NEWID() PRIMARY KEY,
        user_id uniqueidentifier NOT NULL,
        actividad_agenda_id uniqueidentifier NOT NULL,
        tipo_notificacion nvarchar(50) NOT NULL,
        estado_envio nvarchar(50) NOT NULL,
        fecha_ejecucion datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT fk_log_notificaciones_user FOREIGN KEY (user_id) REFERENCES dbo.users(id),
        -- Permite eliminar un curso incluso si sus actividades ya tienen logs.
        CONSTRAINT fk_log_notificaciones_actividad FOREIGN KEY (actividad_agenda_id) REFERENCES dbo.actividades_agenda(id) ON DELETE CASCADE
    );

    CREATE TABLE dbo.precios_modelo_ia (
        id int IDENTITY(1,1) NOT NULL PRIMARY KEY,
        proveedor nvarchar(50) NOT NULL,
        modelo nvarchar(100) NOT NULL,
        precio_prompt_por_millon_usd decimal(12,6) NOT NULL,
        precio_completion_por_millon_usd decimal(12,6) NOT NULL,
        vigente_desde datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        vigente_hasta datetime2(7) NULL,
        is_active bit NOT NULL DEFAULT 1,
        CONSTRAINT uq_precios_modelo_ia_version UNIQUE (proveedor, modelo, vigente_desde),
        CONSTRAINT ck_precios_modelo_ia_valores CHECK (
            precio_prompt_por_millon_usd >= 0 AND precio_completion_por_millon_usd >= 0
            AND (vigente_hasta IS NULL OR vigente_hasta > vigente_desde))
    );

    CREATE TABLE dbo.consumo_tokens (
        id uniqueidentifier NOT NULL DEFAULT NEWID() PRIMARY KEY,
        institucion_id uniqueidentifier NOT NULL,
        curso_id int NULL,
        user_id uniqueidentifier NOT NULL,
        tipo_operacion nvarchar(50) NOT NULL,
        prompt_tokens int NOT NULL,
        completion_tokens int NOT NULL,
        costo_estimado_usd decimal(10,6) NOT NULL,
        precio_modelo_ia_id int NULL,
        proveedor_modelo nvarchar(50) NULL,
        modelo_ia nvarchar(100) NULL,
        precio_prompt_por_millon_usd decimal(12,6) NULL,
        precio_completion_por_millon_usd decimal(12,6) NULL,
        fecha datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        -- No cascada desde institución/usuario: curso ya usa SET NULL.
        -- SQL Server prohíbe múltiples rutas de cascada desde institución.
        CONSTRAINT fk_consumo_tokens_institucion FOREIGN KEY (institucion_id) REFERENCES dbo.instituciones(id),
        CONSTRAINT fk_consumo_tokens_user FOREIGN KEY (user_id) REFERENCES dbo.users(id),
        CONSTRAINT fk_consumo_tokens_curso FOREIGN KEY (curso_id) REFERENCES dbo.cursos(id) ON DELETE SET NULL,
        CONSTRAINT fk_consumo_tokens_precio_modelo_ia FOREIGN KEY (precio_modelo_ia_id) REFERENCES dbo.precios_modelo_ia(id) ON DELETE SET NULL,
        CONSTRAINT ck_consumo_tokens_valores CHECK (prompt_tokens >= 0 AND completion_tokens >= 0 AND costo_estimado_usd >= 0)
    );

    CREATE TABLE dbo.rag_ingestion_jobs (
        id nvarchar(36) NOT NULL PRIMARY KEY,
        institucion_id uniqueidentifier NOT NULL,
        curso_id int NOT NULL,
        coordinador_id uniqueidentifier NULL,
        estado nvarchar(20) NOT NULL DEFAULT N'queued',
        intento int NOT NULL DEFAULT 1,
        documentos_json nvarchar(max) NOT NULL DEFAULT N'[]',
        chunks_indexados int NOT NULL DEFAULT 0,
        archivos_procesados int NOT NULL DEFAULT 0,
        respuesta_procesador_json nvarchar(max) NULL,
        error_message nvarchar(1000) NULL,
        created_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
        completed_at datetime2(7) NULL,
        -- coordinador_id es una referencia histórica, no una dependencia de borrado.
        CONSTRAINT fk_rag_ingestion_jobs_institucion FOREIGN KEY (institucion_id) REFERENCES dbo.instituciones(id) ON DELETE CASCADE,
        CONSTRAINT fk_rag_ingestion_jobs_curso FOREIGN KEY (curso_id) REFERENCES dbo.cursos(id),
        CONSTRAINT ck_rag_ingestion_jobs_estado CHECK (estado IN (N'queued', N'processing', N'completed', N'failed', N'unknown')),
        CONSTRAINT ck_rag_ingestion_jobs_metricas CHECK (intento >= 1 AND chunks_indexados >= 0 AND archivos_procesados >= 0)
    );

    -- Índices que corresponden a cuotas, analíticas, chat y catálogos por tenant.
    -- La PK de user_roles y el UNIQUE de email ya cubren sus búsquedas.
    CREATE INDEX idx_users_institucion ON dbo.users(institucion_id) WHERE is_active = 1;
    CREATE INDEX ix_cursos_institucion ON dbo.cursos(institucion_id);
    CREATE UNIQUE INDEX uq_cursos_institucion_codigo ON dbo.cursos(institucion_id, codigo) WHERE codigo IS NOT NULL;
    CREATE INDEX ix_estudiante_cursos_curso ON dbo.estudiante_cursos(curso_id, is_active);
    CREATE INDEX ix_sesiones_chat_user_curso ON dbo.sesiones_chat(user_id, curso_id, updated_at DESC);
    CREATE INDEX idx_mensajes_chat_sesion ON dbo.mensajes_chat(sesion_chat_id, created_at);
    CREATE INDEX ix_actividades_agenda_curso ON dbo.actividades_agenda(curso_id, fecha_limite);
    CREATE INDEX idx_actividades_fecha ON dbo.actividades_agenda(fecha_limite);
    CREATE INDEX ix_log_notificaciones_actividad ON dbo.log_notificaciones(actividad_agenda_id);
    CREATE INDEX ix_log_notificaciones_user ON dbo.log_notificaciones(user_id);
    CREATE INDEX ix_consumo_tokens_institucion_fecha ON dbo.consumo_tokens(institucion_id, fecha)
        INCLUDE (user_id, curso_id, prompt_tokens, completion_tokens);
    CREATE INDEX ix_consumo_tokens_user ON dbo.consumo_tokens(user_id);
    CREATE UNIQUE INDEX uq_precio_modelo_ia_actual ON dbo.precios_modelo_ia(proveedor, modelo)
        WHERE is_active = 1 AND vigente_hasta IS NULL;
    CREATE INDEX ix_rag_ingestion_jobs_curso_created ON dbo.rag_ingestion_jobs(curso_id, created_at DESC);
    CREATE INDEX ix_rag_ingestion_jobs_institucion_estado ON dbo.rag_ingestion_jobs(institucion_id, estado);

    COMMIT TRANSACTION;
    PRINT N'Esquema inicial de TutorIA creado correctamente.';
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
GO