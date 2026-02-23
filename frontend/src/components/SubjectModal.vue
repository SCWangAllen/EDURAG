<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" @click="$emit('close')">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- 背景遮罩 -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

      <!-- Modal 內容 -->
      <div
        class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full"
        @click.stop
      >
        <form @submit.prevent="handleSubmit">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 mb-6">
                  {{ subject ? t('subjectModal.editTitle') : t('subjectModal.createTitle') }}
                </h3>

                <div class="space-y-6">
                  <!-- 科目名稱 -->
                  <div>
                    <label for="name" class="block text-sm font-medium text-gray-700 mb-2">
                      {{ t('subjectModal.subjectName') }} <span class="text-red-500">*</span>
                    </label>
                    <input
                      id="name"
                      v-model="form.name"
                      type="text"
                      required
                      maxlength="50"
                      class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      :placeholder="t('subjectModal.subjectNamePlaceholder')"
                    />
                  </div>

                  <!-- 科目描述 -->
                  <div>
                    <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
                      {{ t('subjectModal.subjectDescription') }}
                    </label>
                    <textarea
                      id="description"
                      v-model="form.description"
                      rows="3"
                      maxlength="500"
                      class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      :placeholder="t('subjectModal.subjectDescriptionPlaceholder')"
                    ></textarea>
                  </div>

                  <!-- 適用年級 -->
                  <div>
                    <label for="grade" class="block text-sm font-medium text-gray-700 mb-2">
                      {{ t('subjectModal.subjectGrade') }} <span class="text-red-500">*</span>
                    </label>
                    <input
                      id="grade"
                      v-model="form.grade"
                      type="text"
                      required
                      maxlength="50"
                      class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      :placeholder="t('subjectModal.gradePlaceholder')"
                    />
                    <p class="text-xs text-gray-500 mt-1">{{ t('subjectModal.gradeHint') }}</p>
                  </div>

                  <!-- 科目顏色 -->
                  <div>
                    <label for="color" class="block text-sm font-medium text-gray-700 mb-2">
                      {{ t('subjectModal.subjectColor') }}
                    </label>
                    <div class="flex items-center space-x-3">
                      <input
                        id="color"
                        v-model="form.color"
                        type="color"
                        class="h-10 w-16 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      />
                      <input
                        v-model="form.color"
                        type="text"
                        pattern="^#[0-9A-Fa-f]{6}$"
                        class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="#3B82F6"
                      />
                    </div>
                    <p class="text-xs text-gray-500 mt-1">{{ t('subjectModal.colorHint') }}</p>
                  </div>

                  <!-- 預覽 -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">{{ t('subjectModal.preview') }}</label>
                    <div class="p-3 bg-gray-50 rounded-md">
                      <span
                        :style="{ backgroundColor: form.color, color: getTextColor(form.color) }"
                        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      >
                        {{ form.name || t('subjectModal.subjectNamePreview') }}
                        <span v-if="form.grade" class="ml-1.5 text-xs">{{ form.grade }}</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="submit"
              :disabled="!form.name.trim() || !form.grade.trim()"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ subject ? t('subjectModal.update') : t('subjectModal.create') }}
            </button>
            <button
              type="button"
              @click="$emit('close')"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              {{ t('cancel') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'

export default {
  name: 'SubjectModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    subject: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'save'],
  setup(props, { emit }) {
    const { t } = useLanguage()
    const form = reactive({
      name: '',
      description: '',
      grade: '',
      color: '#3B82F6'
    })

    // 重置表單
    const resetForm = () => {
      form.name = ''
      form.description = ''
      form.grade = ''
      form.color = '#3B82F6'
    }

    // 載入科目資料
    const loadSubject = () => {
      if (props.subject) {
        form.name = props.subject.name || ''
        form.description = props.subject.description || ''
        form.grade = props.subject.grade || ''
        form.color = props.subject.color || '#3B82F6'
      } else {
        resetForm()
      }
    }

    // 計算文字顏色
    const getTextColor = (backgroundColor) => {
      const hex = backgroundColor.replace('#', '')
      const r = parseInt(hex.substr(0, 2), 16)
      const g = parseInt(hex.substr(2, 2), 16)
      const b = parseInt(hex.substr(4, 2), 16)
      const brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000
      return brightness > 155 ? '#000000' : '#FFFFFF'
    }

    // 提交表單
    const handleSubmit = () => {
      if (!form.grade.trim()) {
        return
      }

      const subjectData = {
        name: form.name.trim(),
        description: form.description.trim() || null,
        grade: form.grade.trim(),
        color: form.color
      }

      emit('save', subjectData)
    }

    // 監聽 props 變化
    watch(() => [props.show, props.subject], loadSubject, { immediate: true })

    return {
      t,
      form,
      handleSubmit,
      getTextColor
    }
  }
}
</script>