import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    allowedHosts: [
      '2f3f-2401-4900-67b8-bbbd-e0ca-a3f5-e94f-1e67.ngrok-free.app'
    ],
  }
});
