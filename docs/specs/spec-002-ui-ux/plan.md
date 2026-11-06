# PLAN-002 — Sistema visual y experiencia de usuario de TutorIA

## 1. Estado, objetivo y alcance

**Estado:** aprobado por el responsable, incluida la paleta de §3.1.  
**Fecha:** 2026-09-30.  
**Fecha de aprobación del plan y paleta:** 2026-10-31.  
**Especificación:** [SPEC-002 aprobada](spec.md), con reparación de defectos funcionales previos de Excel excluida por indicación del responsable.  
**Gobernanza:** [Constitución](../constitution.md).  
**Baseline cerrado:** [Spec-000 — MVP](../spec-000-mvp/Spec-000-mvp.md).  
**Regresión:** [registro de SPEC-001](../spec-001-tests/test.md) y [criterios proporcionales](../../../testing/REGRESSION.md).

Implementar una interfaz coherente, accesible y adaptable para las funcionalidades existentes, con Claro/Oscuro/Sistema y composición reutilizable. Este documento define cómo construir y comprobar el incremento; **su aprobación no acredita implementación ni ejecución de pruebas**.

La dirección visual actualizada por el responsable es **verde y blanco, más luminosa, amable e inspiradora**. Se formalizará la paleta y se estandarizarán los colores existentes; el verde será un color principal de identidad y acción, no solo un acento. Se sustituye la propuesta anterior de fondos negros/gris carbón por un Oscuro verde desaturado y más suave, sin eliminar esa opción ni alterar Sistema por defecto.

**Decisión registrada el 2026-10-31:** ante la discrepancia entre T01 marcada y la cabecera propuesta, el responsable seleccionó explícitamente **«Apruebo el plan actual y su paleta»**. Se aprueba el contenido actual del plan, incluidos los códigos de §3.1, exclusiones y modalidades de verificación. Las parejas renderizadas siguen requiriendo pruebas de contraste. Esta decisión resuelve C0-G01 y permite cerrar T01 documentalmente; no se retrodata a C0 ni autoriza ejecutar C1–C5 durante la consolidación documental.

### 1.1 Incluido

- Login y estructura de panel de los tres roles; rutas y secciones internas, incluido perfil por rol.
- Instituciones, planes, suscripciones y coordinadores; cursos, detalle, cuentas, institución y analíticas.
- Configuración del tutor, selección PDF y presentación del conocimiento/trabajos existentes.
- Conversaciones, modos, composición, imagen, dictado, diagramas, agenda y sus alternativas textuales.
- Tokens, temas, navegación, estados, formularios, confirmaciones, listas, selección de archivos, idioma y documentación de uso.
- Integración frontend, regresión pertinente y recorridos de sistema, diferenciando datos controlados de servicios reales.

### 1.2 Límites

- No modificar backend, esquema SQL, workflows, endpoints, campos, códigos HTTP, cuotas, permisos ni lógica transaccional. Las comprobaciones cliente de formato/tamaño son ayuda, no autorización.
- RF-12 cubre nombres/ayudas/retirada de archivos y presentación de respuestas existentes. **No reparar el fallo previo de Excel ni cambiar el enlace selector–manejador–servicio para solucionarlo**, normalizar su envío o reescribir el importador. Su conservación no permite comunicar éxito falso.
- No introducir otra biblioteca UI, TypeScript, portal de componentes, framework de formularios, gráficos o internacionalización, telemetría ni persistencia de borradores. No instalar herramientas de pruebas sin justificar y aprobar su necesidad.
- No migrar todos los componentes de ubicación por estética ni realizar refactorizaciones sin requisito. Cada extracción migra sus consumidores y retira únicamente la duplicación sustituida.
- No ejecutar IA, indexación, consumo ni notificaciones para probar apariencia. Las pruebas reales requieren destino, autorización, fixtures y recuperación aprobados; este plan no concede esa autorización.

## 2. Base técnica comprobada y estrategia

La inspección de fuente confirma Vue/JavaScript, Pinia, Vue Router, Axios, Vuetify, Tailwind, Mermaid y DOMPurify; [las dependencias y scripts declarados](../../../frontend/package.json) son la referencia, no una afirmación sobre versiones realmente instaladas.

| Base existente | Decisión del incremento |
|---|---|
| [Arranque](../../../frontend/src/main.js), [HTML inicial](../../../frontend/index.html) y [raíz](../../../frontend/src/App.vue) | Resolver apariencia antes del contenido; montar una sola aplicación; no usar una clave de tema que remonte `router-view` |
| [Vuetify](../../../frontend/src/plugins/vuetify.js), [Tailwind](../../../frontend/tailwind.config.js) y [CSS global](../../../frontend/src/style.css) | Sustituir colores fijos por roles semánticos; preservar `corePlugins.preflight: false` para no reintroducir conflictos con las capas CSS de Vuetify |
| [Router](../../../frontend/src/router/index.js) | Conservar rutas válidas y guards por rol; añadir presentación de ruta inexistente, título y foco, sin nuevos permisos |
| [Cliente HTTP](../../../frontend/src/services/api.js) y [autenticación](../../../frontend/src/stores/auth.js) | Conservar contratos, autenticación e identidad; coordinar expiración con limpieza de estado privado y explicación pública |
| [RoleSidebar](../../../frontend/src/components/RoleSidebar.vue), [PanelTitle](../../../frontend/src/components/PanelTitle.vue), [ProfileSection](../../../frontend/src/components/ProfileSection.vue) | Mejorar y reutilizar; no crear copias para otro rol o tema |
| [MermaidMessage](../../../frontend/src/components/MermaidMessage.vue) | Conservar entrada `content`, importación diferida y sanitización; adaptar paleta, foco, errores locales y alternativa de fuente |
| [Login](../../../frontend/src/views/Login.vue) y [SynapseBackdrop](../../../frontend/src/components/SynapseBackdrop.vue) | Conservar identidad sin depender de efectos; revisar movimiento, contraste y controles nativos |
| [Panel de estudiante](../../../frontend/src/views/EstudianteDashboard.vue) | Separar responsabilidades de conversación, composición y agenda; el calendario actual contiene una cuadrícula propia: no sustituirlo por FullCalendar solo porque la dependencia esté instalada |
| [Panel superadmin](../../../frontend/src/views/SuperAdminDashboard.vue) y [layout coordinador](../../../frontend/src/views/coordinador/CoordinadorLayout.vue) | Extraer estructura repetida, manteniendo cada contenedor responsable de servicios y decisiones de su rol |

