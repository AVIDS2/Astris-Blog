import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../api'

interface User {
    id: number
    username: string
    email: string | null
    avatar: string | null
}

export const useAuthStore = defineStore('auth', () => {
    const token = ref<string | null>(localStorage.getItem('token'))
    const user = ref<User | null>(null)

    const isLoggedIn = computed(() => !!token.value)

    async function login(username: string, password: string) {
        const formData = new FormData()
        formData.append('username', username)
        formData.append('password', password)

        const response = await api.post('/api/admin/auth/login', formData)
        token.value = response.data.access_token
        localStorage.setItem('token', response.data.access_token)

        // 获取用户信息
        await fetchUser()
    }

    async function fetchUser() {
        if (!token.value) return
        try {
            const response = await api.get('/api/admin/auth/me')
            user.value = response.data
        } catch {
            logout()
        }
    }

    function logout() {
        token.value = null
        user.value = null
        localStorage.removeItem('token')
    }

    return {
        token,
        user,
        isLoggedIn,
        login,
        fetchUser,
        logout
    }
})
