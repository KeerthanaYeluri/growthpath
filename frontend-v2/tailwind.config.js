/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        fadeIn: {
          from: { opacity: '0', transform: 'translateY(12px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        pulseRing: {
          '0%': { transform: 'scale(1)', opacity: '0.6' },
          '100%': { transform: 'scale(2.2)', opacity: '0' },
        },
        bounce: {
          '0%,80%,100%': { transform: 'translateY(0)' },
          '40%': { transform: 'translateY(-8px)' },
        },
        micWave: {
          '0%,100%': { height: '12px' },
          '50%': { height: '28px' },
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'pulse-ring': 'pulseRing 1.5s ease-out infinite',
        'bounce-dot': 'bounce 1.4s ease-in-out infinite',
        'mic-wave': 'micWave 1s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
