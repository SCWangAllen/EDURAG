<template>
  <BaseModal
    :model-value="modelValue"
    :title="t('settings.title')"
    size="md"
    @update:modelValue="$emit('update:modelValue', $event)"
  >
    <div class="space-y-4">
      <div v-if="loading" class="py-6 text-center text-sm text-gray-500">
        {{ t('settings.loading') }}
      </div>

      <p v-else-if="loadError" class="py-6 text-center text-sm text-danger-600">
        {{ loadError }}
      </p>

      <template v-else>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('settings.generationModel') }}</label>
          <select
            v-model="selected"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-white text-gray-800 focus:outline-none focus:border-primary-500"
          >
            <option value="" disabled>{{ t('settings.selectPlaceholder') }}</option>
            <optgroup v-if="recommended.length" :label="t('settings.recommendedGroup')">
              <option v-for="m in recommended" :key="m.id" :value="m.id">{{ m.display_name }}</option>
            </optgroup>
            <optgroup v-if="others.length" :label="t('settings.otherGroup')">
              <option v-for="m in others" :key="m.id" :value="m.id">{{ m.display_name }}</option>
            </optgroup>
            <option :value="CUSTOM">{{ t('settings.customOption') }}</option>
          </select>
          <p class="mt-1 text-xs text-gray-500">
            {{ t('settings.currentModel') }}<span class="font-mono text-gray-700">{{ currentModel || '-' }}</span>
          </p>
        </div>

        <!-- 自訂模型 ID -->
        <div v-if="selected === CUSTOM">
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('settings.customLabel') }}</label>
          <input
            v-model.trim="customId"
            type="text"
            spellcheck="false"
            :placeholder="t('settings.customPlaceholder')"
            class="w-full px-3 py-2 text-sm font-mono border border-gray-300 rounded-md focus:outline-none focus:border-primary-500"
          />
          <p class="mt-1 text-xs text-gray-500">{{ t('settings.customHint') }}</p>
        </div>

        <p class="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-md px-3 py-2">
          {{ t('settings.globalWarning') }}
        </p>
      </template>
    </div>

    <template #footer>
      <BaseButton variant="secondary" @click="$emit('update:modelValue', false)">
        {{ t('settings.cancel') }}
      </BaseButton>
      <BaseButton
        variant="primary"
        :loading="saving"
        :disabled="loading || !!loadError || !effectiveModel"
        @click="handleSave"
      >
        {{ t('settings.save') }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import BaseModal from '@/components/Base/BaseModal.vue'
import BaseButton from '@/components/Base/BaseButton.vue'
import settingsService from '@/api/settingsService.js'
import { useToast } from '@/composables/useToast.js'
import { useLanguage } from '@/composables/useLanguage.js'

const props = defineProps({
  modelValue: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])

const { t } = useLanguage()
const { showSuccess, showError } = useToast()

const CUSTOM = '__custom__'

const models = ref([])
const selected = ref('')
const customId = ref('')
const currentModel = ref('')
const loading = ref(false)
const saving = ref(false)
const loadError = ref('')

const recommended = computed(() => models.value.filter(m => (m.group || 'recommended') === 'recommended'))
const others = computed(() => models.value.filter(m => m.group === 'other'))

// 要送出的模型 ID:選「自訂」就用輸入框的值
const effectiveModel = computed(() => (selected.value === CUSTOM ? customId.value : selected.value))

const load = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const [modelsRes, currentRes] = await Promise.all([
      settingsService.getModels(),
      settingsService.getModel()
    ])
    models.value = modelsRes.models || []
    currentModel.value = currentRes.model || ''
    // 目前的模型若不在清單裡(例如之前自訂輸入的),切到「自訂」並帶入
    const inList = models.value.some(m => m.id === currentModel.value)
    if (currentModel.value && !inList) {
      selected.value = CUSTOM
      customId.value = currentModel.value
    } else {
      selected.value = currentModel.value
      customId.value = ''
    }
  } catch (error) {
    loadError.value = error.response?.data?.detail || t('settings.loadFailed')
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  if (!effectiveModel.value) return
  saving.value = true
  try {
    await settingsService.setModel(effectiveModel.value)
    showSuccess(t('settings.saveSuccess'))
    emit('update:modelValue', false)
  } catch (error) {
    const detail = error.response?.data?.detail || t('settings.saveFailed')
    showError(detail)
  } finally {
    saving.value = false
  }
}

watch(
  () => props.modelValue,
  (open) => {
    if (open) load()
  }
)
</script>
