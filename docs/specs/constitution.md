# Constitución de TutorIA

Principios innegociables para la evolución posterior a [Spec-000](spec-000-mvp/Spec-000-mvp.md). Toda especificación, plan e implementación debe cumplirlos. Los incumplimientos bloquean la aprobación del cambio.

## I. Simplicidad del stack

- Conservar Vue/JavaScript, Flask/Python, PostgreSQL 18.x y n8n como base; incorporar o sustituir tecnologías requiere una spec aprobada que justifique la necesidad.
- Antes de añadir dependencias o abstracciones, comprobar que las existentes no cubren el requisito. No implementar funcionalidades futuras sin requisitos aprobados.

## II. Relación entre especificación y código

- Spec-000 es el baseline cerrado; los cambios posteriores requieren una spec aprobada antes de implementar.
- Cada spec tiene un identificador único, utilizado en su plan, tareas, commits y revisión del cambio.
- Cada requisito debe vincularse con su implementación y evidencia de verificación conforme a la sección IV; todo cambio de comportamiento debe corresponder a un requisito.
- Si la implementación exige cambiar lo especificado, actualizar y aprobar primero la spec. No admitir divergencias silenciosas.

## III. Separación de lógica e interfaz

- Vistas y componentes presentan datos y gestionan interacción; las reglas de negocio y autorización se ejecutan en el backend, sin depender de validaciones del cliente.
- Las rutas HTTP validan entradas, aplican controles de acceso, delegan operaciones y construyen respuestas; las nuevas reglas de negocio se implementan en servicios.
- Encapsular persistencia e integraciones externas en servicios, adaptadores o workflows, separados de la presentación; no acoplar la interfaz a proveedores de IA.
- No duplicar reglas entre capas ni introducir refactorizaciones no exigidas por la spec.

## IV. Política de pruebas — PUDS

La referencia para la **disciplina de Pruebas** es la adaptación del capítulo 11, «Prueba», de *El Proceso Unificado de Desarrollo de Software* (Jacobson, Booch y Rumbaugh) contenida en `guia-pruebas-puds-dev-ai.md`, proporcionada por el responsable. Se adopta **solo esa disciplina de pruebas**, no PUDS como metodología global de gestión o desarrollo. La gestión histórica del MVP se realizó con Scrum; los incrementos posteriores se gobiernan mediante SDD (sección II). Estas prácticas son complementarias, no equivalentes.

- **Decidir antes del plan:** antes de elaborar el plan de una spec, el desarrollador decide si se realizarán pruebas y cuál será su alcance. La IA puede proponer una estrategia, pero no la aprueba. Registrar en la spec la decisión, su motivo y, cuando se incluyan pruebas, los requisitos/casos de uso cubiertos, tipos de prueba, exclusiones y criterios de evaluación. No asumir pruebas obligatorias ni definir su alcance sin esa decisión.
- **Incorporar la decisión al plan:** dentro del alcance aprobado, la IA propone y el desarrollador valida el plan de pruebas, las prioridades y los criterios medibles de entrada y éxito que correspondan. El plan de la spec concreta casos, recursos, herramientas y ejecución; no requiere implementar ni ejecutar los tests antes de su aprobación. Los porcentajes de la guía son ejemplos, no umbrales universales. Cualquier cambio de alcance requiere una nueva decisión explícita del desarrollador y actualización de spec y plan.
- **Planificar y diseñar por iteración:** para cada construcción con pruebas incluidas, identificar requisitos y riesgos; diseñar los casos desde los **casos de uso y sus flujos** (caja negra) o las **realizaciones de diseño** (caja blanca), con entradas, estado inicial, resultado esperado y trazabilidad. El desarrollador valida los resultados esperados antes de implementar las pruebas. No derivarlos únicamente del código bajo prueba.
- **Implementar componentes de prueba:** la IA implementa los tests automatizables dentro del alcance, reutilizando procedimientos cuando resulte útil; el desarrollador revisa por muestreo los casos críticos. No introducir automatización o infraestructura sin necesidad aprobada. Mantener los casos de regresión seleccionados cuando cambien sus comportamientos.
- **Ejecutar integración por construcción:** cuando forme parte del alcance acordado, la IA ejecuta los casos pertinentes de cada build, compara resultado observado y esperado, investiga diferencias y registra defectos **antes** de proponer o aplicar su corrección. Usa componentes reales siempre que el entorno autorizado lo permita; las simulaciones no acreditan integración real. El responsable decide y documenta si se prolonga la construcción, se difiere la corrección o se asigna una investigación; una corrección fuera del alcance aprobado exige la aprobación correspondiente. Tras una corrección autorizada, se vuelve a probar.
- **Ejecutar sistema al final de la iteración:** cuando esté incluido y se cumplan los criterios de entrada establecidos, la IA ejecuta los casos automatizados acordados y el desarrollador comprueba los recorridos manuales de comportamiento observable. Las pruebas de sistema derivan de los casos de uso y requisitos externos, no solo de detalles de implementación.
- **Evaluar y decidir:** para cada iteración con pruebas, la IA informa **compleción** (casos ejecutados / previstos) y **fiabilidad** (casos aprobados, defectos nuevos, abiertos y cerrados), junto con la relación requisito–caso–resultado–evidencia–defecto. El desarrollador decide la aceptación, la continuación de pruebas o el tratamiento de partes pendientes. Un requisito fallido o no ejecutado no puede declararse probado; una decisión de entrega no convierte un fallo en éxito.
- **Independencia de resultados esperados:** la IA no modifica un resultado esperado para hacer pasar una prueba sin aprobación explícita del desarrollador. Presentar salidas reales de ejecución y distinguir casos aislados, integración, sistema, observaciones manuales y comprobaciones no ejecutadas.
- **Artefactos proporcionales:** documentar plan, casos/procedimientos, componentes automatizados, defectos y evaluación en los archivos de la spec y/o proyecto de pruebas ya existentes, conservando sus convenciones (por ejemplo, `test.md` cuando corresponda). Los nombres `tests/plan-iterN.md` y `tests/casos.md` de la guía son una estructura sugerida, no una obligación de duplicar documentación.
- **Sin pruebas por decisión explícita:** si el desarrollador decide no realizarlas, registrar esa decisión y los límites de verificación. No exigir casos ni ejecuciones para cerrar la spec ni presentar sus requisitos como probados.

