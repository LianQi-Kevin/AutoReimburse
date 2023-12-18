import {createApp} from 'vue';
import './style.css';
import App from './App.vue';
// to support element style
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

// 创建vue实例
const app = createApp(App);

// 绑定APP.vue到DOM
app.mount('#app');

