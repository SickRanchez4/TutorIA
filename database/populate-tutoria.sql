-- Script: Add simulated super_admin user
-- =============================================

-- 1. Make sure the 'super_admin' role exists
IF NOT EXISTS (SELECT 1 FROM [dbo].[roles] WHERE [name] = 'super_admin')
    INSERT INTO [dbo].[roles] ([name]) VALUES ('super_admin');
GO

-- 2. Create the simulated super_admin user (only if the email does not already exist)
IF NOT EXISTS (SELECT 1 FROM [dbo].[users] WHERE [email] = 'administracion@tutoria.edu')
BEGIN
    DECLARE @SuperAdminId UNIQUEIDENTIFIER = NEWID();
    DECLARE @PasswordHash NVARCHAR(255) = CONVERT(NVARCHAR(255), HASHBYTES('SHA2_256', N'password'), 2);

    INSERT INTO [dbo].[users] (
        [id],
        [institucion_id],    -- NULL because super_admin is not tied to a single institution
        [email],
        [email_verified],
        [password_hash],
        [first_name],
        [last_name],
        [phone],
        [is_active]
    )
    VALUES (
        @SuperAdminId,
        NULL,
        'administracion@tutoria.edu',
        1,                   -- email verified
        @PasswordHash,
        'Elena',
        'Rojas',
        NULL,
        1                    -- active
    );

    -- 3. Assign the super_admin role to the new user
    DECLARE @RoleId INT = (SELECT [id] FROM [dbo].[roles] WHERE [name] = 'super_admin');
    INSERT INTO [dbo].[user_roles] ([user_id], [role_id])
    VALUES (@SuperAdminId, @RoleId);
END
GO

-- =============================================
-- Script: Insert simulated academic data for tutoria-webapp
-- =============================================
SET NOCOUNT ON;
GO

-- -----------------------------------------------------
-- AI model pricing (USD per million tokens)
-- Update this row with the provider's current published rate when it changes.
-- -----------------------------------------------------
IF NOT EXISTS (
    SELECT 1
    FROM [dbo].[precios_modelo_ia]
    WHERE [proveedor] = 'openai'
      AND [modelo] = 'gpt-5.4-mini'
      AND [is_active] = 1
      AND [vigente_hasta] IS NULL
)
BEGIN
    INSERT INTO [dbo].[precios_modelo_ia] (
        [proveedor],
        [modelo],
        [precio_prompt_por_millon_usd],
        [precio_completion_por_millon_usd],
        [vigente_desde],
        [is_active]
    )
    VALUES ('openai', 'gpt-5.4-mini', 0.750000, 4.500000, SYSUTCDATETIME(), 1);
END
GO

-- -----------------------------------------------------
-- 1. Roles
-- -----------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM [dbo].[roles] WHERE [name] = 'super_admin')
    INSERT INTO [dbo].[roles] ([name]) VALUES ('super_admin');
IF NOT EXISTS (SELECT 1 FROM [dbo].[roles] WHERE [name] = 'coordinador')
    INSERT INTO [dbo].[roles] ([name]) VALUES ('coordinador');
IF NOT EXISTS (SELECT 1 FROM [dbo].[roles] WHERE [name] = 'estudiante')
    INSERT INTO [dbo].[roles] ([name]) VALUES ('estudiante');

-- -----------------------------------------------------
-- 2. Plan
-- -----------------------------------------------------
DECLARE @PlanId INT;

IF NOT EXISTS (SELECT 1 FROM [dbo].[planes] WHERE [nombre] = 'Plan Académico Esencial')
BEGIN
    INSERT INTO [dbo].[planes] ([nombre], [max_cuentas], [max_almacenamiento_gb], [is_active])
    VALUES ('Plan Académico Esencial', 100, 50.0, 1);
    SET @PlanId = SCOPE_IDENTITY();
END
ELSE
    SET @PlanId = (SELECT [id] FROM [dbo].[planes] WHERE [nombre] = 'Plan Académico Esencial');

-- -----------------------------------------------------
-- 3. Institution
-- -----------------------------------------------------
DECLARE @InstitucionId UNIQUEIDENTIFIER;

