# Casos y regresión — SPEC-002/T04

**Estado:** diseño completado; casos **no ejecutados**. Las tablas describen expectativas, no observaciones. Referencias: [spec](spec.md), [plan](plan.md), [inventario de superficies P01–P24](inventory.md), [registro y plantilla de evidencia](test.md), [recursos/carencias](evidence.md#entorno-t03-2026-09-30).

## 1. Modalidades y precondiciones comunes

IDs completos: `SPEC-002/UI-xx/nn`. Un caso parametrizado conserva ID y registra superficie, rol, tema, viewport y variante. **E:** revisión estática/cálculo. **C:** integración frontend controlada, componentes y handlers reales con respuestas sustituidas. **S:** recorrido en navegador con interacción real, declarando si los datos están sustituidos. **R:** API/SQL/persistencia real con autorización nueva. S con datos controlados no acredita sistema end-to-end; ningún doble demuestra SQL, dictado real o proveedor.

Antes de C/S: construcción correspondiente implementada, build servido localmente, navegador/versión/canal identificados, estado inicial reproducible y datos ficticios. Bloquear o interceptar tráfico externo **antes** de montar. No sustituir el componente bajo prueba ni agregar modo mock permanente al producto. Capturar cantidades/métodos/estados, no Authorization, contraseñas, filas Excel crudas ni HAR. Para R, cumplir §4 antes de navegar: incluso GET de configuración de tutor puede escribir.

### Entradas diseñadas, todavía no creadas

| Conjunto | Valores y respuestas |
|---|---|
| D-L | Cada lista con 0/1/11/26/51 filas, IDs estables, última fila única, texto de150 caracteres y cadena sin espacios; dos contextos institucionales cuando aplique |
| D-F | Formulario vacío/válido; email inválido, error de campo/general; respuesta retenida liberada manualmente; 400/403/409/500; timeout tras posible guardado |
| D-X | Excel ficticio con columnas del inventario; cursos created=1/skipped=[]; estudiantes created=1/enrolled=2/skipped=[]; parcial con omisiones, vacío,400,timeout. skipped.row incluye marcador privado sintético para comprobar proyección segura |
| D-K | Trabajos queued/processing/completed/failed/unknown; documento y rechazo de reintento por temporal perdido. PDF 0/1/10/11,20MiB/20MiB+1byte, vacío y extensión inválida; nunca enviados a n8n |
| D-C | Cursos y sesiones A/B; sin cursos/sesiones/historial, tutor no disponible; lectura A retenida mientras B resuelve; mensajes largos/autores/fuentes; Mermaid válido/inválido/grande y descripción presente/ausente |
| D-I | PNG/JPEG/WEBP/GIF sintéticos, ≤4MiB/4MiB/4MiB+1byte, formato ajeno y lectura fallida. Cuatro formatos son objetivo RF-15; UI actual solo acepta PNG/JPEG |
| D-A | Actividades de dos cursos/meses contiguos, múltiples por día, título largo y fecha con offset; métricas0/null/ausentes/límite ilimitado explícito/USD decimal |

## 2. Procedimientos y aserciones

Las precondiciones de cada fila se añaden a las comunes. Repetir variantes por separado y registrar resultados por criterio en [test](test.md), sin aprobar un requisito completo por un único subcaso.

### UI-01 — Dirección visual y arquitectura

RF-1/RF-5/RF-20; RNF-1/RNF-2. E y S visual; P01–P24.

| Caso | Precondición | Pasos | Aserciones esperadas |
|---|---|---|---|
| UI-01/01 | Tokens/consumidores de la construcción implementados | 1.Revisar familias de inventario. 2.Trazar CSS/Vuetify/Tailwind/canvas/SVG a rol. 3.Comparar diff/paquetes | Una fuente de paleta; excepciones justificadas; preflight desactivado; sin valores oscuros paralelos o nuevo framework |
| UI-01/02 | Mismo dataset/viewport de login, administración y chat antes/después | 1.Comparar Claro/Oscuro. 2.Registrar juicio concreto del responsable | Claro blanco/menta inspirador; Oscuro verde suavizado, sin grandes fondos carbón. Aprobación estética atribuida, no inferida desde hex/contraste |
| UI-01/03 | Componentes migrados y todos sus consumidores | 1.Revisar props/emits/slots/catálogo. 2.Accionar intención por consumidor. 3.Revisar servicios/backend | Sin HTTP/negocio oculto ni contratos viejos; una intención por acción; sin CRUD universal ni cambio de reglas/esquema |

### UI-02 — Apariencia y persistencia

RF-2/RF-3/RF-4; RNF-4/RNF-7. C y S de build servido; login/tres shells/overlays.

| Caso | Precondición | Pasos | Aserciones esperadas |
|---|---|---|---|
| UI-02/01 | Sin preferencia, SO claro/oscuro; luego preferencia opuesta, caché fría | 1.Cargar directo rutas permitidas. 2.Observar filmstrip/primer contenido/selector. 3.Repetir variantes | Sistema default; elección explícita vence al SO; sin flash opuesto antes de contenido ni HTTP por tema |
| UI-02/02 | Storage corrupto/ausente, excepción getItem/setItem, matchMedia ausente (variantes) | 1.Cargar. 2.Cambiar. 3.Recargar. 4.Logout y otro contexto | Fallback válido y arranque útil; memoria funciona sin persistencia; sin matchMedia acaba en Claro; logout conserva solo apariencia no sensible |
| UI-02/03 | Dos pestañas, Sistema y luego explícito | 1.Cambiar SO. 2.Cambiar preferencia en otra pestaña. 3.Retirar/corromper clave. 4.Contar handlers | Sistema sigue SO, explícito no; sincronización/fallback sin bucles ni listeners duplicados |
| UI-02/04 | Form dirty con cursor; imagen/dictado; envío retenido; diálogo/drawer/menú/tooltip/date-picker/snackbar (variantes) | 1.Registrar foco/valores/identidad/llamadas. 2.Cambiar tema. 3.Continuar operación | Sin remount/pérdida/reinicio/HTTP adicional; overlays/calendario/Mermaid adaptados; imágenes intactas |
| UI-02/05 | Encabezados/login en desktop y320 CSS | 1.Alcanzar selector por teclado. 2.Elegir tres opciones. 3.Leer nombre/estado | Visible/alcanzable en móvil y cada rol; español y estado coherente con apariencia aplicada |

### UI-03 — Navegación y auth

RF-6/RF-10; RNF-6/RNF-7. C/S; R separado en §4.

| Caso | Precondición | Pasos | Aserciones esperadas |
|---|---|---|---|
| UI-03/01 | Anónimo/cada rol, rutas del inventario | 1.Login válido/error. 2.Directo a ruta propia/ajena. 3.Recargar/back/forward. 4.URL desconocida/detalle404 | Guards intactos, sin datos ajenos/bucles; título/foco/destino correctos; salida clara de recurso ausente |
| UI-03/02 | 26 cursos, filtro/página2 y tabs detalle | 1.Abrir curso/tab. 2.Volver por enlace/historial. 3.Repetir tras eliminar última fila con doble | Conserva contexto o ajusta última página válida; tabs no se convierten en rutas ni peticiones de tema |
| UI-03/03 | Trigger drawer móvil enfocado; tres roles y variante desktop | 1.Abrir. 2.Tab/ShiftTab extremos. 3.Intentar fondo. 4.Escape/cerrar/backdrop/seleccionar destino | Móvil modal: fondo no interactuable, foco contenido/retornado; navegación enfoca destino. Drawer permanente desktop no bloquea contenido |
| UI-03/04 | Dirty/chat/dictado/lectura retenida,401/403 | 1.Liberar401 y luego lectura tardía. 2.Back tras login. 3.Repetir403 con sesión válida | Expiración segura limpia privados/detiene dictado, nada reaparece;403 no hace logout ni filtra entidad; sin bucles |

### UI-04 — Formularios y decisiones

RF-7/RF-8/RF-9/RF-10/RF-18; RNF-3/RNF-6. D-F, C/S. Parametrizar login, formularios superadmin, curso/estudiante/cuenta/institución/tutor y **los tres perfiles**, no solo piloto.

| Caso | Precondición | Pasos | Aserciones esperadas |
|---|---|---|---|
| UI-04/01 | Campos inválidos, teclado y lector cuando disponible | 1.Enviar. 2.Leer/corregir errores. 3.Probar autocomplete/gestor con datos ficticios | Label/ayuda/error asociados en español; foco primer inválido; no depende de color; no pérdida de valores ni bloqueo arbitrario de autocomplete |
| UI-04/02 | Respuesta válida retenida | 1.Doble clic/Enter. 2.Cambiar tema. 3.Liberar éxito/fallo | Una operación/pending local; no cierre previo; éxito confirmado, fallo conserva edición/error localizable; aviso no roba foco |
| UI-04/03 | Dirty con ruta/tab/cierre (variantes) | 1.Salir→Permanecer. 2.Salir→Descartar. 3.Repetir limpio/guardado/pending | Permanecer conserva valores/foco; descartar abandona; limpio sin aviso; pending no finge cancelar transacción ni recuperar borrador tras cierre |
| UI-04/04 | Acción destructiva y trigger enfocado | 1.Abrir/revisar identidad/consecuencia. 2.Cancelar. 3.Confirmar con respuesta retenida. 4.Liberar403/error/éxito | Trap/restore; cancelar cero mutaciones; una confirmación, no retiro ante fallo; cuenta/matrícula/archivo/archivo de conversación diferenciados |
| UI-04/05 | Timeout después de posible commit y marcador técnico en error | 1.Enviar. 2.Liberar timeout/error. 3.Esperar/cambiar tema. 4.Consultar explícitamente | Resultado no confirmado, sin éxito/reintento automático; error seguro sin SQL/traceback/token/rutas; privados no persistidos |
| UI-04/06 | Lecturas lenta/vacía/sin coincidencias/500 y A/B fuera de orden | 1.Visitar. 2.Resolver variantes. 3.Pedir B, liberar A antigua | Estados distintos; solo identidad vigente actualiza; retry de lectura explícito; sin mutaciones por recarga/estado |

### UI-05 — Listas y Excel

RF-7/RF-11/RF-12/RF-18; RNF-7. P03–P06/P09/P11/P14, D-L/D-X, C/S; S-2 real aparte.

| Caso | Precondición | Pasos | Aserciones esperadas |
|---|---|---|---|
| UI-05/01 | Cada listado,0/1/11/26/51 filas | 1.Tamaño10/25/50. 2.Última fila/acción. 3.Filtrar a0/restablecer. 4.Eliminar última de última página con doble | Todas las filas/acciones accesibles, cuenta/página válidas; búsqueda local declarada, no paginación API inventada |
| UI-05/02 | Texto largo,320 CSS | 1.Teclado/scroll región. 2.Cambiar filtro/contexto | Sin overflow global ni acciones cortadas; scroll bidimensional propio nombrado; no resultado de contexto anterior |
| UI-05/03 | Excel cursos/estudiantes, sin envío real | 1.Revisar ayuda/aliases. 2.Elegir/cancelar/retirar/reseleccionar. 3.Leer selección | Columnas correctas/password condicional; .xlsx compatible sin prometer .xls; selección visible. Bloqueo previo se registra **sin reparar binding/importador** |
| UI-05/04 | D-X sustituido en límite servicio/presentación | 1.Presentar éxito/parcial/vacío/400/timeout. 2.Cambiar tema/volver. 3.Descartar/nuevo. 4.Buscar marcador privado | Contadores fieles, parcial explícito y resumen consultable; proyección segura sin skipped.row crudo. No acredita envío/persistencia ni subsana S-2 |

### UI-06 — Tutor/RAG

RF-7/RF-8/RF-9/RF-13/RF-18; RNF-6/RNF-7. P12/P13, D-F/D-K, C/S controlados.

| Caso | Precondición | Pasos | Aserciones esperadas |
|---|---|---|---|
| UI-06/01 | Config tutor ficticia y guardado retenido | 1.Editar opciones/prompt/temperatura. 2.Salir/permanecer. 3.Guardar éxito/error/timeout | Dirty/pending coherentes; conserva reglas/payload; no IA al elegir opciones/tema ni guardado tácito |
| UI-06/02 | PDF D-K, upload bloqueado/interceptado | 1.Elegir variantes cantidad/tamaño/extensión/vacío. 2.Retirar/reseleccionar. 3.Confirmar permitido | Ayuda10×20MiB/error corregible; multipart files existente; sin porcentaje ficticio ni bytes a proveedor |
| UI-06/03 | Cinco estados/lectura fuera de orden | 1.Mostrar cada estado. 2.Cambiar curso. 3.Liberar lectura vieja | Etiquetas españolas/unknown honesto; sin porcentajes; solo documentos/trabajos vigentes, error sin internos |
| UI-06/04 | Failed, temporal perdido, respuestas operaciones | 1.Reintentar explícito/rechazo. 2.Eliminar documento→cancelar. 3.Limpiar curso→confirmar/timeout | No promesa de recuperación; archivo/curso y consecuencias distintas; contratos existentes; timeout no borra ni relanza |

### UI-07 — Asistente y recursos

RF-7/RF-9/RF-10/RF-14/RF-15/RF-16/RF-18; RNF-3/RNF-4/RNF-5/RNF-6/RNF-7. P19–P21, D-C/D-I, C/S controlados; dictado real identificado por separado.

| Caso | Precondición | Pasos | Aserciones esperadas |
|---|---|---|---|
| UI-07/01 | Sin cursos/sesiones/historial; tutor indisponible | 1.Abrir/crear sesión con doble. 2.Elegir modos permitidos/deshabilitados | Estados/contexto claros; cambiar tema/modo no envía ni consume IA |
| UI-07/02 | A lenta/B rápida, historial largo/autores/fuentes | 1.Abrir A/B, liberar A. 2.Leer arriba/recibir mensaje. 3.Repetir al final | Sin contaminación; autores/fuentes legibles sin inventarlas; arriba mantiene posición/ofrece final, abajo sigue final |
| UI-07/03 | Envío por cada modo retenido, borrador | 1.Enter. 2.Repetir Enter/clic pending. 3.ShiftEnter. 4.Enter durante IME. 5.Cambiar modo | Una intención, salto de línea, IME no envía; pending bloquea incompatibles; conserva payload de cada modo |
| UI-07/04 | Imágenes D-I/lectura fallida | 1.Adjuntar variantes. 2.Preview/nombre/error. 3.Retirar/reseleccionar. 4.Tema | Cuatro formatos objetivo≤4MiB; corrección posible; selección intacta/sin inversión; payload conservado y URL temporal revocada si existe |
| UI-07/05 | SpeechRecognition soportado/ausente/denegado/error; voz ficticia consentida para variante real | 1.Comprobar inactivo. 2.Activar explícito. 3.Dictar/tema/detener. 4.Salir/401 | Sin inicio/envío automático, estado visible; parada al salir; escritura manual útil; sin audio en API ni texto persistido. Dobles no acreditan navegador real |
| UI-07/06 | Borrador texto/imagen en A | 1.Intentar sesión B/curso/sección. 2.Permanecer. 3.Descartar. 4.Logout/401 | No transferir borrador; retener/limpiar según decisión; auth elimina privados sin opción de guardado inseguro |
| UI-07/07 | Timeout después de posible envío | 1.Enviar. 2.Timeout. 3.Tema/modo. 4.Consultar historial explícitamente | Incertidumbre honesta, sin reenvío/duplicación/éxito ficticio |
| UI-07/08 | Mermaid válido/inválido/grande, vecino válido | 1.Renderizar. 2.Tema/contenido durante render. 3.Fuente. 4.Markup con script/URL no permitido | Error local, solo última identidad pinta; DOMPurify intacto/fuente escapada; sin scripts/fetch externo ni fallo total del chat |
| UI-07/09 | Diagrama con descripción suministrada/ausente | 1.Ampliar teclado. 2.Zoom/scroll. 3.Escape/volver. 4.Leer alternativa | Trap/restore/controles accesibles; descripción existente visible; fuente técnica no se declara equivalente accesible; ausencia se registra, no se genera contenido |

### UI-08 — Lectura de agenda/analíticas

RF-4/RF-7/RF-17/RF-18; RNF-3/RNF-7. P15/P16/P22, D-A, C/S controlados.

| Caso | Precondición | Pasos | Aserciones esperadas |
|---|---|---|---|
| UI-08/01 | Calendario/lista mismo dataset | 1.Filtro curso/mes. 2.Comparar IDs/título/tipo/fecha. 3.Mes/curso/vacío/error. 4.Múltiples eventos | Misma información recibida/periodo/filtro, lectura sin hover/truncado; no edición ni nuevo parámetro API de periodo; zona/mes coherentes |
| UI-08/02 | KPIs/filtros D-A/lectura tardía | 1.7/30/90/personalizado. 2.Tipo/curso. 3.Fuera de orden. 4.Leer detalle | Periodo/unidad/USD/porcentaje claros;0≠ausente≠ilimitado; lectura textual equivalente; no recalcular reglas backend |
| UI-08/03 | Suscripción activa/inactiva/ausente y fechas offset | 1.Leer habilitado/usado/disponible/fecha. 2.Tema/viewport. 3.Fallo lectura | No ausencia convertida a0 ni ilimitado inventado; disponibilidad respeta respuesta; unidades/estado sin depender de color |

### UI-09 — Accesibilidad, compatibilidad y rendimiento

RF-1/RF-4/RF-6/RF-8/RF-9/RF-15/RF-16/RF-17/RF-19; RNF-3/RNF-4/RNF-5. S con modalidad de datos declarada; matriz §3.

| Caso | Precondición | Pasos | Aserciones esperadas |
|---|---|---|---|
| UI-09/01 | Ambos temas/normal-hover-focus-selección-error-disabled | 1.Colores computados/composición. 2.Medir contraste. 3.Medir targets | Texto4,5:1/grande3:1; indicadores necesarios3:1;24×24CSS mínimo o excepción justificada,44×44 preferido. Exención decorativa/disabled no exime texto activo |
| UI-09/02 | Solo teclado, patrones/tres roles | 1.Tab/skip-link. 2.Nav/forms/dialog/listas/chat/agenda/diagrama. 3.Activar/cerrar/volver | Orden/nombre/estado correctos; foco visible/no oculto; trap solo modal y salida útil |
| UI-09/03 | Lector identificado/versión | 1.Recorrer patrones. 2.Provocar carga/error/éxito/mensaje. 3.Registrar anuncios | Roles/labels/errores/anuncios útiles; sin robo de foco. Lector ausente→no ejecutado, no pase por DOM |
| UI-09/04 | Viewports §3, texto200 %, reflow400 % sobre1280 CSS | 1.Recorrer. 2.Orientación/teclado virtual/overlay. 3.Reduced-motion | Desde320CSS sin overflow global; región bidimensional nombrada con scroll propio; foco/compositor visibles, efectos reducidos |
| UI-09/05 | Cada navegador/dispositivo real §3 | 1.Recorrido asignado. 2.Versión/canal/viewport. 3.Dictado/fallback | Operación esencial consistente; emulación Windows no acredita Safari/Android; recurso ausente no ejecutado |
| UI-09/06 | Entorno T03 comprobado/datos cargados/caché declarada | 1.Performance/filmstrip input→fotograma. 2.20 muestras de tema+diálogo/drawer/confirmación/tab local. 3.Network | Por interacción19/20≤200ms, todas las muestras registradas; API/IA separado,0 API por tema; tiempo build no acredita latencia UI |
| UI-09/07 | Listeners/timers/dictado/render pendiente | 1.20 entradas/salidas por función. 2.Inspeccionar actividad/listeners. 3.Un evento. 4.Carga Mermaid | Sin acumulación, una reacción por evento y disposición al salir; render viejo no pinta; Mermaid bajo demanda, sin telemetría permanente |

### UI-10 — Regresión/evaluación

RF-20; RNF-1/RNF-2/RNF-6/RNF-7/RNF-8. E y modalidad del caso reutilizado.

| Caso | Precondición | Pasos | Aserciones esperadas |
|---|---|---|---|
| UI-10/01 | Fin de construcción, diff/reportes | 1.Mapear requisito/caso/evidencia. 2.Lint/build versión nueva. 3.Revisar catálogo/contratos | Sin aprobación parcial/antigua; baseline separado de regresión; límites de stack/backend conservados |
| UI-10/02 | Selección §4, autorización nueva para R | 1.Ejecutar. 2.Salida/código/observación. 3.Limpieza/postcommit | IDs originales/evidencia nueva, sin rebajar esperado; ausencia de permiso/recurso→no ejecutado |
| UI-10/03 | Registro/defectos comunicados | 1.Revisar20RF/8RNF. 2.Decisión real del responsable. 3.Veredicto acotado | Prolongar/diferir/investigar atribuido; tarea completada≠producto conforme; no cerrar por silencio |

## 3. Matriz pantalla–estado–tema–viewport

**T:** Claro/Oscuro en cada fila. **V:**320×568,390×844,768×1024,1440×900 CSS en Chrome Windows. Sistema se concentra en UI-02. N=normal,L=carga,V=vacío,F=sin coincidencias,E=error,P=pending,D=dirty,O=overlay. Profundidad del patrón compartido una vez y comprobación de integración en **cada** consumidor; no basta login. F solo donde hay búsqueda/filtro actual; si no aplica, justificar sin crear filtro nuevo. No exigir dirty a región solo lectura.

| Superficie | Rol | Estados aplicables | Tema/viewport | Casos |
|---|---|---|---|---|
| P01 Login | Anónimo | N/E/P/O | T/V | UI-01/02/03/04/09 |
| P02 Shell | Superadmin | N/O | T/V | UI-01/02/03/09 |
| P03 Instituciones | Superadmin | N/L/V/F/E/P/D/O | T/V | UI-04/05/09 |
| P04 Planes | Superadmin | N/L/V/F/E/P/D/O | T/V | UI-04/05/09 |
| P05 Suscripciones | Superadmin | N/L/V/F/E/P/D/O | T/V | UI-04/05/08/09 |
| P06 Coordinadores | Superadmin | N/L/V/F/E/P/D/O | T/V | UI-04/05/09 |
| P07 Perfil | Superadmin | N/L/E/P/D/O | T/V | UI-04/09 |
| P08 Shell | Coordinador | N/O | T/V | UI-01/02/03/09 |
| P09 Cursos | Coordinador | N/L/V/F/E/P/D/O | T/V | UI-03/04/05/09 |
| P10 Detalle/resumen | Coordinador | N/L/E/P/D/O | T/V | UI-03/04/09 |
| P11 Estudiantes/matrículas | Coordinador | N/L/V/F/E/P/D/O | T/V | UI-04/05/09 |
| P12 Tutor | Coordinador | N/L/E/P/D/O | T/V | UI-04/06/09 |
| P13 Conocimiento | Coordinador | N/L/V/E/P/O;cinco estados | T/V | UI-06/09 |
| P14 Cuentas | Coordinador | N/L/V/F/E/P/D/O | T/V | UI-04/05/09 |
| P15 Institución/suscripción | Coordinador | N/L/V/E/P/D/O | T/V | UI-04/08/09 |
| P16 Analíticas | Coordinador | N/L/V/F/E/O | T/V | UI-08/09 |
| P17 Perfil | Coordinador | N/L/E/P/D/O | T/V | UI-04/09 |
| P18 Shell | Estudiante | N/O | T/V | UI-01/02/03/09 |
| P19 Conversación | Estudiante | N/L/V/E/P/D/O | T/V | UI-03/07/09 |
| P20 Compositor | Estudiante | N/E/P/D/O;dictado ausente/activo/denegado | T/V | UI-02/07/09 |
| P21 Recursos/Mermaid | Estudiante | N/L/E/O | T/V | UI-02/07/09 |
| P22 Agenda | Estudiante | N/L/V/F/E/O | T/V | UI-08/09 |
| P23 Perfil | Estudiante | N/L/E/P/D/O | T/V | UI-04/09 |
| P24 Auth/404/overlays | Anónimo/tres roles | E/O y pérdida auth con P/D | T/V | UI-02/03/04/09 |

| Entorno | Recorridos futuros | Disponibilidad/resultado C0 |
|---|---|---|
| Chrome Windows | Barrido T/V completo y casos aplicables; rendimiento/ciclos | Ejecutable detectado, canal/ejecución pendiente; no ejecutado |
| Edge Windows | Login/nav/form/dialog tres roles; estudiante/agenda/diagrama; tema+overlays,Claro/Oscuro,390×844 y1440×900 | Detectado, canal/ejecución pendiente; no ejecutado |
| Firefox Windows | Mismo recorrido representativo Edge,teclado/lector si disponible | No confirmado; no ejecutado |
| Chrome Android real | Login/drawer/tema/form+teclado virtual/chat/imagen/agenda/lista/diagrama;vertical/horizontal;dictado/fallback | No confirmado; no ejecutado |
| Safari iOS real | Mismo recorrido móvil;imagen/teclado/fallback o dictado | No confirmado; no ejecutado |
| Lector identificado | Roles/nombres/errores/anuncios/foco de todos los patrones representativos | No confirmado; no ejecutado |

## 4. Regresión proporcional, autorización y limpieza

Fuentes: [REGRESSION](../../../testing/REGRESSION.md), [README pruebas](../../../testing/README.md), [SYSTEM](../../../testing/SYSTEM.md). En C0 se **excluye ejecución funcional**: solo documentos y lint/build, sin comportamiento modificado. Revisar trazabilidad/integridad no se presenta como A/I/S ejecutados. Las decisiones siguientes rigen consumidores posteriores; conservar IDs/expectativas e historia, no duplicar tests por renombrar spec.

| Caso/riesgo | Decisión posterior y motivo | Esperado/límite |
|---|---|---|
| A1-P1…P5/variantes,capacidad presentada | Reutilizar T94 al cambiar altas/planes/suscripciones | Regla intacta, no prueba SQL/foco |
| A2-P1…P8,normalización/tenant/rol | Reutilizar T94 por estudiantes/cuentas | Identidad/rechazos intactos; no demuestra envío Excel |
| A3-P1…P5/variantes,matrícula/sesión | Reutilizar T94 por creación de conversación |201/400/403/rollback aislado; sin IA |
| Suite aislada actual | Reutilizar23 pruebas completas, runner sin filtro, señalar pertinencia A1/A2/A3 | No discovery global ni porcentaje de cobertura inventado |
| I-1,conteo SQL | Reutilizar T95 por formularios T43/T45/T52 que presentan capacidad | Exclusión ajenos/inactivos; fixture nuevo autorizado |
| I-2/I-3,alta/reutilización/rechazo | Reutilizar T95 por T52/T54; adaptar solo preparación/registro a SPEC-002 | Identidad/conteo real; no cambiar esperado para ocultar importador |
| I-4,matrícula/creación | Reutilizar T95 por T65/T66 |201 con matrícula,403 sin ella, persistencia sin mensajes |
| S-1,rechazo alta visible | Adaptar recorrido visual T96, conservar ID/esperado | Aviso/409 y SQL sin alta, no mock equivalente |
| S-2,Excel estudiantes visible | Adaptar solo recorrido visual T96,conservar200/created1/enrolled2 | Si persiste bloqueo:fallido, sin reparación implícita ni pase por UI-05/04 |
| S-3/S-3b,sesión/denegación | Adaptar recorrido/registro T96 y reutilizar esperado | Sesión visible201/cero mensajes;403 sin sesión;token solo memoria |
| Controles de journals/runner/seguridad | Excluir si soporte intacto por diff; reutilizar pertinentes si se cambia soporte | Sin infraestructura nueva ni autorización histórica transferida |
| Apariencia/foco/estados/archivos | Añadir UI-01…UI-09, ausentes en A/I/S | Integración por construcción T17/18/38/39/63/64/78/79; dobles no proveedor |
| Mensajes/consumo/RAG/notificaciones reales | Excluir por defecto; usar UI-06/07 controlados | Soporte previo no recupera estos datos; si requieren reales, aprobar diseño/fixtures/cleanup específico **antes** |

Si consumidor finalmente no cambia, actualizar selección con diff/motivo antes de omitir; falta permiso/recurso no convierte caso pertinente en aprobado.

### Reglas R obligatorias

1. Confirmar destino local y autorización nueva por operación de preparación/ejecución/limpieza. No usar permisos/fixtures históricos ni descubrir destinos probando credenciales.
2. App detenida y sin otros escritores al preparar/limpiar. Conjunto independiente/journal exacto con reservas previas. Reservar configuración del agente **antes de abrir detalle** porque GET puede crearla.
3. Solo datos ficticios propios; no tocar roles/datos preexistentes ni limpiar por prefijos amplios. Excel efímero fuera de evidencias; sanear filas/auth/capturas.
4. Observación manual/HTTP y SQL se registran por separado. S-3/S-3b no envían mensajes; no ejecutar upload/retry/delete/clear para una captura sin autorización.
5. Limpiar incluso tras fallo mediante journal propio; comprobar ausencia postcommit con conexión independiente; retirar Excel/temporales y conservar reporte saneado. Limpieza fallida→recuperación pendiente, no éxito.

## 5. Cierre del diseño

Diez grupos,48 casos,24 superficies,matriz de estados/temas/viewports y decisiones A/I/S diseñados. Comprobación documental Node:102 enlaces válidos en documentos C0,28 filas RF/RNF únicas,48 IDs de caso únicos,10 grupos y24 superficies presentes; código0. **Ningún caso funcional/de datos ejecutado en T04.** Registrar futuras observaciones según [test](test.md), no copiar aserciones como resultados.