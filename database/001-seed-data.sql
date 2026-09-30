/*
  TutorIA — cuentas iniciales y datos académicos de ejemplo.
  Ejecutar después de 001-initial-schema.sql

  Credenciales INICIALES PÚBLICAS (cambiar desde Perfil antes de publicar):
    administracion@demo.com / password
    coordinador@demo.com     / password
    estudiante@demo.com   / password
    Los demás estudiantes usan la misma contraseña académica inicial.
  Solo se almacenan hashes PBKDF2-SHA256 compatibles con Werkzeug.
*/
USE [tutoria-webapp];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;

-- ============================================================
-- Valores iniciales editables (mantener este bloque en un batch).
-- Para una instalación sin ejemplos, poner @CargarEjemplos = 0:
-- se crean administración, roles y tarifa IA, sin datos académicos.
-- ============================================================
DECLARE @CargarEjemplos bit = 1;
DECLARE @AdminEmail nvarchar(255) = N'administracion@demo.com';
DECLARE @AdminNombre nvarchar(100) = N'Sick';
DECLARE @AdminApellido nvarchar(100) = N'Ranchez';
DECLARE @AdminHash nvarchar(255) = N'pbkdf2:sha256:1000000$NEwbQxVlSDJiB6Ud$6e25e19319e695cf7ff2a011fc540b9f133735c55e62297f48e7cdaf70efba46';
DECLARE @AcademicoHash nvarchar(255) = @AdminHash; -- Todas las cuentas iniciales usan password.
DECLARE @InstitucionNombre nvarchar(255) = N'Universidad C-137';
DECLARE @Dominio nvarchar(100) = N'demo.com';
DECLARE @PlanNombre nvarchar(100) = N'Plan Académico Esencial';
DECLARE @MaxCuentas int = 100;
DECLARE @MaxAlmacenamientoGB decimal(5, 2) = 50;
DECLARE @LimiteTokensMensual bigint = 1000000;
DECLARE @DuracionSuscripcionMeses int = 12;
DECLARE @Proveedor nvarchar(50) = N'openai';
DECLARE @Modelo nvarchar(100) = N'gpt-5.4-mini';
-- Revisar contra las tarifas del proveedor antes de operar (USD / millón).
DECLARE @PrecioPrompt decimal(12, 6) = 0.750000;
DECLARE @PrecioCompletion decimal(12, 6) = 2.500000;

-- Correos personales sin sufijos artificiales; rol y orden son internos.
DECLARE @Personas TABLE (
    orden int PRIMARY KEY, nombre nvarchar(100), apellido nvarchar(100),
    correo nvarchar(200) UNIQUE, rol nvarchar(50), user_id uniqueidentifier NULL
);
INSERT INTO @Personas (orden, nombre, apellido, correo, rol) VALUES
    (0, N'Marco', N'Aurelio', N'coordinador.alfa', N'coordinador'),
    (1, N'Ronaldo', N'Dos Santos', N'coordinador.beta', N'coordinador'),
    (2, N'Thomas', N'Shelby', N'estudiante.alfa', N'estudiante'),
    (3, N'Friedrich', N'Nietzsche', N'estudiante.beta', N'estudiante'),
    (4, N'Diego', N'Ramírez', N'diego.ramirez', N'estudiante'),
    (5, N'Sofía', N'Mendoza', N'sofia.mendoza', N'estudiante'),
    (6, N'Mateo', N'Castillo', N'mateo.castillo', N'estudiante'),
    (7, N'Valentina', N'Ruiz', N'valentina.ruiz', N'estudiante'),
    (8, N'Santiago', N'Vega', N'santiago.vega', N'estudiante'),
    (9, N'Isabella', N'Navarro', N'isabella.navarro', N'estudiante'),
    (10, N'Andrés', N'Morales', N'andres.morales', N'estudiante'),
    (11, N'Paula', N'Romero', N'paula.romero', N'estudiante'),
    (12, N'Gabriel', N'Acosta', N'gabriel.acosta', N'estudiante');

