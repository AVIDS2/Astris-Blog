<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { api } from '../api'

const message = useMessage()

const loading = ref(false)
const saving = ref(false)
const content = ref('')
const originalContent = ref('')

async function fetchAboutContent() {
  loading.value = true
  try {
    const response = await api.get('/api/admin/about')
    content.value = response.data.content
    originalContent.value = response.data.content
  } catch (error) {
    message.error('获取内容失败')
  } finally {
    loading.value = false
  }
}

async function saveContent() {
  saving.value = true
  try {
    await api.put('/api/admin/about', { content: content.value })
    originalContent.value = content.value
    message.success('保存成功')
  } catch (error) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

function resetContent() {
  content.value = originalContent.value
  message.info('已恢复原内容')
}

onMounted(fetchAboutContent)
</script>

<template>
  <div class="about-page">
    <div class="page-header">
      <div class="header-info">
        <h1>关于页面</h1>
        <p class="sub-label">编辑前端「关于」页面的 Markdown 内容</p>
      </div>
      <div class="header-actions">
        <n-button :disabled="content === originalContent" ghost round @click="resetContent">
          重置
        </n-button>
        <n-button 
          type="primary" 
          :loading="saving" 
          :disabled="content === originalContent"
          round
          @click="saveContent"
        >
          保存更改
        </n-button>
      </div>
    </div>

    <n-spin :show="loading">
      <div class="editor-container">
        <div class="editor-hint">
          <span class="hint-icon">📝</span>
          <span>支持 Markdown 语法，保存后前端页面自动更新</span>
        </div>
        <textarea
          v-model="content"
          class="markdown-editor"
          placeholder="在这里编辑关于页面内容..."
        ></textarea>
      </div>
    </n-spin>
  </div>
</template>

<style scoped>
.about-page {
  animation: fadeIn 0.4s ease-out;
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
  flex-wrap: wrap;
  gap: 16px;
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

.header-actions {
  display: flex;
  gap: 12px;
}

.editor-container {
  background: var(--wf-card);
  border: 1px solid var(--wf-border);
  border-radius: 16px;
  overflow: hidden;
}

.editor-hint {
  padding: 12px 20px;
  background: rgba(122, 162, 247, 0.08);
  border-bottom: 1px solid var(--wf-border);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--wf-text-dim);
}

.hint-icon {
  font-size: 16px;
}

.markdown-editor {
  width: 100%;
  min-height: 60vh;
  padding: 20px;
  border: none;
  background: transparent;
  color: var(--wf-text);
  font-size: 14px;
  line-height: 1.8;
  font-family: 'SF Mono', 'Menlo', 'Monaco', 'Consolas', monospace;
  resize: vertical;
  outline: none;
  box-sizing: border-box;
}

.markdown-editor::placeholder {
  color: var(--wf-text-dim);
}

@media (max-width: 600px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-actions {
    width: 100%;
  }
  .header-actions .n-button {
    flex: 1;
  }
  .markdown-editor {
    min-height: 50vh;
    font-size: 13px;
  }
}
</style>
