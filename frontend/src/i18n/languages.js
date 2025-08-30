export const languages = {
  zh: {
    // 通用
    save: '儲存',
    cancel: '取消',
    edit: '編輯',
    delete: '刪除',
    view: '檢視',
    close: '關閉',
    reset: '重置',
    export: '匯出',
    search: '搜尋',
    loading: '載入中...',
    
    // 導航
    nav: {
      dashboard: '儀表板',
      templates: '模板管理',
      documents: '文件管理',
      questions: '問題管理',
      generate: '題目生成'
    },
    
    // 儀表板
    dashboard: {
      title: '儀表板',
      quickActions: '快速操作',
      systemStatus: '系統狀態',
      stats: {
        templates: '模板總數',
        documents: '文件總數',
        questions: '題目總數',
        subjects: '支援科目'
      },
      status: {
        backendApi: '後端 API',
        templateSystem: '模板系統',
        database: '資料庫',
        running: '運行正常',
        error: '錯誤',
        stopped: '已停止',
        unknown: '未知狀態',
        mockMode: '開發模式',
        initialized: '已初始化預設模板',
        devMode: '開發環境'
      },
      actions: {
        manageQuestions: '題目管理',
        manageTemplates: '管理模板',
        manageDocuments: '管理文件',
        generateQuestions: '生成題目',
        exportQuestions: '匯出題目'
      }
    },
    
    // 模板管理
    templates: {
      title: '模板管理',
      subtitle: '管理不同科目的題目生成模板',
      createTemplate: '新增模板',
      initializeDefaults: '初始化預設模板',
      filterBySubject: '科目篩選',
      allSubjects: '全部科目',
      itemsPerPage: '每頁顯示',
      noTemplates: '尚未建立任何模板',
      clickToCreate: '點擊「新增模板」來建立第一個模板',
      version: '版本',
      updatedAt: '更新時間',
      items: '筆',
      edit: '編輯',
      delete: '刪除',
      prevPage: '上一頁',
      nextPage: '下一頁',
      showing: '顯示',
      to: '到',
      of: '筆，共',
      results: '筆結果',
      initializeSuccess: '預設模板初始化完成！',
      initializeError: '初始化失敗，請稍後再試',
      confirmDelete: '確定要刪除這個模板嗎？',
      deleteSuccess: '模板刪除成功！',
      deleteError: '刪除失敗，請稍後再試',
      updateSuccess: '模板更新成功！',
      createSuccess: '模板建立成功！',
      saveError: '儲存失敗，請稍後再試',
      
      // 模板 Modal
      modal: {
        createTitle: '新增模板',
        editTitle: '編輯模板',
        templateName: '模板名稱',
        subject: '科目',
        selectSubject: '請選擇科目',
        otherSubject: '其他科目',
        customSubjectName: '自訂科目名稱',
        promptTemplate: 'Prompt 模板',
        promptPlaceholder: '使用 {context} 作為文章內容的替換標記。支援 Markdown 格式。',
        llmParams: 'LLM 參數設定',
        temperature: '溫度 (Temperature)',
        maxTokens: '最大字數 (Max Tokens)',
        topP: 'Top P',
        frequencyPenalty: '頻率懲罰 (Frequency Penalty)',
        preview: '預覽',
        saving: '儲存中...'
      }
    },
    
    // 文件管理
    documents: {
      title: '文件管理',
      downloadTemplate: '下載範本',
      uploadExcel: '上傳 Excel',
      
      // 統計
      totalDocuments: '總文件數',
      subjectCount: '科目數量',
      withImages: '含圖片',
      chapterCount: '章節數量',
      
      // 搜尋和篩選
      search: '搜尋',
      searchPlaceholder: '搜尋文件標題或內容...',
      subject: '科目',
      allSubjects: '全部科目',
      pageSize: '每頁顯示',
      searchButton: '搜尋',
      
      // 文件列表
      documentList: '文件清單',
      totalCount: '筆文件',
      loading: '載入中...',
      noDocuments: '尚無文件資料',
      noDocumentsHint: '請上傳 Excel 檔案來新增文件',
      withImage: '含圖片',
      characters: '字',
      edit: '編輯',
      delete: '刪除',
      
      // 分頁
      previous: '上一頁',
      next: '下一頁',
      showing: '顯示',
      to: '到',
      of: '筆，共',
      results: '筆結果',
      
      // Excel 上傳
      excelPreview: 'Excel 文件預覽',
      uploadSuccess: '成功解析 Excel 文件',
      fileName: '檔案名稱',
      totalDocs: '總文件數',
      index: '序號',
      title: '標題',
      chapter: '章節',
      contentLength: '內容長度',
      chunkCount: '分塊數量',
      chunks: '塊',
      cancel: '取消',
      confirmSave: '確認儲存',
      saving: '儲存中...',
      
      // 文件詳情/編輯
      documentDetail: '文件詳情',
      editDocument: '編輯文件',
      documentTitle: '標題',
      documentSubject: '科目',
      documentChapter: '章節',
      content: '內容',
      contentLen: '內容長度',
      createdAt: '建立時間',
      close: '關閉',
      startEdit: '編輯',
      saveChanges: '儲存',
      
      // 訊息
      uploadSuccess: '文件上傳成功！',
      uploadError: '上傳失敗: ',
      saveError: '儲存失敗: ',
      deleteConfirm: '確定要刪除文件',
      deleteSuccess: '文件已刪除',
      deleteError: '刪除失敗: ',
      
      comingSoon: '文件管理功能開發中',
      phase2Features: '此功能將在 Phase 2 中實作，包括：',
      features: {
        excelImport: 'Excel 批量匯入',
        chapterManagement: '章節篩選與管理',
        imageTextAssociation: '圖片與文字關聯',
        multiSelectInterface: '多選勾選介面'
      }
    },
    
    // 題目生成
    generate: {
      title: '題目生成',
      subtitle: '選擇模板和文件來生成客製化題目',
      generating: '生成中...',
      generateQuestions: '生成題目',
      
      // 設定面板
      selectTemplate: '選擇模板',
      selectDocuments: '選擇文件',
      questionTypes: '題型設定',
      
      // 模板選擇
      noTemplatesAvailable: '尚無可用模板',
      goCreateTemplate: '前往建立模板',
      
      // 文件選擇
      searchDocuments: '搜尋文件...',
      noDocumentsAvailable: '尚無可用文件',
      goImportDocuments: '前往匯入文件',
      
      // 題型
      singleChoice: '單選題',
      cloze: '填空題',
      shortAnswer: '簡答題',
      auto: '自動',
      unknown: '未知',
      totalQuestions: '總題數',
      questionCount: '生成數量',
      
      // 預覽和結果
      templatePreview: '模板預覽',
      documentsSelected: '個文件已選擇',
      previewNote: '此預覽顯示模板如何應用於選中的文件內容',
      generatedResults: '生成結果',
      questions: '題',
      
      // 空狀態
      readyToGenerate: '準備開始生成題目',
      selectRequirements: '請選擇模板、文件和題型設定',
      steps: {
        selectTemplate: '選擇一個生成模板',
        selectDocument: '選擇至少一個文件',
        setQuestionTypes: '設定題型和數量'
      },
      
      // 題目卡片
      answer: '答案',
      source: '來源',
      explanation: '解釋',
      document: '文件',
      
      // 傳統生成模式
      traditionalGenerate: '生成題目',
      traditionalMode: '傳統生成模式',
      traditionalModeDesc: '選擇一個模板和文件進行題目生成',
      traditionalGenerateDesc: '基於選擇的模板和文件生成題目',
      
      // 批次生成模式
      batchMode: '批次生成模式',
      batchModeDesc: '為每個文件配對合適的模板，批次生成題目',
      batchGenerate: '批次生成',
      batchConfiguration: '批次生成配置',
      
      // 批次生成相關
      selectedDocuments: '已選文件',
      templatePairing: '模板配對',
      pairingPreview: '配對預覽',
      documentTemplateMapping: '文件-模板配對',
      addTemplatePairing: '+ 新增模板配對',
      totalPairings: '總配對',
      expectedQuestions: '預計生成',
      pairingCount: '個模板配對',
      selectDocumentsFirst: '請先在上方選擇文件',
      selectDocumentsAfterPairing: '選擇文件後開始配對',
      clickPairingToPreview: '點擊配對查看預覽',
      willGenerate: '將生成',
      questionsCount: '道題目',
      
      // 批次文件選擇
      batchDocumentSelection: '批次文件選擇',
      batchSelectDocuments: '選擇要進行批次生成的文件',
      batchSearchDocuments: '搜尋批次生成文件...',
      noBatchDocuments: '尚未選擇批次生成文件',
      addBatchDocuments: '請選擇文件進行批次生成'
    },
    
    // 科目名稱
    subjects: {
      health: '健康',
      english: '英文',
      history: '歷史'
    },
    
    // 問題管理
    questions: {
      title: '問題管理',
      subtitle: '管理和匯出已生成的題目',
      
      // 統計
      totalQuestions: '總題目數',
      byType: '按題型分佈',
      bySubject: '按科目分佈', 
      byDifficulty: '按難度分佈',
      
      // 搜尋和篩選
      search: '搜尋',
      searchPlaceholder: '搜尋題目內容...',
      filterByType: '題型篩選',
      filterBySubject: '科目篩選',
      filterByDifficulty: '難度篩選',
      allTypes: '全部題型',
      allSubjects: '全部科目',
      allDifficulties: '全部難度',
      
      // 題型
      single_choice: '單選題',
      cloze: '填空題',
      short_answer: '簡答題',
      
      // 難度
      easy: '容易',
      medium: '中等',
      hard: '困難',
      
      // 問題清單
      questionList: '問題清單',
      content: '題目內容',
      type: '題型',
      subject: '科目',
      difficulty: '難度',
      createdAt: '建立時間',
      actions: '操作',
      
      // 操作
      view: '檢視',
      edit: '編輯',
      delete: '刪除',
      export: '匯出',
      create: '新增問題',
      
      // 匯出
      exportTitle: '匯出題目',
      exportFormat: '匯出格式',
      exportFilters: '匯出篩選',
      confirmExport: '確認匯出',
      exporting: '匯出中...',
      exportSuccess: '匯出成功！',
      exportError: '匯出失敗：',
      
      // 分頁
      showing: '顯示',
      to: '到',
      of: '筆，共',
      results: '筆結果',
      previous: '上一頁',
      next: '下一頁',
      
      // 訊息
      loading: '載入中...',
      noQuestions: '尚無題目資料',
      noQuestionsHint: '請先到「題目生成」頁面生成題目',
      deleteConfirm: '確定要刪除此題目嗎？',
      deleteSuccess: '題目已刪除',
      deleteError: '刪除失敗：',
      
      // 問題詳情
      questionDetail: '題目詳情',
      options: '選項',
      correctAnswer: '正確答案',
      explanation: '解釋',
      sourceDocument: '來源文件',
      sourceContent: '來源內容',
      chapter: '章節'
    }
  },
  
  en: {
    // Common
    save: 'Save',
    cancel: 'Cancel',
    edit: 'Edit',
    delete: 'Delete',
    view: 'View',
    close: 'Close',
    reset: 'Reset',
    export: 'Export',
    search: 'Search',
    loading: 'Loading...',
    
    // Navigation
    nav: {
      dashboard: 'Dashboard',
      templates: 'Templates',
      documents: 'Documents',
      questions: 'Questions',
      generate: 'Generate'
    },
    
    // Dashboard
    dashboard: {
      title: 'Dashboard',
      quickActions: 'Quick Actions',
      systemStatus: 'System Status',
      stats: {
        templates: 'Total Templates',
        documents: 'Total Documents',
        questions: 'Total Questions',
        subjects: 'Supported Subjects'
      },
      status: {
        backendApi: 'Backend API',
        templateSystem: 'Template System',
        database: 'Database',
        running: 'Running Normally',
        error: 'Error',
        stopped: 'Stopped',
        unknown: 'Unknown Status',
        mockMode: 'Development Mode',
        initialized: 'Default Templates Initialized',
        devMode: 'Development Environment'
      },
      actions: {
        manageQuestions: 'Manage Questions',
        manageTemplates: 'Manage Templates',
        manageDocuments: 'Manage Documents',
        generateQuestions: 'Generate Questions',
        exportQuestions: 'Export Questions'
      }
    },
    
    // Templates
    templates: {
      title: 'Template Management',
      subtitle: 'Manage question generation templates for different subjects',
      createTemplate: 'Create Template',
      initializeDefaults: 'Initialize Defaults',
      filterBySubject: 'Filter by Subject',
      allSubjects: 'All Subjects',
      itemsPerPage: 'Items per Page',
      noTemplates: 'No templates created yet',
      clickToCreate: 'Click "Create Template" to create your first template',
      version: 'Version',
      updatedAt: 'Updated',
      items: 'items',
      edit: 'Edit',
      delete: 'Delete',
      prevPage: 'Previous',
      nextPage: 'Next',
      showing: 'Showing',
      to: 'to',
      of: 'of',
      results: 'results',
      initializeSuccess: 'Default templates initialized successfully!',
      initializeError: 'Initialization failed, please try again later',
      confirmDelete: 'Are you sure you want to delete this template?',
      deleteSuccess: 'Template deleted successfully!',
      deleteError: 'Delete failed, please try again later',
      updateSuccess: 'Template updated successfully!',
      createSuccess: 'Template created successfully!',
      saveError: 'Save failed, please try again later',
      
      // Template Modal
      modal: {
        createTitle: 'Create Template',
        editTitle: 'Edit Template',
        templateName: 'Template Name',
        subject: 'Subject',
        selectSubject: 'Please select a subject',
        otherSubject: 'Other Subject',
        customSubjectName: 'Custom Subject Name',
        promptTemplate: 'Prompt Template',
        promptPlaceholder: 'Use {context} as placeholder for content. Supports Markdown format.',
        llmParams: 'LLM Parameters',
        temperature: 'Temperature',
        maxTokens: 'Max Tokens',
        topP: 'Top P',
        frequencyPenalty: 'Frequency Penalty',
        preview: 'Preview',
        saving: 'Saving...'
      }
    },
    
    // Documents
    documents: {
      title: 'Document Management',
      downloadTemplate: 'Download Template',
      uploadExcel: 'Upload Excel',
      
      // Statistics
      totalDocuments: 'Total Documents',
      subjectCount: 'Subjects',
      withImages: 'With Images',
      chapterCount: 'Chapters',
      
      // Search and Filter
      search: 'Search',
      searchPlaceholder: 'Search document title or content...',
      subject: 'Subject',
      allSubjects: 'All Subjects',
      pageSize: 'Items per page',
      searchButton: 'Search',
      
      // Document List
      documentList: 'Document List',
      totalCount: 'documents in total',
      loading: 'Loading...',
      noDocuments: 'No documents available',
      noDocumentsHint: 'Please upload Excel file to add documents',
      withImage: 'With Image',
      characters: 'characters',
      edit: 'Edit',
      delete: 'Delete',
      
      // Pagination
      previous: 'Previous',
      next: 'Next',
      showing: 'Showing',
      to: 'to',
      of: 'of',
      results: 'results',
      
      // Excel Upload
      excelPreview: 'Excel File Preview',
      uploadSuccess: 'Upload successful',
      fileName: 'File Name',
      totalDocs: 'Total Documents',
      index: 'Index',
      title: 'Title',
      chapter: 'Chapter',
      contentLength: 'Content Length',
      chunkCount: 'Chunk Count',
      chunks: 'chunks',
      cancel: 'Cancel',
      confirmSave: 'Confirm Save',
      saving: 'Saving...',
      
      // Document Detail/Edit
      documentDetail: 'Document Details',
      editDocument: 'Edit Document',
      documentTitle: 'Title',
      documentSubject: 'Subject',
      documentChapter: 'Chapter',
      content: 'Content',
      contentLen: 'Content Length',
      createdAt: 'Created At',
      close: 'Close',
      startEdit: 'Edit',
      saveChanges: 'Save',
      
      // Messages
      uploadSuccess: 'Documents uploaded successfully!',
      uploadError: 'Upload failed: ',
      saveError: 'Save failed: ',
      deleteConfirm: 'Are you sure you want to delete document',
      deleteSuccess: 'Document deleted successfully',
      deleteError: 'Delete failed: ',
      
      comingSoon: 'Document Management Feature Coming Soon',
      phase2Features: 'This feature will be implemented in Phase 2, including:',
      features: {
        excelImport: 'Bulk Excel Import',
        chapterManagement: 'Chapter Filtering & Management',
        imageTextAssociation: 'Image & Text Association',
        multiSelectInterface: 'Multi-select Interface'
      }
    },
    
    // Generate
    generate: {
      title: 'Question Generation',
      subtitle: 'Select templates and documents to generate customized questions',
      generating: 'Generating...',
      generateQuestions: 'Generate Questions',
      traditionalGenerate :'Generate Questions',
      traditionalMode:'Traditional Generation Mode',
      traditionalModeDesc:'Select template and document for question generation',
      traditionalGenerateDesc:'Generate questions based on template and document',
      //batch
      batchMode:'Batch Generate ',
      batchModeDesc:'Generate a lot of question with one click',
      batchGenerate :'Batch Generate',
      // Settings Panel
      selectTemplate: 'Select Template',
      selectDocuments: 'Select Documents',
      questionTypes: 'Question Types',
      
      // Template Selection
      noTemplatesAvailable: 'No templates available',
      goCreateTemplate: 'Go to create templates',
      
      // Document Selection
      searchDocuments: 'Search documents...',
      noDocumentsAvailable: 'No documents available',
      goImportDocuments: 'Go to import documents',
      
      // Question Types
      singleChoice: 'Single Choice',
      cloze: 'Cloze Test',
      shortAnswer: 'Short Answer',
      auto: 'Auto',
      unknown: 'Unknown',
      totalQuestions: 'Total Questions',
      questionCount: 'Question Count',
      
      // Preview and Results
      templatePreview: 'Template Preview',
      documentsSelected: 'documents selected',
      previewNote: 'This preview shows how the template will be applied to the selected document content',
      generatedResults: 'Generated Results',
      questions: ' Questions',
      
      // Empty State
      readyToGenerate: 'Ready to Generate Questions',
      selectRequirements: 'Please select template, documents and question types',
      steps: {
        selectTemplate: 'Choose a generation template',
        selectDocument: 'Select at least one document',
        setQuestionTypes: 'Set question types and quantities'
      },
      
      // Question Cards
      answer: 'Answer',
      source: 'Source',
      explanation: 'Explanation',
      document: 'Document',
      
      // Traditional Generate Mode
      traditionalGenerate: 'Preview Generate',
      traditionalMode: 'Traditional Generate Mode',
      traditionalModeDesc: 'Select a template and document for preview generation',
      traditionalGenerateDesc: 'Generate sample questions based on selected template and documents',
      
      // Batch Generate Mode
      batchMode: 'Batch Generate Mode',
      batchModeDesc: 'Pair templates with documents and generate questions in batch',
      batchGenerate: 'Batch Generate',
      batchConfiguration: 'Batch Generation Configuration',
      
      // Batch Generation Related
      selectedDocuments: 'Selected Documents',
      templatePairing: 'Template Pairing',
      pairingPreview: 'Pairing Preview',
      documentTemplateMapping: 'Document-Template Mapping',
      addTemplatePairing: '+ Add Template Pairing',
      totalPairings: 'Total Pairings',
      expectedQuestions: 'Expected Questions',
      pairingCount: ' template pairings',
      selectDocumentsFirst: 'Please select documents above first',
      selectDocumentsAfterPairing: 'Select documents to start pairing',
      clickPairingToPreview: 'Click pairing to view preview',
      willGenerate: 'Will generate',
      questionsCount: ' questions',
      
      // Batch Document Selection
      batchDocumentSelection: 'Batch Document Selection',
      batchSelectDocuments: 'Select documents for batch generation',
      batchSearchDocuments: 'Search batch generation documents...',
      noBatchDocuments: 'No batch generation documents selected',
      addBatchDocuments: 'Please select documents for batch generation'
    },
    
    // Subjects
    subjects: {
      health: 'Health',
      english: 'English',
      history: 'History'
    },
    
    // Questions Management
    questions: {
      title: 'Questions Management',
      subtitle: 'Manage and export generated questions',
      
      // Statistics
      totalQuestions: 'Total Questions',
      byType: 'Distribution by Type',
      bySubject: 'Distribution by Subject',
      byDifficulty: 'Distribution by Difficulty',
      
      // Search and Filter
      search: 'Search',
      searchPlaceholder: 'Search question content...',
      filterByType: 'Filter by Type',
      filterBySubject: 'Filter by Subject',
      filterByDifficulty: 'Filter by Difficulty',
      allTypes: 'All Types',
      allSubjects: 'All Subjects',
      allDifficulties: 'All Difficulties',
      
      // Question Types
      single_choice: 'Single Choice',
      cloze: 'Cloze Test',
      short_answer: 'Short Answer',
      
      // Difficulty
      easy: 'Easy',
      medium: 'Medium',
      hard: 'Hard',
      
      // Question List
      questionList: 'Question List',
      content: 'Question Content',
      type: 'Type',
      subject: 'Subject',
      difficulty: 'Difficulty',
      createdAt: 'Created At',
      actions: 'Actions',
      
      // Actions
      view: 'View',
      edit: 'Edit',
      delete: 'Delete',
      export: 'Export',
      create: 'Create Question',
      
      // Export
      exportTitle: 'Export Questions',
      exportFormat: 'Export Format',
      exportFilters: 'Export Filters',
      confirmExport: 'Confirm Export',
      exporting: 'Exporting...',
      exportSuccess: 'Export successful!',
      exportError: 'Export failed: ',
      
      // Pagination
      showing: 'Showing',
      to: 'to',
      of: 'of',
      results: 'results',
      previous: 'Previous',
      next: 'Next',
      
      // Messages
      loading: 'Loading...',
      noQuestions: 'No questions available',
      noQuestionsHint: 'Please go to "Generate Questions" page to create questions first',
      deleteConfirm: 'Are you sure you want to delete this question?',
      deleteSuccess: 'Question deleted successfully',
      deleteError: 'Delete failed: ',
      
      // Question Detail
      questionDetail: 'Question Details',
      options: 'Options',
      correctAnswer: 'Correct Answer',
      explanation: 'Explanation',
      sourceDocument: 'Source Document',
      sourceContent: 'Source Content',
      chapter: 'Chapter'
    }
  }
}