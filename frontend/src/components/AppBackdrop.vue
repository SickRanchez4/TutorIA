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
  background: var(--tutoria-bg);
}

.app-backdrop__noise,
.app-backdrop__vignette {
  position: absolute;
  inset: 0;
}

/* Explicit tile size: an SVG without intrinsic size renders as a single square. */
.app-backdrop__noise {
  opacity: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 220 220' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.35'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 220px 220px;
}

.app-backdrop__vignette {
  background: transparent;
}
</style>
