<template>
  <div
    :class="[
      'bg-white rounded-lg border border-gray-200 shadow-card',
      hoverable ? 'transition-shadow hover:shadow-md' : ''
    ]"
  >
    <div v-if="$slots.header" class="px-6 py-4 border-b border-gray-200">
      <slot name="header" />
    </div>
    <div :class="padded ? 'p-6' : ''">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  hoverable: { type: Boolean, default: false },
  padded: { type: Boolean, default: true }
})
</script>
