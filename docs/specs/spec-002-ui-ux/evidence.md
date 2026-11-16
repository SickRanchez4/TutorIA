# Evidencia de SPEC-002

Resumen único de la preparación C0, referido por [test.md](test.md) y [tasks.md](tasks.md). Los archivos separados de entorno, baseline, validación y salidas de lint/build se consolidaron aquí el 2026-10-31. Commit de referencia: `6b7b79bbfdbea5614ffe369330e55905fffe3c98`, sin cambios de producto. C0 no implementa ni verifica interfaz: los 28 requisitos de UI siguen **no ejecutados**.

**Lectura al 2026-11-14:** lo anterior identifica C0, no todo el estado actual. La sección final registra el refactor posterior previo a C1, incorporado en `35c6f3d` el 2026-11-05. Sus comprobaciones controladas no cierran los requisitos integrales; la referencia general está en [contexto del proyecto](../../project-context.md). No se repitieron pruebas para esta actualización documental.

**Estado vigente al 2026-11-15:** [cierre funcional acotado](#cierre-funcional-acotado-de-spec-002-2026-11-15). Las secciones anteriores a ese cierre son historia, no la paleta/estado actual ni una certificación integral.

## Entorno (T03, 2026-09-30)

Inspección local sin arrancar navegador, app, SQL ni proveedores.

| Recurso | Observado | Límite |
|---|---|---|
| OS / PowerShell | Windows 11 Home 10.0.26200; PowerShell 5.1 | No prueba compatibilidad de la app |
| Hardware | Core i9-12900H, 20 procesadores lógicos, 31,69 GiB RAM, pantalla reportada 1920×1080 | Equipo de referencia, no mínimos del producto |
| Chrome / Edge | 154.0.8037.58 / 154.0.4258.37 detectados | Canal y versión por verificar al medir |
| Firefox, NVDA, Android/iOS | No detectados o no confirmados | Pendientes de recurso antes de sus casos |
| Escala Windows / DPR | Sin valor utilizable | Registrar antes de medir |
| Node / npm | v22.17.0 / 10.9.2 | Sin instalar ni actualizar paquetes |

Dependencias instaladas relevantes: vue 3.5.42, vuetify 4.1.12, vite 8.2.2, eslint 10.9.1, tailwindcss 3.4.19, pinia 2.3.1, vue-router 4.6.4, mermaid 11.17.2, dompurify 3.4.14, axios 1.20.0, FullCalendar 6.1.21 (instalada; la agenda actual es una cuadrícula propia). Una dependencia instalada no prueba que se use en pantalla.

Entorno de medición para C1/C5: Chrome verificado, build de producción solo en loopback, viewport 1440×900 CSS, zoom 100 %, sin throttling ni extensiones, 20 repeticiones por interacción con 19/20 ≤200 ms al primer fotograma. Mediciones y canal de navegador aún no verificados.

## Baseline de construcción (T05, 2026-09-30)

Ejecución real desde `frontend`, sin autofix ni cambios de dependencias.

| Operación | Resultado |
|---|---|
| `npm run lint` | **Fallido**, código 1: 1 error, 0 avisos |
| `npm run build` | Satisfactorio, código 0: 2500 módulos; chunk 662,12 kB (gzip 143,15 kB) sobre el umbral de 500 kB; diagnóstico de tiempos de plugins (14 % de 16,4 s) |

Salida completa del lint:

```text
C:\...\frontend\src\views\coordinador\CoordinadorLayout.vue
  68:7  error  'currentLabel' is assigned a value but never used  no-unused-vars

✖ 1 problem (1 error, 0 warnings)
```

| ID | Hallazgo | Tratamiento |
|---|---|---|
| C0-B01 | `currentLabel` sin usar en [CoordinadorLayout.vue](../../../frontend/src/views/coordinador/CoordinadorLayout.vue#L68) | Previo; sin autofix. Corregir al migrar el shell o registrar decisión explícita del responsable |
| C0-B02 | Aviso de tamaño de chunk | Previo, no es error de compilación; medir en T92 antes de dividir código |
| C0-B03 | Diagnóstico de tiempo de plugins | Información de herramienta, no defecto |

Compilar no acredita arranque, contraste, interacción ni rendimiento. Integridad posterior: diff de frontend, backend, database, automation, docker y compose vacío; `frontend/dist` ignorado por Git; corpus frontend de 30 archivos con SHA-256 `299de1840d965cd7c6bb89d3c482fae9fd07dbf88b78008a23f2c9f98087b4dd`. Huellas de archivos: `package.json` `3d138abb1767450fae6e04af0755cf2a722ad733fb7e52ab752abb634b896b4b`; `eslint.config.js` `5310a3ac676bcbdc524d25f4e1ea30da84463fca599334d1d552e8ab2e37ccb4`; `vite.config.js` `f6d2535444e8adf720b0a3b58d9d18ad7cdf0a3cef6f7700f9a9c462e7391436`; `CoordinadorLayout.vue` `1daf2584b72bd31c22631a6eb8d31d824aa747c44740490db195838553b73c0e`. Sin fixtures, SQL, HTTP ni proveedores: no hay datos que limpiar.

## Validación documental de C0

Comprobación automatizada con Node: 8 archivos Markdown, 179 enlaces válidos, 98 tareas, T01–T05 marcadas, 28 requisitos (20 RF y 8 RNF) en «No ejecutado», 48 casos únicos y salida de build idéntica a la captura. Sin errores y sin diff de producto. Esto no sustituye a ESLint, que sí falló.

**Veredicto C0:** inventario (T02), recursos (T03), diseño de casos (T04) y baseline (T05) completados. Sin interfaz implementada ni casos funcionales ejecutados. La corrección del lint previo y la autorización de C1 siguen pendientes del responsable.

## Refactorización y corrección de defectos previa a C1 (2026-10-31)

**Autorización:** el responsable pidió refactorizar el frontend sin sobreingeniería y corregir lo que estuviera mal (incluidos fondos cortados en el panel del estudiante), y autorizó explícitamente corregir S-001 (importación Excel). No es la implementación de C1–C5: la paleta verde/blanca, el tema claro y los tokens de T06 siguen pendientes. Solo frontend; sin cambios de backend, SQL, contratos ni dependencias.

| Defecto encontrado | Causa | Corrección |
|---|---|---|
| Fondo cortado horizontalmente al desplazar (estudiante) | `v-app` fijo en `100vh` con su propio fondo; el contenido más alto mostraba el fondo distinto de `body` | Capa fija compartida `AppBackdrop`; `v-app` transparente; modo chat con altura de viewport en `RoleLayout` |
| Fondo cortado verticalmente (~900 px) en todas las pantallas | SVG de ruido sin tamaño intrínseco: se pintaba un único cuadrado | Ruido en mosaico con `background-size` explícito |
| Tipografía y márgenes inconsistentes | Vuetify 4 renombró las clases MD2 (`text-h5`, `text-caption`…) y retiró su reset global | Codemod a clases MD3 según la guía oficial y reset mínimo recomendado |
| Diseño roto entre 840–960 px y 1145–1280 px | Media queries con breakpoints de Vuetify 3 | Alineadas a 600/840/1145 |
| Diagramas Mermaid sin etiquetas; spinner infinito ante error | DOMPurify elimina `foreignObject`; sin manejo de errores | `htmlLabels: false` y estado de error con la definición |
| Iconos `color="primary"` y textos de diálogos forzados a blanco | Reglas globales `!important` en `style.css` | Eliminadas junto con clases muertas |
| Listas con fondo oscuro propio dentro de tarjetas; scroll horizontal en conversaciones | Fondo por defecto de `VList`; `translateX` en hover | Default `bgColor: transparent`; `overflow-x: hidden` |
| S-001: la importación Excel nunca se enviaba | `v-file-input` simple entrega `File` y se leía `[0]` | Helper `firstFile` en cursos y alumnos |
| Detalle de curso fallaba si la carga del curso fallaba | Plantilla accedía a `curso.nombre` con `null` | Estado de error con reintento y retorno |
| C0-B01 | `currentLabel` sin usar | El shell muestra la sección actual en la barra superior |

Reorganización: `RoleLayout` (shell común de los tres roles), `PageHeader`, `StatCard`, `ProfileSection` autónomo sobre `authService`, `utils/format.js`, `createToast` reactivo, y el panel del estudiante dividido en `estudiante/EstudianteChat.vue` y `estudiante/EstudianteAgenda.vue`. Las referencias por línea del [inventario](inventory.md) son anteriores a esta reorganización.

**Verificación:** `npm run lint` código 0 sin avisos; `npm run build` código 0 con el mismo aviso previo C0-B02 (chunk 662,12 kB de Mermaid). Revisión visual en Edge headless a 390×844, 1024×768, 1280×720, 1440×900 y 1920×700 de los tres roles y el login con **API simulada local** (sin backend, SQL ni IA): fondo continuo al desplazar, sin desbordamiento horizontal, sin errores de consola salvo 404 esperados. Con la API simulada, ambos diálogos de importación envían `POST multipart/form-data`. Esto **no** acredita S-2 en sistema real ni ejecuta casos UI-xx; los 28 requisitos siguen no ejecutados.

## Ajustes focalizados de administración (2026-11-15)

**Alcance autorizado:** reemplazar los paneles laterales de alta de instituciones y asignación de suscripciones por botones que abren diálogos; buscar instituciones por nombre en las tres pestañas; ordenar ascendentemente el selector de Coordinadores. No se cambian backend, esquema, contratos, dependencias ni las pantallas de otros roles.

Implementación en [SuperAdminDashboard.vue](../../../frontend/src/views/SuperAdminDashboard.vue): se reutiliza `v-dialog` con el fondo semitransparente existente y los listados pasan a ocupar el ancho disponible. Los filtros locales ignoran mayúsculas, tildes y espacios exteriores; incluyen limpieza y estado sin coincidencias. El selector usa orden español ascendente sin mutar el arreglo original; filtrar opciones no cambia la institución seleccionada ni su etiqueta. Los formularios conservan sus campos, validación y mensajes; muestran carga y bloquean envíos repetidos mientras guardan, y solo se vacían/cierran tras éxito.

**Verificación realizada con API simulada local**, sin conectar ni escribir en PostgreSQL:

| Comprobación | Resultado observado |
|---|---|
| Instituciones: buscar `PORTICO` con espacios y sin tilde | Solo Academia del Pórtico; búsqueda inexistente muestra mensaje y limpiar restaura el listado |
| Nueva institución | Diálogo accesible por nombre; error HTTP 400 controlado conserva formulario; éxito HTTP 201 cierra, limpia y actualiza el listado |
| Coordinadores: orden del selector | Academia del Pórtico, Ágora de Atenas, Liceo de Estagira, Universidad Zenón |
| Coordinadores: filtrar instituciones | Filtra por nombre, informa ausencia de coincidencias y conserva la selección y su nombre aunque no coincida con el filtro |
| Suscripciones: búsqueda por institución | Filtra sin distinguir tildes/mayúsculas, informa ausencia de resultados y el botón de limpiar restaura el listado |
| Asignar suscripción | Error HTTP 409 controlado conserva formulario; éxito HTTP 201 cierra y actualiza la lista; opacidad final del fondo 0,32 |
| Adaptación de los diálogos | Comprobados a 1440×1000 y 390×844; tarjetas móviles de unos 342 px dentro del viewport de 390 px, sin desbordamiento horizontal |

ESLint sobre la vista modificada y `npm run build`: código 0. Persiste el aviso previo por chunk mayor de 500 kB. No se añaden suites ni se declaran completos C1–C5 o los 28 requisitos; tampoco se acredita integración HTTP/SQL real ni S-2. Los servidores auxiliares de comprobación se detienen al finalizar.

## Ajustes focalizados de coordinación (2026-11-15)

**Alcance autorizado:** búsqueda de cursos, estados deshabilitados, matrícula visual de cuentas, navegación y resumen institucional, edición explícita de datos institucionales y cierre del detalle de curso en analíticas. No cambia permisos ni elimina matrículas al inhabilitar cuentas.

- [Cursos](../../../frontend/src/views/coordinador/CursosListView.vue): filtro local por nombre que reutiliza la normalización de búsquedas de administración, sin distinguir tildes, mayúsculas ni espacios exteriores. Muestra coincidencias/total, limpieza y ausencia de resultados. Los cursos inhabilitados tienen distintivo de alumnos gris y botón Ajustes gris, deshabilitado y sin destino.
- [Cuentas](../../../frontend/src/views/coordinador/CuentasView.vue): la matrícula solo se muestra activa cuando la cuenta está habilitada y existe inscripción activa.
- [Institución](../../../frontend/src/views/coordinador/InstitucionConfigView.vue): datos semánticos de solo lectura, sin inputs ni cursor de edición hasta pulsar Editar; cancelar restaura valores y guardar mantiene el flujo existente. Dos `StatCard` muestran todos los cursos y las cuentas institucionales, incluidos alumnos y coordinadores, sin excluir inhabilitados.
- [Navegación](../../../frontend/src/views/coordinador/CoordinadorLayout.vue): Institución, Cursos, Cuentas, Analíticas y Perfil. Se conserva la ruta de entrada existente.
- [Analíticas](../../../frontend/src/views/coordinador/AnalyticsGlobalView.vue): botón accesible «Cerrar detalle del curso» limpia la selección y mantiene disponible «Ver curso».
- [API institucional](../../../backend/routes/coordinador.py): `GET /api/coordinador/institucion/config` conserva institución/suscripción y añade `resumen.total_cursos` y `resumen.total_cuentas`, filtrados por la institución del coordinador autenticado.

**Verificación:** ESLint focalizado y build de producción satisfactorios; continúa únicamente el aviso previo de chunk mayor de 500 kB. Navegador con build y API simulada local a 1440×1000 y 390×844: búsqueda con/sin resultados y limpieza; colores y bloqueo de ajustes; habilitar/inhabilitar curso conservando filtro; cuenta inscrita que se inhabilita/reactiva y coincide con el diálogo; cuenta habilitada sin matrícula; orden del menú; tarjetas y edición/cancelación/guardado institucional; enlace y cierre del detalle analítico. Tarjetas apiladas en móvil y vistas de institución, cursos y analíticas sin desbordamiento horizontal; cierre analítico visible y operable en móvil.

Con Flask y PostgreSQL reales se verificó la lectura del resumen con dos coordinadores de instituciones distintas: C-137, 15 cursos/93 cuentas; Pórtico, 5 cursos/43 cuentas. Los valores coinciden con consultas institucionales independientes. Ninguna edición de esta comprobación se envió a la base real; las mutaciones visuales usaron exclusivamente la API simulada. Sin llamadas a proveedores, nuevas suites ni certificación integral de C1–C5/S-2.

### Refinamiento visual y período inicial (2026-11-15)

- Las tarjetas de cursos/cuentas usan las mismas columnas `md=7/5` que datos institucionales/suscripción; por debajo de ese breakpoint ambas filas ocupan todo el ancho. Mediciones en navegador a 1440, 1024, 840, 839, 768, 600 y 390 px: bordes izquierdos y anchos correspondientes con diferencias inferiores a 1 px, sin desbordamiento horizontal. Se esperó a que terminara la transición de navegación al cruzar breakpoints.
- Analíticas inicia en 7 días: botón seleccionado, etiqueta «Últimos 7 días» y primera petición `GET /api/coordinador/analiticas/consumo?days=7` verificados. Cambiar a 30 días funciona; recargar restaura el valor inicial de 7.
- Paleta compartida en verdes bosque y salvia, con lima como primario y menta como secundario, sin fondos blancos dominantes. Tokens CSS y tema Vuetify actualizados junto con fondo fijo, barra superior, navegación y panel de acceso. Revisión visual de institución y login con build de producción y API simulada, sin SQL ni proveedores.
- Comprobación numérica representativa del texto sobre la zona más clara del degradado de tarjeta: texto principal 5,62:1, secundario 4,66:1 y primario 4,52:1; texto sobre botón primario 10,06:1. Es una comprobación focalizada, no una auditoría de contraste de todos los componentes/estados.

ESLint focalizado y build satisfactorios; persiste el aviso previo por chunk mayor de 500 kB. No se declaran completos C1–C5 ni los requisitos integrales de SPEC-002.

### Paleta ejecutiva y separación de superficies (2026-11-15)

A petición posterior del responsable, se sustituye la dominante verde del refinamiento anterior por superficies diferenciadas: lateral carbón `#19282e`, barra superior petróleo `#243b42` y fondo central grafito `#2c393f`, con tarjetas gris azulado y acentos salvia `#9acbb1`. Se atenúan los halos y la textura; el verde queda reservado principalmente para acciones, indicadores e identidad. Sin cambios de estructura, navegación, datos ni lógica.

El elemento lateral seleccionado combina fondo al 6 % con superposición activa al 4 %, en lugar de sumar dos capas intensas. Se conservan las respuestas visuales de hover y foco de Vuetify. Revisión visual y comprobación operativa con Edge aislado y API simulada a 1440×1000 y 390×844: superficies diferenciadas, selección visible, hover/foco presentes y menú móvil operable sin desbordamiento horizontal.

Contraste representativo calculado sobre la zona más clara de las tarjetas: texto principal 8,06:1, secundario 6,00:1 y primario 5,02:1; texto de botón primario 8,03:1. No equivale a certificar todos los estados/componentes. ESLint focalizado y build correctos, con el aviso previo de tamaño de chunk; sin acceso a PostgreSQL ni proveedores.

### Referencia oliva y retirada de la barra superior (2026-11-15)

Solicitud posterior: retirar la barra superior de los tres paneles y tomar únicamente los colores de la imagen proporcionada. Se mantiene la tipografía, disposición y componentes existentes; no se copia el diseño de la referencia.

- `RoleLayout` deja de renderizar la barra y su espacio superior. El nombre del usuario, navegación, perfil y cierre de sesión permanecen en el lateral. En móvil se conserva un botón compacto para abrir el menú, sin reconstruir una barra.
- Colores muestreados de la referencia: fondo `#4a493c`, lateral `#25231b`, tarjetas `#585747`, selección `#3b3932` y texto secundario `#f3d6a2`. El primario se aclara ligeramente a `#b6da92` para alcanzar 4,68:1 sobre las tarjetas; texto principal 6,32:1 y secundario 5,21:1 en esa superficie.
- Los colores semánticos de Tailwind reutilizan los tokens compartidos/Vuetify: antes sus valores independientes conservaban el verde anterior en iconos y etiquetas. El chat del estudiante adopta los mismos tonos en burbujas, código y entrada, sin cambiar su composición.

Verificación con build de producción, Edge aislado y API simulada: administración, coordinación y estudiante sin `v-app-bar`, sin banner superior ni padding superior reservado; escritorio 1440×1000 y móvil 390×844, apertura/cierre del menú y ausencia de desbordamiento horizontal. El chat ocupa el viewport de escritorio sin scroll de página adicional; la agenda del alumno sigue accesible desde el menú móvil. Primario renderizado de iconos/etiquetas contrastado con el token esperado, sin errores JavaScript ni peticiones inesperadas.

ESLint focalizado y build correctos. Persiste el aviso previo de chunk mayor de 500 kB. Sin cambios de backend, SQL, datos reales, dependencias ni certificación integral de SPEC-002.

### Topo cálido + Oliva ejecutivo (2026-11-15)

La paleta explícita proporcionada posteriormente sustituye los colores de la referencia anterior:

| Uso | Color |
| --- | --- |
| Fondo general | `#9A8C7D` |
| Tarjetas, paneles, formularios y diálogos | `#575646` |
| Lateral y texto sobre verde | `#25231B` |
| Selección y botones secundarios | `#404036` |
| Acciones principales e indicadores activos | `#B6DA92` |
| Texto principal y lateral normal | `#F2EFE3` |
| Texto secundario, etiquetas y acentos secundarios | `#D5BE90` |
| Bordes y divisores | `#74745D` |

Cambios limitados a colores, bordes y sombras: fondo mate uniforme, superficies opacas diferenciadas, sombras cálidas suaves y reducción de halos/brillos. Se incluyen estilos particulares de acceso, red decorativa, cursos, analíticas, agenda, chat y diagramas Mermaid, además de los tokens CSS/Tailwind/Vuetify. Los desplegables reciben superficie de tarjeta en lugar de heredar transparencia; las listas integradas mantienen su fondo original heredado. Se preservan los estados de foco, error y deshabilitado, así como el color semántico de error desaturado.

Verificación focalizada con Edge aislado y todas las peticiones API interceptadas, sin mutaciones: login, los tres roles, institución/cursos/cuentas/analíticas/perfil del coordinador, alta de institución en diálogo, chat con diagrama y ampliación, selector de materia y agenda móvil. Colores computados contrastados con los valores solicitados, incluyendo tarjetas/bordes, lateral, selección, botones, desplegables y diagramas.

Comparación antes/después de geometría, tipografía y radios en escritorio 1440×1000 sin diferencias. En móvil 390×844 se comprobó el renderizado tras estabilizar los breakpoints, estructura, menú y agenda operables y ausencia de desbordamiento horizontal. Revisión visual de acceso e institución; sin errores JavaScript ni peticiones inesperadas. ESLint focalizado y build de producción correctos, con el aviso previo de chunk mayor de 500 kB. Sin cambios en dependencias, backend, SQL o datos reales; no supone certificación integral de SPEC-002.

### Fondo eucalipto y login diferenciado (2026-11-15)

A petición posterior, el fondo general cambia de topo a eucalipto `#638478`, más vivo, manteniendo las tarjetas y el resto de la paleta. El login compartido utiliza un fondo independiente verde petróleo `#182D2A`, definido localmente sin extender ese tono a los paneles.

La red decorativa del login aumenta su grosor un 50 %: líneas de 1,5 px y radios base de partículas entre 1,2 y 3 px. El ajuste queda limitado a esa instancia; el chat conserva líneas de 1 px y radios base entre 0,8 y 2 px. No cambian velocidad, densidad, conexiones, interacción del cursor ni disposición de las pantallas.

Verificación con Edge aislado y API interceptada: colores computados de fondo comprobados en login y los tres roles, conservando las superficies de tarjetas/lateral. Instrumentación del canvas verifica grosor de conexiones normales y del cursor, radios y continuidad del dibujo animado; con movimiento reducido se conserva la imagen estática. Login revisado a 1440×1000 y 390×844, sin desbordamiento horizontal. ESLint focalizado y build correctos, con el aviso previo de tamaño de chunk; sin SQL, proveedores ni cambios funcionales.

## Cierre funcional acotado de SPEC-002 (2026-11-15)

### Decisión y entrega

El responsable pidió reutilizar la implementación/evidencia, completar solo lo faltante de C1–C4 y minimizar C5. Aprobó **«Claro verde muy claro/blanco y Oscuro verde suave; conservar el login petróleo solo en Oscuro como excepción explícita»** y **«Revisar nombres, roles y estados accesibles en Edge; dejar el recorrido con lector real documentado como no ejecutado y no bloqueante»**. La enmienda queda en [spec.md](spec.md); catálogo y equivalencias reales, en [plan.md](plan.md).

Fondos vigentes: Claro `#E6F4DF`, Oscuro `#405C4E`; login Claro `#D2E6D8`, login Oscuro `#182D2A`. Tokens canónicos y controlador previo a Vue resuelven Claro/Oscuro/Sistema. Selector en login/lateral, sin recuperar la barra superior. Se reutilizan layout, vistas, perfil, agenda y bloques locales, añadiendo únicamente primitivas compartidas con consumidores reales.

### Entorno y modalidad

- Revisión: `565dd39` **más cambios locales** de esta entrega; no se presenta ese commit como si ya contuviera los nuevos archivos.
- Windows; Node `22.17.0`, Vue/Vuetify/Vite existentes. Referencia horaria local del registro final: `2026-11-15T11:23:56.7557965-04:00`.
- Build de producción servido en `http://127.0.0.1:5174`. Binario instalado de **Microsoft Edge `157.0.4341.46`**, ejecución headless mediante Playwright existente en el espacio de sesión y `--disable-gpu`. No se infiere canal estable ni compatibilidad por compartir motor con Chrome.
- Consultas semánticas, estilos calculados, acciones/foco y capturas de ese navegador; login consultado adicionalmente en el navegador integrado. No equivale a recorrido humano completo ni lector real.
- Viewports CSS: administrador `320×568`, `768×1024`, `1440×900` en ambos temas; coordinador `390×844`; estudiante `320×568`, además de recorridos de escritorio. Contextos con movimiento reducido. DPR, escala del SO y zoom de navegador **no registrados para certificación**; no se ejecutó matriz de zoom 200 %/400 %.
- Todos los destinos `**/api/**` interceptados con respuestas sintéticas; petición desconocida y error de página hacen fallar el caso. Sin backend, SQL, proveedores, audio real ni datos de cuentas reales. Las respuestas de alta/guardado solo prueban reacción del frontend, no persistencia real.
- Controlador comprobado en VM y paginación con el runtime Vue existente; el resto en Edge real con dobles HTTP. Sin instalar paquetes ni introducir modo mock permanente.

### Casos seleccionados y resultado obtenido

Todos los identificadores siguientes emitieron `PASS`; se ejecutaron por grupos y solo se repitieron los afectados por correcciones. No representan ejecución de todos los casos detallados de [cases.md](cases.md).

| Identificador ejecutado | Esperado y obtenido | Cobertura |
|---|---|---|
| `UI-02/controller-storage-system-disposal` | Preferencias ausentes/corruptas/válidas, fallback sin soporte, cambio de sistema solo en Sistema, evento entre pestañas y borrado de preferencia; storage bloqueado avisa y conserva estado en memoria; unsubscribe/dispose retiran callbacks | RF-2/3/4; T07–T09, VM, no campaña de 20 ciclos |
| `UI-05/pagination-boundaries` | 0/1/11/26 filas, páginas 10, ajuste al reducir datos y conservación de página 2 mientras carga la lista | RF-11; T31/T48, runtime Vue |
| `UI-02/login-prepaint-keyboard-cross-tab-mobile` | Primer RAF refleja preferencia contraria al sistema, selector con teclado y sincronización de pestañas; datos conservados, error de acceso genérico, cambio de tema sin HTTP y login utilizable a 320 px | RF-2/3/4/8; T10/T13/T14/T17/T18 |
| `UI-03/admin-lists-dialogs-profile-theme` | Búsqueda, 10 de 26 instituciones, permanecer/descartar en alta/perfil, secciones alcanzables y tema con diálogo abierto sin perder datos ni generar peticiones | RF-6/8/9/11; C2/C3, no todas las permutaciones CRUD |
| `UI-04/coordinator-form-pagination-return-profile` | Lista página 2→detalle→retorno página 2; invalidación accesible/foco del primer campo, un POST ante doble clic, 500 seguro conserva edición; cuentas/institución/perfil; resultados 30/90 invertidos conservan 90; drawer móvil contiene foco, Escape, fondo inert y retorno al disparador | RF-6/8/9/10/11/17; C2/C3 y T84/T85 |
| `UI-07/student-draft-IME-image-scroll-mermaid-agenda` | IME/Mayús+Enter no envían; permanecer conserva borrador/imagen durante tema; un envío, fallo conserva composición y no reenvía; respuesta no baja al lector situado arriba; diagramas válido/inválido aislados, tema sin HTTP, zoom real y bbox dentro del viewBox, foco tras cierre; agenda con 12 actividades y perfil | RF-14–17; C4 |
| `UI-03/not-found-expired-cleanup` | 401 al guardar perfil ya sucio expulsa sin bloqueo, elimina token y texto privado y muestra explicación de expiración; ruta desconocida tiene retorno usable | RF-6/9/10; T33/T35 |
| `UI-06/pdf-boundaries-safe-excel-knowledge-states` | 20 MiB+1 y 11 PDF rechazados sin request; 20 MiB exactos admitidos por el mock; queued/processing/completed/failed/unknown distinguibles; resumen Excel parcial muestra conteos/categorías sin fila, contraseña ni razón SQL cruda | RF-12/13; T55/T56/T60/T61, no indexación/importación real |
| `UI-09/rendered-contrast-responsive` | Muestra de ratios estabilizados satisface umbrales, viewports registrados sin overflow global y controles disponibles; semántica/foco en muestra móvil | RF-1/4/19; T83/T86, no conformidad WCAG global |
| `UI-07/images-types-exact-size-speech-double-fallback` | PNG/JPEG/WEBP/GIF; 4 MiB admitidos y 4 MiB+1 rechazados; inicio explícito de reconocimiento doble, resultado revisable, tema conserva texto/escucha, abandonar aborta; sin soporte se conserva escritura manual | RF-15; T70/T71, no micrófono/permiso/dictado real |
| `UI-02/storage-blocked-real-app-no-matchmedia` | App arranca sin matchMedia y con Storage bloqueado, resuelve Claro, permite cambiar a Oscuro e iniciar sesión sintética en memoria y cargar cursos; no pantalla en blanco por el almacén de autenticación | RF-2/3; T07/T08/T14, Edge con APIs controladas |

### Contraste mínimo

Se muestrean estilos computados de texto/botón una vez estabilizado el tema (~250 ms); borde/foco corresponden al rol de token contra la tarjeta renderizada. No se atribuye medición a todos los overlays, estados ni contornos visibles. Una lectura durante transición no es el ratio final.

| Pareja | Claro | Oscuro | Umbral |
|---|---:|---:|---:|
| Texto principal / tarjeta | 12,76:1 | 8,61:1 | 4,5:1 |
| Texto secundario / tarjeta | 7,51:1 | 6,83:1 | 4,5:1 |
| Texto / botón principal | 5,07:1 | 7,75:1 | 4,5:1 |
| Rol borde de control / tarjeta | 4,91:1 | 5,02:1 | 3:1 |
| Rol foco / tarjeta | 6,50:1 | 6,53:1 | 3:1 |

### Defectos observados, corrección y re-ejecución

- **Página de cursos:** la lista vacía inicial restablecía prematuramente la página retenida. El clamp espera fin de carga; límite y retorno en Edge pasan.
- **Semántica de controles:** reglas Vuetify no exponían `aria-invalid`; periodo analítico no anunciaba selección. Estado explícito y primer inválido enfocado; muestra vuelve a pasar.
- **Drawer móvil:** `$el` de Vuetify podía ser un marcador de fragmento; se usa la raíz nativa desde el botón Cerrar. Focus trap/Escape/retorno pasan. Se oculta temporalmente el toast para no tapar el primer control, sin borrar el aviso.
- **Mermaid:** viewBox inicial recortaba nodos trasladados, max-width inline impedía zoom real y rerender de tema destruía el disparador. Bbox tras inserción, override de zoom y conservación del SVG/disparador con restauración after-leave; tamaño real, contención y foco pasan.
- **Arranque degradado:** controlar solo el storage de apariencia no protegía el inicio de auth. Operaciones de su almacenamiento ahora avisan y usan estado en memoria; Authorization y validación de 401 usan el token vigente del store, sin cambiar el contrato. Login/Synapse toleran ausencia de matchMedia. Caso de app real bloqueada y regresión de expiración pasan.

### Construcción, alcance y límites

`npm run lint`: **código 0**, sin errores/avisos. `npm run build`: **código 0**, con el aviso histórico de chunk >500 kB; no se elevó el umbral ni se añadió dependencia. Build final comprobado con Edge; tras los últimos cambios se repitieron almacenamiento bloqueado, coordinador, expiración, login, administrador y estudiante. La muestra restante ya satisfactoria se reutiliza cuando no cambió.

Cotejo mínimo T81: manifiestos frontend sin cambios; patrones presentacionales delegan HTTP al contenedor/composable; tokens centralizados; único dato persistente nuevo `tutoria.appearance`. Endpoints, payloads, bindings Excel y límites backend conservados. Cambios backend/seed presentes previamente en el árbol **no pertenecen a este cierre** y se preservan; no se ejercitaron ni modificaron aquí.

**No ejecutados:** lector real/anuncios acústicos, micrófono/permisos/dictado real, Android/iOS/teclado virtual, matriz completa de zoom/viewports/roles, Chrome/Firefox, 20 muestras de latencia/20 ciclos, campaña de contenido malicioso, todas las permutaciones CRUD, regresión backend/DB/proveedores y S-2 en sistema real. Una fuente Mermaid como texto no equivale a descripción alternativa del contenido si no viene en origen.

**Tareas futuras sin casilla de ejecución:** T87, T89–T91, T92–T93 y T94–T98. T85 semántica y T86 muestra responsive se cierran solo con el alcance mínimo aprobado; sus partes de lector/zoom/dispositivo real quedan futuras. T88 tiene resultado propio, sin depender de Chrome diferido.

**Limpieza verificada:** preview local detenido, contextos Edge cerrados por el checker, script temporal y sus seis capturas eliminados por ruta exacta. Se preservan otros helpers del espacio de sesión. Sin datos reales creados que revertir. `git diff --check` satisfactorio; conteo automático confirma 98 tareas, 87 marcadas y únicamente las once diferidas sin marcar. No se realizó commit/push.

**Veredicto:** C1–C4 funcionalmente completados, T80–T86 mínimos y T88 satisfechos en el alcance adaptado; **87 tareas cerradas y 11 diferidas**. No aprobación integral de los 28 requisitos ni ejecución de T98. Se puede continuar la definición de SPEC-003 con los límites y brechas de producto vigentes.

### Ajustes posteriores: Perfil, campos y switches (2026-11-15)

A petición del responsable, el selector de apariencia se traslada del sidebar a `ProfilePanel`, compartido por los tres roles, y se conserva en login. Funciona incluso mientras el perfil carga/falla y aplica la preferencia al instante, independientemente de Guardar perfil. La mención al lateral en la evidencia de cierre anterior describe la ubicación comprobada en aquel momento, no la vigente.

Reproducción y comprobación focalizada en Edge `157.0.4341.46`, build servido, API totalmente interceptada:

- **Planes:** la etiqueta flotante estaba 9 px por encima del área visible de la fila. Con espacio vertical adicional, las tres etiquetas quedan dentro del contenedor (muestra Nombre: top 238,5 frente a límite 231,5; bottom 256,5 frente a límite 303,5).
- **Switches:** pista apagada antes casi idéntica al pulgar y opacidad 0,6. Ahora pista opaca con rol de borde de control al apagar y verde al encender; pulgar de superficie/on-primary respectivamente. Ambos estados cambian correctamente en Claro/Oscuro. Ajuste común sin sobrescribir el modo de colores forzados.
- **Foco:** el input interno del login recibía el outline global sólido de 2 px. Se elimina únicamente ese marco duplicado; Vuetify conserva el campo enfocado y los botones conservan outline de teclado. Clic en lupa de búsqueda de alumnos enfoca el input sin marco interno; comprobado en ambos temas.
- **Perfil de los tres roles:** selector visible, ausente del sidebar; elegir Oscuro actualiza tema sin perder el nombre editado. A 390×844 sigue disponible y sin overflow horizontal global.

`npm run lint` y `npm run build` código 0; permanece el aviso histórico de chunk >500 kB. Casos focalizados satisfactorios, sin errores de página ni peticiones API desconocidas. Capturas del switch apagado inspeccionadas en ambos temas. No backend/DB/proveedores ni cambios en el alcance de tareas diferidas.

### Login fijo Oscuro y red con deriva sostenida (2026-11-15)

Nueva decisión del responsable: retirar Apariencia del login y mostrarlo siempre Oscuro. Se fija tema local CSS/Vuetify, sin modificar storage/controlador global; Apariencia permanece solo en Perfil. Sustituye el comportamiento de login descrito en las secciones anteriores, que se conserva como evidencia histórica.

La instancia de red del login usa mayor densidad (área/14000, mínimo 52/máximo 150), nodos con opacidad 0,6 y conexiones más claras, conservando grosor de 1,5 px. Una velocidad mínima de deriva impide que la fricción detenga las partículas sin cursor. El chat mantiene los valores y amortiguación anteriores. Se conserva render estático con movimiento reducido y pausa en pestaña oculta.

**Verificación:** lint/build código 0, mismo aviso previo de chunk. Edge `157.0.4341.46`, build servido, API interceptada: con SO/preferencia Claro, login sin selector, CSS/Vuetify Oscuro y fondo computado `rgb(24, 45, 42)`; preferencia global permanece Claro. Tras autenticación sintética y navegación a Perfil, se recuperan superficies claras y selector. Canvas instrumentado: 93 nodos a 1440×900, 52 a 390×844, colores/grosor esperados y posiciones cambiantes sin cursor; sin overflow horizontal móvil. Movimiento reducido conserva posiciones sin redibujo continuo. Simulación focalizada de 2000 pasos confirma velocidad sostenida solo para la variante de login y amortiguación original en la variante compartida. Captura de escritorio inspeccionada; sin errores de página, backend real, DB ni proveedores.
