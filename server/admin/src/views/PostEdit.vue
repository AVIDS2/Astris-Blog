<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { postsApi, categoriesApi, tagsApi } from '../api'

import axios from 'axios'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const contentInput = ref<any>(null)

const isEdit = computed(() => !!route.params.id)
const loading = ref(false)
const saving = ref(false)

// 图片上传处理
async function handleImageUpload({ file }: { file: any }) {
  const formData = new FormData()
  formData.append('file', file.file)
  
  try {
    const res = await axios.post('/api/admin/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    // 始终使用相对路径，确保在任何设备上都能正确访问
    const imageUrl = res.data.url  // 已经是相对路径 /uploads/photos/xxx
    const markdownImage = `\n![图片描述](${imageUrl})\n`
    insertAtCursor(markdownImage)
    message.success('图片上传成功')
  } catch (error) {
    message.error('图片上传失败')
  }
}

// 封面图片上传处理
async function handleCoverUpload({ file }: { file: any }) {
  const formData = new FormData()
  formData.append('file', file.file)
  
  try {
    const res = await axios.post('/api/admin/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    // 始终使用相对路径
    form.value.cover_image = res.data.url
    message.success('封面上传成功')
  } catch (error) {
    message.error('封面上传失败')
  }
}

// 粘贴处理
function handlePaste(event: ClipboardEvent) {
  const items = event.clipboardData?.items
  if (!items) return

  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (item && item.type.indexOf('image') !== -1) {
      const file = item.getAsFile()
      if (file) {
        handleImageUpload({ file: { file } })
        // 阻止默认粘贴行为（防止粘贴 base64）
        event.preventDefault()
      }
    }
  }
}

// 在光标位置插入文字
function insertAtCursor(text: string) {
  const textarea = contentInput.value?.textareaElRef
  if (!textarea) {
    form.value.content += text
    return
  }

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const content = form.value.content
  
  form.value.content = content.substring(0, start) + text + content.substring(end)
  
  // 重新聚焦
  setTimeout(() => {
    textarea.focus()
    textarea.setSelectionRange(start + text.length, start + text.length)
  }, 0)
}

const form = ref({
  title: '',
  slug: '',
  content: '',
  summary: '',
  cover_image: '',
  is_published: false,
  is_pinned: false,
  category_id: null as number | null,
  tag_ids: [] as number[]
})

const categories = ref<{ label: string; value: number }[]>([])
const tags = ref<{ label: string; value: number }[]>([])

// 自动生成 slug
function generateSlug() {
  if (!form.value.slug && form.value.title) {
    form.value.slug = form.value.title
      .toLowerCase()
      .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-')
      .replace(/^-|-$/g, '')
  }
}

async function fetchData() {
  loading.value = true
  try {
    // 获取分类和标签
    const [catRes, tagRes] = await Promise.all([
      categoriesApi.getAll(),
      tagsApi.getAll()
    ])
    categories.value = catRes.data.map((c: any) => ({ label: c.name, value: c.id }))
    tags.value = tagRes.data.map((t: any) => ({ label: t.name, value: t.id }))
    
    // 如果是编辑模式，获取文章详情
    if (isEdit.value) {
      const postsRes = await postsApi.getAll()
      const post = postsRes.data.find((p: any) => p.id === Number(route.params.id))
      if (post) {
        form.value = {
          title: post.title,
          slug: post.slug,
          content: post.content,
          summary: post.summary || '',
          cover_image: post.cover_image || '',
          is_published: post.is_published,
          is_pinned: post.is_pinned,
          category_id: post.category?.id || null,
          tag_ids: post.tags.map((t: any) => t.id)
        }
      }
    }
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!form.value.title || !form.value.slug || !form.value.content) {
    message.warning('请填写标题、Slug 和内容')
    return
  }
  
  saving.value = true
  try {
    if (isEdit.value) {
      await postsApi.update(Number(route.params.id), form.value)
      message.success('更新成功')
    } else {
      await postsApi.create(form.value)
      message.success('创建成功')
    }
    router.push('/posts')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const showSettings = ref(false)

onMounted(fetchData)
</script>

<template>
  <div class="post-edit-page">
    <!-- 沉浸式顶栏 -->
    <div class="edit-header">
      <div class="header-left">
        <button class="icon-btn" @click="router.back()">←</button>
        <div class="edit-title-group">
          <span class="edit-status-dot" :class="{ published: form.is_published }"></span>
          <h2 class="edit-page-name">{{ isEdit ? '修改文章' : '新创作' }}</h2>
        </div>
      </div>
      <div class="header-right">
        <n-button 
          strong 
          secondary 
          circle 
          type="info" 
          class="show-on-mobile settings-trigger"
          @click="showSettings = true"
        >
          ⚙️
        </n-button>
        <n-button 
          type="primary" 
          :loading="saving" 
          round
          class="submit-btn-premium"
          @click="handleSubmit"
        >
          {{ isEdit ? '发布更改' : '发布保存' }}
        </n-button>
      </div>
    </div>
    
    <n-spin :show="loading">
      <div class="edit-layout">
        <!-- 主编辑区 -->
        <div class="editor-section">
          <div class="title-input-card">
            <input 
              v-model="form.title" 
              class="seamless-title-input" 
              placeholder="在这里输入标题..." 
              @blur="generateSlug"
            />
          </div>

          <div class="content-editor-card">
            <textarea
              ref="contentInput"
              v-model="form.content"
              class="seamless-content-textarea"
              placeholder="开始你的创作之旅 (支持 Markdown)…"
              @paste="handlePaste"
            ></textarea>
          </div>
        </div>

        <!-- 桌面端侧边栏 (Hide on Mobile) -->
        <div class="desktop-settings-sidebar hide-on-mobile">
          <div class="settings-card-premium">
            <h3 class="settings-title">发布设置</h3>
            <n-form label-placement="top">
              <n-form-item label="封面图">
                <div class="cover-section">
                  <div class="premium-cover-box">
                    <div v-if="form.cover_image" class="cover-img-wrapper">
                      <img :src="form.cover_image" />
                      <button class="remove-cover" @click="form.cover_image = ''">×</button>
                    </div>
                    <n-upload v-else :show-file-list="false" :custom-request="handleCoverUpload">
                      <div class="upload-placeholder">点此上传</div>
                    </n-upload>
                  </div>
                  <n-input 
                    v-model:value="form.cover_image" 
                    placeholder="或粘贴图片 URL" 
                    size="small"
                    style="margin-top: 8px;"
                  />
                </div>
              </n-form-item>
              
              <n-form-item label="状态与展示">
                <div class="toggle-row">
                  <span>发布</span> <n-switch v-model:value="form.is_published" />
                </div>
                <div class="toggle-row">
                  <span>置顶</span> <n-switch v-model:value="form.is_pinned" />
                </div>
              </n-form-item>

              <n-form-item label="核心分类">
                <n-select v-model:value="form.category_id" :options="categories" placeholder="请选择" />
              </n-form-item>
              
              <n-form-item label="标签">
                <n-select v-model:value="form.tag_ids" :options="tags" multiple placeholder="多选标签" />
              </n-form-item>
              
              <n-form-item label="自定义路径 (Slug)">
                <n-input v-model:value="form.slug" placeholder="custom-path" />
              </n-form-item>

              <n-form-item label="文章摘要">
                <n-input v-model:value="form.summary" type="textarea" placeholder="写一点摘要吧..." />
              </n-form-item>
            </n-form>
          </div>
        </div>

        <!-- 手机端专属：设置抽屉 -->
        <n-drawer v-model:show="showSettings" placement="bottom" height="85vh" style="border-radius: 30px 30px 0 0;">
          <n-drawer-content title="发布配置" closable>
            <div class="mobile-settings-drawer">
              <!-- 把上面的表单逻辑复用 -->
              <n-form label-placement="top">
                <div class="premium-cover-box big">
                  <div v-if="form.cover_image" class="cover-img-wrapper">
                    <img :src="form.cover_image" />
                    <button class="remove-cover" @click="form.cover_image = ''">×</button>
                  </div>
                  <n-upload v-else :show-file-list="false" :custom-request="handleCoverUpload">
                    <div class="upload-placeholder">点此上传封面图</div>
                  </n-upload>
                </div>
                
                <div class="drawer-toggles">
                  <div class="drawer-toggle-item">
                    <span>公开文章</span> <n-switch v-model:value="form.is_published" />
                  </div>
                  <div class="drawer-toggle-item">
                    <span>置顶展示</span> <n-switch v-model:value="form.is_pinned" />
                  </div>
                </div>

                <n-form-item label="文章分类"><n-select v-model:value="form.category_id" :options="categories" /></n-form-item>
                <n-form-item label="关联标签"><n-select v-model:value="form.tag_ids" :options="tags" multiple /></n-form-item>
                <n-form-item label="路径 Slug"><n-input v-model:value="form.slug" /></n-form-item>
                <n-form-item label="文章描述"><n-input v-model:value="form.summary" type="textarea" /></n-form-item>
              </n-form>
              <n-button type="primary" block size="large" round @click="showSettings = false">完成配置</n-button>
            </div>
          </n-drawer-content>
        </n-drawer>
      </div>
    </n-spin>
  </div>
</template>

<style scoped>
.post-edit-page {
  padding: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 响应式辅助类 */
@media (max-width: 768px) {
  .hide-on-mobile { display: none !important; }
  .show-on-mobile { display: flex !important; }
}

/* 沉浸式顶栏 */
.edit-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: var(--wf-card) !important;
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--wf-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-btn {
  background: transparent;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #4a5568;
}

.edit-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.edit-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #cbd5e0;
}

.edit-status-dot.published {
  background: #48bb78;
  box-shadow: 0 0 8px rgba(72, 187, 120, 0.4);
}

.edit-page-name {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  color: var(--wf-text);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.submit-btn-premium {
  font-weight: 800;
  padding: 0 24px;
}

/* 布局结构 */
.edit-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  padding: 24px;
  flex: 1;
}

@media (max-width: 768px) {
  .edit-layout {
    grid-template-columns: 1fr;
    padding: 12px;
    gap: 12px;
    height: calc(100vh - 70px);
    overflow: hidden;
  }
  .editor-section {
    height: 100%;
    overflow: hidden;
  }
  .title-input-card {
    flex-shrink: 0;
  }
  .seamless-title-input {
    font-size: 22px;
    padding: 6px 0;
  }
  .content-editor-card {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }
  .seamless-content-textarea {
    flex: 1;
    min-height: 0;
    height: 100%;
    padding: 14px;
    font-size: 14px;
    overflow-y: auto;
  }
}

/* 编辑器核心 */
.editor-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0; /* 关键：阻止内容撑大 grid 单元 */
  overflow: hidden;
}

.title-input-card {
  background: transparent;
}

.seamless-title-input {
  width: 100%;
  background: transparent;
  border: none;
  font-size: 32px;
  font-weight: 800;
  color: var(--wf-text);
  outline: none;
  padding: 10px 0;
}

.seamless-title-input::placeholder {
  color: #cbd5e0;
}

.content-editor-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--wf-card);
  backdrop-filter: blur(25px) saturate(180%);
  border-radius: 14px;
  border: 1px solid var(--wf-border);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.03);
  overflow: visible;
  min-width: 0;
}

