<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage, useDialog, NButton, NInput, NSwitch, NModal, NForm, NFormItem, NSpace, NSpin, NEmpty, NImage, NImageGroup, NUpload, NUploadDragger, NInputNumber, type UploadFileInfo } from 'naive-ui'
import { useAuthStore } from '../stores/auth'

const message = useMessage()
const dialog = useDialog()
const authStore = useAuthStore()

// 动态获取 API 基础路径，支持手机访问
const isLocalDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
const API_BASE = isLocalDev ? `http://${window.location.hostname}:8000` : ''

interface Photo {
  id: number
  url: string
  title: string | null
}

interface Album {
  id?: number
  name: string
  description: string
  cover: string | null
  sort_order: number
  is_visible: boolean
  photo_count: number
  photos?: Photo[]
}

const albums = ref<Album[]>([])
const loading = ref(false)
const showModal = ref(false)
const showPhotoModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const currentAlbum = ref<Album | null>(null)
const uploading = ref(false)

const form = ref<Album>({
  name: '',
  description: '',
  cover: null,
  sort_order: 0,
  is_visible: true,
  photo_count: 0
})

async function fetchAlbums() {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/albums/admin/all`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      albums.value = await res.json()
    }
  } catch (e) {
    message.error('获取相册列表失败')
  } finally {
    loading.value = false
  }
}

function showAddModal() {
  isEditing.value = false
  editingId.value = null
  form.value = {
    name: '',
    description: '',
    cover: null,
    sort_order: 0,
    is_visible: true,
    photo_count: 0
  }
  showModal.value = true
}

function editAlbum(album: Album) {
  isEditing.value = true
  editingId.value = album.id!
  form.value = { ...album }
  showModal.value = true
}

async function saveAlbum() {
  if (!form.value.name) {
    message.warning('请填写相册名称')
    return
  }

  saving.value = true
  try {
    const url = isEditing.value
      ? `${API_BASE}/api/albums/admin/${editingId.value}`
      : `${API_BASE}/api/albums/admin`
    
    const res = await fetch(url, {
      method: isEditing.value ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`
      },
      body: JSON.stringify(form.value)
    })

    if (res.ok) {
      message.success(isEditing.value ? '更新成功' : '创建成功')
      showModal.value = false
      fetchAlbums()
    } else {
      message.error('操作失败')
    }
  } catch (e) {
    message.error('网络错误')
  } finally {
    saving.value = false
  }
}

function deleteAlbum(album: Album) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除相册 "${album.name}" 吗？其中的所有照片也会被删除！`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const res = await fetch(`${API_BASE}/api/albums/admin/${album.id}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${authStore.token}` }
        })
        if (res.ok) {
          message.success('删除成功')
          fetchAlbums()
        }
      } catch (e) {
        message.error('删除失败')
      }
    }
  })
}

async function openPhotos(album: Album) {
  currentAlbum.value = album
  // 获取相册详情
  try {
    const res = await fetch(`${API_BASE}/api/albums/${album.id}`)
    if (res.ok) {
      const data = await res.json()
      currentAlbum.value = data
    }
  } catch (e) {
    message.error('获取照片失败')
  }
  showPhotoModal.value = true
}

async function handleUpload({ file }: { file: UploadFileInfo }) {
  if (!currentAlbum.value?.id) return
  
  uploading.value = true
  const formData = new FormData()
  formData.append('files', file.file as File)
  
  try {
    const res = await fetch(`${API_BASE}/api/albums/admin/${currentAlbum.value.id}/photos`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${authStore.token}` },
      body: formData
    })
    
    if (res.ok) {
      message.success('上传成功')
      // 刷新照片列表
      openPhotos(currentAlbum.value)
      fetchAlbums()
    }
  } catch (e) {
    message.error('上传失败')
  } finally {
    uploading.value = false
  }
}

async function deletePhoto(photo: Photo) {
  dialog.warning({
    title: '确认删除',
    content: '确定要删除这张照片吗？',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const res = await fetch(`${API_BASE}/api/albums/admin/photos/${photo.id}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${authStore.token}` }
        })
        if (res.ok) {
          message.success('删除成功')
          if (currentAlbum.value) {
            openPhotos(currentAlbum.value)
          }
          fetchAlbums()
        }
      } catch (e) {
        message.error('删除失败')
      }
    }
  })
}

onMounted(fetchAlbums)
</script>

