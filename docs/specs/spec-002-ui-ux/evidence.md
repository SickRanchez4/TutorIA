# Evidencia de SPEC-002 — C0

Resumen único de la preparación C0, referido por [test.md](test.md) y [tasks.md](tasks.md). Los archivos separados de entorno, baseline, validación y salidas de lint/build se consolidaron aquí el 2026-10-31. Commit de referencia: `6b7b79bbfdbea5614ffe369330e55905fffe3c98`, sin cambios de producto. C0 no implementa ni verifica interfaz: los 28 requisitos de UI siguen **no ejecutados**.

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
