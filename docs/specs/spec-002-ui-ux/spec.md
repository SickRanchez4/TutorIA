# SPEC-002 — Interfaz, experiencia de usuario y sistema visual de TutorIA

## 1. Contexto y objetivo

**Estado:** aprobado.  
**Fecha:** 2026-09-30.  
**Baseline:** [Spec-000 — MVP](../spec-000-mvp/Spec-000-mvp.md).  
**Gobernanza:** [Constitución](../constitution.md).  
**Antecedentes de verificación:** [registro de SPEC-001](../spec-001-tests/test.md) y [regresión proporcional](../../../testing/REGRESSION.md).

TutorIA necesita una experiencia coherente en toda su interfaz: no solo cambiar colores, sino unificar navegación, jerarquía, formularios, estados, accesibilidad y comportamiento en diferentes dispositivos. La aplicación debe permitir elegir un tema claro u oscuro y sus componentes visuales deben tener responsabilidades delimitadas, contratos explícitos y reutilización real, sin construir un framework propio.

**Dirección visual solicitada:** formalizar y estandarizar la paleta actual para una experiencia más luminosa, amable e inspiradora, con **verde y blanco como colores principales**. El verde no quedará reducido a un acento aislado: organizará identidad, acciones y selección; blanco, verdes suaves y neutros claros aportarán amplitud. El tema oscuro seguirá disponible, pero será una variante verde suave, más clara que la interfaz casi negra actual, no una conservación de sus fondos negros/gris carbón. Esta actualización de dirección visual fue solicitada por el responsable; no acredita aprobación de códigos concretos del plan ni implementación.

Esta spec define **el comportamiento objetivo del incremento UI/UX**, no una descripción retrospectiva ni una declaración de trabajo implementado. Abarca la presentación e interacción de las funcionalidades existentes. No redefine sus reglas de negocio, permisos, contratos externos ni persistencia transaccional.

### 1.1 Punto de partida comprobado por lectura

- Existe un tema oscuro en [frontend/src/plugins/vuetify.js](../../../frontend/src/plugins/vuetify.js), acompañado de colores oscuros fijos en [frontend/src/style.css](../../../frontend/src/style.css) y [frontend/tailwind.config.js](../../../frontend/tailwind.config.js). Añadir un selector no bastará para cubrir toda la interfaz.
- Se reutilizan [frontend/src/components/RoleSidebar.vue](../../../frontend/src/components/RoleSidebar.vue), [frontend/src/components/PanelTitle.vue](../../../frontend/src/components/PanelTitle.vue), [frontend/src/components/ProfileSection.vue](../../../frontend/src/components/ProfileSection.vue) y [frontend/src/components/MermaidMessage.vue](../../../frontend/src/components/MermaidMessage.vue). El incremento deberá aprovecharlos o reorganizarlos justificadamente, no mantener una segunda implementación equivalente.
- [frontend/src/router/index.js](../../../frontend/src/router/index.js) contiene login, paneles por rol y subrutas del coordinador. Los paneles de estudiante y superadministrador también contienen secciones internas; el inventario UI no se limita al número de rutas.
- Mermaid utiliza actualmente una superficie clara propia. Su adaptación deberá ser explícita, sin invertir imágenes ni alterar el contenido educativo.

Esta revisión de fuente no acredita contraste, usabilidad, accesibilidad ni comportamiento visual en ejecución. Las evidencias anteriores conservan su alcance y no aprueban SPEC-002.

### 1.2 Resultados esperados

1. Permitir completar las tareas actuales en claro y oscuro, sin pérdida de información o funcionalidad.
2. Hacer reconocibles la ubicación, acción principal, estado de la operación y forma de recuperarse de un error.
3. Permitir navegación con teclado, tecnologías de asistencia y pantallas pequeñas.
4. Disponer de patrones visuales compartidos, documentados y fáciles de mantener, sin duplicación por tema o rol.
5. Verificar el incremento conforme a PUDS, con trazabilidad y defectos visibles.

## 2. Usuarios y alcance de pantallas

| Actor | Superficie incluida | Tareas que deben conservarse |
|---|---|---|
| Visitante | Inicio de sesión y estados públicos | Introducir credenciales, mostrar/ocultar contraseña, recibir errores comprensibles y elegir apariencia |
| Superadministrador | Instituciones, planes, suscripciones, coordinadores y perfil | Consultar y gestionar entidades mediante las operaciones ya disponibles; identificar institución y alcance de cada acción |
| Coordinador | Cursos y detalle de curso | Crear, editar, activar/desactivar, eliminar e importar cursos; gestionar estudiantes y matrículas; configurar tutor y conocimiento |
| Coordinador | Cuentas e institución | Buscar y gestionar estudiantes con acciones existentes; consultar/editar institución y consultar suscripción, capacidad y consumo disponibles |
| Coordinador | Analíticas y perfil | Filtrar periodos/tipos existentes, consultar indicadores y desgloses; editar datos propios y contraseña |
| Estudiante | Asistente y conversaciones | Elegir curso, crear, abrir, renombrar y archivar conversaciones; consultar historial; utilizar consulta, práctica y recursos según permisos |
| Estudiante | Composición y recursos | Escribir, adjuntar imágenes, dictar cuando exista soporte y ampliar diagramas |
| Estudiante | Agenda y perfil | Consultar actividades con filtros existentes y editar datos propios; agenda de solo lectura |
| Todos los actores | Elementos transversales | Navegación, encabezados, formularios, tablas, listas, tarjetas, pestañas, menús, diálogos, avisos, tooltips, estados y errores |

También se incluyen rutas inexistentes, recursos no disponibles, sesión expirada, respuestas tardías y superposiciones abiertas. No se incorporan pantallas de registro público, recuperación por correo, nuevos roles ni funciones de administración ausentes del baseline.

## 3. Principios de experiencia y límites del cambio

- **Identidad luminosa e inspiradora:** verde y blanco serán los colores principales de TutorIA, con superficies blancas/blanco roto y verdes suaves en Claro, y verdes desaturados de luminosidad moderada con texto blanco/blanco roto en Oscuro. Evitar grandes superficies negras o casi negras en estructura, navegación y tarjetas. La sensación buscada es apertura, calma y acompañamiento al aprendizaje, no una interfaz pesada o dramática.
- **Claridad antes que decoración:** la identidad verde/blanca se expresa mediante jerarquía, espacio y contraste, sin llenar todo de verde saturado. Efectos, sombras y transparencias no deben competir con contenido, foco o estado; no se sacrifica legibilidad para usar tonos más claros.
- **Consistencia sin uniformidad forzada:** los patrones compartidos mantienen significado, pero una conversación, una tabla administrativa y un calendario conservan composiciones adecuadas a su tarea.
- **Divulgación progresiva:** las acciones frecuentes quedan visibles; detalles secundarios pueden desplegarse sin ocultar información necesaria para decidir.
- **Backend como autoridad:** ocultar o deshabilitar controles es ayuda de interacción, no autorización. No se recrean reglas de cuotas, matrícula, vigencia ni validadores de negocio.
- **Cambio proporcional:** la extracción de componentes y ajustes de interacción quedan vinculados a requisitos de esta spec. No se impone un tamaño máximo arbitrario de archivo ni una abstracción por cada etiqueta.
- **Sin promesas falsas:** no mostrar operaciones exitosas, porcentajes, disponibilidad, citas o datos que el contrato real no confirme.

