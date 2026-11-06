# SPEC-001 — Pruebas esenciales de TutorIA

## Contexto y objetivo

**Estado:** aprobado.  
**Fecha:** 2026-09-30.  
**Baseline:** [Spec-000 — MVP](../spec-000-mvp/Spec-000-mvp.md).  
**Gobernanza:** [Constitución](../constitution.md).

TutorIA necesita una forma sencilla, reproducible y verificable de comprobar lógica específica de negocio. Esta construcción incorpora un proyecto de pruebas independiente, parte de la solución, sin modificar los proyectos de frontend o backend ni su comportamiento.

El objetivo no es probar todos los casos de la aplicación ni certificar el MVP completo. Se selecciona lógica esencial por su riesgo y se combina análisis de caja blanca mediante **camino básico**, pruebas ejecutables y una lista de comprobación acotada. Cada prueba debe explicar por qué existe y cómo verifica el comportamiento.

La primera construcción comprende tres algoritmos existentes del MVP:

| ID | Lógica seleccionada | Justificación | Referencia funcional del baseline |
|---|---|---|---|
| A-1 | Permiso para crear una cuenta según vigencia de suscripción, estado del plan y capacidad de cuentas activas | Evitar altas incompatibles con la capacidad contratada | Spec-000, §§3.2 y 3.3 |
| A-2 | Alta o reutilización de un estudiante dentro de una institución | Conservar la identidad del estudiante, comprobar su rol y evitar reutilizar cuentas de otra institución | Spec-000, §§3.1 y 3.3 |
| A-3 | Creación de una conversación para un estudiante con matrícula activa en el curso | Comprobar el requisito académico de acceso antes de crear la conversación | Spec-000, §§3.4 y 6.1 |

La selección y los límites están acordados:

- **A-1:** la decisión existente de permitir crear una cuenta; incluye consulta de suscripción, vigencia, estado del plan y conteo de cuentas activas, sin analizar el consumo de tokens.
- **A-2:** la decisión existente de reutilizar o crear un estudiante a partir de sus datos; incluye sus salidas de rechazo y error. La lectura del archivo de importación y los algoritmos internos de validación y generación del hash quedan fuera del grafo.
- **A-3:** la operación existente de crear una conversación; incluye validación del curso, consulta de matrícula y persistencia con su tratamiento de error. Se parte de un estudiante autenticado y autorizado; no se analizan los algoritmos internos de autenticación ni se envían mensajes.

El plan identificará las funciones correspondientes y detallará las pruebas dentro de estos límites, sin ampliar el alcance. La integración se realizará con la aplicación ejecutada en local y la base de datos local configurada en el archivo de entorno del backend, sin modificar ni publicar esa configuración.

La lista de comprobación se limita a estos algoritmos y a los requisitos de esta construcción. El resto del MVP se declarará **fuera del alcance de verificación**, no como probado.

## Requisitos funcionales

Los criterios de aceptación se expresan en notación EARS: condición o evento y respuesta verificable.

### RF-1. Independencia de las pruebas

**Requisito:** disponer de un proyecto de pruebas separado que verifique el comportamiento real sin alterar la aplicación.

- **Siempre**, el proyecto de pruebas deberá mantener sus propios recursos de ejecución y documentación, sin requerir cambios en los proyectos de frontend o backend.
- **Cuando** una prueba necesite acceder a lógica existente, deberá poder importarla o ejercitar sus interfaces existentes sin copiar sus reglas de negocio ni introducir accesos nuevos en la aplicación.
- **Cuando** la ejecución finalice, deberá dejar de aplicar las sustituciones temporales utilizadas para aislar dependencias.

### RF-2. Selección esencial y trazabilidad

**Requisito:** justificar un conjunto mínimo de pruebas de lógica específica.

- **Cuando** se diseñe una prueba, deberá identificarse el algoritmo, comportamiento del baseline o requisito que verifica, el riesgo que justifica incluirla y su resultado esperado.
- **Siempre**, la primera construcción deberá limitarse a A-1, A-2 y A-3, sin incorporar pruebas genéricas o un caso automatizado por cada funcionalidad del MVP.
- **Cuando** varios comportamientos dependan de una misma regla, deberán reutilizarse las verificaciones pertinentes, evitando duplicación innecesaria.

### RF-3. Análisis de caja blanca mediante camino básico

