<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog, NButton, NTag, NSpace } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { postsApi } from '../api'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

interface Post {
  id: number
  title: string
  slug: string
  is_published: boolean
  is_pinned: boolean
  view_count: number
  created_at: string
  category: { name: string } | null
  tags: { name: string }[]
}

const posts = ref<Post[]>([])
const loading = ref(true)

const columns: DataTableColumns<Post> = [
  {
    title: 'ID',
    key: 'id',
    width: 60
  },
  {
    title: '标题',
    key: 'title',
    ellipsis: { tooltip: true }
  },
  {
    title: '分类',
    key: 'category',
    width: 100,
    render(row) {
      return row.category ? row.category.name : '-'
    }
  },
  {
    title: '标签',
    key: 'tags',
    width: 150,
    render(row) {
      if (!row.tags.length) return '-'
      return h(NSpace, { size: 'small' }, () =>
        row.tags.slice(0, 2).map(tag => h(NTag, { size: 'small', type: 'info' }, () => tag.name))
      )
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render(row) {
      return h(NSpace, { size: 'small' }, () => [
        row.is_published
          ? h(NTag, { type: 'success', size: 'small' }, () => '已发布')
          : h(NTag, { type: 'warning', size: 'small' }, () => '草稿'),
        row.is_pinned
          ? h(NTag, { type: 'error', size: 'small' }, () => '置顶')
          : null
      ])
    }
  },
  {
    title: '浏览',
    key: 'view_count',
    width: 80
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    render(row) {
      return new Date(row.created_at).toLocaleString('zh-CN')
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render(row) {
      return h(NSpace, { size: 'small' }, () => [
        h(NButton, {
          size: 'small',
          onClick: () => router.push(`/posts/${row.id}/edit`)
        }, () => '编辑'),
        h(NButton, {
          size: 'small',
          type: 'error',
          onClick: () => handleDelete(row)
        }, () => '删除')
      ])
    }
  }
]

async function fetchPosts() {
  loading.value = true
  try {
    const response = await postsApi.getAll()
    posts.value = response.data
  } catch (error) {
    message.error('获取文章列表失败')
  } finally {
    loading.value = false
  }
}

function handleDelete(post: Post) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除文章「${post.title}」吗？此操作不可恢复。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await postsApi.delete(post.id)
        message.success('删除成功')
        fetchPosts()
      } catch {
        message.error('删除失败')
      }
    }
  })
}

onMounted(fetchPosts)
</script>

<template>
  <div class="posts-page">
    <div class="page-header hide-on-mobile">
      <h1>文章管理</h1>
      <router-link to="/posts/new">
        <n-button type="primary" size="large" ghost round>+ 发布新文章</n-button>
      </router-link>
    </div>

    <div class="mobile-section-title show-on-mobile">文章列表</div>

    <!-- 桌面端视图：表格 -->
    <div class="desktop-view hide-on-mobile">
      <n-data-table
        :columns="columns"
        :data="posts"
        :loading="loading"
        :bordered="false"
      />
    </div>

    <!-- 手机端视图 -->
    <div class="mobile-view show-on-mobile">
      <div v-if="loading" class="mobile-loading">
        <n-spin size="large" />
      </div>
      <div v-else class="post-cards-wf">
        <div v-for="post in posts" :key="post.id" class="post-card-wf" @click="router.push(`/posts/${post.id}/edit`)">
          <div class="card-accent-bar" :class="{ pinned: post.is_pinned }"></div>
          <div class="card-body">
            <div class="card-meta">
              <span class="cat">{{ post.category?.name || '未分类' }}</span>
              <span class="date">{{ new Date(post.created_at).toLocaleDateString() }}</span>
            </div>
            <h3 class="title">{{ post.title }}</h3>
            <div class="card-info">
              <div class="tags-row">
                <span v-for="tag in post.tags" :key="tag.name" class="wf-tag">#{{ tag.name }}</span>
              </div>
              <div class="views-wf">
                <span class="v-val">{{ post.view_count }}</span>
                <span class="v-lab">浏览量</span>
              </div>
            </div>
            <div class="card-footer-wf" @click.stop>
              <n-space>
                <n-button text type="primary" size="tiny" @click="router.push(`/posts/${post.id}/edit`)">编辑文章</n-button>
                <n-button text type="error" size="tiny" @click="handleDelete(post)">删除记录</n-button>
              </n-space>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.posts-page {
  padding: 0;
  max-width: 800px;
  margin: 0 auto;
}

.mobile-section-title {
  font-size: 10px;
  font-weight: 900;
  color: var(--wf-accent);
  letter-spacing: 3px;
  text-transform: uppercase;
  margin: 0 0 16px 4px;
}

/* Warframe 风格卡片流 */
.post-cards-wf {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 100px;
}

.post-card-wf {
  background: var(--wf-card);
  border: 1px solid var(--wf-border);
  border-radius: 12px;
  display: flex;
  overflow: hidden;
  position: relative;
  transition: all 0.2s;
}

.post-card-wf:active {
  background: rgba(255, 255, 255, 0.08);
  transform: scale(0.98);
}

.card-accent-bar {
  width: 4px;
  background: rgba(255, 255, 255, 0.1);
}

.card-accent-bar.pinned {
  background: var(--wf-accent);
  box-shadow: 0 0 10px var(--wf-accent-dim);
}

.card-body {
  flex: 1;
  padding: 16px 20px;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.card-meta .cat {
  font-size: 9px;
  font-weight: 900;
  color: var(--wf-accent);
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.card-meta .date {
  font-size: 10px;
  color: var(--wf-text-dim);
  font-weight: 500;
}

.title {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--wf-text);
  line-height: 1.4;
  letter-spacing: 0.5px;
}

.card-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.wf-tag {
  font-size: 10px;
  font-weight: 700;
  color: #7AA2F7;
}

.views-wf {
  text-align: right;
}

.views-wf .v-val {
  display: block;
  font-size: 14px;
  font-weight: 900;
  color: var(--wf-text);
}

.views-wf .v-lab {
  font-size: 8px;
  font-weight: 800;
  color: var(--wf-text-dim);
  letter-spacing: 1px;
}

.card-footer-wf {
  display: flex;
  gap: 20px;
  padding-top: 12px;
  border-top: 1px solid var(--wf-border);
}

.link {
  font-size: 10px;
  font-weight: 900;
  color: #7AA2F7;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  cursor: pointer;
}

.link.danger {
  color: #f56565;
}

.link:active {
  opacity: 0.5;
}

.mobile-loading {
  padding: 60px 0;
  text-align: center;
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
</style>
