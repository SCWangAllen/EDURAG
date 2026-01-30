<template>
  <div class="customization-panel">
    <div class="panel-content">
      <!-- 考券基本設定 -->
      <div class="section-header">
        <h3 class="section-title">📝 {{ t('examDesigner.examDesign') }}</h3>
        <p class="section-description">{{ t('examDesigner.examDesignDescription') }}</p>
      </div>

      <!-- 題型順序管理 -->
      <div class="customizer-section">
        <div class="section-header">
          <h3 class="section-title">📋 {{ t('examDesigner.questionTypeOrder') }}</h3>
          <p class="section-description">{{ t('examDesigner.questionTypeOrderDescription') }}</p>
        </div>

        <div class="question-types-list">
          <div
            v-for="(typeInfo, index) in orderedTypes"
            :key="typeInfo.type"
            class="type-item"
            :class="{ 'has-questions': typeInfo.count > 0 }"
            draggable="true"
            @dragstart="onDragStart(index)"
            @dragover.prevent
            @drop="onDrop(index)"
          >
            <div class="type-drag-handle">⋮⋮</div>

            <div class="type-info">
              <div class="type-header">
                <span class="type-icon">{{ getTypeIcon(typeInfo.type) }}</span>
                <span class="type-name">{{ getTypeName(typeInfo.type) }}</span>
                <span class="type-count" :class="{ 'empty': typeInfo.count === 0 }">
                  {{ typeInfo.count }} {{ t('examDesigner.questions') }}
                </span>
              </div>

              <div v-if="typeInfo.count > 0" class="type-preview">
                <div class="preview-questions">
                  <span
                    v-for="n in Math.min(3, typeInfo.count)"
                    :key="n"
                    class="preview-dot"
                  ></span>
                  <span v-if="typeInfo.count > 3" class="preview-more">
                    +{{ typeInfo.count - 3 }}
                  </span>
                </div>
              </div>

              <div v-else class="type-empty">
                {{ t('examDesigner.noQuestions') }}
              </div>
            </div>

            <div class="type-actions">
              <button
                v-if="index > 0"
                @click="$emit('move-up', index)"
                class="action-btn"
                :title="t('examDesigner.moveUp')"
              >
                ↑
              </button>
              <button
                v-if="index < orderedTypes.length - 1"
                @click="$emit('move-down', index)"
                class="action-btn"
                :title="t('examDesigner.moveDown')"
              >
                ↓
              </button>
            </div>
          </div>
        </div>

        <div class="order-info">
          <div class="info-item">
            <strong>{{ t('examDesigner.examStructurePreview') }}：</strong>
          </div>
          <div class="structure-preview">
            <div
              v-for="(typeInfo, index) in orderedTypes.filter(t => t.count > 0)"
              :key="typeInfo.type"
              class="structure-item"
            >
              <span class="structure-number">{{ index + 1 }}.</span>
              <span class="structure-name">{{ getTypeName(typeInfo.type) }}</span>
              <span class="structure-count">({{ typeInfo.count }} {{ t('examDesigner.questions') }})</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作按鈕 -->
    <div class="panel-footer">
      <div class="flex justify-end items-center p-4 bg-gray-50 border-t">
        <button
          @click="$emit('export')"
          class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
        >
          📤 {{ t('examDesigner.exportPDF') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useLanguage } from '../../composables/useLanguage.js'

const { t } = useLanguage()

const props = defineProps({
  orderedTypes: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['move-up', 'move-down', 'export', 'reorder'])

const draggedIndex = ref(-1)

const getTypeName = (type) => {
  return t(`generate.${type}`) || type
}

const getTypeIcon = (type) => {
  const icons = {
    single_choice: '📝',
    multiple_choice: '☑️',
    cloze: '✏️',
    short_answer: '💬',
    true_false: '✓✗',
    matching: '🔗',
    sequence: '🔢',
    enumeration: '📋',
    symbol_identification: '🔍',
    mixed: '🎲',
    essay: '📄',
    auto: '🤖'
  }
  return icons[type] || '❓'
}

const onDragStart = (index) => {
  draggedIndex.value = index
}

const onDrop = (targetIndex) => {
  if (draggedIndex.value === -1 || draggedIndex.value === targetIndex) {
    return
  }
  emit('reorder', { from: draggedIndex.value, to: targetIndex })
  draggedIndex.value = -1
}
</script>

<style scoped>
.customization-panel {
  width: 400px;
  background: #f9fafb;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.panel-footer {
  flex-shrink: 0;
  border-top: 1px solid #e5e7eb;
}

.customizer-section {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.section-header {
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.section-description {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.question-types-list {
  margin-bottom: 20px;
}

.type-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  transition: all 0.2s;
  cursor: move;
}

.type-item:hover {
  border-color: #9ca3af;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.type-item.has-questions {
  border-left: 4px solid #10b981;
}

.type-drag-handle {
  color: #9ca3af;
  margin-right: 12px;
  font-size: 14px;
  cursor: grab;
}

.type-drag-handle:active {
  cursor: grabbing;
}

.type-info {
  flex: 1;
}

.type-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.type-icon {
  font-size: 16px;
}

.type-name {
  font-weight: 500;
  color: #374151;
}

.type-count {
  font-size: 12px;
  color: #10b981;
  font-weight: 500;
}

.type-count.empty {
  color: #9ca3af;
}

.type-preview {
  margin-left: 24px;
}

.preview-questions {
  display: flex;
  align-items: center;
  gap: 2px;
}

.preview-dot {
  width: 4px;
  height: 4px;
  background: #10b981;
  border-radius: 50%;
}

.preview-more {
  font-size: 10px;
  color: #6b7280;
  margin-left: 4px;
}

.type-empty {
  margin-left: 24px;
  font-size: 12px;
  color: #9ca3af;
}

.type-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  width: 24px;
  height: 24px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  color: #6b7280;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
  color: #374151;
}

.order-info {
  padding: 16px;
  background: #fef7f0;
  border: 1px solid #fed7aa;
  border-radius: 6px;
}

.info-item {
  margin-bottom: 8px;
  font-size: 13px;
  color: #9a3412;
}

.structure-preview {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.structure-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #7c2d12;
}

.structure-number {
  font-weight: 600;
  min-width: 20px;
}

.structure-name {
  font-weight: 500;
}

.structure-count {
  color: #a16207;
}

@media (max-width: 1200px) {
  .customization-panel {
    width: 350px;
  }
}

@media (max-width: 900px) {
  .customization-panel {
    width: 100%;
    height: 300px;
  }
}
</style>
