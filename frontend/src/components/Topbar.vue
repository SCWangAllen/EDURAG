<template>
  <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
    <button class="lg:hidden text-2xl" @click="$emit('toggle-sidebar')">☰</button>
    <h1 class="text-lg font-medium"><slot>Qusetion Generator</slot></h1>
    <div class="text-sm text-gray-500">
      API Status:
      <span :class="apiOnline ? 'text-green-600' : 'text-red-600'">
        ● {{ apiOnline ? 'Online' : 'Offline' }}
      </span>
    </div>
  </header>
</template>

<script>
export default {
  name: 'Topbar',
  props: {
    apiOnline: { type: Boolean, default: true }
  }
}
</script>