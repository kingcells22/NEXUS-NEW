import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // Busca el token en el navegador por si refrescas la página
    token: localStorage.getItem('nexus_token') || null,
    rol: localStorage.getItem('nexus_rol') || null,
  }),
  actions: {
    async loginUser(correo: string, password: string) {
      // FastAPI exige que los datos vayan en formato Form-UrlEncoded
      const formData = new URLSearchParams()
      formData.append('username', correo)
      formData.append('password', password)

      try {
        // Asegúrate de que esta URL apunte a donde está corriendo tu backend de Python
        const response = await axios.post('http://127.0.0.1:8000/api/login', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        })

        // Guardamos las credenciales en la memoria de Vue
        this.token = response.data.access_token
        this.rol = response.data.rol

        // Las guardamos en el disco duro del navegador para no perderlas
        localStorage.setItem('nexus_token', this.token)
        localStorage.setItem('nexus_rol', this.rol)

        return true
      } catch (error) {
        this.token = null
        this.rol = null
        localStorage.removeItem('nexus_token')
        localStorage.removeItem('nexus_rol')
        throw error // Lanza el error para que el formulario muestre la alerta roja
      }
    },
    logout() {
      this.token = null
      this.rol = null
      localStorage.removeItem('nexus_token')
      localStorage.removeItem('nexus_rol')
    }
  }
})