IF NOT EXISTS (SELECT 1 FROM [dbo].[instituciones] WHERE [nombre] = 'Universidad del Valle Central')
BEGIN
    INSERT INTO [dbo].[instituciones] ([nombre], [dominio_permitido], [is_active])
    VALUES ('Universidad del Valle Central', 'uvc.edu', 1);
    SET @InstitucionId = (SELECT [id] FROM [dbo].[instituciones] WHERE [nombre] = 'Universidad del Valle Central');
END
ELSE
    SET @InstitucionId = (SELECT [id] FROM [dbo].[instituciones] WHERE [nombre] = 'Universidad del Valle Central');

-- -----------------------------------------------------
-- 4. Subscription
-- -----------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM [dbo].[suscripciones] WHERE [institucion_id] = @InstitucionId)
BEGIN
    INSERT INTO [dbo].[suscripciones] ([institucion_id], [plan_id], [limite_tokens_mensual], [fecha_inicio], [fecha_fin], [is_active])
    VALUES (@InstitucionId, @PlanId, 1000000, '2025-01-01', '2026-01-01', 1);
END

-- -----------------------------------------------------
-- 5. Users
-- -----------------------------------------------------
DECLARE @SuperAdminId UNIQUEIDENTIFIER;
DECLARE @CoordId UNIQUEIDENTIFIER;
DECLARE @Est1Id UNIQUEIDENTIFIER;
DECLARE @Est2Id UNIQUEIDENTIFIER;

-- 5.1 Super admin (reuse the one from previous script, or create if missing)
IF NOT EXISTS (SELECT 1 FROM [dbo].[users] WHERE [email] = 'administracion@tutoria.edu')
BEGIN
    SET @SuperAdminId = NEWID();
    INSERT INTO [dbo].[users] ([id], [institucion_id], [email], [email_verified], [password_hash], [first_name], [last_name], [is_active])
    VALUES (@SuperAdminId, NULL, 'administracion@tutoria.edu', 1,
            CONVERT(NVARCHAR(255), HASHBYTES('SHA2_256', N'SuperAdmin123!'), 2),
            'Elena', 'Rojas', 1);
END
ELSE
    SET @SuperAdminId = (SELECT [id] FROM [dbo].[users] WHERE [email] = 'administracion@tutoria.edu');

-- 5.2 Coordinator (linked to the institution)
IF NOT EXISTS (SELECT 1 FROM [dbo].[users] WHERE [email] = 'lucia.herrera@uvc.edu')
BEGIN
    SET @CoordId = NEWID();
    INSERT INTO [dbo].[users] ([id], [institucion_id], [email], [email_verified], [password_hash], [first_name], [last_name], [phone], [is_active])
    VALUES (@CoordId, @InstitucionId, 'lucia.herrera@uvc.edu', 1,
            CONVERT(NVARCHAR(255), HASHBYTES('SHA2_256', N'Password123!'), 2),
            'Lucía', 'Herrera', '700-1842', 1);
END
ELSE
    SET @CoordId = (SELECT [id] FROM [dbo].[users] WHERE [email] = 'lucia.herrera@uvc.edu');

-- 5.3 Student 1
IF NOT EXISTS (SELECT 1 FROM [dbo].[users] WHERE [email] = 'maria.gonzalez@uvc.edu')
BEGIN
    SET @Est1Id = NEWID();
    INSERT INTO [dbo].[users] ([id], [institucion_id], [email], [email_verified], [password_hash], [first_name], [last_name], [phone], [is_active])
    VALUES (@Est1Id, @InstitucionId, 'maria.gonzalez@uvc.edu', 1,
            CONVERT(NVARCHAR(255), HASHBYTES('SHA2_256', N'Password123!'), 2),
            'María', 'González', '700-2265', 1);
END
ELSE
    SET @Est1Id = (SELECT [id] FROM [dbo].[users] WHERE [email] = 'maria.gonzalez@uvc.edu');

