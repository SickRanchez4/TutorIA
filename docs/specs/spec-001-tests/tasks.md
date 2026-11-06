# Tareas de SPEC-001 — Pruebas esenciales de TutorIA

**Referencias:** [spec.md](spec.md) y [plan.md](plan.md), aprobados; [Constitución](../constitution.md).  
**Estado:** T1–T24 completadas como trabajo de pruebas y evaluación. RF-5/RNF-6 fallidos y S-001/H-004 abiertos; sin reparación del producto. Integración y cuatro conjuntos de sistema limpiados. [Evaluación final](evidence.md#evaluación-final-t23t24-2026-09-30). Completar tareas no equivale a aprobar todos los requisitos.

Las tareas están ordenadas por dependencia. Solo se marcarán al cumplir su condición verificable. Si falta un recurso, falla una comprobación o se necesita modificar frontend/backend, registrar el bloqueo y notificar al responsable; no marcar la tarea como hecha ni ampliar el alcance sin aprobación.

**Seguimiento posterior al aplazamiento:** cuatro conjuntos preparados, casos ejecutados y resultados/defecto registrados; limpieza y retirada de Excel verificadas. S-1/S-3/S-3b aprobados y S-2 fallido, corrección diferida por decisión del operador. Observación manual confirmada y reporte SQL sustituyen capturas por ajuste autorizado. [Seguimiento actual](evidence.md#sistema-manual-t19t22-2026-09-30).

## 1. Preparación y documentación inicial

- [x] **T1 — Crear el proyecto independiente de pruebas.**
	**RF:** RF-1, RF-8. **Depende de:** ninguna.  
	**Hecho cuando:** existe la estructura mínima de `testing/` prevista por el plan, con dependencias por referencia, entorno propio e instrucciones de preparación; no se modificaron frontend ni backend ni se añadieron frameworks de pruebas.

- [x] **T2 — Crear el registro central de pruebas.**
	**RF:** RF-2, RF-7, RF-9. **Depende de:** T1.  
	**Hecho cuando:** la carpeta de esta spec contiene `test.md` con alcance, versión, checklist de RF-1 a RF-11 y RNF, columnas de resultados/evidencias/defectos y todos los casos pendientes como «no ejecutado».

- [x] **T3 — Documentar los tres grafos y caminos.**
	**RF:** RF-2, RF-3. **Depende de:** T2.  
	**Hecho cuando:** el registro incluye tres grafos Mermaid renderizables, vinculados con las funciones reales, convención, nodos/aristas, cálculo de complejidad y los 18 caminos base del plan con entradas y resultados esperados; cualquier discrepancia con la versión fuente está resuelta o bloqueada explícitamente.

## 2. Aislamiento y casos de camino básico

- [x] **T4 — Preparar importaciones y contextos aislados.**
	**RF:** RF-1, RF-10. **Depende de:** T1.  
	**Hecho cuando:** se importa la lógica existente en el orden previsto, se crean solo los contextos Flask necesarios, no se leen secretos del backend ni se accede a SQL/servicios externos y las sustituciones se restauran incluso ante un fallo.

- [x] **T5 — Implementar pruebas aisladas de capacidad.**
	**RF:** RF-2, RF-3, RF-4. **Depende de:** T3, T4.  
	**Hecho cuando:** A1-P1 a A1-P5 y las variantes esenciales de configuración, actividad, vigencia y capacidad tienen pruebas identificables, aserciones de contrato y explicación de propósito; los conteos simulados no se presentan como integración real.

- [x] **T6 — Implementar pruebas aisladas de estudiantes.**
	**RF:** RF-2, RF-3, RF-5. **Depende de:** T3, T4.  
	**Hecho cuando:** A2-P1 a A2-P8 verifican alta, reutilización y excepciones; se comprueba normalización del email, identidad/rol institucional y add/flush sin commit, sin copiar reglas ni eliminar roles reales.

- [x] **T7 — Implementar pruebas aisladas de conversaciones.**
	**RF:** RF-2, RF-3, RF-6. **Depende de:** T3, T4.  
	**Hecho cuando:** A3-P1 a A3-P5 verifican cuerpos, status, títulos y commit/rollback; el error de persistencia se provoca de forma controlada y se declara que esta modalidad no prueba decoradores ni SQL real.

- [x] **T8 — Implementar la ejecución aislada predeterminada.**
	**RF:** RF-1, RF-8, RF-9, RF-10. **Depende de:** T5, T6, T7.  
	**Hecho cuando:** el ejecutor descubre solo las pruebas aisladas por defecto, identifica casos/resultados y devuelve estado no satisfactorio ante fallos u omisiones obligatorias; no activa integración ni carga su conexión accidentalmente.

- [x] **T9 — Ejecutar y registrar las pruebas aisladas.**
	**RF:** RF-1, RF-3, RF-4, RF-5, RF-6, RF-7, RF-9, RF-10. **Depende de:** T8.  
	**Hecho cuando:** se conserva un reporte real con fecha/versión, resultados de los 18 caminos y variantes, código de salida y comprobación de aislamiento/restauración; el checklist refleja los resultados y cualquier fallo tiene tratamiento documentado conforme a PUDS.

## 3. Seguridad, datos propios y limpieza

- [x] **T10 — Implementar la autorización del destino local.**
	**RF:** RF-1, RF-10. **Depende de:** T4.  
	**Hecho cuando:** la modalidad optativa de integración carga la configuración existente antes de importar la fábrica, valida localidad/identidad/esquema en lectura y exige confirmación; conflictos de conexión, destino no verificable o confirmación ausente bloquean escrituras sin revelar secretos.

- [x] **T11 — Implementar el registro durable de propiedad.**
	**RF:** RF-7, RF-9, RF-10. **Depende de:** T2, T10.  
	**Hecho cuando:** el JSON mínimo definido en el plan registra marcas previstas antes de crear datos e IDs después del commit, se actualiza por reemplazo y permite identificar recursos de una ejecución interrumpida sin incluir credenciales, tokens o contraseñas.

- [x] **T12 — Preparar fixtures ficticios independientes.**
	**RF:** RF-4, RF-5, RF-6, RF-10. **Depende de:** T11.  
	**Hecho cuando:** se pueden preparar los recursos mínimos de cada caso con identidad exclusiva, fechas controladas y campos obligatorios; los roles existentes son de solo lectura y no se ejecutan seed, creación de tablas, migraciones ni llamadas de IA.

- [x] **T13 — Implementar limpieza y recuperación.**
	**RF:** RF-9, RF-10. **Depende de:** T12.  
	**Hecho cuando:** la limpieza respeta el orden de claves foráneas, registra residuos y se intenta ante fallos parciales; la recuperación revalida destino/confirmación y solo borra recursos atribuibles a la ejecución, sin depender de un rollback global ni borrar roles compartidos.

- [x] **T14 — Verificar bloqueos y limpieza controlada.**
	**RF:** RF-1, RF-9, RF-10. **Depende de:** T13.  
	**Hecho cuando:** existen resultados registrados para bloqueo sin autorización/destino válido, fallo durante preparación, recuperación desde el registro y negativa a borrar recursos ajenos o no atribuibles; las verificaciones simuladas se distinguen de las efectuadas sobre SQL local.

Evidencia de la sección 3: [31 controles simulados, regresión de 23 casos y tratamiento de fallos](evidence.md#suite-aislada-y-controles-simulados). Esta evidencia no sustituye SQL local real.

## 4. Integración real local

- [x] **T15 — Implementar integración de capacidad.**
	**RF:** RF-4, RF-9, RF-10. **Depende de:** T5, T14.  
	**Hecho cuando:** I-1 consulta SQL Server real con fixtures propios y comprueba capacidad inferior/alcanzada/ilimitada, incluyendo que cuentas inactivas o de otra institución no suman; el caso tiene limpieza registrada.

- [x] **T16 — Implementar integración de estudiantes.**
	**RF:** RF-5, RF-9, RF-10. **Depende de:** T6, T14.  
	**Hecho cuando:** I-2 e I-3 comprueban alta y reutilización con persistencia real, rechazos de otra institución/rol incompatible/capacidad agotada y ausencia de duplicados; el llamador controla transacciones y usa datos independientes.

- [x] **T17 — Implementar integración de conversaciones.**
	**RF:** RF-6, RF-9, RF-10. **Depende de:** T7, T14.  
	**Hecho cuando:** I-4 utiliza la fábrica, decoradores y cliente Flask reales con SQL local; comprueba 201/403 y persistencia para matrícula activa, ausente, inactiva, de otro curso o usuario, sin enviar mensajes ni simular componentes declarados integrados.

- [x] **T18 — Ejecutar y registrar la integración.**
	**RF:** RF-4, RF-5, RF-6, RF-7, RF-9, RF-10. **Depende de:** T15, T16, T17.  
	**Hecho cuando:** I-1 a I-4 se ejecutaron en un proceso separado y destino confirmado; el reporte identifica versión, resultados y limpieza comprobada en SQL, y el checklist registra cualquier fallo/omisión y la decisión del responsable sin declarar requisitos afectados como aprobados.

Evidencia de la sección 4: [I-1…I-4 sobre SQL real y limpieza posterior](evidence.md#integración-sql-real-t15t18-2026-09-30), con ocho conjuntos limpiados, 97 intenciones revisadas y cero filas propias restantes. Sistema aún no ejecutado al cerrar T18; resultados posteriores en sección 5.

## 5. Herramientas y sistema

- [x] **T19 — Documentar herramientas y procedimientos.**  
	**RF:** RF-7, RF-8, RF-10. **Depende de:** T8, T13, T15, T16, T17.  
	**Hecho cuando:** las instrucciones explican preparación propia, uso de unittest y Mermaid, comandos PowerShell, captura de salida/código de proceso, confirmación local, recuperación y límites; los ejemplos esperados no se presentan como evidencia real.

- [x] **T20 — Preparar los escenarios de sistema.**
	**RF:** RF-4, RF-5, RF-6, RF-9, RF-10. **Depende de:** T18, T19.  
	**Hecho cuando:** S-1, S-2, S-3 y S-3b tienen pasos, datos ficticios registrados, resultados esperados y limpieza; se dispone del Excel temporal de dos filas y la aplicación local, sin editar frontend/backend ni publicar contraseñas.

- [x] **T21 — Ejecutar rechazo e importación en sistema.**
	**RF:** RF-4, RF-5, RF-7, RF-9, RF-10. **Depende de:** T20.  
	**Hecho cuando:** S-1 y S-2 se recorrieron en la aplicación local y tienen observación manual confirmada por el operador (resultado UI y status/valores HTTP observados) y reporte SQL de comprobación de datos, sin exigir capturas de pantalla; se documentan 409 sin alta y created=1/enrolled=2/skipped vacío como resultados esperados, registrando cualquier diferencia y su tratamiento.

- [x] **T22 — Ejecutar conversaciones y limpiar sistema.**
	**RF:** RF-6, RF-7, RF-9, RF-10. **Depende de:** T21.  
	**Hecho cuando:** S-3 tiene observación manual confirmada por el operador y reporte SQL, sin exigir capturas de pantalla; S-3b tiene reporte HTTP saneado y comprobación SQL del rechazo sin matrícula, con token válido no expuesto y sin envío de mensajes; al finalizar se verificó la limpieza de datos propios y del Excel temporal o se registraron residuos y decisiones pendientes.

**Estado de la sección 5:** T19–T22 completadas como preparación, ejecución y registro de resultados, no como aprobación de todo el producto. [Seguimiento y resultados](evidence.md#sistema-manual-t19t22-2026-09-30): S-1/S-3/S-3b aprobados; S-2 fallido, con cero altas/matrículas frente al éxito esperado y S-001 abierto, corrección diferida expresamente fuera de esta spec. Cuatro conjuntos limpiados con lectura independiente postcommit y Excel eliminado. Capturas no exigidas según ajuste autorizado. Controles 53/53 y regresión 23/23 ([resumen](evidence.md#suite-aislada-y-controles-simulados)); cierre posterior en sección 6.

## 6. Continuidad y cierre

- [x] **T23 — Documentar regresión para futuras specs.**
	**RF:** RF-2, RF-8, RF-11. **Depende de:** T19.  
	**Hecho cuando:** se explica cómo seleccionar pruebas por requisitos/riesgo, reutilizar identificadores y evidencias y añadir solo casos esenciales; no se impone analizar otros tres algoritmos ni se implementa infraestructura futura.

- [x] **T24 — Evaluar requisitos y revisar el cambio.**
	**RF:** RF-1 a RF-11. **Depende de:** T3, T9, T14, T18, T19, T22, T23.  
	**Hecho cuando:** el registro contiene veredicto por RF/RNF con evidencia, defectos y decisiones; se revisó el diff para confirmar no intrusión, idioma y ausencia de secretos; ningún requisito fallido/no ejecutado se declara cumplido ni se certifica el resto del MVP.

## Trazabilidad resumida

Evidencia de sección 6: [regresión proporcional](../../../testing/REGRESSION.md), [evaluación final](evidence.md#evaluación-final-t23t24-2026-09-30) y [checklist final](test.md#L30). Suites actuales 23/23 y 53/53 conformes; RF-5/RNF-6 fallidos. T24 completa porque evalúa y registra incumplimientos, no porque todos los requisitos aprueben.

| RF | Tareas principales |
|---|---|
| RF-1 | T1, T4, T8, T9, T10, T14, T24 |
| RF-2 | T2, T3, T5, T6, T7, T23, T24 |
| RF-3 | T3, T5, T6, T7, T9, T24 |
| RF-4 | T5, T9, T12, T15, T18, T20, T21, T24 |
| RF-5 | T6, T9, T12, T16, T18, T20, T21, T24 |
| RF-6 | T7, T9, T12, T17, T18, T20, T22, T24 |
| RF-7 | T2, T9, T11, T18, T19, T21, T22, T24 |
| RF-8 | T1, T8, T19, T23, T24 |
| RF-9 | T2, T8, T9, T11, T13 a T18, T20 a T22, T24 |
| RF-10 | T4, T8 a T22, T24 |
| RF-11 | T23, T24 |

Los RNF y los seis principios constitucionales se revisan durante cada tarea y formalmente en T24. La redacción de estas tareas no autoriza ejecutarlas todas de una vez: la implementación seguirá las tareas que solicite el responsable.