**Requisito:** documentar y comprobar los caminos independientes de los tres algoritmos seleccionados.

- **Cuando** se analice cada algoritmo, deberá elaborarse un grafo de flujo con nodos, aristas, decisiones, entradas y salidas identificables y vinculados con la implementación existente.
- **Cuando** se calcule su complejidad ciclomática, deberá registrarse el cálculo, la convención usada para condiciones compuestas y manejo de errores, y el conjunto de caminos independientes resultante.
- **Siempre**, el análisis deberá representar cada condición completa de una decisión como un predicado, sin desglosar el cortocircuito de sus operadores internos; deberá distinguir las salidas normales y de error explícitas del algoritmo y excluir los recorridos internos de sus dependencias. Esta convención y sus límites deberán indicarse junto a cada grafo.
- **Cuando** se calcule la complejidad de un grafo conectado, deberá usarse `V(G) = E - N + 2`, identificando el número de aristas y nodos e incorporando una salida común cuando existan varias terminaciones. El valor se derivará del grafo real, no de una cantidad prefijada de tests.
- **Cuando** se diseñen las pruebas de camino básico, deberá asociarse cada camino independiente factible con entradas, resultado esperado y una prueba ejecutable.
- **Si** un camino resulta inviable, deberá justificarse su inviabilidad, sin declararlo ejecutado ni reducir artificialmente el análisis para ocultarlo.

El mínimo de pruebas se determina por los caminos de los algoritmos seleccionados y los límites esenciales de negocio; no supone explorar todas las combinaciones de entradas ni todos los recorridos posibles.

### RF-4. Capacidad de cuentas

**Requisito:** verificar el permiso de alta conforme al estado institucional existente.

- **Cuando** falte la suscripción o el plan, o no se cumplan sus condiciones de actividad y vigencia, las pruebas deberán comprobar que no se permite crear otra cuenta.
- **Cuando** el plan tenga una capacidad finita, las pruebas deberán comprobar que se permite el alta por debajo del límite y se rechaza al alcanzarlo o superarlo.
- **Cuando** la capacidad del plan sea ilimitada, las pruebas deberán comprobar que no se rechaza el alta por cantidad de cuentas.
- **Cuando** existan cuentas inactivas o de otras instituciones, las pruebas deberán comprobar que no incrementan el conteo de cuentas activas de la institución evaluada.

### RF-5. Alta y reutilización de estudiantes

**Requisito:** verificar la decisión de crear, reutilizar o rechazar una cuenta de estudiante.

- **Cuando** el email normalizado corresponda a un estudiante de la misma institución, las pruebas deberán comprobar que se reutiliza la cuenta sin crear un duplicado.
- **Cuando** el email pertenezca a otra institución o a una cuenta sin rol de estudiante, las pruebas deberán comprobar que se rechaza la reutilización.
- **Cuando** se solicite un alta nueva con datos válidos, capacidad disponible y rol requerido existente, las pruebas deberán comprobar que se crea el estudiante asociado a la institución y al rol correspondiente.
- **Cuando** el email o la contraseña sean inválidos, no exista capacidad de alta o falte el rol requerido, las pruebas deberán comprobar la salida de rechazo o error existente y que no se crea el estudiante.

Los validadores subordinados se comprobarán únicamente en lo necesario para los caminos de este algoritmo; no se exige una suite exhaustiva de formatos o contraseñas.

### RF-6. Creación de conversaciones según matrícula

**Requisito:** verificar la creación de una conversación sin enviar mensajes ni invocar IA.

- **Cuando** un estudiante solicite crear una conversación con un identificador válido de curso y matrícula activa, las pruebas deberán comprobar que se crea vinculada al estudiante y al curso solicitado.
- **Cuando** no exista matrícula activa del estudiante en ese curso, las pruebas deberán comprobar que se rechaza la creación y no se persiste una conversación.
- **Cuando** falte el identificador de curso o no pueda interpretarse según el contrato existente, las pruebas deberán comprobar la salida de validación del algoritmo.
- **Si** falla la persistencia durante la creación, las pruebas deberán comprobar el tratamiento de error y la reversión de la operación, sin exigir cambios en la aplicación.

### RF-7. Lista de comprobación acotada

**Requisito:** permitir revisar el cumplimiento del alcance con resultados inequívocos.

