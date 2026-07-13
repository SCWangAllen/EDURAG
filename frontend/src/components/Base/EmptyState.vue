<template>
  <div class="flex flex-col items-center justify-center py-12 px-4 text-center">
    <div class="text-4xl mb-3">{{ icon }}</div>
    <h3 class="text-base font-medium text-gray-900">{{ title }}</h3>
    <p v-if="description" class="mt-1 text-sm text-gray-500 max-w-sm">{{ description }}</p>
    <div v-if="$slots.default" class="mt-4">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '📄' },
  title: { type: String, required: true },
  description: { type: String, default: '' }
})
</script>
