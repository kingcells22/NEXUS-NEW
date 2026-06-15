import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import RedactarMemorandum from '../views/RedactarMemorandum.vue' // <-- 1. Importamos la nueva vista

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView
    },
    {
      path: '/registro',
      name: 'registro',
      component: RegisterView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue')
    },
    // --- 2. Agregamos la ruta del Memorándum ---
    {
      path: '/redactar-memo',
      name: 'redactar-memorandum',
      component: RedactarMemorandum
    }
  ]
})

export default router