El modelo será **contenedor de funcionalidad → componente específico → patrón compartido → Vuetify/CSS semántico**. Las vistas coordinan solicitudes y adaptan respuestas; los componentes visuales reciben datos y emiten intención. No se crea una capa HTTP adicional ni un esquema universal de entidades.

## 3. Diseño visual y apariencia

### 3.1 Catálogo inicial

La paleta siguiente fue aprobada explícitamente el 2026-10-31 como diseño. Se comprobarán las parejas efectivamente renderizadas, incluyendo opacidad, hover, disabled, foco y superposición; la aprobación de los códigos no acredita contraste en ejecución. Un ajuste que respete los roles, identidad y mínimos de contraste se registra en el catálogo, sin duplicar valores por vista.

#### Dirección y paleta de marca

- **Claro:** blanco y blanco roto dominan las superficies de lectura; menta/salvia claros distinguen regiones y selección, y verde medio/profundo da contraste a acciones y texto de marca. Aire, bordes suaves y sombras ligeras, sin grandes paneles verdes saturados.
- **Oscuro suave:** fondos y superficies verde salvia/bosque desaturado de luminosidad moderada, claramente más claros que #17181C/#1E1F25/#26272E del baseline. Blanco roto en contenido principal y verdes claros en acciones mantienen la identidad. No emplear negro puro ni gris carbón como grandes superficies de shell, sidebar, tarjetas, formularios o chat.
- Blanco es un color principal de marca, no la obligación de llenar de blanco una pantalla Oscuro; en esa variante se expresa en contenido y contraste de identidad. El tema sigue siendo una alternativa de menor luminosidad que Claro.
- La cualidad «inspiradora» se concreta en apertura, jerarquía legible, espacio y verde coherente; se valida mediante revisión comparativa del responsable sobre login, un panel administrativo y chat. No se afirma una respuesta emocional medida ni se añaden animaciones para simularla.

| Escala de marca | Valor propuesto | Uso permitido |
|---|---|---|
| `brandWhite` | #FFFFFF | Superficies Claro e identidad; no usar como texto sobre verde claro sin comprobar contraste |
| `green50` | #F1F8F2 | Fondo claro teñido |
| `green100` | #E4F2E7 | Superficie secundaria clara |
| `green200` | #D2E6D8 | Apoyo suave; nunca texto pequeño sobre blanco |
| `green300` | #A6DEAD | Acción/acento legible sobre superficies Oscuro |
| `green400` | #7CC576 | Verde actual conservado como referencia de marca/decoración; no texto pequeño sobre blanco |
| `green500` | #2F7D46 | Acción principal Claro, con texto blanco |
| `green600` | #246B35 | Hover/foco y texto de marca en Claro |
| `green700` | #405C4E | Superficie elevada Oscuro |
| `green800` | #354F43 | Superficie Oscuro |
| `green900` | #2C4238 | Fondo Oscuro suave; no volver al casi negro del baseline |

La numeración expresa una escala de uso/luminosidad, no permiso para aplicar cualquier tono a cualquier elemento. Las vistas consumen **roles semánticos**, no posiciones de esta escala; la tabla siguiente fija los roles. Las dos tablas se documentan, pero la implementación guarda cada valor canónico una vez y referencia su equivalente de marca donde coincide.

| Rol semántico | Claro | Oscuro | Uso |
|---|---|---|---|
| `background` | #F1F8F2 | #2C4238 | Fondo de aplicación, menta / verde suave |
| `surface` | #FFFFFF | #354F43 | Formularios, tarjetas y diálogos |
| `surfaceRaised` | #E4F2E7 | #405C4E | Superficie secundaria/elevada |
| `textPrimary` | #1C3828 | #F7FCF8 | Contenido principal |
| `textSecondary` | #46594D | #D2E6D8 | Ayuda y metadatos legibles |
| `borderDecorative` | #CCDCCF | #6D8D79 | Separación decorativa; no única señal de control |
| `borderControl` | #637569 | #ADC9B6 | Contorno necesario de controles |
| `primary` | #2F7D46 | #A6DEAD | Acción e identidad TutorIA |
| `primaryHover` | #246B35 | #B9E8BF | Hover de acción principal |
| `onPrimary` | #FFFFFF | #203D2B | Texto sobre acción primaria/hover |
| `primarySoft` | #E0F3E3 | #466650 | Selección y énfasis suaves, no nueva superficie general |
| `onPrimarySoft` | #245D35 | #E1F5E5 | Texto/icono de selección suave |
| `focus` | #246B35 | #B9E8BF | Indicador de foco visible |
| `error` | #B42332 | #FFCACB | Texto/icono de error sobre superficie |
| `warning` | #7A4B00 | #FFE0A3 | Texto/icono de advertencia |
| `success` | #246B35 | #A6DEAD | Texto/icono de éxito |
| `info` | #175E9B | #B9DDF8 | Texto/icono informativo |

Los colores de estado son funcionales secundarios, no otra identidad de marca. No reutilizar sus tonos de texto como fondo sin definir y verificar su pareja `on-*`. Disabled conserva nombre/explicación/estado distinguible; no crear un hexadecimal por vista ni bajar opacidad de forma que pierda legibilidad necesaria.

#### Estandarización de los colores actuales

1. Inventariar valores en configuración Vuetify, Tailwind, CSS global/scoped, estilos inline/SVG, calendario y Mermaid. Registrar consumidor, función, estado/tema, origen y token sustituto.
2. Mapear los fondos actuales #17181C/#1E1F25/#26272E a `background`/`surface`/`surfaceRaised`, no simplemente aclarar cada hexadecimal de forma independiente. Convertir blancos translúcidos y grises de texto/borde a sus roles; el verde actual #7CC576 se mantiene como referencia de marca, no como texto sobre blanco.
3. Migrar por superficie junto con hover/foco/selección/disabled/overlays y retirar sus estilos sustituidos. Fotografías/documentos/contenido ajeno conservan color; excepciones técnicas deben tener motivo y pareja accesible documentados. No permitir excepciones decorativas para recuperar grandes fondos negros.
4. Revisar muestra comparativa login–administración–chat: Claro luminoso con predominio blanco/menta, Oscuro suavizado, verde/blanco reconocibles, espacios/jerarquía e identidad consistente. Registrar decisión de diseño separada de contraste/pruebas funcionales.

