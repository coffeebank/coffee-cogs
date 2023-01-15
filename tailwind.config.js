/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx,md,mdx}",
    "./content/**/*.{js,jsx,ts,tsx,md,mdx}",
    "./static/**/*.{js,jsx,ts,tsx,md,mdx}"
  ],
  darkMode: 'class', // bool, 'media', or 'class'
  theme: {
    extend: {
      colors: {
        'fcfcfc': '#fcfcfc',
        'gray-150': '#EEEFF2',
        'gray-175': '#E9EBEE',
        'discord-bg-primary': '#36393f'
      },
      screens: {
        'xs': '320px'
      },
    }
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
