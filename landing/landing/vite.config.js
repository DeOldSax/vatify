// vite.config.js
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        blog: resolve(__dirname, 'blog.html'),
        imprint: resolve(__dirname, 'imprint.html'),
        privacy: resolve(__dirname, 'privacy.html'),
        alternatives: resolve(__dirname, 'alternatives.html'),
        comparison: resolve(__dirname, 'comparison.html'),
      },
    },
  },
})
