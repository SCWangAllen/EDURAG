<template>
  <div class="bg-white shadow rounded-lg mb-6">
    <div class="p-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <!-- Search -->
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.search') }}</label>
          <input
            type="text"
            :value="searchQuery"
            @input="$emit('update:searchQuery', $event.target.value)"
            :placeholder="t('imageQuestions.searchPlaceholder')"
            list="image-question-missing-filenames"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          />
          <datalist id="image-question-missing-filenames">
            <option v-for="name in missingImageNames" :key="name" :value="name" />
          </datalist>
        </div>

        <!-- Subject -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.subject') }}</label>
          <SubjectSelect
            :model-value="selectedSubject"
            :options="subjects"
            :placeholder="t('imageQuestions.allSubjects')"
            @update:model-value="$emit('update:selectedSubject', $event)"
          />
        </div>

        <!-- Grade -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.grade') }}</label>
          <select
            :value="selectedGrade"
            @change="$emit('update:selectedGrade', $event.target.value)"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">{{ t('imageQuestions.allGrades') }}</option>
            <option v-for="grade in grades" :key="grade" :value="grade">{{ getGradeLabel(grade) }}</option>
          </select>
        </div>

        <!-- Verification Status -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.verificationStatus') }}</label>
          <select
            :value="selectedVerified"
            @change="$emit('update:selectedVerified', $event.target.value)"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">{{ t('imageQuestions.allStatus') }}</option>
            <option value="true">{{ t('imageQuestions.verifiedOnly') }}</option>
            <option value="false">{{ t('imageQuestions.unverifiedOnly') }}</option>
          </select>
        </div>
      </div>

      <!-- Chapter (if there are chapters) -->
      <div v-if="chapters && chapters.length > 0" class="mt-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.chapter') }}</label>
        <select
          :value="selectedChapter"
          @change="$emit('update:selectedChapter', $event.target.value)"
          class="w-full md:w-1/3 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="">{{ t('imageQuestions.allChapters') }}</option>
          <option v-for="chapter in chapters" :key="chapter" :value="chapter">{{ chapter }}</option>
        </select>
      </div>

      <!-- Sort -->
      <div class="mt-4 flex flex-wrap items-end gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.sortBy') }}</label>
          <select
            :value="sortBy"
            @change="$emit('update:sortBy', $event.target.value)"
            class="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="created_at">{{ t('imageQuestions.sortByDate') }}</option>
            <option value="question_image">{{ t('imageQuestions.sortByName') }}</option>
            <option value="subject">{{ t('imageQuestions.sortBySubject') }}</option>
            <option value="grade">{{ t('imageQuestions.sortByGrade') }}</option>
            <option value="chapter">{{ t('imageQuestions.sortByChapter') }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('imageQuestions.sortDir') }}</label>
          <select
            :value="sortDir"
            @change="$emit('update:sortDir', $event.target.value)"
            class="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="desc">{{ t('imageQuestions.descending') }}</option>
            <option value="asc">{{ t('imageQuestions.ascending') }}</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useLanguage } from '@/composables/useLanguage.js'
import { useSubjects } from '@/composables/useSubjects.js'
import SubjectSelect from '@/components/Base/SubjectSelect.vue'

export default {
  name: 'ImageQuestionFilters',
  components: {
    SubjectSelect
  },
  props: {
    searchQuery: { type: String, default: '' },
    selectedSubject: { type: String, default: '' },
    selectedGrade: { type: String, default: '' },
    selectedChapter: { type: String, default: '' },
    selectedVerified: { type: String, default: '' },
    subjects: { type: Array, default: () => [] },
    grades: { type: Array, default: () => [] },
    chapters: { type: Array, default: () => [] },
    sortBy: { type: String, default: 'created_at' },
    sortDir: { type: String, default: 'desc' },
    missingImageNames: { type: Array, default: () => [] },
  },
  emits: [
    'update:searchQuery',
    'update:selectedSubject',
    'update:selectedGrade',
    'update:selectedChapter',
    'update:selectedVerified',
    'update:sortBy',
    'update:sortDir',
    'search',
  ],
  setup() {
    const { t } = useLanguage()
    const { getDisplayName, getGradeLabel } = useSubjects()
    return { t, getDisplayName, getGradeLabel }
  },
}
</script>