- **Cuando** se prepare una construcción, la lista deberá identificar los requisitos aplicables, algoritmos y caminos, procedimiento, recursos, resultado esperado y evidencia necesaria.
- **Cuando** se registre un resultado, deberá distinguirse entre **aprobado**, **fallido**, **no ejecutado** y **no aplicable**, con justificación para este último.
- **Si** una comprobación no se ejecutó o carece de evidencia, no deberá figurar como aprobada.
- **Siempre**, la lista deberá identificar defectos pendientes y excluir cualquier afirmación de cobertura integral del MVP.
- **Cuando** se documenten las pruebas de una spec, su carpeta deberá contener un documento `test.md` como registro central de alcance, grafos, caminos, checklist, instrucciones, resultados y defectos. Los reportes deberán referenciarse desde ese documento y conservarse en la misma carpeta o en una subcarpeta de evidencias.

### RF-8. Documentación de herramientas para uso posterior

**Requisito:** explicar cómo el usuario podrá ejecutar las verificaciones y obtener evidencia con herramientas adecuadas, sin automatizaciones adicionales innecesarias.

La selección mínima será **unittest**, incluido en Python, para ejecutar y obtener resultados de las pruebas; **Mermaid**, ya utilizado en la solución, para representar los grafos; y el documento de pruebas para el checklist y la evaluación. Se documentará su uso desde PowerShell y cómo conservar la salida de ejecución en un reporte de texto. No se requiere instalar un generador de reportes, automatizar el navegador ni añadir una herramienta de cobertura en esta primera construcción.

- **Cuando** se documente una herramienta, deberá explicarse su propósito, requisitos previos, preparación, pasos de uso, interpretación del resultado y forma de conservar la evidencia.
- **Cuando** el usuario siga la documentación, deberá poder ejecutar las pruebas seleccionadas, consultar resultados, visualizar los grafos y completar la lista de comprobación.
- **Si** se utiliza un informe de cobertura, deberá explicarse su alcance sobre la lógica seleccionada y que no demuestra por sí solo cobertura de caminos ni corrección funcional.
- **Siempre**, la documentación deberá diferenciar ejemplos o resultados esperados de evidencias obtenidas realmente.

Esta fase solo especifica el entregable documental. No obliga a instalar, integrar o ejecutar ahora las herramientas, ni a incorporar una plataforma de reportes, un pipeline o un panel en la aplicación.

### RF-9. Ejecución y evaluación conforme a PUDS

**Requisito:** registrar la verificación real cuando se implemente y ejecute esta construcción.

- **Antes de** ejecutar pruebas, deberán definirse alcance, recursos y criterios de evaluación, así como los casos de integración pertinentes y la regresión reutilizable.
- **Cuando** se ejecuten pruebas de integración, deberán registrarse resultados, fallos y evidencia reproducible.
- **Cuando** se verifique la integración, deberán ejercitarse los tres algoritmos seleccionados con la persistencia local real y datos ficticios propios de las pruebas: capacidad de cuentas, creación/reutilización/rechazo de estudiantes y creación/rechazo de conversaciones. Las salidas de error difíciles de provocar de forma segura deberán comprobarse con dependencias controladas, identificándolas como pruebas aisladas, no como integración real.
- **Al finalizar** la iteración, deberán ejecutarse los casos de sistema pertinentes al alcance seleccionado y registrarse sus resultados, sin extender el alcance al MVP completo.
- **Cuando** se compruebe el sistema, deberán revisarse manualmente en la aplicación local tres escenarios acotados: rechazo de un alta por capacidad alcanzada, importación mínima que crea un estudiante y reutiliza otro de la misma institución sin duplicarlo, y creación de una conversación por un estudiante matriculado. La denegación de creación sin matrícula se comprobará mediante la interfaz HTTP existente si la interfaz visual no permite solicitarla; no se automatizará el navegador.
- **Cuando** se conserve evidencia, cada caso deberá indicar fecha, versión o commit evaluado, tipo de prueba, datos ficticios relevantes, resultado esperado, resultado obtenido y referencia al reporte correspondiente, sin incluir credenciales. Para los recorridos manuales de sistema bastará registrar la observación confirmada por el operador (resultado en la interfaz y status/valores HTTP observados), junto con el reporte de verificación SQL de datos propios; no se exigirán capturas de pantalla. Se distinguirá la observación comunicada de la comprobación automatizada: SQL por sí solo no acredita la interfaz ni la respuesta HTTP. Los casos aislados no sustituirán la evidencia de integración o sistema.
- **Si** se detecta un fallo, deberá notificarse al responsable y registrarse su decisión de prolongar la construcción, diferir la corrección o asignar investigación; no deberá corregirse el producto de forma implícita dentro de esta spec.
- **Cuando** se evalúe la construcción, deberá conservarse la relación requisito–prueba–resultado–evidencia–defectos pendientes, identificando la versión evaluada y el entorno utilizado.

