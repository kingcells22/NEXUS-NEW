import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import RecuperarPasswordView from '../views/RecuperarPasswordView.vue'
import DashboardView from '../views/DashboardView.vue'
import EmitidosView from '../views/EmitidosView.vue' // <-- 1. Importamos la bandeja
import RedactarMemorandum from '../views/RedactarMemorandum.vue' // <-- 2. Importamos el formulario

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
      path: '/recuperar-password',
      name: 'recuperar-password',
      component: RecuperarPasswordView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      children: [
        // Todo lo que esté aquí adentro se abrirá en el espacio central de tu Dashboard
        {
          path: 'emitidos',
          name: 'emitidos',
          component: EmitidosView
        },
        {
          path: 'usuarios/crear',
          name: 'crear-usuario',
          component: () => import('../views/CrearUsuarioView.vue')
        },
        {
          path: 'usuarios',
          name: 'usuarios',
          component: () => import('../views/UsuariosView.vue') // Luego crearemos este archivo
        },
        {
          path: 'redactar-memo',
          name: 'redactar-memorandum',
          component: RedactarMemorandum
        }
      ]
    }
  ]
})

export default router