<template>
  <BaseModal
    :model-value="show"
    size="xl"
    @update:model-value="$emit('close')"
  >
    <template #header>
      <div class="flex-1 flex items-center justify-between pr-2">
        <h3 class="text-lg leading-6 font-medium text-gray-900">
          {{ t('templates.viewModal.title') }}
        </h3>
        <span :class="getSubjectColor(template?.subject)" :style="getSubjectStyle(template?.subject)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
          {{ getSubjectDisplayName(template) }}
        </span>
      </div>
    </template>

    <div v-if="template" class="space-y-6">
      <!-- 基本資訊 -->
      <div class="bg-gray-50 p-4 rounded-lg">
        <h4 class="text-sm font-medium text-gray-900 mb-3">{{ t('templates.viewModal.basicInfo') }}</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-medium text-gray-500 uppercase tracking-wide">{{ t('templates.viewModal.templateName') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ template.name }}</p>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 uppercase tracking-wide">{{ t('templates.viewModal.version') }}</label>
            <p class="mt-1 text-sm text-gray-900">v{{ template.version }}</p>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 uppercase tracking-wide">{{ t('templates.viewModal.createdAt') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ formatDate(template.created_at) }}</p>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 uppercase tracking-wide">{{ t('templates.viewModal.updatedAt') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ formatDate(template.updated_at) }}</p>
          </div>
        </div>
      </div>

      <!-- Prompt 內容 -->
      <div>
        <label class="block text-sm font-medium text-gray-900 mb-3">{{ t('ui.md_prompt_template') }}</label>
        <div class="bg-gray-800 text-green-400 p-4 rounded-lg overflow-x-auto">
          <pre class="text-sm whitespace-pre-wrap font-mono">{{ template.content }}</pre>
        </div>
      </div>

      <!-- 預覽效果 -->
      <div>
        <label class="block text-sm font-medium text-gray-900 mb-3">{{ t('ui.md_preview_effect') }}</label>
        <div class="bg-blue-50 p-4 rounded-lg">
          <div class="text-sm text-gray-700 whitespace-pre-wrap">
            {{ previewContent }}
          </div>
        </div>
      </div>

      <!-- JSON 格式 -->
      <details class="group">
        <summary class="flex cursor-pointer items-center justify-between rounded-lg p-2 text-gray-900 hover:bg-gray-50">
          <span class="text-sm font-medium">{{ t('ui.md_json_format') }}</span>
          <span class="ml-1.5 flex-shrink-0 transition duration-300 group-open:-rotate-180">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </span>
        </summary>
        <div class="mt-2">
          <div class="bg-gray-800 text-gray-300 p-4 rounded-lg overflow-x-auto">
            <pre class="text-xs">{{ JSON.stringify(template, null, 2) }}</pre>
          </div>
        </div>
      </details>
    </div>

    <template #footer>
      <button
        type="button"
        @click="$emit('close')"
        class="px-4 py-2 rounded-md border border-gray-300 shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        {{ t('close') }}
      </button>
    </template>
  </BaseModal>
</template>

<script>
import { computed } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'
import { formatDateTimeFull } from '@/utils/formatters.js'
import { useSubjects } from '@/composables/useSubjects.js'
import { getSubjectDisplayName as getSubjectDisplayNameUtil } from '@/utils/subjectUtils.js'
import BaseModal from '@/components/Base/BaseModal.vue'

export default {
  name: 'TemplateViewModal',
  components: {
    BaseModal
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    template: {
      type: Object,
      default: null
    },
    subjectList: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close'],
  setup(props) {
    const { t } = useLanguage()
    const previewContent = computed(() => {
      if (!props.template?.content) return ''
      return props.template.content
        .replace(/\{context\}/g, t('templates.viewModal.sampleContent'))
        .replace(/\{count\}/g, '5')
    })

    const { subjectBadgeClass, subjectBadgeStyle, ensureLoaded } = useSubjects()
    ensureLoaded()
    const getSubjectColor = (subject) => subjectBadgeClass(subject)
    const getSubjectStyle = (subject) => subjectBadgeStyle(subject)

    const formatDate = (dateString) => formatDateTimeFull(dateString)

    const getSubjectDisplayName = (template) => {
      return getSubjectDisplayNameUtil(template, props.subjectList)
    }

    return {
      t,
      previewContent,
      getSubjectColor,
      getSubjectStyle,
      getSubjectDisplayName,
      formatDate
    }
  }
}
</script>
