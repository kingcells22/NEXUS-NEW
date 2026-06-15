import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router' // <-- Importamos el router
import App from './App.vue'
import './style.css'

const app = createApp(App)

app.use(createPinia())
app.use(router) // <-- Lo encendemos

app.mount('#app')