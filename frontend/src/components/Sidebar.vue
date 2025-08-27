<template>
  <aside :class="['fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200 flex flex-col transition-transform', sidebarOpen ? '' : '-translate-x-full lg:translate-x-0']">
    <div class="h-16 flex items-center px-6 text-xl font-bold text-blue-600">
      Abraham
    </div>
    <nav class="flex-1 px-4 space-y-2">
      <a v-for="item in menu" :key="item.text" href="#"
         class="flex items-center gap-2 px-3 py-2 rounded-md text-gray-700 hover:bg-blue-50">
        <span v-html="item.icon"></span><span>{{ item.text }}</span>
      </a>
    </nav>
  </aside>
</template>

<script>
export default {
  name: 'Sidebar',
  props: {
    sidebarOpen: { type: Boolean, required: true },
    menu: { type: Array, required: true }
  }
}
</script>