<template>
  <div class="albums-page">
    <div class="page-header hide-on-mobile">
      <h1>相册管理</h1>
      <n-button type="primary" size="large" ghost round @click="showAddModal">
        + 创建新相册
      </n-button>
    </div>

    <!-- 手机端标题栏 -->
    <div class="mobile-section-header show-on-mobile">
      <div class="header-meta">图库资源 / 相册存档</div>
      <n-button type="primary" ghost round size="small" @click="showAddModal">
        + 新增
      </n-button>
    </div>

    <n-spin :show="loading">
      <n-empty v-if="albums.length === 0 && !loading" description="暂无相册存档" />
      
      <div v-else class="album-flow-wf">
        <div v-for="album in albums" :key="album.id" class="album-card-wf" :class="{ 'hidden-wf': !album.is_visible }">
          <div class="album-cover-wf" @click="openPhotos(album)">
            <img v-if="album.cover" :src="API_BASE + album.cover" alt="" />
            <div v-else class="empty-cover-wf">暂无封面</div>
            <div class="count-badge">{{ album.photo_count }} 张照片</div>
          </div>
          
          <div class="album-content-wf">
            <div class="album-main-info">
              <h3 class="album-name-wf">{{ album.name }}</h3>
              <p class="album-desc-wf">{{ album.description || '暂无描述信息' }}</p>
            </div>
            
            <div class="album-footer-wf">
              <div class="wf-actions-row">
                <n-button text type="primary" size="tiny" @click="openPhotos(album)">管理照片</n-button>
                <n-button text type="primary" size="tiny" @click="editAlbum(album)">编辑属性</n-button>
                <n-button text type="error" size="tiny" @click="deleteAlbum(album)">删除相册</n-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </n-spin>

    <!-- 创建/编辑相册弹窗 -->
    <n-modal v-model:show="showModal" preset="dialog" :title="isEditing ? '编辑相册' : '新增相册'" class="wf-modal">
      <n-form :model="form" label-placement="top">
        <n-form-item label="相册名称" required>
          <n-input v-model:value="form.name" placeholder="输入名称" />
        </n-form-item>
        <n-form-item label="描述 (可选)">
          <n-input v-model:value="form.description" type="textarea" placeholder="填写相册简介..." />
        </n-form-item>
        <n-form-item label="显示优先级">
          <n-input-number v-model:value="form.sort_order" :min="0" />
        </n-form-item>
        <n-form-item label="是否公开显示">
          <n-switch v-model:value="form.is_visible" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="saveAlbum">确认保存</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 照片管理弹窗 -->
    <n-modal v-model:show="showPhotoModal" preset="card" :title="currentAlbum?.name || '管理照片'" style="width: 900px; max-width: 95vw;" class="wf-modal">
      <div class="photo-manager-wf">
        <!-- 上传区域 -->
        <n-upload
          multiple
          :custom-request="({ file }) => handleUpload({ file })"
          :show-file-list="false"
          accept="image/*"
        >
          <n-upload-dragger class="wf-dragger">
            <div style="padding: 20px;">
              <p class="upload-title">点击或拖拽照片至此上传</p>
              <p class="upload-tip">支持 JPG, PNG, WEBP 格式</p>
            </div>
          </n-upload-dragger>
        </n-upload>

        <!-- 照片列表 -->
        <div class="photo-grid-wf" v-if="currentAlbum?.photos?.length">
          <n-image-group>
            <div v-for="photo in currentAlbum.photos" :key="photo.id" class="photo-item-wf">
              <n-image 
                :src="API_BASE + photo.url" 
                object-fit="cover" 
                show-toolbar-tooltip
              />
              <button class="purge-btn" @click.stop="deletePhoto(photo)">×</button>
            </div>
          </n-image-group>
        </div>
        <n-empty v-else description="相册内暂无静态记录" style="margin-top: 20px;" />
      </div>
    </n-modal>
  </div>
</template>

<style scoped>
.albums-page {
  padding: 0;
  max-width: 800px;
  margin: 0 auto;
}

.mobile-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-meta {
  font-size: 10px;
  font-weight: 900;
  color: var(--wf-accent);
  letter-spacing: 3px;
}

/* Warframe 风格列表 */
.album-flow-wf {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-bottom: 100px;
}

.album-card-wf {
  background: var(--wf-card);
  border: 1px solid var(--wf-border);
  border-radius: 16px;
  display: flex;
  overflow: hidden;
  transition: all 0.3s;
}

.album-card-wf.hidden-wf {
  opacity: 0.5;
  filter: grayscale(0.8);
}

.album-cover-wf {
  width: 120px;
  height: 120px;
  min-width: 120px;
  position: relative;
  cursor: pointer;
  background: #000;
}

.album-cover-wf img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.8;
}

.album-content-wf {
  flex: 1;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.album-name-wf {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--wf-text);
  letter-spacing: 0.5px;
}

.album-desc-wf {
  margin: 10px 0 20px 0;
  font-size: 13px;
  color: var(--wf-text-dim);
  line-height: 1.6;
  white-space: normal;
}

.album-footer-wf {
  margin-top: auto;
  border-top: 1px solid var(--wf-border);
  padding-top: 14px;
}

.wf-actions-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.empty-cover-wf {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
  color: var(--wf-text-dim);
}

.count-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  color: #7AA2F7;
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 900;
  border: 1px solid rgba(122, 162, 247, 0.2);
}

.upload-title {
  font-size: 16px; 
  font-weight: 800; 
  color: var(--wf-accent);
  margin: 0;
}

.upload-tip {
  font-size: 12px; 
  color: var(--wf-text-dim);
  margin: 4px 0 0 0;
}

/* 照片管理器专场 */
.photo-manager-wf {
  padding: 0;
}

.wf-dragger {
  background: rgba(255, 255, 255, 0.02) !important;
  border: 1px dashed rgba(255, 255, 255, 0.1) !important;
}

.photo-grid-wf {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-top: 24px;
}

.photo-item-wf {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  background: var(--wf-bg);
  border: 1px solid var(--wf-border);
}

.photo-item-wf :deep(img) {
  width: 100%;
  height: 100%;
  opacity: 1;
  transition: opacity 0.3s;
}

.photo-item-wf:hover :deep(img) {
  opacity: 1;
}

.purge-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: rgba(245, 101, 101, 0.8);
  border: none;
  color: white;
  font-size: 10px;
  cursor: pointer;
  z-index: 10;
}

/* 桌面端头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 900;
  letter-spacing: 4px;
  color: var(--wf-accent);
}

/* 兼容小屏幕 */
@media (max-width: 480px) {
  .album-card-wf {
    flex-direction: column;
  }
  .album-cover-wf {
    width: 100%;
    height: 160px;
  }
}
</style>
