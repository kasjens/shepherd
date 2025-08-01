/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Terminal-inspired theme colors from THEME_DESIGN.md
        'terminal-black': '#1a1d21',
        'command-gray': '#2c3136',
        'border-gray': '#495057',
        'prompt-white': '#f8f9fa',
        'muted-gray': '#adb5bd',
        'shepherd-blue': '#0969da',
        'success-green': '#2da44e',
        'warning-amber': '#fb8500',
        'error-red': '#cf222e',
      },
      fontFamily: {
        'sans': ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        'mono': ['SF Mono', 'Monaco', 'Cascadia Code', 'monospace'],
      },
    },
  },
  plugins: [],
}