### RF-10. Seguridad del entorno y los datos

**Requisito:** permitir integración real de pruebas solo en un entorno expresamente preparado para ello.

- **Cuando** se ejecuten pruebas aisladas, deberán utilizar datos ficticios y dependencias controladas, documentando qué comportamiento real no verifican.
- **Cuando** una prueba requiera integración con persistencia real o con la aplicación en ejecución, deberá exigirse configuración explícita de un entorno de pruebas, datos identificables y un procedimiento de preparación y limpieza.
- **Cuando** se prepare la integración, deberá reutilizarse la conexión a la base local configurada en el archivo de entorno del backend, comprobando el destino sin mostrar sus credenciales y requiriendo confirmación del operador antes de modificar datos. No se creará una segunda configuración de conexión en el frontend o backend.
- **Cuando** se preparen datos, deberán crearse instituciones y registros ficticios identificables y exclusivos de la ejecución, con referencias temporales controladas. Al finalizar, incluso ante fallos, deberá intentarse eliminar únicamente esos registros y documentar cualquier residuo; no se vaciará la base ni se alterarán cuentas, planes o roles preexistentes para provocar un caso.
- **Si** no puede verificarse que el destino corresponde al entorno de pruebas autorizado, la ejecución que pueda modificar datos deberá bloquearse e indicar el motivo.
- **Siempre**, las pruebas deberán evitar producción, datos personales reales, llamadas a proveedores de IA, consumo de tokens y envío de notificaciones; la limpieza deberá limitarse a los datos creados por las pruebas.

### RF-11. Continuidad para futuras especificaciones

**Requisito:** mantener una práctica de pruebas esenciales, proporcional a cada cambio.

- **Cuando** se planifique una nueva spec, deberán seleccionarse las verificaciones de lógica específica según sus requisitos y riesgos, justificando qué se añade, adapta o reutiliza.
- **Cuando** un cambio afecte comportamientos ya cubiertos, deberán ejecutarse las pruebas de regresión pertinentes y actualizarse la trazabilidad.
- **Si** una nueva spec no necesita analizar otros algoritmos, no deberá imponerse la incorporación de otros dos o tres por cumplir una cantidad fija.
- **Siempre**, deberá explicarse el propósito y funcionamiento de las nuevas pruebas, manteniendo el alcance mínimo justificable.

## Requisitos no funcionales

- **RNF-1 — Sencillez:** código de pruebas breve y legible, sin un framework propio, capas preventivas ni abstracciones para necesidades futuras.
- **RNF-2 — No intrusión:** ninguna modificación de lógica, contratos, esquema, configuración o dependencias de los proyectos de frontend y backend como condición de esta construcción. Si una dificultad exige tales cambios, se detendrá esa parte y se solicitará revisar y aprobar el alcance antes de continuar.
- **RNF-3 — Reproducibilidad:** declarar prerrequisitos y recursos, controlar fechas y datos relevantes y evitar que el orden de ejecución determine el resultado.
- **RNF-4 — Mantenibilidad:** probar la implementación existente, sin reproducir sus algoritmos dentro del proyecto de pruebas; documentar límites de los dobles de prueba.
- **RNF-5 — Evidencia honesta:** conservar resultados reales e identificar lo no ejecutado; no fijar un porcentaje global de cobertura ni afirmar certificación del producto.
- **RNF-6 — Idioma:** documentación y mensajes al usuario en español; identificadores y comentarios nuevos en inglés, conservando los nombres existentes.
- **RNF-7 — Confidencialidad:** no incluir secretos ni datos privados en documentación, datos de prueba o reportes; mensajes públicos sin excepciones internas ni información sensible innecesaria.

## Casos límite