## 4. Requisitos funcionales

Los criterios utilizan condición o evento y respuesta verificable. Los identificadores completos se citarán como **SPEC-002/RF-n** y **SPEC-002/RNF-n** para no confundirlos con SPEC-001. Todos los requisitos son obligatorios para declarar cumplimiento íntegro tras la aprobación; dividir su ejecución en construcciones no los vuelve opcionales.

### RF-1. Sistema visual coherente

**Requisito:** aplicar un lenguaje visual común a todas las superficies incluidas.

- **Siempre**, la interfaz deberá emplear un catálogo común de roles visuales: fondo, superficies, texto principal/secundario, bordes, foco, acción primaria/secundaria, éxito, información, advertencia y error, con variantes para ambos temas.
- **Antes de** migrar colores, deberá formalizarse una paleta de marca verde/blanca con escala de verdes claros, medios y oscuros, blancos/neutros compatibles, códigos identificables y usos permitidos/prohibidos. Los colores actuales se inventariarán y mapearán a roles de esa paleta; no bastará añadir colores nuevos manteniendo variantes arbitrarias por pantalla.
- **Siempre**, verde y blanco deberán definir la identidad en login, encabezados, navegación, tarjetas y acciones. En Claro predominarán superficies blancas/blanco roto y verdes suaves; en Oscuro se usarán fondos verdes desaturados más luminosos que los fondos casi negros actuales, manteniendo una diferencia útil entre ambos temas y texto claro legible. Negro/gris carbón no serán el fondo principal de la aplicación ni de sus regiones estructurales.
- **Cuando** se migre una pantalla, sus colores propios de producto deberán usar tokens aprobados de fondo, texto, acciones y estados, incluidos hover, selección, disabled, bordes y overlays. Fotografías, documentos y contenido externo conservan su color; error/advertencia/información mantienen colores funcionales distinguibles sin desplazar la identidad verde/blanca.
- **Cuando** se evalúe la dirección inspiradora, deberá compararse una muestra de login, administración y chat con el baseline, registrando predominio de superficies luminosas en Claro, ausencia de grandes fondos negros en Oscuro, jerarquía/espacio y consistencia de la familia verde. La valoración del responsable se registrará como revisión de diseño, no como prueba de una emoción del usuario ni sustituto de accesibilidad.
- **Cuando** se represente el mismo tipo de acción o estado en distintas pantallas, deberá conservar su significado, jerarquía, iconografía y tratamiento visual. Un estado no dependerá exclusivamente del color.
- **Siempre**, tipografía, escala de espaciado, tamaños de controles, radios, elevaciones y capas de superposición deberán seguir criterios compartidos, en lugar de valores repetidos por vista.
- **Cuando** se diseñen encabezados y secciones, deberá identificarse un título principal de pantalla y una acción primaria por bloque de tarea cuando corresponda; no se usarán tamaños de título para suplir una estructura semántica incorrecta.

### RF-2. Selección de tema claro, oscuro y del sistema

**Requisito:** ofrecer dos temas completos y una selección automática opcional.

- **Cuando** el usuario abra login o cualquier panel, deberá poder acceder desde el encabezado a un control de apariencia, también en móvil, con las opciones **Claro**, **Oscuro** y **Sistema** y la opción seleccionada identificable.
- **Cuando** no exista una preferencia válida guardada, deberá seleccionarse Sistema; si el navegador no informa preferencia, se resolverá a Claro.
- **Cuando** se seleccione Claro u Oscuro, deberá aplicarse inmediatamente sin recargar, navegar, cerrar diálogos, reiniciar formularios, perder foco o alterar una operación en curso.
- **Mientras** esté seleccionada la opción Sistema, los cambios de preferencia del sistema operativo deberán reflejarse en la interfaz abierta. Una selección explícita de Claro u Oscuro tendrá prioridad sobre esos cambios.
- **Cuando** se use teclado o lector de pantalla, el control deberá comunicar su propósito, opciones y selección sin depender de un icono de sol o luna.

### RF-3. Persistencia e inicialización de apariencia

**Requisito:** recordar la apariencia de manera sencilla, segura y determinista.

- **Cuando** cambie la selección, deberá guardarse únicamente la preferencia de apariencia en el navegador para el mismo origen y perfil, sin identificadores personales, credenciales ni una nueva llamada al backend.
- **Cuando** se recargue, cierre sesión o inicie sesión otra cuenta en ese mismo navegador, deberá conservarse esa preferencia local. No se promete sincronización por usuario ni entre dispositivos; en un navegador compartido la preferencia también es compartida.
- **Cuando** inicie la aplicación, deberá resolver y aplicar el tema antes de mostrar el contenido principal para evitar un primer fotograma del tema contrario, incluidos el fondo de la página y los controles nativos compatibles.
- **Si** el almacenamiento está bloqueado o falla, deberá mantenerse la selección durante la pestaña actual sin bloquear el uso de la aplicación; al recargar se resolverá Sistema si no puede leerse una preferencia válida.
- **Si** existe un valor guardado desconocido o corrupto, deberá ignorarse sin provocar error de arranque. Si otra pestaña cambia la preferencia y el navegador notifica el cambio, las pestañas abiertas deberán actualizarla.

### RF-4. Cobertura integral de los temas

**Requisito:** evitar una mezcla accidental de temas o variantes incompletas.

- **Siempre**, claro y oscuro deberán cubrir login, paneles, navegación, formularios y sus estados, tablas, tarjetas, calendario, chat, avisos, menús, tooltips y diálogos, incluidos los renderizados fuera del contenedor de la vista.
- **Cuando** cambie el tema con un menú o diálogo abierto, deberá actualizarse también esa superficie, su fondo superpuesto y sus controles.
- **Cuando** se muestren diagramas generados, texto, conectores y superficie deberán ser legibles y usar la variante correspondiente del sistema visual, tanto en vista previa como ampliada; el cambio no modificará su fuente ni solicitará generación al proveedor.
- **Cuando** se muestren fotografías, imágenes adjuntas o documentos, deberán conservar sus colores originales; no se aplicarán filtros globales de inversión. Los logotipos podrán tener variantes de contraste sin alterar su identidad.
- **Siempre**, ambas variantes deberán ofrecer las mismas acciones, datos y criterios de accesibilidad. No se mantendrán copias separadas de una pantalla para cada tema.

