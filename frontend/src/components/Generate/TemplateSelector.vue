<template>
  <div class="bg-white shadow rounded-lg p-6">
    <h3 class="text-lg font-medium text-gray-900 mb-4">{{ t('generate.selectTemplate') }}</h3>

    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('templates.filterBySubject') }}</label>
      <select
        :value="selectedSubject"
        @change="onSubjectChange"
        class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="">{{ t('templates.allSubjects') }}</option>
        <option v-for="subject in subjects" :key="subject" :value="subject">
          {{ isEnglish ? t('subjects.' + getSubjectKey(subject)) : subject }}
        </option>
      </select>
    </div>

    <div class="space-y-2 max-h-64 overflow-y-auto">
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
            <p class="text-xs text-gray-500">{{ isEnglish ? t('subjects.' + getSubjectKey(template.subject)) : getSubjectDisplayName(template) }}</p>
            <div class="mt-1">
              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                {{ getQuestionTypeLabel(template.question_type) || template.question_type || '未指定' }}
              </span>
            </div>
          </div>
          <div class="flex-shrink-0">
            <span
              :class="getSubjectStyle(template.subject) ? '' : getSubjectColor(template.subject)"
              :style="getSubjectStyle(template.subject)"
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
            >
              {{ isEnglish ? t('subjects.' + getSubjectKey(template.subject)) : getSubjectDisplayName(template) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="templates.length === 0 && !loadingTemplates" class="text-center py-4 text-gray-500">
      <p>{{ t('generate.noTemplatesAvailable') }}</p>
      <button @click="$router.push('/templates')" class="text-blue-600 hover:text-blue-800 text-sm">
        {{ t('generate.goCreateTemplate') }}
      </button>
    </div>
  </div>
</template>

<script>
import { useLanguage } from '../../composables/useLanguage.js'
import { getSubjectColor as getSubjectColorDefault, getQuestionTypeLabel as getQuestionTypeLabelUtil } from '@/utils/formatters.js'
import { getSubjectDisplayName as getSubjectDisplayNameUtil } from '@/utils/subjectUtils.js'

export default {
  name: 'TemplateSelector',
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
    const { t, isEnglish } = useLanguage()

    const getSubjectKey = (subjectName) => {
      const mapping = {
        '健康': 'health',
        '英文': 'english',
        '歷史': 'history',
        'Health': 'health',
        'English': 'english',
        'History': 'history'
      }
      return mapping[subjectName] || 'health'
    }

    const getTextColor = (backgroundColor) => {
      const hex = backgroundColor.replace('#', '')
      const r = parseInt(hex.substr(0, 2), 16)
      const g = parseInt(hex.substr(2, 2), 16)
      const b = parseInt(hex.substr(4, 2), 16)
      const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000
      return brightness > 155 ? '#000000' : '#FFFFFF'
    }

    const getSubjectStyle = (subject) => {
      const subjectData = props.subjectList.find(s => s.name === subject)
      if (subjectData && subjectData.color) {
        return {
          backgroundColor: subjectData.color,
          color: getTextColor(subjectData.color)
        }
      }
      return null
    }

    const getSubjectColor = (subject) => {
      const subjectData = props.subjectList.find(s => s.name === subject)
      if (subjectData && subjectData.color) {
        return ''
      }
      return getSubjectColorDefault(subject)
    }

    const getSubjectDisplayName = (subjectNameOrTemplate) => {
      return getSubjectDisplayNameUtil(subjectNameOrTemplate, props.subjectList)
    }

    const getQuestionTypeLabel = (type) => {
      if (!type) return t('generate.unknown') || '未指定'
      return getQuestionTypeLabelUtil(type, t) || type
    }

    const onSubjectChange = (event) => {
      emit('update:selectedSubject', event.target.value)
      emit('fetch-templates')
    }

    return {
      t,
      isEnglish,
      getSubjectKey,
      getSubjectColor,
      getSubjectDisplayName,
      getSubjectStyle,
      getQuestionTypeLabel,
      onSubjectChange
    }
  }
}
</script>
