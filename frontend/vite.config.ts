import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    esbuildOptions: {
      loader: {
        '.js': 'jsx',
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
  server: {
    port: 3000,
    headers: {
      'Content-Security-Policy': "script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval';",
    },
    proxy: {
      '/v1': {
        target: 'http://backend:5030',
        changeOrigin: true,
      }
    }
  }
})