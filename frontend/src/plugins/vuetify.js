import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import { es } from 'vuetify/locale'

function readTheme(name) {
  const node = document.createElement('div')
  node.dataset.theme = name
  node.hidden = true
  document.documentElement.append(node)
  const css = getComputedStyle(node)
  const token = key => css.getPropertyValue(`--tutoria-${key}`).trim()
  const theme = {
    dark: name === 'dark',
    colors: {
      background: token('bg'),
      surface: token('surface'),
      'surface-bright': token('surface-raised'),
      'surface-variant': token('nav-active-bg'),
      'on-surface-variant': token('text-muted'),
      primary: token('green'),
      'primary-darken-1': token('green-bright'),
      secondary: token('nav-active-bg'),
      'secondary-lighten-1': token('surface-raised'),
      error: token('error'),
      info: token('info'),
      success: token('green'),
      warning: token('warning'),
      'on-primary': token('on-primary'),
      'on-secondary': token('on-selected'),
      'on-background': token('text'),
      'on-surface': token('text'),
      'on-error': token('on-error'),
      'on-info': token('on-info'),
      'on-success': token('on-primary'),
      'on-warning': token('on-warning'),
    },
    variables: {
      'border-color': token('border'),
      'border-opacity': 1,
      'high-emphasis-opacity': 1,
      'medium-emphasis-opacity': 0.8,
      'theme-code': token('nav-active-bg'),
      'theme-on-code': token('text'),
    },
  }
  node.remove()
  return theme
}

export default createVuetify({
  theme: {
    defaultTheme: `tutoria-${window.tutoriaAppearance.getState().resolved}`,
    themes: { 'tutoria-light': readTheme('light'), 'tutoria-dark': readTheme('dark') },
  },
  locale: { locale: 'es', fallback: 'es', messages: { es } },
  typography: {
    fontFamily: "'Roboto', 'Roboto Mono', 'Segoe UI', 'Helvetica Neue', sans-serif",
  },
  defaults: {
    VBtn: {
      rounded: 'lg',
      class: 'text-none font-weight-medium',
      variant: 'tonal',
      border: false,
    },
    VCard: {
      rounded: 'lg',
      color: 'surface',
      elevation: '0',
      class: 'border-thin',
    },
    VDialog: {
      transition: 'scale-transition',
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      flat: true,
      hideDetails: 'auto',
      border: 'sm',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      flat: true,
      hideDetails: 'auto',
      border: 'sm',
    },
    VTextarea: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      flat: true,
      hideDetails: 'auto',
      border: 'sm',
    },
    VSwitch: {
      color: 'primary',
      density: 'compact',
      hideDetails: true,
      inset: true,
    },
    VCheckbox: {
      color: 'primary',
      density: 'compact',
      hideDetails: true,
    },
    VChip: {
      rounded: 'lg',
    },
    VTooltip: {
      location: 'top',
    },
    VTabs: {
      color: 'primary',
    },
    // Lists inherit the card/drawer surface instead of painting their own slab.
    VList: {
      bgColor: 'transparent',
    },
    VDataTable: {
      hover: true,
    },
  },
})

