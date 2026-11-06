# Regresión proporcional para futuras specs — T23

## Seleccionar por impacto, no por cantidad

Antes de construir una nueva spec, relacionar sus requisitos con reglas modificadas y dependencias compartidas. Para cada caso registrar riesgo, entrada, esperado y decisión: **reutilizar**, **adaptar**, **añadir** o **excluir con justificación**. No imponer otros tres algoritmos, suites CRUD genéricas, todas las pantallas ni porcentajes globales de cobertura.

| Cambio o riesgo | Regresión pertinente de SPEC-001 | Qué demuestra / qué falta |
|---|---|---|
| Suscripción, vigencia, plan o conteo activo institucional | A1-P1…P5 y variantes; I-1; S-1 si cambia el alta visible | Aislados verifican decisiones; I-1 conteo SQL; S-1 contrato/UI comunicado y SQL |
| Normalización, rol, institución o creación/reutilización de estudiante | A2-P1…P8; I-2/I-3; S-2 si afecta importación | Mantener identidad, rechazos y persistencia; S-001 sigue abierto, no usar el antiguo fallo como aprobación |
| Matrícula o creación de sesiones | A3-P1…P5 y variantes; I-4; S-3/S-3b | Acceso/persistencia y 403 sin matrícula; no enviar mensajes ni probar IA |
| Helper de aislamiento, imports o runner | Suite aislada completa (23), controles pertinentes | Restauración, guardias y caminos obligatorios; no acredita SQL real |
| Journal, fixtures, autorización o limpieza | Controles (53) y casos reales afectados, con nueva autorización | Dobles verifican recuperación/bloqueos; SQL real debe comprobar destino y limpieza |
| Cambio solo documental sin comportamiento afectado | Revisión de trazabilidad/enlaces; justificar exclusión funcional | No inventar regresión funcional ejecutada |

## Reutilización y adaptación

Conservar IDs A/I/S originales al reutilizar casos; el registro de la nueva spec añade referencia al cambio evaluado y al reporte nuevo. No copiar reglas de negocio ni duplicar tests solo para renombrarlos. Si cambia un contrato, conservar el reporte histórico, justificar la nueva expectativa aprobada y actualizar el caso/grafo pertinente; no cambiar expectativas para ocultar un bug. Añadir pruebas únicamente cuando falte una verificación esencial, explicando funcionamiento y límite.

La [suite aislada](run_tests.py) actual selecciona explícitamente los tres módulos y exige los 18 caminos: no tiene opción de filtro y un subconjunto no equivale a aprobar SPEC-001. Para regresión de A-1/A-2/A-3 ejecutar la suite completa, pequeña; identificar en el registro qué casos eran pertinentes. Si una nueva spec necesita un subconjunto independiente, definir selección explícita con sus criterios y reporte propios, sin alterar ahora el runner ni hacer discovery global (podría cargar integración).

## Ejecutar y conservar evidencia

Seguir [README.md](README.md) y [SYSTEM.md](SYSTEM.md) para comandos PowerShell, entorno propio, salida/código y modalidades. Usar reporte nuevo: nunca sobrescribir evidencia. Registrar fecha, versión/commit y cambios locales/huellas, nueva spec, casos reutilizados, esperado/obtenido, código y defectos. Revisar primero la versión fuente: una aprobación histórica no certifica código modificado después.

1. Ejecutar aislamiento y controles pertinentes sin SQL/HTTP/lectura de secretos.
2. Para integración/sistema real, comprobar destino local y solicitar autorización **nueva por operación**; aplicación detenida para preparar/limpiar, sin otros escritores. Conjuntos independientes, reservas previas y journal exacto; no reutilizar fixtures limpiados.
3. Registrar observación manual del operador y SQL por separado. S-3b utiliza HTTP real saneado, token solo en memoria. No se exigen capturas; no compartir contraseñas/Excel/HAR.
4. Limpiar incluso si falla el caso, verificar ausencia postcommit en conexión independiente y retirar Excel temporal. Un fallo de limpieza es pendiente de recuperación, no éxito.
5. Evaluar requisito–caso–resultado–evidencia–defecto. Cero tests, omisiones o resultados esperados no son aprobación. Si no hay entorno autorizado, registrar **no ejecutado**, no sustituirlo por mocks.

## Tratamiento de defectos y cierre

S-001 (S-2) es un fallo del producto expuesto por pruebas y diferido por el responsable: ninguna reparación pertenece a esta spec. Una futura corrección aprobada debe verificar la reproducción con datos nuevos y repetir casos afectados; hasta entonces conservar **fallido**. Completar una tarea de pruebas no exige que todo el producto apruebe. El cierre diferencia entregables documentales verificados, comportamiento fallido y alcance no evaluado; nunca certifica el MVP completo.

Este procedimiento no añade infraestructura, CI/CD, módulos futuros ni pruebas ejecutadas ficticias. T23 se verifica mediante revisión documental; sus ejemplos de selección son instrucciones, no nuevas ejecuciones funcionales.