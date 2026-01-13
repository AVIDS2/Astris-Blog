<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { categoriesApi } from '../api'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

interface Category {
  id: number
  name: string
  slug: string
  description: string | null
  post_count: number
}

const categories = ref<Category[]>([])
const loading = ref(true)
const showModal = ref(false)

const newCategory = ref({
  name: '',
  slug: '',
  description: ''
})

async function fetchCategories() {
  loading.value = true
  try {
    const response = await categoriesApi.getAll()
    categories.value = response.data
  } finally {
    loading.value = false
  }
}

function generateSlug() {
  if (!newCategory.value.slug && newCategory.value.name) {
    newCategory.value.slug = newCategory.value.name
      .toLowerCase()
      .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-')
      .replace(/^-|-$/g, '')
  }
}

async function handleCreate() {
  if (!newCategory.value.name || !newCategory.value.slug) {
    message.warning('请填写名称和 Slug')
    return
  }
  
  try {
    await categoriesApi.create(newCategory.value)
    message.success('创建成功')
    showModal.value = false
    newCategory.value = { name: '', slug: '', description: '' }
    fetchCategories()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '创建失败')
  }
}

function handleDelete(category: Category) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除分类「${category.name}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await categoriesApi.delete(category.id)
        message.success('删除成功')
        fetchCategories()
      } catch {
        message.error('删除失败')
      }
    }
  })
}

onMounted(fetchCategories)
</script>

<template>
  <div class="categories-page">
    <div class="page-header">
      <div class="section-meta">内容分析 / 分类</div>
      <n-button type="primary" size="small" round ghost @click="showModal = true">+ 新增分类</n-button>
    </div>
    
    <n-spin :show="loading">
      <div v-if="categories.length > 0" class="categories-flow-wf">
        <div v-for="cat in categories" :key="cat.id" class="category-card-wf" @click="router.push('/posts')">
          <div class="card-body-wf">
            <div class="cat-top-wf">
              <span class="name-wf">{{ cat.name }}</span>
              <div class="stats-wf">
                <span class="val">{{ cat.post_count }}</span>
                <span class="lab">篇文章</span>
              </div>
            </div>
            <div class="cat-sub-wf">路径标识: {{ cat.slug }}</div>
            
            <div class="card-footer-wf" @click.stop>
              <n-button text type="error" size="tiny" @click="handleDelete(cat)">删除分类</n-button>
            </div>
          </div>
        </div>
      </div>
      
      <n-empty v-if="!loading && !categories.length" description="暂无分类数据" />
    </n-spin>
    
    <n-modal v-model:show="showModal" preset="dialog" title="新建分类" class="wf-modal">
      <n-form label-placement="top">
        <n-form-item label="分类名称" required>
          <n-input v-model:value="newCategory.name" placeholder="输入名称" @blur="generateSlug" />
        </n-form-item>
        <n-form-item label="路径 Slug" required>
          <n-input v-model:value="newCategory.slug" placeholder="用于 URL 的唯一标识" />
        </n-form-item>
        <n-form-item label="描述 (可选)">
          <n-input v-model:value="newCategory.description" type="textarea" placeholder="分类简单说明..." />
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
.categories-page {
  padding: 0;
  max-width: 600px;
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

/* Warframe 风格列表 */
.categories-flow-wf {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 100px;
}

.category-card-wf {
  background: var(--wf-card);
  border: 1px solid var(--wf-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.category-card-wf:active {
  background: rgba(255, 255, 255, 0.08);
  transform: scale(0.98);
}

.card-body-wf {
  padding: 18px 20px;
}

.cat-top-wf {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.name-wf {
  font-size: 18px;
  font-weight: 700;
  color: var(--wf-text);
  letter-spacing: 0.5px;
}

.stats-wf {
  text-align: right;
}

.stats-wf .val {
  display: block;
  font-size: 14px;
  font-weight: 900;
  color: var(--wf-text);
}

.stats-wf .lab {
  font-size: 8px;
  font-weight: 800;
  color: var(--wf-accent);
  letter-spacing: 1px;
  opacity: 0.6;
}

.cat-sub-wf {
  font-size: 10px;
  color: var(--wf-text-dim);
  font-weight: 800;
  letter-spacing: 1px;
}

.card-footer-wf {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--wf-border);
  display: flex;
  justify-content: flex-end;
}

.wf-link {
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  cursor: pointer;
}

.wf-link.danger {
  color: #f56565;
}

.wf-link:active {
  opacity: 0.5;
}
</style>
