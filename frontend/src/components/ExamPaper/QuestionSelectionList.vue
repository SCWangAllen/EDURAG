<template>
  <div class="question-selection-list">
    <!-- Loading 狀態 -->
    <div v-if="loading" class="flex flex-col items-center py-12 px-4 gap-4">
      <div class="spinner w-10 h-10 border-4 border-gray-100 border-t-primary-500 rounded-full"></div>
      <p>{{ t('ui.ep_loadingQuestions') }}</p>
    </div>

    <!-- 題目列表 -->
    <div v-else-if="questions.length > 0" class="flex flex-col gap-4">
      <div class="flex justify-between items-center">
        <h3 class="text-base font-semibold text-gray-900">
          📚 {{ t('ui.ep_questionList') }}
          <span class="inline-flex items-center justify-center px-2 py-1 bg-primary-500 text-white rounded text-xs font-semibold ml-2">{{ totalQuestions }} {{ t('ui.ep_questionsUnit') }}</span>
        </h3>
        <div class="flex items-center gap-2 text-sm text-gray-500">
          <input
            type="checkbox"
            :checked="isAllSelected"
            @change="$emit('toggle-select-all')"
            id="select-all"
            class="w-4 h-4 cursor-pointer"
          >
          <label for="select-all" class="cursor-pointer select-none">{{ t('ui.ep_selectAllOnPage') }}</label>
        </div>
      </div>

      <div class="flex flex-col gap-3">
        <div
          v-for="question in questions"
          :key="question.id"
          :class="[
            'flex gap-4 p-4 border rounded-lg transition-all duration-200 cursor-pointer hover:border-primary-500 hover:shadow-[0_1px_3px_rgba(59,130,246,0.1)]',
            isSelected(question.id) ? 'bg-primary-50 border-primary-500' : 'bg-white border-gray-200'
          ]"
          @click="$emit('toggle-selection', question)"
        >
          <div class="flex-shrink-0 flex items-start pt-1" @click.stop>
            <input
              type="checkbox"
              :checked="isSelected(question.id)"
              @change="$emit('toggle-selection', question)"
              class="w-5 h-5 cursor-pointer"
            >
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex gap-2 mb-2 flex-wrap">
              <span class="px-2 py-0.5 rounded text-xs font-medium bg-primary-100 text-primary-800">{{ t(`generate.${question.type}`) }}</span>
              <span v-if="question.subject" class="px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800">{{ question.subject }}</span>
              <span v-if="question.grade" class="px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">{{ question.grade }}</span>
              <span v-if="question.difficulty" class="px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">{{ question.difficulty }}</span>
              <!-- 格數:配對幾組 / 填充幾格 / 辨識幾項 / 圖片幾格,挑題時看得到自己在湊幾格 -->
              <span v-if="unitsBadge(question)" class="px-2 py-0.5 rounded text-xs font-medium bg-sky-100 text-sky-800">{{ unitsBadge(question) }}</span>
              <span v-if="question.type === 'diagram_question' && question.images_verified" class="px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800">✓ {{ t('ui.ep_verified') }}</span>
            </div>

            <!-- 圖片題目特殊渲染 -->
            <template v-if="question.type === 'diagram_question'">
              <div class="flex gap-4 items-start">
                <div class="flex-shrink-0 w-[120px] h-[80px] border border-gray-200 rounded-md overflow-hidden bg-gray-50">
                  <img
                    v-if="question.question_image_url"
                    :src="question.question_image_url"
                    :alt="question.content || t('ui.ep_questionImageAlt')"
                    class="w-full h-full object-cover"
                    @error="handleImageError"
                  />
                  <div v-else class="image-placeholder">
                    🖼️ {{ question.question_image || t('ui.ep_noImage') }}
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm text-gray-900 mb-2 leading-normal">{{ question.content || t('ui.ep_imageQuestionFallback') }}</div>
                  <div v-if="question.chapter" class="text-xs text-gray-500 mt-1">
                    <span class="font-medium text-gray-700">{{ t('ui.ep_chapterLabel') }}</span>{{ question.chapter }}
                  </div>
                  <div v-if="question.page" class="text-xs text-gray-500 mt-1">
                    <span class="font-medium text-gray-700">{{ t('ui.ep_pageLabel') }}</span>{{ question.page }}
                  </div>
                  <div v-if="question.answer_image" class="inline-flex items-center gap-1 mt-2 px-2 py-0.5 bg-primary-100 text-primary-800 rounded text-xs font-medium">
                    ✓ {{ t('ui.ep_includesAnswerImage') }}
                  </div>
                </div>
              </div>
            </template>

            <!-- 一般題目渲染 -->
            <template v-else>
              <div class="text-sm text-gray-900 mb-2 leading-normal">{{ question.content }}</div>
              <!-- 來源教材的章節與課本頁碼,挑題時對得上考試範圍 -->
              <div v-if="question.chapter || question.source_page" class="text-xs text-gray-500 mb-2">
                <span v-if="question.chapter">{{ question.chapter }}</span>
                <span v-if="question.chapter && question.source_page"> · </span>
                <span v-if="question.source_page">P.{{ question.source_page }}</span>
              </div>

              <div v-if="question.options" class="flex flex-wrap gap-2 mb-2">
                <span
                  v-for="(opt, idx) in question.options"
                  :key="idx"
                  class="px-2 py-1 bg-gray-100 rounded text-xs text-gray-500"
                >
                  {{ opt }}
                </span>
              </div>

              <div v-if="question.correct_answer" class="text-xs text-emerald-600 px-2 py-1 bg-emerald-100 rounded inline-block">
                <strong>{{ t('ui.ep_answerLabel') }}</strong>{{ formatAnswer(question.correct_answer) }}
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- 分頁 -->
      <div class="flex items-center justify-center gap-2 py-4">
        <button
          @click="$emit('change-page', currentPage - 1)"
          :disabled="currentPage === 1"
          class="px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-700 text-sm cursor-pointer transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed enabled:hover:bg-gray-100 enabled:hover:border-gray-400"
        >
          ← {{ t('ui.ep_previousPage') }}
        </button>

        <div class="flex gap-1">
          <button
            v-for="page in pageNumbers"
            :key="page"
            @click="$emit('change-page', page)"
            :class="[
              'px-3 py-2 border rounded-md text-sm cursor-pointer transition-all duration-200',
              page === currentPage
                ? 'bg-primary-500 text-white border-primary-500'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100 hover:border-gray-400'
            ]"
          >
            {{ page }}
          </button>
        </div>

        <button
          @click="$emit('change-page', currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-700 text-sm cursor-pointer transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed enabled:hover:bg-gray-100 enabled:hover:border-gray-400"
        >
          {{ t('ui.ep_nextPage') }} →
        </button>

        <div class="ml-2 text-sm text-gray-500">
          {{ t('ui.ep_pageOf') }} {{ currentPage }} / {{ totalPages }}
        </div>
      </div>
    </div>

    <!-- 空狀態 -->
    <div v-else class="flex flex-col items-center py-12 px-4 text-center">
      <div class="text-[4rem] mb-4 opacity-50">📝</div>
      <p class="text-lg font-semibold text-gray-700 mb-2">{{ t('ui.ep_noQuestionsFound') }}</p>
      <p class="text-sm text-gray-500 mb-6">{{ t('ui.ep_adjustFilterOrRetryLater') }}</p>
    </div>
  </div>
