# Inventario C0 — SPEC-002/T02

**Resultado:** revisión de fuente completada; no es una prueba visual ni de contratos HTTP ejecutados.  
**Fecha de inspección:** 2026-09-30; captura local 20:00:46 −04:00 (2026-10-01 00:00:46 UTC).  
**Commit base:** `6b7b79bbfdbea5614ffe369330e55905fffe3c98`. Frontend/backend sin diff contra HEAD al inspeccionar. Hay cambios documentales y soporte de pruebas locales no versionados; el commit por sí solo no identifica esos documentos.  
**Referencias:** [plan](plan.md), [tareas](tasks.md), [spec](spec.md), [regresión](../../../testing/REGRESSION.md).

## 1. Inventario de superficies

Los códigos Pxx permiten asignar casos sin confundir una pestaña interna con una ruta. Todas las superficies requieren Claro/Oscuro; ninguna está migrada en C0.

| ID | Superficie actual / fuente | Contrato o coordinación existente | Decisión y tareas |
|---|---|---|---|
| P01 | [Login](../../../frontend/src/views/Login.vue) | Credenciales, auth store, mostrar contraseña, hero/SynapseBackdrop | Conservar flujo; adaptar tokens/etiquetas/efectos; T14–T15 |
| P02 | [Shell superadmin](../../../frontend/src/views/SuperAdminDashboard.vue) | RoleSidebar, PanelTitle, secciones por `tab`, avisos locales | Extraer AppShell; T19/T22 |
| P03 | Instituciones en [superadmin](../../../frontend/src/views/SuperAdminDashboard.vue) | Listado, alta, edición y acciones existentes vía superAdminService | Reutilizar patrones, conservar contenedor; T40–T41 |
| P04 | Planes en [superadmin](../../../frontend/src/views/SuperAdminDashboard.vue) | Listado/formularios; `max_cuentas`, `max_almacenamiento_gb` | No redefinir capacidad; T42–T43 |
| P05 | Suscripciones en [superadmin](../../../frontend/src/views/SuperAdminDashboard.vue) | Contexto institucional, fechas/capacidad, operaciones existentes | T44–T45 |
| P06 | Coordinadores en [superadmin](../../../frontend/src/views/SuperAdminDashboard.vue) | Filtro institucional, listado y operaciones existentes | T46–T47 |
| P07 | Perfil en [superadmin](../../../frontend/src/views/SuperAdminDashboard.vue#L392) | ProfileSection, handlers propios con servicio de rol | Mantener consumidor, migrar contrato compartido; T29–T30 |
| P08 | [CoordinadorLayout](../../../frontend/src/views/coordinador/CoordinadorLayout.vue) | Router-view, navegación de 5 destinos, coordinadorToast | Extraer shell sin convertirlo en coordinador de negocio; T21 |
| P09 | [CursosListView](../../../frontend/src/views/coordinador/CursosListView.vue) | Lista/crear/editar, modal Añadir curso–Importar Excel; importCursosExcel | T48–T49/T55; conservar contexto al volver |
| P10 | Resumen en [CursoDetalleView](../../../frontend/src/views/coordinador/CursoDetalleView.vue) | Datos, estado/opciones, curso de route param y retorno | T50; no modificar reglas de curso |
| P11 | Estudiantes/matrículas en [CursoDetalleView](../../../frontend/src/views/coordinador/CursoDetalleView.vue) | Listado/alta manual/retirada e importEstudiantesCursoExcel | T51–T52/T56; cuenta no equivale a matrícula |
| P12 | Tutor en [CursoDetalleView](../../../frontend/src/views/coordinador/CursoDetalleView.vue) | get/updateAgenteCurso; system_prompt, temperatura y opciones actuales | Extraer TutorSettingsForm; T59 |
| P13 | Conocimiento en [CursoDetalleView](../../../frontend/src/views/coordinador/CursoDetalleView.vue) | PDF múltiple, resumen/documentos/trabajos, reintento y operaciones | Extraer KnowledgePanel; T60–T62; dobles para proveedores |
| P14 | [CuentasView](../../../frontend/src/views/coordinador/CuentasView.vue) | Listado/búsqueda local, edición/eliminación; cuenta/matrícula/cursos | T53–T54 |
| P15 | [InstitucionConfigView](../../../frontend/src/views/coordinador/InstitucionConfigView.vue) | Nombre/dominio editables; fecha/estado y suscripción de tokens en lectura | T57; no contiene una sección de analíticas/coordinadores |
| P16 | [AnalyticsGlobalView](../../../frontend/src/views/coordinador/AnalyticsGlobalView.vue) | 7/30/90/personalizado, tipo, KPIs, cursos/selección, enfoques e indicadores | T58; es una pantalla implementada, no un placeholder |
| P17 | [ProfileView](../../../frontend/src/views/coordinador/ProfileView.vue) | ProfileSection y handlers coordinador | T29–T30 |
| P18 | Shell en [EstudianteDashboard](../../../frontend/src/views/EstudianteDashboard.vue#L377) | Destinos explícitos Asistente/Agenda/Perfil | T23; perfil sí es destino visible de navegación |
| P19 | Conversaciones/asistente en [EstudianteDashboard](../../../frontend/src/views/EstudianteDashboard.vue) | Curso/sesión/contexto/mensajes; crear, abrir, renombrar y archivar; modos | T65–T68; separar lista/presentación de handlers |
| P20 | Composición en [EstudianteDashboard](../../../frontend/src/views/EstudianteDashboard.vue) | inputMsg, imageAttachment, sendByMode, reconocimiento del navegador | Extraer ChatComposer; T69–T72; no audio en API |
| P21 | Recursos y [MermaidMessage](../../../frontend/src/components/MermaidMessage.vue) | `content`, bloques Mermaid, SVG sanitizado, diálogo de ampliación | T73–T75; conservar especializado y lazy import |
| P22 | Agenda en [EstudianteDashboard](../../../frontend/src/views/EstudianteDashboard.vue#L736) | Cuadrícula `calendarDays` de 42 días y actividades; filtro curso, mes local | T76–T77; FullCalendar está instalado pero esta cuadrícula no lo usa |
| P23 | Perfil en [EstudianteDashboard](../../../frontend/src/views/EstudianteDashboard.vue#L346) | ProfileSection con handlers estudiante | T29–T30 |
| P24 | [Router](../../../frontend/src/router/index.js), overlays y [API](../../../frontend/src/services/api.js) | Guards de rol/auth, catch-all redirige a login, 401 logout/redirect, timeout 70 s | T20/T25–T28/T32–T36; preservar destinos válidos |

Rutas conservadas: `/login`, `/super-admin`, `/coordinador/cursos`, `/coordinador/cursos/:id`, `/coordinador/cuentas`, `/coordinador/institucion`, `/coordinador/analytics`, `/coordinador/perfil`, `/estudiante`. Raíz y `/coordinador` tienen redirección; no crear una ruta por pestaña por conveniencia de pruebas.

## 2. Contratos compartidos y propiedad de datos

| Componente / fuente | Contrato real leído | Consumidores y decisión |
|---|---|---|
| [RoleSidebar](../../../frontend/src/components/RoleSidebar.vue#L84) | Props `role`, `icon`, `userName`, `items`, `active`, `permanentOnDesktop`; `defineModel` booleano (modelValue/update:modelValue implícitos); emits `select`, `logout`. Item usa `to` o `value`, `label`, `icon` | Los tres shells; reutilizar y mejorar foco/inert. No inventar una prop llamada `open`: es el nombre local del modelo |
| [PanelTitle](../../../frontend/src/components/PanelTitle.vue) | Props `role` obligatorio y `subtitle` opcional; sin eventos | RoleSidebar y app-bars; reutilizar. Hoy usa párrafos, no establece por sí solo un h1 |
| [ProfileSection](../../../frontend/src/components/ProfileSection.vue) | Prop `profile` con first_name/last_name/phone; emits update-profile, update-password, notify. Password emite current_password/new_password | Tres perfiles; reutilizar. El emit no espera resultado y hoy limpia contraseña tras emitir; T29 coordinará confirmación sin nueva regla backend |
| [MermaidMessage](../../../frontend/src/components/MermaidMessage.vue) | Prop `content` String; texto y fences Mermaid, renderSequence, DOMPurify; sin HTTP | Mensajes del tutor en estudiante; conservar especializado y mejorar errores/paleta |
| [SynapseBackdrop](../../../frontend/src/components/SynapseBackdrop.vue) | Props density/minNodes/maxNodes, canvas y efectos locales; sin eventos de negocio | Login **y estado vacío del asistente**; conservar con tokens/reduced-motion, no duplicar efecto |
| [useToast](../../../frontend/src/composables/useToast.js) | createToast → message/isError/notify/notifyError; singleton coordinadorToast | Coordinador y factories en otros paneles; extender mismo patrón, no importar servicios aquí |

Las vistas seguirán coordinando [superAdminService](../../../frontend/src/services/superAdminService.js), [coordinadorService](../../../frontend/src/services/coordinadorService.js), [estudianteService](../../../frontend/src/services/estudianteService.js) y [authService](../../../frontend/src/services/authService.js). Perfil usa GET/PATCH `/auth/profile` y PATCH `/auth/profile/password`. Interceptor retorna `response.data`, no el objeto Axios entero. No definir contratos de dobles con otra envoltura.

Patrones nuevos solo por responsabilidad ya repetida: AppShell, PageHeader si aporta semántica, AsyncState, ConfirmDialog, apariencia, estado de lista y cambios sin guardar. Los formularios de entidad no se convierten en CRUD universal. Autorización/cuotas permanecen en backend; identidades y nombres actuales se conservan.

## 3. Archivos y contratos de importación

Todos los paths de servicio se añaden a la base `/api`. Fuente de envío: [coordinadorService](../../../frontend/src/services/coordinadorService.js); autoridad de lectura/validación: [rutas backend](../../../backend/routes/coordinador.py). C0 solo lee estas fuentes.

| Flujo | Método y request actual | Columnas / respuesta confirmadas por lectura |
|---|---|---|
| Cursos | importCursosExcel; POST `/coordinador/cursos/importar/excel`, FormData campo `file` | Por fila, nombre y codigo requeridos, descripcion opcional. 200 `{message, created, skipped}`; skipped contiene `{row, reason}`, donde row es el objeto de fila, **no número de línea** |
| Estudiantes de curso | importEstudiantesCursoExcel(cursoId,file); POST `/coordinador/cursos/{id}/estudiantes/importar/excel`, FormData `file` | Tras normalizar, email/first_name/last_name requeridos por fila; phone opcional; password necesario para crear cuenta nueva. 200 `{message, created, enrolled, skipped}`; omisión puede ser `{row,reason}` o `{email,reason}` |
| Estudiantes globales con cursos | importAlumnosCursosExcel; POST `/coordinador/estudiantes/importar/excel`, FormData `file` | Mismos datos de estudiante; claves cuyo nombre en minúsculas empieza por `curso` aportan códigos existentes, por ejemplo curso_1/curso_2. No hay obligación de dos columnas ni de exactamente ese sufijo. Retorna message/created/enrolled/skipped |
| Material PDF | uploadMaterialCurso; POST `/coordinador/cursos/{id}/subir-materiales`, campo repetido `files`, timeout 180000 ms | Hasta 10 PDF/20 MiB cada uno. Respuesta actual 200 `{message, trabajo}`; no asumir `{jobId,status}` ni 202 |
| Reintento / conocimiento | GET `/coordinador/cursos/{id}/conocimiento`; POST `.../conocimiento/trabajos/{jobId}/reintentar` y `.../conocimiento/operaciones` | Reintento retorna `{message, trabajo}`. Operaciones action=`delete_document`, archivo; o action=`clear_course`; esta última devuelve message/trabajos_eliminados |
| Imagen de chat | sendMensaje y modos mediante estudianteService; JSON, no multipart | Consulta envía `{contenido,image}`; otros modos conservan su payload existente. Imagen `{data_url,mime_type,name}`; no audio. **UI actual restringe PNG/JPEG hasta 4 MiB**; RF-15/T70 pide también WEBP/GIF, diferencia pendiente de implementación |

### Columnas y límites que la ayuda debe respetar

- [Normalización real](../../../backend/routes/coordinador.py#L61-L122): trim/minúsculas, vocales acentuadas, guiones y espacios a guion bajo. Cursos: nombre/name/curso; codigo/code/código; descripcion/description/descripción.
- Estudiante: email/correo/correo_electronico/mail; first_name/nombre/nombres/name; last_name/apellido/apellidos/surname; phone/telefono/celular/movil/phone_number; password/contrasena/contraseña/clave. Si faltan nombres separados, acepta full_name/nombre_completo/student_name y divide el último término como apellido. No agregar aliases no implementados.
- [Creación/reutilización](../../../backend/routes/coordinador.py#L133-L173): password pasa validate_password **para cuenta nueva**, no se exige de nuevo al reutilizar estudiante propio. Email, rol, institución y capacidad son decisiones backend. No describir password como opcional sin esta condición.
- [Parser](../../../backend/routes/coordinador.py#L198-L213): openpyxl.load_workbook, hoja activa, primera fila cabeceras, data_only. La UI ofrece `.xlsx,.xls`, pero el lector no da soporte al formato binario `.xls`. Ayuda propuesta debe indicar `.xlsx` como formato compatible y registrar esta discrepancia, sin prometer reparación del importador ni cambiar el binding excluido.
- [Importación de curso](../../../backend/routes/coordinador.py#L675-L738) y [global](../../../backend/routes/coordinador.py#L740-L836) no son idénticas al reactivar matrículas: conservar comportamiento, no uniformarlo desde UI.
- Excel: 400 si archivo ausente/ilegible; contexto/permisos pueden dar 403/404. Un 200 con omisiones es parcial, no éxito completo. No inventar límite Excel no definido. **No volcar `skipped.row` crudo en UI/evidencias:** puede contener password de la fila; proyectar datos seguros y motivo público.
- [Límites PDF](../../../backend/services/rag_ingestion.py#L18-L19) y [rutas RAG](../../../backend/routes/coordinador.py#L958-L1033): los mensajes/trabajos reales se presentan, no porcentajes ficticios. No ejecutar upload/retry/delete/clear en preparación visual.
- El método global importAlumnosCursosExcel existe en el servicio pero la búsqueda de consumidores no encuentra una invocación de vista. **No añadir otra pantalla** solo para exponerlo; documentado como contrato existente, no tarea nueva.
- Abrir detalle llama GET del agente y puede crear configuración por defecto ([fuente](../../../backend/routes/coordinador.py#L893-L909)); los fixtures reales requieren reserva de configuración previa, aunque la navegación parezca solo lectura.

## 4. Inventario cromático y mapeo

### Método y alcance

Lectura de todos los `.vue`, `.js`, `.css` bajo frontend/src más configuración Tailwind e HTML inicial: **30 archivos**, **562 coincidencias léxicas** de hex/rgb/rgba/hsl (incluyen referencias a variables; no son 562 colores únicos). Hash SHA-256 del corpus normalizado por rutas `/`, contenido UTF-8 y separador NUL: `299de1840d965cd7c6bb89d3c482fae9fd07dbf88b78008a23f2c9f98087b4dd` (orden de rutas del recorrido Windows usado en la captura). Revisión adicional de clases/props de color y selectores: la búsqueda de literales sola no identifica herencia, transparencia ni función.

Los mapeos siguientes son por **función de la ocurrencia**, no reemplazo global por hexadecimal. Todas las familias inventariadas tienen destino o excepción técnica; el RGBA y su opacidad dejan de ser una paleta adicional. T06 materializa tokens; T12 y tareas de vista migran consumidores, no C0.

### Colores centrales actuales → rol objetivo

| Fuente / valores actuales | Función / estado actual | Destino y restricción |
|---|---|---|
| [HTML](../../../frontend/index.html#L8) `#0a0a0c`; [Vuetify](../../../frontend/src/plugins/vuetify.js#L8) y [CSS](../../../frontend/src/style.css#L9) `#17181c` | Color del navegador/fondo base dark | `background`; theme-color coherente con variante resuelta, no negro fijo |
| Vuetify/Tailwind `#1e1f25` | Surface/card/dialog normal | `surface` |
| `#26272e`, `#2f3038`; gray-soft, surface-2/3, theme-code | Superficie secundaria, código, variante | `surfaceRaised`/`surface` según jerarquía, código con `textPrimary`; no inventar surfaceLowest/tertiary |
| `#7cc576`, `#5fa85f`, `#9fd99f` | Primary, hover, light; mismo verde también success/decoración | `primary`, `primaryHover`, `success`; selección: `primarySoft` + `onPrimarySoft`; decoración derivada de marca en §4.3 |
| `#f3f4f6`, `#ffffff`, `#f5f6f7`, `#dfe0e4` | Texto claro dark, títulos/íconos; blanco también surface Mermaid/on-error | `textPrimary` cuando texto general; `onPrimary` sobre acción; `surface` si fondo. Parejas on-error/on-info/etc. se derivan y verifican en catálogo, no asumir blanco universal |
| `#a3a5ad`, `#9a9ba3`, `#a9abb4`, `#c5c7cd`, `#82838d` | Ayuda/placeholder/label/grises texto | `textSecondary`; no opacidad heredada que reduzca contraste |
| gray-50…400 `#202126`, `#26272e`, `#2f3038`, `#3d3e47`, `#5c5e68` | Escala Tailwind invertida para dark; fondo/borde, depende de utilidad | bg→surface/surfaceRaised; border→borderDecorative o borderControl si necesario; text→textSecondary. Resolver por consumidor, no conservar escala arbitraria |
| `rgba(255,255,255,0.06/0.08/0.09/0.1/0.2)` y similares | Separación, outline normal/hover y glass | Borde decorativo→`borderDecorative`; outline/control necesario→`borderControl`; foco→`focus`; glass/fondo→`surface` con composición medida |
| `#0a0a0c`, text-black | Texto sobre verde/secondary/info/success/warning | `onPrimary` en acción; pareja on-state calculada de roles de texto; no usar oscuro fijo sobre cualquier relleno |
| Red `#2a1414/#3a1a1a/#4a2222/#f47272/#fb9c9c`; otras vistas `#ffa8a8` | Error, eliminar, descenso de KPI | `error` para texto/icono; fondo tonal derivado de error+surface, con pareja comprobada, no extraer un color primario nuevo |
| Green `#153a20/#86e08c` | Estado éxito/activo | `success` y tonal derivado de surface; no marca indiscriminada |
| Amber `#2a2210/#3a2e14/#f0b94d/#f7ca72` | Advertencia/estado | `warning` y tonal derivado; sin porcentaje ficticio |
| Blue `#12202e/#6fb2f2` | Información | `info` y tonal derivado |
| Sombras negras RGB(0,0,0) con alpha y colores de glow | Profundidad/decoración, no contenido | Variables de sombra por tema del catálogo; suavizar/eliminar glow innecesario. Negro se permite como sombra/scrim acotado, no gran superficie estructural |
| transparent/currentColor, rgb/rgba(var(--v-theme-…)) | Herencia/transparencia/roles ya existentes | Conservar semántica sin hex nuevo, verificar la variable consumida y composición; no son evidencia de contraste por sí solos |

### Familias por consumidor y función

**Regla común G:** todas las variantes RGB `(124,197,118)` con alpha, y verdes próximos listados abajo, se asignan por selector: color de acción→primary; hover→primaryHover; foco→focus; selección/fondo de control→primarySoft; texto sobre selección→onPrimarySoft; éxito→success. Bordes separadores→borderDecorative, bordes necesarios→borderControl; sombras/partículas/radiales→decoración derivada de primary con opacidad central del catálogo. No conservar alphas dispersos ni generar un token por cada alpha. Los derivados son configuración central revisable en T06, no valores aprobados inventados en C0.

**Regla común N:** neutrales opacos/degradados oscuros de fondo→background, tarjetas/formulario/toolbar→surface y elevación/hover→surfaceRaised. Blancos/grises verdosos de texto→textPrimary/textSecondary según jerarquía; borde→borderDecorative/borderControl; blanco sobre acción→onPrimary. Un mismo blanco de fondo **no** se mapea a texto. Las tablas indican archivos y rangos para resolver cada ocurrencia en su contexto.

| Fuente / bloques | Colores/familias leídos además de G | Estado / mapeo por función |
|---|---|---|
| [RoleSidebar](../../../frontend/src/components/RoleSidebar.vue#L115-L154) | RGB(36,37,43)/(45,47,55) alpha .98; (7,10,12) .3; `#abeca3`; (235,243,235) .65 | Fondo drawer→surface/surfaceRaised (N); backdrop→scrim acotado; símbolo/hover/activo G; cierre→textSecondary. No mantener fondo carbón |
| [PanelTitle](../../../frontend/src/components/PanelTitle.vue#L16-L26) | `#f4f8f4`, `#9be692` | Título→textPrimary; span de marca→primary; ambos legibles en Claro |
| [SynapseBackdrop](../../../frontend/src/components/SynapseBackdrop.vue#L106-L164) | RGB(124,197,118), (164,233,149), (182,242,170); alpha variable | Partículas/enlaces/glow→decoración G calculada desde tokens; desactivar con reduced-motion, no invocar generación |
| [Login](../../../frontend/src/views/Login.vue#L351-L512) | Bases `#101216/#111419/#171b20/#121518`; RGB(42,48,52)/(24,29,32), scrim (9,11,13)/(7,10,11); blancos `#f4f8f4/#f7faf7/#ecf7eb/#f4f8f3`; texto `#10200f` | Background/surface/scrim N; texto general→textPrimary, ayuda rgba claros→textSecondary, texto botón→onPrimary |
| Login, mismos bloques | Verdes `#b6f2aa/#9be692/#92e487/#9ce294/#a7e6a0/#a3e69b/#a7ed9f/#a6e99d/#9ce493/#72c96c/#a4e995`; RGB(69,148,113)/(75,168,126)/(146,228,135)/(155,226,153)/(164,233,149)/(171,238,163)/(191,236,185)/(205,237,199) y próximos de label | Regla G para hero, botón/hover/focus, badges/ornamentos; tonos claros de label RGB(22x–24x,23x–24x,22x–23x)→textSecondary (N); rojo (244,114,114)→error |
| [SuperAdminDashboard](../../../frontend/src/views/SuperAdminDashboard.vue#L830-L995) | Bases `#252830/#2d313a/#383c46/#383d46/#454b56`; RGB(48,52,61)/(58,63,73)/(47,52,61)/(57,62,72)/(46,51,60); `#f0f5ef/#fff/#132313` | Shell→background, app-bar/dialog/card→surface/surfaceRaised; texto N. Tablas e inputs no quedan con fondo hardcoded |
| Superadmin, mismos bloques | `#abeca3/#9be692/#b0eaa9/#8ee486/#a6e99e/#7cc576/#609f5b`; RGB(150,227,144)/(142,228,134), rgba(229,238,229) | G para acción/hover/selección/decoración; ayuda→textSecondary; white sobre botón→onPrimary |
| [CoordinadorLayout](../../../frontend/src/views/coordinador/CoordinadorLayout.vue#L78-L101) | `#1c1d22/#22242a/#2b2d34`; RGB(40,42,49); `#0f0f11` | Fondo→background, barra→surface, on-button→onPrimary; radiales/bordes G |
| [CursosListView](../../../frontend/src/views/coordinador/CursosListView.vue#L313-L411) | `#242429/#2c2d33/#25262b/#25262c/#2f3037`; `#8fd189/#7cc576/#609f5b/#ffffff` | Hero/card/dialog N; overline/acción/hover G; blanco sobre botón→onPrimary; active-row→primarySoft, no nueva paleta por lista |
| [CursoDetalleView](../../../frontend/src/views/coordinador/CursoDetalleView.vue#L739-L847) | `#25262b/#2e3037/#26272d/#31323a/#2f3038`; `#ffffff/#7cc576/#609f5b`; RGB(244,248,244) .72 | Hero, tabs, cards, inputs/documentos N/G; metadatos→textSecondary; selección de tabs→primarySoft/onPrimarySoft; error/RAG respeta estado funcional |
| [CuentasView](../../../frontend/src/views/coordinador/CuentasView.vue#L225-L288), [InstitucionConfigView](../../../frontend/src/views/coordinador/InstitucionConfigView.vue#L173-L208), [ProfileView](../../../frontend/src/views/coordinador/ProfileView.vue#L100-L134) | `#8fd189/#25262b/#2f3038/#26272d/#31323a/#ffffff/#7cc576/#609f5b`; institución RGB(235,242,235) .74 | Misma familia repetida hero/card/dialog/botón G/N, ayuda→textSecondary. Reutilizar composición, retirar duplicación al migrar |
| [AnalyticsGlobalView](../../../frontend/src/views/coordinador/AnalyticsGlobalView.vue#L307-L438) | `#7cc576/#a3e99c/#343941/#454a55/#ffa8a8`; RGB(47,50,58)/(37,40,47)/(18,21,26); rgba claros (233–238,242–245,233–238) | Filtros/KPI/curso N; barra/icono/selección G; ayuda→textSecondary, delta negativa→error. No crear biblioteca de gráficos |
| [EstudianteDashboard](../../../frontend/src/views/EstudianteDashboard.vue#L833-L1644) | Bases `#111419/#171b20/#121518/#0a0a0c`; RGB(26,30,35)/(19,23,27)/(42,48,52)/(24,29,32)/(49,54,62)/(31,35,42)/(42,46,53)/(52,57,65)/(43,48,56)/(17,21,25); rgba(9,11,13) | Shell→background; sidebar/panel/mensajes/compositor/perfil/calendario→surface/surfaceRaised; scrim/sombras no se convierten en grandes fondos negros |
| Estudiante, mismos bloques | `#b6f2aa/#7cc576/#9be692/#5f9d5a/#8bd584/#6bb566/#5d9e58`; `#fff/#10200f`; RGB(69,148,113)/(155,226,153)/(171,238,163)/(155,230,146)/(184,237,177); claros RGB(205,237,199)/(235,242,235)/(234,241,234)/(230,239,230)/(154,155,163) | G para modo/selección/acción/decoración; texto N y onPrimary. Calendar-event examen/tarea/proyecto/default usa pesos/opacidades de verde: trasladar a roles coherentes más etiqueta de tipo, no a color como única información |
| [CSS global](../../../frontend/src/style.css) | Literales centrales + white alphas, `invert(1)` del control date, overrides `!important` en iconos/texto/outline | Deshacer overrides oscuros sustituidos por roles; color-scheme por tema, sin filtro global de imágenes; date-icon depende de variante, no inversión perpetua |

### Mermaid: todas las familias especiales de render

Fuente: [configuración/SVG](../../../frontend/src/components/MermaidMessage.vue#L80-L143) y [estilos de preview/diálogo](../../../frontend/src/components/MermaidMessage.vue#L177-L305). Es superficie clara fija hoy, no un tema correcto ya implementado.

| Actual | Función | Destino |
|---|---|---|
| `#ffffff/#fff`, rgba(255,255,255,.94) | SVG/preview/dialogo/fondo | surface/surfaceRaised según región, sin blanco rígido en Oscuro |
| `#172033`, `#53657d` | Texto/node labels, conectores | textPrimary/textSecondary; línea necesaria cumple 3:1 |
| `#e8f0ff/#f7faff/#eef7f2/#fff5df` | Nodos/clusters/filas y familias de Mermaid | surfaceRaised/primarySoft; distinción secundaria info/success/warning solo si aporta semántica, derivada centralmente y contrastada |
| `#315da8/#3f8a65/#b47516/#b7c9e7` | Bordes y líneas | borderControl para delimitación necesaria; primary/info/success/warning solo por significado del diagrama. No conservar otra marca azul fija |
| `#296a27/#6fbe67`; RGB(95,168,88)/(185,235,179)/(74,133,68)/(111,190,103) | Controles ampliar/hover/borde y sombra | primary/primaryHover/onPrimary, borderControl, decoración/sombra G |
| RGB(19,43,79) alphas .08/.16 y variables Vuetify primary/error | Sombra/borde y error local | Sombras del catálogo y error; conservar variables semánticas correctas, no ejecutar contenido externo |

### Clases/props sin literales y excepciones

- `color="primary/success/error/warning/info/surface"`, text-primary/text-error, clases gray/red/green/amber/blue de Tailwind: misma decisión central anterior; `grey`, `default`, `text-medium-emphasis` son dependencia de biblioteca a revisar en inactive/disabled, no colores aprobados por omisión.
- `bg-white/...`, `border-white/...`, `text-black` en utilidades: mapear según N; composición tonal se calcula con tema. La opacidad no sustituye un rol de contraste.
- Fotografías, imagen adjunta y documentos: excepción explícita **conservar contenido**, no inventariar píxeles de usuarios ni invertir imágenes. Logos propios usan variante legible si se requiere; SVG/canvas decorativos propios sí están en alcance.
- `none`/`transparent`/`currentColor` son excepciones técnicas válidas si no eliminan una señal necesaria. Sombras/scrim pueden usar oscuro con opacidad como función de capa; no excepción para retornar a paneles casi negros.
- La decisión de token está cerrada a nivel de función; el valor final/composición/contraste de cada consumidor se valida al implementarlo. No afirmar cobertura exhaustiva de CSS generado de dependencias ni conformidad visual de una búsqueda textual.

## 5. Cierre de T02

Fuentes directas confirmaron superficies, consumidores, columnas/requests/responses y los grupos de color anteriores. El mapeo identifica la función y destino de cada familia inventariada; no crea tokens/código ni modifica el enlace Excel. Los hallazgos de baseline se registran en el registro central; las limitaciones de lectura no se convierten en fallos visuales observados. **T02 completada como inventario documental.**