| Caso | Tratamiento dentro del alcance |
|---|---|
| Vigencia en los instantes exactos de inicio y fin | Verificar los límites temporales existentes mediante referencias controladas |
| Capacidad finita alcanzada o superada | Rechazar nuevas altas; no introducir reservas ni controles nuevos |
| Capacidad ilimitada | Distinguirla de una capacidad finita agotada |
| Cuentas inactivas o de otra institución | No contarlas para la capacidad activa institucional |
| Email con variaciones normalizables | Verificar la decisión de reutilización sin duplicado |
| Email de otra institución o rol incompatible | Rechazar reutilización sin alterar la cuenta existente |
| Datos de alta inválidos, capacidad indisponible o rol ausente | Verificar rechazo/error del algoritmo sin alta nueva |
| Matrícula ausente, inactiva o correspondiente a otro curso/estudiante | Rechazar creación de conversación |
| Error de persistencia al crear la conversación | Comprobar error y reversión de la operación |
| Camino no factible o prueba bloqueada por el entorno | Registrar justificación o bloqueo; no marcar como ejecutado |
| Entorno real de pruebas no disponible | Mantener esas comprobaciones como no ejecutadas; no sustituirlas por una afirmación de integración exitosa |
| Destino de integración no verificable como autorizado | Bloquear operaciones que puedan modificar datos |
| Discrepancia entre comportamiento y baseline | Registrar defecto y decisión; no cambiar silenciosamente la aplicación o lo especificado |

## Fuera de alcance

- Pruebas, grafos o reportes relativos a tokens, consumo, precios o cuotas de IA.
- Envío de mensajes, respuestas del tutor, calidad de IA, RAG y proveedores externos.
- Pruebas exhaustivas de toda la importación de estudiantes o de todos los validadores subordinados.
- Comprobación completa del MVP, de cada endpoint, caso, pantalla o requisito existente.
- Suites genéricas de CRUD, pruebas visuales, de carga, rendimiento o seguridad integral.
- Corrección de defectos del producto, refactorizaciones para facilitar tests o nuevas reglas de negocio.
- Solución de las limitaciones de concurrencia de capacidad declaradas por Spec-000.
- Cambios en frontend, backend, contratos públicos, esquema o workflows.
- Instalación o ejecución de herramientas durante la redacción de la spec; infraestructura de reportes, CI/CD o panel de pruebas dentro de la aplicación.
- Imponer dos o tres algoritmos adicionales o cobertura exhaustiva en cada spec futura.

## Criterios de finalización

### Aprobación de la especificación

- Alcance, requisitos y exclusiones revisados y aprobados explícitamente por el responsable.
- Alcance de los algoritmos, convención de grafos, herramientas, entorno local y registro de evidencias definidos en esta spec; el plan detallará su ejecución sin ampliar los requisitos.
- Ningún test implementado ni prueba declarada ejecutada por el mero hecho de redactar esta spec.

### Finalización de la construcción posterior

- Proyecto de pruebas independiente y sin modificaciones en frontend o backend.
- Tres algoritmos vinculados con la implementación y el baseline; grafos, cálculos y caminos documentados.
- Pruebas esenciales con propósito, entradas, resultado esperado y explicación de funcionamiento.
- Checklist limitado al alcance acordado, con trazabilidad y estados verificables.
- Documento de pruebas dentro de la carpeta de esta spec que centralice grafos, caminos, checklist, procedimientos y resultados; observaciones manuales confirmadas y reportes de texto referenciados, sin secretos ni obligación de capturas de pantalla.
- Herramientas y procedimientos de uso posterior documentados, incluida conservación e interpretación de evidencia.
- Integración y sistema pertinentes ejecutados conforme a PUDS, o bloqueos y comprobaciones no ejecutadas expresamente registrados.
- Fallos notificados, defectos pendientes y decisiones documentados. Un fallo o bloqueo impide declarar cumplido el requisito afectado, aunque el responsable decida cerrar o diferir trabajo.
- Evaluación final que distinga requisitos cumplidos, fallidos y no verificados, sin certificar el resto del MVP.

## Preguntas abiertas

Ninguna. Las decisiones necesarias para delimitar la funcionalidad están resueltas. Los valores de complejidad, nodos, aristas y casos concretos se obtendrán del análisis de la implementación durante la planificación; son resultados del trabajo, no dudas de alcance pendientes.
