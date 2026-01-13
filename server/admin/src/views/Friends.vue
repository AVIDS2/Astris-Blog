<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useMessage, useDialog, NButton, NInput, NInputNumber, NSwitch, NModal, NForm, NFormItem, NSpace, NSpin, NEmpty, NTag, NDataTable, type DataTableColumns } from 'naive-ui'
import { useAuthStore } from '../stores/auth'

const message = useMessage()
const dialog = useDialog()
const authStore = useAuthStore()

// 动态获取 API 基础路径
const isDev = window.location.port !== ''
const API_BASE = isDev ? `http://${window.location.hostname}:8000` : ''

interface Friend {
  id?: number
  name: string
  url: string
  avatar: string
  description: string
  tags: string
  sort_order: number
  is_visible: boolean
  created_at?: string
}

const friends = ref<Friend[]>([])
const loading = ref(false)
const showModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)

const form = ref<Friend>({
  name: '',
  url: '',
  avatar: '',
  description: '',
  tags: '',
  sort_order: 0,
  is_visible: true
})

const columns: DataTableColumns<Friend> = [
  { 
    title: '头像', 
    key: 'avatar', 
    width: 60,
    render: (row) => row.avatar ? h('img', { 
      src: row.avatar, 
      style: 'width: 40px; height: 40px; border-radius: 50%; object-fit: cover;' 
    }) : h('span', { style: 'color: #999;' }, '无')
  },
  { title: '名称', key: 'name', width: 120 },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  { 
    title: '标签', 
    key: 'tags', 
    width: 150,
    render: (row) => {
      if (!row.tags) return h('span', { style: 'color: #999;' }, '-')
      const tagList = row.tags.split(',').filter(t => t.trim())
      return h(NSpace, { size: 'small' }, () => 
        tagList.map(tag => h(NTag, { type: 'info', bordered: false, size: 'small' }, () => tag.trim()))
      )
    }
  },
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
      h(NButton, { text: true, type: 'primary', onClick: () => editFriend(row) }, () => '编辑'),
      h(NButton, { text: true, type: 'error', onClick: () => deleteFriend(row) }, () => '删除')
    ])
  }
]

