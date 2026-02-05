<template>
  <div>
    <!-- 統計資訊與儲存按鈕 -->
    <div class="stats-panel">
      <div class="stat-card">
        <div class="stat-label">{{ mode === 'select' ? '已選題型' : '已啟用題型' }}</div>
        <div class="stat-value">{{ enabledTypeCount }} 種</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">{{ mode === 'select' ? '已選題數' : '總題數' }}</div>
        <div class="stat-value">{{ totalQuestions }} 題</div>
      </div>
      <div class="stat-card highlight">
        <div class="stat-label">總分</div>
        <div class="stat-value">{{ totalPoints }} 分</div>
      </div>

      <!-- 儲存設定按鈕 -->
      <button
        @click="$emit('save')"
        class="save-config-btn"
        :class="{ 'has-changes': hasUnsavedChanges }"
      >
        <span class="btn-icon">💾</span>
        <span class="btn-text">{{ hasUnsavedChanges ? '儲存設定 *' : '已儲存' }}</span>
      </button>
    </div>

    <!-- 快速配置按鈕（AI生成模式才顯示） -->
    <div v-if="mode !== 'select'" class="quick-config">
      <p class="quick-config-title">💡 快速配置：</p>
      <div class="quick-config-buttons">
        <button @click="$emit('apply-preset', 'standard')" class="preset-btn">
          📋 標準考券 (41題)
        </button>
        <button @click="$emit('apply-preset', 'simple')" class="preset-btn">
          ✏️ 簡易考券 (20題)
        </button>
        <button @click="$emit('apply-preset', 'comprehensive')" class="preset-btn">
          📚 綜合考券 (50題)
        </button>
        <button @click="$emit('reset')" class="preset-btn danger">
          🔄 全部重置
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  enabledTypeCount: {
    type: Number,
    required: true
  },
  totalQuestions: {
    type: Number,
    required: true
  },
  totalPoints: {
    type: Number,
    required: true
  },
  hasUnsavedChanges: {
    type: Boolean,
    required: true
  },
  mode: {
    type: String,
    default: 'generate'
  }
})

defineEmits(['save', 'apply-preset', 'reset'])
</script>

<style scoped>
/* 統計面板 */
.stats-panel {
  display: grid;
  grid-template-columns: repeat(3, 1fr) auto;
  gap: 1rem;
  margin-top: 1.5rem;
  align-items: center;
}

.stat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  text-align: center;
}

.stat-card.highlight {
  background: #eff6ff;
  border-color: #3b82f6;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
}

.stat-card.highlight .stat-value {
  color: #3b82f6;
}

/* 儲存設定按鈕 */
.save-config-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.save-config-btn:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.save-config-btn:active:not(:disabled) {
  transform: translateY(0);
}

.save-config-btn:disabled {
  background: #d1d5db;
  color: #9ca3af;
  cursor: not-allowed;
}

.save-config-btn.has-changes {
  background: #f59e0b;
  animation: pulse 2s infinite;
}

.save-config-btn.has-changes:hover:not(:disabled) {
  background: #d97706;
}

.save-config-btn .btn-icon {
  font-size: 1.125rem;
}

.save-config-btn .btn-text {
  font-weight: 600;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.85;
  }
}

/* 快速配置 */
.quick-config {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.quick-config-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.75rem;
}

.quick-config-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.preset-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.preset-btn.danger {
  color: #dc2626;
  border-color: #fca5a5;
}

.preset-btn.danger:hover {
  background: #fef2f2;
  border-color: #f87171;
}
</style>