- Fuente local: `system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`; sin descargas nuevas. Base 16 px/1,5; ayudas 14 px/1,5; títulos de bloque 20 px/1,35; título de página 28 px/1,25 y 24 px en móvil. Los encabezados mantienen jerarquía HTML independiente del tamaño.
- Espaciado: 4, 8, 12, 16, 24, 32 y 48 px, expresado en unidades escalables cuando corresponda. Radios: 8 px en controles, 12 px en tarjetas y 16 px en diálogos.
- Elevación: plana para regiones, una sombra discreta para tarjetas elevadas y otra para overlays; definiciones únicas por tema. Sin glow obligatorio ni transparencias que reduzcan contraste. El scrim no sustituye el bloqueo de interacción del fondo.
- Foco: contorno de 2 px con separación de 2 px, conservado en ambos temas; no eliminar el foco nativo sin equivalente. Acciones principales con objetivo táctil de 44 × 44 px; controles secundarios respetan el mínimo/alternativa de separación de RNF-3.
- Página: ancho máximo 1440 px para administración; lectura de texto larga aproximadamente 72 caracteres por línea cuando no sea tabla/código. Espaciado lateral 12 px a 320 px, 16 px desde 600 px y 24 px desde 960 px.
- Adaptación: menos de 600 px, una columna; de 600 a 959 px, composición intermedia; desde 960 px, navegación persistente y columnas cuando haya espacio. Priorizar ancho disponible, no detección de dispositivo.
- Listados: 10 registros por página inicialmente; opciones 10/25/50, conteo y controles accesibles. Filtrar/ordenar antes de paginar los registros recibidos; ajustar página si queda vacía. No incorporar consulta o paginación de servidor.
- Diálogo estándar: hasta 640 px y márgenes de 12 px; diagrama ampliado hasta 1200 px. Alto limitado al viewport dinámico, contenido desplazable y acciones alcanzables con teclado virtual. No resolver overflow ocultando acciones.
- Capas: utilizar la jerarquía de Vuetify para drawer, diálogo, menú y tooltip; centralizar excepciones justificadas en CSS, sin `z-index` por vista. Verificar foco no oculto por barras persistentes.

### 3.2 Una fuente de color y un controlador de preferencia

**Módulos previstos, todavía no creados:** hoja `frontend/src/styles/tokens.css`, controlador temprano `frontend/public/appearance.js` y adaptador Vue `frontend/src/composables/useAppearance.js`.

1. La hoja de tokens define ambas paletas mediante selectores `data-theme`, además de tipografía, medidas y sombras. Será la fuente de valores; Vuetify, utilidades Tailwind y estilos específicos los consumirán, no mantendrán otra paleta literal.
2. Cargar esta hoja desde el HTML inicial y un script clásico síncrono pequeño en el encabezado, antes del cuerpo. El script no depende de Vue, router, HTTP ni usuario. La compilación Vite debe conservar el orden y las URLs válidas en desarrollo y producción.
3. El controlador valida `tutoria.appearance` con valores `light`, `dark`, `system`; si falta/es inválido, usa `system`. Resuelve `matchMedia('(prefers-color-scheme: dark)')`, con Claro si no hay soporte; aplica `data-theme` y `color-scheme` en la raíz antes de mostrar contenido.
4. Toda lectura/escritura de almacenamiento lleva manejo de excepción. Mantener selección en memoria si falla; no quitar ni reemplazar preferencias al cerrar sesión. Un evento `storage` válido sincroniza pestañas; eliminación vuelve a Sistema y valores inválidos se ignoran como preferencia desconocida.
5. El controlador expone solamente selección, tema resuelto, cambio y suscripción a apariencia; el adaptador Vue reutiliza ese controlador. Un solo listener de sistema y uno de almacenamiento por aplicación, con disposición explícita; no añadirlos por pantalla.
6. Para registrar Claro y Oscuro en Vuetify, obtener una vez los tokens calculados de ambas variantes con nodos de lectura temporales aislados y retirarlos antes de montar. Mapear los roles a las claves de Vuetify, incluidos `on-*` y variables de énfasis. El cambio posterior solo selecciona el tema registrado y actualiza la raíz, sin volver a leer/generar paletas ni remontar vistas.
7. Tailwind conservará utilidades de distribución y sustituirá colores semánticos por variables compatibles con su sintaxis de opacidad; retirar clases antiguas de color al migrar sus consumidores. La hoja global define fondo/estados base y los estilos scoped solo la composición específica.
8. El selector visual recibe selección/opciones y emite cambio; el contenedor/adaptador aplica la preferencia. Su texto es Claro/Oscuro/Sistema, con nombre accesible y estado seleccionado. Estará en login y todos los encabezados, no solo en perfil.

Validar ausencia de flash en carga fría/recarga con preferencia contraria al sistema y en el build servido; no basta ver el estado final. Menús teletransportados reciben tokens de la raíz. Imágenes no se invierten. Mermaid puede regenerar SVG localmente a partir de la misma fuente, nunca pedir otra respuesta al tutor.

### 3.3 Movimiento, texto e idioma

- Animaciones locales decorativas como máximo 150 ms; no introducir demoras artificiales. Con `prefers-reduced-motion: reduce`, detener fondo animado/tilt/parallax, eliminar smooth scroll y mostrar carga estática identificable.
- Configurar locale español de Vuetify y de cualquier widget realmente utilizado; compartir etiquetas de estado y formatos donde se repiten. No cambiar campos API ni traducir mensajes escritos por usuarios.
- Fechas/números con `Intl` español; decidir explícitamente si cada fecha representa instante, fecha civil o periodo UTC antes de formatear. Mostrar zona cuando cambie su interpretación. Costos estimados USD; ausente, cero e ilimitado se representan separadamente.

## 4. Estructura de módulos y contratos de presentación

Los nombres nuevos serán en inglés. Las ubicaciones siguientes son **previstas**, no archivos implementados. Se mantendrán los componentes existentes que ya cumplen el propósito y se evitarán envolturas de Vuetify que solo reenvíen atributos.