### RF-5. Componentes limpios y reutilizables

**Requisito:** organizar los elementos visuales por responsabilidad y reutilizar patrones reales.

- **Cuando** dos o más superficies necesiten el mismo patrón de presentación e interacción, deberá existir una implementación compartida o una composición de los componentes existentes, con variantes explícitas y sin copias divergentes.
- **Siempre**, deberán distinguirse responsabilidades de estructura de página, patrones visuales comunes, componentes específicos de funcionalidad y coordinación de datos de la vista. Un componente específico puede usarse una sola vez si delimita una responsabilidad real.
- **Cuando** un componente visual reutilizable reciba datos o comunique acciones, deberá hacerlo mediante entradas, eventos y espacios de composición documentados; no dependerá ocultamente de una ruta, rol, institución, proveedor o solicitud HTTP concreta.
- **Cuando** un contenedor necesite cargar o guardar datos, deberá utilizar la capa de servicios existente. Los componentes de presentación no contendrán reglas de negocio ni acceso directo a integraciones externas.
- **Cuando** se necesiten diferencias entre roles, se expresarán mediante composición o configuración de las opciones permitidas, no mediante un componente universal con ramas de negocio para toda la aplicación.
- **Cuando** se extraiga un patrón, deberán migrarse sus consumidores incluidos en el alcance y retirarse la duplicación y estilos obsoletos sustituidos. No se envolverá un componente de la biblioteca si la envoltura no aporta comportamiento o consistencia necesarios.

Patrones mínimos a evaluar y unificar donde ya se repiten: estructura de panel y encabezado, navegación, título/acciones de página, estados de carga/vacío/error, notificaciones, confirmaciones, formularios de perfil, selección de archivos y presentación de listas/tablas. Esta lista define responsabilidades, no obliga a crear un archivo o componente nuevo por elemento; el plan justificará qué se reutiliza, extrae o mantiene específico.

### RF-6. Navegación, contexto y orientación

**Requisito:** permitir saber dónde se está y cómo completar o abandonar una tarea.

- **Cuando** se acceda a un panel, deberá identificarse el rol, la sección activa y la institución o curso cuando sean necesarios para interpretar la acción, sin ofrecer funciones de otro rol.
- **Cuando** haya espacio de escritorio, la navegación deberá poder permanecer visible y contraerse sin perder nombres accesibles; en pantallas pequeñas deberá abrirse y cerrarse sin tapar permanentemente la tarea.
- **Cuando** se abra navegación temporal, deberá gestionarse el foco, impedir interacción con el fondo y permitir cierre mediante control visible y Escape. Tras seleccionar destino se cerrará; al cancelarla se devolverá el foco al disparador.
- **Cuando** se abra el detalle de un curso, deberá existir un retorno explícito al listado; al volver durante la misma sesión de navegación se conservarán búsqueda, filtros y página previamente seleccionados cuando sigan siendo válidos.
- **Siempre**, se conservarán las rutas válidas existentes y su protección. Los cambios de ruta deberán actualizar el título del documento y situar el foco en el contenido principal; las pestañas internas mantendrán el comportamiento de foco propio de pestañas y comunicarán la sección activa.

### RF-7. Estados de carga, vacío y resultado

**Requisito:** expresar el estado real de cada región sin bloquear innecesariamente el resto.

- **Cuando** una región espere datos, deberá mostrar carga identificable y no presentar todavía «sin registros» ni valores cero como si fueran resultados confirmados.
- **Cuando** una consulta termine sin datos, deberá distinguirse entre ausencia inicial, ausencia de coincidencias de filtros e indisponibilidad; se ofrecerá una acción pertinente, como limpiar filtros, solo si está disponible para ese actor.
- **Cuando** se envíe una operación, deberá indicarse su progreso y bloquear envíos repetidos del mismo control hasta recibir resultado, sin afirmar garantías de idempotencia del servidor.
- **Cuando** una operación termine, se comunicará éxito, resultado parcial o fallo según la respuesta. Los avisos breves no robarán foco; un error que requiera corrección o decisión permanecerá localizable hasta resolverlo o descartarlo explícitamente.
- **Si** falla una lectura recuperable, deberá ofrecerse un reintento manual; no se repetirán automáticamente mutaciones, importaciones ni solicitudes del tutor.
- **Cuando** una respuesta de una selección anterior llegue después de cambiar de curso, institución, periodo o conversación, no deberá reemplazar los datos ni el estado de la selección actual.

### RF-8. Formularios y validación comprensibles

**Requisito:** facilitar la entrada y corrección de datos sin duplicar la autoridad del backend.

- **Siempre**, los campos deberán tener etiquetas persistentes, obligatoriedad identificable y ayudas necesarias antes del envío; un placeholder no sustituirá la etiqueta.
- **Cuando** se detecte un error de entrada o el servidor rechace el formulario, deberá explicarse en español qué corregir, asociado al campo cuando el contrato permita identificarlo; al enviar se dirigirá el foco al primer error o resumen pertinente.
- **Cuando** falle el guardado, deberán conservarse los valores editados en la vista activa salvo credenciales que deban limpiarse por seguridad; no se cerrará el formulario ni se mostrará éxito falso.
- **Cuando** un control esté deshabilitado por falta de contexto o indisponibilidad conocida, el motivo deberá ser accesible sin depender de un tooltip sobre un elemento deshabilitado.
- **Siempre**, mostrar/ocultar contraseña, autocompletado apropiado, pegar texto y gestores de contraseñas deberán funcionar; no se añadirán restricciones de autenticación ni requisitos de memoria ajenos al baseline.

### RF-9. Diálogos, confirmaciones y salida con cambios

**Requisito:** prevenir pérdidas accidentales y distinguir acciones reversibles de destructivas.

- **Antes de** eliminar permanentemente cursos, instituciones, cuentas o conocimiento, deberá mostrarse una confirmación con entidad identificable, alcance conocido, consecuencia y botones inequívocos; el foco inicial no recaerá en la acción destructiva.
- **Cuando** la operación sea archivar una conversación, deberá denominarse «Archivar» y no prometer eliminación física ni recuperación si no hay una acción disponible para ello.
- **Cuando** se abra un diálogo, deberá tener título accesible, orden de foco lógico y foco contenido; al cerrarlo se devolverá al origen o a un destino válido si el origen desapareció.
- **Cuando** el usuario intente cerrar o abandonar dentro de la SPA un formulario editado sin guardar, deberá poder **seguir editando** o **descartar**. Cambiar el tema no disparará ese aviso ni descartará datos. La salida del navegador podrá usar su confirmación nativa cuando sea compatible.
- **Mientras** se procesa una mutación que no admite cancelación real, no deberá ofrecerse «Cancelar operación». Se indicará el estado; si se impide cerrar temporalmente, el cierre volverá a estar disponible tras respuesta o timeout, con tratamiento de resultado incierto conforme a RF-10.

