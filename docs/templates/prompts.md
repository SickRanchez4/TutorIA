# Prompts SDD

Estos son ejemplos genéricos de redacción, no specs aprobadas ni instrucciones de ejecución de TutorIA. Los proyectos de hábitos y agentes citados son ejemplos ajenos al producto; sus nombres, IDs y rutas son marcadores que deben sustituirse antes de usar un prompt.

En TutorIA, consultar la [Constitución vigente](../specs/constitution.md) y las [specs y estados actuales](../../README.md). Las specs reales residen en `docs/specs/`; estas plantillas no crean una segunda fuente de requisitos ni autorizan cambios.

## Constitución

```text
Vamos a crear la constitución de un proyecto nuevo: una CLI en Python para
registrar hábitos de estudio y calcular rachas. Es un proyecto educativo que
debe poder mantener un desarrollador junior.

Proponme un docs/constitution.md con 6 principios innegociables, cortos y
verificables, que cubran: simplicidad del stack, relación entre spec y código,
separación entre lógica e interfaz, política de tests, persistencia de datos
e idioma del código y los mensajes. Máximo 15 líneas. Espera mi aprobación.
```

*Destino ilustrativo: `/.sdd/constitution.md`; no es una ruta del repositorio.*

## Especificación

```text
NO escribas código en ningún momento. Vamos a redactar la especificación de la funcionalidad [003-agents-structure].
Lee .sdd/constitution.md.

Idea inicial: Como desarrollador, quiero que todos los agentes de IA actuales y q se vayan a crear a futuro tengan una estructura limpia y robusta para su implementacion,
tomando en cuenta todas las partes que necesita un agente de IA para funcionar correctamente a nivel produccion.
No se debe caer en la sobreingenieria, se debe planificar e implementar solamente lo necesario.
se debera analizar como funcionan los agentes actuales y asi definir una estructura adecuada para ellos (tomando en cuenta q las herramientas de estos agentes ejecutan acciones en el cliente que consume esta microservicio y actualmente hay informacion replicada y redundate para lograr esto tanto en el cliente(Clients.dRevealWebClient) como en el microservicio(AIEngine))


Acceptance criteria
- Introduce and integrate AI Agents abstractions.
- Move common agentic functionality into reusable functionalities.
- Maintain existing functionality after the refactoring.
- Establish a clear separation of responsibilities business logic, services and providers reusing the structures that already exist.

Tu trabajo:
1. Hazme preguntas de UNA en UNA para eliminar ambigüedades (casos límite,
   comportamiento con errores, qué queda fuera del alcance).
2. Con mis respuestas, genera specs/[003-agents-structure]/spec.md con esta estructura:
   contexto y objetivo, usuarios, requisitos funcionales
   numerados (RF-x) con criterios de aceptación en notación EARS en español,
   requisitos no funcionales, casos límite, fuera de alcance, criterios de
   finalización y dudas abiertas marcadas como [TBD].
3. El QUÉ y el POR QUÉ. Nada de stack, arquitectura ni nombres de archivos.
```

*Destino ilustrativo: `specs/001-xxx/spec.md`; sustituir por la carpeta de la spec real.*

## Clarificación

```text
Revisa specs/001-xxx/spec.md como si fueras un QA profesional senior.
Lista: (1) ambigüedades restantes, (2) contradicciones entre requisitos,
(3) casos límite no cubiertos, (4) conflictos con .sdd/constitution.md.
No propongas soluciones todavía: solo detecta. Formato: lista numerada.
```

## Diagramar

```text
En tasks.md, en la sección DIAGRAM, crea el diagrama UML usando Mermaid.js con la solución completa para esta especificación.
Utiliza color verde para las clases nuevas y color azul para las clases que ya existen.
```

## Planificación

```text
Lee .sdd/constitution.md y specs/003-agents-structure/spec.md. NO escribas código.
Genera specs/003-agents-structure/plan.md con: estructura de módulos, modelo de
datos JSON en caso de ser necesario, contratos, decisiones técnicas
justificadas, y estrategia de tests.
Todo debe respetar la constitución y cubrir todos los RF. Marca qué RF cubre cada parte.
```

*Destino ilustrativo: `specs/001-xxx/plan.md`; sustituir por la carpeta de la spec real.*

## Tareas

```text
A partir de spec.md y plan.md, genera specs/001-xxx/tasks.md:
tareas pequeñas, en orden de dependencia, cada una con los RF que cubre 
y una línea "Done when:" verificable. Usa checkboxes.
```

*Destino ilustrativo: `specs/001-xxx/tasks.md`; sustituir por la carpeta de la spec real.*

## Implementación

```text
Implementa SOLO la tarea T1 de specs/001-xxx/tasks.md, siguiendo
plan.md y la constitución. Al terminar: marca la tarea en tasks.md,
indica qué RF cubre y PÁRATE.
```

*Genera la implementación del código dentro de /habits*

## Validación

```text
Recorre specs/001-habits-mvp/spec.md requisito por requisito (RF-1 a RF-11).
Para cada uno indica: qué test lo cubre, y el resultado de ejecutarlo.
Si algún RF no está cubierto o falla, dilo claramente. Después comprueba los
criterios de finalización y dame un veredicto: ¿la spec está cumplida?
```

## Próximos pasos

```text
Nuevo requisito para habits-cli: marcar como hecho el día de ayer con
`habits done <nombre> --ayer`. NO toques código. Primero: actualiza
specs/001-habits-mvp/spec.md (nuevo RF con EARS + casos límite: ¿y si ayer
ya estaba marcado? ¿afecta a la racha?) y muéstrame el diff de la spec.
```