import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { VantResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    Components({
      resolvers: [VantResolver()],
    }),
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      // 这里的 /api 会匹配你代码里的 axios.get('/api/...')
      '/api': {
        target: 'http://127.0.0.1:8000', // 确保指向你的 Python 后端
        changeOrigin: true,
        // 不要写 rewrite，因为我们的后端路径本身就带有 /api
      },
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
      }
    }
  }
})