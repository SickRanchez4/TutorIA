<template>
  <div class="app-backdrop" aria-hidden="true">
    <div class="app-backdrop__noise"></div>
    <div class="app-backdrop__vignette"></div>
  </div>
</template>

<style scoped>
/*
 * Fixed, viewport-sized decorative layer shared by every screen. Being fixed,
 * it never ends where the scrollable content ends.
 */
.app-backdrop {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(100% 90% at 0% 0%, rgba(var(--tutoria-green-rgb), 0.11), transparent 55%),
    radial-gradient(70% 110% at 100% 100%, rgba(69, 148, 113, 0.12), transparent 58%),
    linear-gradient(127deg, #111419 0%, #171b20 52%, #121518 100%);
}

.app-backdrop__noise,
.app-backdrop__vignette {
  position: absolute;
  inset: 0;
}

/* Explicit tile size: an SVG without intrinsic size renders as a single square. */
.app-backdrop__noise {
  opacity: 0.2;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 220 220' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.35'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 220px 220px;
}

.app-backdrop__vignette {
  background: radial-gradient(120% 95% at 50% 42%, transparent 45%, rgba(9, 11, 13, 0.5) 100%);
}
</style>
