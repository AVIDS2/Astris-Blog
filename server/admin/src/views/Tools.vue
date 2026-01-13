<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage, useDialog, NButton, NInput, NInputNumber, NSelect, NSwitch, NModal, NForm, NFormItem, NSpace, NSpin, NEmpty, NTag, NDataTable, type DataTableColumns } from 'naive-ui'
import { useAuthStore } from '../stores/auth'

const message = useMessage()
const dialog = useDialog()
const authStore = useAuthStore()

// 动态获取 API 基础路径，支持手机访问
const isDev = window.location.port !== ''
const API_BASE = isDev ? `http://${window.location.hostname}:8000` : ''

interface Tool {
  id?: number
  name: string
  url: string
  description: string
  icon: string
  category: string
  sort_order: number
  is_visible: boolean
}

const tools = ref<Tool[]>([])
const loading = ref(false)
const showModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)

const categoryOptions = [
  { label: '开发工具', value: '开发工具' },
  { label: '设计资源', value: '设计资源' },
  { label: '效率工具', value: '效率工具' },
  { label: '学习资源', value: '学习资源' },
  { label: '其他', value: '其他' }
]

const form = ref<Tool>({
  name: '',
  url: '',
  description: '',
  icon: '',
  category: '其他',
  sort_order: 0,
  is_visible: true
})

const columns: DataTableColumns<Tool> = [
  { title: '名称', key: 'name', width: 150 },
  { 
    title: '分类', 
    key: 'category', 
    width: 100,
    render: (row) => h(NTag, { type: 'info', bordered: false, size: 'small' }, () => row.category)
  },
  { title: '链接', key: 'url', ellipsis: { tooltip: true } },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  { title: '排序', key: 'sort_order', width: 60 },
  { 
    title: '显示', 
    key: 'is_visible', 
    width: 80,
    render: (row) => h(NSwitch, { 
      value: row.is_visible, 
      size: 'small',
      onUpdateValue: (val: boolean) => toggleVisibility(row, val)
    })
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    render: (row) => h(NSpace, { size: 'small' }, () => [
      h(NButton, { text: true, type: 'primary', onClick: () => editTool(row) }, () => '编辑'),
      h(NButton, { text: true, type: 'error', onClick: () => deleteTool(row) }, () => '删除')
    ])
  }
]

import { h } from 'vue'

async function fetchTools() {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/tools/admin/all`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      tools.value = await res.json()
    }
  } catch (e) {
    message.error('获取工具列表失败')
  } finally {
    loading.value = false
  }
}

function showAddModal() {
  isEditing.value = false
  editingId.value = null
  form.value = {
    name: '',
    url: '',
    description: '',
    icon: '',
    category: '其他',
    sort_order: 0,
    is_visible: true
  }
  showModal.value = true
}

function editTool(tool: Tool) {
  isEditing.value = true
  editingId.value = tool.id!
  form.value = { ...tool }
  showModal.value = true
}

async function saveTool() {
  if (!form.value.name || !form.value.url) {
    message.warning('请填写名称和链接')
    return
  }

  saving.value = true
  try {
    const url = isEditing.value
      ? `${API_BASE}/api/tools/admin/${editingId.value}`
      : `${API_BASE}/api/tools/admin`
    
    const res = await fetch(url, {
      method: isEditing.value ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`
      },
      body: JSON.stringify(form.value)
    })

    if (res.ok) {
      message.success(isEditing.value ? '更新成功' : '添加成功')
      showModal.value = false
      fetchTools()
    } else {
      message.error('操作失败')
    }
  } catch (e) {
    message.error('网络错误')
  } finally {
    saving.value = false
  }
}

async function toggleVisibility(tool: Tool, val: boolean) {
  try {
    await fetch(`${API_BASE}/api/tools/admin/${tool.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`
      },
      body: JSON.stringify({ is_visible: val })
    })
    tool.is_visible = val
  } catch (e) {
    message.error('更新失败')
  }
}

function deleteTool(tool: Tool) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除 "${tool.name}" 吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const res = await fetch(`${API_BASE}/api/tools/admin/${tool.id}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${authStore.token}` }
        })
        if (res.ok) {
          message.success('删除成功')
          fetchTools()
        }
      } catch (e) {
        message.error('删除失败')
      }
    }
  })
}

onMounted(fetchTools)
</script>

