import axios from 'axios'
import { useAuthStore } from '../stores/auth'

// 只有在 localhost 开发时才使用 8000 端口，其他情况使用相对路径
const isLocalDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
const apiBase = isLocalDev ? `http://${window.location.hostname}:8000` : ''

export const api = axios.create({
    baseURL: apiBase,
    timeout: 10000
})

// 请求拦截器 - 添加 Token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

// 响应拦截器 - 处理错误
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            const authStore = useAuthStore()
            authStore.logout()
            window.location.href = '/admin/login'
        }
        return Promise.reject(error)
    }
)

// API 接口封装
export const postsApi = {
    getAll: () => api.get('/api/admin/posts'),
    create: (data: any) => api.post('/api/admin/posts', data),
    update: (id: number, data: any) => api.put(`/api/admin/posts/${id}`, data),
    delete: (id: number) => api.delete(`/api/admin/posts/${id}`)
}

export const categoriesApi = {
    getAll: () => api.get('/api/categories'),
    create: (data: any) => api.post('/api/admin/categories', data),
    delete: (id: number) => api.delete(`/api/admin/categories/${id}`)
}

export const tagsApi = {
    getAll: () => api.get('/api/tags'),
    create: (data: any) => api.post('/api/admin/tags', data),
    delete: (id: number) => api.delete(`/api/admin/tags/${id}`)
}

export const commentsApi = {
    getAll: (approved?: boolean) => api.get('/api/admin/comments', { params: { approved } }),
    approve: (id: number) => api.put(`/api/admin/comments/${id}/approve`),
    delete: (id: number) => api.delete(`/api/admin/comments/${id}`)
}

export const statsApi = {
    get: () => api.get('/api/stats')
}
