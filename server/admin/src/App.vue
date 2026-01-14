<script setup lang="ts">
import { h, onMounted, computed, ref, watch } from 'vue'
import { RouterView, useRouter, useRoute } from 'vue-router'
import {
  NLayout,
  NLayoutSider,
  NLayoutHeader,
  NLayoutContent,
  NMenu,
  NAvatar,
  NDropdown,
  NConfigProvider,
  NMessageProvider,
  NDialogProvider,
  NGlobalStyle,
  zhCN,
  dateZhCN,
  type GlobalThemeOverrides,
  type MenuOption
} from 'naive-ui'
import { useAuthStore } from './stores/auth'
import adminAvatar from './assets/admin-avatar.png'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isDark = ref(localStorage.getItem('admin-theme') !== 'light')

const themeOverrides = computed<GlobalThemeOverrides>(() => ({
  common: {
    primaryColor: '#7AA2F7',
    primaryColorHover: '#89DDFF',
    primaryColorPressed: '#5D87D6',
    borderRadius: '8px',
  },
  Layout: {
    color: 'transparent',
    headerColor: 'transparent',
    siderColor: isDark.value ? 'rgba(15, 17, 23, 0.85)' : 'rgba(255, 255, 255, 0.9)',
  },
  DataTable: {
    tdColor: 'transparent',
    thColor: isDark.value ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)',
    thTextColor: isDark.value ? '#c4a47c' : '#2d3748',
    tdTextColor: isDark.value ? '#e2e8f0' : '#1a202c',
    borderColor: isDark.value ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)',
    thFontWeight: '800',
  },
  Card: {
    color: isDark.value ? 'rgba(20, 23, 28, 0.6)' : 'rgba(255, 255, 255, 0.8)',
    borderColor: isDark.value ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)',
    titleTextColor: isDark.value ? '#c4a47c' : '#2d3748',
  },
  Menu: {
    itemTextColor: isDark.value ? '#e2e8f0' : '#4a5568',
    itemTextColorHover: '#7AA2F7',
    itemTextColorActive: '#7AA2F7',
    itemIconColor: isDark.value ? '#a0aec0' : '#718096',
    itemIconColorHover: '#7AA2F7',
    itemIconColorActive: '#7AA2F7',
    color: 'transparent',
  },
  Button: {
    textColor: isDark.value ? '#e2e8f0' : '#1a202c',
    textColorPrimary: '#ffffff',
    textColorHoverPrimary: '#ffffff',
    textColorPressedPrimary: '#ffffff',
    textColorFocusPrimary: '#ffffff',
    textColorHover: '#7AA2F7',
  },
  Drawer: {
    color: isDark.value ? '#1e2229' : '#ffffff',
    titleTextColor: isDark.value ? '#e2e8f0' : '#1a202c',
    bodyPadding: '0',
  }
}))

function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem('admin-theme', isDark.value ? 'dark' : 'light')
}

const menuOptions: MenuOption[] = [
  { label: '仪表盘', key: '/', icon: () => h('span', '📊') },
  { label: '文章管理', key: '/posts', icon: () => h('span', '📝') },
  { label: '分类管理', key: '/categories', icon: () => h('span', '📁') },
  { label: '标签管理', key: '/tags', icon: () => h('span', '🏷️') },
  { label: '评论管理', key: '/comments', icon: () => h('span', '💬') },
  { label: '工具收藏', key: '/tools', icon: () => h('span', '🛠️') },
  { label: '相册管理', key: '/albums', icon: () => h('span', '📷') },
  { label: '友链管理', key: '/friends', icon: () => h('span', '🔗') },
  { label: 'Banner', key: '/banner', icon: () => h('span', '🖼️') },
  { label: '关于页面', key: '/about', icon: () => h('span', '👤') }
]

const sidebarOpen = ref(false)
const userOptions = computed(() => [
  { label: isDark.value ? '白天模式' : '夜间模式', key: 'theme' },
  { label: '退出登录', key: 'logout' }
])

const selectedKey = computed(() => {
  if (route.path.startsWith('/posts')) return '/posts'
  return route.path
})

function handleMenuSelect(key: string) {
  router.push(key)
  sidebarOpen.value = false
}