<template>
  <div class="tools-page">
    <div class="page-header">
      <div class="header-info">
        <h1>工具收藏</h1>
        <p class="sub-label">管理导航页显示的常用工具链接</p>
      </div>
      <n-button type="primary" size="large" ghost round @click="showAddModal">
        + 新增工具内容
      </n-button>
    </div>

    <n-spin :show="loading">
      <div v-if="tools.length === 0 && !loading" class="empty-holder">
        <n-empty description="暂无工具数据" />
      </div>
      
      <!-- 桌面端视图 -->
      <div class="desktop-view hide-on-mobile">
        <div class="table-container">
          <n-data-table
            :columns="columns"
            :data="tools"
            :bordered="false"
          />
        </div>
      </div>

      <!-- 手机端视图 -->
      <div class="mobile-view show-on-mobile">
        <div class="tool-cards">
          <div v-for="tool in tools" :key="tool.id" class="tool-card-wf">
            <div class="card-main">
              <div class="icon-section">
                <img v-if="tool.icon" :src="tool.icon" alt="" class="tool-img" />
                <div v-else class="icon-avatar">{{ tool.name.charAt(0).toUpperCase() }}</div>
              </div>
              <div class="info-section">
                <div class="top-meta">
                  <h3 class="name">{{ tool.name }}</h3>
                  <span class="cat-tag">{{ tool.category }}</span>
                </div>
                <p class="desc">{{ tool.description || '暂无详细描述' }}</p>
                <div class="link-url">{{ tool.url }}</div>
              </div>
            </div>
            
            <div class="card-footer">
              <div class="f-left">
                <span class="order">排序: {{ tool.sort_order }}</span>
                <n-switch 
                  size="small" 
                  :value="tool.is_visible" 
                  @update:value="toggleVisibility(tool, $event)"
                />
              </div>
              <div class="f-right">
                <n-button text type="primary" size="tiny" @click="editTool(tool)">修改</n-button>
                <n-button text type="error" size="tiny" @click="deleteTool(tool)">移除</n-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </n-spin>

    <!-- 添加/编辑弹窗 -->
    <n-modal v-model:show="showModal" preset="dialog" :title="isEditing ? '编辑工具' : '添加工具'">
      <n-form :model="form" label-placement="left" label-width="80px">
        <n-form-item label="名称" required>
          <n-input v-model:value="form.name" placeholder="例如：Astro" />
        </n-form-item>
        <n-form-item label="链接" required>
          <n-input v-model:value="form.url" placeholder="https://astro.build/" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="form.description" type="textarea" placeholder="速度极快的前端框架" />
        </n-form-item>
        <n-form-item label="图标">
          <n-input v-model:value="form.icon" placeholder="图标 URL（可选）" />
        </n-form-item>
        <n-form-item label="分类">
          <n-select v-model:value="form.category" :options="categoryOptions" />
        </n-form-item>
        <n-form-item label="排序">
          <n-input-number v-model:value="form.sort_order" :min="0" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="saveTool">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<style scoped>
.tools-page {
  animation: fadeIn 0.4s ease-out;
  overflow-x: hidden;
  max-width: 100%;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.table-container {
  background: var(--wf-card);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

/* 移动端卡片式列表 */
.tool-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 100px;
  max-width: 100%;
  overflow: hidden;
}

.tool-card-wf {
  background: var(--wf-card);
  border: 1px solid var(--wf-border);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.2s;
  max-width: 100%;
}

.tool-card-wf:active {
  background: rgba(255, 255, 255, 0.05);
  transform: scale(0.98);
}

.card-main {
  padding: 16px;
  display: flex;
  gap: 12px;
  min-width: 0;
}

.icon-section {
  width: 48px;
  height: 48px;
  min-width: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.tool-img { width: 100%; height: 100%; object-fit: contain; }
.icon-avatar { font-size: 24px; font-weight: 900; color: #7AA2F7; }

.info-section { flex: 1; min-width: 0; }

.top-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.name {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--wf-text);
}

.cat-tag {
  font-size: 10px;
  font-weight: 800;
  color: #7AA2F7;
  padding: 2px 8px;
  background: rgba(122, 162, 247, 0.05);
  border-radius: 6px;
}

.desc {
  font-size: 13px;
  color: var(--wf-text-dim);
  line-height: 1.5;
  margin: 0 0 10px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.link-url {
  font-size: 11px;
  color: var(--wf-text-dim);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: monospace;
  max-width: 100%;
}

.card-footer {
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.02);
  border-top: 1px solid rgba(255, 255, 255, 0.03);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.f-left { display: flex; align-items: center; gap: 12px; }
.order { font-size: 11px; opacity: 0.4; font-weight: 800; }
.f-right { display: flex; gap: 16px; }

.empty-holder { padding: 60px 0; }
</style>