-- 5.4 Student 2
IF NOT EXISTS (SELECT 1 FROM [dbo].[users] WHERE [email] = 'pedro.lopez@uvc.edu')
BEGIN
    SET @Est2Id = NEWID();
    INSERT INTO [dbo].[users] ([id], [institucion_id], [email], [email_verified], [password_hash], [first_name], [last_name], [phone], [is_active])
    VALUES (@Est2Id, @InstitucionId, 'pedro.lopez@uvc.edu', 1,
            CONVERT(NVARCHAR(255), HASHBYTES('SHA2_256', N'Password123!'), 2),
            'Pedro', 'López', '700-3108', 1);
END
ELSE
    SET @Est2Id = (SELECT [id] FROM [dbo].[users] WHERE [email] = 'pedro.lopez@uvc.edu');

-- -----------------------------------------------------
-- 6. User roles
-- -----------------------------------------------------
DECLARE @RoleSuperAdminId INT = (SELECT [id] FROM [dbo].[roles] WHERE [name] = 'super_admin');
DECLARE @RoleCoordId INT = (SELECT [id] FROM [dbo].[roles] WHERE [name] = 'coordinador');
DECLARE @RoleEstId INT = (SELECT [id] FROM [dbo].[roles] WHERE [name] = 'estudiante');

-- Assign super_admin role
IF NOT EXISTS (SELECT 1 FROM [dbo].[user_roles] WHERE [user_id] = @SuperAdminId AND [role_id] = @RoleSuperAdminId)
    INSERT INTO [dbo].[user_roles] ([user_id], [role_id]) VALUES (@SuperAdminId, @RoleSuperAdminId);

-- Assign coordinator role
IF NOT EXISTS (SELECT 1 FROM [dbo].[user_roles] WHERE [user_id] = @CoordId AND [role_id] = @RoleCoordId)
    INSERT INTO [dbo].[user_roles] ([user_id], [role_id]) VALUES (@CoordId, @RoleCoordId);

-- Assign student roles
IF NOT EXISTS (SELECT 1 FROM [dbo].[user_roles] WHERE [user_id] = @Est1Id AND [role_id] = @RoleEstId)
    INSERT INTO [dbo].[user_roles] ([user_id], [role_id]) VALUES (@Est1Id, @RoleEstId);

IF NOT EXISTS (SELECT 1 FROM [dbo].[user_roles] WHERE [user_id] = @Est2Id AND [role_id] = @RoleEstId)
    INSERT INTO [dbo].[user_roles] ([user_id], [role_id]) VALUES (@Est2Id, @RoleEstId);

-- -----------------------------------------------------
-- 7. Courses
-- -----------------------------------------------------
DECLARE @CursoMateId INT;
DECLARE @CursoFisicaId INT;

-- Mathematics course
IF NOT EXISTS (SELECT 1 FROM [dbo].[cursos] WHERE [codigo] = 'MAT-101' AND [institucion_id] = @InstitucionId)
BEGIN
    INSERT INTO [dbo].[cursos] ([institucion_id], [nombre], [codigo], [is_active], [descripcion])
    VALUES (@InstitucionId, 'Matemáticas Básicas', 'MAT-101', 1, 'Curso introductorio de álgebra y cálculo');
    SET @CursoMateId = SCOPE_IDENTITY();
END
ELSE
    SET @CursoMateId = (SELECT [id] FROM [dbo].[cursos] WHERE [codigo] = 'MAT-101' AND [institucion_id] = @InstitucionId);

-- Physics course
IF NOT EXISTS (SELECT 1 FROM [dbo].[cursos] WHERE [codigo] = 'FIS-201' AND [institucion_id] = @InstitucionId)
BEGIN
    INSERT INTO [dbo].[cursos] ([institucion_id], [nombre], [codigo], [is_active], [descripcion])
    VALUES (@InstitucionId, 'Física General', 'FIS-201', 1, 'Mecánica y termodinámica básica');
    SET @CursoFisicaId = SCOPE_IDENTITY();
END
ELSE
    SET @CursoFisicaId = (SELECT [id] FROM [dbo].[cursos] WHERE [codigo] = 'FIS-201' AND [institucion_id] = @InstitucionId);

