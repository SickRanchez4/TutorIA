import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const tutoria = {
  dark: true,
  colors: {
    background: '#17181c',
    surface: '#1e1f25',
    'surface-bright': '#26272e',
    'surface-variant': '#2f3038',
    'on-surface-variant': '#c5c7cd',
    primary: '#7cc576',
    'primary-darken-1': '#5fa85f',
    secondary: '#f3f4f6',
    'secondary-lighten-1': '#ffffff',
    error: '#f47272',
    info: '#6fb2f2',
    success: '#7cc576',
    warning: '#f0b94d',
    'on-primary': '#0a0a0c',
    'on-secondary': '#0a0a0c',
    'on-background': '#f3f4f6',
    'on-surface': '#f3f4f6',
    'on-error': '#ffffff',
    'on-info': '#0a0a0c',
    'on-success': '#0a0a0c',
    'on-warning': '#0a0a0c',
  },
  variables: {
    'border-color': '#ffffff',
    'border-opacity': 0.1,
    'high-emphasis-opacity': 1,
    'medium-emphasis-opacity': 0.72,
    'theme-code': '#26272e',
    'theme-on-code': '#f3f4f6',
  },
}

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'tutoria',
    themes: { tutoria },
  },
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
    VDataTable: {
      hover: true,
    },
  },
})