| Responsabilidad | Módulo/acción prevista | Consumidores y límites |
|---|---|---|
| Estructura de panel | `components/layout/AppShell.vue`, composición con RoleSidebar y PanelTitle existentes | Tres paneles; slots de título, contexto, herramientas y contenido; no conoce servicios ni permisos |
| Selector de apariencia | `components/common/AppearanceSelector.vue` + adaptador de §3.2 | Login y AppShell; sin almacenamiento o llamadas HTTP en el componente visual |
| Título y acciones de página | `components/common/PageHeader.vue` si la composición compartida aporta jerarquía real | Vistas coordinador y secciones administrativas; un título y acciones por tarea |
| Estado de región | `components/common/AsyncState.vue` | Carga, vacío inicial, sin coincidencias, error e indisponibilidad; mensaje/ayuda y evento de reintento manual |
| Confirmación | `components/common/ConfirmDialog.vue` | Identidad, consecuencia, texto de confirmar y pendiente; emite intención, nunca elimina entidades por sí mismo |
| Avisos | Mejorar [useToast](../../../frontend/src/composables/useToast.js) y presentar una única región de avisos por panel | Éxito breve sin foco; error accionable persistente o resumen local; limpiar mensajes privados al salir |
| Formularios | ProfileSection existente; `composables/useUnsavedChanges.js` para patrón repetido | Edición local/snapshot, confirmación de descarte y eventos; validación de negocio en backend |
| Listados | Vuetify + `composables/useListState.js` para filtros/página locales repetidos | Contratos simples, sin tabla universal CRUD; columnas/acciones en cada funcionalidad |
| Archivos | Vuetify + presentación común de ayuda/nombre/resumen donde haya duplicación real | No adaptar el envío Excel excluido; selección PDF e imagen conservan contratos específicos |
| Estudiante | `components/student/ConversationList.vue`, `ChatComposer.vue`, `AgendaPanel.vue` | Responsabilidades distintas; mensajes/sesiones/eventos entregados por el contenedor |
| Tutor y conocimiento | `components/coordinator/TutorSettingsForm.vue`, `KnowledgePanel.vue` | Estado de edición y estado de trabajos separados; no conocimiento de Pinecone/n8n ni llamadas propias |
| Recursos | MermaidMessage existente | Fuente `content`, render local aislado, sanitización, zoom/foco y alternativa textual |

### 4.1 Contratos mínimos a documentar al construir

| Patrón | Entradas / espacios | Eventos y garantías |
|---|---|---|
| AppShell | Navegación permitida, sección activa, nombre/contexto; slots de encabezado/contenido | Selección/logout hacia contenedor; skip link y contenido principal; no fetch al montar por tema |
| RoleSidebar | Conservar `role`, `icon`, `userName`, `items`, `active`, `permanentOnDesktop` actuales | Conservar `select`/`logout`; cualquier contrato controlado de apertura añadido se migra en todos los consumidores |
| AppearanceSelector | `modelValue`: light/dark/system; etiquetas españolas | `update:modelValue`; controles accesibles, sin remount de su contenedor |
| AsyncState | `status`, `message`, ayuda/acción; slot de contenido | `retry` solo si está permitido; `aria-busy` en región y estado anunciado sin ocultar resultados confirmados innecesariamente |
| ConfirmDialog | Apertura, título, identidad, consecuencia, pendiente, textos de acción | Confirmar/cerrar; foco inicial no destructivo, trap/restore; nunca promete cancelación del servidor |
| ProfileSection | Conservar `profile`; añadir estados pendientes/error/resultado por operación | Conservar `update-profile`, `update-password`, `notify`; no tratar `emit` como Promise ni como confirmación de guardado |
| ChatComposer | Borrador/imágenes, modo, disponibilidad/envío; estado de dictado coordinado | Actualizar borrador, enviar, retirar imagen, iniciar/detener dictado; no llamadas IA internas |
| KnowledgePanel | Curso, resumen, documentos, trabajos y pendientes por acción | Cargar/consultar/reintentar/eliminar/limpiar como intenciones; acciones solo según contrato actual |
| AgendaPanel | Periodo, filtros y actividades recibidas | Cambio de periodo/filtro y selección de detalle; calendario y lista comparten datos, ambos de lectura |

Los slots de acción no conceden permisos. El contenedor deriva opciones de la respuesta/rol actual y el servidor mantiene autorización. Cada contrato tendrá propósito, valores por defecto, estados, ejemplo mínimo y notas de foco/teclado en el catálogo.

### 4.2 Coordinación de estado y solicitudes

- Mantener estado de tema separado del estado autenticado. Al cerrar sesión/401, invalidar solicitudes visuales pendientes, detener dictado, retirar referencias a archivos/previews y limpiar datos privados, formularios, avisos y filtros de entidad. Revocar URLs de objetos si se usan. Solo apariencia sobrevive.
- Mantener búsqueda/filtros/página de cursos en memoria durante navegación de la misma sesión; no persistirlos en localStorage. Revalidar página tras actualización. No montar toda la aplicación con `KeepAlive` para conservar un listado.
- El contenedor mantiene contador/identidad de solicitud para lecturas que cambian por curso, institución, periodo o conversación. Aplicar resultados y `finally` solo si pertenecen al contexto vigente; desmontar/401 invalida el contexto. No asumir que descartar una respuesta cancela una mutación real.
- Bloquear repetición del mismo envío con pendiente por operación y restaurarlo tras respuesta/timeout. Lecturas recuperables tienen reintento manual; mutaciones/IA nunca reintento automático. Error de red/timeout tras mutación implica resultado no confirmado y consulta antes de repetir.
- Error público: usar mensajes seguros reconocidos del contrato, traducir estados técnicos pertinentes y fallback español para respuesta inesperada. No mostrar excepciones o `response.data` crudos. Un 403 no se transforma en logout indiscriminado ni habilita una ruta prohibida.
- Formularios: snapshot solo tras carga inicial/guardado confirmado; no sobrescribir edición con un refresh tardío. Mostrar errores asociados si el contrato lo permite y resumen/foco si no. Contraseñas siguen tratamiento sensible separado, sin borradores persistentes.
- Guard de cambios: integración con navegación SPA, cierre de diálogo y cambio de sección/conversación; botón Seguir editando/Descartar. Expiración/logout por seguridad limpia estado sin quedar atrapado por el guard. `beforeunload` solo mientras haya edición, sin prometer cobertura donde el navegador la restrinja.

## 5. Integración por superficie