</template>

<script setup>
import { useLanguage } from '@/composables/useLanguage.js'
import { scoringUnits, unitsKind } from '@/utils/scoringUnits.js'

const { t } = useLanguage()

// 每題格數標籤(每題計分的題型不顯示)
const unitsBadge = (question) => {
  const kind = unitsKind(question.type)
  if (!kind) return ''
  const n = scoringUnits(question)
  const key = { pairs: 'ui.ed_units_pairs', blanks: 'ui.ed_units_blanks', items: 'ui.ed_units_items' }[kind]
  return t(key).replace('{n}', n)
}

const props = defineProps({
  questions: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  totalQuestions: {
    type: Number,
    default: 0
  },
  currentPage: {
    type: Number,
    default: 1
  },
  totalPages: {
    type: Number,
    default: 0
  },
  pageNumbers: {
    type: Array,
    default: () => []
  },
  selectedIds: {
    type: Set,
    required: true
  },
  isAllSelected: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle-selection', 'toggle-select-all', 'change-page'])

const isSelected = (questionId) => {
  return props.selectedIds.has(questionId)
}

const formatAnswer = (answer) => {
  if (Array.isArray(answer)) {
    return answer.join(', ')
  }
  if (typeof answer === 'object') {
    return JSON.stringify(answer)
  }
  return String(answer).substring(0, 50) + (String(answer).length > 50 ? '...' : '')
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
  const placeholder = document.createElement('div')
  placeholder.className = 'image-placeholder'
  placeholder.textContent = t('ui.ep_imageLoadFailed')
  event.target.parentNode.appendChild(placeholder)
}
</script>

<style scoped>
/* 保留：旋轉動畫 keyframes 無法以純 Tailwind utility 可靠表達（維持 0.8s 速度） */
.spinner {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 保留：此 class 也被 handleImageError() 動態建立的節點使用，
   template 內的 Tailwind utility 無法套用到 JS 建立的元素 */
.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: #9ca3af;
  text-align: center;
  padding: 0.5rem;
}
</style>
