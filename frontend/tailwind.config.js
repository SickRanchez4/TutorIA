/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        primary: '#7cc576',
        'primary-dark': '#5fa85f',
        'primary-light': '#9fd99f',
        secondary: '#f3f4f6',
        light: '#ffffff',
        dark: '#17181c',
        surface: '#1e1f25',
        'surface-2': '#26272e',
        'surface-3': '#2f3038',
        muted: '#a3a5ad',
        'gray-soft': '#26272e',
        'gray-border': 'rgba(255, 255, 255, 0.09)',
        // Semantic overrides so existing gray/red/green/amber/blue utility
        // classes automatically render correctly on the new dark surface.
        gray: {
          50: '#202126',
          100: '#26272e',
          200: '#2f3038',
          300: '#3d3e47',
          400: '#5c5e68',
          500: '#82838d',
          600: '#a9abb4',
          700: '#c5c7cd',
          800: '#dfe0e4',
          900: '#f5f6f7',
        },
        red: {
          50: '#2a1414',
          100: '#3a1a1a',
          200: '#4a2222',
          600: '#f47272',
          700: '#fb9c9c',
        },
        green: {
          100: '#153a20',
          700: '#86e08c',
        },
        amber: {
          50: '#2a2210',
          100: '#3a2e14',
          600: '#f0b94d',
          700: '#f7ca72',
        },
        blue: {
          50: '#12202e',
          600: '#6fb2f2',
        },
      },
      fontFamily: {
        sans: ['system-ui', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 0 24px rgba(124, 197, 118, 0.25)',
        card: '0 4px 24px rgba(0, 0, 0, 0.35)',
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

