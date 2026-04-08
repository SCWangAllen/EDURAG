<template>
  <div class="bg-white shadow rounded-lg p-6 mb-6">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('questions.search') }}</label>
        <input
          v-model="localSearchQuery"
          type="text"
          :placeholder="t('questions.searchPlaceholder')"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('questions.filterByType') }}</label>
        <select
          v-model="localSelectedType"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">{{ t('questions.allTypes') }}</option>
          <option v-for="qt in questionTypes" :key="qt.value" :value="qt.value">{{ t(qt.labelKey) }}</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('questions.filterBySubject') }}</label>
        <select
          v-model="localSelectedSubject"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">{{ t('questions.allSubjects') }}</option>
          <option v-for="subject in subjects" :key="subject" :value="subject">
            {{ subject }}
          </option>
        </select>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('questions.grade') }}</label>
        <select
          v-model="localSelectedGrade"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">{{ t('questions.allGrades') }}</option>
          <option v-for="g in gradeOptions" :key="g.value" :value="g.value">{{ g.label }}</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('questions.filterByDifficulty') }}</label>
        <select
          v-model="localSelectedDifficulty"
          class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">{{ t('questions.allDifficulties') }}</option>
          <option value="easy">{{ t('questions.easy') }}</option>
          <option value="medium">{{ t('questions.medium') }}</option>
          <option value="hard">{{ t('questions.hard') }}</option>
        </select>
      </div>

      <div class="flex items-end">
        <button
          @click="searchQuestions"
          class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium"
        >
          {{ t('questions.search') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useLanguage } from '../../composables/useLanguage.js'

export default {
  name: 'QuestionFilters',
  props: {
    searchQuery: {
      type: String,
      default: ''
    },
    selectedType: {
      type: String,
      default: ''
    },
    selectedSubject: {
      type: String,
      default: ''
    },
    selectedGrade: {
      type: String,
      default: ''
    },
    selectedDifficulty: {
      type: String,
      default: ''
    },
    subjects: {
      type: Array,
      default: () => []
    },
    questionTypes: {
      type: Array,
      default: () => []
    },
    gradeOptions: {
      type: Array,
      default: () => []
    }
  },
  emits: [
    'update:searchQuery',
    'update:selectedType',
    'update:selectedSubject',
    'update:selectedGrade',
    'update:selectedDifficulty',
    'search'
  ],
  setup(props, { emit }) {
    const { t } = useLanguage()

    const localSearchQuery = computed({
      get: () => props.searchQuery,
      set: (val) => emit('update:searchQuery', val)
    })

    const localSelectedType = computed({
      get: () => props.selectedType,
      set: (val) => emit('update:selectedType', val)
    })

    const localSelectedSubject = computed({
      get: () => props.selectedSubject,
      set: (val) => emit('update:selectedSubject', val)
    })

    const localSelectedGrade = computed({
      get: () => props.selectedGrade,
      set: (val) => emit('update:selectedGrade', val)
    })

    const localSelectedDifficulty = computed({
      get: () => props.selectedDifficulty,
      set: (val) => emit('update:selectedDifficulty', val)
    })

    const searchQuestions = () => {
      emit('search')
    }

    return {
      t,
      localSearchQuery,
      localSelectedType,
      localSelectedSubject,
      localSelectedGrade,
      localSelectedDifficulty,
      searchQuestions
    }
  }
}
</script>