-- -----------------------------------------------------
-- 8. AI Configuration (one per course)
-- -----------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM [dbo].[configuracion_ia] WHERE [curso_id] = @CursoMateId)
    INSERT INTO [dbo].[configuracion_ia] ([curso_id], [system_prompt], [temperatura], [modos_permitidos], [extender_conocimiento])
    VALUES (@CursoMateId, 'Eres un tutor de matemáticas para estudiantes universitarios.', 0.3, 'chat,practicar,recursos', 1);

IF NOT EXISTS (SELECT 1 FROM [dbo].[configuracion_ia] WHERE [curso_id] = @CursoFisicaId)
    INSERT INTO [dbo].[configuracion_ia] ([curso_id], [system_prompt], [temperatura], [modos_permitidos], [extender_conocimiento])
    VALUES (@CursoFisicaId, 'Eres un asistente de física que explica conceptos claramente.', 0.2, 'chat,practicar', 0);

-- -----------------------------------------------------
-- 9. Student enrollments
-- -----------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM [dbo].[estudiante_cursos] WHERE [user_id] = @Est1Id AND [curso_id] = @CursoMateId)
    INSERT INTO [dbo].[estudiante_cursos] ([user_id], [curso_id], [is_active])
    VALUES (@Est1Id, @CursoMateId, 1);

IF NOT EXISTS (SELECT 1 FROM [dbo].[estudiante_cursos] WHERE [user_id] = @Est1Id AND [curso_id] = @CursoFisicaId)
    INSERT INTO [dbo].[estudiante_cursos] ([user_id], [curso_id], [is_active])
    VALUES (@Est1Id, @CursoFisicaId, 1);

IF NOT EXISTS (SELECT 1 FROM [dbo].[estudiante_cursos] WHERE [user_id] = @Est2Id AND [curso_id] = @CursoMateId)
    INSERT INTO [dbo].[estudiante_cursos] ([user_id], [curso_id], [is_active])
    VALUES (@Est2Id, @CursoMateId, 1);

IF NOT EXISTS (SELECT 1 FROM [dbo].[estudiante_cursos] WHERE [user_id] = @Est2Id AND [curso_id] = @CursoFisicaId)
    INSERT INTO [dbo].[estudiante_cursos] ([user_id], [curso_id], [is_active])
    VALUES (@Est2Id, @CursoFisicaId, 1);

-- -----------------------------------------------------
-- 10. Chat sessions (one per student per course)
-- -----------------------------------------------------
DECLARE @SesionMateEst1 UNIQUEIDENTIFIER;
DECLARE @SesionMateEst2 UNIQUEIDENTIFIER;
DECLARE @SesionFisicaEst1 UNIQUEIDENTIFIER;

IF NOT EXISTS (SELECT 1 FROM [dbo].[sesiones_chat] WHERE [user_id] = @Est1Id AND [curso_id] = @CursoMateId AND [titulo] = 'Dudas de álgebra')
BEGIN
    SET @SesionMateEst1 = NEWID();
    INSERT INTO [dbo].[sesiones_chat] ([id], [user_id], [titulo], [is_active], [curso_id])
    VALUES (@SesionMateEst1, @Est1Id, 'Dudas de álgebra', 1, @CursoMateId);
END
ELSE
    SET @SesionMateEst1 = (SELECT TOP 1 [id] FROM [dbo].[sesiones_chat] WHERE [user_id] = @Est1Id AND [curso_id] = @CursoMateId AND [titulo] = 'Dudas de álgebra');

IF NOT EXISTS (SELECT 1 FROM [dbo].[sesiones_chat] WHERE [user_id] = @Est2Id AND [curso_id] = @CursoMateId AND [titulo] = 'Repaso ecuaciones')
BEGIN
    SET @SesionMateEst2 = NEWID();
    INSERT INTO [dbo].[sesiones_chat] ([id], [user_id], [titulo], [is_active], [curso_id])
    VALUES (@SesionMateEst2, @Est2Id, 'Repaso ecuaciones', 1, @CursoMateId);
