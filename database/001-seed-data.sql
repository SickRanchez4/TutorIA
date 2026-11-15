/*
  TutorIA - datos iniciales para PostgreSQL 18.x.
  Ejecutar despues de 001-initial-schema.sql sobre la misma base.
  Cuentas publicas de demostracion: administracion@demo.com,
  coordinador.alfa@demo.com, coordinador.beta@demo.com,
  estudiante.alfa@demo.com y estudiante.beta@demo.com; clave: password.
  Cambiar las contrasenas desde Perfil antes de exponer la aplicacion.
  Incluye 12 instituciones ficticias adicionales con dominios .test,
  36 coordinadores y 480 estudiantes inspirados en la filosofia.
  Los fallos RAG y de notificaciones son simulados; no hay acciones externas.
*/
BEGIN;
SET LOCAL search_path TO public;
SET LOCAL TIME ZONE 'UTC';
SELECT pg_advisory_xact_lock(hashtextextended('TutorIA:seed', 0));

DO $seed$
DECLARE
    -- false: solo roles, administracion y tarifa; sin ejemplos academicos.
    v_load_examples boolean := true;
    v_admin_email text := 'administracion@demo.com';
    v_admin_first_name text := 'Sick';
    v_admin_last_name text := 'Ranchez';
    v_password_hash text := 'pbkdf2:sha256:1000000$NEwbQxVlSDJiB6Ud$6e25e19319e695cf7ff2a011fc540b9f133735c55e62297f48e7cdaf70efba46';
    v_institution_name text := 'Universidad C-137';
    v_domain text := 'demo.com';
    v_plan_name text := 'Plan Académico Esencial';
    v_max_accounts integer := 100;
    v_max_storage numeric(5,2) := 50;
    v_token_limit bigint := 1000000;
    v_subscription_months integer := 12;
    v_provider text := 'openai';
    v_model text := 'gpt-5.4-mini';
    v_prompt_price numeric(12,6) := 0.750000;
    v_completion_price numeric(12,6) := 2.500000;
    v_people jsonb := '[
      {"first":"Marco","last":"Aurelio","email":"coordinador.alfa","role":"coordinador"},
      {"first":"Ronaldo","last":"Dos Santos","email":"coordinador.beta","role":"coordinador"},
      {"first":"Thomas","last":"Shelby","email":"estudiante.alfa","role":"estudiante"},
      {"first":"Friedrich","last":"Nietzsche","email":"estudiante.beta","role":"estudiante"},
      {"first":"Diego","last":"Ramírez","email":"diego.ramirez","role":"estudiante"},
      {"first":"Sofía","last":"Mendoza","email":"sofia.mendoza","role":"estudiante"},
      {"first":"Mateo","last":"Castillo","email":"mateo.castillo","role":"estudiante"},
      {"first":"Valentina","last":"Ruiz","email":"valentina.ruiz","role":"estudiante"},
      {"first":"Santiago","last":"Vega","email":"santiago.vega","role":"estudiante"},
      {"first":"Isabella","last":"Navarro","email":"isabella.navarro","role":"estudiante"},
      {"first":"Andrés","last":"Morales","email":"andres.morales","role":"estudiante"},
      {"first":"Paula","last":"Romero","email":"paula.romero","role":"estudiante"},
      {"first":"Gabriel","last":"Acosta","email":"gabriel.acosta","role":"estudiante"}
    ]';
    v_now timestamp := CURRENT_TIMESTAMP AT TIME ZONE 'UTC';
    v_base_date timestamp;
    v_institution_id uuid;
    v_plan_id integer;
    v_user_id uuid;
    v_price_id integer;
    v_person record;
    v_course record;
    v_student record;
    v_email text;
    v_title text;
    v_session_id uuid;
    v_event integer;
    v_when timestamp;
    v_operation text;
    v_prompt_tokens integer;
    v_completion_tokens integer;
    v_schools jsonb := '[
      {"name":"Academia del Pórtico de Atenas","domain":"portico.test"},
      {"name":"Liceo Aristotélico de Estagira","domain":"liceo.test"},
      {"name":"Instituto Hipatia de Alejandría","domain":"hipatia.test"},
      {"name":"Universidad del Jardín de Samos","domain":"jardin.test"},
      {"name":"Escuela Cínica de Sinope","domain":"sinope.test"},
      {"name":"Colegio Filosófico de Cirene","domain":"cirene.test"},
      {"name":"Academia Neoplatónica de Licópolis","domain":"neoplatonica.test"},
      {"name":"Instituto Humanista de Hipona","domain":"hipona.test"},
      {"name":"Universidad Crítica de Königsberg","domain":"konigsberg.test"},
      {"name":"Escuela Racionalista de Ámsterdam","domain":"racionalista.test"},
      {"name":"Centro Existencial de Copenhague","domain":"copenhague.test"},
      {"name":"Instituto de Filosofía de Friburgo","domain":"friburgo.test"}
    ]';
    v_philosophers jsonb := '[
      ["Lucio Anneo","Séneca","lucio.seneca"],
      ["Marco","Aurelio","marco.aurelio"],
      ["Epicteto","de Hierápolis","epicteto.hierapolis"],
      ["Sócrates","de Atenas","socrates.atenas"],
      ["Platón","de Atenas","platon.atenas"],
      ["Aristóteles","de Estagira","aristoteles.estagira"],
      ["Zenón","de Citio","zenon.citio"],
      ["Cleantes","de Asos","cleantes.asos"],
      ["Crisipo","de Solos","crisipo.solos"],
      ["Musonio","Rufo","musonio.rufo"],
      ["Hierocles","de Alejandría","hierocles.alejandria"],
      ["Hipatia","de Alejandría","hipatia.alejandria"],
      ["Epicuro","de Samos","epicuro.samos"],
      ["Diógenes","de Sinope","diogenes.sinope"],
      ["Antístenes","de Atenas","antistenes.atenas"],
      ["Pirrón","de Élide","pirron.elide"],
      ["Sexto","Empírico","sexto.empirico"],
      ["Plotino","de Licópolis","plotino.licopolis"],
      ["Porfirio","de Tiro","porfirio.tiro"],
      ["Proclo","de Constantinopla","proclo.constantinopla"],
      ["Agustín","de Hipona","agustin.hipona"],
      ["Anicio Manlio","Boecio","anicio.boecio"],
      ["Tomás","de Aquino","tomas.aquino"],
      ["Guillermo","de Ockham","guillermo.ockham"],
      ["René","Descartes","rene.descartes"],
      ["Baruch","Spinoza","baruch.spinoza"],
      ["John","Locke","john.locke"],
      ["David","Hume","david.hume"],
      ["Immanuel","Kant","immanuel.kant"],
      ["Georg Wilhelm","Hegel","georg.hegel"],
      ["Arthur","Schopenhauer","arthur.schopenhauer"],
      ["Friedrich","Nietzsche","friedrich.nietzsche"],
      ["Søren","Kierkegaard","soren.kierkegaard"],
      ["Simone","Weil","simone.weil"],
      ["Hannah","Arendt","hannah.arendt"],
      ["Simone","de Beauvoir","simone.beauvoir"],
      ["Edith","Stein","edith.stein"],
      ["María","Zambrano","maria.zambrano"],
      ["José","Ortega y Gasset","jose.ortega"],
      ["Bertrand","Russell","bertrand.russell"],
      ["Ludwig","Wittgenstein","ludwig.wittgenstein"],
      ["Emmanuel","Lévinas","emmanuel.levinas"],
      ["Max","Scheler","max.scheler"]
    ]';
    v_school record;
    v_catalog record;
    v_activity record;
    v_course_id integer;
    v_session_index integer;
    v_session_time timestamp;
    v_role text;
    v_price_started_at timestamp;
    v_history_start timestamp;
    v_history_end timestamp;
    v_subscription_end timestamp;
    v_school_created_at timestamp;
