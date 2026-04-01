import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import axios from 'axios'


// 引入 Vant 全局样式
import 'vant/lib/index.css'

const app = createApp(App)
const pinia = createPinia()

// 2. 配置后端 cpolar 公网地址 (替换为你自己的后端 cpolar 域名)
// 注意：末尾不要带斜杠
axios.defaults.baseURL = 'https://59a7106f.r35.cpolar.top'; 
axios.defaults.baseURL = 'http://192.168.100.102:8000';
//axios.defaults.baseURL = 'http://127.0.0.1:8000';

// 3. 为了方便在组件中使用，也可以挂载到全局（可选）
app.config.globalProperties.$http = axios


// 确保状态管理库在应用挂载前被注入
app.use(pinia)

app.mount('#app')