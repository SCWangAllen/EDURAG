<template>
  <div class="bg-white shadow rounded-lg p-6">
    <h3 class="text-lg font-medium text-gray-900 mb-4">{{ t('generate.selectTemplate') }}</h3>

    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('templates.filterBySubject') }}</label>
      <SubjectSelect
        :model-value="selectedSubject"
        :options="subjects"
        :placeholder="t('templates.allSubjects')"
        @update:model-value="onSubjectChange"
      />
    </div>

    <!-- 模板列表：固定高度約 3 個項目 -->
    <div class="space-y-2 h-[210px] overflow-y-auto">
      <div
        v-for="template in filteredTemplates"
        :key="template.id"
        @click="$emit('select-template', template)"
        :class="[
          'cursor-pointer p-3 border rounded-md transition-colors',
          selectedTemplate?.id === template.id
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        ]"
      >
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-sm font-medium text-gray-900">{{ template.name }}</h3>
            <p class="text-xs text-gray-500">{{ getDisplayName(template.subject) }}</p>
            <div class="mt-1">
              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                {{ getQuestionTypeLabel(template.question_type) || template.question_type || t('ui.vw_unspecified') }}
              </span>
            </div>
          </div>
          <div class="flex-shrink-0">
            <span
              :class="getSubjectStyle(template.subject) ? '' : getSubjectColor(template.subject)"
              :style="getSubjectStyle(template.subject)"
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
            >
              {{ getDisplayName(template.subject) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="templates.length === 0 && !loadingTemplates" class="text-center py-4 text-gray-500">
      <p>{{ t('generate.noTemplatesAvailable') }}</p>
      <button @click="$router.push('/templates')" class="text-primary-600 hover:text-blue-800 text-sm">
        {{ t('generate.goCreateTemplate') }}
      </button>
    </div>
  </div>
</template>

<script>
import { useLanguage } from '../../composables/useLanguage.js'
import { useSubjects } from '@/composables/useSubjects.js'
import { getQuestionTypeLabel as getQuestionTypeLabelUtil } from '@/utils/formatters.js'
import SubjectSelect from '@/components/Base/SubjectSelect.vue'

export default {
  name: 'TemplateSelector',
  components: {
    SubjectSelect
  },
  props: {
    templates: {
      type: Array,
      default: () => []
    },
    filteredTemplates: {
      type: Array,
      default: () => []
    },
    subjects: {
      type: Array,
      default: () => []
    },
    subjectList: {
      type: Array,
      default: () => []
    },
    selectedSubject: {
      type: String,
      default: ''
    },
    selectedTemplate: {
      type: Object,
      default: null
    },
    loadingTemplates: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:selectedSubject', 'select-template', 'fetch-templates'],
  setup(props, { emit }) {
    const { t } = useLanguage()
    const { getDisplayName, subjectBadgeClass, subjectBadgeStyle, ensureLoaded } = useSubjects()
    ensureLoaded()
    // 科目標籤顏色改用全站共用的 useSubjects 取色(科目管理設定的顏色)
    const getSubjectColor = (subject) => subjectBadgeClass(subject)
    const getSubjectStyle = (subject) => subjectBadgeStyle(subject)



    const getQuestionTypeLabel = (type) => {
      if (!type) return t('generate.unknown') || t('ui.vw_unspecified')
      return getQuestionTypeLabelUtil(type, t) || type
    }

    const onSubjectChange = (value) => {
      emit('update:selectedSubject', value)
      emit('fetch-templates')
    }

    return {
      t,
      getDisplayName,
      getSubjectColor,
      getSubjectStyle,
      getQuestionTypeLabel,
      onSubjectChange
    }
  }
}
</script>
