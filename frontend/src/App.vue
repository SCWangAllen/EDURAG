<template>
  <div class="bg-gray-50 min-h-screen flex">
    <Sidebar :sidebarOpen="sidebarOpen" :menu="menu" />
    <div class="flex-1 lg:ml-64 flex flex-col">
      <Topbar :apiOnline="apiOnline" @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <main class="flex-1 overflow-y-auto">
        <router-view />
      </main>
    </div>
    <Drawer :open="drawerOpen" :context="currentContext" @close="drawerOpen = false" />
  </div>
</template>

<script>
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Topbar from './components/Topbar.vue'
import SettingsPanel from './components/SettingsPanel.vue'
import QuestionList from './components/QuestionList.vue'
import Drawer from './components/Drawer.vue'
import { useQuestions } from './composables/useQuestions'

export default {
  components: { Sidebar, Topbar, SettingsPanel, QuestionList, Drawer },
  setup() {
    const { questions, output, loading, error, load } = useQuestions()
    const sidebarOpen    = ref(false)
    const drawerOpen     = ref(false)
    const apiOnline      = ref(true)
    const menu = ref([
      { 
        name: '儀表板', 
        id: 'dashboard',
        route: '/',
        icon: 'M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z' 
      },
      { 
        name: '模板管理', 
        id: 'templates',
        route: '/templates',
        icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' 
      },
      { 
        name: '文件管理', 
        id: 'documents',
        route: '/documents',
        icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10'
      },
      { 
        name: '題目生成', 
        id: 'generate',
        route: '/generate',
        icon: 'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' 
      }
    ])
    const subjects       = ref(['Chinese','English','Math'])
    const selectedSubject= ref('Chinese')
    const textInput      = ref('')
    const types          = ref({ single:{enabled:true,num:3}, cloze:{enabled:false,num:1}, short:{enabled:false,num:1} })
    const labelMap       = ref({ single:'single', cloze:'cloze', short:'short' })
    const currentContext = ref('')

    async function handleGenerate() {
      const payload = {
        subject: selectedSubject.value,
        text:    textInput.value,
        types:   Object.entries(types.value)
                  .filter(([_,cfg]) => cfg.enabled)
                  .map(([type,cfg]) => ({ type, num: cfg.num }))
      }
      const success = await load(payload)
      // If API call fails, set output to the original text for display
      if (!success) {
        output.value = textInput.value
      }
    }

    function openDrawer(ctx) {
      currentContext.value = ctx
      drawerOpen.value     = true
    }

    return { 
      sidebarOpen, drawerOpen, apiOnline, menu, subjects, selectedSubject, 
      textInput, types, labelMap, questions, output, loading, error, 
      currentContext, handleGenerate, openDrawer 
    }
  }
}
</script>
