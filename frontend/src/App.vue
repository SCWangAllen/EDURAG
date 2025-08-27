<template>
  <div class="bg-gray-50 min-h-screen flex">
    <Sidebar :sidebarOpen="sidebarOpen" :menu="menu" />
    <div class="flex-1 lg:ml-64 flex flex-col">
      <Topbar :apiOnline="apiOnline" @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <main class="flex-1 p-6 overflow-y-auto">
        <SettingsPanel
          :subjects="subjects"
          v-model:selectedSubject="selectedSubject"
          v-model:textInput="textInput"
          :types="types"
          :labelMap="labelMap"
          :apiOutput="output" 
          @generate="handleGenerate"
          @update:apiOutput="output = $event"
        />
        <QuestionList :questions="questions" @open-drawer="openDrawer" />
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
    const menu           = ref([{icon:'📚',text:'Generate'},{icon:'📝',text:'Lesson Management'},{icon:'⚙️',text:'setting'}])
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
