import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

// 引入 Vant 全局样式
import 'vant/lib/index.css'

const app = createApp(App)
const pinia = createPinia()

// 确保状态管理库在应用挂载前被注入
app.use(pinia)

app.mount('#app')