END
ELSE
    SET @SesionMateEst2 = (SELECT TOP 1 [id] FROM [dbo].[sesiones_chat] WHERE [user_id] = @Est2Id AND [curso_id] = @CursoMateId AND [titulo] = 'Repaso ecuaciones');

IF NOT EXISTS (SELECT 1 FROM [dbo].[sesiones_chat] WHERE [user_id] = @Est1Id AND [curso_id] = @CursoFisicaId AND [titulo] = 'Consulta leyes de Newton')
BEGIN
    SET @SesionFisicaEst1 = NEWID();
    INSERT INTO [dbo].[sesiones_chat] ([id], [user_id], [titulo], [is_active], [curso_id])
    VALUES (@SesionFisicaEst1, @Est1Id, 'Consulta leyes de Newton', 1, @CursoFisicaId);
END
ELSE
    SET @SesionFisicaEst1 = (SELECT TOP 1 [id] FROM [dbo].[sesiones_chat] WHERE [user_id] = @Est1Id AND [curso_id] = @CursoFisicaId AND [titulo] = 'Consulta leyes de Newton');

-- -----------------------------------------------------
-- 11. Chat messages
-- -----------------------------------------------------
-- Add messages for the "Dudas de álgebra" session (if session exists and no messages yet)
IF EXISTS (SELECT 1 FROM [dbo].[sesiones_chat] WHERE [id] = @SesionMateEst1)
AND NOT EXISTS (SELECT 1 FROM [dbo].[mensajes_chat] WHERE [sesion_chat_id] = @SesionMateEst1)
BEGIN
    INSERT INTO [dbo].[mensajes_chat] ([sesion_chat_id], [rol], [contenido], [tipo_interaccion])
    VALUES 
        (@SesionMateEst1, 'user', '¿Cómo se resuelve una ecuación cuadrática?', 'consulta'),
        (@SesionMateEst1, 'assistant', 'Para resolver ax² + bx + c = 0 puedes usar la fórmula general: x = [-b ± √(b² - 4ac)] / (2a). ¿Necesitas un ejemplo?', 'consulta');
END

-- Add messages for the "Repaso ecuaciones" session
IF EXISTS (SELECT 1 FROM [dbo].[sesiones_chat] WHERE [id] = @SesionMateEst2)
AND NOT EXISTS (SELECT 1 FROM [dbo].[mensajes_chat] WHERE [sesion_chat_id] = @SesionMateEst2)
BEGIN
    INSERT INTO [dbo].[mensajes_chat] ([sesion_chat_id], [rol], [contenido], [tipo_interaccion])
    VALUES 
        (@SesionMateEst2, 'user', 'Necesito repasar factorización.', 'consulta'),
        (@SesionMateEst2, 'assistant', 'Claro, empecemos con el factor común. ¿Tienes un polinomio en mente?', 'consulta');
END

-- Add messages for the "Consulta leyes de Newton" session
IF EXISTS (SELECT 1 FROM [dbo].[sesiones_chat] WHERE [id] = @SesionFisicaEst1)
AND NOT EXISTS (SELECT 1 FROM [dbo].[mensajes_chat] WHERE [sesion_chat_id] = @SesionFisicaEst1)
BEGIN
    INSERT INTO [dbo].[mensajes_chat] ([sesion_chat_id], [rol], [contenido], [tipo_interaccion])
    VALUES 
        (@SesionFisicaEst1, 'user', 'Explícame la segunda ley de Newton.', 'consulta'),
        (@SesionFisicaEst1, 'assistant', 'F = m * a. La fuerza neta es igual a la masa por la aceleración.', 'consulta');
END

-- -----------------------------------------------------
-- 12. Activities / Agenda
-- -----------------------------------------------------
DECLARE @ActMate1 UNIQUEIDENTIFIER;
DECLARE @ActFisica1 UNIQUEIDENTIFIER;

