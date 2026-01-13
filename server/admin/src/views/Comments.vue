<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { commentsApi } from '../api'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

interface Comment {
  id: number
  nickname: string
  email: string | null
  content: string
  is_approved: boolean
  created_at: string
  post_id: number
  post_title: string
  post_slug: string | null
}

const comments = ref<Comment[]>([])
const loading = ref(true)
const filter = ref<'all' | 'pending' | 'approved'>('all')

async function fetchComments() {
  loading.value = true
  try {
    const approved = filter.value === 'all' ? undefined : filter.value === 'approved'
    const response = await commentsApi.getAll(approved)
    comments.value = response.data
  } finally {
    loading.value = false
  }
}

async function handleApprove(comment: Comment) {
  try {
    await commentsApi.approve(comment.id)
    message.success('已通过审核')
    fetchComments()
  } catch {
    message.error('操作失败')
  }
}

function handleDelete(comment: Comment) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除这条评论吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await commentsApi.delete(comment.id)
        message.success('删除成功')
        fetchComments()
      } catch {
        message.error('删除失败')
      }
    }
  })
}

onMounted(fetchComments)
</script>

<template>
  <div class="comments-page">
    <div class="page-header">
      <div class="section-meta">内容互动 / 评论管理</div>
      <div class="filter-row">
        <n-radio-group v-model:value="filter" @update:value="fetchComments" size="small" type="button">
          <n-radio-button value="all">全部</n-radio-button>
          <n-radio-button value="pending">待审核</n-radio-button>
          <n-radio-button value="approved">已通过</n-radio-button>
        </n-radio-group>
      </div>
    </div>
    
    <n-spin :show="loading">
      <div v-if="comments.length > 0" class="comments-flow-wf">
        <div v-for="comment in comments" :key="comment.id" class="comment-card-wf">
          <div class="status-indicator" :class="{ approved: comment.is_approved }"></div>
          <div class="card-content">
            <div class="comment-head">
              <div class="author-info">
                <div class="avatar-box">{{ comment.nickname.charAt(0).toUpperCase() }}</div>
                <div class="meta-text">
                  <div class="nickname">{{ comment.nickname }}</div>
                  <div class="source-post" @click="router.push(`/posts/${comment.post_id}/edit`)">
                    来自: {{ comment.post_title }} ↗
                  </div>
                </div>
              </div>
              <div class="publish-date">{{ new Date(comment.created_at).toLocaleDateString() }}</div>
            </div>

            <div class="comment-body">
              {{ comment.content }}
            </div>

            <div class="action-footer">
              <div class="left-btns">
                <n-button v-if="!comment.is_approved" text type="primary" size="tiny" @click="handleApprove(comment)">通过审核</n-button>
              </div>
              <n-button text type="error" size="tiny" @click="handleDelete(comment)">删除评论</n-button>
            </div>
          </div>
        </div>
      </div>
      
      <n-empty v-if="!loading && !comments.length" description="暂无相关评论数据" />
    </n-spin>
  </div>
</template>

<style scoped>
.comments-page {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  margin-bottom: 30px;
}

.section-meta {
  font-size: 10px;
  font-weight: 900;
  color: var(--wf-accent);
  letter-spacing: 3px;
  margin-bottom: 20px;
}

.filter-row :deep(.n-radio-button) {
  background: transparent !important;
  border-color: var(--wf-border) !important;
  color: var(--wf-text-dim) !important;
  font-weight: 800;
  font-size: 11px;
}

.filter-row :deep(.n-radio-button--checked) {
  background: var(--wf-accent-dim) !important;
  color: var(--wf-accent) !important;
  border-color: var(--wf-accent) !important;
}

/* 列表流 */
.comments-flow-wf {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 100px;
}

.comment-card-wf {
  background: var(--wf-card);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  display: flex;
  overflow: hidden;
  transition: all 0.2s;
}

.comment-card-wf:active {
  background: rgba(255, 255, 255, 0.05);
}

.status-indicator {
  width: 4px;
  background: #f56565;
  opacity: 0.4;
}

.status-indicator.approved {
  background: #48bb78;
}

.card-content {
  flex: 1;
  padding: 20px;
}

.comment-head {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.author-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.avatar-box {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background: var(--wf-bg);
  border: 1px solid var(--wf-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  color: var(--wf-accent);
}

.nickname {
  font-size: 15px;
  font-weight: 800;
  color: var(--wf-text);
}

.source-post {
  font-size: 10px;
  color: #7AA2F7;
  margin-top: 2px;
  font-weight: 700;
  cursor: pointer;
}

.publish-date {
  font-size: 11px;
  color: var(--wf-text-dim);
}

.comment-body {
  font-size: 14px;
  line-height: 1.6;
  color: var(--wf-text);
  margin-bottom: 20px;
}

.action-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 14px;
  border-top: 1px solid var(--wf-border);
}

.left-btns {
  display: flex;
  gap: 20px;
}
</style>
