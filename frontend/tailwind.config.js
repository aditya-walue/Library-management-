import frappeUIPreset from "frappe-ui/tailwind"

export default {
  presets: [frappeUIPreset],
  content: [
    "./index.html",
    "./src/**/*.{vue,js}",
    "./node_modules/frappe-ui/src/components/**/*.{vue,js,ts}",
  ],
  theme: {
    extend: {
      colors: {
        room: { DEFAULT: "#1F3A2E", deep: "#172C23", soft: "#E9EFEB" },
        paper: { DEFAULT: "#F7F7F5", line: "#E7E7E3" },
        ink: { DEFAULT: "#1A1D1B", muted: "#5C625E", faint: "#8A8F8B" },
        brick: { DEFAULT: "#A33A2B", soft: "#F6E6E3" },
      },
      fontFamily: {
        display: ['"Newsreader"', "Georgia", "serif"],
        ui: ['"Hanken Grotesk"', "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
}