-- Activity for Mathematics course
IF NOT EXISTS (SELECT 1 FROM [dbo].[actividades_agenda] WHERE [titulo] = 'Tarea 1: Resolver 10 ecuaciones' AND [curso_id] = @CursoMateId)
BEGIN
    SET @ActMate1 = NEWID();
    INSERT INTO [dbo].[actividades_agenda] ([id], [titulo], [descripcion], [tipo], [fecha_limite], [estado], [curso_id])
    VALUES (@ActMate1, 'Tarea 1: Resolver 10 ecuaciones', 'Resolver las ecuaciones del capítulo 2.', 'tarea', DATEADD(DAY, 7, GETDATE()), 'vigente', @CursoMateId);
END
ELSE
    SET @ActMate1 = (SELECT [id] FROM [dbo].[actividades_agenda] WHERE [titulo] = 'Tarea 1: Resolver 10 ecuaciones' AND [curso_id] = @CursoMateId);

-- Activity for Physics course
IF NOT EXISTS (SELECT 1 FROM [dbo].[actividades_agenda] WHERE [titulo] = 'Laboratorio: Medición de fuerzas' AND [curso_id] = @CursoFisicaId)
BEGIN
    SET @ActFisica1 = NEWID();
    INSERT INTO [dbo].[actividades_agenda] ([id], [titulo], [descripcion], [tipo], [fecha_limite], [estado], [curso_id])
    VALUES (@ActFisica1, 'Laboratorio: Medición de fuerzas', 'Realizar el experimento de la polea y entregar informe.', 'laboratorio', DATEADD(DAY, 14, GETDATE()), 'vigente', @CursoFisicaId);
END
ELSE
    SET @ActFisica1 = (SELECT [id] FROM [dbo].[actividades_agenda] WHERE [titulo] = 'Laboratorio: Medición de fuerzas' AND [curso_id] = @CursoFisicaId);

-- -----------------------------------------------------
-- 13. Notification log (one example per activity)
-- -----------------------------------------------------
IF EXISTS (SELECT 1 FROM [dbo].[actividades_agenda] WHERE [id] = @ActMate1)
AND NOT EXISTS (SELECT 1 FROM [dbo].[log_notificaciones] WHERE [actividad_agenda_id] = @ActMate1)
    INSERT INTO [dbo].[log_notificaciones] ([user_id], [actividad_agenda_id], [tipo_notificacion], [estado_envio])
    VALUES (@Est1Id, @ActMate1, 'email', 'enviado');

IF EXISTS (SELECT 1 FROM [dbo].[actividades_agenda] WHERE [id] = @ActFisica1)
AND NOT EXISTS (SELECT 1 FROM [dbo].[log_notificaciones] WHERE [actividad_agenda_id] = @ActFisica1)
    INSERT INTO [dbo].[log_notificaciones] ([user_id], [actividad_agenda_id], [tipo_notificacion], [estado_envio])
    VALUES (@Est2Id, @ActFisica1, 'email', 'pendiente');

-- -----------------------------------------------------
-- 14. Token consumption
-- -----------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM [dbo].[consumo_tokens] WHERE [user_id] = @Est1Id AND [institucion_id] = @InstitucionId)
BEGIN
    INSERT INTO [dbo].[consumo_tokens] ([institucion_id], [curso_id], [user_id], [tipo_operacion], [prompt_tokens], [completion_tokens], [costo_estimado_usd])
    VALUES 
        (@InstitucionId, @CursoMateId, @Est1Id, 'chat', 150, 200, 0.005),
        (@InstitucionId, @CursoFisicaId, @Est2Id, 'chat', 80, 120, 0.003);
END

PRINT 'Datos académicos simulados insertados correctamente.';
GO

/*
  Datos de ejemplo para el panel de analíticas.
  - Usa únicamente estudiantes inscritos y cursos activos.
  - Crea actividad distribuida durante los últimos 60 días para que se
    puedan mostrar tendencia, participación, continuidad y fuentes RAG.
  - Es idempotente: cada fila se identifica por usuario, curso, fecha y tipo.
*/
SET NOCOUNT ON;

DECLARE @today date = CAST(SYSDATETIME() AS date);

IF OBJECT_ID('tempdb..#analytics_seed') IS NOT NULL DROP TABLE #analytics_seed;

