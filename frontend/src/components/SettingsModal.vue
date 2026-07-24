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

      <FormSelect
        v-else
        v-model="selected"
        :label="t('settings.generationModel')"
        :options="modelOptions"
        :placeholder="t('settings.selectPlaceholder')"
      />
    </div>

    <template #footer>
      <BaseButton variant="secondary" @click="$emit('update:modelValue', false)">
        {{ t('settings.cancel') }}
      </BaseButton>
      <BaseButton
        variant="primary"
        :loading="saving"
        :disabled="loading || !!loadError || !selected"
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
import FormSelect from '@/components/Base/FormSelect.vue'
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

const models = ref([])
const selected = ref('')
const loading = ref(false)
const saving = ref(false)
const loadError = ref('')

const modelOptions = computed(() =>
  models.value.map(m => ({ value: m.id, label: m.display_name }))
)

const load = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const [modelsRes, currentRes] = await Promise.all([
      settingsService.getModels(),
      settingsService.getModel()
    ])
    models.value = modelsRes.models || []
    selected.value = currentRes.model || ''
  } catch (error) {
    loadError.value = error.response?.data?.detail || t('settings.loadFailed')
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  if (!selected.value) return
  saving.value = true
  try {
    await settingsService.setModel(selected.value)
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
