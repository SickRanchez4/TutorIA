# Tareas de SPEC-002 — Interfaz y experiencia de usuario

**Referencias:** [spec aprobada](spec.md), [plan aprobado](plan.md) y [Constitución](../constitution.md).  
**Estado:** T01 respaldada por aprobación explícita del plan y paleta el 2026-10-31; T02–T05 completadas con evidencia histórica de preparación C0. C1–C5 pendientes, sin implementación UI. Lint baseline fallido, build satisfactorio con avisos; completar la captura no aprueba el producto. La consolidación documental no autoriza implementar C1–C5.
**Fecha:** 2026-09-30.
**Actualización documental:** 2026-10-31; no modifica las fechas ni resultados de C0.

## Convenciones de ejecución

- Cada Tnn representa un resultado acotado, con dependencias, requisitos y comprobación. Su identificador completo es `SPEC-002/Tnn`; los RF/RNF de este documento pertenecen a SPEC-002.
- Se conserva literalmente **«Echo cuando»** como etiqueta solicitada. El checkbox es la condición de cierre de la tarea, no una aprobación anticipada del requisito.
- **Dirección visual obligatoria en toda tarea de pantalla:** formalizar y estandarizar la paleta existente con verde y blanco como colores principales, tonos más claros y una experiencia abierta, amable e inspiradora. Claro usa blanco/menta; Oscuro usa verdes desaturados de luminosidad moderada y texto blanco roto, no grandes fondos negros/carbón. Cada migración consume tokens de T06 y revisa hover/foco/selección/disabled/overlays; no basta cambiar el fondo ni conservar colores arbitrarios por vista. Fotografías/documentos mantienen su color.
- Las tareas de implementación se marcan solo con entregable y comprobación satisfactoria registrados. Las de ejecución/evaluación pueden cerrarse tras ejecutar y registrar fallos con decisión del responsable; eso no aprueba el comportamiento fallido. Falta de recurso o prueba no ejecutada no cumple una tarea que exige ejecutarla.
- Cada comprobación deja caso `SPEC-002/UI-xx/caso`, esperado/obtenido, fecha, versión/cambios locales, modalidad, entorno, rol/tema/viewport pertinentes y evidencia saneada. Documentar pasos no equivale a ejecutarlos. En implementación, cubrir ambas variantes y el estado relevante; las verificaciones integrales de C5 amplían, no sustituyen esas comprobaciones.
- Entregables de preparación: [inventario](inventory.md), [registro de pruebas](test.md), [casos y matriz](cases.md) y [baseline lint/build](evidence.md#baseline-de-construcción-t05-2026-09-30). El catálogo del frontend (UI-UX.md en su carpeta de documentación) sigue pendiente de implementación. T03 define resultados por RF/RNF, T04 diseña casos y cada tarea posterior añade sus evidencias al registro.
- No reparar el defecto funcional previo de Excel, cambiar contratos/backend/SQL/n8n ni introducir dependencias sin aprobación. Las tareas de importación se limitan a presentación e interacción; resultados controlados no certifican envío o persistencia real.
- Toda prueba con escrituras reales exige autorización nueva, destino local verificable, fixtures propios y recuperación aprobados. No ejecutar IA/indexación/notificaciones para estilos. No reutilizar permisos históricos; no persistir borradores ni secretos en evidencias.
- Cada construcción termina con integración y sistema parciales, además del tratamiento de defectos PUDS. Tareas independientes de una misma construcción pueden avanzar en paralelo cuando compartan dependencias satisfechas; no ejecutar una etapa sobre resultados incompatibles pendientes sin decisión explícita.

## C0 — Preparación

### T01 — Registrar aprobación del plan
**Requisitos:** RF-20; RNF-1, RNF-7. **Depende de:** ninguna.  
**Entregable:** decisión explícita del responsable sobre plan, paleta concreta verde/blanca, Claro luminoso/Oscuro suavizado, exclusiones y modalidades; no modificar el estado por inferencia.  
**Verificación:** comparar decisión con [plan.md](plan.md), identificando versión y cualquier ajuste solicitado.
- [x] **Echo cuando:** la versión del plan y su paleta concreta tienen aprobación explícita registrada, incluida la dirección luminosa verde/blanca, y las divergencias están resueltas antes de tocar la aplicación.

**Evidencia T01:** [decisión explícita del 2026-10-31](plan.md), «Apruebo el plan actual y su paleta». La marca existía al iniciar C0 sin cabecera coherente; este antecedente se conserva en [C0-G01](test.md). La aprobación se registra ahora, no como una decisión retroactiva de septiembre.

### T02 — Inventariar consumidores y contratos actuales
**Requisitos:** RF-1, RF-5, RF-12, RF-20; RNF-2, RNF-7. **Depende de:** T01.  
**Entregable:** inventario de pantallas/secciones, componentes, contratos y columnas Excel; tabla color actual→rol propuesto con consumidor/origen/estado/tema en Vuetify, Tailwind, CSS, SVG/inline, calendario y Mermaid.  
**Verificación:** contrastar entradas con fuente/baseline, distinguir reutilizar/extraer/conservar y excepciones de contenido externo, sin colores o funciones supuestos.
- [x] **Echo cuando:** cada color propio inventariado tiene función/consumidor y token objetivo o excepción justificada, todas las superficies están identificadas y no se propone reparar el enlace de importación.

**Evidencia T02:** [inventario de superficies, contratos y colores](inventory.md), revisión estática de fuente; no ejecución funcional ni reparación Excel.

### T03 — Crear el registro de pruebas y fijar recursos
**Requisitos:** RF-20; RNF-4, RNF-5, RNF-8. **Depende de:** T01.  
**Entregable:** registro central con 20 RF/8 RNF inicialmente no ejecutados, entorno de rendimiento, navegadores/dispositivos/lector disponibles y plantilla de evidencia.  
**Verificación:** revisar campos de versión, caso, modalidad, resultado, defectos/decisión y limpieza; registrar carencias reales.
- [x] **Echo cuando:** el registro tiene una fila por requisito, entorno medible y recursos confirmados o carencias explícitas, sin resultados inventados.

**Evidencia T03:** [registro inicial de 28 requisitos](test.md) y [recursos/versiones detectados](evidence.md#entorno-t03-2026-09-30). Sin mediciones UI ni pruebas funcionales ejecutadas.

### T04 — Diseñar los casos y la regresión por impacto
**Requisitos:** RF-20; RNF-6, RNF-7, RNF-8. **Depende de:** T02, T03.  
**Entregable:** casos UI-01 a UI-10 con precondiciones/pasos/aserciones; matriz pantalla–estado–tema–viewport y decisión reutilizar/adaptar/añadir/excluir sobre pruebas previas.  
**Verificación:** comprobar cobertura de los criterios de la spec y distinguir respuestas controladas, sistema real y preparación/cleanup de datos propios.
- [x] **Echo cuando:** cada RF/RNF tiene casos diseñados y la selección A/I/S está justificada, sin autorización implícita ni reparación Excel añadida.
- **Evidencia T04:** [48 casos, matriz de superficies y selección de regresión](cases.md). Validación documental satisfactoria; no hay casos funcionales ejecutados.

### T05 — Capturar el baseline de construcción
**Requisitos:** RF-20; RNF-1, RNF-7, RNF-8. **Depende de:** T03.  
**Entregable:** resultados actuales de lint/build y registro de defectos previos, antes del cambio UI.  
**Verificación:** ejecutar scripts actuales del frontend, guardar salida/código y versión; separar errores previos de nuevas regresiones.
- [x] **Echo cuando:** ambas ejecuciones reales y su resultado están registrados, con tratamiento de fallos, sin afirmar que prueban interacción o sistema.

**Evidencia T05:** [baseline, lint real (código1) y build real (código0 con avisos)](evidence.md#baseline-de-construcción-t05-2026-09-30). Fuente intacta; reparación del lint previo pendiente de decisión, no realizada en C0.

## C1 — Apariencia

### T06 — Formalizar la paleta verde/blanca en tokens
**Requisitos:** RF-1, RF-4; RNF-2. **Depende de:** T02, T05.  
**Entregable:** fuente canónica de escala verde/blanca y roles semánticos de ambos temas, incluidos superficie/texto/acción-hover/selección/foco/estados; medidas del catálogo y mapeo T02 resuelto.  
**Verificación:** valores calculados y parejas básicas, escala/usos permitidos, fondo claro blanco/menta y Oscuro verde más luminoso que el baseline; sin paletas por vista.
- [ ] **Echo cuando:** la paleta formalizada define códigos/usos, ambos temas consumen los mismos roles sin valores paralelos, las parejas comprobadas cumplen contraste y los fondos casi negros previos no son las nuevas superficies estructurales.

### T07 — Implementar la resolución de apariencia
**Requisitos:** RF-2, RF-3. **Depende de:** T06.  
**Entregable:** controlador independiente de Vue/usuario/HTTP para light/dark/system, selección y tema resuelto.  
**Verificación:** casos UI-02 con valor ausente/válido/desconocido, sistema claro/oscuro y ausencia de matchMedia.
- [ ] **Echo cuando:** las selecciones se resuelven determinísticamente, Sistema es el valor por defecto y la ausencia de soporte termina en Claro sin fallo de arranque.

### T08 — Añadir persistencia tolerante a fallos
**Requisitos:** RF-3; RNF-6. **Depende de:** T07.  
**Entregable:** lectura/escritura protegidas de la clave de apariencia y selección de pestaña en memoria cuando el almacenamiento falle.  
**Verificación:** bloquear lectura/escritura, recargar con valores corruptos y revisar las claves nuevas almacenadas.
- [ ] **Echo cuando:** storage bloqueado no impide uso/cambio, recarga sigue el fallback y el único dato persistente nuevo es la preferencia no sensible.

### T09 — Sincronizar sistema y pestañas
**Requisitos:** RF-2, RF-3; RNF-4. **Depende de:** T08.  
**Entregable:** suscripción única a sistema/storage y adaptador Vue con disposición explícita.  
**Verificación:** cambio del sistema con selección explícita/Sistema, cambio/eliminación de clave desde otra pestaña y recuento de callbacks.
- [ ] **Echo cuando:** solo Sistema sigue al dispositivo, las pestañas notificadas actualizan su selección y no hay listeners añadidos por vista o callbacks duplicados.

### T10 — Aplicar apariencia antes del contenido
**Requisitos:** RF-3; RNF-4. **Depende de:** T06, T09.  
**Entregable:** hoja y controlador tempranos conectados al HTML inicial, con fondo y color-scheme correctos antes del montaje.  
**Verificación:** carga fría/recarga con preferencia opuesta al sistema en desarrollo y build servido; inspeccionar primeros fotogramas y URLs.
- [ ] **Echo cuando:** los casos registrados no muestran contenido en el tema contrario, no fallan recursos de arranque y la aplicación solo se monta una vez.

### T11 — Conectar los tokens con Vuetify
**Requisitos:** RF-1, RF-2, RF-4; RNF-2. **Depende de:** T10.  
**Entregable:** temas Vuetify Claro/Oscuro obtenidos de tokens, incluidos on-colors y variables necesarias; retirar nodos temporales de lectura.  
**Verificación:** campos, botones, menú y diálogo abiertos en ambas variantes; revisar DOM residual y conservación de foco.
- [ ] **Echo cuando:** Vuetify selecciona la variante resuelta sin paleta literal paralela, restos temporales, remount ni cierre de overlays por cambiar tema.

### T12 — Migrar los estilos globales y Tailwind
**Requisitos:** RF-1, RF-4; RNF-2, RNF-3. **Depende de:** T11.  
**Entregable:** utilidades/globales semánticos de la paleta verde/blanca, opacidades compatibles y retirada de fondos carbón/grises/colores arbitrarios sustituidos según mapeo T02.  
**Verificación:** estilos computados de fondo/texto/bordes/acción y todos sus estados, con excepciones justificadas y preflight desactivado.
- [ ] **Echo cuando:** los colores propios globales migrados apuntan a tokens, no sobreviven fondos negros/carbón como estructura, no se invierten imágenes ni desaparecen contornos Vuetify y la duplicación reemplazada fue retirada.

### T13 — Crear el selector visual de apariencia
**Requisitos:** RF-2, RF-5; RNF-3. **Depende de:** T09, T11.  
**Entregable:** selector con entrada/control de selección, etiquetas españolas y evento; sin storage/HTTP interno.  
**Verificación:** teclado y árbol accesible para Claro/Oscuro/Sistema, incluyendo selección y cambio sin pérdida de foco.
- [ ] **Echo cuando:** se pueden elegir las tres opciones con teclado, sus nombres/selección son accesibles y el selector solo emite intención al contenedor.

### T14 — Integrar apariencia y formulario en login
**Requisitos:** RF-2, RF-4, RF-8, RF-10, RF-18; RNF-3, RNF-6. **Depende de:** T12, T13.  
**Entregable:** login verde/blanco luminoso en Claro y verde suavizado en Oscuro, con selector, etiquetas, ayuda, mostrar contraseña/autocomplete y error genérico seguro; decoración sin gran panel negro heredado.  
**Verificación:** teclado, pegado/gestor, error controlado, texto largo y 320 px; alternar tema con credenciales introducidas.
- [ ] **Echo cuando:** formulario y selector son utilizables en ambos temas, el error no revela existencia de cuenta y cambiar apariencia no pierde datos ni dispara autenticación.

### T15 — Adaptar los efectos a movimiento reducido
**Requisitos:** RF-19; RNF-3, RNF-5. **Depende de:** T12, T14.  
**Entregable:** fallback estático de fondo/tilt/parallax, carga y desplazamiento suave, sin dependencia funcional de animaciones.  
**Verificación:** activar prefers-reduced-motion y observar login/transiciones/carga con y sin soporte decorativo.
- [ ] **Echo cuando:** el modo reducido detiene decoración continua y smooth scroll, conserva indicación estática de estado y no impide ninguna acción.

### T16 — Configurar idioma y formatos compartidos
**Requisitos:** RF-17, RF-18; RNF-2. **Depende de:** T02, T11.  
**Entregable:** locale español de biblioteca/widgets usados y definiciones repetidas de estados/Intl; sin framework multidioma.  
**Verificación:** controles de biblioteca y ejemplos de fecha civil/instante/UTC, USD, cero, ausente e ilimitado.
- [ ] **Echo cuando:** las etiquetas compartidas son españolas y los formatos conservan significado/unidades, sin renombrar campos API ni traducir contenido de usuarios.

### T17 — Ejecutar integración de apariencia
**Requisitos:** RF-1, RF-2, RF-3, RF-4; RNF-2, RNF-4. **Depende de:** T12, T14, T15, T16.  
**Entregable:** resultados UI-01/02 sobre paleta/mapeo, controlador, Vuetify, CSS, selector y overlays conectados.  
**Verificación:** identidad verde/blanca y superficie verde no negra de Oscuro, storage/fallback/pestañas/sistema, diálogo abierto, edición en curso y Network sin nuevas solicitudes API.
- [ ] **Echo cuando:** los casos diseñados se ejecutaron y están registrados con foco/datos/tráfico observado y tratamiento PUDS de cualquier fallo.

### T18 — Ejecutar sistema parcial C1
**Requisitos:** RF-2, RF-3, RF-4, RF-20; RNF-8. **Depende de:** T17.  
**Entregable:** recorrido de login y superficies ya migradas en ambos temas, recarga/logout y móvil pertinente.  
**Verificación:** observación del navegador integrado, diferenciando controles reales de estados simulados y defectos de pantallas aún pendientes.
- [ ] **Echo cuando:** se registró el recorrido real parcial, se actualizaron resultados de C1 y el responsable decidió sobre fallos sin declarar el resto del producto verificado.

## C2 — Patrones e interacción compartidos

### T19 — Extraer la estructura de panel
**Requisitos:** RF-1, RF-5, RF-6, RF-19; RNF-2. **Depende de:** T18.  
**Entregable:** AppShell con slots de contexto/herramientas/contenido, skip link y composición de componentes existentes.  
**Verificación:** revisión del contrato y montaje con navegación suministrada, sin HTTP/tenant/reglas ocultos.
- [ ] **Echo cuando:** el shell presenta una estructura semántica accesible y recibe datos/intenciones, sin convertirse en un componente universal de negocio.

### T20 — Completar el comportamiento del drawer
**Requisitos:** RF-6, RF-19; RNF-3. **Depende de:** T19.  
**Entregable:** RoleSidebar persistente/contraíble en escritorio y modal temporal en móvil con cierre visible/Escape/foco.  
**Verificación:** abrir, tabular, cancelar y seleccionar destino; comprobar fondo inerte y retorno al disparador.
- [ ] **Echo cuando:** el drawer temporal contiene foco/bloquea fondo y lo devuelve al cancelar, cierra al navegar y el modo rail conserva nombres accesibles.

### T21 — Migrar el layout coordinador al shell
**Requisitos:** RF-2, RF-5, RF-6; RNF-7. **Depende de:** T19, T20, T13.  
**Entregable:** layout coordinador consumidor de AppShell/sidebar/selector sin duplicar encabezado.  
**Verificación:** acceder a cada subruta permitida en desktop/móvil y cambiar tema con una edición activa.
- [ ] **Echo cuando:** rutas, sección/contexto y logout del coordinador siguen funcionando y el layout reemplazado no conserva estructura/estilos duplicados.

### T22 — Migrar el shell del superadministrador
**Requisitos:** RF-2, RF-5, RF-6; RNF-7. **Depende de:** T19, T20, T13.  
**Entregable:** dashboard superadmin consumidor del shell, manteniendo sus secciones internas y perfil.  
**Verificación:** navegación por cada sección, nombres accesibles, drawer móvil y cambio de tema con sección activa.
- [ ] **Echo cuando:** todas las secciones previas siguen alcanzables con selección/contexto correctos y no hay un segundo encabezado ni funciones de otro rol.

### T23 — Migrar el shell del estudiante
**Requisitos:** RF-2, RF-5, RF-6; RNF-7. **Depende de:** T19, T20, T13.  
**Entregable:** dashboard estudiante consumidor del shell, conservando asistente/agenda/perfil.  
**Verificación:** navegación móvil/desktop, cambio de tema con texto activo y ausencia de creación de sesión por montaje visual.
- [ ] **Echo cuando:** las tres secciones permanecen disponibles, el cambio visual conserva estado y no crea conversaciones ni solicitudes por sí solo.

### T24 — Unificar título y acciones de página
**Requisitos:** RF-1, RF-5; RNF-2. **Depende de:** T02, T19.  
**Entregable:** patrón de encabezado compartido en consumidores repetidos, conservando PanelTitle donde corresponde.  
**Verificación:** jerarquía HTML/título/acción principal en listado de cursos y una sección administrativa; justificar composición sin wrapper si es suficiente.
- [ ] **Echo cuando:** los consumidores identificados usan el mismo patrón semántico y no quedan copias sustituidas o una envoltura sin responsabilidad.

### T25 — Implementar estados de región
**Requisitos:** RF-5, RF-7; RNF-3. **Depende de:** T19.  
**Entregable:** AsyncState con carga, vacío inicial, sin coincidencias, fallo e indisponibilidad y reintento manual permitido.  
**Verificación:** cinco estados controlados, aria-busy/anuncio y contenido previo confirmado cuando corresponda.
- [ ] **Echo cuando:** los estados son distintos, carga no simula cero/vacío y el reintento emite intención sin llamadas ni mutaciones automáticas.

### T26 — Unificar avisos y errores persistentes
**Requisitos:** RF-5, RF-7, RF-18; RNF-3, RNF-6. **Depende de:** T21, T22, T23.  
**Entregable:** patrón de avisos reutilizado por tres paneles, con éxito breve y errores accionables persistentes/localizables.  
**Verificación:** sucesión de avisos, lectura de estado, descarte explícito y ausencia de foco robado o error que desaparece prematuramente.
- [ ] **Echo cuando:** cada panel tiene una sola región pertinente y la gravedad/acción determina duración sin borrar un error necesario para corregir la tarea.

### T27 — Implementar la confirmación compartida
**Requisitos:** RF-5, RF-9; RNF-3. **Depende de:** T19.  
**Entregable:** ConfirmDialog con identidad/consecuencia, confirmación/cierre y pendiente, sin operación HTTP interna.  
**Verificación:** tab/Escape/foco inicial no destructivo, origen eliminado, pendiente y timeout simulado.
- [ ] **Echo cuando:** foco queda contenido y vuelve a destino válido, los botones son inequívocos y nunca se ofrece cancelar una mutación no cancelable.

### T28 — Implementar el guard de cambios sin guardar
**Requisitos:** RF-8, RF-9; RNF-6. **Depende de:** T27.  
**Entregable:** patrón compartido de snapshot/dirty/stay-discard, conexión SPA y beforeunload condicionado; sin persistencia.  
**Verificación:** edición, intento de salida/cierre, permanecer/descartar, tema y desmontaje; estado pendiente no cambia por una lectura tardía.
- [ ] **Echo cuando:** solo una edición real solicita decisión, cambiar tema no la dispara y listeners se retiran sin prometer recuperación tras recarga.

### T29 — Adaptar el contrato de ProfileSection
**Requisitos:** RF-5, RF-8, RF-9; RNF-2, RNF-6. **Depende de:** T25, T28.  
**Entregable:** perfil con estados por operación, validación/errores y resultado comunicado por contenedor, conservando eventos existentes.  
**Verificación:** respuesta confirmada/fallo/retrasada, foco de primer error, snapshot de edición y tratamiento sensible de contraseñas.
- [ ] **Echo cuando:** emitir no se considera confirmación de guardado, fallo conserva valores permitidos y el componente no llama servicios ni limpia edición prematuramente.

### T30 — Integrar el perfil en los tres roles
**Requisitos:** RF-5, RF-8, RF-9; RNF-7. **Depende de:** T21, T22, T23, T29.  
**Entregable:** todos los consumidores de ProfileSection adaptados al mismo contrato; servicios de cada rol en contenedores.  
**Verificación:** guardar/error/cambiar contraseña y salida con cambios en cada consumidor, con respuestas controladas identificadas.
- [ ] **Echo cuando:** ningún consumidor usa el contrato viejo, los resultados reales/controlados se distinguen y los tres perfiles respetan foco/pending/dirty sin duplicar formularios.

### T31 — Implementar el estado local de listados
**Requisitos:** RF-11; RNF-2, RNF-7. **Depende de:** T02.  
**Entregable:** patrón de filtros/orden/página del conjunto recibido, 10/25/50 por página y página válida tras cambios.  
**Verificación:** 0/1/11/26 filas, filtro sin coincidencias y eliminación del último registro de página.
- [ ] **Echo cuando:** se recorren todos los registros recibidos con conteo correcto y filtrar/paginar no cambia contratos ni promete búsqueda global.

### T32 — Gestionar título y foco de navegación
**Requisitos:** RF-6, RF-19; RNF-3. **Depende de:** T21, T22, T23.  
**Entregable:** título documental/foco al cambiar ruta y semántica de pestañas internas por rol.  
**Verificación:** navegación adelante/atrás, guard redirigido y cambio de pestaña con teclado, sin robar foco por cambio de tema.
- [ ] **Echo cuando:** cada destino identifica sección y sitúa foco pertinente; pestañas anuncian selección y respetan su patrón de teclado.

### T33 — Presentar rutas y recursos no disponibles
**Requisitos:** RF-10; RNF-6, RNF-7. **Depende de:** T25, T32.  
**Entregable:** presentación not-found/recurso no disponible con salida segura al destino permitido.  
**Verificación:** URL inexistente sin sesión/con cada rol y recurso inaccesible controlado.
- [ ] **Echo cuando:** no hay página vacía/bucle ni revelación de entidad ajena, se conservan rutas válidas/guards y hay retorno operable.

### T34 — Unificar errores públicos e incertidumbre
**Requisitos:** RF-7, RF-10; RNF-6, RNF-7. **Depende de:** T25, T26.  
**Entregable:** presentación segura de 403/red/error interno/timeout, manteniendo status y contrato originales.  
**Verificación:** respuestas controladas con excepción/datos crudos y mutación posiblemente confirmada, seguida de acción de consulta.
- [ ] **Echo cuando:** se muestran mensajes españoles seguros, timeout no afirma que nada se guardó y no existe reintento automático de mutaciones/IA.

### T35 — Limpiar estado privado al cerrar sesión
**Requisitos:** RF-3, RF-10, RF-15; RNF-6. **Depende de:** T28, T30, T34.  
**Entregable:** logout/401 coordinado con vistas, invalidación de pendientes, archivos/avisos/ediciones y escuchas existentes.  
**Verificación:** expirar sesión durante edición y respuesta tardía; iniciar otra cuenta y comprobar storage/DOM/estado en memoria.
- [ ] **Echo cuando:** no reaparecen datos privados ni bloquea el dirty guard la salida de seguridad, se explica la expiración y solo apariencia nueva persiste.

### T36 — Evitar resultados visuales obsoletos
**Requisitos:** RF-7; RNF-7. **Depende de:** T25, T35.  
**Entregable:** patrón de identidad/secuencia de lectura aplicado a un consumidor y documentado para los siguientes; no cancelar ficticiamente mutaciones.  
**Verificación:** dos selecciones con respuestas/finally invertidos y desmontaje antes de finalizar.
- [ ] **Echo cuando:** ni datos ni loading/error de la selección actual son reemplazados por el contexto anterior y la prueba identifica el consumidor integrado.

### T37 — Aplicar pendiente y errores al formulario piloto
**Requisitos:** RF-7, RF-8, RF-9, RF-10; RNF-3. **Depende de:** T27, T28, T34.  
**Entregable:** un formulario existente de curso como referencia de etiquetas, errores asociados, pending por operación y cierre tras respuesta/timeout.  
**Verificación:** doble clic/Enter, rechazo, primer error, consulta tras resultado incierto y salida con cambios.
- [ ] **Echo cuando:** hay un solo envío desde el control, valores permitidos sobreviven al fallo y el patrón queda documentado sin un framework de formularios nuevo.

### T38 — Ejecutar integración de patrones C2
**Requisitos:** RF-5 a RF-11, RF-20; RNF-2, RNF-3, RNF-6, RNF-7. **Depende de:** T24, T30, T31, T33, T35, T36, T37.  
**Entregable:** resultados UI-03/04/05 parciales sobre consumidores reales, guards, servicios y respuestas controladas.  
**Verificación:** foco/drawer/diálogos/dirty, errores/pending y lecturas tardías en los tres roles.
- [ ] **Echo cuando:** los casos de C2 se ejecutaron y registraron con consumidores/modalidades y todos los fallos tienen decisión PUDS.

### T39 — Ejecutar sistema parcial C2
**Requisitos:** RF-6, RF-8, RF-9, RF-10, RF-20; RNF-8. **Depende de:** T38.  
**Entregable:** recorrido integrado de navegación y perfil por rol en ambos temas y móvil pertinente.  
**Verificación:** login, ruta/pestaña, drawer, perfil, descarte y expiración con fixtures autorizados cuando haya escrituras.
- [ ] **Echo cuando:** el recorrido parcial tiene observación real y limpieza pertinente, y bloqueos/cobertura no ejecutada se distinguen de resultados aprobados.

## C3 — Administración y coordinación

### T40 — Adaptar el listado de instituciones
**Requisitos:** RF-1, RF-4, RF-7, RF-11. **Depende de:** T39.  
**Entregable:** lista de instituciones con estado, contexto, acciones nombradas y paginación/filtros actuales.  
**Verificación:** UI-05 con 0/11/26 filas, búsqueda sin resultados y textos largos en ambas variantes.
- [ ] **Echo cuando:** todas las filas/acciones son alcanzables, vacío y sin coincidencias son distintos y no existe overflow horizontal global.

### T41 — Adaptar formularios de institución
**Requisitos:** RF-7, RF-8, RF-9, RF-10. **Depende de:** T40, T37.  
**Entregable:** creación/edición/eliminación actuales con pending, dirty, errores y confirmación identificable.  
**Verificación:** éxito/fallo/timeout controlados y eliminación de última fila con contexto conservado.
- [ ] **Echo cuando:** cada operación usa su resultado real, mantiene edición permitida ante error y confirma consecuencias sin duplicar reglas de institución.

### T42 — Adaptar el listado de planes
**Requisitos:** RF-4, RF-7, RF-11, RF-18. **Depende de:** T39.  
**Entregable:** lista de planes con datos/estados y acciones actuales, conteo local y etiquetas claras de capacidad.  
**Verificación:** carga/vacío, tamaño de página, nombre largo y capacidad ausente/cero/ilimitada recibida.
- [ ] **Echo cuando:** filas y acciones se recorren en ambos temas y las capacidades se presentan sin inventar límites o cálculos de negocio.

### T43 — Adaptar formularios de planes
**Requisitos:** RF-7, RF-8, RF-9, RF-10. **Depende de:** T42, T37.  
**Entregable:** operaciones actuales de plan con etiquetas, errores, pending/descarte y confirmación pertinente.  
**Verificación:** guardar/rechazo/incertidumbre y actualización del listado con respuesta confirmada.
- [ ] **Echo cuando:** no hay doble envío ni cierre por falso éxito y ningún campo/regla del contrato cambió por el rediseño.

### T44 — Adaptar el listado de suscripciones
**Requisitos:** RF-4, RF-7, RF-11, RF-17. **Depende de:** T39, T16.  
**Entregable:** lectura de suscripciones con institución, estado, periodo, unidades y filtros existentes.  
**Verificación:** cero/ausente/ilimitado, fecha relevante, múltiples instituciones y paginación local.
- [ ] **Echo cuando:** se identifica institución/periodo de cada registro, no se confunden ausencias con cero y todos los datos/acciones son accesibles.

### T45 — Adaptar formularios de suscripción
**Requisitos:** RF-7, RF-8, RF-9, RF-10. **Depende de:** T44, T37.  
**Entregable:** operaciones existentes de suscripción con contexto institucional visible, validación comprensible y pending.  
**Verificación:** respuesta confirmada/rechazo/timeout y salida con edición, sin modificar cálculos o vigencia.
- [ ] **Echo cuando:** el usuario conoce el alcance de la acción y se conservan valores/contrato/autoridad backend en fallo y éxito.

### T46 — Adaptar el listado de coordinadores
**Requisitos:** RF-4, RF-7, RF-11. **Depende de:** T39.  
**Entregable:** filtro institucional/búsqueda/lista y acciones nombradas con estados coherentes.  
**Verificación:** cambio de institución con respuestas invertidas, filtro vacío y múltiples páginas.
- [ ] **Echo cuando:** no se mezcla información de selecciones anteriores y el alcance de búsqueda se limita explícitamente al conjunto cargado.

### T47 — Adaptar formularios de coordinador
**Requisitos:** RF-7, RF-8, RF-9, RF-10; RNF-6. **Depende de:** T46, T37.  
**Entregable:** alta/edición/eliminación actuales, tratamiento sensible de credenciales y confirmación contextual.  
**Verificación:** rechazo, guardado, doble envío y abandono de edición con campos sensibles.
- [ ] **Echo cuando:** entidad/institución/consecuencia están claras, los errores son seguros y no se persisten ni se incluyen credenciales en evidencia.

### T48 — Adaptar el listado y retorno de cursos
**Requisitos:** RF-4, RF-6, RF-7, RF-11. **Depende de:** T39.  
**Entregable:** listado de cursos y memoria de filtros/página durante ida a detalle y retorno, sin localStorage nuevo.  
**Verificación:** búsqueda/página→detalle→volver, última fila retirada y 320 px.
- [ ] **Echo cuando:** el retorno conserva contexto válido, ajusta páginas inválidas y ofrece todos los datos/acciones sin romper el ancho global.

### T49 — Adaptar el formulario de curso
**Requisitos:** RF-7, RF-8, RF-9, RF-10. **Depende de:** T48, T37.  
**Entregable:** patrón piloto completado en operaciones de curso existentes con actualización confirmada del listado.  
**Verificación:** error/pending/descarte y éxito conservando página/filtro, sin incluir envío Excel.
- [ ] **Echo cuando:** crear/editar curso conserva contratos, errores/estado/foco coherentes y no se muestra éxito sin confirmación.

### T50 — Adaptar los datos del detalle de curso
**Requisitos:** RF-4, RF-6, RF-8, RF-9. **Depende de:** T48, T49.  
**Entregable:** bloque de datos/estado/opciones actuales con título, retorno, edición pendiente y confirmaciones pertinentes.  
**Verificación:** entrar a distintos cursos, edición/rechazo/descarte e inhabilitación/eliminación controladas.
- [ ] **Echo cuando:** identidad de curso y alcance de cada acción son visibles, respuestas obsoletas no reemplazan contexto y la edición usa el patrón compartido.

### T51 — Adaptar el listado de estudiantes y matrículas
**Requisitos:** RF-4, RF-7, RF-11. **Depende de:** T50.  
**Entregable:** listado del curso con estados de matrícula/datos/acciones actuales y región responsive.  
**Verificación:** carga/vacío/filtrado donde exista, páginas, nombres largos y curso cambiado durante lectura.
- [ ] **Echo cuando:** todas las filas/datos/acciones se pueden consultar y el estado de matrícula no depende solo del color ni de una regla cliente nueva.

### T52 — Adaptar formularios manuales de estudiantes del curso
**Requisitos:** RF-7, RF-8, RF-9, RF-10. **Depende de:** T51, T37.  
**Entregable:** alta/edición/retirada manuales disponibles con etiquetas, resultados y confirmación de alcance real.  
**Verificación:** capacidad/rechazo controlados, doble clic, éxito y dirty; mantener importación fuera de esta tarea.
- [ ] **Echo cuando:** rechazos backend se respetan, no se confunden cuenta y matrícula y solo una respuesta confirmada actualiza el listado.

### T53 — Adaptar el listado de cuentas
**Requisitos:** RF-4, RF-7, RF-11. **Depende de:** T39.  
**Entregable:** lista/búsqueda de cuentas con estados/acciones legibles y paginación local.  
**Verificación:** 0/11/26 cuentas, sin coincidencias, datos largos y desplazamiento interno con teclado.
- [ ] **Echo cuando:** se mantienen filtros/orden existentes, el conteo es fiel y todas las acciones/datos siguen disponibles en móvil.

### T54 — Adaptar la edición y eliminación de cuentas
**Requisitos:** RF-7, RF-8, RF-9, RF-10; RNF-6. **Depende de:** T53, T37.  
**Entregable:** operaciones actuales con dirty/pending, error seguro y confirmación de cuenta identificable.  
**Verificación:** campo inválido/rechazo/timeout, credenciales sensibles y última fila de página.
- [ ] **Echo cuando:** edición no se pierde por fallo, la consecuencia se describe sin promesa falsa y el listado queda válido después de éxito confirmado.

### T55 — Adaptar la presentación de Excel de cursos
**Requisitos:** RF-12, RF-18; RNF-7. **Depende de:** T49, T02.  
**Entregable:** nombre/retirada/sustitución, ayuda de formato/columnas reales y resumen consultable de resultados recibidos.  
**Verificación:** cancelar/reseleccionar y respuestas completas/parciales/rechazadas controladas; revisar diff del binding/manejador/servicio.
- [ ] **Echo cuando:** ayuda/selección/resumen son verificables sin autoenvío ni falso éxito y no se reparó ni modificó el enlace de importación excluido.

### T56 — Adaptar la presentación de Excel de estudiantes
**Requisitos:** RF-12, RF-18; RNF-7. **Depende de:** T51, T02.  
**Entregable:** presentación consistente del flujo existente de estudiantes, manteniendo su control/envío previo y limitándose a ayuda/selección/resumen.  
**Verificación:** UI-05 controlado, estado sin archivo/error/parcial y revisión del enlace intacto; registrar bloqueos reales por separado.
- [ ] **Echo cuando:** los criterios visuales de RF-12 tienen evidencia y ningún ajuste del selector–manejador–servicio solucionó implícitamente el defecto previo.

### T57 — Adaptar institución y suscripción del coordinador
**Requisitos:** RF-4, RF-8, RF-9, RF-17. **Depende de:** T39, T16, T37.  
**Entregable:** edición de datos existente y lectura de plan/consumo/capacidad/fechas, con unidades y estados claros.  
**Verificación:** error de edición, cero/ausente/ilimitado, vencimiento y textos largos en ambos temas.
- [ ] **Echo cuando:** se distingue edición de lectura y capacidad de consumo, no hay división inválida ni cambios en reglas/periodos backend.

### T58 — Adaptar analíticas y lectura equivalente
**Requisitos:** RF-4, RF-7, RF-17, RF-18. **Depende de:** T39, T16, T36.  
**Entregable:** filtros actuales de periodo/tipo, KPIs/desgloses y valores/texto equivalentes; costos estimados USD.  
**Verificación:** periodos 7/30/90/personalizado, lecturas invertidas, ausencia/cero y consulta sin hover/color.
- [ ] **Echo cuando:** filtros/periodo/unidad son visibles, los valores se leen sin gráfico y el resultado tardío no sobrescribe la selección actual.

### T59 — Separar el formulario de configuración del tutor
**Requisitos:** RF-5, RF-8, RF-9, RF-13. **Depende de:** T50, T37.  
**Entregable:** TutorSettingsForm con prompt/temperatura/modos/opciones actuales y estado dirty/pending comunicado al contenedor.  
**Verificación:** edición, rechazo, descarte, respuesta confirmada y contrato de props/eventos sin HTTP.
- [ ] **Echo cuando:** valores guardados/editados se distinguen, errores no pierden edición permitida y no se cambian prompts/modelos o reglas por razones ajenas a presentación.

### T60 — Adaptar la selección de PDF
**Requisitos:** RF-5, RF-13; RNF-7. **Depende de:** T50.  
**Entregable:** bloque de carga con curso, archivos seleccionados/nombres/retirada, ayuda de hasta 10 PDF y 20 MiB por archivo.  
**Verificación:** límites exactos/excedidos, selección múltiple/error y estado pendiente controlados, sin indexación real.
- [ ] **Echo cuando:** ayuda y comprobación orientativa son claras, el servidor sigue siendo autoridad y no se inventan porcentajes/cancelación o límites nuevos.

### T61 — Presentar documentos y estados de trabajos
**Requisitos:** RF-5, RF-7, RF-13, RF-18; RNF-6. **Depende de:** T60, T16, T36.  
**Entregable:** KnowledgePanel con resumen/documentos y cinco estados traducidos, reintentos únicamente soportados.  
**Verificación:** queued/processing/completed/failed/unknown, lectura tardía y pérdida de archivos temporales con respuestas controladas.
- [ ] **Echo cuando:** cada estado/action refleja el contrato, no muestra logs/rutas privadas ni progreso ficticio y un reintento imposible no promete recuperación.

### T62 — Diferenciar eliminar documento y limpiar conocimiento
**Requisitos:** RF-9, RF-13; RNF-7. **Depende de:** T61, T27.  
**Entregable:** confirmaciones separadas de entidad/consecuencia para las dos acciones existentes.  
**Verificación:** cancelar/confirmar/pending/rechazo/timeout controlados con foco y actualización confirmada.
- [ ] **Echo cuando:** la identidad y el alcance de ambas acciones son inequívocos y no se ofrece cancelación del procesamiento ni limpieza optimista falsa.

### T63 — Ejecutar integración de administración C3
**Requisitos:** RF-7 a RF-13, RF-17, RF-18, RF-20; RNF-7, RNF-8. **Depende de:** T41, T43, T45, T47, T52, T54, T55, T56, T57, T58, T59, T62.  
**Entregable:** UI-04/05/06/08 ejecutados sobre todas las secciones migradas con casos controlados identificados.  
**Verificación:** formularios/listados/archivos/tutor y estados reales de lectura donde esté autorizado, sin proveedores.
- [ ] **Echo cuando:** cada sección tiene resultados de integración, los bloques simulados están identificados y los fallos tienen tratamiento documentado sin reparar Excel.

### T64 — Ejecutar sistema parcial C3
**Requisitos:** RF-11, RF-12, RF-13, RF-17, RF-20; RNF-8. **Depende de:** T63.  
**Entregable:** recorrido administrativo y de coordinación integrado en ambos temas y móvil, con preparación/limpieza aprobadas.  
**Verificación:** tarea principal por sección, alta/importación visual, configuración y métricas; registrar importación bloqueada sin aprobarla con mocks.
- [ ] **Echo cuando:** el sistema parcial tiene observación, resultados y decisiones, y se distingue UI comprobada de persistencia/proveedores no acreditados.

## C4 — Estudiante

### T65 — Separar la lista de conversaciones
**Requisitos:** RF-5, RF-14. **Depende de:** T39.  
**Entregable:** ConversationList con selección/título/curso y acciones actuales de crear/abrir/renombrar/archivar emitidas al contenedor.  
**Verificación:** vacío/selección/nombre largo, archivado y respuesta tardía; revisar identidad conservada.
- [ ] **Echo cuando:** las acciones están nombradas y conservan sesión/curso, archivar no promete borrado físico y el componente no llama IA/servicios.

### T66 — Identificar contexto y modos del asistente
**Requisitos:** RF-7, RF-14, RF-18. **Depende de:** T65.  
**Entregable:** curso/conversación/modo visibles y ayudas Consulta/Práctica/Recursos con disponibilidad recibida.  
**Verificación:** sin cursos/sin selección/conversación vacía/loading/error y cambio de modo en Network.
- [ ] **Echo cuando:** los estados son distintos y cambiar tema/modo/panel no crea conversación ni envía una solicitud educativa.

### T67 — Adaptar la lectura del historial
**Requisitos:** RF-4, RF-7, RF-14; RNF-6. **Depende de:** T66, T36.  
**Entregable:** autores/textos/saltos/fuentes reales e indisponibilidad distinguibles, con contención de contenido largo.  
**Verificación:** historial controlado con autores, fuentes/ausencia, fallo/indisponibilidad y selecciones invertidas.
- [ ] **Echo cuando:** autor/estado no dependen del color, no se inventan citas ni se reescribe el historial y mensajes largos no rompen el ancho global.

### T68 — Mantener el contexto de scroll del chat
**Requisitos:** RF-14; RNF-3. **Depende de:** T67.  
**Entregable:** seguimiento del final y acción Ir al último mensaje sin mover al lector que consulta mensajes anteriores.  
**Verificación:** llegada de mensaje estando arriba/al final, acción con teclado y anuncios live.
- [ ] **Echo cuando:** el scroll solo sigue el final cuando corresponde, la acción es accesible y no se anuncia de nuevo todo el historial.

### T69 — Separar composición y prevenir envíos accidentales
**Requisitos:** RF-5, RF-7, RF-15. **Depende de:** T66, T34.  
**Entregable:** ChatComposer controlado con botón Enviar, Enter/Mayús+Enter, IME y bloqueo de envíos incompatibles.  
**Verificación:** vacío según modo, composición IME, Enter repetido, envío pendiente y timeout incierto con historial consultable.
- [ ] **Echo cuando:** IME/Mayús+Enter no envían, solo una intención sale del control y tema/timeout no borran ni reenvían automáticamente el texto de pestaña.

### T70 — Adaptar la imagen adjunta
**Requisitos:** RF-15; RNF-6, RNF-7. **Depende de:** T69.  
**Entregable:** nombre/preview/retirada y ayuda PNG/JPEG/WEBP/GIF, máximo 4 MiB, conservando payload actual.  
**Verificación:** imagen válida/límite/exceso/formato inválido, retirar/reseleccionar y cambio de tema; revocar URL temporal si se utiliza.
- [ ] **Echo cuando:** la selección permanece durante el cambio visual, el error permite corregirla y no se invierte imagen ni se altera contrato/persistencia.

### T71 — Coordinar dictado y fallback de escritura
**Requisitos:** RF-15; RNF-4, RNF-5, RNF-6. **Depende de:** T69, T35.  
**Entregable:** dictado por acción explícita, escucha/stop/revisión y limpieza de callbacks, sin audio backend/autoenvío.  
**Verificación:** soporte/ausencia/denegación, iniciar/parar, tema durante escucha y abandono/logout con reconocimiento controlado o navegador compatible.
- [ ] **Echo cuando:** solo el usuario solicita permiso, puede revisar texto y la escucha termina al salir; la alternativa manual funciona y el caso real se distingue del doble.

### T72 — Proteger el borrador al cambiar de contexto
**Requisitos:** RF-9, RF-15; RNF-6. **Depende de:** T65, T69, T70, T71, T28.  
**Entregable:** permanecer/descartar antes de cambiar conversación/curso/sección con texto o imagen sin enviar.  
**Verificación:** cambio por sidebar/pestaña/ruta, dictado activo, tema y expiración; revisar ausencia de persistencia nueva.
- [ ] **Echo cuando:** permanecer conserva el contexto, descartar no traslada borrador al curso nuevo y la salida por seguridad limpia datos sin quedar bloqueada.

### T73 — Aislar fallos Mermaid y ofrecer fuente segura
**Requisitos:** RF-16; RNF-6. **Depende de:** T67.  
**Entregable:** error local por bloque, carga terminada, texto/fuente disponibles y sanitización conservada.  
**Verificación:** Mermaid válido/inválido y SVG/HTML malicioso controlados dentro de un mensaje con otros bloques.
- [ ] **Echo cuando:** un bloque fallido no rompe historial/texto, no se ejecuta contenido arbitrario ni se muestran excepciones y la fuente se presenta como texto.

### T74 — Adaptar la paleta y secuencia de Mermaid
**Requisitos:** RF-4, RF-16; RNF-2, RNF-4. **Depende de:** T73, T11.  
**Entregable:** render local con tokens y secuencia/serialización necesaria para configuración compartida, preservando importación diferida.  
**Verificación:** cambio rápido de contenido/tema con render demorado y diálogo abierto, observando fuente/Network.
- [ ] **Echo cuando:** preview/ampliación usan el tema vigente, renders obsoletos no reemplazan el actual y no se regenera contenido educativo ni se llama al proveedor.

### T75 — Completar la ampliación accesible de diagramas
**Requisitos:** RF-16, RF-19; RNF-3. **Depende de:** T74, T27.  
**Entregable:** apertura/cierre/zoom/desplazamiento por teclado y foco restaurado; título/descripción asociados cuando llegan.  
**Verificación:** diagrama grande, teclado/lector, cierre y cambio de tema; contenido con/sin descripción alternativa.
- [ ] **Echo cuando:** ampliación no pierde selección/foco ni rompe viewport, y la limitación de fuente sin descripción queda registrada sin inventar una alternativa o llamada IA.

### T76 — Separar el calendario de agenda
**Requisitos:** RF-5, RF-17, RF-18; RNF-7. **Depende de:** T23, T16, T36.  
**Entregable:** AgendaPanel de lectura con periodo/filtro/detalle actuales y estado de consulta, sin reemplazo de biblioteca injustificado.  
**Verificación:** sin eventos, filtros/periodo, evento por teclado/táctil y lectura tardía.
- [ ] **Echo cuando:** periodo/curso son claros, todos los detalles actuales son alcanzables y no se habilita edición ni otro origen de datos.

### T77 — Añadir la lista equivalente de agenda
**Requisitos:** RF-17, RF-19; RNF-3. **Depende de:** T76.  
**Entregable:** lista accesible de todas las actividades recibidas del periodo/filtros activos, con formato español pertinente.  
**Verificación:** comparar IDs/conteo/detalles calendario–lista, incluyendo más de ocho eventos y lector/móvil.
- [ ] **Echo cuando:** la lista no omite actividades recibidas ni cambia periodo/origen, y permite consultar la misma información sin cuadrícula visual.

### T78 — Ejecutar integración del estudiante C4
**Requisitos:** RF-14, RF-15, RF-16, RF-17, RF-20; RNF-6, RNF-7. **Depende de:** T68, T72, T75, T77.  
**Entregable:** resultados UI-07/08 con modos, historial, composición, dictado, diagramas y agenda conectados.  
**Verificación:** estados controlados/errores/selecciones tardías/tema, sin mensajes reales IA, indexación o consumo.
- [ ] **Echo cuando:** los casos C4 se ejecutaron y registraron, su modalidad es explícita y cualquier fallo tiene decisión PUDS.

### T79 — Ejecutar sistema parcial C4
**Requisitos:** RF-14 a RF-17, RF-20; RNF-8. **Depende de:** T78.  
**Entregable:** recorrido integrado estudiante en ambos temas y móvil, incluyendo conversación/agenda/perfil y respuestas controladas identificadas donde corresponda.  
**Verificación:** seleccionar/crear conversación solo con preparación autorizada, navegar y usar composición/recursos sin proveedor real.
- [ ] **Echo cuando:** el recorrido tiene observación y limpieza pertinente, y no se presenta historial/dictado simulado como prueba de persistencia o reconocimiento real.

## C5 — Evaluación integral y cierre

### T80 — Completar el catálogo de componentes y estilos
**Requisitos:** RF-1, RF-5, RF-20; RNF-2. **Depende de:** T64, T79.  
**Entregable:** documento proporcional con paleta formalizada, escala/usos permitidos-prohibidos, mapeo de colores heredados a tokens y componentes reales con contratos/ejemplos/estados/accesibilidad.  
**Verificación:** contrastar valores/usos/excepciones con implementación y consumidores; distinguir marca, roles de tema y colores funcionales secundarios.
- [ ] **Echo cuando:** catálogo y aplicación coinciden en la identidad verde/blanca y códigos/usos, cada patrón tiene contrato/ejemplo real y no se documenta como vigente una paleta o funcionalidad futura.

### T81 — Auditar separación, contratos y duplicación
**Requisitos:** RF-5, RF-20; RNF-1, RNF-2, RNF-6, RNF-7. **Depende de:** T80.  
**Entregable:** revisión de diff/imports/consumidores y persistencia nueva; revisar los seis principios constitucionales.  
**Verificación:** ausencia de reglas/HTTP, ciclos, paletas duplicadas/colores arbitrarios o fondos negros estructurales heredados, dependencias extra y cambios backend/SQL/workflows/enlace Excel; conciliar inventario T02 con excepciones reales.
- [ ] **Echo cuando:** cada entrada del inventario está migrada o justificada sin recuperar fondos negros estructurales, los hallazgos están resueltos/registrados y ninguna desviación silenciosa se aprueba.

### T82 — Ejecutar lint y build finales
**Requisitos:** RF-20; RNF-1, RNF-8. **Depende de:** T64, T79.  
**Entregable:** salida/códigos reales de scripts existentes y comprobación del build servido frente al baseline T05.  
**Verificación:** identificar regresiones de construcción y URLs/orden del arranque de producción.
- [ ] **Echo cuando:** las ejecuciones finales tienen versión/evidencia, los fallos están tratados y no se atribuye aprobación de sistema a un build exitoso.

### T83 — Medir contraste en ambos temas
**Requisitos:** RF-1, RF-4; RNF-3. **Depende de:** T81, T82.  
**Entregable:** medidas por parejas renderizadas de texto normal/grande y controles/foco/estados necesarios, incluyendo overlays y opacidad.  
**Verificación:** ratios reales ≥ 4,5:1 o ≥ 3:1 según criterio/excepción, incluidos verde sobre blanco/menta, blanco sobre verde de acción y texto claro sobre Oscuro suavizado, con fuente/superficie/estado.
- [ ] **Echo cuando:** aclarar la paleta no rebaja los mínimos, cada pareja tiene medida/resultado/excepción y cualquier incumplimiento se registra sin volver al fondo casi negro ni afirmar conformidad global.

### T84 — Ejecutar recorridos solo con teclado
**Requisitos:** RF-6, RF-8, RF-9, RF-15, RF-16, RF-19; RNF-3. **Depende de:** T81, T82.  
**Entregable:** resultados sin ratón para skip link, drawer, tabs, formularios, diálogo, listas, chat, agenda y diagrama.  
**Verificación:** orden/foco visible no oculto, Escape/retorno, acciones sin hover/arrastre y regiones desplazables.
- [ ] **Echo cuando:** cada patrón de la muestra tiene un recorrido ejecutado con foco/acción observado y los fallos o trampas están registrados y tratados.

### T85 — Ejecutar recorridos con lector de pantalla
**Requisitos:** RF-7, RF-8, RF-16, RF-17, RF-19; RNF-3, RNF-8. **Depende de:** T84.  
**Entregable:** resultados de lector/navegador reales y sus versiones para los patrones interactivos de la matriz.  
**Verificación:** nombres/roles/estados, errores asociados, selección/tablas/listas y anuncios sin repetir historial completo.
- [ ] **Echo cuando:** se ejecutó la muestra con lector y se registraron anuncios observados/límites; ausencia de lector deja esta tarea pendiente, no aprobada por inspección estática.

### T86 — Verificar adaptación, zoom y movimiento
**Requisitos:** RF-4, RF-19; RNF-3. **Depende de:** T81, T82.  
**Entregable:** matriz visual 320×568, 390×844, 768×1024, 1440×900, texto 200 %, reflow 400 % a 1280 px y movimiento reducido.  
**Verificación:** todas las superficies/tarea principal, controles alcanzables y overflow solo en regiones justificadas; teclado virtual se completa en móvil real.
- [ ] **Echo cuando:** todas las entradas de la matriz se ejecutaron en ambos temas con observaciones concretas de contenido/foco/acciones y resultados/defectos, no solo capturas.

### T87 — Ejecutar sistema integral en Chrome Windows
**Requisitos:** RF-1, RF-2, RF-4, RF-6, RF-20; RNF-5, RNF-8. **Depende de:** T82, T86.  
**Entregable:** barrido completo en ambas variantes y revisión comparativa de dirección visual login–administración–chat con baseline y decisión del responsable.  
**Verificación:** predominio blanco/menta en Claro, ausencia de grandes fondos negros/carbón en Oscuro, identidad verde/blanca, jerarquía/espacio y tarea principal; modalidades/proveedores no ejercitados señalados.
- [ ] **Echo cuando:** cada superficie tiene resultado de sistema y la muestra visual tiene observaciones/decisión de diseño registradas; «inspiradora» no se presenta como emoción probada ni sustituye contraste/interacción.

### T88 — Ejecutar compatibilidad en Edge Windows
**Requisitos:** RF-2, RF-4, RF-19; RNF-5. **Depende de:** T87.  
**Entregable:** muestra del plan en Edge estable: login/navegación/formulario/diálogo/chat/agenda/diagrama y tema con overlay.  
**Verificación:** ejecutar ambas variantes y registrar versión/diferencias frente a Chrome.
- [ ] **Echo cuando:** todos los recorridos Edge seleccionados se ejecutaron y tienen resultado propio, no deducido de compartir motor con Chrome.

### T89 — Ejecutar compatibilidad en Firefox Windows
**Requisitos:** RF-2, RF-4, RF-19; RNF-5. **Depende de:** T87.  
**Entregable:** muestra del plan en Firefox estable con fallback de dictado cuando corresponda.  
**Verificación:** login/navegación/formulario/diálogo/chat/agenda/diagrama, ambas variantes y overlay abierto.
- [ ] **Echo cuando:** los recorridos Firefox tienen evidencia propia y soporte/fallback observado, sin suponer que el comportamiento de Chromium los acredita.

### T90 — Ejecutar recorridos en Chrome Android
**Requisitos:** RF-6, RF-15, RF-16, RF-17, RF-19; RNF-5. **Depende de:** T87.  
**Entregable:** resultados Android/navegador real o entorno que lo ejecute, versión/dispositivo y vertical/horizontal.  
**Verificación:** login/drawer/tema/formulario con teclado virtual/chat-imagen/agenda-lista/diagrama y dictado o fallback.
- [ ] **Echo cuando:** ambos temas y los recorridos esenciales se ejecutaron con acciones alcanzables al abrir teclado; viewport de Windows no cuenta como esta evidencia.

### T91 — Ejecutar recorridos en Safari iOS
**Requisitos:** RF-6, RF-15, RF-16, RF-17, RF-19; RNF-5. **Depende de:** T87.  
**Entregable:** resultados Safari/iOS real o entorno que lo ejecute, versiones/dispositivo y orientación.  
**Verificación:** mismos recorridos móviles esenciales, permisos/fallback, overlays y teclado virtual en ambos temas.
- [ ] **Echo cuando:** los casos se ejecutaron en Safari iOS identificado; falta de dispositivo/navegador mantiene la tarea pendiente y RNF-5 no ejecutado en esa parte.

### T92 — Medir latencia de interacción local
**Requisitos:** RF-2, RF-19; RNF-4. **Depende de:** T82, T87.  
**Entregable:** 20 medidas por interacción fijada: tema con diálogo, abrir/cerrar drawer, abrir confirmación y pestaña con datos cargados.  
**Verificación:** entorno T03, evento→primer fotograma visible en build servido; al menos 19/20 ≤ 200 ms, sin API/IA en el tiempo medido.
- [ ] **Echo cuando:** se registraron las 20 medidas de cada interacción y su veredicto, Network confirma ausencia de HTTP por tema y no se sustituyen tiempos por percepción subjetiva.

### T93 — Verificar disposición tras veinte ciclos
**Requisitos:** RF-3, RF-15, RF-16; RNF-4, RNF-6. **Depende de:** T82, T79.  
**Entregable:** resultados de 20 entradas/salidas de apariencia/shell/dictado/diagramas y otras funciones con listeners/temporizadores.  
**Verificación:** recuento de callbacks/actividad en DevTools, respuestas tardías y logout; inspeccionar importación Mermaid diferida.
- [ ] **Echo cuando:** se registraron los ciclos y no se oculta duplicación/escucha residual; resultados y fallos de estabilidad tienen evidencia sin telemetría permanente.

### T94 — Ejecutar la regresión aislada pertinente
**Requisitos:** RF-20; RNF-7, RNF-8. **Depende de:** T04, T81.  
**Entregable:** suite aislada completa de 23 casos cuando el impacto justifique reutilizar A-1/A-2/A-3, o exclusión documentada si no se afecta esa lógica.  
**Verificación:** IDs/salida/código/versión; no introducir filtro inexistente ni modificar algoritmos para obtener un resultado.
- [ ] **Echo cuando:** la ejecución real está registrada con fallos tratados, o la no aplicabilidad está justificada por diff/impacto; no se convierte una exclusión en evidencia de ejecución.

### T95 — Ejecutar integración backend/SQL seleccionada
**Requisitos:** RF-20; RNF-6, RNF-7, RNF-8. **Depende de:** T04, T81.  
**Entregable:** resultados I-1 a I-4 seleccionados por impacto y justificación de omisiones, con nueva autorización por operación y recursos propios.  
**Verificación:** interfaces reales y resultados persistidos, journal/identidad/cleanup; no ampliar a mensajes/consumo/RAG sin diseño aprobado.
- [ ] **Echo cuando:** los casos aplicables se ejecutaron realmente con autorización y recuperación documentadas, o se justificó no aplicabilidad; un recurso ausente deja ejecución pendiente.

### T96 — Ejecutar regresión de sistema seleccionada
**Requisitos:** RF-10, RF-12, RF-14, RF-20; RNF-7, RNF-8. **Depende de:** T04, T87.  
**Entregable:** nuevas ejecuciones pertinentes S-1/S-2/S-3/S-3b con IDs preservados y versión actual, sin sobrescribir historia.  
**Verificación:** sistema real/HTTP/SQL según caso autorizado; separar fallo previo de Excel de regresión visual y no sustituirlo por mock.
- [ ] **Echo cuando:** los casos seleccionados fueron ejecutados y registrados con esperado/obtenido y decisión ante fallos, o exclusión justificada por impacto; no se exige reparar el importador.

### T97 — Comprobar limpieza y recuperación de datos propios
**Requisitos:** RF-20; RNF-6, RNF-8. **Depende de:** T64, T79, T95, T96.  
**Entregable:** comprobación final de journals/residuos de todas las ejecuciones reales y retirada de archivos ficticios temporales.  
**Verificación:** verificar propiedad/destino antes de limpiar, seguir orden permitido y confirmar ausencia postcleanup; no borrar recursos ajenos por patrón.
- [ ] **Echo cuando:** cada ejecución tiene limpieza demostrada o residuos/decisión explícitos, y una verificación independiente confirma el resultado donde corresponde; sin escrituras, no aplicabilidad justificada.

### T98 — Evaluar requisitos y emitir el veredicto final
**Requisitos:** RF-20; RNF-1 a RNF-8. **Depende de:** T80 a T97, o decisiones explícitas de diferimiento de tareas bloqueadas.  
**Entregable:** checklist individual de 20 RF/8 RNF, evidencia/casos/defectos, cumplimiento constitucional y decisión del responsable.  
**Verificación:** revisar cobertura completa, recursos no disponibles, tarea versus requisito, bloqueos previos y nuevos, sin cerrar checkboxes pendientes por conveniencia.
- [ ] **Echo cuando:** cada requisito tiene veredicto sustentado y el responsable registra decisiones; se distinguen entregables terminados, fallos y no ejecutados y solo se declara cumplimiento íntegro si toda la evidencia requerida lo permite.

## Matriz de cobertura de tareas

Esta matriz enlaza implementación y evaluación; no supone que ejecutar una tarea aislada apruebe por completo su requisito. Los rangos representan todas las tareas comprendidas.

| Requisito | Tareas principales | Comprobación integral |
|---|---|---|
| RF-1 | T02, T06, T11, T12, T24 | T17, T80, T81, T83, T87 |
| RF-2 | T07, T09, T13, T14, T21–T23 | T17, T18, T87–T92 |
| RF-3 | T07–T10, T35 | T17, T18, T93 |
| RF-4 | T06, T11, T12, T14, T40–T77 según superficie | T17, T63, T78, T83, T86–T91 |
| RF-5 | T19–T30, T59–T61, T65, T69, T76 | T38, T80, T81 |
| RF-6 | T19–T23, T32, T48, T50 | T38, T39, T84, T87–T91 |
| RF-7 | T25, T26, T34, T36, T37, T40–T78 según operación | T38, T63, T78, T85 |
| RF-8 | T14, T28–T30, T37, T41–T59 según formulario | T38, T63, T84, T85 |
| RF-9 | T27–T30, T37, T41–T62 según acción, T72 | T38, T63, T78, T84 |
| RF-10 | T14, T33–T35, T37, T41–T54 según operación | T38, T39, T87, T96 |
| RF-11 | T31, T40, T42, T44, T46, T48, T51, T53 | T38, T63, T84, T86 |
| RF-12 | T55, T56 | T63, T64, T96 |
| RF-13 | T59–T62 | T63, T64 |
| RF-14 | T65–T68 | T78, T79, T87, T96 |
| RF-15 | T35, T69–T72 | T78, T79, T84, T90–T93 |
| RF-16 | T73–T75 | T78, T79, T84, T85, T90, T91, T93 |
| RF-17 | T16, T44, T57, T58, T76, T77 | T63, T78, T85, T90, T91 |
| RF-18 | T14, T16, T26, T42, T55, T56, T58, T61, T66, T76 | T63, T78, T80, T87–T91 |
| RF-19 | T15, T19, T20, T32, T75, T77 | T84–T92 |
| RF-20 | T01–T05, T80 | T17, T18, T38, T39, T63, T64, T78, T79, T94–T98 |
| RNF-1 | T01, T05 | T81, T82, T98 |
| RNF-2 | T02, T06, T11, T12, T16, T19, T24, T29, T31, T74 | T17, T38, T80, T81, T98 |
| RNF-3 | T13–T15, T19, T20, T25–T27, T32, T37, T68, T75, T77 | T38, T83–T86, T98 |
| RNF-4 | T03, T09, T10, T71, T74 | T17, T92, T93, T98 |
| RNF-5 | T03, T15, T71 | T88–T91, T98 |
| RNF-6 | T04, T08, T14, T26, T28, T29, T34, T35, T47, T54, T61, T67, T70–T72, T73 | T81, T93, T95, T97, T98 |
| RNF-7 | T01, T02, T21–T23, T31, T33, T34, T36, T55, T56, T60, T62, T70, T76 | T81, T94–T96, T98 |
| RNF-8 | T03–T05 | T18, T39, T63, T64, T79, T82, T85, T87, T94–T98 |

**Cierre:** ningún checkbox se marca por redactar estas tareas. Las tareas bloqueadas conservan su estado y el registro final debe mostrar su impacto en los RF/RNF; diferirlas no equivale a aprobar SPEC-002.
