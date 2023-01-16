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
      spacing: {
        'nav': '36px'
      }
    },
    screens: {
      'xs': '320px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
    }
  },
  variants: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
