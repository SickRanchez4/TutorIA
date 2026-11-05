# Constitución de TutorIA

Principios innegociables para la evolución posterior a [Spec-000](spec-000-mvp/Spec-000-mvp.md). Toda especificación, plan e implementación debe cumplirlos. Los incumplimientos bloquean la aprobación del cambio.

## I. Simplicidad del stack

- Conservar Vue/JavaScript, Flask/Python, SQL Server y n8n como base; incorporar o sustituir tecnologías requiere una spec aprobada que justifique la necesidad.
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

- **Planificar:** cada construcción define alcance, requisitos que comprobar, recursos y criterios de evaluación.
- **Diseñar integración:** preparar casos y procedimientos para verificar interfaces y requisitos entre componentes; reutilizar y adaptar pruebas de construcciones precedentes para regresión.
- **Ejecutar integración:** registrar resultados y fallos; notificar al responsable del proyecto para decidir y documentar si prolonga la construcción, difiere la corrección o asigna personal para investigarla.
- **Ejecutar sistema:** al final de la iteración, probar la versión parcial con los casos del sistema y aplicar el mismo tratamiento de fallos.
- **Evaluar:** conservar una lista de comprobación por requisito con resultado, evidencia y defectos pendientes. Un requisito no ejecutado no puede declararse probado.
- Las herramientas, pasos de ejecución y reportes deben quedar documentados. Explicar cómo usar una herramienta no constituye evidencia de haber ejecutado las pruebas.

## V. Persistencia, contratos y configuración

- SQL Server es la fuente de verdad de los datos transaccionales; archivos y vectores mantienen identidad y vinculación verificables con institución y curso.
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