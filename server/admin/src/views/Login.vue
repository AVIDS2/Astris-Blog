<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    message.warning('请输入用户名和密码')
    return
  }
  
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    message.success('Welcome aboard, Captain. 🏴‍☠️')
    router.push('/')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card glass-panel">
      <div class="login-header">
        <div class="logo-text">D.Will</div>
        <p>The Will of Freedom</p>
      </div>
      
      <n-form @submit.prevent="handleLogin" size="large">
        <n-form-item :show-label="false">
          <n-input
            v-model:value="username"
            placeholder="Username"
            class="glass-input"
            round
          >
            <template #prefix>👤</template>
          </n-input>
        </n-form-item>
        
        <n-form-item :show-label="false">
          <n-input
            v-model:value="password"
            type="password"
            placeholder="Password"
            show-password-on="click"
            class="glass-input"
            round
            @keyup.enter="handleLogin"
          >
            <template #prefix>🔒</template>
          </n-input>
        </n-form-item>
        
        <n-button
          type="primary"
          size="large"
          block
          round
          :loading="loading"
          @click="handleLogin"
          class="login-btn"
        >
          登 录
        </n-button>
      </n-form>
      
      <div class="footer-text">
        Powered by Astro & FastAPI
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Pirata+One&display=swap');

.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 独立的更梦幻的背景，或者直接复用全局背景 */
}

.glass-panel {
  width: 380px;
  padding: 48px;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(25px) saturate(180%);
  -webkit-backdrop-filter: blur(25px) saturate(180%);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.06);
  animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-text {
  font-family: 'Pirata One', cursive;
  font-size: 56px;
  color: #2d3748;
  margin-bottom: 8px;
  text-shadow: 3px 3px 0px rgba(0,0,0,0.1);
}

.login-header p {
  color: #718096;
  margin: 0;
  font-size: 14px;
  letter-spacing: 2px;
  text-transform: uppercase;
  font-weight: 600;
}

/* 覆盖 input 样式为透明风格 */
:deep(.n-input) {
  background-color: rgba(255, 255, 255, 0.5) !important;
  border: 1px solid transparent;
  transition: all 0.3s;
}

:deep(.n-input:hover), :deep(.n-input:focus-within) {
  background-color: rgba(255, 255, 255, 0.8) !important;
  box-shadow: 0 0 0 2px rgba(122, 162, 247, 0.2);
}

.login-btn {
  margin-top: 12px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 14px rgba(122, 162, 247, 0.4);
}

.footer-text {
  margin-top: 32px;
  text-align: center;
  font-size: 12px;
  color: #a0aec0;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
