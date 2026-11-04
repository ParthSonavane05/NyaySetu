/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        obsidian: '#0B0D10',
        graphite: '#171B21',
        'slate-glass': 'rgba(41, 46, 53, 0.65)',
        'light-gray': '#E9E7E2',
        'muted-gray': '#9299A2',
        champagne: '#827760',
        titanium: '#A9A297',
      },
      borderColor: {
        hairline: 'rgba(169, 162, 151, 0.14)',
      }
    },
  },
  plugins: [],
}