;WITH inscritos AS (
    SELECT
        ec.user_id,
        ec.curso_id,
        c.institucion_id,
        ROW_NUMBER() OVER (PARTITION BY c.institucion_id ORDER BY ec.user_id, ec.curso_id) AS posicion
    FROM dbo.estudiante_cursos ec
    INNER JOIN dbo.cursos c ON c.id = ec.curso_id
    INNER JOIN dbo.users u ON u.id = ec.user_id
    WHERE ec.is_active = 1 AND c.is_active = 1 AND u.is_active = 1
), seleccion AS (
    SELECT * FROM inscritos WHERE posicion <= 10
)
SELECT user_id, curso_id, institucion_id, posicion
INTO #analytics_seed
FROM seleccion;

/* Actividad reciente: cuatro usos por estudiante, repartidos en 28 días. */
INSERT INTO dbo.consumo_tokens
    (id, institucion_id, curso_id, user_id, tipo_operacion, prompt_tokens, completion_tokens, costo_estimado_usd, fecha)
SELECT
    NEWID(), s.institucion_id, s.curso_id, s.user_id,
    CASE v.orden % 3 WHEN 1 THEN 'chat_rag' WHEN 2 THEN 'practicar' ELSE 'resumen_sintetico' END,
    260 + (s.posicion * 17) + (v.orden * 23),
    110 + (s.posicion * 9) + (v.orden * 15),
    CAST((0.00018 + (s.posicion * 0.000011) + (v.orden * 0.000007)) AS decimal(10, 6)),
    DATEADD(hour, 9 + v.orden, DATEADD(day, -((s.posicion * 2 + v.orden * 5) % 28), CAST(@today AS datetime2)))
FROM #analytics_seed s
CROSS JOIN (VALUES (1), (2), (3), (4)) v(orden)
WHERE NOT EXISTS (
    SELECT 1
    FROM dbo.consumo_tokens ct
    WHERE ct.institucion_id = s.institucion_id
      AND ct.curso_id = s.curso_id
      AND ct.user_id = s.user_id
    AND ct.tipo_operacion = CASE v.orden % 3 WHEN 1 THEN 'chat_rag' WHEN 2 THEN 'practicar' ELSE 'resumen_sintetico' END
      AND ct.fecha = DATEADD(hour, 9 + v.orden, DATEADD(day, -((s.posicion * 2 + v.orden * 5) % 28), CAST(@today AS datetime2)))
);

/* Ventana anterior: ocho estudiantes para calcular continuidad sin simular 100 %. */
INSERT INTO dbo.consumo_tokens
    (id, institucion_id, curso_id, user_id, tipo_operacion, prompt_tokens, completion_tokens, costo_estimado_usd, fecha)
SELECT
    NEWID(), s.institucion_id, s.curso_id, s.user_id,
    CASE v.orden WHEN 1 THEN 'chat_rag' ELSE 'practicar' END,
    230 + (s.posicion * 14) + (v.orden * 18),
    95 + (s.posicion * 8) + (v.orden * 12),
    CAST((0.00015 + (s.posicion * 0.000009) + (v.orden * 0.000006)) AS decimal(10, 6)),
    DATEADD(hour, 11 + v.orden, DATEADD(day, -(31 + ((s.posicion * 3 + v.orden * 6) % 26)), CAST(@today AS datetime2)))
FROM #analytics_seed s
CROSS JOIN (VALUES (1), (2)) v(orden)
WHERE s.posicion <= 8
  AND NOT EXISTS (
      SELECT 1
      FROM dbo.consumo_tokens ct
      WHERE ct.institucion_id = s.institucion_id
        AND ct.curso_id = s.curso_id
        AND ct.user_id = s.user_id
        AND ct.tipo_operacion = CASE v.orden WHEN 1 THEN 'chat_rag' ELSE 'practicar' END
        AND ct.fecha = DATEADD(hour, 11 + v.orden, DATEADD(day, -(31 + ((s.posicion * 3 + v.orden * 6) % 26)), CAST(@today AS datetime2)))
  );

/* Dos usuarios que participaron solo en el período anterior, cuando existen,
   permiten que la continuidad no sea artificialmente perfecta. */