async function fetchFriends() {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/admin/friends`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      friends.value = await res.json()
    }
  } catch (e) {
    message.error('获取友链列表失败')
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
    avatar: '',
    description: '',
    tags: '',
    sort_order: 0,
    is_visible: true
  }
  showModal.value = true
}

function editFriend(friend: Friend) {
  isEditing.value = true
  editingId.value = friend.id!
  form.value = { ...friend }
  showModal.value = true
}

async function saveFriend() {
  if (!form.value.name || !form.value.url) {
    message.warning('请填写名称和链接')
    return
  }

  saving.value = true
  try {
    const url = isEditing.value
      ? `${API_BASE}/api/admin/friends/${editingId.value}`
      : `${API_BASE}/api/admin/friends`
    
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
      fetchFriends()
    } else {
      message.error('操作失败')
    }
  } catch (e) {
    message.error('操作失败')
  } finally {
    saving.value = false
  }
}

async function toggleVisibility(friend: Friend, visible: boolean) {
  try {
    const res = await fetch(`${API_BASE}/api/admin/friends/${friend.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`
      },
      body: JSON.stringify({ ...friend, is_visible: visible })
    })

    if (res.ok) {
      friend.is_visible = visible
      message.success(visible ? '已显示' : '已隐藏')
    }
  } catch (e) {
    message.error('操作失败')
  }
}

function deleteFriend(friend: Friend) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除友链"${friend.name}"吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const res = await fetch(`${API_BASE}/api/admin/friends/${friend.id}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${authStore.token}` }
        })

        if (res.ok) {
          message.success('删除成功')
          fetchFriends()
        } else {
          message.error('删除失败')
        }
      } catch (e) {
        message.error('删除失败')
      }
    }
  })
}

onMounted(() => {
  fetchFriends()
})
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h2>友情链接管理</h2>
      <NButton type="primary" @click="showAddModal">添加友链</NButton>
    </div>

    <NSpin :show="loading">
      <div class="content-card">
        <!-- 桌面端：表格视图 -->
        <div class="desktop-view">
          <NDataTable
            v-if="friends.length > 0"
            :columns="columns"
            :data="friends"
            :bordered="false"
            :single-line="false"
          />
          <NEmpty v-else description="暂无友链" />
        </div>

        <!-- 移动端：卡片视图 -->
        <div class="mobile-view">
          <div v-if="friends.length > 0" class="friend-cards">
            <div 
              v-for="friend in friends" 
              :key="friend.id" 
              class="friend-card"
              :class="{ 'is-hidden': !friend.is_visible }"
            >
              <div class="card-header">
                <img 
                  v-if="friend.avatar" 
                  :src="friend.avatar" 
                  :alt="friend.name"
                  class="card-avatar"
                />
                <div v-else class="card-avatar-placeholder">
                  {{ friend.name.charAt(0) }}
                </div>
                <div class="card-info">
                  <h3 class="card-title">{{ friend.name }}</h3>
                  <p class="card-desc">{{ friend.description || '暂无描述' }}</p>
                </div>
              </div>

              <div class="card-tags" v-if="friend.tags">
                <NTag 
                  v-for="tag in friend.tags.split(',')" 
                  :key="tag"
                  size="small"
                  type="info"
                  :bordered="false"
                >
                  {{ tag.trim() }}
                </NTag>
              </div>

              <div class="card-footer">
                <div class="card-meta">
                  <span>排序: {{ friend.sort_order }}</span>
                  <NSwitch 
                    :value="friend.is_visible" 
                    size="small"
                    @update:value="(val) => toggleVisibility(friend, val)"
                  />
                </div>
                <div class="card-actions">
                  <NButton text type="primary" size="small" @click="editFriend(friend)">
                    编辑
                  </NButton>
                  <NButton text type="error" size="small" @click="deleteFriend(friend)">
                    删除
                  </NButton>
                </div>
              </div>
            </div>
          </div>
          <NEmpty v-else description="暂无友链" />
        </div>
      </div>
    </NSpin>

    <!-- 添加/编辑弹窗 -->
    <NModal
      v-model:show="showModal"
      :title="isEditing ? '编辑友链' : '添加友链'"
      preset="card"
      style="width: 500px; max-width: 90vw;"
    >
      <NForm :model="form" label-placement="top">
        <NFormItem label="名称" required>
          <NInput v-model:value="form.name" placeholder="友链名称" />
        </NFormItem>
        <NFormItem label="链接" required>
          <NInput v-model:value="form.url" placeholder="https://example.com" />
        </NFormItem>
        <NFormItem label="头像">
          <NInput v-model:value="form.avatar" placeholder="头像 URL" />
        </NFormItem>
        <NFormItem label="描述">
          <NInput 
            v-model:value="form.description" 
            type="textarea" 
            placeholder="简短描述"
            :rows="2"
          />
        </NFormItem>
        <NFormItem label="标签">
          <NInput 
            v-model:value="form.tags" 
            placeholder="多个标签用逗号分隔" 
          />
        </NFormItem>
        <div class="form-row">
          <NFormItem label="排序" style="flex: 1;">
            <NInputNumber v-model:value="form.sort_order" :min="0" style="width: 100%;" />
          </NFormItem>
          <NFormItem label="显示" style="flex: 1;">
            <NSwitch v-model:value="form.is_visible" />
          </NFormItem>
        </div>
      </NForm>

      <template #footer>
        <NSpace justify="end">
          <NButton @click="showModal = false">取消</NButton>
          <NButton type="primary" :loading="saving" @click="saveFriend">
            {{ isEditing ? '保存' : '添加' }}
          </NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>

<style scoped>
.page-container {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.page-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.content-card {
  background: var(--wf-card);
  border-radius: 12px;
  padding: 16px;
}

/* 桌面端显示表格，隐藏卡片 */
.desktop-view {
  display: block;
}

.mobile-view {
  display: none;
}

/* 移动端显示卡片，隐藏表格 */
@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }

  .desktop-view {
    display: none;
  }

  .mobile-view {
    display: block;
  }

  .content-card {
    padding: 12px;
  }
}

/* 卡片样式 */
.friend-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.friend-card {
  background: var(--wf-bg);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s ease;
}

.friend-card.is-hidden {
  opacity: 0.5;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.card-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  object-fit: cover;
  flex-shrink: 0;
}

.card-avatar-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #7AA2F7 0%, #89DDFF 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-title {
  margin: 0 0 4px 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--wf-text);
}

.card-desc {
  margin: 0;
  font-size: 0.875rem;
  color: var(--wf-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.75rem;
  color: var(--wf-text-secondary);
}

.card-actions {
  display: flex;
  gap: 8px;
}

.form-row {
  display: flex;
  gap: 16px;
}

@media (max-width: 480px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
}
</style>