### RF-10. Autenticación, errores y recuperación segura

**Requisito:** mantener una salida comprensible ante problemas de acceso, red o recursos.

- **Cuando** fallen las credenciales, deberá comunicarse un error comprensible sin revelar si existe una cuenta ni mostrar datos de otros usuarios.
- **Cuando** la sesión expire o el servidor rechace la autenticación, deberán retirarse los datos privados de las vistas activas y volver a login con una explicación; ningún borrador privado se persistirá para atravesar el cierre de sesión.
- **Cuando** el servidor deniegue una acción autorizada solo aparentemente por el cliente, deberá respetarse el rechazo y mostrar el motivo público seguro, sin ofrecer evasión del control.
- **Cuando** se acceda a una ruta inexistente o falte un recurso solicitado, deberá mostrarse un estado «Página no encontrada» o «Recurso no disponible» sin pantalla vacía ni bucles, con retorno a login o al panel permitido. No se revelará la existencia de recursos ajenos.
- **Si** falla la red, se alcanza un timeout o llega un error interno, deberá mostrarse un mensaje seguro y una salida útil. Si el servidor pudo haber confirmado una mutación, se indicará que no se pudo confirmar el resultado y se ofrecerá actualizar/consultar antes de repetir; no se afirmará que nada se guardó.
- **Siempre**, los mensajes públicos excluirán excepciones internas, respuestas crudas de proveedores, credenciales y detalles privados. Los códigos HTTP y contratos existentes no se cambiarán para conseguir un mensaje visual distinto.

### RF-11. Listas, tablas y gestión administrativa

**Requisito:** presentar datos administrativos con densidad y acciones consistentes.

- **Cuando** se muestren instituciones, planes, suscripciones, coordinadores, cursos, cuentas o matrículas, deberán identificarse sus estados, datos principales y acciones disponibles sin depender de iconos sin nombre.
- **Cuando** existan búsqueda, orden o filtros en el flujo actual, deberán conservarse y mostrar su alcance, valor activo y forma de limpiarlos; no se prometerá búsqueda global cuando solo se filtra el conjunto cargado.
- **Cuando** un listado supere el tamaño de página definido en el catálogo visual, deberá permitir recorrer todos los registros recibidos con navegación accesible y conteo claro. La paginación local no supondrá un nuevo contrato ni búsqueda del lado del servidor.
- **Cuando** una mutación confirme cambios, deberá actualizarse el registro/listado correspondiente conservando contexto; si se elimina el último elemento de una página, se pasará a una página válida.
- **Cuando** no quepa una tabla en móvil, se deberá adaptar la presentación o confinar su desplazamiento horizontal a una región identificada y operable, manteniendo acceso a todas las acciones y datos necesarios.

### RF-12. Selección de archivos e importaciones Excel

**Requisito:** hacer utilizable y consistente la selección y el resultado de las importaciones existentes.

- **Cuando** se seleccione un archivo, deberá mostrarse su nombre, permitir retirarlo o sustituirlo y distinguir selección simple de múltiple según la operación.
- **Cuando** se presente una importación Excel de cursos o estudiantes, deberán explicarse formato y columnas requeridas según su contrato actual, sin inventar un límite ni un esquema alternativo de importación.
- **Cuando** termine una importación, deberán mostrarse los contadores y omisiones que devuelva el backend; un resultado parcial no se comunicará como éxito completo. Se conservará un resumen consultable hasta descartarlo o iniciar otra importación.
- **Si** no se seleccionó archivo o la operación devuelve error, deberá mantenerse el contexto y permitir corregir la selección sin repetir automáticamente el envío.

Este requisito comprende presentación e interacción de las importaciones existentes, no la reparación de defectos funcionales previos ni cambios en el enlace de importación, interpretación de filas o reglas del importador.

### RF-13. Configuración del tutor y gestión del conocimiento

**Requisito:** separar configuración, carga y estado de procesamiento sin exponer detalles de infraestructura.

- **Cuando** un coordinador configure el tutor, deberán agruparse de manera clara prompt, temperatura, modos y opciones existentes, distinguiendo valores guardados de edición pendiente y aplicando RF-8/RF-9.
- **Cuando** cargue materiales, deberá identificarse el curso y explicarse el límite vigente del baseline: hasta 10 PDF por carga y 20 MiB por archivo. La comprobación cliente será orientativa; el servidor mantiene validación y autoridad.
- **Cuando** se muestre un trabajo, deberá traducirse su estado a una etiqueta comprensible, incluidos `queued`, `processing`, `completed`, `failed` y `unknown`. No se inventarán porcentajes cuando el contrato solo informe estado.
- **Cuando** haya errores o archivos temporales no disponibles, deberán mostrarse las acciones realmente soportadas y el resultado de intentar reanudar. No se prometerá un reintento exitoso ni cancelación de procesamiento que el backend no implemente.
- **Antes de** eliminar un documento o limpiar el conocimiento del curso, deberá diferenciarse el alcance y solicitar confirmación. Los detalles públicos del trabajo no expondrán logs crudos, rutas privadas ni credenciales.

### RF-14. Conversaciones y modos de aprendizaje

**Requisito:** priorizar la lectura y el contexto académico en el espacio del estudiante.

- **Cuando** el estudiante entre al asistente, deberá distinguir los estados sin cursos, sin conversación seleccionada, conversación vacía, carga de historial y error; no se creará una conversación solo por cambiar el tema o abrir un panel.
- **Cuando** seleccione una conversación, deberán identificarse su curso, título y modo aplicable; crear, renombrar y archivar conservarán las operaciones actuales y la identidad de la conversación.
- **Cuando** se ofrezcan Consulta, Práctica y Recursos, deberá explicarse brevemente su propósito y señalarse la selección y la indisponibilidad según la información del backend. Cambiar un modo no enviará una solicitud por sí solo.
- **Cuando** se muestren mensajes, deberán distinguirse autor y contenido sin depender del color o alineación; textos largos, saltos de línea y fuentes recibidas deberán poder consultarse sin romper el ancho de la página ni inventar citas.
- **Cuando** llegue una respuesta y el usuario esté al final, podrá mantenerse visible el último mensaje; si está leyendo mensajes anteriores, no se desplazará forzosamente y se ofrecerá volver al último mensaje.
- **Cuando** el contrato indique indisponibilidad del servicio, se distinguirá de una respuesta educativa normal; no se ocultará ni se sobrescribirá el historial persistido.