| Superficie / fuentes existentes | Trabajo UI previsto | Verificación principal |
|---|---|---|
| [Login](../../../frontend/src/views/Login.vue) | Apariencia, etiquetas, password manager, errores genéricos, reducción de efectos y contraste | UI-02/03/04/09; credenciales inválidas sin revelar existencia |
| [Superadmin](../../../frontend/src/views/SuperAdminDashboard.vue) | AppShell, instituciones/planes/suscripciones/coordinadores y perfil; filtros/tablas/confirmaciones por sección | UI-03/04/05/09; identidad de institución y actualización después de confirmar |
| [Cursos](../../../frontend/src/views/coordinador/CursosListView.vue) | Encabezado, estado/lista/paginación, retorno con contexto, formularios y ayudas/resultados Excel | UI-03/04/05; sin reparación del envío Excel previo |
| [Detalle de curso](../../../frontend/src/views/coordinador/CursoDetalleView.vue) | Datos, estudiantes/matrículas y tutor/conocimiento como bloques; confirmaciones, estados, pendientes y archivos | UI-04/05/06; nombres públicos en español, límites contractuales |
| [Cuentas](../../../frontend/src/views/coordinador/CuentasView.vue) | Búsqueda del conjunto cargado, filas/acciones con nombre, edición y confirmación | UI-04/05/09; última fila y textos largos |
| [Institución](../../../frontend/src/views/coordinador/InstitucionConfigView.vue) | Datos/edición existentes y lectura de suscripción; diferenciar cero, ausente, ilimitado y vigencia | UI-04/08; sin cálculo nuevo de cuotas |
| [Analíticas](../../../frontend/src/views/coordinador/AnalyticsGlobalView.vue) | Periodos 7/30/90/personalizado y tipos existentes, KPIs/desgloses; valores/texto equivalentes y unidades | UI-07/08/09; respuestas tardías no sustituyen periodo activo |
| [Perfil coordinador](../../../frontend/src/views/coordinador/ProfileView.vue) y perfiles en ambos dashboards | Contrato de ProfileSection común con resultado real y cambios sin guardar | UI-04; error conserva datos permitidos y no cierra prematuramente |
| [Estudiante](../../../frontend/src/views/EstudianteDashboard.vue) | Conversaciones/contexto/modos, composición, historial, recursos, agenda y perfil | UI-03/07/08/09; sin creación/envío al cambiar tema o modo |
| Router y overlays compartidos | Not-found/recursos inaccesibles, foco/título, drawer temporal, diálogos y avisos | UI-02/03/04/09; sin bucles ni revelación de recursos ajenos |

Los contenedores seguirán usando [coordinadorService](../../../frontend/src/services/coordinadorService.js), [estudianteService](../../../frontend/src/services/estudianteService.js), [superAdminService](../../../frontend/src/services/superAdminService.js) y [authService](../../../frontend/src/services/authService.js). No se moverán estos servicios a componentes visuales.

### 5.1 Archivos y conocimiento

- Presentar ayuda del Excel según columnas reales documentadas en el baseline/contrato; sin inventar tamaño, nuevas columnas, plantilla de descarga o validación de filas cliente. Resumen conserva contadores/omisiones recibidos y distingue parcial/completo/fallo.
- No modificar el binding o conversión de archivo para arreglar el defecto excluido. Si la presentación común obligara a ello, mantener el control actual y limitar la extracción a ayuda/resumen; registrar el límite antes de ampliar alcance.
- PDF: mostrar máximo 10 por carga y 20 MiB por archivo; pendientes y acciones por trabajo. Traducir queued/processing/completed/failed/unknown, sin barra porcentual ficticia. Los estados desconocidos y pérdida de temporales ofrecen solamente acciones reales.
- Eliminar documento y limpiar conocimiento son confirmaciones diferentes. No invocar proveedores para representar estas pantallas ni trasladar a la UI rutas/logs internos.

### 5.2 Chat, dictado y diagramas

- Identidad de sesión/curso y autor explícitos; modos con propósito/indisponibilidad. Cargar historial no implica crear conversación. Conservar campos y contenido de la respuesta, incluidas fuentes reales e indisponibilidad.
- Scroll: comprobar si el lector está al final antes de agregar contenido; si no, mantener posición y ofrecer Ir al último mensaje. No anunciar todo el historial mediante una región live.
- Enter solo envía cuando no hay IME (`isComposing`/estado de composición), no hay envío/dictado incompatible y se cumplen condiciones actuales del modo; Mayús+Enter permite salto. El botón sigue disponible para otros métodos de entrada.
- Imagen: ayuda PNG/JPEG/WEBP/GIF y 4 MiB, nombre/preview/retirada. No modificar contrato de imagen ni incluir audio. Borrador solo en la conversación actual y memoria de pestaña; permanecer o descartar antes de cambiar contexto.
- Dictado usa soporte del navegador; permiso por acción explícita, indicador/stop/revisión, sin autoenvío. Limpiar callbacks/escucha al abandonar la función o sesión; denegación/ausencia de soporte mantiene texto manual.
- Mermaid: conservar fuente parseada y sanitizar cada SVG. Capturar errores por bloque, cerrar loading y ofrecer fuente como texto, sin bloquear otros mensajes. Serializar renderizados cuando la configuración compartida de Mermaid lo requiera; usar identidad/secuencia para impedir aplicar renders obsoletos al cambiar contenido/tema.
- Mantener diagrama seleccionado y foco al actualizar preview/ampliación; no cerrar el diálogo por cambio de tema. Asociar título/descripción recibidos; fuente técnica disponible no equivale por sí sola a alternativa accesible. Registrar limitación de contenido sin pedir generación adicional.

### 5.3 Agenda y métricas

- Calendario y lista equivalente utilizan exactamente periodo, filtros y actividades recibidas; la lista no se limita silenciosamente a ocho eventos. Todos los detalles disponibles siguen alcanzables en móvil/teclado.
- No añadir edición, navegación a periodos inexistentes ni métricas nuevas. Las barras/indicadores actuales reciben valor/unidad/resumen legible; color solo complementario. Ausencia no se convierte en cero y capacidad ilimitada no se calcula como porcentaje.

## 6. Construcciones y entregables

Cada etapa aplica PUDS y termina con integración del incremento parcial, recorrido de sistema pertinente y decisión de defectos. Las etapas son orden de trabajo, no un recorte del conjunto de requisitos.

| Etapa | Dependencia y alcance | Entregable / condición de salida |
|---|---|---|
| C0 — Preparación | Aprobación del plan; confirmar contratos/columnas, consumidores, navegadores y entorno | Inventario/matriz de casos; baseline build/lint y defectos conocidos registrados; tareas posteriores con IDs SPEC-002, sin alterar evidencias previas |
| C1 — Apariencia | C0; tokens/bootstrap/Vuetify/Tailwind/selector y estilos compartidos | Dos temas completos en estructura, overlays y login; pruebas UI-01/02 y contraste inicial; no pérdida de estado ni HTTP por tema |
| C2 — Patrones e interacción | C1; AppShell/sidebar/perfil, estado/aviso/confirmación, formularios y listas | Consumidores reales migrados; UI-03/04/05 parcial; foco/dirty/401/timeout y retorno con filtros verificados |
| C3 — Administración y coordinación | C2; todas las secciones de superadmin/coordinador, tutor/RAG y analíticas | UI-05/06/08; estados simulados identificados, ayudas Excel sin reparación, todos los formularios/acciones accesibles |
| C4 — Estudiante | C2; conversación/compositor/dictado/agenda/Mermaid | UI-07/08; ambas variantes, errores y alternativas; sin llamadas reales IA para estados controlados |
| C5 — Evaluación integral | C3 y C4 | UI-01 a UI-10, regresión pertinente, matriz de pantallas/navegadores, rendimiento/lectores y checklist por RF/RNF con evidencia/defectos |

