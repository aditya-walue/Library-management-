import path from "node:path"
import vue from "@vitejs/plugin-vue"
import frappeui from "frappe-ui/vite"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [
    frappeui({
      frappeProxy: true,
      jinjaBootData: true,
      buildConfig: {
        outDir: "../library_management/public/frontend",
        indexHtmlPath: "../library_management/www/library.html",
        emptyOutDir: true,
      },
    }),
    vue(),
  ],
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
  optimizeDeps: {
    include: ["feather-icons", "showdown", "highlight.js/lib/core", "interactjs"],
    exclude: ["frappe-ui"],
  },
  server: { allowedHosts: true },
})
