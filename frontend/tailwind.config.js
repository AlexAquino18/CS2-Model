/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{js,jsx}',
    './components/**/*.{js,jsx}',
    './app/**/*.{js,jsx}',
    './src/**/*.{js,jsx}',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "#1F1F1F",
        input: "#121212",
        ring: "#DE9B35",
        background: "#050505",
        foreground: "#EDEDED",
        primary: {
          DEFAULT: "#DE9B35",
          foreground: "#000000",
        },
        secondary: {
          DEFAULT: "#5D79AE",
          foreground: "#FFFFFF",
        },
        destructive: {
          DEFAULT: "#FF4444",
          foreground: "#FFFFFF",
        },
        muted: {
          DEFAULT: "#1A1A1A",
          foreground: "#888888",
        },
        accent: {
          DEFAULT: "#CCFF00",
          foreground: "#000000",
        },
        popover: {
          DEFAULT: "#0A0A0A",
          foreground: "#EDEDED",
        },
        card: {
          DEFAULT: "#0A0A0A",
          foreground: "#FFFFFF",
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['Unbounded', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        lg: "0.25rem",
        md: "0.25rem",
        sm: "0.125rem",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "pulse-glow": {
          "0%, 100%": { boxShadow: "0 0 20px -5px rgba(222, 155, 53, 0.3)" },
          "50%": { boxShadow: "0 0 30px -5px rgba(222, 155, 53, 0.6)" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}