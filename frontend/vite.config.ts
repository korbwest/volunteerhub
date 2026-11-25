import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8080',
      '/docs': 'http://127.0.0.1:8080',
      '/openapi.json': 'http://127.0.0.1:8080',
    },
  },
  test: {
    environment: 'jsdom', setupFiles: ['./src/test-setup.ts'],
    coverage: { provider: 'v8', reporter: ['text', 'json-summary', 'lcov'], include: ['src/**/*.{ts,tsx}'], exclude: ['src/**/*.test.*', 'src/test-setup.ts', 'src/main.tsx', 'src/types.ts'] },
  },
});
