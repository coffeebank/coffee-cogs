/** @type {import('tailwindcss').Config} */
module.exports = {
  corePlugins: {
    preflight: false,
  },
  content: [
    "./src/pages/**/*.{js,jsx,ts,tsx,md,mdx}",
    "./src/components/**/*.{js,jsx,ts,tsx,md,mdx}",
    "./src/docs/**/*.{js,jsx,ts,tsx,md,mdx}",
    "./src/**/*.{js,jsx,ts,tsx,md,mdx}"
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
      minHeight: {
        '5r': '5rem',
      },
      screens: {
        'xs': '320px',
        'sidebar': '719px',
      },
    }
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