### RF-15. Composición, imágenes y dictado

**Requisito:** evitar envíos accidentales y conservar una alternativa de entrada disponible.

- **Cuando** se escriba un mensaje, deberá existir un botón Enviar accesible, impedir contenido vacío conforme al modo actual y mostrar el estado de envío. Enter enviará y Mayús+Enter insertará salto de línea, con ayuda visible o accesible; no se enviará durante composición de texto mediante IME.
- **Mientras** haya envío o dictado activo, deberán bloquearse envíos incompatibles. Cambiar de tema conservará texto, selección de imagen, conversación y estado de dictado sin reiniciarlos.
- **Cuando** se adjunte una imagen, deberán mostrarse vista previa, nombre y acción de retirada; se explicarán PNG, JPEG, WEBP o GIF y el límite de 4 MiB, sin eludir la validación backend.
- **Cuando** se active el dictado, se solicitará permiso solo por acción del usuario, se indicará que está escuchando y se permitirá detenerlo y revisar/editar el texto antes de enviarlo. No se enviará automáticamente ni se añadirá un contrato de audio al backend.
- **Si** el navegador no soporta dictado o deniega el permiso, la escritura seguirá disponible con explicación. Al salir de la función de dictado o cerrar sesión deberá detenerse la escucha.
- **Cuando** se cambie de conversación o se abandone el asistente con contenido sin enviar, deberá poder conservarse permaneciendo en la conversación o descartarse explícitamente; nunca se trasladará silenciosamente al curso nuevo.
- **Si** no puede confirmarse un envío, deberá conservarse el texto para revisión en la pestaña activa y consultar el historial antes de repetir. No se garantiza recuperar borradores o archivos tras recargar ni se guardarán en almacenamiento persistente nuevo.

### RF-16. Recursos y diagramas accesibles

**Requisito:** aislar fallos de representación y ofrecer una lectura alternativa.

- **Cuando** un recurso incluya Mermaid, deberá poder ampliarse y cerrarse mediante teclado, conservando foco y contexto del mensaje, con desplazamiento contenido si el diagrama es grande.
- **Si** la representación falla, deberá terminar la indicación de carga, mostrar un error local y conservar el resto del mensaje; un recurso inválido no bloqueará el historial ni mostrará excepciones internas.
- **Siempre**, se conservará la sanitización de contenido renderizado y se ofrecerá acceso al texto disponible y al código fuente del diagrama como texto, sin ejecutar HTML arbitrario.
- **Cuando** el recurso contenga título o descripción textual, deberán asociarse al diagrama. La fuente técnica por sí sola no se considerará una descripción accesible equivalente; la evaluación registrará esa limitación cuando el contenido recibido carezca de alternativa, sin inventar una explicación ni exigir nuevas llamadas IA.

### RF-17. Agenda e indicadores

**Requisito:** hacer comprensibles calendarios y datos sin ampliar su funcionalidad de negocio.

- **Cuando** el estudiante consulte agenda, deberá identificar periodo, curso y filtros disponibles, distinguir eventos y acceder a los detalles actuales mediante teclado y táctil. La vista seguirá siendo de solo lectura.
- **Cuando** el calendario resulte inadecuado para pantalla pequeña o lector de pantalla, deberá existir una lista accesible equivalente de las actividades recibidas para el periodo y filtros activos, sin crear otro origen de datos.
- **Cuando** se muestren analíticas, sus filtros activos, periodo, unidades y significado deberán ser claros; los gráficos tendrán valores o resumen/tablas textuales equivalentes y no dependerán solo de color, hover o animación.
- **Cuando** una métrica esté ausente, sea cero o represente capacidad ilimitada, deberá distinguirse cada caso. No se dividirá por cero ni se mostrarán valores inválidos o porcentajes ficticios.
- **Siempre**, los costos se etiquetarán como estimados en USD, no como facturas; las fechas y números usarán formato español consistente, indicando la zona horaria cuando afecte a la interpretación. No se modificarán periodos UTC ni cálculos de negocio del backend.

### RF-18. Ayuda contextual e idioma

**Requisito:** utilizar textos breves, coherentes y orientados a la tarea.

- **Siempre**, los textos propios, validaciones, navegación, calendarios y controles de la biblioteca deberán mostrarse en español. Se usará «curso» para la entidad académica y «estudiante» de forma consistente, sin renombrar campos o contratos existentes.
- **Cuando** una acción sea ambigua, deberá explicar su efecto cerca del control; la ayuda necesaria no dependerá únicamente de hover.
- **Cuando** se muestre una función no disponible, deberá explicarse el motivo conocido y una alternativa real; no se ofrecerán botones sin implementación ni promesas de soporte, recuperación o notificación inexistentes.
- **Cuando** un texto requiera traducción o formato repetido, deberá reutilizarse su definición pertinente, sin introducir un sistema multidioma completo ni traducir automáticamente contenido escrito por usuarios.

### RF-19. Adaptación a dispositivos y accesibilidad de interacción

**Requisito:** poder completar las tareas esenciales sin ratón ni una pantalla grande.

- **Siempre**, la interfaz deberá funcionar desde 320 px CSS de ancho, en orientación vertical y horizontal, sin desbordamiento horizontal global ni controles esenciales ocultos. Tablas, código y diagramas podrán tener desplazamiento interno identificado cuando sea necesario por su naturaleza.
- **Cuando** se amplíe el texto al 200 % o se evalúe redistribución a 400 % de zoom sobre 1280 px de ancho, deberán conservarse contenido y acciones, salvo desplazamiento bidimensional acotado a contenido que lo requiera.
- **Cuando** se navegue con teclado, deberán existir orden lógico, foco visible no tapado por encabezados o paneles y un enlace para saltar al contenido principal. Ninguna tarea dependerá solo de arrastrar, hover o gestos.
- **Cuando** se use móvil y teclado virtual, el campo activo y la acción de envío/guardado deberán seguir siendo alcanzables mediante desplazamiento; diálogos y paneles no los ocultarán permanentemente.
- **Cuando** se active reducción de movimiento, deberán desactivarse animaciones decorativas continuas, desplazamiento suave y efectos de parallax/inclinación, manteniendo una indicación estática de carga y estados.

### RF-20. Documentación y trazabilidad del sistema visual

**Requisito:** permitir mantener y verificar la interfaz sin redescubrir sus convenciones.

- **Antes de** implementar, el plan deberá relacionar cada RF/RNF con pantallas, patrones/componentes afectados, entregables y verificación, usando el identificador SPEC-002 también en tareas, commits y revisión.
- **Cuando** se construya el sistema visual, deberá conservarse una guía del catálogo de estilos y componentes con propósito, variantes, entradas/eventos, ejemplos mínimos de composición, estados, temas y requisitos de accesibilidad. Será documentación proporcional, no un portal nuevo de componentes.
- **Cuando** se cierre una construcción, deberá existir una lista por requisito con resultado, evidencia y defectos, distinguiendo revisión de código, pruebas controladas, integración y sistema.
- **Si** aparece una necesidad incompatible con los límites aprobados, deberá actualizarse y aprobarse primero la spec, sin ampliar silenciosamente el alcance bajo una refactorización UI.

