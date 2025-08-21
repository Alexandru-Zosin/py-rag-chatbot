import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// For local dev only: you can uncomment the proxy below to forward /api to localhost:8080.
// In production, nginx inside the container already proxies /api to chatbot_api:8080.
//
// server: { proxy: { "/api": "http://localhost:8080" } }

export default defineConfig({
  plugins: [react()],
});
