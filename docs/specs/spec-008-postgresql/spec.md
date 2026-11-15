# SPEC-008 — PostgreSQL 18 y configuración de conexión

**Fecha:** 2026-11-14.

**Autorización de alcance:** el responsable solicita sustituir SQL Server por PostgreSQL 18.x y configurar las credenciales por separado. Confirma una base nueva —la anterior ya no existe— y PostgreSQL externo, sin servicio de base de datos en Compose.

## Requisitos

- Utilizar PostgreSQL 18.x mediante SQLAlchemy y psycopg, conservando las interfaces HTTP, roles y separación institucional.
- Sustituir `DATABASE_URL` por `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` y `DB_SSLMODE`. Construir la URL internamente sin concatenar ni exponer credenciales; aceptar caracteres reservados en usuario/contraseña.
- Proporcionar esquema inicial y seed PostgreSQL para las 16 tablas; mantener UUID como strings en la API, enteros autogenerados, fechas UTC y datos de ejemplo opcionales/idempotentes.
- Eliminar la dependencia ODBC de aplicación/imagen y adaptar el soporte de pruebas que depende del dialecto.
- Actualizar ejemplos, configuración local y documentación vigente. Preservar el carácter histórico de Spec-000 y de los resultados anteriores.
- Durante la adaptación inicial no conectar, crear ni escribir en instancias externas. La instalación posterior requiere autorización y credenciales del operador.

## Decisión de pruebas anterior al plan (2026-11-14)

El desarrollador seleccionó: **«Solo verificaciones de configuración y compilación, sin añadir tests»**. No se añaden ni ejecutan suites, integración PostgreSQL ni recorridos de sistema. Se permiten comprobaciones de sintaxis/compilación, construcción de configuración con valores ficticios y coherencia de artefactos, sin red hacia bases ni lectura de credenciales para conectarse.

El soporte existente se adapta por dependencia del cambio; ello no acredita su ejecución ni actualiza los resultados históricos. La instalación real posterior se registra separadamente abajo.

## Exclusiones

No hay migración de datos SQL Server, cambio de proveedor vectorial a pgvector, nuevo contenedor PostgreSQL, nueva funcionalidad académica ni reimplementación de negocio.

## Secuencia de implementación

1. Configuración separada, driver y modelos compatibles con UUID PostgreSQL.
2. Scripts de instalación/seed y adaptación de consultas de mantenimiento del soporte existente.
3. Imagen sin ODBC, ejemplos/archivos locales y documentación vigente.
4. Verificaciones autorizadas y registro de límites reales, sin declarar integración probada.

## Verificación inicial (2026-11-14)

- Compilación de sintaxis de 40 archivos Python y comprobación Pylance de la configuración/fábrica y del preparador local: sin errores de sintaxis.
- Parseo PostgreSQL de ambos scripts, incluidos sus bloques PL/pgSQL, y de tres consultas de metadatos del soporte local: correcto.
- Construcción de la aplicación con valores ficticios y conexiones bloqueadas: 65 rutas registradas, mapeadores configurados y DDL de las 16 tablas ORM compilado para PostgreSQL.
- Configuración: caracteres reservados conservados hasta los parámetros psycopg; dotenv sin interpolación; rechazo explícito de URI heredada, contraseña vacía, puerto y modo SSL inválidos.
- `docker compose config --quiet`, también con la configuración de producción, y `pip check` del entorno backend: correctos.
- 124 enlaces locales de documentación comprobados y `git diff --check`: sin errores.

Estas verificaciones no ejecutan el esquema ni el seed contra un servidor y no prueban permisos, restricciones, idempotencia o flujos HTTP con PostgreSQL real. Tampoco se construyó ni arrancó la imagen Docker. El soporte de pruebas adaptado no se ejecutó y los resultados históricos permanecen sin recertificar.

Los archivos locales conservan el resto de su configuración y usan ahora los campos `DB_*`; la contraseña nueva queda vacía deliberadamente. Antes de arrancar, el operador debe completar las credenciales de su PostgreSQL 18.x externo, crear la base vacía y ejecutar primero el esquema y después el seed.

## Instalación autorizada y conexión real (2026-11-15)

El desarrollador proporcionó las credenciales en el archivo local y autorizó crear la base y cargar registros de prueba. Tras corregir el destino, se comprobó PostgreSQL 18.x y se encontró la base configurada ya creada, sin objetos de aplicación. No fue necesario crear otra base ni se eliminaron datos.

