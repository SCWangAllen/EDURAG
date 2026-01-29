<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <h1 class="text-3xl font-bold text-gray-900 mb-8 whitespace-pre-wrap">{{ t('dashboard.title') }}</h1>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('dashboard.stats.templates') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.templates }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('dashboard.stats.documents') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.documents }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('dashboard.stats.questions') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.questions }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                  </svg>
                </div>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">{{ t('dashboard.stats.subjects') }}</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.subjects }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快速操作 -->
      <div class="bg-white shadow rounded-lg mb-8">
        <div class="p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">{{ t('dashboard.quickActions') }}</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <button
              @click="$router.push('/templates')"
              class="inline-flex items-center justify-center px-4 py-2 border border-gray-300 shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 rounded-md"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              {{ t('dashboard.actions.manageTemplates') }}
            </button>
            
            <button
              @click="$router.push('/documents')"
              class="inline-flex items-center justify-center px-4 py-2 border border-gray-300 shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 rounded-md"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
              </svg>
              {{ t('dashboard.actions.manageDocuments') }}
            </button>
            
            <button
              @click="$router.push('/generate')"
              class="inline-flex items-center justify-center px-4 py-2 border border-gray-300 shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 rounded-md"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              {{ t('dashboard.actions.generateQuestions') }}
            </button>

            <button
              @click="$router.push('/questions')"
              class="inline-flex items-center justify-center px-4 py-2 border border-gray-300 shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 rounded-md"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              {{ t('dashboard.actions.manageQuestions') || t('dashboard.actions.exportQuestions') }}
            </button>
          </div>
        </div>
      </div>

      <!-- 系統狀態 -->
      <div class="bg-white shadow rounded-lg">
        <div class="p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">{{ t('dashboard.systemStatus') }}</h2>
          <div class="space-y-3">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div :class="[
                  'w-2 h-2 rounded-full',
                  systemStatus.backend_api === 'running' ? 'bg-green-400' : 'bg-red-400'
                ]"></div>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">{{ t('dashboard.status.backendApi') }}</p>
                <p class="text-sm text-gray-500">{{ getStatusText(systemStatus.backend_api) }}</p>
              </div>
            </div>
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div :class="[
                  'w-2 h-2 rounded-full',
                  systemStatus.template_system === 'running' ? 'bg-green-400' : 'bg-red-400'
                ]"></div>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">{{ t('dashboard.status.templateSystem') }}</p>
                <p class="text-sm text-gray-500">{{ getStatusText(systemStatus.template_system) }}</p>
              </div>
            </div>
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div :class="[
                  'w-2 h-2 rounded-full',
                  systemStatus.database === 'running' ? 'bg-green-400' : 
                  systemStatus.database === 'mock_mode' ? 'bg-yellow-400' : 'bg-red-400'
                ]"></div>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">{{ t('dashboard.status.database') }}</p>
                <p class="text-sm text-gray-500">{{ getDatabaseStatusText(systemStatus.database) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useLanguage } from '../composables/useLanguage.js'
import dashboardService from '../api/dashboardService.js'

export default {
  name: 'Dashboard',
  setup() {
    const { t } = useLanguage()
    
    const stats = ref({
      templates: 0,
      documents: 0,
      questions: 0,
      subjects: 0
    })
    
    const loading = ref(true)
    const systemStatus = ref({
      backend_api: 'running',
      template_system: 'running',
      database: 'running'
    })

    const loadStats = async () => {
      try {
        loading.value = true
        const response = await dashboardService.getStats()
        stats.value = {
          templates: response.templates || 0,
          documents: response.documents || 0,
          questions: response.questions || 0,
          subjects: response.subjects || 0
        }
        
        if (response.system_status) {
          systemStatus.value = response.system_status
        }
        
      } catch (error) {
        // 如果載入失敗，使用預設值
        stats.value = {
          templates: 0,
          documents: 0,
          questions: 0,
          subjects: 0
        }
      } finally {
        loading.value = false
      }
    }

    const getStatusText = (status) => {
      switch (status) {
        case 'running':
          return t('dashboard.status.running') || '運行中'
        case 'error':
          return t('dashboard.status.error') || '錯誤'
        case 'stopped':
          return t('dashboard.status.stopped') || '已停止'
        default:
          return t('dashboard.status.unknown') || '未知'
      }
    }

    const getDatabaseStatusText = (status) => {
      switch (status) {
        case 'running':
          return t('dashboard.status.running') || '運行中'
        case 'mock_mode':
          return t('dashboard.status.mockMode') + ' (' + (t('dashboard.status.devMode') || '開發模式') + ')'
        case 'error':
          return t('dashboard.status.error') || '錯誤'
        case 'stopped':
          return t('dashboard.status.stopped') || '已停止'
        default:
          return t('dashboard.status.unknown') || '未知'
      }
    }

    onMounted(() => {
      loadStats()
    })

    return {
      t,
      stats,
      loading,
      systemStatus,
      getStatusText,
      getDatabaseStatusText
    }
  }
}
</script>