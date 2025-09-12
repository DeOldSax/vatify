import defaultTheme from 'tailwindcss/defaultTheme'

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", ...defaultTheme.fontFamily.sans],
        mono: ["IBM Plex Mono", ...defaultTheme.fontFamily.mono],
      },
      colors: {
        brand: {
          50:  "#f5f9ff",
          100: "#e8f0ff",
          200: "#d6e4ff",
          300: "#adc8ff",
          400: "#84a9ff",
          500: "#5b8def",
          600: "#3366ff",  // Primary – vertrauensvolles Blau
          700: "#254eda",
          800: "#1939b7",
          900: "#102693",
        },
        success: {
          500: "#16a34a", // grün für ok
        },
        danger: {
          500: "#dc2626", // rot für Fehler
        },
        warning: {
          500: "#f59e0b", // gelb für Hinweis
        },
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.25rem',
      },
      boxShadow: {
        soft: "0 2px 6px rgba(0,0,0,0.05)",
        card: "0 4px 12px rgba(0,0,0,0.06)",
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
