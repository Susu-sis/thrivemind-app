/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        background: '#0f172a',
        foreground: '#f1f5f9',
        card: '#1e293b',
        border: '#334155',
        accent: '#8b5cf6',
      },
    },
  },
  plugins: [],
};
