<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useMessage, NUpload } from 'naive-ui'
import { api } from '../api'
import type { UploadFileInfo } from 'naive-ui'

const message = useMessage()

const loading = ref(false)
const desktopBanners = ref<string[]>([])
const mobileBanners = ref<string[]>([])
const activeTab = ref<'desktop' | 'mobile'>('desktop')

const currentBanners = computed(() => 
  activeTab.value === 'desktop' ? desktopBanners.value : mobileBanners.value
)

const bannerBasePath = computed(() => 
  activeTab.value === 'desktop' ? '/assets/desktop-banner/' : '/assets/mobile-banner/'
)

async function fetchBanners() {
  loading.value = true
  try {
    const response = await api.get('/api/admin/banner')
    desktopBanners.value = response.data.desktop
    mobileBanners.value = response.data.mobile
  } catch (error) {
    message.error('获取 Banner 列表失败')
  } finally {
    loading.value = false
  }
}

async function handleUpload({ file }: { file: UploadFileInfo }) {
  if (!file.file) return
  
  const formData = new FormData()
  formData.append('file', file.file)
  
  try {
    await api.post(`/api/admin/banner/upload/${activeTab.value}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    message.success('上传成功')
    fetchBanners()
  } catch (error) {
    message.error('上传失败')
  }
}

async function deleteBanner(filename: string) {
  try {
    await api.delete(`/api/admin/banner/${activeTab.value}/${filename}`)
    message.success('删除成功')
    fetchBanners()
  } catch (error) {
    message.error('删除失败')
  }
}

const API_BASE = `http://${window.location.hostname}:8000`

onMounted(fetchBanners)
</script>

<template>
  <div class="banner-page">
    <div class="page-header">
      <div class="header-info">
        <h1>Banner 管理</h1>
        <p class="sub-label">管理首页轮播横幅图片，支持桌面端和移动端分开配置</p>
      </div>
    </div>

    <!-- 设备切换 -->
    <div class="tab-switcher">
      <button 
        :class="['tab-btn', { active: activeTab === 'desktop' }]"
        @click="activeTab = 'desktop'"
      >
        🖥️ 桌面端 ({{ desktopBanners.length }})
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'mobile' }]"
        @click="activeTab = 'mobile'"
      >
        📱 移动端 ({{ mobileBanners.length }})
      </button>
    </div>

    <n-spin :show="loading">
      <!-- 上传区域 -->
      <div class="upload-section">
        <n-upload
          accept="image/*"
          :show-file-list="false"
          :custom-request="({ file }) => handleUpload({ file })"
        >
          <div class="upload-trigger">
            <span class="upload-icon">📤</span>
            <span>点击或拖拽上传{{ activeTab === 'desktop' ? '桌面端' : '移动端' }} Banner</span>
            <span class="upload-hint">支持 JPG / PNG / WebP / GIF 格式</span>
          </div>
        </n-upload>
      </div>

      <!-- 图片列表 -->
      <div class="banner-grid" v-if="currentBanners.length > 0">
        <div v-for="filename in currentBanners" :key="filename" class="banner-card">
          <div class="banner-preview">
            <img 
              :src="`${API_BASE}${bannerBasePath}${filename}`" 
              :alt="filename"
              loading="lazy"
              decoding="async"
              @load="(e: Event) => (e.target as HTMLImageElement).classList.add('loaded')"
            />
            <div class="img-loading">加载中...</div>
          </div>
          <div class="banner-info">
            <span class="filename">{{ filename }}</span>
            <n-button size="small" type="error" quaternary @click="deleteBanner(filename)">
              删除
            </n-button>
          </div>
        </div>
      </div>

      <n-empty v-else description="暂无 Banner 图片" style="margin-top: 40px;" />
    </n-spin>

    <div class="tip-box">
      <strong>💡 提示：</strong>
      <ul>
        <li>桌面端建议尺寸：1920 × 600 像素或更大</li>
        <li>移动端建议尺寸：750 × 400 像素或更大</li>
        <li>上传后需要重新构建前端才能生效（或等待热更新）</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.banner-page {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 900;
  color: var(--wf-accent);
}

.sub-label {
  font-size: 13px;
  color: var(--wf-text-dim);
  margin-top: 4px;
}

.tab-switcher {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 12px 24px;
  border: 1px solid var(--wf-border);
  border-radius: 12px;
  background: var(--wf-card);
  color: var(--wf-text);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  border-color: var(--wf-accent);
}

.tab-btn.active {
  background: #7AA2F7;
  border-color: #7AA2F7;
  color: white;
}

.upload-section {
  margin-bottom: 24px;
}

.upload-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  border: 2px dashed var(--wf-border);
  border-radius: 16px;
  background: var(--wf-card);
  cursor: pointer;
  transition: all 0.2s;
}

.upload-trigger:hover {
  border-color: #7AA2F7;
  background: rgba(122, 162, 247, 0.05);
}

.upload-icon {
  font-size: 32px;
}

.upload-hint {
  font-size: 12px;
  color: var(--wf-text-dim);
}

.banner-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.banner-card {
  background: var(--wf-card);
  border: 1px solid var(--wf-border);
  border-radius: 12px;
  overflow: hidden;
}

.banner-preview {
  aspect-ratio: 16 / 9;
  overflow: hidden;
  position: relative;
  background: var(--wf-card);
}

.banner-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.3s;
}

.banner-preview img.loaded {
  opacity: 1;
}

.img-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  color: var(--wf-text-dim);
}

.banner-preview img.loaded + .img-loading {
  display: none;
}

.banner-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-top: 1px solid var(--wf-border);
}

.filename {
  font-size: 12px;
  color: var(--wf-text-dim);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}

.tip-box {
  margin-top: 32px;
  padding: 16px 20px;
  background: rgba(122, 162, 247, 0.08);
  border-radius: 12px;
  font-size: 13px;
  color: var(--wf-text-dim);
}

.tip-box ul {
  margin: 8px 0 0 20px;
  padding: 0;
}

.tip-box li {
  margin-bottom: 4px;
}

@media (max-width: 600px) {
  .tab-switcher {
    flex-direction: column;
  }
  .banner-grid {
    grid-template-columns: 1fr;
  }
}
</style>
