# Registro de pruebas — SPEC-002

**Estado vigente:** SPEC-002 funcionalmente completada con C1–C4 y C5 mínimo acordado, incluida muestra propia de Edge; **sin certificación integral**. T87 y T89–T98 diferidas. Lector real y partes extensas de zoom/móvil no ejecutadas, no bloqueantes.
**Actualización documental:** 2026-11-15. [Entrega actual](#7-entrega-funcional-acotada-2026-11-15) y [evidencia](evidence.md#cierre-funcional-acotado-de-spec-002-2026-11-15); se preserva la historia C0/refactor y el [contexto del proyecto](../../project-context.md).
**Versión histórica C0:** `6b7b79bbfdbea5614ffe369330e55905fffe3c98`, sin cambios de producto al iniciar C0. Versión de entrega actual: `565dd39` más cambios locales.
**Fecha histórica C0:** 2026-09-30 (capturas posteriores a medianoche UTC se identifican con su offset).
**Referencias:** [spec](spec.md), [plan](plan.md), [tareas](tasks.md), [inventario T02](inventory.md), [entorno T03](evidence.md#entorno-t03-2026-09-30).

## 1. Alcance y significado del resultado

C0 elabora inventario, entorno, casos y baseline lint/build. No implementa apariencia ni consume API/SQL/IA, no crea fixtures transaccionales y no ejecuta los casos UI-01 a UI-10. Revisión de código, comprobación numérica de paleta, lint/build, integración controlada, integración real y sistema se registran por separado.

**Aprobado:** todos los criterios aplicables del requisito tienen evidencia satisfactoria. **Fallido:** un criterio ejecutado no se cumple. **No ejecutado:** no se corrió o falta recurso/parte necesaria; si hay cobertura parcial, describirla sin convertirla en aprobación integral. **No aplicable:** exige justificación concreta, no equivale a pasar una prueba. Un caso puede estar ejecutado/fallido mientras la tarea de registro esté completada.

Al iniciar C0, T01 ya estaba marcada por el usuario y el plan conservaba cabecera propuesta. La autorización de aquella construcción cubría T02–T05, no C1 ni escrituras reales. Esta discrepancia se registró como C0-G01 y no se interpretó como aprobación del plan.

El 2026-10-31, durante la consolidación documental, el responsable seleccionó **«Apruebo el plan actual y su paleta»**. La [decisión](plan.md) respalda T01 y resuelve C0-G01 desde esta fecha; no acredita aprobación anterior, implementación, contraste ni pruebas UI/UX. Esta limpieza no autoriza C1–C5 ni operaciones SQL.

## 2. Recursos y protocolo

[Captura de entorno](evidence.md#entorno-t03-2026-09-30): Windows 11, i9-12900H, 31,69 GiB, Node 22.17.0/npm 10.9.2; Chrome y Edge detectados, canal y ejecución por confirmar. Firefox/NVDA no confirmados; Android/iOS sin recurso confirmado. Escala Windows y DPR no inferidos desde resolución física.

Referencia de rendimiento: build servido en loopback, Chrome local, 1440×900 CSS/zoom100 %, pestaña activa y configuración comprobada antes de medir; 20 repeticiones de cada interacción local fijada. No se ha abierto una app para medir ni se considera el dev server equivalente a producción.

Los [casos y matriz T04](cases.md) detallan precondiciones, pasos y aserciones de UI-01…UI-10. Datos ficticios, errores/retrasos y estados de tutor/RAG se presentarán mediante dobles claramente identificados; no se añadirá un modo mock permanente de producto. Destinos no controlados se bloquean antes de cualquier recorrido.

## 3. Plantilla obligatoria de evidencia por caso

| Campo | Contenido a registrar |
|---|---|
| ID / requisito / tarea | SPEC-002/UI-xx/caso; RF/RNF; Tnn y construcción |
| Versión | Commit, cambios locales y huellas de archivos afectados |
| Fecha y entorno | Fecha/hora con offset/UTC; OS/hardware relevante, navegador/canal/versión, lector/dispositivo, viewport CSS/zoom/DPR |
| Modalidad | Estática / cálculo / integración controlada / integración real / sistema; sustituciones exactas |
| Actor y contexto | Rol, tema, superficie Pxx, entidad ficticia propia; no credenciales |
| Precondiciones / datos | Estado inicial, respuestas/archivos ficticios, autorización y journal si aplica |
| Pasos | Acciones realmente ejecutadas, no copiar el procedimiento como si hubiera ocurrido |
| Esperado / obtenido | Aserciones y observación concreta; Network/status permitido sin tokens/HAR/filas privadas |
| Resultado | Aprobado/fallido/no ejecutado/no aplicable justificado; cobertura parcial explicada |
| Evidencia | Enlace a reporte/captura saneada/medición/observación confirmada; capturas opcionales |
| Defecto y decisión | ID, previo/nuevo, impacto, responsable y decisión literal cuando exista; no decidir por él |
| Limpieza | Journal propio, recuperación/residuos y comprobación posterior; o no aplicable sin datos |

## 4. Checklist individual inicial

**Instantánea histórica de C0:** la tabla siguiente se conserva como registro inicial; sus pendientes no describen el código vigente. La cobertura seleccionada posterior está en §7 y no convierte cada requisito en aprobación integral.

Cada fila se actualiza después de ejecutar los casos correspondientes. Las tareas de documentación C0 no aprueban RF-20 completo, que también exige catálogo construido y trazabilidad de evidencias posteriores.

| Requisito | Grupos previstos | Resultado | Evidencia funcional | Defectos / límites |
|---|---|---|---|---|
| RF-1 | UI-01, UI-09 | No ejecutado | — | Inventario estático no prueba apariencia inspiradora |
| RF-2 | UI-02 | No ejecutado | — | Selector/temas aún no implementados |
| RF-3 | UI-02 | No ejecutado | — | Persistencia/fallback nuevos aún no implementados |
| RF-4 | UI-02, UI-07, UI-08, UI-09 | No ejecutado | — | Solo dark actual y Mermaid claro fijo |
| RF-5 | UI-01 | No ejecutado | — | Contratos inventariados, migración pendiente |
| RF-6 | UI-03, UI-09 | No ejecutado | — | Guards existentes no son prueba de foco |
| RF-7 | UI-04 a UI-08 | No ejecutado | — | Estados/dobles por construir y ejecutar |
| RF-8 | UI-04, UI-09 | No ejecutado | — | Formularios por evaluar |
| RF-9 | UI-04, UI-07, UI-09 | No ejecutado | — | Dirty/foco/confirmaciones por evaluar |
| RF-10 | UI-03, UI-04, UI-07 | No ejecutado | — | No autenticación ni HTTP real en C0 |
| RF-11 | UI-05, UI-09 | No ejecutado | — | Listados y paginación por evaluar |
| RF-12 | UI-05 | No ejecutado | — | Corrección frontend previa a C1 comprobada con mock; S-2 real y criterios UI-05 pendientes |
| RF-13 | UI-06, UI-04 | No ejecutado | — | No RAG/IA real autorizado |
| RF-14 | UI-07 | No ejecutado | — | No mensajes o sesiones nuevos en C0 |
| RF-15 | UI-07, UI-09 | No ejecutado | — | Dictado real y permisos no comprobados |
| RF-16 | UI-07, UI-09 | No ejecutado | — | Fuente técnica no equivale a descripción accesible |
| RF-17 | UI-08, UI-09 | No ejecutado | — | Agenda/analíticas por evaluar |
| RF-18 | UI-04 a UI-09 | No ejecutado | — | Idioma de biblioteca/errores por evaluar |
| RF-19 | UI-09 | No ejecutado | — | Sin prueba de viewport/zoom/móvil/teclado |
| RF-20 | UI-01, UI-10 | No ejecutado | — | Preparación parcial C0; falta construcción/catálogo/evaluación final |
| RNF-1 | UI-01, UI-10 | No ejecutado | — | Inspección de dependencias no acredita cambio futuro |
| RNF-2 | UI-01, UI-10 | No ejecutado | — | Tokens y separación futuros por revisar |
| RNF-3 | UI-04, UI-07 a UI-09 | No ejecutado | — | Sin auditoría renderizada/lector |
| RNF-4 | UI-02, UI-09 | No ejecutado | — | Sin mediciones UI ni 20 ciclos |
| RNF-5 | UI-07, UI-09 | No ejecutado | — | Firefox/lector/móviles no confirmados; canales pendientes |
| RNF-6 | UI-03, UI-04, UI-06, UI-07, UI-10 | No ejecutado | — | No ejecución de flujos privados; proteger skipped.row |
| RNF-7 | UI-02, UI-03, UI-05 a UI-08, UI-10 | No ejecutado | — | Regresión real no ejecutada en C0 |
| RNF-8 | UI-10 | No ejecutado | — | Plantilla creada; falta evidencia de construcciones posteriores |

## 5. Hallazgos previos y carencias

| ID de seguimiento C0 | Evidencia / clasificación | Tratamiento y efecto |
|---|---|---|
| C0-K01 | Fallo de importación de estudiantes previamente registrado en [SPEC-001](../spec-001-tests/test.md); no se reprodujo de nuevo | Corrección de frontend autorizada e implementada el 2026-10-31 ([detalle](evidence.md#refactorización-y-corrección-de-defectos-previa-a-c1-2026-10-31)); verificado solo con API simulada. S-2 en sistema real sigue pendiente de re-ejecución |
| C0-K02 | Mensajes del runner previamente fallidos en idioma, [registro anterior](../spec-001-tests/test.md) | Fuera de reparación UI; no alterar evidencia histórica |
| C0-K03 | Lectura: UI ofrece .xls y lector usa openpyxl; [inventario](inventory.md) | Ayuda debe expresar formato compatible; sin cambiar enlace/importador. No se ejecutó un .xls para este hallazgo |
| C0-K04 | Lectura: skipped.row puede contener contraseña; [normalización/importaciones](../../../backend/routes/coordinador.py#L675-L738) | Diseñar prueba controlada de proyección segura; no guardar filas crudas, no cambiar contrato backend |
| C0-K05 | Lectura: colores propios repetidos y tema dark único; [inventario cromático](inventory.md) | Trabajo previsto T06 y migraciones; no reportarlo como regresión introducida por C0 |
| C0-K06 | Lectura: `selectImage` (ahora en [EstudianteChat.vue](../../../frontend/src/views/estudiante/EstudianteChat.vue)) solo acepta PNG/JPEG; RF-15/T70 pide además WEBP/GIF | Diferencia actual–objetivo registrada para T70; no afirmar soporte UI actual de cuatro formatos |
| C0-R01 | Firefox/NVDA/Android/iOS sin recurso confirmado | Casos correspondientes no ejecutados hasta disponer del recurso; no instalar por inferencia |
| C0-R02 | Escala/DPR/canal de navegador sin comprobación de ejecución | Condición previa a medir RNF-4/RNF-5, no inventar viewport ni canal estable |
| C0-G01 | Histórico C0: T01 marcada y cabecera del plan propuesta | Resuelto documentalmente el 2026-10-31 mediante [aprobación explícita del plan y paleta](plan.md). T01 respaldada desde esa fecha; T06 y C1–C5 siguen pendientes, sin aprobación funcional ni autorización de ejecución |
| C0-B01 | Lint real:1error no-unused-vars en currentLabel; [salida](evidence.md#baseline-de-construcción-t05-2026-09-30) | **Resuelto 2026-10-31** en la [refactorización previa a C1](evidence.md#refactorización-y-corrección-de-defectos-previa-a-c1-2026-10-31): lint código 0 |
| C0-B02 | Build real código0,chunk>500kB; [salida](evidence.md#baseline-de-construcción-t05-2026-09-30) | Aviso previo; preservar diagnóstico y medir carga/interacción antes de proponer ajuste. No subir umbral para ocultarlo |
| C0-B03 | Plugin timings y hooks solapados; [baseline](evidence.md#baseline-de-construcción-t05-2026-09-30) | Diagnóstico de herramienta, no resultado de rendimiento UI |

Los hallazgos de lectura no se convierten en resultados de sistema ni autorizan reparaciones. Lint/build ejecutados tienen evidencia y tratamiento en [baseline T05](evidence.md#baseline-de-construcción-t05-2026-09-30); no se arregló el producto para esta captura.

## 6. Historial de preparación

| Tarea | Modalidad / resultado de trabajo | Evidencia |
|---|---|---|
| T01 | Aprobación documental explícita del 2026-10-31, posterior a C0 | [Decisión del responsable](plan.md); resuelve C0-G01 sin retrodatación |
| T02 | Revisión documental completada | [Inventario](inventory.md) |
| T03 | Registro y recursos completados; carencias explícitas | Este documento y [entorno](evidence.md#entorno-t03-2026-09-30) |
| T04 | Diseño y validación documental completados | [48 casos, matriz y regresión](cases.md); no ejecución funcional |
| T05 | Ambas ejecuciones completadas:lint fallido/código1,build satisfactorio/código0 con avisos | [Baseline, huellas, integridad y tratamiento](evidence.md#baseline-de-construcción-t05-2026-09-30) |

**Limpieza C0:** no aplica a datos de negocio porque no se crearon ni consultaron; no reutilizar journals históricos. La salida de build es artefacto local de compilación, no evidencia de persistencia/API.

**Cierre documental C0:** [validación histórica de enlaces, estados, casos e integridad](evidence.md#validación-documental-de-c0) satisfactoria. T02–T05 completadas en C0; T01 respaldada posteriormente el 2026-10-31. C1–C5 pendientes; lint previo no reparado, y los 28 requisitos siguen no ejecutados en su comportamiento UI/UX.

## 7. Entrega funcional acotada (2026-11-15)

**Decisión:** reutilizar lo ya comprobado; terminar C1–C4, T80–T86 mínimos y T88 en Edge. Enmienda aprobada para Claro verde muy claro/blanco, Oscuro verde suave y excepción petróleo solo en login Oscuro; T85 semántica sin lector real. [Tareas adaptadas](tasks.md) y [plan vigente](plan.md).

**Resultado de ejecución seleccionada:** once identificadores con `PASS` (VM/runtime Vue y Edge `157.0.4341.46`), registrados con esperado/obtenido/modalidad en [evidencia de cierre](evidence.md#cierre-funcional-acotado-de-spec-002-2026-11-15). Lint/build finales código 0; solo aviso previo de chunk. API interceptada, no datos ni proveedores reales.

| Cobertura actual | Requisitos relacionados | Resultado / límite |
|---|---|---|
| Tokens, selector, prepaint, sistema/pestañas y storage bloqueado | RF-1–4; RNF-2 | Muestra satisfactoria; estética no se presenta como emoción probada |
| Shell/navegación, diálogo/dirty, perfil, estados/errores y limpieza de sesión | RF-5–10/18; RNF-6 | Integración seleccionada satisfactoria, sin todas las permutaciones ni autorización backend real |
| Listados/retorno, tutor, PDF/Excel seguros, institución y analíticas | RF-11–13/17 | Patrón y casos límite seleccionados satisfactorios; no importación/indexación/persistencia real |
| Historial/borrador, IME/imágenes, dictado doble, Mermaid y agenda completa | RF-14–17 | Muestra satisfactoria; audio real y alternativa semántica ausente de origen no acreditados |
| Contraste, controles/foco semánticos y responsive en Edge | RF-19; RNF-3/5 | Ratios y viewports de muestra satisfactorios; sin lector, zoom completo ni otros navegadores/dispositivos |
| Catálogo/trazabilidad y construcción | RF-20; RNF-1/2/8 | Entregables mínimos completados; no auditoría extensa ni certificación T98 |
| Rendimiento/ciclos y regresión real | RNF-4/7 y certificación integral | **No ejecutados**, diferidos |

**Hallazgos históricos conciliados:** C0-K03 ayuda `.xlsx`; C0-K04 resumen sin filas/razones privadas; C0-K05 temas/tokens; C0-K06 cuatro MIME/4 MiB implementados y comprobados en la muestra actual. C0-B01 sigue resuelto; C0-B02 conserva aviso. C0-K01/S-2 real, C0-K02 y carencias de lector/móviles/rendimiento no se cierran mediante mocks.

**No ejecutado/futuro:** T87 (Chrome integral), T89–T91 (Firefox/Android/iOS), T92–T93 (rendimiento/limpieza extensa), T94–T98 (regresión integral, cierre/certificación originales). Se conserva su casilla vacía. Partes de lector real de T85 y zoom/dispositivos completos de T86 son futuras, aunque la muestra mínima adaptada esté completada.

**Veredicto de entrega:** 87 tareas completadas en alcance adaptado y 11 diferidas; SPEC-002 funcionalmente cerrada para continuar SPEC-003. **No** se declara aprobación completa de los 20 RF/8 RNF ni ejecución de toda la matriz original. Preparación C0 y evidencia de paletas anteriores siguen históricas.