# Procedimiento local de sistema — SPEC-001

**Estado:** T19–T22 completadas; S-1/S-3/S-3b aprobados, S-2 fallido con S-001 abierto y corrección diferida fuera de esta spec. Cuatro conjuntos limpiados y Excel eliminado; servidores detenidos. [Resultados reales](../docs/specs/spec-001-tests/evidence.md#sistema-manual-t19t22-2026-09-30). El procedimiento por sí solo no acredita aprobación; no se exigen capturas de pantalla.

## 1. Preparación y herramientas

Usar el entorno independiente y las instrucciones de [README.md](README.md). unittest/unittest.mock son biblioteca estándar; los ejecutores seleccionan explícitamente aislamiento, controles o integración. No ejecutar discovery general contra los módulos: la integración requiere autorización separada. `FAIL` es una aserción incumplida; `ERROR`, una excepción inesperada; `skipped`/`expectedFailure` no acreditan los casos obligatorios. Cero tests o código distinto de cero impiden aprobar la ejecución.

Los tres grafos están en [el registro](../docs/specs/spec-001-tests/test.md). Abrir su vista previa en un visor Markdown compatible con Mermaid o copiar exclusivamente un bloque Mermaid al visor integrado. No instalar dependencias en el frontend ni enviar datos privados a visores públicos. El grafo y la trazabilidad justifican caminos seleccionados; unittest no calcula cobertura de caminos ni certifica el MVP.

Desde PowerShell en la raíz, este **ejemplo de procedimiento, no resultado real**, conserva stdout/stderr y el código inmediatamente después del proceso:

```powershell
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$report = ".\docs\specs\spec-001-tests\evidence\isolated-$stamp.txt"
$capture = ".\docs\specs\spec-001-tests\evidence\console-$stamp.txt"
& .\testing\.venv\Scripts\python.exe -m testing.run_tests --report $report 2>&1 | Tee-Object -FilePath $capture
$testExitCode = $LASTEXITCODE
"Código de proceso: $testExitCode" | Add-Content -Path $capture
if ($testExitCode -ne 0) { throw 'Ejecución incompleta: revisar el reporte.' }
```

No derivar éxito de `$?` de `Tee-Object` ni de la mera existencia del archivo. La captura sirve para el ejecutor aislado saneado: **no capturar terminales con contraseñas, logs SQL crudos, cabeceras de login ni tokens**. En integración usar el reporte saneado de `--integration`, no exportaciones generales de logs.

## 2. Autorización y recursos

La aplicación debe usar el mismo SQL Server local verificado por el preparador. La última integración usó RASTONE-PC / Tutoria-demo, pero **ese permiso no autoriza sistema**: cada preparación/verificación/recuperación revalida configuración e identidad y pide escribir exactamente `AUTORIZO <etiqueta actual>`. No copiar conexiones ni modificar configuración de aplicación. No ejecutar esquema, seed, migraciones o reset de IDENTITY.

Preparar con frontend/backend detenidos y sin otros escritores. Para los recorridos iniciar el backend existente en modo local y el frontend con su script `dev`, solo en loopback, usando los mismos parámetros de conexión existentes. El frontend usa `VITE_API_URL` o `http://localhost:5000/api`; Vite no tiene proxy configurado. Comprobar el origen realmente usado en el navegador y los puertos, no asumir que disponibilidad HTTP prueba el destino SQL. No conservar contraseña ni token en capturas. Al terminar cerrar sesión, limpiar el almacenamiento de ese origen y cerrar la pestaña.

El preparador solicitará una contraseña ficticia con entrada oculta, confirmación y validación existente. El operador la conserva únicamente durante el recorrido; no se imprime ni guarda un archivo de credenciales. El Excel temporal sí contiene la contraseña de la cuenta nueva: no abrirlo en un visor compartido, adjuntarlo a evidencia ni versionarlo. Vive en una carpeta local ignorada, asociada al UUID del registro. Detener recorridos si se pierde el registro; no continuar creando filas fuera del alcance reservado.

Cada escenario tiene institución/plan/suscripción/cuentas/curso propios. Los IDs y marcas previstos se conservan en el journal sin secretos. S-2 necesita reservar una matrícula **antes** del importador que genera el UUID del usuario: su marca operacional usa `user_email` exclusivo y `curso_id` propio. La recuperación resuelve primero el usuario por email **y** institución propios y luego usa su ID SQL; no busca por prefijos, no adopta cuentas existentes ni amplía el esquema del producto. Esta variante solo se acepta en registros `system` y exige un usuario reservado en el mismo journal.

**Ajuste autorizado durante el recorrido guiado:** abrir el detalle del curso ejecuta automáticamente GET del agente y el backend crea su configuración predeterminada si falta. No se prueba IA, pero esa fila debe tener reserva previa para permitir limpieza segura. S-1/S-2 reservan `configuracion_ia` por su PK `curso_id` propio, sin copiar prompt ni parámetros al journal. Se comprueban PK/FK/permisos/triggers y se borra explícitamente antes del curso; configuraciones no registradas o de otros cursos siguen bloqueadas/preservadas. Para un fixture preparado antes de esta extensión usar `reserve-config` **antes** de abrir el detalle: revalida destino y curso en lectura, rechaza configuración preexistente sin reserva y actualiza solo el journal. El operador aprobó esta ampliación del soporte, sin modificar producto/esquema.

### Arranque futuro, sin cambios de aplicación

Después de preparar datos, abrir dos terminales PowerShell en la raíz. Son **comandos de uso**, no un arranque ejecutado. Deben existir dependencias del frontend y configuración local vigente del backend; si faltan, registrar bloqueo. No instalar paquetes en el backend ni copiar secretos. Los ajustes efímeros evitan almacenamiento externo del limitador y se restauran al detenerlo; no se prueba rate limiting.

Terminal de backend:

```powershell
$oldLimiter = $env:RATELIMIT_STORAGE_URI
$oldProxy = $env:TRUSTED_PROXY_COUNT
$oldDebug = $env:FLASK_DEBUG
Push-Location .\backend
try {
	$env:RATELIMIT_STORAGE_URI = 'memory://'
	$env:TRUSTED_PROXY_COUNT = '0'
	$env:FLASK_DEBUG = '0'
	& ..\testing\.venv\Scripts\python.exe -m flask --app app:create_app run --host 127.0.0.1 --port 5000 --no-reload --no-debugger
} finally {
	Pop-Location
	$env:RATELIMIT_STORAGE_URI = $oldLimiter
	$env:TRUSTED_PROXY_COUNT = $oldProxy
	$env:FLASK_DEBUG = $oldDebug
}
```

Terminal de frontend:

```powershell
$oldApiUrl = $env:VITE_API_URL
Push-Location .\frontend
try {
	$env:VITE_API_URL = 'http://localhost:5000/api'
	node .\node_modules\vite\bin\vite.js --host localhost --port 5173 --strictPort
} finally {
	Pop-Location
	$env:VITE_API_URL = $oldApiUrl
}
```

La invocación directa ejecuta el mismo Vite del script `dev`, evitando la pérdida de argumentos observada con npm en PowerShell. El origen API queda restringido al backend local únicamente en ese proceso.

Abrir `http://localhost:5173`; liveness está en `http://localhost:5000/healthz` (no `/api/healthz` en Flask directo). Puerto ocupado, CORS/origen incompatible o destino distinto bloquean el recorrido; no cambiar código para ocultarlo. Detener terminales con Ctrl+C antes de limpieza; no conservar logs generales como evidencia.

## 3. Recorridos y evidencia exigida

| Caso | Datos independientes | Acción manual | Resultado esperado, no observado |
|---|---|---|---|
| S-1 | Coordinador + estudiante activos; límite 2; curso sin matrículas; email de alta reservado | Login del coordinador → Cursos → Ajustes del curso propio → Alumnos → Añadir alumno. Introducir email previsto y nombre/apellido/teléfono ficticios para elegir alta, más contraseña temporal | POST de estudiantes: 409 y mensaje de límite; SQL conserva dos usuarios y cero altas/matrículas nuevas |
| S-2 | Coordinador + estudiante existentes; límite 4; curso sin matrículas; Excel con una cuenta nueva y el estudiante existente | Login del coordinador de S-2 → curso propio → Alumnos → Añadir alumno → Importar desde Excel. Elegir archivo temporal y pulsar Importar alumnos una sola vez | 200; created=1, enrolled=2, skipped=[]; tres cuentas; mismo ID del estudiante reutilizado; dos matrículas activas |
| S-3 | Coordinador + estudiante matriculado; límite 4; curso con una matrícula activa | Login del estudiante de S-3 → Asistente → seleccionar curso propio → Abrir conversación **una sola vez** | 201; Nueva Conversación visible; una sesión persistida para el usuario/curso y cero mensajes |
| S-3b | Conjunto propio de conversación pero sin matrícula | Solicitud HTTP local con token válido obtenido por login y conservado solo en memoria; no requiere ni sustituye recorrido UI | 403, mensaje de falta de inscripción; cero sesiones/mensajes |

No enviar mensajes, renombrar conversaciones, usar práctica, recursos, RAG o notificaciones. No reutilizar el mismo conjunto para repetir una alta/importación/conversación: registrar la desviación y limpiar antes de preparar otro.

Con herramientas de desarrollo, observar **status y valores JSON de respuesta** de la petición concreta. Registrar en texto la confirmación del operador sobre el resultado en la interfaz y esos valores, más el reporte SQL de recursos propios. No se exigen capturas de pantalla ni exportar HAR, request, payload con contraseña, cookies o cabeceras. No repetir una operación solo para obtener evidencia visual. La observación comunicada se identifica como tal; la verificación SQL o el cliente Flask por sí solos no acreditan interfaz ni los valores HTTP observados manualmente.

Registrar UTC, commit, cambios locales/huellas, UUID y destino saneado del preparador, navegador/origen cuando se conozca (no inventarlo), caso, pasos realmente realizados, esperado, obtenido, confirmación del operador y status/valores HTTP observados, verificación SQL, código de proceso y limpieza. Para S-3b conservar el reporte HTTP saneado. Si no se efectuó el recorrido, mantener `no ejecutado`; si contradice el contrato, `fallido`. No convertir una comprobación documental en aprobación funcional. Notificar el defecto y documentar decisión de investigar/diferir sin modificar frontend/backend ni reinterpretar la spec.

## 4. Limpieza y recuperación

Detener la aplicación antes de limpiar: las comprobaciones usan bloqueos exclusivos locales breves. Usar el registro exacto y nueva confirmación del destino. La limpieza identifica filas por propiedad, inventaría FK entrantes y bloquea ante mensajes/dependencias inesperadas; no borra datos ajenos ni roles compartidos. El journal permanece como evidencia aunque el Excel se elimina. Si un editor mantiene abierto el Excel y bloquea su eliminación, cerrar el editor y repetir; **SQL limpio con Excel residual no es limpieza completa**.

Una interrupción requiere recuperar cada journal indicado; no limpiar todas las ejecuciones por prefijo. Si no se conserva la contraseña, abandonar el recorrido y limpiar, no restablecer cuentas ajenas. Los huecos de IDENTITY son posibles y no se corrigen. Tras limpieza, una nueva conexión de lectura debe confirmar ausencia de recursos propios y verificar que el Excel/carpeta temporal ya no existen. No borrar capturas/reportes saneados.

Los comandos de preparación, verificación y limpieza se documentan junto con su soporte en [README.md](README.md). La disponibilidad del soporte no cumple T20 mientras no existan los datos autorizados, Excel y aplicación local; T21/T22 requieren ejecuciones/evidencias reales.