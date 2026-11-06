# Plan de SPEC-001 — Pruebas esenciales de TutorIA

**Estado:** aprobado.  
**Fecha:** 2026-09-30.  
**Referencia:** [spec.md](spec.md), aprobada.  
**Gobernanza:** [Constitución](../constitution.md).  
**Baseline:** [Spec-000](../spec-000-mvp/Spec-000-mvp.md).

Este plan no implementa código ni declara ejecutadas las pruebas. Define la construcción del proyecto independiente de pruebas y la evaluación de tres algoritmos. No incluye cambios de producto, migraciones, pruebas de tokens ni certificación del MVP completo.

## 1. Estructura de módulos

**Cubre:** RF-1, RF-2, RF-7, RF-8, RF-10 y RF-11; RNF-1, RNF-2, RNF-4 y RNF-6.

Se propone un proyecto `testing/` en la raíz, hermano de los proyectos de aplicación. Los nombres siguientes son artefactos previstos, no archivos creados en esta fase.

| Artefacto previsto | Responsabilidad | RF |
|---|---|---|
| `testing/README.md` | Preparación del entorno propio, ejecución aislada, integración optativa, limpieza y referencia a la documentación de cada spec | RF-1, RF-8, RF-10, RF-11 |
| `testing/requirements.txt` | Referencia a las dependencias existentes del backend, sin cambiar su listado ni incorporar un framework de tests | RF-1, RF-8 |
| `testing/run_tests.py` | Entrada mínima: selección explícita de pruebas aisladas o integración, comprobación del destino, confirmación, ejecución con unittest y código de salida | RF-1, RF-8, RF-10 |
| `testing/support.py` | Importación controlada del backend, contexto Flask, datos ficticios, registro de propiedad y limpieza. Funciones sencillas, sin capas de repositorios o proveedores propias | RF-1, RF-9, RF-10 |
| `testing/spec_001/test_account_capacity.py` | A-1: casos de camino básico y límites de capacidad/vigencia con dependencias controladas | RF-2, RF-3, RF-4 |
| `testing/spec_001/test_student_creation.py` | A-2: creación, reutilización y rechazos con dependencias controladas | RF-2, RF-3, RF-5 |
| `testing/spec_001/test_session_creation.py` | A-3: validaciones, matrícula y fallo de persistencia en contexto HTTP aislado | RF-2, RF-3, RF-6 |
| `testing/spec_001/test_integration.py` | Casos seleccionados con SQL Server local real; nunca incluidos en la ejecución predeterminada | RF-4, RF-5, RF-6, RF-9, RF-10 |
| `docs/specs/spec-001-tests/test.md` | Registro central de grafos Mermaid, caminos, checklist, instrucciones, resultados, defectos y veredicto | RF-2, RF-3, RF-7, RF-8, RF-9 |
| `docs/specs/spec-001-tests/evidence.md` | Resumen versionado de resultados. Los reportes y journals que generen los runners en `evidence/<run_id>/` son locales y no se versionan | RF-7, RF-9, RF-10 |

Los paquetes de pruebas tendrán los marcadores mínimos necesarios para descubrimiento con unittest. No se crearán servicios de ejecución HTTP, interfaz de pruebas, clases base extensibles, CI/CD ni herramientas de reportes adicionales.

El entorno virtual propio residirá dentro del proyecto de pruebas. Reutilizar dependencias por referencia no implica compartir el entorno virtual del backend ni modificarlo. La documentación explicará que las dependencias importadas por las rutas, aunque no se ejerciten, deben estar disponibles.

## 2. Integración técnica con la aplicación existente

**Cubre:** RF-1, RF-4, RF-5, RF-6 y RF-10; RNF-2, RNF-3 y RNF-4.

### 2.1 Importaciones y contexto