;WITH inscritos AS (
    SELECT ec.user_id, ec.curso_id, c.institucion_id,
           ROW_NUMBER() OVER (PARTITION BY c.institucion_id ORDER BY ec.user_id, ec.curso_id) AS posicion
    FROM dbo.estudiante_cursos ec
    INNER JOIN dbo.cursos c ON c.id = ec.curso_id
    INNER JOIN dbo.users u ON u.id = ec.user_id
    WHERE ec.is_active = 1 AND c.is_active = 1 AND u.is_active = 1
)
INSERT INTO dbo.consumo_tokens
    (id, institucion_id, curso_id, user_id, tipo_operacion, prompt_tokens, completion_tokens, costo_estimado_usd, fecha)
SELECT NEWID(), i.institucion_id, i.curso_id, i.user_id, 'chat_rag',
       245 + (i.posicion * 11), 105 + (i.posicion * 7),
       CAST((0.00017 + (i.posicion * 0.000008)) AS decimal(10, 6)),
       DATEADD(hour, 13, DATEADD(day, -(38 + (i.posicion % 12)), CAST(@today AS datetime2)))
FROM inscritos i
WHERE i.posicion BETWEEN 11 AND 12
  AND NOT EXISTS (
      SELECT 1 FROM dbo.consumo_tokens ct
      WHERE ct.institucion_id = i.institucion_id
        AND ct.curso_id = i.curso_id
        AND ct.user_id = i.user_id
        AND ct.tipo_operacion = 'chat_rag'
        AND ct.fecha = DATEADD(hour, 13, DATEADD(day, -(38 + (i.posicion % 12)), CAST(@today AS datetime2)))
  );

/* Conversaciones y respuestas del asistente para medir cobertura con fuentes. */
INSERT INTO dbo.sesiones_chat (id, user_id, curso_id, titulo, is_active, created_at, updated_at)
SELECT NEWID(), s.user_id, s.curso_id, N'Seguimiento de aprendizaje', 1,
       DATEADD(day, -s.posicion, CAST(@today AS datetime2)),
       DATEADD(day, -s.posicion, CAST(@today AS datetime2))
FROM #analytics_seed s
WHERE s.posicion <= 8
  AND NOT EXISTS (
      SELECT 1 FROM dbo.sesiones_chat sc
      WHERE sc.user_id = s.user_id AND sc.curso_id = s.curso_id AND sc.titulo = N'Seguimiento de aprendizaje'
  );

;WITH sesiones_demo AS (
    SELECT sc.id, s.posicion
    FROM dbo.sesiones_chat sc
    INNER JOIN #analytics_seed s ON s.user_id = sc.user_id AND s.curso_id = sc.curso_id
    WHERE sc.titulo = N'Seguimiento de aprendizaje' AND s.posicion <= 8
)
INSERT INTO dbo.mensajes_chat (id, sesion_chat_id, rol, contenido, citas_contexto_json, tipo_interaccion, created_at)
SELECT NEWID(), sd.id, v.rol,
       CASE v.rol WHEN N'user' THEN N'Necesito practicar el tema visto esta semana.' ELSE N'Claro. Revisemos el concepto y avancemos con un ejemplo breve.' END,
       CASE WHEN v.rol = N'assistant' AND sd.posicion % 4 <> 0 THEN N'[{"archivo":"guia-del-curso.pdf","pagina":' + CAST((sd.posicion % 6) + 1 AS nvarchar(10)) + N'}]' ELSE NULL END,
    CASE sd.posicion % 3 WHEN 1 THEN N'consulta' WHEN 2 THEN N'practicar' ELSE N'recurso_sintetico' END,
       DATEADD(hour, v.hora, DATEADD(day, -sd.posicion, CAST(@today AS datetime2)))
FROM sesiones_demo sd
CROSS JOIN (VALUES (N'user', 14), (N'assistant', 15)) v(rol, hora)
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.mensajes_chat mc
    WHERE mc.sesion_chat_id = sd.id
      AND mc.rol = v.rol
      AND mc.created_at = DATEADD(hour, v.hora, DATEADD(day, -sd.posicion, CAST(@today AS datetime2)))
);

DROP TABLE #analytics_seed;