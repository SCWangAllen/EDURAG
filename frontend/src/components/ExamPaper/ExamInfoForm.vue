<template>
  <div class="exam-info-form">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- 學校名稱 -->
      <div class="form-field">
        <label class="form-label">
          {{ t('examPaper.schoolName') || '學校名稱' }}
        </label>
        <input
          v-model="localValue.schoolName"
          type="text"
          class="form-input"
          :placeholder="t('examPaper.schoolNamePlaceholder') || DEFAULT_SCHOOL_NAME"
        />
      </div>

      <!-- 考試標題 -->
      <div class="form-field">
        <label class="form-label">
          {{ t('examPaper.examTitle') }} <span class="text-red-500">*</span>
        </label>
        <input
          v-model="localValue.title"
          type="text"
          class="form-input"
          :placeholder="t('examPaper.examTitlePlaceholder') || '2024 Semester 2 G4 Health Midterm Exam'"
        />
      </div>

      <!-- 副標題 -->
      <div class="form-field md:col-span-2">
        <label class="form-label">
          {{ t('examPaper.examSubtitle') || '副標題' }}
        </label>
        <input
          v-model="localValue.subtitle"
          type="text"
          class="form-input"
          :placeholder="t('examPaper.examSubtitlePlaceholder') || '(Understanding God\'s World pp. 115-171)'"
        />
      </div>

      <!-- Weekly Test 模式開關（暫時隱藏） -->
      <div v-if="false" class="form-field md:col-span-2">
        <label class="inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            v-model="isWeeklyTestMode"
            class="form-checkbox h-5 w-5 text-blue-600"
          />
          <span class="ml-2 text-sm font-medium text-gray-700">
            Weekly Test 模式（多科目合併）
          </span>
        </label>
        <p class="mt-1 text-xs text-gray-500">
          開啟後可選擇多個科目，考卷會按科目分區顯示
        </p>
      </div>

      <!-- 科目（單選模式） -->
      <div v-if="!isWeeklyTestMode" class="form-field">
        <label class="form-label">
          {{ t('examPaper.subject') || '科目' }} <span class="text-red-500">*</span>
        </label>
        <select v-model="localValue.subject" class="form-select">
          <option value="Health">{{ t('subjects.health') || '健康教育' }}</option>
          <option value="Math">{{ t('subjects.math') || '數學' }}</option>
          <option value="Science">{{ t('subjects.science') || '自然科學' }}</option>
          <option value="English">{{ t('subjects.english') || '英語' }}</option>
          <option value="Chinese">{{ t('subjects.chinese') || '國語' }}</option>
          <option value="Social">{{ t('subjects.social') || '社會' }}</option>
        </select>
      </div>

      <!-- 科目（多選模式 - Weekly Test） -->
      <div v-else class="form-field md:col-span-2">
        <label class="form-label">
          選擇科目 <span class="text-red-500">*</span>
        </label>
        <div class="flex flex-wrap gap-2 mt-2">
          <label
            v-for="sub in availableSubjects"
            :key="sub.value"
            class="inline-flex items-center px-3 py-2 rounded-lg border cursor-pointer transition-colors"
            :class="[
              localValue.subjects?.includes(sub.value)
                ? 'bg-blue-100 border-blue-500 text-blue-700'
                : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
            ]"
          >
            <input
              type="checkbox"
              :checked="localValue.subjects?.includes(sub.value)"
              @change="toggleSubject(sub.value)"
              class="sr-only"
            />
            <span class="text-sm font-medium">{{ sub.label }}</span>
          </label>
        </div>
        <p v-if="localValue.subjects?.length > 0" class="mt-2 text-sm text-blue-600">
          已選擇：{{ localValue.subjects.join(', ') }}
        </p>
      </div>

      <!-- 年級 -->
      <div class="form-field">
        <label class="form-label">
          {{ t('examPaper.grade') || '年級' }} <span class="text-red-500">*</span>
        </label>
        <select v-model="localValue.grade" class="form-select">
          <option value="G1">G1 (一年級)</option>
          <option value="G2">G2 (二年級)</option>
          <option value="G3">G3 (三年級)</option>
          <option value="G4">G4 (四年級)</option>
          <option value="G5">G5 (五年級)</option>
          <option value="G6">G6 (六年級)</option>
          <option value="ALL">ALL (全年級)</option>
        </select>
      </div>

      <!-- 考試時間 -->
      <div class="form-field">
        <label class="form-label">
          {{ t('examPaper.duration') || '考試時間（分鐘）' }}
        </label>
        <input
          v-model="localValue.duration"
          type="number"
          min="10"
          max="300"
          step="5"
          class="form-input"
          placeholder="90"
        />
      </div>

      <!-- 總分 -->
      <div class="form-field">
        <label class="form-label">
          {{ t('examPaper.totalScore') || '總分' }}
        </label>
        <input
          v-model="localValue.totalScore"
          type="number"
          min="10"
          max="500"
          step="10"
          class="form-input"
          placeholder="100"
        />
        <p class="form-hint">實際總分會根據題型配置自動計算</p>
      </div>
    </div>

    <!-- 快速填寫提示 -->
    <div class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <div class="text-sm text-blue-800">
          <p class="font-medium mb-1">💡 快速提示</p>
          <ul class="list-disc list-inside space-y-1">
            <li>考試標題會自動根據科目和年級生成，您也可以手動修改</li>
            <li>副標題可填寫考試範圍（如：課本頁數、章節名稱）</li>
            <li>總分會根據下方題型配置自動計算，此處僅供參考</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch, computed } from 'vue'
