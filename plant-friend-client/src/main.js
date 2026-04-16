import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import axios from 'axios';
import { NavBar } from 'vant';
import 'vant/lib/index.css';

// In dev, force relative API paths so Vite proxy (/api -> 127.0.0.1:8000) is always used.
// In prod, allow explicit base URL via VITE_API_BASE_URL.
const apiBase = (import.meta.env.VITE_API_BASE_URL || '').trim();
if (!import.meta.env.DEV && apiBase) {
  axios.defaults.baseURL = apiBase;
}

document.title = '我的植物朋友';

const app = createApp(App);
const pinia = createPinia();

app.config.globalProperties.$http = axios;
app.use(pinia);
app.use(NavBar);
app.mount('#app');