## 5. Requisitos no funcionales

| ID | Requisito y criterio verificable |
|---|---|
| RNF-1 — Stack y sencillez | Conservar Vue/JavaScript, Flask/Python, SQL Server y n8n; aprovechar Vuetify, Tailwind, FullCalendar, Mermaid y DOMPurify existentes. No migrar framework, añadir otra biblioteca UI, TypeScript, un framework propio ni dependencias sin necesidad justificada y aprobación según la constitución. |
| RNF-2 — Separación y mantenibilidad | Una fuente identificable para roles visuales y preferencia de tema; estilos específicos acotados a su componente. Sin paletas claro/oscuro duplicadas por vista, dependencias circulares ni reglas de negocio en presentación. La revisión de consumidores, contratos y diff verificará RF-5; nombres y comentarios nuevos en inglés, existentes conservados. |
| RNF-3 — Accesibilidad medible | Usar WCAG 2.2 nivel AA como referencia y evaluar criterios aplicables a las pantallas/recorridos intervenidos: contraste de texto normal ≥ 4,5:1, texto grande ≥ 3:1 y componentes/indicadores necesarios ≥ 3:1 conforme a sus excepciones; nombres/roles/estados accesibles, errores asociados, anuncios de estado sin repetir todo el historial, foco y teclado. Controles táctiles propios de al menos 24 × 24 px CSS o separación equivalente permitida; acciones principales preferentemente 44 × 44. No declarar conformidad integral sin auditoría suficiente; documentar límites de contenido generado de RF-16. |
| RNF-4 — Rendimiento y estabilidad | En el entorno de referencia fijado antes de implementar, el cambio de tema y feedback de interacción local deberán hacerse visibles en ≤ 200 ms en al menos el 95 % de 20 repeticiones por interacción seleccionada. No medir latencia de IA/API como rendimiento UI. Conservar carga bajo demanda de recursos pesados, evitar remontar vistas o repetir HTTP al cambiar tema y comprobar ausencia de listeners, temporizadores o escuchas duplicados tras 20 ciclos de entrada/salida. |
| RNF-5 — Compatibilidad | Verificar Chrome, Edge y Firefox estables en escritorio Windows; Chrome Android y Safari iOS estables para los recorridos móviles esenciales, registrando versiones y dispositivo o emulación real utilizada. Emular un viewport de escritorio no acredita Safari/iOS. Falta de dispositivo o navegador: prueba no ejecutada, no aprobación. Dictado y efectos decorativos son mejoras progresivas, nunca prerrequisito. |
| RNF-6 — Seguridad y privacidad | No persistir datos privados nuevos para preferencias o borradores; no filtrar excepciones, secretos o contenido ajeno. Mantener sanitización y autorización backend. Fixtures y evidencias ficticios/saneados; no introducir telemetría, grabación de sesiones ni dependencias externas para medir uso. |
| RNF-7 — Compatibilidad funcional | Conservar endpoints, campos, códigos HTTP, límites, identidad institucional, reglas de negocio y estructura SQL. No migraciones ni cambios de workflows. Los únicos cambios de comportamiento son los especificados aquí en presentación/interacción. No alterar contenido persistido al cambiar apariencia. |
| RNF-8 — Verificación reproducible | Documentar herramientas, preparación, pasos PowerShell cuando proceda, recursos, esperado, obtenido y límites de cada modalidad. Evidencia con fecha, versión/commit, cambios locales, caso, rol, tema, viewport, navegador y resultado. Un build, lint o revisión visual aislada no sustituye integración, teclado ni sistema. |

Los valores exactos de paletas, escala tipográfica, espaciado, tamaños de página, puntos de adaptación y entorno de medición se fijarán en el plan/catálogo antes de implementar, respetando estos mínimos. Son decisiones de diseño, no permiso para reducir el alcance.

## 6. Casos límite

| Caso | Resultado exigido | Referencias |
|---|---|---|
| Primera visita; preferencia ausente o corrupta | Sistema y fallback Claro; sin fallo de arranque | RF-2, RF-3 |
| Almacenamiento bloqueado o varias pestañas | Selección temporal operativa; sincronización cuando el navegador la notifique | RF-3 |
| Cambio de tema mientras se edita, dicta, carga o hay un diálogo abierto | Mantener datos, foco y operación; actualizar todas las superficies sin nuevas solicitudes | RF-2 a RF-4, RF-15 |
| Cambio de preferencia del sistema con selección explícita | Respetar Claro/Oscuro; solo Sistema sigue al dispositivo | RF-2 |
| Nombres, emails, títulos o mensajes muy largos | Ajuste o truncado con acceso al contenido completo, sin desbordamiento global | RF-11, RF-14, RF-19 |
| Listado vacío, filtro sin coincidencias o última fila eliminada | Estados distintos y navegación de lista válida | RF-7, RF-11 |
| Respuestas fuera de orden tras cambiar de entidad o periodo | Mantener el contexto vigente y descartar efectos visuales obsoletos | RF-7 |
| Doble clic, Enter repetido o composición IME | No duplicar envío desde el control; respetar composición de texto | RF-7, RF-15 |
| Timeout después de posible guardado o envío | Resultado no confirmado; consultar antes de repetir, sin reintento automático | RF-10, RF-15 |
| Sesión expirada mientras hay un formulario o mensaje abierto | Limpiar datos privados, detener dictado y volver a login con explicación | RF-10, RF-15 |
| Rol o matrícula cambia después de cargar la pantalla | Respetar rechazo backend sin inferir acceso por datos antiguos | RF-10, RF-14 |
| Cancelar selector, retirar archivo o elegir el mismo nuevamente | Selección visible y recuperable; no envío implícito | RF-12 |
| Selección Excel y resultado completo, parcial o rechazado | Mostrar selección, ayudas y resultado recibido sin convertir un fallo en éxito ni reenviar automáticamente | RF-12 |
| PDF vacío, exceso de tamaño/cantidad o trabajo desconocido | Rechazo/estado comprensible según contrato, sin progreso ficticio | RF-13 |
| Recursos temporales RAG perdidos | Informar resultado real del reintento; no prometer recuperación inexistente | RF-13 |
| Imagen inválida, permiso de micrófono denegado o dictado no soportado | Corrección posible y escritura manual disponible | RF-15 |
| Mermaid inválido, enorme o sin alternativa descriptiva | Fallo local, texto/fuente disponibles, ampliación contenida y límite de accesibilidad registrado | RF-4, RF-16 |
| Agenda sin eventos; indicador cero, ausente o ilimitado | Mensaje/valor diferenciados y lectura alternativa | RF-17 |
| Móvil con teclado, zoom alto o movimiento reducido | Acciones alcanzables, foco visible y alternativa sin animación | RF-19; RNF-3, RNF-5 |
| Navegador o integración real no disponible para probar | Registrar bloqueo y no ejecutado; no sustituirlo por una aprobación con mocks | RF-20; RNF-8 |

