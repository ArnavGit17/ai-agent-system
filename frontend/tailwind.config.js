/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        surface: {
          0: '#0a0a0f',
          1: '#12121a',
          2: '#1a1a26',
          3: '#242434',
        },
        accent: {
          DEFAULT: '#6c5ce7',
          dim: '#5a4bd4',
          glow: '#8b7cf7',
        },
        success: '#00b894',
        warning: '#fdcb6e',
        danger: '#e17055',
      },
    },
  },
  plugins: [],
};