.editor-toolbar-premium {
  padding: 12px 20px;
  background: rgba(122, 162, 247, 0.05);
  display: flex;
  gap: 15px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);
  flex-shrink: 0;
}

.toolbar-tool {
  font-size: 13px;
  font-weight: 700;
  color: #7AA2F7;
  cursor: pointer;
  white-space: nowrap;
}

.seamless-content-textarea {
  width: 100%;
  flex: 1;
  min-height: 50vh;
  border: none;
  background: transparent;
  padding: 20px;
  font-size: 15px;
  line-height: 1.8;
  color: var(--wf-text);
  outline: none;
  resize: none;
  font-family: inherit;
  box-sizing: border-box;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

/* 侧边栏/抽屉 统一样式 */
.settings-card-premium {
  background: var(--wf-card);
  backdrop-filter: blur(25px) saturate(180%);
  border-radius: 24px;
  padding: 24px;
  border: 1px solid var(--wf-border);
  position: sticky;
  top: 90px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}

.settings-title {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 800;
}

.premium-cover-box {
  width: 100%;
  aspect-ratio: 2/1;
  max-height: 120px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 10px;
  border: 1px dashed var(--wf-border);
  overflow: hidden;
  position: relative;
}

.premium-cover-box.big {
  aspect-ratio: 16/9;
  max-height: 160px;
  margin-bottom: 16px;
}

.cover-img-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.cover-img-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-cover {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(0,0,0,0.5);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a0aec0;
  font-size: 12px;
  font-weight: 700;
}

.toggle-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 10px 14px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 12px;
}

.toggle-row span {
  font-size: 13px;
  font-weight: 700;
  color: var(--wf-text);
  opacity: 0.6;
}

.drawer-toggles {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.drawer-toggle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 16px;
}

.drawer-toggle-item span {
  font-size: 13px;
  font-weight: 700;
}

.mobile-settings-drawer {
  padding-bottom: 40px;
}
</style>
