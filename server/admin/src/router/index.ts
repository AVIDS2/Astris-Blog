import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('../views/Login.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/posts',
        name: 'Posts',
        component: () => import('../views/Posts.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/posts/new',
        name: 'NewPost',
        component: () => import('../views/PostEdit.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/posts/:id/edit',
        name: 'EditPost',
        component: () => import('../views/PostEdit.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/categories',
        name: 'Categories',
        component: () => import('../views/Categories.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/tags',
        name: 'Tags',
        component: () => import('../views/Tags.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/comments',
        name: 'Comments',
        component: () => import('../views/Comments.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/tools',
        name: 'Tools',
        component: () => import('../views/Tools.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/albums',
        name: 'Albums',
        component: () => import('../views/Albums.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/about',
        name: 'About',
        component: () => import('../views/About.vue'),
        meta: { requiresAuth: true, title: '关于页面' }
    },
    {
        path: '/banner',
        name: 'Banner',
        component: () => import('../views/Banner.vue'),
        meta: { requiresAuth: true, title: 'Banner 管理' }
    },
    {
        path: '/friends',
        name: 'Friends',
        component: () => import('../views/Friends.vue'),
        meta: { requiresAuth: true, title: '友链管理' }
    }
]

const router = createRouter({
    history: createWebHistory('/admin'),
    routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
    const authStore = useAuthStore()

    if (to.meta.requiresAuth && !authStore.isLoggedIn) {
        next('/login')
    } else if (to.path === '/login' && authStore.isLoggedIn) {
        next('/')
    } else {
        next()
    }
})

export default router
