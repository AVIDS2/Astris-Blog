<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { statsApi } from '../api'

const stats = ref({
  posts: 0,
  categories: 0,
  tags: 0,
  comments: 0,
  views: 0
})

const loading = ref(true)

onMounted(async () => {
  try {
    const response = await statsApi.get()
    stats.value = response.data
  } finally {
    loading.value = false
  }
})

const quickActions = [
  { label: '写文章', path: '/posts/new', icon: '✏️' },
  { label: '删评论', path: '/comments', icon: '💬' },
  { label: '传照片', path: '/albums', icon: '📷' }
]
</script>

<template>
  <div class="dashboard-page">
    <div class="overview-header">
      <div class="welcome-msg">
        <h2>控制台概览</h2>
        <p>系统目前运行良好，以下是实时统计数据</p>
      </div>
      <div class="quick-stat-orb">
        <div class="orb-content">
          <span class="orb-val">{{ stats.views }}</span>
          <span class="orb-label">今日总访问</span>
        </div>
      </div>
    </div>

    <n-spin :show="loading">
      <div class="stats-container">
        <div class="stat-item">
          <div class="stat-icon">📝</div>
          <div class="stat-info">
            <span class="stat-label">文章总数</span>
            <span class="stat-value">{{ stats.posts }}</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon">💬</div>
          <div class="stat-info">
            <span class="stat-label">收到评论</span>
            <span class="stat-value">{{ stats.comments }}</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon">📁</div>
          <div class="stat-info">
            <span class="stat-label">分类层级</span>
            <span class="stat-value">{{ stats.categories }}</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon">🏷️</div>
          <div class="stat-info">
            <span class="stat-label">标签索引</span>
            <span class="stat-value">{{ stats.tags }}</span>
          </div>
        </div>
      </div>
    </n-spin>

    <div class="entry-section">
      <h3 class="section-title">快捷入口</h3>
      <div class="entry-grid">
        <router-link v-for="action in quickActions" :key="action.path" :to="action.path" class="entry-card">
          <div class="entry-content">
            <span class="entry-icon">{{ action.icon }}</span>
            <span class="entry-label">{{ action.label }}</span>
          </div>
          <span class="entry-arrow">▶</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-page {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30px;
  background: var(--wf-card);
  border: 1px solid var(--wf-border);
  border-radius: 20px;
  margin-bottom: 24px;
}

.welcome-msg h2 {
  margin: 0;
  font-size: 26px;
  font-weight: 800;
  color: var(--wf-text);
}

.welcome-msg p {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: var(--wf-text-dim);
}

.quick-stat-orb {
  background: rgba(122, 162, 247, 0.1);
  padding: 15px 25px;
  border-radius: 15px;
  border: 1px solid rgba(122, 162, 247, 0.2);
  min-width: 140px;
  text-align: center;
}

.orb-val {
  display: block;
  font-size: 30px;
  font-weight: 900;
  color: #7AA2F7;
}

.orb-label {
  font-size: 11px;
  font-weight: 800;
  color: var(--wf-text-dim);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 40px;
}

.stat-item {
  background: var(--wf-card);
  border: 1px solid var(--wf-border);
  padding: 24px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s;
}

.stat-item:hover {
  border-color: rgba(122, 162, 247, 0.3);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 28px;
}

.stat-info .stat-label {
  display: block;
  font-size: 12px;
  font-weight: 800;
  color: var(--wf-text-dim);
  margin-bottom: 4px;
}

.stat-info .stat-value {
  font-size: 28px;
  font-weight: 900;
  color: var(--wf-text);
}

.section-title {
  font-size: 14px;
  font-weight: 900;
  color: var(--wf-accent);
  letter-spacing: 2px;
  margin-bottom: 20px;
  padding-left: 4px;
}

.entry-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.entry-card {
  background: var(--wf-card);
  border: 1px solid var(--wf-border);
  padding: 18px 24px;
  border-radius: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
}

.entry-card:hover {
  background: rgba(122, 162, 247, 0.05);
  border-color: rgba(122, 162, 247, 0.2);
}

.entry-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.entry-icon { font-size: 20px; }
.entry-label { font-size: 16px; font-weight: 700; color: var(--wf-text); }
.entry-arrow { font-size: 12px; color: var(--wf-text-dim); }

@media (max-width: 600px) {
  .overview-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    gap: 12px;
    border-radius: 14px;
    margin-bottom: 16px;
  }
  .welcome-msg h2 { font-size: 18px; }
  .welcome-msg p { font-size: 11px; margin-top: 2px; }
  .quick-stat-orb { 
    min-width: auto;
    padding: 10px 14px;
    border-radius: 10px;
  }
  .orb-val { font-size: 20px; }
  .orb-label { font-size: 9px; }
  
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-bottom: 20px;
  }
  .stat-item {
    padding: 12px;
    gap: 8px;
    border-radius: 10px;
  }
  .stat-icon { font-size: 18px; }
  .stat-info .stat-label { font-size: 9px; margin-bottom: 1px; }
  .stat-info .stat-value { font-size: 18px; }
  
  .section-title { font-size: 11px; margin-bottom: 10px; }
  
  .entry-grid {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 8px;
  }
  .entry-card { 
    padding: 10px 14px; 
    border-radius: 20px;
    flex: 0 0 auto;
  }
  .entry-icon { font-size: 14px; }
  .entry-label { font-size: 12px; }
  .entry-content { gap: 6px; }
  .entry-arrow { display: none; }
}
</style>
