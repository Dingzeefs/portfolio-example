/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        matcha: {
          100: '#e8f5e9',  // Lightest green (text highlights)
          300: '#a5d6a7',  // Soft green (accents)
          500: '#4caf50',  // Standard green
          800: '#2e7d32',  // Rich green
          900: '#1b5e20',  // Deepest green (old primary)
        },
        // New Luxury Dark Theme Colors
        'forest-dark': '#0F1C15',    // Main Background (Very dark green)
        'forest-card': '#1A2F23',    // Card Background
        'forest-light': '#2D4A35',   // Card Hover / Borders
        'luxury-gold': '#D4C4A8',    // Primary Text / Accents
        'luxury-cream': '#F0E6D2',   // Secondary Text
      },
      fontFamily: {
        serif: ['Georgia', 'Cambria', 'Times New Roman', 'serif'],
        mono: ['Courier New', 'Courier', 'monospace'],
      },
      animation: {
        'spin-slow': 'spin 8s linear infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}