Entregables documentales previstos: ampliar el catálogo de uso del frontend en un documento proporcional y crear el registro de pruebas de SPEC-002 con casos/evidencias/checklist. Sus nombres y ubicación exacta se fijarán al desglosar tareas; no construir una nueva web de demostración. Este plan no rellena el archivo de tareas ni implementa componentes.

## 7. Verificación PUDS y recursos

### 7.1 Preparación y modalidades

- **Lectura estática:** contratos, dependencias, paletas duplicadas, sanitización, guards y alcance del diff. No demuestra interacción.
- **Integración frontend controlada:** usar navegador/DevTools y dobles locales temporales documentados para respuestas del servicio, sin añadir un modo mock permanente de producto. Registrar cómo reproducir cada respuesta y confirmar que no salen solicitudes a proveedores.
- **Integración real:** aplicación con backend/SQL local autorizado, entidades ficticias propias y limpieza verificable. No simularla con pruebas de componentes.
- **Sistema:** recorrer la versión integrada como usuario con preparación/esperado/obtenido. Si se sustituye una respuesta, identificar esa parte como controlada, no afirmar certificación externa.
- **Calidad de construcción:** scripts actuales `npm run lint` y `npm run build` desde la carpeta frontend; documentar pasos PowerShell en los procedimientos posteriores. No añadir un script de tests ficticio: actualmente no hay runner frontend declarado.

Antes de C1 registrar Windows/CPU/RAM, resolución/escala, navegador/versión y build de referencia. Rendimiento primario: build de producción servido localmente, pestaña activa, sin throttling, extensiones ni trabajo intensivo de fondo. Los datos y estado inicial serán iguales en cada repetición; registrar cold load aparte. No inventar hardware disponible ni medir un dev server como equivalente sin indicarlo.

### 7.2 Matriz mínima de integración y sistema

| Grupo | Procedimiento a diseñar / ejecutar | Resultado verificable |
|---|---|---|
| UI-01 | Revisar paleta verde/blanca, mapeo actual→token, muestra comparativa login–administración–chat, catálogo/contratos y consumidores; build/lint | Dirección luminosa/inspiradora revisada, Oscuro sin grandes fondos negros, roles semánticos aplicados y sin duplicación por tema ni reglas de negocio en presentación |
| UI-02 | Claro/Oscuro/Sistema; ausencia/corrupción/storage bloqueado; recarga/logout; otra pestaña; sistema; edición/dictado/overlay abiertos | Preferencia correcta antes del contenido, mismo foco/datos/operación, cero nuevas llamadas HTTP por tema |
| UI-03 | Login/guards, navegación por rol, detalle→lista con filtros/página, pestañas, not-found, 401 y 403 | Destino permitido, título/foco/sección correctos, drawer modal accesible y datos privados retirados |
| UI-04 | Formulario/error/primer foco, doble envío, fallo/timeout, dirty stay/discard, diálogos y avisos | Resultado real, contexto conservado cuando procede, foco trap/restore, sin reintento de mutación |
| UI-05 | Cada listado, 0/1/11/26 registros y última fila, filtro vacío/textos largos, Excel nombre/ayuda/retirada y respuestas controladas | Alcance local claro, acceso a todas las filas/acciones, resumen fiel completo/parcial/fallo; no certifica reparación Excel |
| UI-06 | Tutor dirty/pending y PDF cantidad/tamaño; trabajos en cinco estados; documento vs limpieza y temporales ausentes | Límites informados, estados/actions reales, sin porcentajes/secretos/cancelación inventados |
| UI-07 | Contextos vacíos/historial/selección tardía/modos; scroll arriba/final; Enter/IME; imagen/dictado/denegación; Mermaid válido/inválido/grande | Sin envíos por tema/modo, borrador no transferido, texto alternativo, error local y foco accesible |
| UI-08 | Agenda calendario/lista para mismo periodo/filtro; métricas cero/ausentes/ilimitadas, fechas y USD | Misma información disponible, formatos correctos y lectura textual sin hover |
| UI-09 | Contraste real de texto/controles/estados, teclado y lector, viewports/zoom/orientación/teclado virtual/movimiento; rendimiento y ciclos | Medidas y observaciones registradas, controles alcanzables, estabilidad e identificación explícita de límites |
| UI-10 | Revisión del registro individual y regresión seleccionada; datos propios/limpieza | Resultado y evidencia por requisito; pendientes/fallos/decisión sin alterar historia ni aprobar casos no ejecutados |

### 7.3 Pantallas, temas y navegadores

- Cada superficie de §5: presentación y acceso a tarea principal en Claro y Oscuro. Cada patrón compartido: profundidad de estados una vez y comprobación de integración por rol. Caso Sistema se concentra en UI-02, no duplica cada CRUD.
- Matriz visual mínima: 320 × 568, 390 × 844, 768 × 1024 y 1440 × 900 px CSS. Usar Chrome Windows como barrido completo inicial; Edge y Firefox Windows recorren login, navegación/formulario/dialog, estudiante/agenda/diagrama y cambio de tema con overlays en ambas variantes. Registrar versiones estables efectivamente disponibles.
- Chrome Android y Safari iOS reales o entornos que ejecuten esos navegadores: login, drawer, tema, formulario/diálogo con teclado virtual, chat/imagen, agenda/lista y ampliación de diagrama; vertical/horizontal. Dictado progresivo donde exista, y fallback donde no. Viewport emulado en Windows solo prueba distribución, no Safari.
- Zoom de texto 200 % y reflow 400 % sobre 1280 px; no scroll horizontal global. Las regiones bidimensionales tendrán nombre, acceso por teclado y desplazamiento propio.
- Teclado sin ratón y al menos un lector de pantalla: recorrido representativo de todos los patrones interactivos; NVDA con Firefox/Chrome Windows si está disponible. Registrar herramienta/versiones, nombre/rol/estado/anuncios y foco observado; si falta recurso, registrar no ejecutado, no conformidad global.
- Medir contraste en ambos temas con colores computados/composición final; texto ≥ 4,5:1 o ≥ 3:1 grande, indicadores/componentes necesarios ≥ 3:1 conforme a excepciones. Capturas saneadas opcionales complementan, no sustituyen la observación.