- El backend usa importaciones absolutas de `models`, `routes`, `services`, `config` y `app`. Se añadirá temporalmente su directorio a la ruta de importación del proceso de pruebas; no se renombrarán paquetes ni se editará la aplicación.
- [La fábrica existente](../../../backend/app.py#L115) ofrece `create_app(config_name=None)`. No existe perfil `testing`: los únicos perfiles son `development` y `production` en [la configuración](../../../backend/config.py). No se invocará un perfil inexistente ni se añadirá otro al backend.
- La configuración captura variables al importar sus clases. La preparación del entorno debe realizarse **antes** de importar `app` o `config`. Se importará primero `app`, después las rutas, evitando conflictos con la importación de `limiter` desde autenticación.
- Las dos modalidades se ejecutarán en procesos separados. Las sustituciones se aplicarán con `unittest.mock` y gestores de contexto o limpieza registrada en unittest; no se mezclarán módulos ya configurados para aislamiento con una conexión real.
- En pruebas aisladas se construirán únicamente los contextos Flask/JWT necesarios. Las consultas y escrituras ORM quedarán sustituidas; no se usará la fábrica completa ni la conexión del entorno del backend. Se proporcionará una clave JWT efímera del proceso, nunca registrada, si la importación la exige.
- Para A-3 aislado se llamará al cuerpo original de la vista a través de sus envoltorios identificados por `__wrapped__`, dentro de un contexto de solicitud y con identidad controlada. Esto verifica el algoritmo, **no** autenticación, autorización ni el endpoint completo.
- En integración se utilizará la fábrica existente y `Flask.test_client()` con los decoradores reales, la conexión local y usuarios ficticios activos. SQL Server no se sustituirá. El cliente en proceso verifica HTTP–aplicación–ORM–SQL; no prueba el servidor de red ni el frontend.
- El sistema se comprobará aparte con frontend y backend ejecutados en local, sin automatizar el navegador. No se cambiará configuración persistente de la aplicación para ejecutar pruebas.

### 2.2 Dependencias y límites

Se utilizan Python/unittest, `unittest.mock`, Flask, Flask-JWT-Extended, Flask-SQLAlchemy, SQLAlchemy, python-dotenv, pyodbc, requests y openpyxl ya presentes directa o transitivamente en [las dependencias del backend](../../../backend/requirements.txt). Otras dependencias importadas por módulos existentes también se instalarán desde ese mismo listado, sin ejercitar funcionalidades excluidas.

No se instalarán pytest, Selenium, Playwright, un generador de reportes o una base alternativa. SQLite no sustituye SQL Server: el esquema existente usa UUID nativos, `NEWID()` y restricciones que no deben presentarse como verificadas sobre otro motor.

No se ejecutarán `db.create_all()`, scripts iniciales ni el seed para preparar una base que ya tiene datos. La ausencia de esquema o roles necesarios bloquea integración; su instalación o reparación queda fuera de esta spec.

## 3. Contratos existentes y contratos de las pruebas

**Cubre:** RF-1, RF-2, RF-4, RF-5, RF-6 y RF-9.

### 3.1 A-1 — Capacidad de cuentas

Fuente: [account_creation_allowed](../../../backend/services/subscription_quota.py#L69).

| Elemento | Contrato observado |
|---|---|
| Entrada | `institucion_id`; `reference` opcional, fecha UTC sin zona conforme al almacenamiento existente |
| Salida | Tupla `(allowed, message)`; éxito: `(True, None)` |
| Suscripción o plan ausente | `(False, 'La institución no tiene una suscripción configurada')` |
| Vigencia o actividad inválida | `(False, 'La suscripción de la institución no está activa o vigente')` |
| Capacidad alcanzada/superada | `(False, 'Límite de cuentas alcanzado para el plan asignado')` |
| Conteo | Usuarios activos de la institución, sin filtrar por rol: incluye coordinadores y estudiantes |
| Persistencia | Solo lectura; no reserva capacidad ni escribe datos |

La falta de plan asociado se simulará únicamente en aislamiento: `plan_id` es obligatorio en el esquema. No se romperá una clave foránea para provocar ese caso.

### 3.2 A-2 — Alta o reutilización de estudiante

Fuente: [_get_or_create_estudiante](../../../backend/routes/coordinador.py#L131).

| Elemento | Contrato observado |
|---|---|
| Entrada | Email, nombres, teléfono, contraseña e identificador de institución |
| Salida | `(user, created)`; reutilización: mismo usuario y `False`; alta: usuario nuevo y `True` |
| Email inválido | `ValueError` |
| Cuenta en otra institución | `StudentTenantConflict` |
| Cuenta existente sin rol estudiante | `ValueError` |
| Contraseña inválida | `ValueError` con resultado del validador existente |
| Capacidad insuficiente | `AccountLimitReached` |
| Rol estudiante inexistente | `RuntimeError` |
| Efectos del alta | Añade usuario, vincula rol estudiante y realiza `flush`; **no hace commit** |

En integración el llamador de prueba controla el commit o rollback. La reutilización debe conservar la identidad y no incrementar el número de usuarios; los rechazos no deben crear otro estudiante. No se convierte una excepción del helper en un status HTTP inventado.

### 3.3 A-3 — Creación de conversación

Fuentes: [create_sesion](../../../backend/routes/estudiante.py#L313) y [_is_enrolled](../../../backend/routes/estudiante.py#L45).

| Elemento | Contrato observado |
|---|---|
| Interfaz | `POST /api/estudiante/chat/sesiones`, JSON y bearer token de estudiante |
| Entrada | `curso_id`, convertible mediante `int`; `titulo` de texto opcional |
| Éxito | `201`, objeto `sesion` con identidad del estudiante, curso y título; persistencia confirmada |
| Curso ausente/falso | `400`, `message: 'curso_id es requerido'` |
| Conversión inválida | `400`, `message: 'curso_id debe ser un número'` |
| Matrícula no activa/no existente | `403`, `message: 'No estás inscrito en este curso'` |
| Fallo dentro del bloque de creación | Rollback y `500`, `message: 'Error al crear la sesión'` |
| Título omitido o vacío | `Nueva Conversación` |

La matrícula se consulta por usuario, curso y `is_active=True`. No se enviarán mensajes. No se probará una normalización de tipos más estricta que la implementada ni se añadirán garantías de curso/institución ajenas al algoritmo seleccionado.

### 3.4 Interfaces necesarias para los casos de sistema

- Alta desde un curso: `POST /api/coordinador/cursos/<curso_id>/estudiantes`, con email, al menos un dato personal y contraseña para entrar en la rama de creación. Una capacidad agotada responde `409`. No usar el caso de solo email, que busca una cuenta existente.
- Importación mínima: [la operación de curso](../../../backend/routes/coordinador.py#L675), `POST /api/coordinador/cursos/<curso_id>/estudiantes/importar/excel`, recibe multipart con campo `file`. Se usará un Excel de dos filas, con columnas `email`, `first_name`, `last_name`, `phone` y `password`: una cuenta nueva y una existente del mismo tenant, aún no matriculada en ese curso. Resultado esperado con datos válidos: `200`, `created=1`, `enrolled=2`, `skipped=[]`.
- Para el rechazo sin matrícula se podrá utilizar PowerShell contra el endpoint de conversación existente, manteniendo el token únicamente en memoria. No se capturarán comandos con credenciales ni cabeceras de autorización.

Los cuerpos son contratos ya existentes, no un nuevo modelo JSON de la aplicación. Los mensajes públicos ya presentes se conservarán aunque algunos errores secundarios estén en otro idioma; esta spec no los corrige.

### 3.5 Contrato del ejecutor y la evidencia

- Ejecución predeterminada: solo pruebas aisladas y sin lectura de secretos del backend.
- Integración: selección explícita, validación del destino y confirmación interactiva antes de crear datos. En ausencia de confirmación, no habrá escritura.
- Resultado de proceso: éxito solo si todas las comprobaciones seleccionadas pasan, ninguna obligatoria se omite y la limpieza requerida termina. Fallos, bloqueos, omisiones obligatorias o residuos deberán producir resultado no satisfactorio claramente identificado.
- unittest puede informar `OK` con casos omitidos: el resumen de evaluación deberá distinguirlo y no declarar cumplidos los requisitos omitidos. Una prueba omitida se registra como **no ejecutada**, no **no aplicable**.
- Reportes: identificación de ejecución, spec, fecha, versión/commit y modalidad; resultados esperados/obtenidos y resumen de limpieza. Solo datos ficticios necesarios. La salida técnica de unittest puede permanecer en su formato original; instrucciones y evaluación estarán en español.
- No se prometerá descubrimiento de todos los caminos por una herramienta de cobertura. La relación entre grafo, camino y caso se revisará expresamente.

## 4. Modelo de datos y preparación del entorno

**Cubre:** RF-4, RF-5, RF-6, RF-7, RF-9 y RF-10; RNF-3, RNF-5 y RNF-7.

### 4.1 Datos de prueba mínimos

No se introduce un modelo transaccional nuevo ni cambios de esquema. Se utilizan [las entidades institucionales](../../../backend/models/institucion.py), [las académicas](../../../backend/models/academia.py), [User](../../../backend/models/user.py) y [SesionChat](../../../backend/models/ia_chat.py).

| Recurso | Preparación mínima y propósito |
|---|---|
| Roles | Leer `coordinador` y `estudiante` existentes, sin modificarlos. Rol ausente: simular solo la consulta en aislamiento |
| Instituciones | Dos instituciones activas exclusivas de la ejecución para comprobar separación institucional |
| Planes | Propios de la ejecución, con capacidades finitas pequeñas e ilimitada cuando corresponda; nunca alterar planes existentes |
| Suscripciones | Propias, vinculadas a esos planes e instituciones, fechas UTC controladas y actividad por caso |
| Usuarios | Coordinador, estudiante existente, estudiante de otra institución y cuenta sin rol estudiante, según el caso; nombres ficticios y emails únicos bajo `example.invalid` |
| Cursos | Curso propio de institución principal y otro curso cuando se compruebe matrícula de otro curso |
| Matrículas | Ausente, activa e inactiva según el caso; nunca duplicar el par usuario–curso |
| Conversaciones | Solo las creadas por el algoritmo probado; sin mensajes |

Los campos obligatorios de los modelos se completarán aunque no sean objeto de una aserción. Por ejemplo, la suscripción exige `limite_tokens_mensual`: se rellenará como requisito estructural del registro, sin calcular, consumir ni probar tokens. No se crearán tarifas ni registros de consumo.

Para A-1 se usará una referencia fija, por ejemplo 30 de septiembre de 2026 a las 12:00 UTC, sin zona en el objeto persistido. Para A-2 y A-3 con la aplicación real se crearán suscripciones válidas respecto del instante de preparación; los límites temporales exactos se ejercitarán mediante `reference` en A-1, no cambiando el reloj del servidor.

En sistema, la capacidad tendrá en cuenta al coordinador activo: con coordinador y estudiante existente, un límite de dos bloquea un alta nueva; un plan propio con límite de cuatro permite la importación de un estudiante adicional. Estos escenarios utilizarán conjuntos de datos propios separados o preparación explícita, sin dependencia del orden de los tests.

### 4.2 Destino local y prevención de efectos externos

1. Cargar explícitamente la configuración de entorno local del backend antes de importar la fábrica. Si una variable de conexión ya existente en el proceso difiere de la configurada allí, bloquear integración y pedir resolver el conflicto; no elegir silenciosamente un destino.
2. Analizar la URL con SQLAlchemy, incluyendo los parámetros de conexión ODBC cuando corresponda; no registrar la cadena ni credenciales.
3. Comprobar que el servidor corresponde a loopback o a una instancia identificada de la máquina local. No asumir que cualquier nombre de equipo o que `FLASK_ENV=development` significa destino seguro.
4. Abrir una conexión de solo lectura y comprobar identidad de servidor/base y disponibilidad del esquema requerido. Mostrar únicamente etiquetas de destino sin credenciales. Si no puede verificarse la localidad, bloquear escritura.
5. Solicitar confirmación expresa del operador para ese destino antes de preparar fixtures. La conexión proviene de la configuración existente, no de un segundo secreto.
6. En el proceso de integración mantener rate limiting en memoria mediante un ajuste efímero de entorno anterior a las importaciones, si es necesario para evitar un almacén externo configurado. El limitador de Flask seguirá siendo el real, no un mock; únicamente cambia su almacenamiento en ese proceso. No persistir el ajuste y documentar que no se verifica rate limiting ni su almacenamiento habitual.
7. No llamar endpoints de mensajes, recursos, práctica, conocimiento o notificaciones. En aislamiento, una llamada externa inesperada fallará mediante sustitución controlada del punto HTTP empleado por las rutas; en integración no se sustituirán los componentes que se afirman integrados.

Se necesita SQL Server local con esquema instalado, driver ODBC compatible con la conexión existente, permisos sobre los registros de prueba, y aplicación local disponible para sistema. No se conectará ni se ejecutará una verificación del destino durante esta planificación.

### 4.3 Registro JSON de propiedad y recuperación

**Decisión:** sí se necesita un JSON pequeño exclusivamente operativo. El registro Markdown centraliza resultados; el JSON permite recuperar y limpiar fixtures después de una interrupción sin depender solo de memoria. No es una API, un almacén de reglas ni una copia de datos del producto.

Se conservará como `ownership.json` dentro de la evidencia de la ejecución. No incluirá URI, credenciales, contraseña, hash, token, contenido privado ni exportaciones de la base.

| Campo | Tipo/valores | Propósito |
|---|---|---|
| `spec_id` | Texto, `SPEC-001` | Trazabilidad |
| `run_id` | UUID textual | Propiedad y separación de ejecuciones |
| `started_at`, `updated_at` | Fecha ISO 8601 UTC | Seguimiento |
| `version` | Commit o etiqueta de versión evaluada | Reproducibilidad; registrar si hay cambios locales |
| `mode` | `integration` o `system` | Tipo de preparación |
| `destination_label` | Identificador local sin credenciales | Revalidación del destino al limpiar |
| `state` | `preparing`, `ready`, `cleaning`, `cleaned`, `cleanup_failed` | Estado de recuperación |
| `resources` | Lista de registros | Identidades y etiquetas exclusivas creadas o previstas |
| Cada recurso | `entity`, `id` si se conoce, `ownership_marker`, `state` | Entidad permitida, identidad exacta, marca de ejecución y estado de creación/limpieza |
| `cleanup_errors` | Lista de mensajes saneados | Residuos o bloqueos, sin traceback con secretos |

Se guardarán marcas/UUID previstos **antes** de crear registros y los identificadores obtenidos inmediatamente después del commit. Para identidades generadas por SQL se registrará previamente una marca única de nombre/email y el padre ya identificado. Así se podrá localizar un registro propio aun si el proceso se interrumpe antes de guardar el ID retornado. Las conversaciones se recuperarán por usuarios y cursos exclusivos previamente registrados.

Las actualizaciones del registro se harán con escritura temporal y reemplazo, usando la biblioteca estándar. La confirmación previa de destino se repetirá antes de una recuperación; el JSON por sí solo no autoriza borrar.

### 4.4 Limpieza

- Registrar la limpieza antes de empezar la preparación y ejecutarla aun si falla la creación parcial, una aserción o una prueba HTTP. Intentar limpiar en `finally`/mecanismos de cleanup de unittest y hacer rollback de sesiones pendientes antes de borrar.
- A-2 hace flush sin commit, pero A-3 confirma su transacción. Por eso un rollback global **no** basta para todos los casos: se requiere borrado explícito por propiedad.
- Orden para los recursos de este alcance: conversaciones y matrículas; asociaciones de rol de usuarios propios; usuarios; cursos; suscripciones; instituciones; planes propios sin referencias. No borrar roles compartidos. Respetar claves foráneas y comprobar los resultados de la limpieza.
- Seleccionar por ID y pertenencia documentada, nunca borrar por un prefijo amplio sin comprobar el registro de ejecución, ni eliminar una institución compartida para aprovechar cascadas.
- Si hay dependencias inesperadas o datos que no pueden atribuirse con certeza a la ejecución, detener ese borrado, registrar residuo y solicitar investigación; no ampliar la limpieza a datos ajenos.
- Una interrupción brusca puede impedir cleanup automático. La documentación explicará la recuperación por registro; no se declarará limpieza exitosa si quedan residuos.
- No se habilitará una limpieza automática sobre todas las ejecuciones anteriores ni se creará un servicio permanente de mantenimiento.

## 5. Caja blanca: grafos y caminos previstos

**Cubre:** RF-2, RF-3, RF-4, RF-5 y RF-6.

Los valores siguientes se derivan de las funciones revisadas en esta planificación. Se contrastarán con la versión exacta al implementar; un cambio del código requiere actualizar la documentación del grafo, no forzar el cálculo.

### 5.1 Convención común

- Cada decisión `if` completa es un predicado. No se desglosa el cortocircuito de `and`/`or` ni se representa cada expresión de valor por defecto como otro algoritmo.
- Las conversiones y el bloque de persistencia de A-3 tienen aristas de salida normal/error explícito. Se agrupan `ValueError`/`TypeError` de conversión en la misma salida del contrato.
- Consultas, validadores, hash, serialización y decoradores se representan como operaciones subordinadas sin expandir sus grafos. No se inventan manejadores para excepciones que el algoritmo no captura.
- Los retornos y excepciones explícitas confluyen en una salida común `X` de cada grafo. Los nodos de operación rectilínea pueden agruparse sin cambiar la complejidad.
- Para los grafos conectados se usa $V(G)=E-N+2$. Las variantes de vigencia o datos que comparten camino se añaden como comprobaciones esenciales, no se cuentan como nuevos caminos independientes.
- La independencia se comprobará contrastando las aristas de cada camino respecto de los anteriores. No se afirmará cobertura de condiciones, MC/DC o todos los recorridos del código Python.

Los grafos Mermaid definitivos se incluirán en el documento de pruebas, utilizando los nodos y aristas siguientes. No requieren instalar una dependencia del frontend para renderizarse.

### 5.2 A-1 — Capacidad

Nodos: `S` entrada y consulta; `D1` falta suscripción/plan; `R1` rechazo de configuración; `D2` actividad/vigencia inválida; `R2` rechazo de vigencia; `D3` límite ilimitado; `C` conteo; `D4` cuentas ≥ límite; `R3` rechazo de capacidad; `A` permiso; `X` salida.

Aristas: S→D1; D1→R1/D2; R1→X; D2→R2/D3; R2→X; D3→A/C; C→D4; D4→R3/A; R3→X; A→X.

**N=11, E=14, V(G)=5.**

| Camino/caso | Secuencia | Resultado esperado |
|---|---|---|
| A1-P1 | S–D1–R1–X | Configuración ausente: rechazo |
| A1-P2 | S–D1–D2–R2–X | Suscripción/plan no activo o no vigente: rechazo |
| A1-P3 | S–D1–D2–D3–A–X | Capacidad ilimitada: permitido |
| A1-P4 | S–D1–D2–D3–C–D4–R3–X | Límite alcanzado: rechazo |
| A1-P5 | S–D1–D2–D3–C–D4–A–X | Por debajo del límite: permitido |

Variantes mínimas mediante parámetros/subtests: plan ausente en aislamiento; suscripción inactiva, futura y vencida, y plan inactivo; referencia exactamente en inicio/fin; conteo igual/superior al límite. La exclusión de cuentas inactivas y de otra institución exige además conteo real de integración, no solo devolver un número desde un mock.

### 5.3 A-2 — Estudiante

Nodos: `S` normalización; `D1` email inválido; `R1` error email; `D2` usuario existente; `D3` otra institución; `R2` conflicto institucional; `D4` rol incompatible; `R3` error rol; `U` reutilización; `D5` contraseña inválida; `R4` error contraseña; `D6` capacidad denegada; `R5` error capacidad; `D7` falta rol configurado; `R6` error configuración; `A` alta, rol y flush; `X` salida.

Aristas: S→D1; D1→R1/D2; R1→X; D2→D3/D5; D3→R2/D4; R2→X; D4→R3/U; R3→X; U→X; D5→R4/D6; R4→X; D6→R5/D7; R5→X; D7→R6/A; R6→X; A→X.

**N=17, E=23, V(G)=8.**

| Camino/caso | Secuencia | Resultado esperado |
|---|---|---|
| A2-P1 | S–D1–R1–X | Email inválido: ValueError, sin alta |
| A2-P2 | S–D1–D2–D3–R2–X | Cuenta de otra institución: StudentTenantConflict |
| A2-P3 | S–D1–D2–D3–D4–R3–X | Cuenta sin rol estudiante: ValueError |
| A2-P4 | S–D1–D2–D3–D4–U–X | Mismo estudiante: misma identidad, created=False |
| A2-P5 | S–D1–D2–D5–R4–X | Contraseña inválida: ValueError |
| A2-P6 | S–D1–D2–D5–D6–R5–X | Capacidad agotada: AccountLimitReached |
| A2-P7 | S–D1–D2–D5–D6–D7–R6–X | Rol configurado ausente: RuntimeError |
| A2-P8 | S–D1–D2–D5–D6–D7–A–X | Alta vinculada con institución/rol, created=True |

La normalización del email se comprobará sobre P4 usando mayúsculas y espacios; no se abrirá una suite independiente de formatos. Una contraseña inválida representativa basta para P5. La ausencia del rol global se provocará con sustitución de consulta solo en aislamiento, nunca eliminando el rol real.

### 5.4 A-3 — Conversación

Nodos: `S` identidad y JSON; `D1` falta curso; `R1` 400 requerido; `D2` conversión con salida normal/error; `R2` 400 formato; `D3` matrícula activa; `R3` 403 matrícula; `D4` bloque de creación con salida normal/error; `R4` rollback/500; `A` 201 con sesión; `X` salida.

Aristas: S→D1; D1→R1/D2; R1→X; D2→R2/D3; R2→X; D3→R3/D4; R3→X; D4→R4/A; R4→X; A→X.

**N=11, E=14, V(G)=5.**

| Camino/caso | Secuencia | Resultado esperado |
|---|---|---|
| A3-P1 | S–D1–R1–X | Curso omitido: 400, sin alta |
| A3-P2 | S–D1–D2–R2–X | Curso no convertible: 400, sin alta |
| A3-P3 | S–D1–D2–D3–R3–X | Sin matrícula activa: 403, sin alta |
| A3-P4 | S–D1–D2–D3–D4–R4–X | Fallo controlado de persistencia: 500 y rollback |
| A3-P5 | S–D1–D2–D3–D4–A–X | Conversación persistida: 201 |

P3 tendrá variantes de matrícula inactiva, de otro curso o de otro usuario en integración. P5 verificará el título por defecto y un título explícito sin añadir otro grafo. P4 provocará una excepción controlada en persistencia solo en aislamiento; comprobará que se llama a rollback, no se filtra la excepción en el cuerpo público y no se confirma la escritura.

**Conjunto base:** 18 caminos independientes entre los tres algoritmos. No son 18 funcionalidades nuevas ni un objetivo de cobertura global. Se implementarán casos parametrizados/subtests donde simplifique, sin perder la identificación de cada camino. Las variantes esenciales y la integración complementan ese conjunto; no lo sustituyen.

## 6. Decisiones técnicas justificadas

| Decisión | Justificación y límite | RF / RNF |
|---|---|---|
| unittest y unittest.mock | Incluidos en Python; suficientes para aserciones, subtests y sustituciones temporales | RF-1, RF-8; RNF-1 |
| Proyecto y entorno propios | Evita contaminar dependencias, arranque y pruebas de los proyectos de aplicación | RF-1; RNF-2 |
| Importar lógica existente, no copiarla | Prueba la fuente real; una reproducción del algoritmo podría fallar de forma distinta o duplicar sus defectos | RF-1, RF-2; RNF-4 |
| Contextos mínimos aislados; fábrica real solo en integración | Previene acceso accidental a SQL en la ejecución predeterminada y respeta las importaciones actuales | RF-1, RF-10; RNF-3 |
| Cliente Flask en proceso para integración | Verifica contrato HTTP, decoradores y SQL sin gestionar otro servidor desde el ejecutor; sistema local verifica el despliegue en ejecución | RF-6, RF-9 |
| SQL Server local con confirmación | Usa el motor real y la conexión existente, sin nueva infraestructura ni sustitución por SQLite | RF-9, RF-10; RNF-2 |
| Datos propios y limpieza explícita | La aplicación hace commits; no basta rollback de una transacción envolvente; evita afectar registros existentes | RF-10; RNF-3 |
| JSON mínimo de propiedad | Posibilita recuperación tras interrupción; no incorpora un modelo de negocio o una plataforma de almacenamiento | RF-10; constitución V |
| Mermaid y checklist Markdown | Explican los caminos y permiten revisar evidencia sin añadir dependencias a la aplicación | RF-3, RF-7, RF-8 |
| Reportes de texto y observaciones manuales confirmadas | Evidencia suficiente para este alcance; no se exigen capturas de pantalla ni se justifica generador HTML, JUnit o porcentaje de cobertura | RF-7, RF-8, RF-9; RNF-5 |
| Sistema manual acotado | Tres escenarios reales y una denegación HTTP; menor mantenimiento que automatización de navegador | RF-9; RNF-1 |
| Regresión proporcional | Reutilizar estos casos cuando cambia la lógica; no imponer otros tres algoritmos a cada spec | RF-11; RNF-1 |

## 7. Estrategia de pruebas y evaluación PUDS

**Cubre:** RF-2 a RF-11, especialmente RF-3, RF-7 y RF-9.

### 7.1 Planificar y diseñar

- Crear el documento de pruebas con alcance A-1/A-2/A-3, versión fuente de los grafos y correspondencia con RF-1 a RF-11 y los RNF.
- Vincular cada caso con su algoritmo/camino, justificación, preparación, entradas, resultado esperado, nivel de prueba y procedimiento de limpieza.
- Definir recursos locales y comprobar prerrequisitos; cualquier recurso ausente debe producir bloqueo documentado, no una aprobación ficticia.
- La revisión documental verifica estructura, no intrusión, instrucciones, seguridad y continuidad. Es evidencia de esos entregables, no de ejecución funcional.

### 7.2 Ejecutar pruebas aisladas

- Ejecutar el conjunto de caminos de la sección 5, con variantes esenciales agrupadas.
- A-1: consultas simuladas y referencia temporal explícita; verificar también los filtros de institución/actividad usados por la lógica.
- A-2: consultas y sesión controladas; conservar los validadores existentes cuando sea sencillo, sin duplicarlos. Verificar identidad de reutilización, asociación de rol y efectos add/flush sin commit. No comprobar el algoritmo criptográfico del hash.
- A-3: contexto JSON/identidad controlado y persistencia simulada; comprobar cuerpos, status y acciones de commit/rollback.
- Garantizar reversión de todas las sustituciones y ausencia de llamadas SQL o HTTP externas. Los mocks no se presentarán como evidencia de restricciones SQL reales.

### 7.3 Ejecutar integración

| ID | Caso mínimo | Evidencia exigida | RF |
|---|---|---|---|
| I-1 | Conteo de cuentas: por debajo del límite, alcanzado; cuenta inactiva y cuenta de otra institución no suman; plan propio ilimitado permite | Resultado real de A-1 y conteos de SQL, sin sustitución de consultas | RF-4, RF-9, RF-10 |
| I-2 | Alta válida y posterior reutilización por email normalizado | Identidad, asociación institucional/rol y número de cuentas antes/después del commit | RF-5, RF-9, RF-10 |
| I-3 | Rechazo de email de otro tenant, cuenta sin rol estudiante y capacidad agotada | Excepción esperada y ausencia de cuenta adicional en SQL | RF-5, RF-9, RF-10 |
| I-4 | POST de conversación con matrícula activa y con matrícula ausente/inactiva/de otro curso o usuario | 201/403 según el caso y existencia/ausencia de nueva sesión en SQL | RF-6, RF-9, RF-10 |

Estos casos parten de fixtures independientes; pueden usar subtests, pero no depender de que otro test cree previamente la cuenta. El token del estudiante para el cliente Flask se genera dentro del contexto de la aplicación real con los usuarios ficticios; no se requiere testar login para probar A-3. En sistema se accederá normalmente por la interfaz de login existente.

Solo se permitirá la modificación de fixtures propios. Tras cada conjunto se comprobará la limpieza. Los errores de persistencia y rol ausente se mantienen aislados, pues provocarlos destruyendo el estado compartido no es aceptable.

### 7.4 Ejecutar sistema local

Preparar explícitamente datos ficticios persistentes y registrar su propiedad antes de iniciar el recorrido; no borrarlos hasta registrar los resultados. Ejecutar frontend y backend mediante sus instrucciones existentes, sin editar sus proyectos.

| ID | Procedimiento acotado | Resultado esperado y evidencia | RF |
|---|---|---|---|
| S-1 | Coordinador de institución propia con capacidad completa intenta crear un estudiante desde su curso | Alta rechazada, respuesta 409 y sin usuario nuevo; observación confirmada por el operador y reporte SQL saneado | RF-4, RF-9 |
| S-2 | Coordinador importa el Excel mínimo de dos filas en un curso propio sin esas matrículas previas | Una cuenta nueva, una reutilizada, dos matrículas; respuesta con created=1, enrolled=2 y skipped vacío, más identificación/conteo en SQL | RF-5, RF-9 |
| S-3 | Estudiante ficticio matriculado inicia una conversación desde la aplicación | Conversación visible y persistida para usuario/curso; no enviar mensajes | RF-6, RF-9 |
| S-3b | Estudiante ficticio sin matrícula solicita la creación por HTTP local si la UI no lo permite, enviando su bearer token válido mantenido en memoria | 403 y sin conversación nueva; registrar solo la respuesta, sin capturar el token ni la cabecera de autorización | RF-6, RF-9 |

S-3b complementa el tercer escenario, no añade otra funcionalidad al alcance. Para S-1/S-2/S-3 se registra la observación confirmada por el operador, incluidos resultado UI y status/valores HTTP observados, junto con el reporte SQL propio; no se exigen capturas de pantalla. La observación comunicada no se presenta como HTTP capturado por el asistente y SQL por sí solo no acredita la interfaz ni el contrato HTTP. S-3b conserva su reporte HTTP saneado y verificación SQL. No se exige probar toda la importación ni todas las pantallas alcanzadas para navegar.

### 7.5 Evaluar y tratar fallos

El documento de pruebas incluirá una tabla con **RF/RNF, caso o revisión, resultado esperado, resultado obtenido, estado, evidencia y defecto pendiente**. Los estados serán aprobado, fallido, no ejecutado o no aplicable con justificación. Toda fila comenzará como no ejecutada; redactar el procedimiento no cambia ese estado.

La evidencia de cada ejecución identificará fecha, commit/versión, cambios locales relevantes, modalidad, destino local saneado, reporte y limpieza. No se incluirán secretos, claves JWT, tokens, contraseñas temporales ni datos personales reales. Los Excel de sistema con contraseñas ficticias temporales se usarán solo como recurso de ejecución, se eliminarán al finalizar y no se adjuntarán como reporte.

Ante fallos: registrar caso/requisito afectado y resultado reproducible, notificar al responsable y documentar la decisión de prolongar construcción, diferir o investigar. No corregir backend/frontend ni actualizar la spec para dar por bueno el fallo sin aprobación.

La evaluación final distinguirá cumplimiento del proyecto de pruebas, comportamiento verificado y limitaciones. Un requisito funcional no ejecutado/fallido no se considerará cumplido; decidir cerrar trabajo con un defecto no equivale a aprobar ese requisito.

## 8. Documentación de herramientas y continuidad

**Cubre:** RF-7, RF-8 y RF-11.

### 8.1 Instrucciones de uso que deberá contener el documento de pruebas

- Entorno virtual propio y dependencias por referencia; directorio desde el que ejecutar y selección explícita de la modalidad.
- Pasos PowerShell para ejecutar unittest, conservar salida estándar/error y capturar inmediatamente el código de salida del proceso. Una tubería de captura no debe ocultar el fracaso de los tests.
- Prerrequisitos de integración, verificación de destino, confirmación, preparación, ejecución y recuperación/limpieza por registro.
- Cómo representar/renderizar los bloques Mermaid con un visor compatible, sin instalar cambios en el frontend. No usar un visor público para datos de ejecución privados; los grafos no incluirán credenciales ni datos reales.
- Cómo interpretar errores, fallos y omisiones de unittest y trasladarlos al checklist; ejemplos claramente marcados como esperados, nunca como resultados reales.
- Cómo comprobar manualmente S-1/S-2/S-3, registrar la confirmación del operador y sus resultados observados, y conservar reportes SQL/HTTP saneados de S-3b sin tokens o campos de contraseña; no se exigen capturas de pantalla.
- Limitaciones: un reporte de unittest no calcula cobertura de caminos; los grafos y trazabilidad documentan los caminos seleccionados; esta construcción no publica un porcentaje global ni certifica el MVP.

Se utilizará texto y tablas, con los comandos de uso documentados durante la implementación documental. En esta planificación no se instalan herramientas, se arrancan programas ni se ejecutan pruebas.

### 8.2 Nuevas specs

- Cada nueva spec conservará su propio documento de pruebas y evidencias. Se reutilizarán instrucciones comunes del proyecto por referencia, evitando copias divergentes.
- Añadir módulos bajo el identificador de la nueva spec solo si hay lógica específica que lo justifique; no construir ahora un catálogo o motor dinámico de suites futuras.
- Documentar qué casos de SPEC-001 se reutilizan por impacto del cambio, cuáles se adaptan y cuáles quedan fuera del alcance. Una ejecución de regresión mantiene la identificación original de caso y añade la referencia de la spec evaluada.
- No se requieren otros dos o tres algoritmos por nueva spec. Si hay un nuevo análisis, debe tener límites y justificación de riesgo propios.

## 9. Matriz de cobertura del plan

| Requisito | Partes del plan | Verificación prevista |
|---|---|---|
| RF-1 | §§1, 2 y 3.5 | Revisión de independencia y diff; ejecución aislada sin SQL/HTTP; restauración de mocks |
| RF-2 | §§1, 3, 5 y 7.1 | Correspondencia caso–algoritmo–riesgo–baseline/RF, sin suites genéricas |
| RF-3 | §5 | Tres grafos, nodos/aristas/cálculos, caminos factibles y resultados asociados |
| RF-4 | §§3.1, 4.1, 5.2 y 7 | Caminos A1, variantes temporales, I-1 y S-1 |
| RF-5 | §§3.2, 4.1, 5.3 y 7 | Caminos A2, I-2/I-3 y S-2 |
| RF-6 | §§3.3, 5.4 y 7 | Caminos A3, I-4 y S-3/S-3b |
| RF-7 | §§1, 3.5 y 7.5 | Documento central, checklist con estados y evidencia por requisito |
| RF-8 | §§2.2, 6 y 8.1 | Revisión y utilización posterior de las instrucciones, reportes y grafos |
| RF-9 | §7 | Integración y sistema realmente ejecutados, resultados y decisiones sobre fallos |
| RF-10 | §§3.5 y 4 | Bloqueo sin destino verificado/confirmación; datos exclusivos, registro durable y limpieza |
| RF-11 | §§1 y 8.2 | Procedimiento documentado de selección por riesgo y reutilización de regresión |

Los RNF se revisarán en conjunto: sencillez y mantenibilidad en estructura/diff; no intrusión en archivos modificados; reproducibilidad en fixtures y ejecuciones; evidencia honesta en checklist; idioma y confidencialidad en documentación/reportes. Ninguna revisión sustituye la ejecución requerida por los RF funcionales.

## 10. Comprobación constitucional y condiciones de cierre

| Principio | Cumplimiento previsto |
|---|---|
| I. Simplicidad | Stack conservado, unittest estándar y dependencias existentes; sin frameworks nuevos ni funcionalidades futuras |
| II. Spec–código | Spec aprobada; plan sujeto a revisión; todos los RF vinculados con entregables y verificación. Un cambio de alcance requiere aprobación previa |
| III. Separación | Pruebas externas a frontend/backend, reglas importadas sin copiarlas ni refactorizarlas; sin cambios de proveedores |
| IV. PUDS | Alcance y criterios, diseño/ejecución de integración, sistema y evaluación explícitos, con evidencia y decisiones sobre defectos |
| V. Persistencia y contratos | SQL Server real, sin cambios de esquema/API; registro durable mínimo para limpieza; configuración existente, secretos fuera de evidencias |
| VI. Idioma | Documentación y mensajes propios en español; identificadores/comentarios nuevos en inglés; nombres existentes conservados |

**Condiciones para pasar a implementación:** aprobación del plan y desglose posterior en tareas verificables. Si la implementación necesita modificar los proyectos de aplicación, alterar contratos o ampliar la lógica seleccionada, deberá detenerse esa parte y revisar primero la spec.

**Condiciones para cerrar la construcción:** entregables independientes, grafos/casos/checklist completos, herramientas documentadas, resultados reales registrados, limpieza comprobada y evaluación final por requisito. Fallos o bloqueos permanecerán explícitos aunque el responsable decida diferirlos. La planificación no certifica ni ejecución ni cumplimiento funcional.
