<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { tagsApi } from '../api'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

interface Tag {
  id: number
  name: string
  slug: string
  post_count: number
}

const tags = ref<Tag[]>([])
const loading = ref(true)
const showModal = ref(false)

const newTag = ref({
  name: '',
  slug: ''
})

async function fetchTags() {
  loading.value = true
  try {
    const response = await tagsApi.getAll()
    tags.value = response.data
  } finally {
    loading.value = false
  }
}

function generateSlug() {
  if (!newTag.value.slug && newTag.value.name) {
    newTag.value.slug = newTag.value.name
      .toLowerCase()
      .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-')
      .replace(/^-|-$/g, '')
  }
}

async function handleCreate() {
  if (!newTag.value.name || !newTag.value.slug) {
    message.warning('请填写名称和 Slug')
    return
  }
  
  try {
    await tagsApi.create(newTag.value)
    message.success('创建成功')
    showModal.value = false
    newTag.value = { name: '', slug: '' }
    fetchTags()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '创建失败')
  }
}

function handleDelete(tag: Tag) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除标签「${tag.name}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await tagsApi.delete(tag.id)
        message.success('删除成功')
        fetchTags()
      } catch {
        message.error('删除失败')
      }
    }
  })
}

onMounted(fetchTags)
</script>

<template>
  <div class="tags-page">
    <div class="page-header">
      <div class="section-meta">内容分析 / 标签</div>
      <n-button type="primary" size="small" round ghost @click="showModal = true">+ 新增标签</n-button>
    </div>
    
    <n-spin :show="loading">
      <div v-if="tags.length > 0" class="tags-cloud-wf">
        <div v-for="tag in tags" :key="tag.id" class="tag-chip-wf">
          <div class="tag-main-wf" @click="router.push('/posts')">
            <span class="tag-hash-wf">#</span>
            <span class="tag-name-wf">{{ tag.name }}</span>
            <span class="tag-count-wf">{{ tag.post_count }}</span>
          </div>
          <div class="tag-sep-wf"></div>
          <button class="tag-del-wf" @click.stop="handleDelete(tag)">×</button>
        </div>
      </div>
      
      <n-empty v-if="!loading && !tags.length" description="暂无标签数据" />
    </n-spin>
    
    <n-modal v-model:show="showModal" preset="dialog" title="新建标签" class="wf-modal">
      <n-form label-placement="top">
        <n-form-item label="标签名称" required>
          <n-input v-model:value="newTag.name" placeholder="输入标签名" @blur="generateSlug" />
        </n-form-item>
        <n-form-item label="路径标识" required>
          <n-input v-model:value="newTag.slug" placeholder="用于 URL 的 Slug" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showModal = false">取消</n-button>
        <n-button type="primary" @click="handleCreate">确认保存</n-button>
      </template>
    </n-modal>
  </div>
</template>

<style scoped>
.tags-page {
  padding: 0;
  max-width: 700px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.section-meta {
  font-size: 10px;
  font-weight: 900;
  color: var(--wf-accent);
  letter-spacing: 3px;
  margin-bottom: 12px;
}

/* Warframe 风格标签云 */
.tags-cloud-wf {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding-bottom: 100px;
}

.tag-chip-wf {
  display: flex;
  align-items: center;
  background: var(--wf-card);
  border: 1px solid var(--wf-border);
  border-radius: 8px;
  transition: all 0.2s;
}

.tag-chip-wf:active {
  background: rgba(255, 255, 255, 0.08);
  transform: scale(0.96);
}

.tag-main-wf {
  padding: 8px 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-hash-wf {
  color: var(--wf-accent);
  font-weight: 900;
  font-size: 14px;
  opacity: 0.6;
}

.tag-name-wf {
  font-size: 14px;
  font-weight: 700;
  color: var(--wf-text);
  letter-spacing: 0.5px;
}

.tag-count-wf {
  font-size: 10px;
  color: #7AA2F7;
  font-weight: 900;
  background: rgba(122, 162, 247, 0.05);
  padding: 0 6px;
  border-radius: 4px;
}

.tag-sep-wf {
  width: 1px;
  height: 16px;
  background: var(--wf-border);
}

.tag-del-wf {
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: #f56565;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.tag-del-wf:active {
  opacity: 1;
  background: rgba(255, 255, 255, 0.03);
}
</style>