## 7. Verificación y evaluación PUDS

### 7.1 Planificar y diseñar integración

- El plan definirá construcciones, alcance, recursos, entorno de rendimiento, matriz pantalla–estado–tema–viewport y criterios de aceptación antes de implementar. No se requiere analizar otros tres algoritmos por cumplir una cantidad.
- Todas las superficies de §2 tendrán una comprobación de presentación y acceso a su tarea principal en ambos temas. Los patrones compartidos se probarán en profundidad una vez y se comprobarán sus integraciones por rol; no se duplicarán todas las combinaciones de CRUD.
- Matriz visual mínima: 320 × 568, 390 × 844, 768 × 1024 y 1440 × 900 px CSS; cambios de orientación, zoom y teclado virtual se añadirán a recorridos relevantes. El plan asignará navegadores según riesgo, sin exigir el producto cartesiano de todos los casos.
- Preparar respuestas controladas para carga, vacío, fallo, retrasos, cuotas visibles, estados RAG y respuestas del tutor. Se identificarán como simulaciones; no certifican API, SQL, proveedores ni calidad educativa.
- Preferir herramientas disponibles, navegador/DevTools y procedimientos manuales documentados. Cualquier dependencia adicional de pruebas deberá justificarse antes de instalarse. No se presupone un servidor de catálogo, plataforma de capturas ni pipeline.

### 7.2 Cobertura mínima prevista

Los siguientes son grupos de verificación propuestos, **no pruebas ejecutadas**. El registro posterior desglosará casos con pasos y aserciones y creará una fila por RF/RNF.

| Grupo | Comprobación esencial | Cobertura |
|---|---|---|
| UI-01 | Paleta verde/blanca formalizada y mapeo de colores actuales a tokens; revisión comparativa luminosa/inspiradora; consumidores compartidos, guía y trazabilidad | RF-1, RF-5, RF-20; RNF-1, RNF-2 |
| UI-02 | Claro/Oscuro/Sistema; primera visita, recarga, logout, almacenamiento bloqueado, otra pestaña y overlays abiertos | RF-2, RF-3, RF-4; RNF-4, RNF-7 |
| UI-03 | Login, navegación de los tres roles, retorno con filtros, rutas inválidas, expiración y denegación | RF-6, RF-10; RNF-6, RNF-7 |
| UI-04 | Formularios, diálogos y avisos con error, guardado, salida con cambios, doble envío y timeout incierto | RF-7, RF-8, RF-9, RF-18; RNF-3, RNF-6 |
| UI-05 | Listados de administración/coordinación, selección Excel, ayudas y presentación de resultados completos/parciales/rechazados | RF-11, RF-12; RNF-7 |
| UI-06 | Configuración de tutor y estados de conocimiento, límites PDF, reintento no disponible y confirmación de limpieza | RF-13; RNF-6, RNF-7 |
| UI-07 | Conversación, modos, lectura/scroll, borrador, imagen, dictado, indisponibilidad y diagrama fallido/ampliado | RF-14, RF-15, RF-16; RNF-3, RNF-6, RNF-7 |
| UI-08 | Agenda/lista equivalente y analíticas: filtros, fechas, unidades, cero/sin datos/ilimitado y lectura textual | RF-17; RNF-3, RNF-7 |
| UI-09 | Teclado y lector de pantalla, contraste en ambos temas, foco, idioma, móvil, zoom, movimiento y rendimiento | RF-1, RF-4, RF-18, RF-19; RNF-3, RNF-4, RNF-5 |
| UI-10 | Ejecución, regresión pertinente, limpieza, checklist y decisiones sobre defectos | RF-20; RNF-6, RNF-7, RNF-8 |

### 7.3 Ejecutar integración y regresión

- Verificar la composición real de tema, estructura de panel, componentes, routing y servicios existentes. Distinguir integración frontend con respuestas controladas de integración con backend y SQL reales.
- Reutilizar [los procedimientos de pruebas existentes](../../../testing/README.md) y la [matriz de regresión](../../../testing/REGRESSION.md) según impacto: S-1 para rechazo de alta, S-2 como regresión del flujo de importación si se modifica su presentación y S-3/S-3b para creación/denegación de conversaciones. Mantener sus IDs y referenciar la nueva versión evaluada. Los fallos funcionales previos se registran, pero su reparación no se incorpora a este incremento.
- Cuando se reutilice lógica cubierta por A-1/A-2/A-3, ejecutar la suite aislada existente completa y pequeña, identificando los casos pertinentes; no inventar un filtro inexistente. I-1 a I-4 se seleccionarán según impacto y se justificarán las exclusiones.
- Usar autorización nueva, destino local verificado, fixtures ficticios propios y limpieza comprobada para pruebas reales. El soporte de SPEC-001 no autoriza datos nuevos de mensajes, consumo o RAG: esas interfaces se simularán para UI, o requerirán diseño de preparación/recuperación aprobado antes de ejercitar persistencia adicional.
- No invocar IA, indexar documentos, consumir tokens ni enviar notificaciones para comprobar estilos y estados. Los dobles permiten verificar presentación de sus contratos, no disponibilidad de servicios externos.

### 7.4 Ejecutar sistema y evaluar

- Al terminar cada iteración, recorrer en la aplicación integrada las tareas críticas del alcance construido y, al finalizar el incremento, login, navegación/perfil por rol, un flujo administrativo, alta/importación de estudiantes y creación de conversación, en ambos temas y con recorrido móvil pertinente.
- Comprobar con teclado y al menos un lector de pantalla una muestra representativa de cada patrón interactivo compartido, incluyendo formulario, diálogo, navegación, tabla/lista, chat y agenda. Documentar herramienta, versión, pasos y anuncios observados; un análisis automatizado no sustituye estas comprobaciones.
- Registrar evidencia visual mediante observaciones comparativas concretas y mediciones de contraste/viewport; las capturas saneadas pueden complementarlas, pero no son obligatorias ni sustituyen interacción. SQL no demuestra apariencia ni comportamiento del navegador.
- Cada caso conservará requisito, preparación, esperado, obtenido, modalidad, entorno, fecha/versión, referencia a evidencia y limpieza. El documento de pruebas de SPEC-002 centralizará el checklist; no se sobrescribirá evidencia histórica.
- Estados permitidos: **aprobado**, **fallido**, **no ejecutado** y **no aplicable con justificación**. Un bloqueo o falta de navegador es no ejecutado. Una prueba con datos simulados no aprueba su equivalente de sistema real.
- Ante fallos, notificar al responsable y registrar su decisión de prolongar la construcción, diferir corrección o asignar investigación. Un requisito fallido o no ejecutado no se declarará cumplido aunque se decida cerrar trabajo.
- Los defectos previos ajenos al alcance conservan su registro histórico y no se declaran corregidos por un rediseño visual. Si bloquean un recorrido, se registra el resultado y la decisión del responsable, sin ampliar silenciosamente esta spec.