DECLARE @Ahora datetime2 = SYSUTCDATETIME();
BEGIN TRY
    BEGIN TRANSACTION;

    INSERT INTO dbo.roles (name)
    SELECT v.nombre FROM (VALUES (N'super_admin'), (N'coordinador'), (N'estudiante')) v(nombre)
    WHERE NOT EXISTS (SELECT 1 FROM dbo.roles r WHERE r.name = v.nombre);

    IF NOT EXISTS (SELECT 1 FROM dbo.users WHERE email = @AdminEmail)
        INSERT INTO dbo.users (email, email_verified, password_hash, first_name, last_name, is_active)
        VALUES (@AdminEmail, 1, @AdminHash, @AdminNombre, @AdminApellido, 1);

    -- Evitar asignar super_admin accidentalmente a una cuenta de institución.
    IF EXISTS (SELECT 1 FROM dbo.users WHERE email = @AdminEmail AND institucion_id IS NOT NULL)
        THROW 50001, N'El correo de administración ya pertenece a una institución. Cambie @AdminEmail.', 1;

    INSERT INTO dbo.user_roles (user_id, role_id)
    SELECT u.id, r.id FROM dbo.users u CROSS JOIN dbo.roles r
    WHERE u.email = @AdminEmail AND r.name = N'super_admin'
      AND NOT EXISTS (SELECT 1 FROM dbo.user_roles ur WHERE ur.user_id = u.id AND ur.role_id = r.id);

    -- La tarifa se requiere también si se comienza sin datos académicos.
    IF NOT EXISTS (SELECT 1 FROM dbo.precios_modelo_ia
                   WHERE proveedor = @Proveedor AND modelo = @Modelo AND is_active = 1 AND vigente_hasta IS NULL)
        INSERT INTO dbo.precios_modelo_ia
            (proveedor, modelo, precio_prompt_por_millon_usd, precio_completion_por_millon_usd, vigente_desde, is_active)
        VALUES (@Proveedor, @Modelo, @PrecioPrompt, @PrecioCompletion, @Ahora, 1);

    IF @CargarEjemplos = 1
    BEGIN
        IF @DuracionSuscripcionMeses <= 0
            THROW 50002, N'La duración de la suscripción debe ser positiva.', 1;

        IF NOT EXISTS (SELECT 1 FROM dbo.planes WHERE nombre = @PlanNombre)
            INSERT INTO dbo.planes (nombre, max_cuentas, max_almacenamiento_gb, is_active)
            VALUES (@PlanNombre, @MaxCuentas, @MaxAlmacenamientoGB, 1);

        IF NOT EXISTS (SELECT 1 FROM dbo.instituciones WHERE nombre = @InstitucionNombre)
            INSERT INTO dbo.instituciones (nombre, dominio_permitido, is_active)
            VALUES (@InstitucionNombre, @Dominio, 1);

        DECLARE @InstitucionId uniqueidentifier;
        IF (SELECT COUNT(*) FROM dbo.instituciones WHERE nombre = @InstitucionNombre) <> 1
            THROW 50003, N'Hay varias instituciones con el nombre inicial. Use un nombre único.', 1;
        SELECT @InstitucionId = id FROM dbo.instituciones WHERE nombre = @InstitucionNombre;

        IF NOT EXISTS (SELECT 1 FROM dbo.suscripciones WHERE institucion_id = @InstitucionId)
            INSERT INTO dbo.suscripciones
                (institucion_id, plan_id, limite_tokens_mensual, fecha_inicio, fecha_fin, is_active)
            SELECT @InstitucionId, id, @LimiteTokensMensual, @Ahora,
                   DATEADD(month, @DuracionSuscripcionMeses, @Ahora), 1
            FROM dbo.planes WHERE nombre = @PlanNombre;

        -- Fecha estable del primer alta: volver a ejecutar no inventa nueva actividad.
        DECLARE @FechaBase date;
        SELECT @FechaBase = CAST(created_at AS date) FROM dbo.instituciones WHERE id = @InstitucionId;

        IF EXISTS (SELECT 1 FROM @Personas p JOIN dbo.users u ON u.email = p.correo + N'@' + @Dominio
                   WHERE u.institucion_id IS NULL OR u.institucion_id <> @InstitucionId)
            THROW 50004, N'Un correo inicial pertenece a otra institución. Revise @Personas y @Dominio.', 1;

        INSERT INTO dbo.users
            (institucion_id, email, email_verified, password_hash, first_name, last_name, is_active)
        SELECT @InstitucionId, p.correo + N'@' + @Dominio, 1, @AcademicoHash, p.nombre, p.apellido, 1
        FROM @Personas p
        WHERE NOT EXISTS (SELECT 1 FROM dbo.users u WHERE u.email = p.correo + N'@' + @Dominio);

        UPDATE p SET user_id = u.id FROM @Personas p
        JOIN dbo.users u ON u.email = p.correo + N'@' + @Dominio AND u.institucion_id = @InstitucionId;

        INSERT INTO dbo.user_roles (user_id, role_id)
        SELECT p.user_id, r.id FROM @Personas p JOIN dbo.roles r ON r.name = p.rol
        WHERE NOT EXISTS (SELECT 1 FROM dbo.user_roles ur WHERE ur.user_id = p.user_id AND ur.role_id = r.id);

        DECLARE @Cursos TABLE (codigo nvarchar(50) PRIMARY KEY, nombre nvarchar(255), descripcion nvarchar(1000));
        INSERT INTO @Cursos VALUES
            (N'MAT-101', N'Matemáticas Básicas', N'Álgebra, funciones y fundamentos de cálculo.'),
            (N'FIS-201', N'Física General', N'Mecánica, leyes de Newton y termodinámica.');

        INSERT INTO dbo.cursos (institucion_id, nombre, codigo, descripcion, is_active)
        SELECT @InstitucionId, c.nombre, c.codigo, c.descripcion, 1 FROM @Cursos c
        WHERE NOT EXISTS (SELECT 1 FROM dbo.cursos actual WHERE actual.institucion_id = @InstitucionId AND actual.codigo = c.codigo);

        INSERT INTO dbo.configuracion_ia (curso_id, system_prompt, temperatura, modos_permitidos, extender_conocimiento)
        SELECT c.id, N'Eres un tutor universitario de ' + c.nombre
               + N'. Explica paso a paso, adapta los ejemplos al estudiante y reconoce cuando no tienes suficiente información.',
               0.3, N'chat,practicar,recursos', 1
        FROM dbo.cursos c JOIN @Cursos inicial ON inicial.codigo = c.codigo
        WHERE c.institucion_id = @InstitucionId
          AND NOT EXISTS (SELECT 1 FROM dbo.configuracion_ia ia WHERE ia.curso_id = c.id);

        INSERT INTO dbo.estudiante_cursos (user_id, curso_id, is_active)
        SELECT p.user_id, c.id, 1 FROM @Personas p CROSS JOIN dbo.cursos c
        JOIN @Cursos inicial ON inicial.codigo = c.codigo
        WHERE p.rol = N'estudiante' AND c.institucion_id = @InstitucionId
          AND NOT EXISTS (SELECT 1 FROM dbo.estudiante_cursos ec WHERE ec.user_id = p.user_id AND ec.curso_id = c.id);

        INSERT INTO dbo.actividades_agenda (titulo, descripcion, tipo, fecha_limite, estado, curso_id)
        SELECT CASE c.codigo WHEN N'MAT-101' THEN N'Ecuaciones cuadráticas y factorización' ELSE N'Informe sobre las leyes de Newton' END,
               CASE c.codigo WHEN N'MAT-101' THEN N'Resolver los ejercicios del capítulo de álgebra y explicar el procedimiento.'
                    ELSE N'Analizar las fuerzas de un sistema y presentar las conclusiones.' END,
               CASE c.codigo WHEN N'MAT-101' THEN N'tarea' ELSE N'proyecto' END,
               DATEADD(day, CASE c.codigo WHEN N'MAT-101' THEN 7 ELSE 14 END, CAST(@FechaBase AS datetime2)), N'vigente', c.id
        FROM dbo.cursos c JOIN @Cursos inicial ON inicial.codigo = c.codigo
        WHERE c.institucion_id = @InstitucionId
          AND NOT EXISTS (SELECT 1 FROM dbo.actividades_agenda a WHERE a.curso_id = c.id
                          AND a.titulo = CASE c.codigo WHEN N'MAT-101' THEN N'Ecuaciones cuadráticas y factorización' ELSE N'Informe sobre las leyes de Newton' END);

        -- Ocho estudiantes con conversaciones; sin citas ni PDFs inexistentes.
        INSERT INTO dbo.sesiones_chat (id, user_id, curso_id, titulo, is_active, created_at, updated_at)
        SELECT NEWID(), p.user_id, c.id,
               CASE c.codigo WHEN N'MAT-101' THEN N'Factorización y ecuaciones' ELSE N'Aplicaciones de las leyes de Newton' END,
               1, DATEADD(day, -p.orden, CAST(@FechaBase AS datetime2)), DATEADD(day, -p.orden, CAST(@FechaBase AS datetime2))
        FROM @Personas p CROSS JOIN dbo.cursos c JOIN @Cursos inicial ON inicial.codigo = c.codigo
        WHERE p.orden BETWEEN 1 AND 8 AND c.institucion_id = @InstitucionId
          AND NOT EXISTS (SELECT 1 FROM dbo.sesiones_chat sc WHERE sc.user_id = p.user_id AND sc.curso_id = c.id
              AND sc.titulo = CASE c.codigo WHEN N'MAT-101' THEN N'Factorización y ecuaciones' ELSE N'Aplicaciones de las leyes de Newton' END);

        INSERT INTO dbo.mensajes_chat (sesion_chat_id, rol, contenido, tipo_interaccion, created_at)
        SELECT sc.id, v.rol,
               CASE WHEN c.codigo = N'MAT-101' AND v.rol = N'user' THEN N'¿Cómo puedo resolver x² - 5x + 6 = 0?'
                    WHEN c.codigo = N'MAT-101' THEN N'Busca dos números cuyo producto sea 6 y cuya suma sea -5. Son -2 y -3, así que (x - 2)(x - 3) = 0. Las soluciones son 2 y 3.'
                    WHEN v.rol = N'user' THEN N'¿Qué aceleración produce una fuerza neta de 12 N sobre una masa de 3 kg?'
                    ELSE N'La segunda ley de Newton indica F = m · a. Entonces a = F / m = 12 / 3 = 4 m/s².' END,
               N'consulta', DATEADD(hour, v.hora, DATEADD(day, -p.orden, CAST(@FechaBase AS datetime2)))
        FROM @Personas p JOIN dbo.sesiones_chat sc ON sc.user_id = p.user_id
        JOIN dbo.cursos c ON c.id = sc.curso_id JOIN @Cursos inicial ON inicial.codigo = c.codigo
        CROSS JOIN (VALUES (N'user', 14), (N'assistant', 15)) v(rol, hora)
        WHERE p.orden BETWEEN 1 AND 8 AND c.institucion_id = @InstitucionId
          AND sc.titulo = CASE c.codigo WHEN N'MAT-101' THEN N'Factorización y ecuaciones' ELSE N'Aplicaciones de las leyes de Newton' END
          AND NOT EXISTS (SELECT 1 FROM dbo.mensajes_chat m WHERE m.sesion_chat_id = sc.id AND m.rol = v.rol);

        -- Diez estudiantes recientes, ocho de ellos también en el período anterior;
        -- dos estudiantes adicionales participaron solo en el período anterior.
        -- El orden es por PERSONA, no por matrícula, para medir continuidad real.
        DECLARE @PrecioId int, @TarifaPrompt decimal(12, 6), @TarifaCompletion decimal(12, 6);
        SELECT @PrecioId = id, @TarifaPrompt = precio_prompt_por_millon_usd,
               @TarifaCompletion = precio_completion_por_millon_usd
        FROM dbo.precios_modelo_ia WHERE proveedor = @Proveedor AND modelo = @Modelo AND is_active = 1 AND vigente_hasta IS NULL;

        ;WITH actividad AS (
            SELECT p.user_id, p.orden, c.id AS curso_id, v.evento,
                   DATEADD(hour, 9 + v.evento,
                       DATEADD(day, CASE WHEN v.evento <= 4 THEN -((p.orden * 2 + v.evento * 5) % 28)
                                         ELSE -(31 + ((p.orden * 3 + v.evento * 6) % 26)) END,
                               CAST(@FechaBase AS datetime2))) AS fecha
            FROM @Personas p CROSS JOIN dbo.cursos c JOIN @Cursos inicial ON inicial.codigo = c.codigo
            CROSS JOIN (VALUES (1), (2), (3), (4), (5), (6)) v(evento)
            WHERE p.rol = N'estudiante' AND c.institucion_id = @InstitucionId
              AND ((v.evento <= 4 AND p.orden <= 10)
                OR (v.evento > 4 AND (p.orden <= 8 OR p.orden >= 11)))
        ), consumo AS (
            SELECT *, CASE evento % 3 WHEN 1 THEN N'chat_rag' WHEN 2 THEN N'practicar' ELSE N'resumen_sintetico' END AS operacion,
                   260 + orden * 17 + evento * 23 AS prompt_tokens,
                   110 + orden * 9 + evento * 15 AS completion_tokens
            FROM actividad
        )
        INSERT INTO dbo.consumo_tokens
            (institucion_id, curso_id, user_id, tipo_operacion, prompt_tokens, completion_tokens,
             costo_estimado_usd, precio_modelo_ia_id, proveedor_modelo, modelo_ia,
             precio_prompt_por_millon_usd, precio_completion_por_millon_usd, fecha)
        SELECT @InstitucionId, s.curso_id, s.user_id, s.operacion, s.prompt_tokens, s.completion_tokens,
               CAST((s.prompt_tokens * @TarifaPrompt + s.completion_tokens * @TarifaCompletion) / 1000000 AS decimal(10, 6)),
               @PrecioId, @Proveedor, @Modelo, @TarifaPrompt, @TarifaCompletion, s.fecha
        FROM consumo s WHERE NOT EXISTS (
            SELECT 1 FROM dbo.consumo_tokens actual WHERE actual.institucion_id = @InstitucionId
              AND actual.curso_id = s.curso_id AND actual.user_id = s.user_id
              AND actual.tipo_operacion = s.operacion AND actual.fecha = s.fecha);
        -- No se simulan notificaciones enviadas ni trabajos de ingestión completados.
    END;

    COMMIT TRANSACTION;
    PRINT N'Cuentas iniciales y datos de TutorIA cargados correctamente.';
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
GO