El servidor rechazaba `search_path` en las opciones de inicio. Se retiraron esas opciones de la URL y se fijan UTC y `public` al comenzar cada transacción SQLAlchemy mediante `set_config(..., true)`, también en el preparador local. Esto evita depender del estado de una sesión retenida por un pooler. Se verificaron tres transacciones consecutivas y la sintaxis Python de los cambios.

Se ejecutaron completos y en orden el esquema y el seed, con sus respectivas confirmaciones de transacción. Una conexión nueva confirmó 16 tablas, 14 usuarios (1 administrador, 2 coordinadores y 11 estudiantes), 2 cursos, 22 matrículas, 16 sesiones, 32 mensajes, 2 actividades y 116 registros de consumo de demostración.

Se verificaron los hashes, estado activo y roles de las tres cuentas públicas solicitadas. Mediante el cliente de Flask conectado a la base real, `/readyz` y los tres logins devolvieron HTTP 200; no se imprimieron tokens ni credenciales de infraestructura. Las cuentas y su contraseña de demostración están documentadas en el seed y deben cambiarse antes de exponer la aplicación.

Esta comprobación operativa autorizada no ejecuta las suites existentes, pruebas negativas de permisos/aislamiento, repetición del seed, recorridos UI ni servicios de IA. No recertifica los resultados históricos ni constituye aceptación integral de PostgreSQL. No se construyó ni arrancó la imagen Docker.

## Ampliación del seed y carga desplegada (2026-11-15)

El desarrollador aprobó añadir 12 instituciones, 36 coordinadores, 480 estudiantes y 60 cursos, sin nuevos administradores y con exactamente dos planes adicionales. Autorizó también fallos sintéticos identificables para RAG y notificaciones, sin acciones externas. Se conservan las cuentas y datos iniciales.

Las identidades se inspiran en personajes del estoicismo y la filosofía; sus contactos usan dominios reservados `.test`. Cada institución adicional tiene tres coordinadores, 40 estudiantes, cinco cursos y una suscripción. Cada estudiante se matricula en tres cursos de su propia institución. Se incluyen cuentas desactivadas, una institución inactiva y una suscripción vencida; se respetan cuotas de cuentas y tokens. El historial académico está fechado dentro del periodo de suscripción y el consumo ampliado referencia su tarifa efectiva con snapshot de precios y costo coherentes.

Los cuatro periodos históricos de tarifa son datos sintéticos con los mismos precios de la tarifa vigente, no una afirmación de precios históricos del proveedor. Los trabajos RAG tienen estado `failed`, cero métricas de procesamiento y error `[SIMULACIÓN SEED]`; sus documentos son solo metadatos ficticios. Los logs de notificaciones son `fallido` y se vinculan a actividades marcadas como simulación. No hay archivos, vectores, citas ni envíos reales.

### Estado final verificado

| Tabla | Registros |
|---|---:|
| roles | 3 |
| planes | 3 |
| instituciones | 13 |
| suscripciones | 13 |
| users | 530 |
| user_roles | 530 |
| cursos | 62 |
| configuracion_ia | 62 |
| estudiante_cursos | 1.462 |
| sesiones_chat | 4.336 |
| mensajes_chat | 17.312 |
| actividades_agenda | 482 |
| log_notificaciones | 11.520 |
| precios_modelo_ia | 5 |
| consumo_tokens | 17.396 |
| rag_ingestion_jobs | 120 |

Distribución final de usuarios: **1 administrador, 38 coordinadores y 491 estudiantes**.

### Verificación operativa

1. Ejecución completa en transacción reversible, comprobación de los incrementos exactos aprobados y rollback.
2. Carga confirmada y segunda ejecución confirmada: mismas filas y contenido, sin duplicados ni cambios en registros previos. Una conexión nueva verificó la persistencia.
3. Comprobaciones de relaciones institucionales en matrículas, sesiones, consumo, logs y trabajos; roles pertinentes; límites de cuentas; precios, fechas y costos del consumo; estados y métricas sintéticas. Comprobación adicional de las cuotas mensuales de tokens.
4. Login real mediante el cliente de Flask del administrador original y de `lucio.seneca@portico.test` y `socrates.atenas@portico.test`: HTTP 200. Listados de instituciones, cursos, matrículas y conversaciones, agenda y analíticas: HTTP 200; el estudiante ve tres cursos y nueve conversaciones de su institución.

No se ejecutaron suites existentes, llamadas a proveedores, recorridos de navegador ni pruebas de carga/concurrencia. El volumen permite simular uso, no certifica capacidad de producción. Las secuencias de identidad pueden avanzar por intentos `ON CONFLICT` incluso en rollback; esto no altera las filas ni exige IDs consecutivos.
