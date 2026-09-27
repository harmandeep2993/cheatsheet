// Vite config. In development the browser talks only to Vite (port 5173);
// Vite forwards /api to the Nginx proxy (port 8080), exactly like production, so no CORS setup is needed.
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8080",
    },
  },
});
