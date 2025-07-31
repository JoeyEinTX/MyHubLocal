/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Theme 1: Calm & Clean
        'calm-light': {
          primary: 'rgb(59 130 246)', // blue-500
          accent: 'rgb(16 185 129)', // emerald-500
          background: 'rgb(249 250 251)', // gray-50
          card: 'rgb(255 255 255)', // white
          text: 'rgb(31 41 55)', // gray-800
        },
        'calm-dark': {
          primary: 'rgb(37 99 235)', // blue-600
          accent: 'rgb(5 150 105)', // emerald-600
          background: 'rgb(17 24 39)', // gray-900
          card: 'rgb(31 41 55)', // gray-800
          text: 'rgb(243 244 246)', // gray-100
        },

        // Theme 2: Sleek & Dark
        'sleek-light': {
          primary: 'rgb(37 99 235)', // blue-600
          accent: 'rgb(99 102 241)', // indigo-500
          background: 'rgb(243 244 246)', // gray-100
          card: 'rgb(255 255 255)', // white
          text: 'rgb(17 24 39)', // gray-900
        },
        'sleek-dark': {
          primary: 'rgb(29 78 216)', // blue-700
          accent: 'rgb(79 70 229)', // indigo-600
          background: 'rgb(15 23 42)', // slate-900
          card: 'rgb(30 41 59)', // slate-800
          text: 'rgb(226 232 240)', // slate-200
        },

        // Theme 3: Sunset Glow
        'sunset-light': {
          primary: 'rgb(249 115 22)', // orange-500
          accent: 'rgb(250 204 21)', // yellow-400
          background: 'rgb(255 251 235)', // amber-50
          card: 'rgb(254 243 199)', // amber-100
          text: 'rgb(154 52 18)', // orange-900
        },
        'sunset-dark': {
          primary: 'rgb(234 88 12)', // orange-600
          accent: 'rgb(245 158 11)', // amber-500
          background: 'rgb(23 23 23)', // neutral-900
          card: 'rgb(38 38 38)', // neutral-800
          text: 'rgb(252 211 77)', // amber-200
        },

        // Theme 4: Ocean Breeze
        'ocean-light': {
          primary: 'rgb(14 165 233)', // sky-500
          accent: 'rgb(20 184 166)', // teal-500
          background: 'rgb(240 249 255)', // sky-50
          card: 'rgb(224 242 254)', // sky-100
          text: 'rgb(22 78 99)', // cyan-900
        },
        'ocean-dark': {
          primary: 'rgb(2 132 199)', // sky-600
          accent: 'rgb(13 148 136)', // teal-600
          background: 'rgb(22 78 99)', // cyan-900
          card: 'rgb(21 94 117)', // cyan-800
          text: 'rgb(165 243 252)', // cyan-200
        },

        // Theme 5: Forest Haze
        'forest-light': {
          primary: 'rgb(34 197 94)', // green-500
          accent: 'rgb(132 204 22)', // lime-500
          background: 'rgb(240 253 244)', // green-50
          card: 'rgb(220 252 231)', // green-100
          text: 'rgb(20 83 45)', // green-900
        },
        'forest-dark': {
          primary: 'rgb(22 163 74)', // green-600
          accent: 'rgb(101 163 13)', // lime-600
          background: 'rgb(6 78 59)', // emerald-900
          card: 'rgb(6 95 70)', // emerald-800
          text: 'rgb(187 247 208)', // green-200
        },

        // Theme 6: Royal Plum
        'royal-light': {
          primary: 'rgb(168 85 247)', // purple-500
          accent: 'rgb(236 72 153)', // pink-500
          background: 'rgb(250 245 255)', // purple-50
          card: 'rgb(243 232 255)', // purple-100
          text: 'rgb(88 28 135)', // purple-900
        },
        'royal-dark': {
          primary: 'rgb(147 51 234)', // purple-600
          accent: 'rgb(219 39 119)', // pink-600
          background: 'rgb(49 46 129)', // indigo-900
          card: 'rgb(55 48 163)', // indigo-800
          text: 'rgb(196 181 253)', // purple-200
        },

        // Theme 7: Steel & Slate
        'steel-light': {
          primary: 'rgb(107 114 128)', // gray-500
          accent: 'rgb(156 163 175)', // gray-400
          background: 'rgb(249 250 251)', // gray-50
          card: 'rgb(243 244 246)', // gray-100
          text: 'rgb(17 24 39)', // gray-900
        },
        'steel-dark': {
          primary: 'rgb(75 85 99)', // gray-600
          accent: 'rgb(107 114 128)', // gray-500
          background: 'rgb(17 24 39)', // gray-900
          card: 'rgb(31 41 55)', // gray-800
          text: 'rgb(243 244 246)', // gray-100
        },

        // Dynamic theme colors (will be set via CSS variables)
        primary: 'rgb(var(--color-primary) / <alpha-value>)',
        accent: 'rgb(var(--color-accent) / <alpha-value>)',
        background: 'rgb(var(--color-background) / <alpha-value>)',
        card: 'rgb(var(--color-card) / <alpha-value>)',
        text: 'rgb(var(--color-text) / <alpha-value>)',
        
        // Additional semantic colors
        'text-secondary': 'rgb(var(--color-text-secondary) / <alpha-value>)',
        'text-muted': 'rgb(var(--color-text-muted) / <alpha-value>)',
        'border-primary': 'rgb(var(--color-border-primary) / <alpha-value>)',
        'border-secondary': 'rgb(var(--color-border-secondary) / <alpha-value>)',
        'surface-hover': 'rgb(var(--color-surface-hover) / <alpha-value>)',
        danger: 'rgb(var(--color-danger) / <alpha-value>)',
        success: 'rgb(var(--color-success) / <alpha-value>)',
        warning: 'rgb(var(--color-warning) / <alpha-value>)',
      },
    },
  },
  plugins: [],
}
