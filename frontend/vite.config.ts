import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    // Proxy API calls to the FastAPI backend in dev (no CORS, downloads work same-origin).
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
