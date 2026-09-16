/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f4f1ec",
          100: "#e8e2d8",
          200: "#d4cbbd",
          400: "#8a7d6b",
          500: "#5c5348",
          600: "#3f3a34",
          700: "#2c2824",
          800: "#1c1917",
        },
      },
      boxShadow: {
        card: "0 1px 2px rgba(28, 25, 23, 0.04), 0 12px 32px rgba(28, 25, 23, 0.06)",
      },
    },
  },
  plugins: [],
};
