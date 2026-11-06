# Evidencia de SPEC-001

Resumen único de las ejecuciones y revisiones que respaldan [test.md](test.md). Los reportes crudos (salida de unittest, preparación/verificación/limpieza SQL y journals de propiedad) se retiraron el 2026-10-31 por decisión del responsable; aquí solo se conservan fecha, modalidad, conteos y resultado. Commit de referencia: `6b7b79bbfdbea5614ffe369330e55905fffe3c98`. Los resultados no certifican el MVP: RF-5 (S-001) y RNF-6 (H-004) siguen fallidos.

Las ejecuciones se repiten con `python -m testing.run_tests`, `--safety`, `--integration` o `testing.run_system`; los reportes que generen son locales y no se versionan (ver [testing/README.md](../../../testing/README.md)).

## Preparación T1–T3 (2026-09-30)

Entorno propio dentro de `testing/`, Python 3.13.2, dependencias por referencia al backend y `pip check` sin conflictos. Grafos de flujo, 18 caminos base y casos derivados definidos. Revisión documental, no prueba funcional.

## Suite aislada y controles simulados

| Fecha | Modalidad | Resultado |
|---|---|---|
| 2026-09-30 | 23 pruebas aisladas (T9, regresiones T14, sistema, T24) | 0 fallos, errores u omisiones; aislamiento restaurado; código 0 |
| 2026-09-30 | Controles simulados de seguridad (31 en T14, 46 en T19–T22, 51–53 posteriores) | Todos aprobados; la primera ejecución de T14 (26 métodos) tuvo 1 fallo y 4 errores del harness, corregidos antes de aprobar |
| 2026-10-31 | 23 aisladas, run `66e3a0b9-0a62-440a-b98f-4e448c163c2b`, UTC 22:46:43 | 0 fallos; restaurado; código 0 |
| 2026-10-31 | 53 controles, UTC 22:50:47 | 0 fallos; restaurado; código 0 |

SQL, HTTP y lectura de secretos reales estuvieron bloqueados en todas estas ejecuciones; los mocks no acreditan SQL real. Orden inverso de la suite aislada comprobado (RNF-3). Huellas SHA-256 de los algoritmos evaluados: ver tabla de [test.md](test.md#1-identificación-y-alcance).

### Fallos de construcción tratados

- **Harness T10–T14:** el doble de conexión no exponía el dialecto MSSQL y un escenario de interrupción asumía hijos sin padre registrado. Se corrigió el soporte; no se relajó ninguna condición de propiedad ni se tocó producto. Además, `UNIQUEIDENTIFIER(as_uuid=True)` falla al enlazar cadenas UUID del journal; se usaron columnas con `as_uuid=False` solo en el helper de limpieza (test `test_T13_reflected_uuid_columns_accept_journal_strings`).
- **H-003 (resuelto):** dos `IndentationError` en el soporte de sistema antes de cargar suites; sin SQL ni reportes asociados.

## Integración SQL real (T15–T18, 2026-09-30)

Destino confirmado: RASTONE-PC / Tutoria-demo, con confirmación expresa del operador. Ejecución `35cb50cd-5c57-4b82-a8a9-69a8af56fe48`, 4 casos, 0 fallos, duración 41.847 s. Cliente Flask en proceso, decoradores JWT/rol, modelos y SQL Server reales; sin servidor de red ni frontend.

- **I-1:** capacidad 3 permite, 2 rechaza, NULL permite; el conteo excluye cuentas inactivas y ajenas.
- **I-2:** alta con conteo 3→4; reutilización por email normalizado devuelve la misma identidad, una fila.
- **I-3:** conflicto institucional, rol incompatible y capacidad agotada producen las excepciones previstas, sin duplicados.
- **I-4:** matrícula activa permite dos sesiones (201, título por defecto y explícito); ausente, inactiva, otro curso y otro usuario devuelven 403 sin alta.

Limpieza: ocho conjuntos `cleaned`; lectura independiente postcommit comprobó 97 recursos o intenciones y cero filas propias restantes. Puede haber huecos en contadores IDENTITY. No se ejecutó seed, DDL, IA, RAG ni notificaciones.

## Sistema manual (T19–T22, 2026-09-30)

Cuatro conjuntos independientes, cada uno con preparación, verificación SQL, limpieza y nueva autorización exacta del destino. Backend y frontend locales solo en loopback, con ajustes efímeros; sin cambios de producto. Contraseñas introducidas por el operador en entrada oculta. La evidencia manual es la observación confirmada del operador más la verificación SQL; no se exigen capturas por ajuste autorizado.

| Caso | Resultado | Hechos |
|---|---|---|
| S-1 | Aprobado | Alta rechazada con mensaje y 409; SQL: dos usuarios, cero altas, matrículas, sesiones y mensajes |
| S-2 | **Fallido** (S-001) | Al importar el Excel propio aparece «selecciona un archivo de Excel»; SQL: cero altas y matrículas. `CursoDetalleView.vue` trata como arreglo el primer File que Vuetify devuelve sin `multiple` y retorna antes del HTTP |
| S-3 | Aprobado | Sesión visible/201; SQL: una matrícula activa, una sesión propia, cero mensajes |
| S-3b | Aprobado | HTTP real 403 con mensaje esperado; sin matrícula, sesión ni mensajes; token solo en memoria |

Decisión del responsable: no corregir bugs dentro de esta spec; S-001 queda abierto. Los cuatro journals terminaron `cleaned` y la lectura independiente confirmó cero recursos propios; Excel y carpetas temporales eliminados. S-3b usó una identidad propia validada antes del POST.

La compatibilidad del soporte extendido (usuario/matrícula con UUID generados por el importador, `user_email` ficticio exclusivo, solo modo `system`) se comprobó únicamente con controles simulados; la integración SQL histórica no se repitió con ese soporte.

## Evaluación final T23–T24 (2026-09-30)

- Regresión aislada final: 23 pruebas; controles finales: 53; `pip check` sin conflictos; 17 archivos Python analizados con AST sin errores.
- Doce journals (ocho de integración y cuatro de sistema) en `cleaned`, sin errores de limpieza, recursos `deleted`.
- Diff contra HEAD vacío para frontend, backend, database, automation y compose; puertos 5000/5173 sin listeners.
- 52 archivos públicos revisados por patrones: cero coincidencias de JWT, claves privadas o asignaciones largas de claves. No es una certificación exhaustiva de secretos.
- **RF-1/2/3/4/6/7/8/9/10/11 y RNF-1/2/3/4/5/7:** aprobados solo en el alcance evaluado. **RF-5 (S-001) y RNF-6 (H-004):** fallidos. RNF-6: `testing/run_tests.py` imprime en inglés sus mensajes propios (Summary, Isolation state restored, Cleanup).
- Continuidad de regresión: [REGRESSION.md](../../../testing/REGRESSION.md).
