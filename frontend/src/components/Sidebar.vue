<template>
  <aside :class="['fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200 flex flex-col transition-transform', sidebarOpen ? '' : '-translate-x-full lg:translate-x-0']">
    <div class="h-16 flex items-center px-6 text-xl font-bold text-blue-600">
      Abraham
    </div>
    <nav class="flex-1 px-4 space-y-2">
      <router-link
        v-for="item in menu"
        :key="item.name"
        :to="item.route"
        v-slot="{ isActive }"
        custom
      >
        <a
          :href="item.route"
          @click.prevent="$router.push(item.route)"
          :class="[
            'flex items-center gap-2 px-3 py-2 rounded-md transition-all duration-200',
            isActive
              ? 'bg-blue-600 text-white font-semibold shadow-md border-l-4 border-blue-800'
              : 'text-gray-700 hover:bg-blue-50'
          ]"
        >
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"></path>
          </svg>
          <span class="break-words whitespace-pre-wrap leading-tight text-sm">{{ item.name }}</span>
        </a>
      </router-link>
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