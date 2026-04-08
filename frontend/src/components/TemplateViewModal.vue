<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" @click="$emit('close')">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- 背景遮罩 -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

      <!-- Modal 內容 -->
      <div
        class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full"
        @click.stop
      >
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
              <div class="flex justify-between items-center mb-6">
                <h3 class="text-lg leading-6 font-medium text-gray-900">
                  {{ t('templates.viewModal.title') }}
                </h3>
                <span :class="getSubjectColor(template?.subject)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                  {{ getSubjectDisplayName(template) }}
                </span>
              </div>

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
                  <label class="block text-sm font-medium text-gray-900 mb-3">Prompt 模板</label>
                  <div class="bg-gray-800 text-green-400 p-4 rounded-lg overflow-x-auto">
                    <pre class="text-sm whitespace-pre-wrap font-mono">{{ template.content }}</pre>
                  </div>
                </div>

                <!-- 參數設定 -->
                <div v-if="template.params">
                  <label class="block text-sm font-medium text-gray-900 mb-3">LLM 參數</label>
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div v-if="template.params.temperature !== undefined">
                        <label class="block text-xs font-medium text-gray-500 uppercase tracking-wide">溫度</label>
                        <p class="mt-1 text-sm text-gray-900">{{ template.params.temperature }}</p>
                      </div>
                      <div v-if="template.params.max_tokens">
                        <label class="block text-xs font-medium text-gray-500 uppercase tracking-wide">最大字數</label>
                        <p class="mt-1 text-sm text-gray-900">{{ template.params.max_tokens }}</p>
                      </div>
                      <div v-if="template.params.top_p !== undefined">
                        <label class="block text-xs font-medium text-gray-500 uppercase tracking-wide">Top P</label>
                        <p class="mt-1 text-sm text-gray-900">{{ template.params.top_p }}</p>
                      </div>
                      <div v-if="template.params.frequency_penalty !== undefined">
                        <label class="block text-xs font-medium text-gray-500 uppercase tracking-wide">頻率懲罰</label>
                        <p class="mt-1 text-sm text-gray-900">{{ template.params.frequency_penalty }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 預覽效果 -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 mb-3">預覽效果</label>
                  <div class="bg-blue-50 p-4 rounded-lg">
                    <div class="text-sm text-gray-700 whitespace-pre-wrap">
                      {{ previewContent }}
                    </div>
                  </div>
                </div>

                <!-- JSON 格式 -->
                <details class="group">
                  <summary class="flex cursor-pointer items-center justify-between rounded-lg p-2 text-gray-900 hover:bg-gray-50">
                    <span class="text-sm font-medium">JSON 格式</span>
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
            </div>
          </div>
        </div>

        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button
            type="button"
            @click="$emit('close')"
            class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:w-auto sm:text-sm"
          >
            關閉
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'
import { getSubjectColor as getSubjectColorDefault, formatDateTimeFull } from '@/utils/formatters.js'
import { getSubjectDisplayName as getSubjectDisplayNameUtil } from '@/utils/subjectUtils.js'

export default {
  name: 'TemplateViewModal',
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
      return props.template.content.replace('{context}', t('templates.viewModal.sampleContent'))
    })

    const getSubjectColor = (subject) => getSubjectColorDefault(subject)

    const formatDate = (dateString) => formatDateTimeFull(dateString)

    const getSubjectDisplayName = (template) => {
      return getSubjectDisplayNameUtil(template, props.subjectList)
    }

    return {
      t,
      previewContent,
      getSubjectColor,
      getSubjectDisplayName,
      formatDate
    }
  }
}
</script>