## 8. Fuera de alcance

- Rediseñar reglas de negocio, cuotas, precios, vigencia, matrícula, roles o autorización; solucionar concurrencia, idempotencia o seguridad integral del backend.
- Cambiar esquema SQL, endpoints, payloads, códigos HTTP, workflows n8n o proveedores; modificar modelos/prompts por razones ajenas a presentar su configuración existente.
- Registro público UI, recuperación por correo, SSO/MFA, nuevos roles, nuevas métricas, evaluaciones/calificaciones, edición de agenda, notificaciones, pagos, colaboración o compartir conversaciones.
- Streaming, cancelación real de generación, generación de descripciones accesibles por IA, nuevas funciones de exportación, búsqueda global o procesamiento de audio en servidor.
- Personalización por institución de marca/paleta, sincronización de tema entre dispositivos, editor de temas, multidioma, aplicación nativa, PWA u operación offline.
- Persistencia nueva de borradores, archivos locales o reintentos transaccionales. La preferencia visual es el único dato persistente cliente nuevo previsto.
- Migración de biblioteca UI, reescritura total del frontend, abstracciones preventivas, portal de componentes, analítica de uso/telemetría, CI/CD o infraestructura de pruebas no justificada.
- Reparar defectos funcionales previos del MVP, incluidos los del flujo de importación Excel, o defectos del ejecutor de pruebas. Las correcciones ajenas a presentación/interacción requieren otro alcance aprobado; las regresiones introducidas por este incremento sí deben tratarse.
- Certificar calidad de respuestas IA, recuperación RAG extremo a extremo, cumplimiento WCAG global de contenido externo o ausencia de todas las limitaciones del baseline.

## 9. Criterios de finalización

### 9.1 Aprobación de la especificación

La especificación figura **aprobada** en su cabecera. Por indicación del responsable se excluye la reparación del problema funcional de Excel; RF-12 conserva únicamente los requisitos de presentación e interacción. Claro/Oscuro/Sistema, preferencia local compartida por navegador y temas completos forman parte del alcance aprobado.

El plan concreta diseño visual, componentes afectados, etapas y verificación sin ampliar requisitos y se revisa antes de implementar; después se desglosan tareas verificables. La aprobación de la spec no aprueba automáticamente el plan ni acredita implementación o pruebas ejecutadas.

### 9.2 Finalización de la construcción posterior

- [ ] Paleta verde/blanca formalizada, colores actuales mapeados a tokens y muestra de dirección visual revisada; Claro luminoso y Oscuro verde suavizado sin grandes fondos negros/carbón. Todas las superficies incluidas funcionan en ambos temas con estados coherentes y contraste verificado.
- [ ] Preferencia inicial, persistencia/fallback, cambios del sistema y cambios en caliente verificados sin pérdida de contexto.
- [ ] Componentes compartidos y específicos tienen responsabilidades/contratos claros; se migraron consumidores y retiró duplicación reemplazada.
- [ ] Formularios, listas, confirmaciones, errores, carga, navegación, chat, agenda y recursos satisfacen sus criterios de interacción y accesibilidad evaluados.
- [ ] Selección, ayudas y resultados de archivos satisfacen RF-12; cualquier bloqueo funcional previo se distingue de la evaluación de presentación, sin reparación ni aprobación ficticia.
- [ ] Catálogo visual y documentación de uso disponibles; build/lint pertinentes y regresión ejecutada documentados, sin confundirlos con sistema.
- [ ] Integración y sistema pertinentes ejecutados, con matriz de temas/dispositivos, evidencia de accesibilidad/rendimiento y limpieza de datos propios.
- [ ] Checklist individual de todos los RF/RNF con estado, evidencia y defectos; bloqueos y decisiones registrados sin aprobaciones ficticias.
- [ ] Revisión confirma contratos, reglas y persistencia conservados y cumplimiento de los seis principios constitucionales.

**Cerrar una etapa con defectos diferidos no equivale a cumplir íntegramente SPEC-002.** El veredicto final deberá separar entregables completados, comportamientos aprobados, fallidos y no verificados.

## 10. Alineación constitucional

| Principio | Aplicación en SPEC-002 |
|---|---|
| I. Simplicidad del stack | Reutilizar tecnologías y componentes existentes; sin migración ni dependencias preventivas (RF-5; RNF-1) |
| II. Relación spec–código | Spec aprobada, plan revisable antes de implementar, IDs trazables, cambios acotados y aprobación previa de desviaciones (RF-20; §9) |
| III. Lógica e interfaz | Presentación por composición; servicios existentes y autoridad backend, sin reglas duplicadas (RF-5, RF-8; RNF-2, RNF-7) |
| IV. PUDS | Planificar, diseñar/ejecutar integración, ejecutar sistema y evaluar cada requisito con resultados y decisiones (§7) |
| V. Persistencia, contratos y configuración | SQL sigue como fuente de verdad; sin migraciones ni contratos nuevos; preferencia visual no sensible, recuperación transaccional existente conservada (RF-3; RNF-6, RNF-7) |
| VI. Idioma y mensajes | Documentación/mensajes en español; identificadores/comentarios nuevos en inglés; errores públicos seguros (RF-10, RF-18; RNF-2, RNF-6) |

## 11. Decisiones de alcance y concreción posterior

El alcance aprobado incluye Sistema por defecto, preferencia por navegador y dos temas completos. La reparación de defectos funcionales previos de Excel queda expresamente excluida por indicación del responsable.

La dirección visual actualizada exige formalizar la paleta, estandarizar los colores existentes y priorizar verde/blanco con tonalidades más claras e inspiradoras, también suavizando el tema oscuro. No implica eliminar Oscuro ni cambiar Sistema por defecto; los códigos y parejas concretos se revisan en el plan antes de implementar.

El detalle de paletas, medidas, puntos de adaptación, estructura concreta de módulos y herramientas de verificación corresponde al plan posterior. Si al concretarlo se descubre una imposibilidad de cumplir un requisito sin cambiar contratos o añadir alcance, se registrará el bloqueo y se revisará la spec antes de implementar.