import { useLanguage } from '../../composables/useLanguage.js'
import { DEFAULT_SCHOOL_NAME } from '@/constants/examDefaults.js'

const { t } = useLanguage()

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

// 使用 reactive 創建本地副本
const localValue = reactive({ ...props.modelValue })

// Weekly Test 模式狀態
const isWeeklyTestMode = computed({
  get: () => localValue.isWeeklyTest || false,
  set: (val) => {
    localValue.isWeeklyTest = val
    // 切換模式時重置科目選擇
    if (val) {
      localValue.subjects = localValue.subject ? [localValue.subject] : []
    } else {
      localValue.subject = Array.isArray(localValue.subjects) && localValue.subjects.length > 0
        ? localValue.subjects[0]
        : ''
    }
  }
})

// 可選科目列表
const availableSubjects = [
  { value: 'Health', label: 'Health' },
  { value: 'Math', label: 'Math' },
  { value: 'Science', label: 'Science' },
  { value: 'English', label: 'English' },
  { value: 'Chinese', label: 'Chinese' },
  { value: 'Social', label: 'Social Studies' }
]

// 切換科目選擇（多選模式）
const toggleSubject = (subject) => {
  if (!localValue.subjects) localValue.subjects = []
  const idx = localValue.subjects.indexOf(subject)
  if (idx === -1) {
    localValue.subjects.push(subject)
  } else {
    localValue.subjects.splice(idx, 1)
  }
}

// 監聽變化並同步回父組件
watch(localValue, (newValue) => {
  emit('update:modelValue', { ...newValue })
}, { deep: true })

// 監聽 props 變化（雙向同步）
watch(() => props.modelValue, (newValue) => {
  Object.assign(localValue, newValue)
}, { deep: true })
</script>

<style scoped>
.exam-info-form {
  width: 100%;
}

.form-field {
  display: flex;
  flex-direction: column;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-input,
.form-select {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #111827;
  background-color: white;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input::placeholder {
  color: #9ca3af;
}

.form-hint {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
}

/* 防止 number input 的箭頭按鈕 */
.form-input[type="number"]::-webkit-inner-spin-button,
.form-input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.form-input[type="number"] {
  -moz-appearance: textfield;
}
</style>