### 7.4 Rendimiento y estabilidad

- Seleccionar antes de implementar: cambio de tema con diálogo abierto, abrir/cerrar drawer, abrir confirmación y cambio de pestaña local con datos cargados. Medir desde evento de entrada hasta primer fotograma que muestra el resultado local mediante Performance/filmstrip del navegador; excluir espera HTTP/IA.
- 20 repeticiones por interacción, al menos 19 con resultado visible ≤ 200 ms. Registrar todas las medidas, entorno y estado de caché; no usar una sola impresión subjetiva. Comprobar por Network que alternar tema no agrega solicitudes de API.
- Repetir 20 entradas/salidas de funciones con listeners, temporizadores, dictado y renders pendientes; comprobar un solo callback por acción y disposición al abandonar. Inspeccionar listeners/actividad en DevTools y recuentos controlados, sin telemetría permanente.
- Mermaid sigue bajo demanda; revisión de bundles/imports y observación de carga. No añadir virtualización o bibliotecas por un supuesto volumen: si el baseline impide cumplir una medida, registrar evidencia y aprobar ajuste antes de ampliar.

### 7.5 Regresión, autorización y bloqueos

- Aplicar [REGRESSION](../../../testing/REGRESSION.md) por impacto, con decisión escrita reutilizar/adaptar/añadir/excluir. Preservar IDs y vincular a versión nueva, sin sobrescribir [evidencia histórica](../spec-001-tests/test.md).
- S-1 es pertinente al presentar rechazo de alta; S-2 al tocar la presentación de importación; S-3/S-3b al crear/denegar conversación. No exigir reparación del importador como condición del rediseño. Si un fallo previo bloquea sistema, registrar fallo/bloqueo y su efecto en cobertura; un mock no aprueba el recorrido real.
- Si el cambio reutiliza lógica A-1/A-2/A-3, ejecutar la suite aislada completa de 23 pruebas y señalar los casos pertinentes; no inventar un filtro. Seleccionar I-1 a I-4 según interfaces afectadas y justificar omisiones. Revisión UI no obliga a modificar esos algoritmos.
- Seguir [preparación y ejecución existentes](../../../testing/README.md) y [seguridad del sistema](../../../testing/SYSTEM.md): nueva autorización para cada operación, destino local verificado, journal/propiedad y cleanup de fixtures propios. Una autorización histórica no es reutilizable.
- El soporte previo no prepara/recupera automáticamente mensajes, consumo o datos RAG nuevos. Para esas superficies usar respuestas controladas; si se necesita persistencia real adicional, diseñar y aprobar fixtures/recuperación antes. No limpiar datos por patrones amplios ni usar cuentas reales en evidencia.
- Al terminar cada construcción, comunicar fallos al responsable y registrar prolongación, diferimiento o investigación. Defecto previo fuera de alcance no se repara aquí; regresión causada por este incremento sí requiere tratamiento. Diferir un caso no equivale a aprobarlo.

### 7.6 Registro de resultados

Crear casos con ID `SPEC-002/UI-xx/caso`, RF/RNF asociados, precondiciones, entradas, pasos, esperado, obtenido, modalidad, fecha, commit/cambios locales, rol, tema, viewport/escala, navegador/herramienta, evidencia, defectos y limpieza. Resumir por cada RF/RNF: aprobado/fallido/no ejecutado/no aplicable justificado, con enlaces a casos. No aprobar un requisito completo por verificar solo una parte.

## 8. Matriz de trazabilidad

Todos los IDs de esta sección pertenecen a SPEC-002; tareas, commits y revisión usarán su identificador completo. Los entregables citados son los módulos/contratos de §3–5 y el registro de §7.

### 8.1 Requisitos funcionales

| ID | Pantallas / entregable técnico | Construcción | Verificación |
|---|---|---|---|
| RF-1 | Todas; paleta verde/blanca, mapeo de colores actuales, tokens, tipografía/espaciado/jerarquía y catálogo | C1–C5 | UI-01/09; revisión comparativa de dirección, contraste y consumidores |
| RF-2 | Login/tres encabezados; selector y controlador de apariencia | C1 | UI-02; cambios explícitos/sistema y conservación |
| RF-3 | HTML/arranque/controlador; clave local y fallback/sync | C1 | UI-02; primera carga, storage/recarga/logout/pestañas |
| RF-4 | Todas y overlays/calendario/chat/diagramas; tokens y paletas render | C1/C3/C4 | UI-02/07/08/09; ambas variantes sin inversión |
| RF-5 | AppShell/patrones/perfil/componentes específicos y consumidores | C2–C4 | UI-01; props/emits/slots, no HTTP oculto/duplicación |
| RF-6 | Router/sidebar/pestañas/cursos; foco/título/list state | C2 | UI-03/09; drawer, retorno y guards |
| RF-7 | Todas; AsyncState/avisos/pending e identidad de lecturas | C2–C4 | UI-04/05/06/07/08; estados y respuestas fuera de orden |
| RF-8 | Login/perfiles/administración/tutor; etiquetas/errores/edición | C2/C3 | UI-04/09; primer error y valores tras fallo |
| RF-9 | Diálogos/formularios/conversaciones; ConfirmDialog/dirty guard | C2–C4 | UI-04/07/09; consecuencias/foco/stay-discard |
| RF-10 | Login/router/API/auth y vistas; errores seguros/cleanup | C2–C4 | UI-03/04/07; expiración, 403, not-found, incertidumbre |
| RF-11 | Superadmin/cursos/cuentas/matrículas; listas/página/filtros | C2/C3 | UI-05/09; tamaño/página, estados y overflow interno |
| RF-12 | Excel de cursos/estudiantes; ayuda/selección/resumen visual | C3 | UI-05; resultados controlados, sin reparación previa |
| RF-13 | Detalle de curso; TutorSettingsForm/KnowledgePanel | C3 | UI-06/04; límites/estados/dirty/confirmaciones |
| RF-14 | Asistente/conversaciones; lista/contexto/modos/historial | C4 | UI-07; estados/autores/scroll/indisponibilidad |
| RF-15 | Composición/imagen/dictado; ChatComposer y coordinación | C4 | UI-07/09; IME, permisos, pending y borradores |
| RF-16 | Recursos; MermaidMessage/error/fuente/ampliación | C4 | UI-07/09; sanitización/foco/límite de alternativa |
| RF-17 | Agenda/analíticas/suscripción; lista equivalente y formatos | C3/C4 | UI-08/09; periodo/filtro/unidades/ausente-cero-ilimitado |
| RF-18 | Todas; textos/locale/ayudas y estados compartidos | C1–C4 | UI-04/06/07/08/09; español y alternativas reales |
| RF-19 | Todas; distribución/foco/movimiento/controles | C1–C5 | UI-09; viewports/zoom/teclado virtual/teclado |
| RF-20 | Plan/tareas posteriores/catálogo/registro y revisión | C0–C5 | UI-01/10; cobertura individual, evidencia y decisiones |

