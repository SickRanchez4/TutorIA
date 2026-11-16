/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        primary: 'rgba(var(--tutoria-green-rgb), <alpha-value>)',
        'primary-dark': 'rgba(var(--v-theme-primary-darken-1), <alpha-value>)',
        'primary-light': 'var(--tutoria-green-bright)',
        secondary: 'rgba(var(--v-theme-secondary), <alpha-value>)',
        light: 'var(--tutoria-text)',
        dark: 'var(--tutoria-sidebar-bg)',
        surface: 'rgba(var(--v-theme-surface), <alpha-value>)',
        'surface-2': 'rgba(var(--v-theme-surface-bright), <alpha-value>)',
        'surface-3': 'rgba(var(--v-theme-surface-variant), <alpha-value>)',
        muted: 'var(--tutoria-text-muted)',
        'gray-soft': 'rgba(var(--v-theme-surface-variant), <alpha-value>)',
        'gray-border': 'var(--tutoria-border)',
      },
      fontFamily: {
        sans: ['system-ui', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 0 24px rgba(var(--tutoria-green-rgb), 0.06)',
        card: 'var(--tutoria-shadow)',
      },
      backdropBlur: {
        xs: '2px',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.97)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.35s ease-out',
        'scale-in': 'scale-in 0.25s ease-out',
      },
    },
  },
  plugins: [],
};