function handleUserSelect(key: string) {
  if (key === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (key === 'theme') {
    toggleTheme()
  }
}

onMounted(() => {
  if (authStore.isLoggedIn) authStore.fetchUser()
  // 初始应用主题类
  updateThemeClass()
})

const themeClass = computed(() => isDark.value ? 'dark-mode' : 'light-mode')

function updateThemeClass() {
  document.documentElement.className = themeClass.value
}

// 监听主题变化
watch(isDark, updateThemeClass)
</script>

<template>
  <n-config-provider 
    :locale="zhCN" 
    :date-locale="dateZhCN" 
    :theme-overrides="themeOverrides"
  >
    <n-global-style />
    <n-message-provider>
      <n-dialog-provider>
        <div class="app-background"></div>
        
        <template v-if="route.path === '/login'">
          <RouterView />
        </template>
        
        <n-layout v-else has-sider style="height: 100vh" class="main-layout">
          <!-- 桌面端侧边栏 -->
          <n-layout-sider
            bordered
            :width="240"
            :native-scrollbar="false"
            class="glass-sider hide-on-mobile"
          >
            <div class="logo">
              <div class="logo-text">AVIDS2</div>
              <div class="logo-sub">管理面板</div>
            </div>
            <n-menu
              :value="selectedKey"
              :options="menuOptions"
              @update:value="handleMenuSelect"
              style="padding: 12px"
            />
          </n-layout-sider>

          <!-- 移动端侧边抽屉 -->
          <n-drawer v-model:show="sidebarOpen" :width="280" placement="left" class="mobile-drawer">
            <n-drawer-content title="导航菜单" closable>
              <n-menu
                :value="selectedKey"
                :options="menuOptions"
                @update:value="handleMenuSelect"
              />
            </n-drawer-content>
          </n-drawer>
          
          <n-layout class="content-layout">
            <n-layout-header class="app-header">
              <div class="header-content">
                <div class="left-section">
                  <n-button class="mobile-nav-toggle show-on-mobile" quaternary circle @click="sidebarOpen = true">
                    <template #icon>☰</template>
                  </n-button>
                  <div class="page-title">{{ route.meta.title || route.name }}</div>
                </div>
                <div class="header-right">
                  <n-space align="center">
                    <n-button quaternary circle @click="toggleTheme" class="theme-toggle">
                      <template #icon>{{ isDark ? '🌞' : '🌙' }}</template>
                    </n-button>
                    <n-dropdown :options="userOptions" @select="handleUserSelect">
                      <n-avatar 
                        round 
                        size="small" 
                        :src="adminAvatar"
                        class="user-avatar-glow"
                      >
                        {{ authStore.user?.username?.charAt(0).toUpperCase() || 'A' }}
                      </n-avatar>
                    </n-dropdown>
                  </n-space>
                </div>
              </div>
            </n-layout-header>

            <n-layout-content class="main-content-area" :native-scrollbar="false">
              <div class="content-wrapper">
                <RouterView v-slot="{ Component }">
                  <transition name="page-fade" mode="out-in">
                    <component :is="Component" />
                  </transition>
                </RouterView>
              </div>
            </n-layout-content>
          </n-layout>
        </n-layout>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;900&display=swap');

:root {
  --wf-bg: #0a0b0e;
  --wf-card: #1e2229;
  --wf-accent: #c4a47c;
  --wf-accent-dim: rgba(196, 164, 124, 0.2);
  --wf-text: #ffffff;
  --wf-text-dim: #a0aec0;
  --wf-border: rgba(255, 255, 255, 0.15);
}

.light-mode {
  --wf-bg: #f3f4f6;
  --wf-card: #ffffff;
  --wf-accent: #1f2937;
  --wf-accent-dim: rgba(31, 41, 55, 0.1);
  --wf-text: #111827;
  --wf-text-dim: #64748b;
  --wf-border: rgba(0, 0, 0, 0.08);
}

body {
  margin: 0;
  font-family: 'Outfit', sans-serif;
  background-color: var(--wf-bg);
  color: var(--wf-text);
  overflow: hidden;
  transition: background-color 0.3s, color 0.3s;
}

/* 背景渲染 */
.app-background {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: -1;
  transition: opacity 0.5s;
}

.dark-mode .app-background {
  background: 
    radial-gradient(at 0% 0%, rgba(196, 164, 124, 0.08) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(122, 162, 247, 0.08) 0px, transparent 50%),
    #08090b;
}

.light-mode .app-background {
  background: #f0f2f5;
}

/* 布局修正 */
.main-layout {
  background: transparent !important;
}

.content-layout {
  background: transparent !important;
}

.app-header {
  background: var(--wf-card) !important;
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
  height: calc(60px + env(safe-area-inset-top, 0px)) !important;
  padding-top: env(safe-area-inset-top, 0px) !important;
  transition: background 0.3s;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  height: 100%;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.left-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 2px;
  color: var(--wf-accent);
}

.main-content-area {
  padding: 0;
}

.content-wrapper {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 侧边栏样式 */
.glass-sider {
  background: var(--wf-card) !important;
  backdrop-filter: blur(12px);
  border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}

.logo {
  padding: 32px 24px;
}

.logo-text {
  font-size: 24px;
  font-weight: 900;
  color: var(--wf-text);
  letter-spacing: 1.5px;
}

.logo-sub {
  font-size: 10px;
  color: var(--wf-accent);
  letter-spacing: 2px;
  opacity: 0.8;
}

/* Table 背景修正：彻底解决大白条问题 */
:deep(.n-data-table) {
  background-color: transparent !important;
}
:deep(.n-data-table .n-data-table-wrapper) {
  background-color: var(--wf-card) !important;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
:deep(.n-data-table-base-table-header) {
  border-radius: 12px 12px 0 0 !important;
}

/* 移动端菜单切换 */
@media (max-width: 768px) {
  .hide-on-mobile { display: none !important; }
  .show-on-mobile { display: flex !important; }
  
  .content-wrapper {
    padding: 16px;
    padding-bottom: calc(16px + env(safe-area-inset-bottom, 0px));
  }
  
  /* 修复移动端导航栏重叠 */
  .app-header {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 1000 !important;
  }
  
  .main-content-area {
    margin-top: calc(60px + env(safe-area-inset-top, 0px)) !important;
  }
}

/* 抽屉菜单安全区域 */
:deep(.n-drawer-header) {
  padding-top: calc(16px + env(safe-area-inset-top, 0px)) !important;
}

:deep(.n-drawer-body-content-wrapper) {
  padding-bottom: env(safe-area-inset-bottom, 0px) !important;
}

/* 页面过渡 */
.page-fade-enter-active, .page-fade-leave-active {
  transition: opacity 0.2s;
}
.page-fade-enter-from, .page-fade-leave-to {
  opacity: 0;
}
</style>
