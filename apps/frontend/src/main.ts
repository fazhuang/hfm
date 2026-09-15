import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'
import './styles/tokens.css'
import './styles/foundations.css'
import './styles/home-scale.css'
import './styles/portal-column.css'

createApp(App).use(createPinia()).use(router).mount('#app')
