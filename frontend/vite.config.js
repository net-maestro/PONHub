import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  base: './',
  plugins: [
    vue(),
    vueDevTools(),
  ],
  build: {
    outDir: '/www/service/abonents/netcontrol',
    emptyOutDir: true,

    rollupOptions: {
    output: {
      manualChunks: undefined,
      inlineDynamicImports: true
    }
  }

  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
   server: {
    host: '0.0.0.0', // Доступен по локальному IP (192.168.x.x)
    port: 3500, // Порт приложения
    strictPort: true, // Не менять порт, если 3500 занят
    hmr: {
      host: 'localhost', // Корректная работа HMR при доступе через IP
      protocol: 'ws', // Явное указание WebSocket
    },
  },
})
