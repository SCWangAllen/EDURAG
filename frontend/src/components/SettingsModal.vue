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

        <!-- 建議清單管理 -->
        <div class="border-t border-gray-200 pt-3">
          <button
            type="button"
            class="w-full flex items-center justify-between text-sm font-medium text-gray-700"
            @click="manageOpen = !manageOpen"
          >
            <span>{{ t('settings.manageRecommended') }}</span>
            <span class="text-xs text-gray-400">{{ manageOpen ? '▲' : '▼' }}</span>
          </button>
          <div v-if="manageOpen" class="mt-2 space-y-2">
            <p class="text-xs text-gray-500">{{ t('settings.manageHint') }}</p>
            <ul class="max-h-52 overflow-auto divide-y divide-gray-100 border border-gray-200 rounded-md">
              <li
                v-for="m in models"
                :key="'rec-' + m.id"
                class="flex items-center justify-between gap-2 px-2 py-1.5"
              >
                <span class="font-mono text-xs text-gray-700 truncate" :title="m.display_name">{{ m.id }}</span>
                <button
                  type="button"
                  :class="['flex-shrink-0 text-xs px-2 py-0.5 rounded border', isRecommended(recKey(m)) ? 'bg-primary-50 border-primary-300 text-primary-700' : 'border-gray-200 text-gray-500 hover:border-gray-300']"
                  @click="toggleRecommended(recKey(m))"
                >{{ isRecommended(recKey(m)) ? '★' : '☆' }} {{ t('settings.recommendedTag') }}</button>
              </li>
              <li
                v-for="id in extraRecommended"
                :key="'rec-x-' + id"
                class="flex items-center justify-between gap-2 px-2 py-1.5 bg-primary-50/30"
              >
                <span class="font-mono text-xs text-gray-700 truncate">{{ id }}</span>
                <button
                  type="button"
                  class="flex-shrink-0 text-xs px-2 py-0.5 rounded border bg-primary-50 border-primary-300 text-primary-700"
                  @click="toggleRecommended(id)"
                >★ {{ t('settings.recommendedTag') }}</button>
              </li>
            </ul>
            <div class="flex gap-2">
              <input
                v-model.trim="newRecommendedId"
                type="text"
                spellcheck="false"
                :placeholder="t('settings.customPlaceholder')"
                class="flex-1 px-2 py-1 text-xs font-mono border border-gray-300 rounded-md focus:outline-none focus:border-primary-500"
                @keyup.enter="addRecommended"
              />
              <button
                type="button"
                class="text-xs px-2 py-1 rounded border border-gray-300 text-gray-700 hover:bg-gray-50"
                @click="addRecommended"
              >{{ t('settings.addRecommended') }}</button>
            </div>
            <div class="flex justify-end">
              <button
                type="button"
                :disabled="!recommendedDirty || savingRecommended"
                class="text-xs px-3 py-1 rounded bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-50"
                @click="saveRecommended"
              >{{ savingRecommended ? t('settings.loading') : t('settings.saveRecommended') }}</button>
            </div>
          </div>
        </div>
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

// 建議清單管理(全站共用;按「儲存建議清單」才生效)
const manageOpen = ref(false)
const recommendedIds = ref([])
const savedRecommendedIds = ref([])
const newRecommendedId = ref('')
const savingRecommended = ref(false)
// 建議清單存的是原始 ID(alias);清單項目的 id 可能是帳號實際的帶日期 ID,比對與切換都用 alias
const recKey = (m) => m.alias || m.id
const isRecommended = (id) => recommendedIds.value.includes(id)
const extraRecommended = computed(() =>
  recommendedIds.value.filter(id => !models.value.some(m => recKey(m) === id))
)
const recommendedDirty = computed(() =>
  JSON.stringify(recommendedIds.value) !== JSON.stringify(savedRecommendedIds.value)
)
const toggleRecommended = (id) => {
  recommendedIds.value = isRecommended(id)
    ? recommendedIds.value.filter(x => x !== id)
    : [...recommendedIds.value, id]
}
const addRecommended = () => {
  const id = newRecommendedId.value
  if (!id) return
  if (!isRecommended(id)) recommendedIds.value = [...recommendedIds.value, id]
  newRecommendedId.value = ''
}
const saveRecommended = async () => {
  savingRecommended.value = true
  try {
    const res = await settingsService.setRecommended(recommendedIds.value)
    recommendedIds.value = res.models || []
    savedRecommendedIds.value = [...recommendedIds.value]
    showSuccess(t('settings.recommendedSaved'))
    const modelsRes = await settingsService.getModels()
    models.value = modelsRes.models || []
  } catch (error) {
    showError(error.response?.data?.detail || t('settings.saveFailed'))
  } finally {
    savingRecommended.value = false
  }
}

const load = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const [modelsRes, currentRes, recRes] = await Promise.all([
      settingsService.getModels(),
      settingsService.getModel(),
      settingsService.getRecommended()
    ])
    models.value = modelsRes.models || []
    recommendedIds.value = recRes.models || []
    savedRecommendedIds.value = [...recommendedIds.value]
    manageOpen.value = false
    newRecommendedId.value = ''
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
