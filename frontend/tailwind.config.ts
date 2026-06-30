import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        civet: {
          background: "#fff8f6",
          surface: "#ffffff",
          surfaceLow: "#fff1ed",
          surfaceContainer: "#ffe9e3",
          outline: "#827472",
          outlineVariant: "#d3c3c0",
          ink: "#2c160e",
          muted: "#504442",
          espresso: "#271310",
          latte: "#ece0dc",
          sage: "#6f8f65",
          terracotta: "#ba1a1a"
        }
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Lexend", "Inter", "ui-sans-serif", "system-ui", "sans-serif"]
      }
    }
  },
  plugins: []
} satisfies Config;
