/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
  ],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#5865F2',
          50: '#FFFFFF',
          100: '#F0F1FE',
          200: '#D1D3FC',
          300: '#B1B5FA',
          400: '#9298F8',
          500: '#727AF6',
          600: '#525CF4',
          700: '#313EF2',
          800: '#1121E6',
          900: '#0E1BCB',
          950: '#0C18B3'
        },
        secondary: {
          DEFAULT: '#36393F',
          50: '#9A9DA5',
          100: '#8F929C',
          200: '#797D88',
          300: '#636772',
          400: '#4D515C',
          500: '#36393F',
          600: '#2A2D31',
          700: '#1E2024',
          800: '#121316',
          900: '#060708',
          950: '#000000'
        },
        success: {
          DEFAULT: '#57F287',
          50: '#FFFFFF',
          100: '#F0FEF5',
          200: '#D1FCE2',
          300: '#B1FACE',
          400: '#92F8BB',
          500: '#73F5A7',
          600: '#57F287',
          700: '#24EF65',
          800: '#0FD24E',
          900: '#0BA83E',
          950: '#098E34'
        },
        warning: {
          DEFAULT: '#FEE75C',
          50: '#FFFFFF',
          100: '#FFFEF8',
          200: '#FFFBDD',
          300: '#FFF8C2',
          400: '#FFF5A7',
          500: '#FFF28C',
          600: '#FEEF71',
          700: '#FEEC56',
          800: '#FEE75C',
          900: '#FEE031',
          950: '#FDDC15'
        },
        danger: {
          DEFAULT: '#ED4245',
          50: '#FCDEDF',
          100: '#FBCBCC',
          200: '#F8A5A7',
          300: '#F57F82',
          400: '#F1595D',
          500: '#ED4245',
          600: '#E31A1E',
          700: '#BA1518',
          800: '#910F13',
          900: '#690A0D',
          950: '#57090B'
        },
        dark: {
          DEFAULT: '#36393F',
          nav: '#2F3136',
          channel: '#2A2D31',
          message: '#40444B',
          sidebar: '#202225',
          footer: '#292B2F'
        },
        accent: {
          blue: '#00B0F4',
          purple: '#5865F2',
          green: '#57F287',
          yellow: '#FEE75C',
          red: '#ED4245',
          pink: '#EB459E'
        },
        theme: {
          space: {
            primary: '#4d76ff',
            secondary: '#1a1a2e',
            accent: '#7d4cdb'
          },
          neon: {
            primary: '#ff00cc',
            secondary: '#00ffcc',
            accent: '#3300ff'
          },
          contrast: {
            primary: '#ffff00',
            secondary: '#000000',
            accent: '#00aaff'
          }
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.5s ease-out',
        'pulse-subtle': 'pulseSubtle 2s infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      boxShadow: {
        'neon-pink': '0 0 10px rgba(255, 0, 204, 0.5), 0 0 20px rgba(255, 0, 204, 0.3)',
        'neon-blue': '0 0 10px rgba(0, 153, 255, 0.5), 0 0 20px rgba(0, 153, 255, 0.3)',
        'neon-green': '0 0 10px rgba(0, 255, 153, 0.5), 0 0 20px rgba(0, 255, 153, 0.3)',
        'neon-yellow': '0 0 10px rgba(255, 255, 0, 0.5), 0 0 20px rgba(255, 255, 0, 0.3)',
        'space-glow': '0 0 15px rgba(77, 118, 255, 0.6)',
        'discord': '0 0 10px rgba(88, 101, 242, 0.4)',
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: '65ch',
            color: 'inherit',
            '[class~="lead"]': {
              color: 'inherit',
            },
            a: {
              color: 'var(--primary-color)',
              textDecoration: 'underline',
              fontWeight: '500',
            },
            strong: {
              color: 'inherit',
              fontWeight: '600',
            },
            'ol[type="A"]': {
              listStyleType: 'upper-alpha',
            },
            'ol[type="a"]': {
              listStyleType: 'lower-alpha',
            },
            'ol[type="I"]': {
              listStyleType: 'upper-roman',
            },
            'ol[type="i"]': {
              listStyleType: 'lower-roman',
            },
            'ol[type="1"]': {
              listStyleType: 'decimal',
            },
            'ul > li::before': {
              backgroundColor: 'currentColor',
              opacity: 0.5,
            },
            'ol > li::before': {
              color: 'inherit',
              opacity: 0.6,
            },
            'code::before': { content: '""' },
            'code::after': { content: '""' },
            'blockquote p:first-of-type::before': {
              content: '',
            },
            'blockquote p:last-of-type::after': {
              content: '',
            },
            h1: {
              color: 'inherit',
              fontWeight: '600',
            },
            h2: {
              color: 'inherit',
              fontWeight: '600',
            },
            h3: {
              color: 'inherit',
              fontWeight: '600',
            },
            h4: {
              color: 'inherit',
              fontWeight: '600',
            },
            'figure figcaption': {
              color: 'inherit',
              opacity: 0.6,
            },
            code: {
              color: 'inherit',
              fontWeight: '600',
            },
            'a code': {
              color: 'inherit',
            },
            pre: {
              color: 'var(--text-color)',
              backgroundColor: 'var(--card-bg)',
              borderRadius: '0.375rem',
              padding: '1rem',
              border: '1px solid var(--border-color)',
            },
            thead: {
              color: 'inherit',
              borderBottomColor: 'currentColor',
              borderBottomWidth: '1px',
            },
            'tbody tr': {
              borderBottomColor: 'currentColor',
              borderBottomWidth: '1px',
              opacity: 0.7,
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
  ],
}