# Proyecto independiente de pruebas de TutorIA

**Spec:** [SPEC-001](../docs/specs/spec-001-tests/spec.md).  
**Plan:** [plan.md](../docs/specs/spec-001-tests/plan.md).  
**Registro:** [test.md](../docs/specs/spec-001-tests/test.md).

## Alcance actual

T1–T24 completan proyecto, grafos, pruebas, continuidad y evaluación. **Hay 23 pruebas aisladas, 53 controles simulados y cuatro casos de integración I-1…I-4**, algunos con subtests. Integración T18 aprobada y limpiada. Sistema S-1/S-3/S-3b aprobado, S-2 fallido y S-001 abierto; no se corrigen bugs del producto en esta spec. RNF-6 fallido por mensajes propios del runner en inglés (H-004). Cuatro conjuntos limpiados con verificación postcommit y Excel eliminado; servidores detenidos. [Evaluación final](../docs/specs/spec-001-tests/evidence.md#evaluación-final-t23t24-2026-09-30).

Este proyecto conserva sus dependencias y entorno virtual propios. No modifica ni comparte el entorno del frontend o backend. [support.py](support.py) importa temporalmente la lógica existente, evitando la carga de secretos y bloqueando conexiones; no crea la aplicación completa ni inicializa SQL.

## Preparación en Windows

Prerrequisito: Python 3.13 compatible con el backend, disponible mediante el lanzador de Python de Windows. Abrir PowerShell en la raíz del repositorio. Si ya existe el entorno de pruebas, omitir su creación.

```powershell
py -3.13 -m venv .\testing\.venv
if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno de pruebas.' }
& .\testing\.venv\Scripts\python.exe -m pip install -r .\testing\requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias de pruebas.' }
& .\testing\.venv\Scripts\python.exe -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Hay dependencias incompatibles.' }
```

Usar el intérprete por su ruta evita activar el entorno y cambiar la política de ejecución de PowerShell. Si no está disponible `py`, usar la ruta del intérprete Python 3.13 instalado para crear el entorno; no usar el entorno de ejecución del backend para instalar las dependencias de pruebas.

[requirements.txt](requirements.txt) referencia el [listado existente del backend](../backend/requirements.txt). unittest y unittest.mock pertenecen a Python y no requieren instalación. Las rutas actuales importan otras dependencias de ese listado aunque los algoritmos seleccionados no las invoquen; por eso se reutiliza el conjunto existente, sin añadir pytest ni duplicar versiones.

El entorno local y las cachés están excluidos mediante [.gitignore](.gitignore); no se versionan ejecutables ni paquetes instalados. No se añade otra copia de la configuración de conexión.

## Estructura y siguientes tareas

- [Paquete raíz](./__init__.py) y [paquete SPEC-001](spec_001/__init__.py): permiten organizar los módulos previstos.
- [Capacidad](spec_001/test_account_capacity.py), [estudiantes](spec_001/test_student_creation.py) y [conversaciones](spec_001/test_session_creation.py): T4–T9 completadas.
- [Autorización local](local_destination.py), [registro durable](ownership.py), [fixtures](fixtures.py), [limpieza](cleanup.py) y [controles](spec_001/test_local_safety.py): T10–T14 implementadas, verificadas en modalidad controlada.
- [Integración real local](spec_001/test_integration.py) y [ejecutor optativo](run_integration.py): T15–T18 completadas, evidencia en el registro.
- [Soporte de sistema](system_support.py) y [CLI optativa](run_system.py): preparación, verificación SQL, HTTP real y limpieza ejecutadas; tres recorridos manuales confirmados por operador, incluyendo fallo S-2. Evidencia enlazada en el registro.
- Instrucciones completas de herramientas, captura de salida/código, Mermaid y sistema: [SYSTEM.md](SYSTEM.md), T19.
- T23/T24 completadas como documentación y evaluación; RF-5/RNF-6 fallidos y S-001/H-004 abiertos, no todo aprobado. [Cierre](../docs/specs/spec-001-tests/evidence.md#evaluación-final-t23t24-2026-09-30).
- [Regresión proporcional](REGRESSION.md): selección por impacto/riesgo, reutilización de IDs, límites de modalidades y conservación de evidencia para futuras specs (T23).

## Ejecutar la suite aislada

Desde la raíz del repositorio:

```powershell
& .\testing\.venv\Scripts\python.exe -m testing.run_tests
$testExitCode = $LASTEXITCODE
if ($testExitCode -ne 0) { throw "La suite aislada no pasó: código $testExitCode." }
```

Para conservar evidencia, indicar un **nuevo** nombre dentro de las evidencias de la spec:

```powershell
$report = '.\docs\specs\spec-001-tests\evidence\isolated-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.txt'
& .\testing\.venv\Scripts\python.exe -m testing.run_tests --report $report
$testExitCode = $LASTEXITCODE
if ($testExitCode -ne 0) { throw "Revisar el reporte: la suite terminó con código $testExitCode." }
```

El [ejecutor](run_tests.py) carga solo los tres módulos aislados explícitos: no descubre integración. Guarda fecha UTC, UUID, versión, cambios locales por nombre, huellas de fuentes, resultados y restauración. No sobrescribe reportes existentes. Cero casos, caminos obligatorios ausentes, fallos, errores u omisiones producen código no satisfactorio; `OK` con omisiones no se presenta como verificación completa. Un rechazo de argumentos termina antes de ejecutar y puede no producir reporte.

Cada prueba vuelve a importar los algoritmos en un contexto acotado. Las consultas y persistencia se sustituyen en su punto de uso; los modelos, normalización y validadores existentes se conservan cuando corresponde. La vista de conversaciones se desenvuelve para comprobar su cuerpo, **no sus decoradores**. Un fallo de escritura simulado comprueba rollback sin intentar corromper SQL.

El soporte anula la carga automática dotenv antes de importar configuración, proporciona una clave efímera y bloquea lectura dotenv, conexiones SQLAlchemy/ODBC y peticiones requests. Si un handler captura el error del guardia, la salida del contexto igualmente falla por el intento. Los mocks, entorno, ruta y módulos se liberan incluso con errores. Esto protege los puntos usados por los módulos actuales; no es un sandbox para código arbitrario.

## Controles de seguridad y soporte, sin SQL real

El flag `--safety` selecciona los 53 controles de [test_local_safety.py](spec_001/test_local_safety.py), con persistencia, HTTP y configuración simulados. T14 ejecutó los 31 originales; 15 posteriores comprobaron soporte de sistema y siete adicionales la dependencia automática del curso y su reserva previa. No son recorridos funcionales. El ejecutor bloquea SQL/ODBC/HTTP/lectura dotenv reales; la suite predeterminada conserva los 23 casos de algoritmos.

```powershell
$report = '.\docs\specs\spec-001-tests\evidence\safety-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.txt'
& .\testing\.venv\Scripts\python.exe -m testing.run_tests --safety --report $report
$testExitCode = $LASTEXITCODE
if ($testExitCode -ne 0) { throw "Los controles no pasaron: código $testExitCode." }
```

Los registros temporales del harness se eliminan al salir. Las verificaciones controladas no acreditan permisos, restricciones, concurrencia ni limpieza sobre SQL Server real. La regresión de 23 casos tampoco lo hace.

## Datos locales optativos y recuperación

El [comando de datos locales](run_local_data.py) es independiente de las suites. **No se ha ejecutado contra SQL en T10–T14.** Sus acciones son `check`, `prepare --case capacity|students|conversations` y `cleanup --ownership <ruta del registro>`. Cada acción se inicia mediante `python -m testing.run_local_data` usando el intérprete propio desde la raíz, en un proceso separado. No ejecuta I-1…I-4, ni tiene un flag de confirmación automática.

`check` lee la configuración existente solo al solicitarlo, verifica en lectura identidad de máquina/base, tablas/columnas/PK/FK, roles, visibilidad de metadatos y permisos de SELECT/INSERT/UPDATE/DELETE. Solicita escribir exactamente `AUTORIZO <etiqueta mostrada>`. No crea fixtures. Si existe DATABASE_URL tanto en el proceso como en la configuración del backend y difieren, bloquea; no se imprime ninguna conexión o secreto. Los destinos remotos, ambiguos, redirigibles mediante parámetros no evaluados o sin identidad local comprobable se rechazan. Solo se aceptan mssql+pyodbc, loopback o el nombre identificado por el sistema operativo; no se aceptan alias DNS arbitrarios. Triggers activos sobre las tablas escritas también bloquean por efectos no evaluados.

`prepare` repite esas comprobaciones y confirmación, crea una nueva carpeta de evidencia por UUID y guarda el registro de propiedad antes de cada inserción. Usa modelos reales, fechas UTC sin zona, instituciones/planes/users/cursos propios y roles compartidos de solo lectura. La contraseña ficticia y su hash no se imprimen ni guardan en el registro. Al terminar queda el registro en estado `ready`: **esta acción conserva los fixtures hasta solicitar limpieza**. Un fallo parcial intenta limpiar inmediatamente y termina con código no satisfactorio aunque la limpieza pase. No se ejecuta seed, DDL, migración ni llamada de IA.

El registro durable contiene únicamente los campos definidos en el plan. Para UUID conocidos se guarda la identidad antes de insertar; para IDs SQL se reserva una marca exacta y el padre propio, y se registra el ID inmediatamente tras commit. Para altas/conversaciones futuras creadas por los algoritmos, el llamador deberá reservar antes el email/tenant o el par usuario/curso/título y registrar el ID tras commit: el builder no intercepta escrituras arbitrarias del producto. No se debe editar un registro para atribuirle datos preexistentes.

`cleanup` valida primero el JSON, revalida la conexión y exige **una nueva confirmación** del destino; la etiqueta debe coincidir con el registro. Recupera únicamente IDs y marcas exactas, comprueba padres propios e inspecciona todas las FK entrantes, incluso cascadas y otros esquemas. Mensajes, consumo, RAG, configuraciones u otras dependencias no previstas **bloquean el borrado**, no se eliminan para facilitarlo. Dos conversaciones indistinguibles por su marca sin ID también bloquean y requieren investigación.

La limpieza realiza preflight completo, borra explícitamente conversaciones/matrículas, asociaciones de roles de usuarios propios, usuarios, cursos, suscripciones, instituciones y planes, dentro de una transacción; no usa cascadas ORM ni borra roles. Retiene bloqueos exclusivos locales breves sobre las tablas involucradas para evitar inserciones concurrentes entre preflight y borrado: **ejecutar con la aplicación local inactiva y sin otros operadores escribiendo**. Puede bloquear temporalmente consultas o escrituras ajenas; no promete limpieza no bloqueante. Confirma ausencia antes de commit. Si falla, revierte y deja `cleanup_failed` con códigos saneados; no oculta residuos ni depende de un rollback global de las pruebas. Si SQL confirmó y se interrumpió antes de actualizar JSON, una nueva recuperación comprueba ausencia y termina el registro de forma idempotente.

El contexto `managed_fixtures()` instala limpieza antes de preparar y la intenta en `finally`, también ante errores del caso. La modalidad local mantiene el limitador real con almacenamiento efímero en memoria; no verifica rate limiting ni cambia configuración persistente del backend. La autorización cubre únicamente el uso local supervisado de estos helpers, no un sandbox para SQL arbitrario.

Las suites predeterminada y `--safety` usan datos ficticios en memoria, sin SQL. La integración usa fixtures propios persistentes y limpieza explícita. Las instrucciones de herramientas/sistema están en [SYSTEM.md](SYSTEM.md); recorridos y evaluación completados con fallos registrados, no aprobación íntegra. No se envían mensajes ni se prueban tokens, IA, RAG o notificaciones.

## Ejecutar integración real optativa

Solo desde un proceso separado y con la aplicación local inactiva. Se reutiliza la configuración existente del backend; no se copia la conexión ni se registra su contenido. Tras verificar el destino se solicita la frase exacta mostrada. No hay argumento de aceptación automática y no se debe canalizar una respuesta predefinida al comando.

```powershell
$report = '.\docs\specs\spec-001-tests\evidence\integration-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.txt'
& .\testing\.venv\Scripts\python.exe -m testing.run_tests --integration --report $report
$testExitCode = $LASTEXITCODE
if ($testExitCode -ne 0) { throw "Integración incompleta: código $testExitCode. Revisar reporte y registros de propiedad." }
```

`--integration` y `--safety` son excluyentes. Sin flags permanece la suite de 23 algoritmos; importar la definición de integración no lee secretos ni conecta. El modo optativo carga solamente los cuatro casos obligatorios y usa SQL real, no SQLite ni mocks de consultas. Cada caso prepara sus datos; I-4 prepara cinco conjuntos independientes para las variantes de matrícula.

Se conservan reporte saneado y un registro durable por conjunto. Se registran resultados esperados/obtenidos, commits propios y limpieza; el token y las contraseñas viven solo en memoria. Los logs privados y tracebacks SQL se suprimen; fallos de aserción/driver se identifican por tipo/caso sin parámetros. Si falla un caso, una omisión obligatoria, la autorización o la limpieza, el proceso devuelve código no satisfactorio. Cero casos no constituye aprobación. Si hay residuos, usar el comando `cleanup` con el registro y confirmar nuevamente el destino; no borrar manualmente por prefijos.

Ejecución T18: I-1…I-4 aprobadas sobre **RASTONE-PC / Tutoria-demo** tras confirmación expresa; ocho conjuntos limpiados y verificación posterior en lectura de 97 recursos/intenciones sin filas restantes. Resumen en [evidence.md](../docs/specs/spec-001-tests/evidence.md#integración-sql-real-t15t18-2026-09-30). Una ejecución de integración no comprueba frontend, servidor HTTP de red, login o sistema manual. Crear/borrar datos puede dejar huecos de IDENTITY; no se reinician secuencias compartidas.

Los resultados, grafos y checklist se conservarán en el registro de cada spec, sin credenciales. Documentar cómo usar una herramienta no equivale a ejecutar las pruebas.

## Preparar y verificar sistema manual, solo cuando se autorice

Leer primero [SYSTEM.md](SYSTEM.md): pasos, datos, registro textual de observaciones confirmadas por el operador, resultados **esperados** y límites; no se exigen capturas de pantalla. Los comandos son instrucciones de uso, **no evidencia de ejecución**. El seguimiento distingue qué operaciones se realizaron; unittest no arranca servidores ni prepara datos.

Cada comando SQL verifica el destino y pide nueva confirmación exacta. Preparar un conjunto independiente para cada uno de `S-1`, `S-2`, `S-3`, `S-3b`, con la aplicación detenida. Usar una contraseña ficticia temporal elegida por el operador mediante entrada oculta; no introducirla como argumento, variable de entorno, respuesta capturada ni archivo de credenciales.

```powershell
& .\testing\.venv\Scripts\python.exe -m testing.run_system prepare --case S-2
$operationCode = $LASTEXITCODE
if ($operationCode -ne 0) { throw 'Preparación incompleta; revisar reporte y registro.' }
```

Cambiar el caso solo cuando vaya a realizarse su recorrido. El comando imprime emails ficticios, ID de curso, ruta del journal y, en S-2, ruta del Excel temporal; no contraseñas. Las reservas preceden a operaciones UI. El Excel tiene encabezado y dos filas: nueva cuenta y estudiante existente sin matrícula; contraseña solo en la fila nueva. Está fuera de evidencia y excluido por Git; **no se cifra ni constituye un almacén de secretos**. Mantenerlo local sin compartirlo y eliminarlo al terminar. No se agregaron dependencias.

Tras el recorrido, usar el journal **real impreso por el preparador**; `$ownership` es un ejemplo con marcador, no una ruta existente:

```powershell
$ownership = '.\docs\specs\spec-001-tests\evidence\<UUID-real>\ownership.json'
& .\testing\.venv\Scripts\python.exe -m testing.run_system verify --ownership $ownership
$operationCode = $LASTEXITCODE
if ($operationCode -ne 0) { throw 'Datos distintos del resultado esperado; registrar la desviación.' }
```

`verify` lee SQL y registra únicamente IDs previstos ya confirmados por la aplicación. Comprueba cuentas, identidad reutilizada, matrículas, sesiones y cero mensajes; **nunca aprueba la UI**. Registrar por separado la confirmación del operador sobre resultado UI y status/valores JSON observados, sin exigir capturas de pantalla: SQL satisfactorio no demuestra 409 ni los contadores HTTP `created/enrolled/skipped`.

S-1/S-2 reservan también la configuración predeterminada que la pantalla crea automáticamente. Si el conjunto se preparó antes de esa extensión y **aún no se abrió el curso**, usar la misma ruta real:

```powershell
& .\testing\.venv\Scripts\python.exe -m testing.run_system reserve-config --ownership $ownership
$operationCode = $LASTEXITCODE
if ($operationCode -ne 0) { throw 'No abrir el curso: reserva no completada; investigar.' }
```

Requiere nueva confirmación, verifica propiedad/ausencia de la configuración en SQL y escribe solo la reserva durable. No crea configuración ni la atribuye si ya existe, ni reserva duplicados. Configuración del curso propio con PK `curso_id` se limpia explícitamente antes del curso; no se prueba IA ni se borran configuraciones ajenas. La extensión está autorizada por el operador y comprobada en 53 controles y una regresión de 23 ([resumen](../docs/specs/spec-001-tests/evidence.md#suite-aislada-y-controles-simulados)).

Para S-3b, preparar su conjunto sin matrícula, iniciar la aplicación y ejecutar el complemento de red (no test_client):

```powershell
& .\testing\.venv\Scripts\python.exe -m testing.run_system deny-http --ownership $ownership --origin http://localhost:5000
$operationCode = $LASTEXITCODE
if ($operationCode -ne 0) { throw 'Contrato HTTP/SQL no satisfactorio; revisar reporte saneado.' }
```

Hace login real con contraseña oculta y comprueba identidad del fixture. Solo acepta HTTP loopback con puerto explícito, sin rutas/credenciales, proxies de entorno ni redirects. JWT solo en memoria: el reporte conserva status y coincidencia con el mensaje esperado, no cabeceras ni respuesta privada del login. No suministrar tokens por terminal/argumentos.

Al finalizar o abandonar **cada** escenario, cerrar sesión, detener la aplicación y recuperar por journal:

```powershell
& .\testing\.venv\Scripts\python.exe -m testing.run_system cleanup --ownership $ownership
$operationCode = $LASTEXITCODE
if ($operationCode -ne 0) { throw 'Limpieza incompleta: revisar filas/Excel residuales.' }
```

Intenta retirar el Excel incluso si SQL se bloquea; no borra archivos inesperados de su carpeta. Tras commit verifica ausencia en una conexión nueva de lectura. Si SQL está limpio pero el Excel permanece abierto, cerrar el editor y repetir. Conservar journal/reportes; la limpieza genérica de datos locales no elimina el Excel de sistema. Código 1 o artefacto no verificable exige investigación.

Reportes optativos: UTC, commit, cambios locales, huellas, destino, operación, resultados saneados y código, sin tracebacks privados. Soporte comprobado con 46 controles y 23 casos aislados ([resumen](../docs/specs/spec-001-tests/evidence.md#suite-aislada-y-controles-simulados)); no sustituye sistema real.