BEGIN
    IF current_setting('server_version_num')::integer NOT BETWEEN 180000 AND 189999 THEN
        RAISE EXCEPTION 'Se requiere PostgreSQL 18.x.';
    END IF;
    INSERT INTO roles (name) VALUES ('super_admin'), ('coordinador'), ('estudiante')
    ON CONFLICT (name) DO NOTHING;

    IF EXISTS (SELECT 1 FROM users WHERE email = v_admin_email AND institucion_id IS NOT NULL) THEN
        RAISE EXCEPTION 'El correo de administracion pertenece a una institucion. Cambie v_admin_email.';
    END IF;
    INSERT INTO users (email, email_verified, password_hash, first_name, last_name)
    VALUES (v_admin_email, true, v_password_hash, v_admin_first_name, v_admin_last_name)
    ON CONFLICT (email) DO NOTHING;
    INSERT INTO user_roles (user_id, role_id)
    SELECT u.id, r.id FROM users u CROSS JOIN roles r
    WHERE u.email = v_admin_email AND r.name = 'super_admin'
    ON CONFLICT DO NOTHING;

    INSERT INTO precios_modelo_ia
        (proveedor, modelo, precio_prompt_por_millon_usd, precio_completion_por_millon_usd, vigente_desde)
    SELECT v_provider, v_model, v_prompt_price, v_completion_price, v_now
    WHERE NOT EXISTS (SELECT 1 FROM precios_modelo_ia
        WHERE proveedor = v_provider AND modelo = v_model AND is_active AND vigente_hasta IS NULL);

    IF NOT v_load_examples THEN
        RETURN;
    END IF;
    IF v_subscription_months <= 0 THEN
        RAISE EXCEPTION 'La duracion de la suscripcion debe ser positiva.';
    END IF;
    INSERT INTO planes (nombre, max_cuentas, max_almacenamiento_gb)
    VALUES (v_plan_name, v_max_accounts, v_max_storage)
    ON CONFLICT (nombre) DO NOTHING;
    SELECT id INTO STRICT v_plan_id FROM planes WHERE nombre = v_plan_name;

    IF NOT EXISTS (SELECT 1 FROM instituciones WHERE nombre = v_institution_name) THEN
        INSERT INTO instituciones (nombre, dominio_permitido) VALUES (v_institution_name, v_domain);
    END IF;
    SELECT id, date_trunc('day', created_at) INTO STRICT v_institution_id, v_base_date
    FROM instituciones WHERE nombre = v_institution_name;
    INSERT INTO suscripciones (institucion_id, plan_id, limite_tokens_mensual, fecha_inicio, fecha_fin)
    VALUES (v_institution_id, v_plan_id, v_token_limit, v_now,
        v_now + make_interval(months => v_subscription_months))
    ON CONFLICT (institucion_id) DO NOTHING;

    FOR v_person IN SELECT * FROM jsonb_to_recordset(v_people)
        AS p(first text, last text, email text, role text)
    LOOP
        v_email := v_person.email || '@' || v_domain;
        IF EXISTS (SELECT 1 FROM users WHERE email = v_email
            AND institucion_id IS DISTINCT FROM v_institution_id) THEN
            RAISE EXCEPTION 'Un correo de ejemplo pertenece a otra institucion. Revise v_people y v_domain.';
        END IF;
        INSERT INTO users (institucion_id, email, email_verified, password_hash, first_name, last_name)
        VALUES (v_institution_id, v_email, true, v_password_hash, v_person.first, v_person.last)
        ON CONFLICT (email) DO NOTHING;
        SELECT id INTO STRICT v_user_id FROM users WHERE email = v_email;
        INSERT INTO user_roles (user_id, role_id)
        SELECT v_user_id, id FROM roles WHERE name = v_person.role
        ON CONFLICT DO NOTHING;
    END LOOP;

    INSERT INTO cursos (institucion_id, nombre, codigo, descripcion)
    SELECT v_institution_id, c.nombre, c.codigo, c.descripcion
    FROM (VALUES
        ('MAT-101', 'Matemáticas Básicas', 'Álgebra, funciones y fundamentos de cálculo.'),
        ('FIS-201', 'Física General', 'Mecánica, leyes de Newton y termodinámica.')
    ) AS c(codigo, nombre, descripcion)
    WHERE NOT EXISTS (SELECT 1 FROM cursos actual
        WHERE actual.institucion_id = v_institution_id AND actual.codigo = c.codigo);

    SELECT id, precio_prompt_por_millon_usd, precio_completion_por_millon_usd
    INTO STRICT v_price_id, v_prompt_price, v_completion_price FROM precios_modelo_ia
    WHERE proveedor = v_provider AND modelo = v_model AND is_active AND vigente_hasta IS NULL;

    FOR v_course IN SELECT * FROM cursos
        WHERE institucion_id = v_institution_id AND codigo IN ('MAT-101', 'FIS-201')
    LOOP
        INSERT INTO configuracion_ia (curso_id, system_prompt, temperatura, extender_conocimiento)
        VALUES (v_course.id, 'Eres un tutor universitario de ' || v_course.nombre
            || '. Explica paso a paso, adapta los ejemplos al estudiante y reconoce cuando no tienes suficiente información.',
            0.3, true)
        ON CONFLICT (curso_id) DO NOTHING;
        v_title := CASE v_course.codigo WHEN 'MAT-101'
            THEN 'Ecuaciones cuadráticas y factorización' ELSE 'Informe sobre las leyes de Newton' END;
        INSERT INTO actividades_agenda (curso_id, titulo, descripcion, tipo, fecha_limite)
        SELECT v_course.id, v_title,
            CASE v_course.codigo WHEN 'MAT-101' THEN 'Resolver los ejercicios del capítulo de álgebra.'
                ELSE 'Analizar las fuerzas de un sistema y presentar las conclusiones.' END,
            CASE v_course.codigo WHEN 'MAT-101' THEN 'tarea' ELSE 'proyecto' END,
            v_base_date + make_interval(days => CASE v_course.codigo WHEN 'MAT-101' THEN 7 ELSE 14 END)
        WHERE NOT EXISTS (SELECT 1 FROM actividades_agenda
            WHERE curso_id = v_course.id AND titulo = v_title);

        FOR v_student IN SELECT item.person->>'email' AS email,
                row_number() OVER (ORDER BY item.position)::integer AS ordinal
            FROM jsonb_array_elements(v_people) WITH ORDINALITY AS item(person, position)
            WHERE item.person->>'role' = 'estudiante'
        LOOP
            SELECT id INTO STRICT v_user_id FROM users WHERE email = v_student.email || '@' || v_domain;
            INSERT INTO estudiante_cursos (user_id, curso_id) VALUES (v_user_id, v_course.id)
            ON CONFLICT (user_id, curso_id) DO NOTHING;

            IF v_student.ordinal <= 8 THEN
                v_title := CASE v_course.codigo WHEN 'MAT-101'
                    THEN 'Factorización y ecuaciones' ELSE 'Aplicaciones de las leyes de Newton' END;
                SELECT id INTO v_session_id FROM sesiones_chat
                WHERE user_id = v_user_id AND curso_id = v_course.id AND titulo = v_title LIMIT 1;
                IF v_session_id IS NULL THEN
                    INSERT INTO sesiones_chat (user_id, curso_id, titulo, created_at, updated_at)
                    VALUES (v_user_id, v_course.id, v_title,
                        v_base_date - make_interval(days => v_student.ordinal),
                        v_base_date - make_interval(days => v_student.ordinal))
                    RETURNING id INTO v_session_id;
                END IF;
                INSERT INTO mensajes_chat (sesion_chat_id, rol, contenido, created_at)
                SELECT v_session_id, m.rol,
                    CASE WHEN v_course.codigo = 'MAT-101' AND m.rol = 'user' THEN '¿Cómo puedo resolver x² - 5x + 6 = 0?'
                        WHEN v_course.codigo = 'MAT-101' THEN 'Factoriza como (x - 2)(x - 3) = 0. Las soluciones son 2 y 3.'
                        WHEN m.rol = 'user' THEN '¿Qué aceleración produce una fuerza de 12 N sobre una masa de 3 kg?'
                        ELSE 'La segunda ley de Newton indica a = F / m = 12 / 3 = 4 m/s².' END,
                    v_base_date - make_interval(days => v_student.ordinal) + make_interval(hours => m.hour)
                FROM (VALUES ('user', 14), ('assistant', 15)) AS m(rol, hour)
                WHERE NOT EXISTS (SELECT 1 FROM mensajes_chat
                    WHERE sesion_chat_id = v_session_id AND rol = m.rol);
            END IF;

            FOR v_event IN 1..6 LOOP
                IF (v_event <= 4 AND v_student.ordinal <= 10)
                    OR (v_event > 4 AND (v_student.ordinal <= 8 OR v_student.ordinal >= 11)) THEN
                    v_when := v_base_date + make_interval(hours => 9 + v_event)
                        - make_interval(days => CASE WHEN v_event <= 4
                            THEN (v_student.ordinal * 2 + v_event * 5) % 28
                            ELSE 31 + (v_student.ordinal * 3 + v_event * 6) % 26 END);
                    v_operation := CASE v_event % 3 WHEN 1 THEN 'chat_rag'
                        WHEN 2 THEN 'practicar' ELSE 'resumen_sintetico' END;
                    v_prompt_tokens := 260 + v_student.ordinal * 17 + v_event * 23;
                    v_completion_tokens := 110 + v_student.ordinal * 9 + v_event * 15;
                    INSERT INTO consumo_tokens
                        (institucion_id, curso_id, user_id, tipo_operacion, prompt_tokens, completion_tokens,
                         costo_estimado_usd, precio_modelo_ia_id, proveedor_modelo, modelo_ia,
                         precio_prompt_por_millon_usd, precio_completion_por_millon_usd, fecha)
                    SELECT v_institution_id, v_course.id, v_user_id, v_operation, v_prompt_tokens, v_completion_tokens,
                        (v_prompt_tokens * v_prompt_price + v_completion_tokens * v_completion_price) / 1000000,
                        v_price_id, v_provider, v_model, v_prompt_price, v_completion_price, v_when
                    WHERE NOT EXISTS (SELECT 1 FROM consumo_tokens
                        WHERE institucion_id = v_institution_id AND curso_id = v_course.id AND user_id = v_user_id
                            AND tipo_operacion = v_operation AND fecha = v_when);
                END IF;
            END LOOP;
        END LOOP;
    END LOOP;
    INSERT INTO planes (nombre, max_cuentas, max_almacenamiento_gb)
    VALUES ('Plan Académico Integral', 300, 150), ('Plan Institucional Avanzado', 1000, 500)
    ON CONFLICT (nombre) DO NOTHING;

    SELECT vigente_desde INTO STRICT v_price_started_at
    FROM precios_modelo_ia WHERE id = v_price_id;
    -- Versiones historicas sinteticas: mismas tarifas, sin alterar la vigente.
    FOR v_event IN REVERSE 4..1 LOOP
        v_history_start := v_price_started_at - make_interval(days => v_event * 30);
        v_history_end := v_price_started_at - make_interval(days => (v_event - 1) * 30);
        INSERT INTO precios_modelo_ia
            (proveedor, modelo, precio_prompt_por_millon_usd, precio_completion_por_millon_usd,
             vigente_desde, vigente_hasta, is_active)
        SELECT v_provider, v_model, v_prompt_price, v_completion_price,
            v_history_start, v_history_end, false
        WHERE NOT EXISTS (SELECT 1 FROM precios_modelo_ia p
            WHERE p.proveedor = v_provider AND p.modelo = v_model
                AND p.vigente_desde < v_history_end
                AND (p.vigente_hasta IS NULL OR p.vigente_hasta > v_history_start));
    END LOOP;

    FOR v_school IN SELECT item.value->>'name' AS name, item.value->>'domain' AS domain,
            item.position::integer AS ordinal
        FROM jsonb_array_elements(v_schools) WITH ORDINALITY AS item(value, position)
    LOOP
        IF EXISTS (SELECT 1 FROM instituciones
            WHERE (nombre = v_school.name AND dominio_permitido IS DISTINCT FROM v_school.domain)
                OR (dominio_permitido = v_school.domain AND nombre <> v_school.name)) THEN
            RAISE EXCEPTION 'Conflicto de identidad de una institucion de simulacion; no se modifican datos existentes.';
        END IF;
        v_school_created_at := v_base_date - make_interval(days => 180 - v_school.ordinal * 2);
        INSERT INTO instituciones (nombre, dominio_permitido, is_active, created_at, updated_at)
        SELECT v_school.name, v_school.domain, v_school.ordinal <> 12,
            v_school_created_at, v_school_created_at
        WHERE NOT EXISTS (SELECT 1 FROM instituciones WHERE dominio_permitido = v_school.domain);
        SELECT id INTO STRICT v_institution_id FROM instituciones
        WHERE dominio_permitido = v_school.domain AND nombre = v_school.name;

        SELECT id INTO STRICT v_plan_id FROM planes
        WHERE nombre = CASE v_school.ordinal % 3
            WHEN 1 THEN v_plan_name WHEN 2 THEN 'Plan Académico Integral'
            ELSE 'Plan Institucional Avanzado' END;
        v_subscription_end := CASE WHEN v_school.ordinal = 11
            THEN v_base_date - INTERVAL '7 days' ELSE v_base_date + INTERVAL '180 days' END;
        INSERT INTO suscripciones
            (institucion_id, plan_id, limite_tokens_mensual, fecha_inicio, fecha_fin,
             is_active, created_at, updated_at)
        VALUES (v_institution_id, v_plan_id, 1000000 + v_school.ordinal * 250000,
            v_school_created_at, v_subscription_end, v_school.ordinal <> 12,
            v_school_created_at, v_school_created_at)
        ON CONFLICT (institucion_id) DO NOTHING;

        FOR v_person IN SELECT p.value->>0 AS first_name, p.value->>1 AS last_name,
                p.value->>2 AS email, p.position::integer AS ordinal
            FROM jsonb_array_elements(v_philosophers) WITH ORDINALITY AS p(value, position)
        LOOP
            v_email := v_person.email || '@' || v_school.domain;
            v_role := CASE WHEN v_person.ordinal <= 3 THEN 'coordinador' ELSE 'estudiante' END;
            IF EXISTS (SELECT 1 FROM users WHERE email = v_email
                AND institucion_id IS DISTINCT FROM v_institution_id) THEN
                RAISE EXCEPTION 'Un correo de simulacion pertenece a otra institucion; operacion cancelada.';
            END IF;
            INSERT INTO users
                (institucion_id, email, email_verified, password_hash, first_name, last_name,
                 is_active, created_at, updated_at)
            VALUES (v_institution_id, v_email, true, v_password_hash,
                v_person.first_name, v_person.last_name, v_person.ordinal <= 39,
                v_school_created_at + INTERVAL '7 days', v_school_created_at + INTERVAL '7 days')
            ON CONFLICT (email) DO NOTHING;
            SELECT id INTO STRICT v_user_id FROM users WHERE email = v_email;
            IF EXISTS (SELECT 1 FROM user_roles ur JOIN roles r ON r.id = ur.role_id
                WHERE ur.user_id = v_user_id AND r.name <> v_role) THEN
                RAISE EXCEPTION 'Un usuario de simulacion tiene otro rol; no se sobrescribe ni se amplian permisos.';
            END IF;
            INSERT INTO user_roles (user_id, role_id)
            SELECT v_user_id, id FROM roles WHERE name = v_role
            ON CONFLICT DO NOTHING;
        END LOOP;

        IF EXISTS (SELECT 1 FROM suscripciones s JOIN planes p ON p.id = s.plan_id
            WHERE s.institucion_id = v_institution_id AND p.max_cuentas IS NOT NULL
                AND (SELECT count(*) FROM users u
                    WHERE u.institucion_id = v_institution_id AND u.is_active) > p.max_cuentas) THEN
            RAISE EXCEPTION 'Los usuarios de simulacion superan el limite de cuentas del plan.';
        END IF;

        FOR v_catalog IN SELECT * FROM (VALUES
            (1, 'ETI-101', 'Ética y vida buena',
             '¿Cómo se distingue lo que depende de nosotros de lo que no controlamos?',
             'Podemos deliberar sobre nuestros juicios y acciones, pero no garantizar todos los resultados externos. Conviene evaluar la decisión por sus razones y consecuencias previsibles.',
             'Al preparar un examen puedes organizar el estudio y pedir ayuda; no puedes decidir qué preguntas aparecerán. Justifica qué acciones sí están a tu alcance.'),
            (2, 'LOG-201', 'Lógica y argumentación',
             '¿Una conclusión verdadera basta para que un argumento sea válido?',
             'No. La validez exige que sea imposible tener premisas verdaderas y conclusión falsa. Debemos examinar la relación entre premisas y conclusión, no solo el resultado.',
             'Que una calle esté mojada no demuestra que haya llovido: también pudo regarse. Identifica la afirmación del consecuente y propone una explicación alternativa.'),
            (3, 'EPI-301', 'Epistemología y método',
             '¿Qué diferencia existe entre sostener una opinión y justificar una creencia?',
             'Una opinión puede carecer de razones explícitas. Justificar una creencia requiere presentar evidencia pertinente, examinar objeciones y reconocer los límites de la conclusión.',
             'Compara un rumor con un informe que describe su método y sus datos. Explica qué evidencia adicional pedirías antes de aceptar sus conclusiones.'),
            (4, 'HIS-210', 'Historia de la filosofía',
             '¿Qué comparten el estoicismo y el epicureísmo y en qué se diferencian?',
             'Ambas escuelas reflexionan sobre cómo vivir y reducir perturbaciones. El estoicismo sitúa la virtud en el centro; el epicureísmo destaca el placer estable y la ausencia de dolor.',
             'Contrasta cómo interpretarían ambas escuelas una pérdida material. Evita reducir el estoicismo a insensibilidad o el epicureísmo a consumo sin límites.'),
            (5, 'POL-220', 'Filosofía política y ciudadanía',
             '¿Por qué conviene distinguir entre legalidad y legitimidad?',
             'La legalidad se refiere a la conformidad con normas vigentes; la legitimidad pregunta por la justificación de la autoridad y de esas normas. Pueden coincidir, pero no son equivalentes.',
             'Analiza una norma aprobada formalmente que excluye a parte de la población. Distingue su procedimiento de aprobación de los argumentos sobre su justicia.')
        ) AS c(ordinal, code, name, question, answer, example)
        LOOP
            INSERT INTO cursos (institucion_id, nombre, codigo, descripcion)
            VALUES (v_institution_id, v_catalog.name, v_catalog.code,
                '[SIMULACIÓN SEED] Seminario universitario con lecturas críticas, debates y evaluación argumentada.')
            ON CONFLICT (institucion_id, codigo) WHERE codigo IS NOT NULL DO NOTHING;
            SELECT id INTO STRICT v_course_id FROM cursos
            WHERE institucion_id = v_institution_id AND codigo = v_catalog.code;
            INSERT INTO configuracion_ia
                (curso_id, system_prompt, temperatura, modos_permitidos, extender_conocimiento, updated_at)
            VALUES (v_course_id, 'Eres un tutor de ' || v_catalog.name
                || '. Pide razones, contrasta objeciones y distingue hechos de interpretaciones. '
                || 'No inventes citas ni fuentes; no hay materiales RAG reales en esta simulación.',
                0.2 + v_catalog.ordinal * 0.05, 'chat,practicar,recursos', false,
                v_base_date - INTERVAL '100 days')
            ON CONFLICT (curso_id) DO NOTHING;

            FOR v_event IN 1..8 LOOP
                v_title := (ARRAY['Diagnóstico', 'Seminario', 'Ensayo', 'Evaluación',
                    'Taller', 'Coloquio', 'Proyecto', 'Síntesis final'])[v_event] || ': ' || v_catalog.name;
                v_when := v_base_date + make_interval(
                    days => (ARRAY[-60, -35, -14, -3, 3, 7, 14, 28])[v_event], hours => 18);
                INSERT INTO actividades_agenda
                    (curso_id, titulo, descripcion, tipo, fecha_limite, estado, created_at)
                SELECT v_course_id, v_title,
                    '[SIMULACIÓN SEED] Actividad académica ficticia para practicar análisis y argumentación. '
                    || 'Sus registros de notificación son fallos simulados; no se enviaron mensajes.',
                    (ARRAY['tarea', 'tarea', 'tarea', 'examen', 'tarea', 'tarea', 'proyecto', 'examen'])[v_event],
                    v_when, 'vigente', v_base_date - INTERVAL '95 days'
                WHERE NOT EXISTS (SELECT 1 FROM actividades_agenda
                    WHERE curso_id = v_course_id AND titulo = v_title);
            END LOOP;

            FOR v_student IN SELECT u.id, u.is_active, (p.position - 3)::integer AS ordinal
                FROM jsonb_array_elements(v_philosophers) WITH ORDINALITY AS p(value, position)
                JOIN users u ON u.email = (p.value->>2) || '@' || v_school.domain
                    AND u.institucion_id = v_institution_id
                WHERE p.position > 3 AND (p.position - 3 + v_catalog.ordinal) % 5 < 3
            LOOP
                INSERT INTO estudiante_cursos (user_id, curso_id, is_active, fecha_inscripcion)
                VALUES (v_student.id, v_course_id, v_student.is_active,
                    v_base_date - make_interval(days => 120 - v_student.ordinal % 17))
                ON CONFLICT (user_id, curso_id) DO NOTHING;

                FOR v_session_index IN 1..3 LOOP
                    v_title := v_catalog.name || ': ' || (ARRAY[
                        'Comprensión de conceptos', 'Práctica razonada', 'Repaso crítico'])[v_session_index];
                    v_session_time := v_base_date
                        - make_interval(days => (4 - v_session_index) * 21 - v_student.ordinal % 9)
                        + INTERVAL '10 hours';
                    SELECT id INTO v_session_id FROM sesiones_chat
                    WHERE user_id = v_student.id AND curso_id = v_course_id
                        AND titulo = v_title AND created_at = v_session_time LIMIT 1;
                    IF v_session_id IS NULL THEN
                        INSERT INTO sesiones_chat
                            (user_id, curso_id, titulo, is_active, created_at, updated_at)
                        VALUES (v_student.id, v_course_id, v_title, v_student.is_active,
                            v_session_time, v_session_time + INTERVAL '4 minutes')
                        RETURNING id INTO v_session_id;
                    END IF;
                    INSERT INTO mensajes_chat
                        (sesion_chat_id, rol, contenido, tipo_interaccion, created_at)
                    SELECT v_session_id, m.rol,
                        CASE m.ordinal WHEN 1 THEN v_catalog.question
                            WHEN 2 THEN '[SIMULACIÓN SEED] ' || v_catalog.answer
                            WHEN 3 THEN 'Propón un ejemplo aplicado y una pregunta para comprobar mi comprensión.'
                            ELSE '[SIMULACIÓN SEED] ' || v_catalog.example END,
                        (ARRAY['consulta', 'practicar', 'recurso_sintetico'])[v_session_index],
                        v_session_time + make_interval(mins => m.ordinal)
                    FROM (VALUES (1, 'user'), (2, 'assistant'), (3, 'user'), (4, 'assistant')) AS m(ordinal, rol)
                    WHERE NOT EXISTS (SELECT 1 FROM mensajes_chat
                        WHERE sesion_chat_id = v_session_id
                            AND created_at = v_session_time + make_interval(mins => m.ordinal));
                END LOOP;

                FOR v_event IN 1..12 LOOP
                    v_when := v_base_date - make_interval(
                        days => CASE WHEN v_school.ordinal = 11 THEN 8 ELSE 1 END
                            + (v_student.ordinal * 3 + v_event * 7) % 89)
                        + make_interval(hours => 9 + v_event % 8);
                    v_operation := (ARRAY['chat_rag', 'practicar', 'resumen_sintetico'])[1 + v_event % 3];
                    v_prompt_tokens := 400 + v_student.ordinal * 19 + v_event * 31;
                    v_completion_tokens := 180 + v_student.ordinal * 11 + v_event * 17;
                    SELECT id, precio_prompt_por_millon_usd, precio_completion_por_millon_usd
                    INTO STRICT v_price_id, v_prompt_price, v_completion_price FROM precios_modelo_ia
                    WHERE proveedor = v_provider AND modelo = v_model AND vigente_desde <= v_when
                        AND (vigente_hasta IS NULL OR vigente_hasta > v_when);
                    INSERT INTO consumo_tokens
                        (institucion_id, curso_id, user_id, tipo_operacion, prompt_tokens, completion_tokens,
                         costo_estimado_usd, precio_modelo_ia_id, proveedor_modelo, modelo_ia,
                         precio_prompt_por_millon_usd, precio_completion_por_millon_usd, fecha)
                    SELECT v_institution_id, v_course_id, v_student.id, v_operation,
                        v_prompt_tokens, v_completion_tokens,
                        (v_prompt_tokens * v_prompt_price + v_completion_tokens * v_completion_price) / 1000000,
                        v_price_id, v_provider, v_model, v_prompt_price, v_completion_price, v_when
                    WHERE NOT EXISTS (SELECT 1 FROM consumo_tokens
                        WHERE institucion_id = v_institution_id AND curso_id = v_course_id
                            AND user_id = v_student.id AND tipo_operacion = v_operation AND fecha = v_when);
                END LOOP;

                FOR v_activity IN SELECT id, fecha_limite FROM actividades_agenda
                    WHERE curso_id = v_course_id AND descripcion LIKE '[SIMULACIÓN SEED]%'
                        AND fecha_limite < v_base_date
                LOOP
                    INSERT INTO log_notificaciones
                        (user_id, actividad_agenda_id, tipo_notificacion, estado_envio, fecha_ejecucion)
                    SELECT v_student.id, v_activity.id, n.tipo, 'fallido',
                        v_activity.fecha_limite - n.anticipacion
                    FROM (VALUES ('recordatorio_7_dias', INTERVAL '7 days'),
                        ('alerta_24_horas', INTERVAL '24 hours')) AS n(tipo, anticipacion)
                    WHERE NOT EXISTS (SELECT 1 FROM log_notificaciones
                        WHERE user_id = v_student.id AND actividad_agenda_id = v_activity.id
                            AND tipo_notificacion = n.tipo);
                END LOOP;
            END LOOP;

            FOR v_event IN 1..2 LOOP
                SELECT id INTO STRICT v_user_id FROM users
                WHERE email = (v_philosophers->(v_event - 1)->>2) || '@' || v_school.domain;
                v_title := '[SIMULACIÓN SEED] Fallo de lote ' || v_event
                    || ': no existen archivos físicos ni vectores; subir PDFs reales para una nueva ingestión.';
                INSERT INTO rag_ingestion_jobs
                    (institucion_id, curso_id, coordinador_id, estado, intento, documentos_json,
                     chunks_indexados, archivos_procesados, error_message, created_at, updated_at)
                SELECT v_institution_id, v_course_id, v_user_id, 'failed', v_event,
                    jsonb_build_array(jsonb_build_object(
                        'archivo', 'simulacion_' || lower(v_catalog.code) || '_' || v_event || '.pdf',
                        'tamano_bytes', 1024))::text,
                    0, 0, v_title, v_base_date - make_interval(days => 20 + v_event),
                    v_base_date - make_interval(days => 20 + v_event) + INTERVAL '2 minutes'
                WHERE NOT EXISTS (SELECT 1 FROM rag_ingestion_jobs
                    WHERE curso_id = v_course_id AND error_message = v_title);
            END LOOP;
        END LOOP;
    END LOOP;
END;
$seed$;

COMMIT;