### 8.2 Requisitos no funcionales

| ID | Entregable / responsabilidad | Construcción | Verificación |
|---|---|---|---|
| RNF-1 | Stack/librerías existentes, diff/dependencias justificadas | C0–C5 | UI-01; package y alcance, sin nuevo framework |
| RNF-2 | Tokens/controlador únicos, contratos, estilos scoped y capas | C1–C4 | UI-01; consumidores, nombres, ausencia de ciclos/negocio |
| RNF-3 | Contraste, semántica, errores/estado/foco/objetivos táctiles | C1–C5 | UI-04/07/08/09; medición, teclado y lector |
| RNF-4 | Arranque/cambio sin remount/HTTP, lazy loading y cleanup | C1/C4/C5 | UI-02/09; 19 de 20 ≤ 200 ms y 20 ciclos |
| RNF-5 | Matriz de navegadores/dispositivos y fallback dictado | C4/C5 | UI-07/09; versiones reales, ausencias no ejecutadas |
| RNF-6 | Preferencia no sensible, estado privado/sanitización/fixtures | C1–C5 | UI-03/04/06/07/10; sin secretos/drafts persistidos |
| RNF-7 | Servicios/guards/reglas/contratos existentes conservados | C0–C5 | UI-02/03/05/06/07/08/10; diff y regresión pertinente |
| RNF-8 | Procedimientos y registro reproducible por modalidad | C0–C5 | UI-10; versión/entorno/evidencias/limpieza y límites |

## 9. Alineación constitucional y riesgos

| Principio | Aplicación / control |
|---|---|
| I — Stack sencillo | Bibliotecas actuales; sin dependencias/abstracciones preventivas; revisar necesidad antes de aprobar ampliaciones |
| II — Spec y código | Spec aprobada con exclusión Excel; plan aún propuesto; IDs en tareas/commits/revisión y cobertura; aprobar desviaciones antes de implementar |
| III — Separación | Contenedores coordinan servicios; patrones reciben datos/intenciones; backend decide permisos/reglas |
| IV — PUDS | C0–C5 tienen integración/sistema/evaluación; fallos y decisiones registrados, no inferir prueba desde explicación |
| V — Persistencia/contratos | SQL y contratos intactos; única persistencia nueva: apariencia no sensible. Estado UI efímero no sustituye recuperación transaccional del backend ni promete recuperación de borradores |
| VI — Idioma/mensajes | Documentación/textos en español, nuevos identificadores/comentarios en inglés, mensajes seguros sin logs internos |

| Riesgo | Mitigación / decisión requerida |
|---|---|
| Colores fijos y cascade Vuetify/Tailwind | Inventariar consumidor/valor/estado→token, migrar semántica por construcción, mantener preflight desactivado y verificar estilos computados |
| Aclarar tonos reduce contraste o conserva un aspecto casi negro | Separar verdes suaves de superficie y tonos legibles de acción/texto; medir parejas reales y comparar login–administración–chat con baseline, sin aprobar estética desde códigos hexadecimales |
| Flash/URLs del bootstrap en producción | Orden HTML síncrono y hoja temprana, validar build servido con storage y sistema opuestos; bloquear C1 si no cumple |
| Refactorizar dashboards rompe operaciones | Extraer por responsabilidad, preservar servicios/eventos y verificar tras cada consumidor; no mover negocio a AppShell |
| Timeout/stale responses se convierten en falso éxito | Identidad de lectura y resultado no confirmado de mutación; sin retry automático ni falsa cancelación |
| Contenido Mermaid sin descripción | Sanitización/error local y fuente; evaluar alternativa real, registrar limitación, no generar contenido adicional |
| Defecto previo bloquea un recorrido | Registrar bloqueo y cobertura no acreditada; responsable decide seguimiento fuera de este alcance, sin reparar Excel implícitamente |
| Falta navegador/lector/destino autorizado | No ejecutado explícito; obtener recursos o registrar decisión. No sustituir sistema con mock ni escritorio con prueba Safari |

## 10. Revisión previa y criterios de cierre

### 10.1 Antes de implementar

- [ ] Responsable aprueba este plan y la paleta concreta verde/blanca con Claro luminoso/Oscuro suavizado, orden de construcciones y modalidades de verificación.
- [ ] Se confirma exclusión de reparación Excel, conservación de contratos y ausencia de dependencias nuevas previstas.
- [ ] Se fijan entorno de referencia, recursos disponibles y casos detallados; las carencias quedan registradas.
- [ ] Se desglosan tareas vinculadas a todos los RF/RNF y se identifican consumidores/criterios, sin convertir instrucciones en evidencia.

### 10.2 Cierre de construcción y evaluación final

- [ ] Entregables técnicos/catalogados y consumidores incluidos migrados, sin duplicación reemplazada pendiente.
- [ ] Build/lint y pruebas pertinentes registrados con baseline/versiones; revisión de diff confirma límites de producto.
- [ ] Paleta formalizada y colores actuales mapeados a tokens; muestra comparativa de dirección visual revisada. Temas completos, arranque/fallback/sync/cambio en caliente verificados sin pérdidas ni tráfico API adicional, con Claro luminoso y Oscuro verde sin grandes superficies negras/carbón.
- [ ] Recorridos por rol, archivos, tutor, chat, agenda y recursos evaluados; defectos previos separados de regresiones nuevas.
- [ ] Teclado/lector/contraste, dispositivos/zoom/movimiento y rendimiento tienen evidencia o no ejecución explícita.
- [ ] Integración/sistema pertinentes ejecutados con autorización vigente y cleanup demostrado donde haya datos reales.
- [ ] Cada RF/RNF tiene resultado/evidencia/defectos; responsable registra decisiones y limitaciones del veredicto.
- [ ] Revisión constitucional completa; ninguna corrección fuera de alcance ni aprobación retrospectiva de SPEC-001.

Cerrar entregables con fallos diferidos no equivale a cumplimiento íntegro. El veredicto distinguirá presentación verificada, recorridos reales bloqueados y requisitos fallidos/no ejecutados. **En la redacción de este plan no se ha implementado ni probado la aplicación.**