## V. Persistencia, contratos y configuración

- PostgreSQL 18.x es la fuente de verdad de los datos transaccionales; archivos y vectores mantienen identidad y vinculación verificables con institución y curso.
- Configurar la conexión mediante `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` y `DB_SSLMODE`; construir la URL internamente, sin solicitar una URI completa ni exponer credenciales.
- Los cambios de esquema requieren scripts versionados, estrategia de preservación de datos y verificación; los scripts iniciales no sustituyen migraciones sobre bases existentes.
- Ningún dato necesario para recuperación o reintento puede depender exclusivamente de memoria o almacenamiento efímero.
- Prompts, modelos, límites y ajustes de proveedores usan configuración o constantes identificables; los secretos nunca se incluyen en código, specs ni logs.
- Los cambios incompatibles en contratos API o n8n requieren especificación y coordinación de todos sus consumidores.

## VI. Idioma y mensajes

- Los nuevos identificadores y comentarios se escriben en inglés; specs, planes, tareas y documentación del proyecto, en español.
- Los nombres existentes en español se conservan salvo renombrado explícitamente especificado; no romper contratos por uniformidad lingüística.
- Los mensajes al usuario se escriben en español; los logs técnicos, en inglés, con contexto útil y sin datos personales innecesarios. La protección de secretos se rige por la sección V.
- Los errores públicos son comprensibles y no exponen excepciones internas ni contenido privado.

## Gobernanza

- Esta constitución rige los cambios posteriores al MVP; no declara corregidas las limitaciones de Spec-000 ni exige reconstruir retrospectivamente su proceso.
- Cada plan y revisión comprueba su cumplimiento. Las modificaciones a la constitución requieren aprobación explícita y registro del motivo.
- **2026-11-14 — Secciones I y V:** por solicitud expresa del responsable, PostgreSQL 18.x sustituye SQL Server y las credenciales se configuran por campos separados. [SPEC-008](spec-008-postgresql/spec.md) registra el alcance: base nueva externa, sin migración de datos ni servicio PostgreSQL en Compose; solo verificaciones de configuración/compilación, sin añadir tests.
- **2026-11-14 — Sección IV:** por solicitud explícita del responsable, la decisión sobre realizar pruebas y su alcance corresponde al desarrollador y precede al plan de cada spec. El cambio no altera resultados históricos ni elimina compromisos de pruebas ya aprobados sin una nueva decisión registrada.
- **2026-11-14 — Aclaración metodológica y sección IV:** a solicitud del responsable, se explicita que Scrum fue la metodología ágil utilizada en el MVP, SDD gobierna los incrementos posteriores y la guía `guia-pruebas-puds-dev-ai.md` adapta exclusivamente la disciplina de Pruebas de PUDS para el binomio desarrollador–copiloto IA. Se añaden responsabilidades, controles de casos/resultados y evaluación por iteración, manteniendo la decisión previa del desarrollador sobre el alcance de pruebas. No se reescriben los resultados ni los compromisos ya aprobados de SPEC-001 o SPEC-002.
