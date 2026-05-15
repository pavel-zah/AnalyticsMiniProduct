/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['SF Pro Display', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
      },
      colors: {
        'primary-blue': '#007AFF',
        'light-gray': '#F5F5F7',
        'border-gray': '#E5E5EA',
        'text-secondary': '#8E8E93',
      },
      spacing: {
        'section': '24px',
        'content': '16px',
      },
      borderRadius: {
        'xl': '16px',
        '2xl': '20px',
      },
      maxWidth: {
        'content': '680px',
      },
    },
  },
  plugins: [],
}
