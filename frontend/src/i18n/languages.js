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
    language: '語言',

    // 科目
    subjects: {
      health: '健康教育',
      math: '數學',
      science: '自然科學',
      english: '英語',
      chinese: '國語',
      social: '社會'
    },

    // Topbar
    topbar: {
      title: '題目生成系統',
      apiStatus: 'API 狀態',
      online: '正常',
      offline: '離線'
    },
    
    // Toast
    toast: {
      operationSuccess: '操作成功',
      operationFailed: '操作失敗',
      operationCompleted: '{operation}已完成',
      unknownError: '發生未知錯誤'
    },
    
    // Subject Modal
    subjectModal: {
      editTitle: '編輯科目',
      createTitle: '新增科目',
      subjectName: '科目名稱',
      subjectNamePlaceholder: '例：健康教育',
      subjectDescription: '科目描述',
      subjectDescriptionPlaceholder: '選填：科目相關說明...',
      subjectGrade: '適用年級',
      allGrades: '所有年級',
      gradeHint: '選填：此科目適用的年級',
      subjectColor: '科目顏色',
      colorHint: '用於顯示科目標籤的顏色',
      preview: '預覽',
      subjectNamePreview: '科目名稱',
      update: '更新',
      create: '建立'
    },
    
    // Exam Preview Components
    examPreview: {
      availableTemplates: '可用的模板組件',
      futureTemplates: '未來可以添加更多模板',
      
      // ExamPreviewModal
      modal: {
        title: '📄 考券預覽 - {title}',
        print: '🖨️ 列印',
        questionCount: '📊 題目數量: {count} 題',
        subject: '📚 科目: {subjects}',
        generatedTime: '⏱️ 生成時間: {time}',
        hint: '💡 提示：這是預覽效果，點擊「列印」可開啟列印視窗',
        openPrintWindow: '🖨️ 開啟列印視窗',
        general: '通用',
        examPreviewLog: '考券預覽',
        popupBlocked: '預覽視窗被阻擋，請檢查瀏覽器設定或查看控制台'
      },
      
      // ExamPrintPreview
      printPreview: {
        defaultSchool: 'Abraham',
        examTime: '考試時間：{duration} 分鐘',
        totalScore: '總分：{score} 分',
        questionCount: '題目數量：{count} 題',
        date: '日期：{date}',
        classLabel: '班級：',
        seatLabel: '座號：',
        nameLabel: '姓名：',
        scoreLabel: '得分：',
        pageInfo: '第 {current} 頁，共 {total} 頁',
        examId: '考試編號：{id}',
        generateTime: '生成時間：{time}'
      }
    },
    
    // 導航
    nav: {
      dashboard: '儀表板',
      dashboardBilingual: 'Dashboard 總覽',
      templates: '模板管理',
      templatesBilingual: 'Exam Prompt Templates 題型模板',
      documents: '文件管理',
      documentsBilingual: 'Upload Documents 文件上傳',
      questions: '問題管理',
      questionsBilingual: 'Exam Library 考題管理',
      generate: '題目生成',
      generateBilingual: 'Exam Generator 考題生成',
      examPaper: '考卷生成',
      examPaperBilingual: 'Exam Paper Generator 考卷生成'
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
      subjectManagement: '科目管理',
      subjectManagementTitle: '📋 科目管理',
      addSubject: '新增科目',
      noSubjects: '尚未建立科目，點擊「新增科目」開始使用',
      templateCount: '個模板',
      confirmDeleteTemplate: '確定要刪除這個模板嗎？',
      initializeDefaultsSuccess: '預設模板初始化成功！',
      initializeDefaultsFailed: '預設模板初始化失敗',
      templateDeleteSuccess: '模板刪除成功！',
      templateDeleteFailed: '模板刪除失敗',
      templateUpdateSuccess: '模板更新成功！',
      templateCreateSuccess: '模板創建成功！',
      templateSaveFailed: '儲存模板時發生錯誤',
      subjectUpdateSuccess: '科目「{name}」更新成功！',
      subjectCreateSuccess: '科目「{name}」建立成功！',
      subjectDeleteSuccess: '科目「{name}」刪除成功！',
      confirmDeleteSubject: '確定要刪除科目「{name}」嗎？',
      forceDeleteSubjectWithTemplates: '這個科目有 {count} 個模板在使用，確定要強制刪除嗎？',
      subjectSaveFailed: '儲存科目失敗',
      subjectDeleteFailed: '刪除科目失敗',
      fetchSubjectsFailed: '取得科目清單失敗',
      fetchSubjectStatsFailed: '取得科目統計失敗',
      questionTypeManagement: '題型管理',
      gradeRequired: '需要年級',
      
      // Template View Modal
      viewModal: {
        title: '模板檢視',
        basicInfo: '基本資訊',
        templateName: '模板名稱',
        version: '版本',
        createdAt: '建立時間',
        updatedAt: '更新時間',
        promptTemplate: 'Prompt 模板',
        llmParams: 'LLM 參數',
        temperature: '溫度',
        maxTokens: '最大字數',
        topP: 'Top P',
        frequencyPenalty: '頻率懲罰',
        previewEffect: '預覽效果',
        jsonFormat: 'JSON 格式',
        sampleContent: '範例文章內容：春天來了，檳花綠放，微風輕拂過綠草地。這是一個美好的季節，充滿了希望與新的開始...'
      },
      // 模板 Modal
      modal: {
        createTitle: '新增模板',
        editTitle: '編輯模板',
        templateName: '模板名稱',
        templateNamePlaceholder: '例：健康單選題預設模板',
        subject: '科目',
        selectSubject: '請選擇科目',
        subjectManageHint: '如需新增科目，請先到模板頁面的「📋 科目管理」建立',
        questionType: '問題類型',
        selectQuestionType: '請選擇題型',
        questionTypeHint: '選擇此模板要生成的問題類型，這將決定 AI 如何解析和生成題目格式',
        promptTemplate: 'Prompt 模板',
        promptHint: '使用 {context} 作為文章內容的替換標記，{count} 作為題目數量的替換標記。支援 Markdown 格式。',
        promptPlaceholder: '請根據以下文章內容，生成{count}道單選題。\\n\\n文章內容：\\n{context}\\n\\n請生成{count}道關於此文章的單選題...',
        llmParams: 'LLM 參數設定',
        temperature: '溫度 (Temperature)',
        temperatureHint: '控制回答的創意性和隨機性',
        maxTokens: '最大字數 (Max Tokens)',
        maxTokensHint: '生成內容的最大長度',
        topP: 'Top P',
        topPHint: '控制詞彙選擇的多樣性',
        frequencyPenalty: '頻率懲罰 (Frequency Penalty)',
        frequencyPenaltyHint: '減少重複內容的傾向',
        preview: '預覽',
        saving: '儲存中...',
        save: '儲存',
        sampleContent: '這裡是文章內容...',
        validation: {
          selectSubject: '請選擇科目！',
          selectQuestionType: '請選擇題型！',
          templateNameRequired: '模板名稱不能為空！',
          templateContentRequired: '模板內容不能為空！',
          saveError: '儲存模板時發生錯誤'
        },
        console: {
          loadSubjects: '📋 載入科目選項',
          updateSubjects: '📋 更新科目選項 (從 props)',
          foundSubject: '✅ 找到對應科目',
          createSubject: '🔄 建立新科目',
          successCreateSubject: '✅ 成功建立新科目',
          handleSubjectFailed: '處理舊科目資料失敗',
          sendTemplateData: '📤 發送模板資料',
          saveTemplateFailed: '儲存模板失敗',
          autoCreateSubject: '自動從模板建立的科目'
        }
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
      grade: '年級',
      gradeFilter: '年級篩選',
      allGrades: '全部年級',
      pageSize: '每頁顯示',
      searchButton: '搜尋',
      deleteSelected: '刪除選擇',
      page: '頁',
      pagePlaceholder: '例如: 1, 2-3, 10',
      contents: '內容',
      image: '圖片',
      
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
      title: 'Question Generator 題目生成器',
      subtitle: '使用AI模板與文件快速生成客製化題目',
      generating: '生成中...',
      generateQuestions: '生成題目',
      clearAllSettings: '清空全部設定',
      autodect:'自動偵測',
      // 設定面板
      selectTemplate: '選擇模板',
      selectDocuments: '選擇文件',
      questionTypes: '題型設定',
      examScope: '考試範圍',
      gradeFilter: '年級篩選',
      generationFailed: '生成失敗',
      questionCountMismatch: '題目數量不符',
      notificationSettings: '通知設定',
      
      // 模板選擇
      noTemplatesAvailable: '尚無可用模板',
      goCreateTemplate: '前往建立模板',
      
      // 文件選擇
      searchDocuments: '搜尋文件...',
      noDocumentsAvailable: '尚無可用文件',
      goImportDocuments: '前往匯入文件',
      showingDocuments: '顯示文件數',
      totalDocuments: '總文件數',
      
      // 題型 (駝峰命名 - 用於前端顯示)
      singleChoice: '單選題',
      cloze: '填空題',
      shortAnswer: '簡答題',
      // G1~G2 題型
      trueFalse: '是非題',
      matching: '配對題',
      sequence: '排序題',
      enumeration: '列舉題',
      symbolIdentification: '符號識別題',
      // 系統題型
      auto: '自動',
      mixed: '混合題型',
      unknown: '未知',

      // 題型 (底線命名 - 用於 API 回傳)
      single_choice: '單選題',
      true_false: '是非題',
      short_answer: '簡答題',
      symbol_identification: '符號識別題',

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
      addBatchDocuments: '請選擇文件進行批次生成',
      
      // 模板組合
      templateGroups: '模板組合',
      templateGroupGenerate: '模板組合生成',
      templateGroupMode: '模板組合模式',
      templateGroupModeDesc: '一個模板可配對多個文件進行批次生成',
      addTemplateGroup: '+ 新增模板組合',
      templateGroupCount: '個模板組合',
      documentsInGroup: '個文件在此組合',
      removeFromGroup: '從組合中移除',
      selectTemplateForGroup: '為組合選擇模板',
      noTemplateSelected: '尚未選擇模板',
      noDocumentsInGroup: '此組合中沒有文件',
      addDocumentsToGroup: '將文件加入此模板組合',
      templateGroup: '模板組合',
      
      // 預覽控制
      showPreview: '顯示預覽',
      hidePreview: '隱藏預覽',
      previewArea: '預覽區域',
      togglePreview: '切換預覽',
      bilingualPreview: '雙語預覽',
      enableBilingual: '開啟雙語',
      disableBilingual: '關閉雙語',
      previewContent: '預覽內容',
      
      // 語言控制
      languageSwitch: '語言切換',
      switchToChinese: '切換到中文',
      switchToEnglish: '切換到英文',
      currentLanguage: '目前語言',
      interfaceLanguage: '介面語言',

      // 訊息和通知
      noResults: '沒有可匯出的結果',
      batchResults: '批次生成結果'
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
      grade: '年級',
      gradeFilter: '年級篩選',
      allGrades: '全部年級',
      allTypes: '全部題型',
      allSubjects: '全部科目',
      allDifficulties: '全部難度',
      save: '儲存',
      updateSuccess: '更新成功',
      
      // 題型
      single_choice: '單選題',
      cloze: '填空題',
      short_answer: '簡答題',
      // G1~G2 題型
      true_false: '是非題',
      matching: '配對題',
      sequence: '排序題',
      enumeration: '列舉題',
      symbol_identification: '符號識別題',
      // 系統題型
      mixed: '混合題型',
      auto: '自動題型',
      
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
      chapter: '章節',
      
      // Questions 頁面專用
      selectAll: '全選',
      examPaper: '考券',
      customExamEditor: '自定義考券編輯器',
      selectedQuestions: '道題目',
      styleEditor: '樣式編輯',
      defaultStyleTemplate: '預設樣式模板',
      standardExam: '標準考券',
      academicExam: '學術考試',
      professionalExam: '專業認證',
      simpleVersion: '簡潔版',
      detailedVersion: '詳細版',
      customStyleSettings: '自定義樣式設定',
      hideEditor: '隱藏編輯器',
      showEditor: '顯示編輯器',
      
      // 版面模板
      layoutTemplate: '版面模板',
      layoutTemplateDescription: '選擇考券的整體版面設計和風格',
      
      // ExamDesigner 新增翻譯
      examDesigner: {
        title: '考券設計器',
        questionsSelected: '道題目已選擇',
        editMode: '編輯模式',
        previewMode: '預覽模式',
        livePreview: '即時預覽',
        reset: '重置',
        saveTemplate: '儲存樣式',
        export: '匯出',
        print: '列印',
        
        // 各種客製化模塊
        layoutTemplate: '版面模板',
        layoutTemplateDescription: '選擇考券的整體版面設計和風格',
        headerCustomization: '頁眉客製化',
        studentInfoCustomization: '學生資訊客製化',
        contentCustomization: '內容客製化',
        answerSheetCustomization: '答案欄客製化',
        
        // 通用設定
        enable: '啟用',
        basicSettings: '基本設定',
        layoutSettings: '版面設定',
        displayOptions: '顯示選項',
        styleSettings: '樣式設定',
        preview: '預覽',
        tip: '提示',
        customTemplateHint: '選擇基礎模板後，你可以進一步客製化每個元素',
        
        // 頁眉設定
        schoolName: '學校名稱',
        schoolNamePlaceholder: '例：○○學校',
        titlePrefix: '標題前綴',
        titlePrefixPlaceholder: '例：Examination',
        subtitle: '副標題',
        subtitlePlaceholder: '例：Final Exam',
        duration: '時間限制',
        durationPlaceholder: '例：90 minutes',
        totalScore: '總分',
        totalScorePlaceholder: '例：100 points',
        centeredLayout: '置中',
        centeredLayoutDesc: '傳統置中排版',
        leftLayout: '左對齊',
        leftLayoutDesc: '現代左側對齊',
        formalLayout: '正式',
        formalLayoutDesc: '學術正式格式',
        showMetadata: '顯示詳細資訊',
        showDate: '顯示日期',
        showQuestionCount: '顯示題目數量',
        
        // 學生資訊設定
        horizontalLayout: '水平排列',
        horizontalLayoutDesc: '欄位横向排列',
        verticalLayout: '垂直排列',
        verticalLayoutDesc: '欄位縱向排列',
        gridLayout: '網格排列',
        gridLayoutDesc: '2x2 網格排列',
        fieldsConfiguration: '欄位配置',
        fieldLabel: '欄位名稱',
        fieldWidth: '欄位寬度',
        addField: '新增欄位',
        backgroundColor: '背景色彩',
        borderStyle: '邊框樣式',
        solidBorder: '實線',
        dashedBorder: '虛線',
        dottedBorder: '點線',
        doubleBorder: '雙線',
        noBorder: '無邊框',
        borderWidth: '邊框寬度',
        padding: '內距',
        
        // 內容設定
        typography: '字體與間距',
        fontSize: '字體大小',
        lineHeight: '行高',
        sectionSpacing: '區段間距',
        questionSpacing: '題目間距',
        questionNumbering: '題目編號',
        numberColor: '編號顏色',
        sectionHeaders: '區段標題',
        showSectionTitles: '顯示區段標題',
        sectionTitleSize: '標題大小',
        sectionTitleColor: '標題顏色',
        underlineSectionTitles: '標題下劃線',
        questionTypeSettings: '題型設定',
        multipleChoice: '選擇題',
        fillInBlanks: '填空題',
        shortAnswer: '簡答題',
        autoQuestions: '自動題',
        includeThisType: '包含此題型',
        sectionTitle: '區段標題',
        pointsPerQuestion: '每題分數',
        inlineOptions: '選項同行顯示',
        answerLines: '答題行數',
        
        // 答案欄設定
        bottomSection: '底部區段',
        bottomSectionDesc: '答案欄在考券底部',
        separatePage: '獨立頁面',
        separatePageDesc: '答案欄獨立成頁',
        rightColumn: '右側欄位',
        rightColumnDesc: '答案欄在右側',
        formatSettings: '格式設定',
        answerSheetTitle: '答案欄標題',
        answerSheetTitlePlaceholder: '例：Answer Sheet',
        answerFormat: '答案格式',
        tableFormat: '表格式',
        gridFormat: '網格式',
        lineFormat: '列式',
        bubbleFormat: '氣泡式',
        questionTypeAnswerSettings: '題型答案設定',
        multipleChoiceAnswers: '選擇題答案',
        fillInBlanksAnswers: '填空題答案',
        shortAnswerAnswers: '簡答題答案',
        columnsCount: '欄位數',
        optionStyle: '選項樣式',
        underlineStyle: '下劃線',
        circleStyle: '圓圈',
        boxStyle: '方框',
        lineWidth: '線條寬度',
        lineStyle: '線條樣式',
        solidLine: '實線',
        dashedLine: '虛線',
        dottedLine: '點線',
        linesPerQuestion: '每題行數',
        lineSpacing: '行間距',
        additionalOptions: '附加選項',
        includeAnswerExplanation: '包含答案解釋',
        includeScoring: '包含評分欄',
        separateAnswerPage: '答案欄獨立成頁'
      },
      
      // 匯出選項
      exportContentSelection: '匯出內容選擇',
      questionsOnly: '只要考券',
      answerSheetOnly: '只要答案券',
      completeExam: '完整考券',
      examHeaderSettings: '考券標題設定',
      enable: '啟用',
      titlePrefix: '標題前綴',
      subtitle: '副標題',
      timeLimit: '時間限制',
      totalScore: '總分',
      questionSectionSettings: '題型區塊設定',
      includeThisType: '包含此題型',
      sectionTitle: '區塊標題',
      pointsPerQuestion: '每題分數',
      multipleChoiceSettings: '選擇題設定',
      fillInBlankSettings: '填空題設定',
      shortAnswerSettings: '簡答題設定',
      autoQuestionSettings: '自動題設定',
      answerSheetSettings: '答案欄設定',
      answerSheetTitle: '答案欄標題',
      studentInfoFields: '學生資訊欄位',
      answerSheetFormat: '答案欄格式',
      tableFormat: '表格式',
      listFormat: '清單式',
      gridFormat: '網格式',
      includeExplanation: '包含答案解析',
      showDetailedExplanation: '顯示詳細解析',
      styleManagement: '樣式管理',
      previewStyle: '預覽樣式',
      saveStyle: '儲存樣式',
      loadStyle: '載入樣式',
      resetStyle: '重置樣式',
      exportingInProgress: '匯出中...',
      exportQuestions: '匯出考券',
      exportAnswerSheet: '匯出答案券',
      exportCompleteExam: '匯出完整考券',
      cancel: '取消',
      
      // UI elements
      headerTitle: '標題和操作按鈕',
      statisticsCards: '統計卡片',
      searchAndFilter: '搜尋和篩選',
      questionList: '問題列表',
      pagination: '分頁',
      selectedQuestionsStyleEditor: '選中問題樣式編輯',
      exportOptionsDropdown: '選中問題匯出選項下拉選單',
      clickOutsideToClose: '點擊外部關閉下拉選單',
      removedOldExportFeature: '移除舊的匯出功能，現在使用自定義考券編輯器',
      
      // Placeholders
      examinationExample: '例: Examination',
      finalExamExample: '例: Final Exam',
      ninetyMinutesExample: '例: 90 minutes',

      sectionTitlePlaceholder: '區塊標題',
      pointsPerQuestionPlaceholder: '每題分數',
      
      // Additional UI text
      multipleChoiceQuestions: 'Multiple Choice Questions',
      fillInBlankQuestions: 'Fill-in-the-Blank Questions',
      shortAnswerQuestions: 'Short Answer Questions',
      autoGeneratedQuestions: 'Auto-Generated Questions',
      name: '姓名',
      studentId: '學號',
      class: '班級',
      answerSheet: '答案券',
      
      // Console messages
      savedSelectedQuestionIds: '已儲存選中題目 ID',
      loadedSelectedQuestionIds: '從 localStorage 載入已選中題目 ID',
      clearedSelectedQuestions: '已清除 localStorage 中的選中題目',
      restoredSelectedQuestions: '恢復了當前頁面的選中題目',
      selectedQuestionsChanged: '選中題目已變更，已儲存至 localStorage',
      failedToSave: '保存選中題目失敗',
      failedToLoad: '載入選中題目失敗',
      failedToClear: '清除選中題目失敗',
      
      // Batch selection
      batchSelection: '批次選擇相關',
      crossPagePersistence: '跨頁面持久化選中題目的 localStorage key',
      localStorageHelperFunctions: 'localStorage 輔助函數',
      editingRelated: '編輯相關',
      removedOldExportFunctions: '移除舊的匯出功能，現在使用批次選擇的自定義考券編輯器',
      originalExportMarkdownRemoved: '原始 exportMarkdownExam 函數已移除，現在使用批次選擇的自定義考券編輯器',
      watchersSection: '監聽器',
      watchForChanges: '監聽選中題目變化並保存到 localStorage',
      loadData: '載入資料',
      clearSelectionAndLocalStorage: '清除選擇和 localStorage',
      automaticallyCalled: '將由 watcher 自動調用 saveSelectedQuestions()'
    },

    // 考卷生成
    examPaper: {
      title: 'Exam Paper Generator 考卷生成器',
      subtitle: '選擇題目或AI生成，快速建立完整考券',
      createExam: '建立考卷',
      examSettings: '考卷設定',

      // 生成模式
      selectMode: '選擇生成模式',
      selectFromLibrary: '從題庫選題',
      selectFromLibraryDesc: '從已有題目中篩選和選擇，適合使用現有題庫',
      aiAutoGenerate: 'AI 自動生成',
      aiAutoGenerateDesc: '根據配置自動生成新題目，適合快速創建考券',

      // 基本資訊
      basicInfo: '基本資訊',
      examTitle: '考卷標題',
      examTitlePlaceholder: '例：第一次段考',
      examSubtitle: '副標題',
      examSubtitlePlaceholder: '例：健康教育科',
      schoolName: '學校名稱',
      schoolNamePlaceholder: '例：○○國民小學',
      examDate: '考試日期',
      duration: '考試時間',
      durationPlaceholder: '例：40',
      minutes: '分鐘',
      totalScore: '總分',
      totalScorePlaceholder: '例：100',
      subject: '科目',
      grade: '年級',

      // 題型配置
      questionTypeSettings: '題型配置',

      // 操作按鈕
      saveDraft: '儲存草稿',
      designExam: '設計考券',
      exportPDF: '匯出 PDF',

      // 選題模式相關
      goToQuestionBank: '前往題庫選題',
      useSelectedQuestions: '使用選中題目生成考券',
      questionsLoaded: '已載入題目',
      syncToConfig: '同步到配置',
      syncConfigDesc: '根據選中題目自動更新題型配置',
      removeQuestion: '移除此題',
      noQuestionsSelected: '尚未選擇任何題目',
      pleaseGoToQuestionBank: '請前往題庫頁面選擇題目，或點擊下方按鈕',
      questionTypeStats: '題型統計',
      totalSelected: '已選總數',

      // 範圍設定
      scopeSettings: '範圍設定',
      selectSubject: '選擇科目',
      selectGrade: '選擇年級',
      selectChapters: '選擇章節',
      allChapters: '全部章節',

      // 題型配置
      questionTypeConfig: '題型配置',
      questionType: '題型',
      questionCount: '題數',
      pointsPerQuestion: '每題分數',
      autoCalculate: '自動計算',
      addQuestionType: '新增題型',
      removeQuestionType: '移除題型',

      // 生成選項
      generationOptions: '生成選項',
      difficulty: '難度',
      easy: '簡單',
      medium: '中等',
      hard: '困難',
      mixed: '混合',
      includeAnswerSheet: '包含答案券',
      includeExplanations: '包含詳解',
      randomOrder: '題目隨機排序',

      // 預覽與匯出
      preview: '預覽',
      generate: '生成考卷',
      generating: '生成中...',
      regenerate: '重新生成',
      exportPDF: '匯出 PDF',
      exportWord: '匯出 Word',
      print: '列印',

      // 訊息
      generationSuccess: '考卷生成成功！',
      generationFailed: '考卷生成失敗',
      noQuestionsAvailable: '沒有可用的題目',
      invalidSettings: '設定不完整',
      pleaseSelectSubject: '請選擇科目',
      pleaseSelectGrade: '請選擇年級',
      pleaseConfigureQuestionTypes: '請配置題型',
      totalScoreMismatch: '總分不符（配置：{configured}，計算：{calculated}）',

      // 考卷模板
      templates: '考卷模板',
      standardTemplate: '標準模板',
      academicTemplate: '學術模板',
      simpleTemplate: '簡潔模板',
      customTemplate: '自訂模板',
      saveTemplate: '儲存模板',
      loadTemplate: '載入模板'
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
    language: 'Language',

    // Subjects
    subjects: {
      health: 'Health Education',
      math: 'Mathematics',
      science: 'Science',
      english: 'English',
      chinese: 'Chinese',
      social: 'Social Studies'
    },

    // Topbar
    topbar: {
      title: 'Question Generator',
      apiStatus: 'API Status',
      online: 'Online',
      offline: 'Offline'
    },
    
    // Toast
    toast: {
      operationSuccess: 'Operation Successful',
      operationFailed: 'Operation Failed',
      operationCompleted: '{operation} completed',
      unknownError: 'Unknown error occurred'
    },
    
    // Subject Modal
    subjectModal: {
      editTitle: 'Edit Subject',
      createTitle: 'Add Subject',
      subjectName: 'Subject Name',
      subjectNamePlaceholder: 'e.g., Health Education',
      subjectDescription: 'Subject Description',
      subjectDescriptionPlaceholder: 'Optional: Subject-related description...',
      subjectGrade: 'Applicable Grade',
      allGrades: 'All Grades',
      gradeHint: 'Optional: The grade level this subject applies to',
      subjectColor: 'Subject Color',
      colorHint: 'Color used to display subject tags',
      preview: 'Preview',
      subjectNamePreview: 'Subject Name',
      update: 'Update',
      create: 'Create'
    },
    
    // Exam Preview Components
    examPreview: {
      availableTemplates: 'Available template components',
      futureTemplates: 'More templates can be added in the future',
      
      // ExamPreviewModal
      modal: {
        title: '📄 Exam Preview - {title}',
        print: '🖨️ Print',
        questionCount: '📊 Question Count: {count} questions',
        subject: '📚 Subject: {subjects}',
        generatedTime: '⏱️ Generated Time: {time}',
        hint: '💡 Tip: This is a preview effect, click "Print" to open print window',
        openPrintWindow: '🖨️ Open Print Window',
        general: 'General',
        examPreviewLog: 'Exam Preview',
        popupBlocked: 'Preview window blocked, please check browser settings or see console'
      },
      
      // ExamPrintPreview
      printPreview: {
        defaultSchool: '○○ School',
        examTime: 'Exam Time: {duration} minutes',
        totalScore: 'Total Score: {score} points',
        questionCount: 'Question Count: {count} questions',
        date: 'Date: {date}',
        classLabel: 'Class: ',
        seatLabel: 'Seat: ',
        nameLabel: 'Name: ',
        scoreLabel: 'Score: ',
        pageInfo: 'Page {current} of {total}',
        examId: 'Exam ID: {id}',
        generateTime: 'Generated Time: {time}'
      }
    },
    
    // Navigation
    nav: {
      dashboard: 'Dashboard',
      dashboardBilingual: 'Dashboard 總覽',
      templates: 'Templates',
      templatesBilingual: 'Exam Prompt Templates 題型模板',
      documents: 'Documents',
      documentsBilingual: 'Upload Documents 文件上傳',
      questions: 'Questions',
      questionsBilingual: 'Exam Library 考題管理',
      generate: 'Generate',
      generateBilingual: 'Exam Generator 考題生成',
      examPaper: 'Exam Paper',
      examPaperBilingual: 'Exam Paper Generator 考卷生成'
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
      subjectManagement: 'Subject Management',
      subjectManagementTitle: '📋 Subject Management',
      addSubject: 'Add Subject',
      noSubjects: 'No subjects created yet, click "Add Subject" to get started',
      templateCount: 'templates',
      confirmDeleteTemplate: 'Are you sure you want to delete this template?',
      initializeDefaultsSuccess: 'Default templates initialized successfully!',
      initializeDefaultsFailed: 'Default templates initialization failed',
      templateDeleteSuccess: 'Template deleted successfully!',
      templateDeleteFailed: 'Template deletion failed',
      templateUpdateSuccess: 'Template updated successfully!',
      templateCreateSuccess: 'Template created successfully!',
      templateSaveFailed: 'Failed to save template',
      subjectUpdateSuccess: 'Subject "{name}" updated successfully!',
      subjectCreateSuccess: 'Subject "{name}" created successfully!',
      subjectDeleteSuccess: 'Subject "{name}" deleted successfully!',
      confirmDeleteSubject: 'Are you sure you want to delete subject "{name}"?',
      forceDeleteSubjectWithTemplates: 'This subject has {count} templates in use, are you sure you want to force delete it?',
      subjectSaveFailed: 'Failed to save subject',
      subjectDeleteFailed: 'Failed to delete subject',
      fetchSubjectsFailed: 'Failed to fetch subjects',
      fetchSubjectStatsFailed: 'Failed to fetch subject statistics',
      questionTypeManagement: 'Question Type Management',
      gradeRequired: 'Grade Required',
      
      // Template View Modal
      viewModal: {
        title: 'Template View',
        basicInfo: 'Basic Information',
        templateName: 'Template Name',
        version: 'Version',
        createdAt: 'Created At',
        updatedAt: 'Updated At',
        promptTemplate: 'Prompt Template',
        llmParams: 'LLM Parameters',
        temperature: 'Temperature',
        maxTokens: 'Max Tokens',
        topP: 'Top P',
        frequencyPenalty: 'Frequency Penalty',
        previewEffect: 'Preview Effect',
        jsonFormat: 'JSON Format',
        sampleContent: 'Sample article content: Spring has arrived, cherry blossoms bloom, and a gentle breeze caresses the green grass. This is a beautiful season filled with hope and new beginnings...'
      },
      // Template Modal
      modal: {
        createTitle: 'Create Template',
        editTitle: 'Edit Template',
        templateName: 'Template Name',
        templateNamePlaceholder: 'e.g., Health Multiple Choice Default Template',
        subject: 'Subject',
        selectSubject: 'Please select a subject',
        subjectManageHint: 'To add a new subject, please go to "📋 Subject Management" on the templates page',
        questionType: 'Question Type',
        selectQuestionType: 'Please select question type',
        questionTypeHint: 'Choose the question type this template will generate, which determines how AI parses and generates question formats',
        promptTemplate: 'Prompt Template',
        promptHint: 'Use {context} as placeholder for article content and {count} as placeholder for question count. Supports Markdown format.',
        promptPlaceholder: 'Please generate {count} multiple choice questions based on the following article content.\\n\\nArticle content:\\n{context}\\n\\nPlease generate {count} multiple choice questions about this article...',
        llmParams: 'LLM Parameters',
        temperature: 'Temperature',
        temperatureHint: 'Controls creativity and randomness of responses',
        maxTokens: 'Max Tokens',
        maxTokensHint: 'Maximum length of generated content',
        topP: 'Top P',
        topPHint: 'Controls vocabulary selection diversity',
        frequencyPenalty: 'Frequency Penalty',
        frequencyPenaltyHint: 'Reduces tendency for repetitive content',
        preview: 'Preview',
        saving: 'Saving...',
        save: 'Save',
        sampleContent: 'Here is the article content...',
        validation: {
          selectSubject: 'Please select a subject!',
          selectQuestionType: 'Please select a question type!',
          templateNameRequired: 'Template name cannot be empty!',
          templateContentRequired: 'Template content cannot be empty!',
          saveError: 'Error occurred while saving template'
        },
        console: {
          loadSubjects: '📋 Load subject options',
          updateSubjects: '📋 Update subject options (from props)',
          foundSubject: '✅ Found corresponding subject',
          createSubject: '🔄 Create new subject',
          successCreateSubject: '✅ Successfully created new subject',
          handleSubjectFailed: 'Failed to handle legacy subject data',
          sendTemplateData: '📤 Send template data',
          saveTemplateFailed: 'Failed to save template',
          autoCreateSubject: 'Auto-created from template'
        }
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
      grade: 'Grade',
      gradeFilter: 'Grade Filter',
      allGrades: 'All Grades',
      pageSize: 'Items per page',
      searchButton: 'Search',
      deleteSelected: 'Delete Selected',
      page: 'Page',
      pagePlaceholder: 'e.g., 1, 2-3, 10',
      contents: 'Contents',
      image: 'Image',
      
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
      title: 'Question Generator',
      subtitle: 'Generate customized questions quickly with AI templates and documents',
      generating: 'Generating...',
      generateQuestions: 'Generate Questions',
      clearAllSettings: 'Clear All Settings',
      traditionalGenerate :'Generate Questions',
      traditionalMode:'Traditional Generation Mode',
      traditionalModeDesc:'Select template and document for question generation',
      traditionalGenerateDesc:'Generate questions based on template and document',
      autoDetect:'Auto Detect',
      questionTypeHint:'Select QuestionType',
      //batch
      batchMode:'Batch Generate ',
      batchModeDesc:'Generate a lot of question with one click',
      batchGenerate :'Batch Generate',
      // Settings Panel
      selectTemplate: 'Select Template',
      selectDocuments: 'Select Documents',
      questionTypes: 'Question Types',
      questionType:'Question Type',
      examScope: 'Exam Scope',
      gradeFilter: 'Grade Filter',
      generationFailed: 'Generation Failed',
      questionCountMismatch: 'Question Count Mismatch',
      notificationSettings: 'Notification Settings',
      // Template Selection
      noTemplatesAvailable: 'No templates available',
      goCreateTemplate: 'Go to create templates',
      
      // Document Selection
      searchDocuments: 'Search documents...',
      noDocumentsAvailable: 'No documents available',
      goImportDocuments: 'Go to import documents',
      showingDocuments: 'Showing',
      totalDocuments: 'Total',
      
      // Question Types (camelCase - for frontend display)
      singleChoice: 'Single Choice',
      cloze: 'Cloze Test',
      shortAnswer: 'Short Answer',
      // G1~G2 Question Types
      trueFalse: 'True/False',
      matching: 'Matching',
      sequence: 'Sequence',
      enumeration: 'Enumeration',
      symbolIdentification: 'Symbol Identification',
      // System Question Types
      auto: 'Auto',
      mixed: 'Mixed Type',
      unknown: 'Unknown',

      // Question Types (snake_case - for API response and ExamPaper)
      single_choice: 'Single Choice',
      true_false: 'True/False',
      short_answer: 'Short Answer',
      symbol_identification: 'Symbol Identification',

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
      traditionalGenerate: 'Generate',
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
      addBatchDocuments: 'Please select documents for batch generation',
      
      // Template Groups
      templateGroups: 'Template Groups',
      templateGroupGenerate: 'Template Group Generate',
      templateGroupMode: 'Template Group Mode',
      templateGroupModeDesc: 'One template can be paired with multiple documents for batch generation',
      addTemplateGroup: '+ Add Template Group',
      templateGroupCount: 'template groups',
      documentsInGroup: 'documents in group',
      removeFromGroup: 'Remove from Group',
      selectTemplateForGroup: 'Select Template for Group',
      noTemplateSelected: 'No Template Selected',
      noDocumentsInGroup: 'No documents in this group',
      addDocumentsToGroup: 'Add documents to this template group',
      templateGroup: 'Template Group',
      
      // Preview Controls
      showPreview: 'Show Preview',
      hidePreview: 'Hide Preview',
      previewArea: 'Preview Area',
      togglePreview: 'Toggle Preview',
      bilingualPreview: 'Bilingual Preview',
      enableBilingual: 'Enable Bilingual',
      disableBilingual: 'Disable Bilingual',
      previewContent: 'Preview Content',
      
      // Language Controls
      languageSwitch: 'Language Switch',
      switchToChinese: 'Switch to Chinese',
      switchToEnglish: 'Switch to English',
      currentLanguage: 'Current Language',
      interfaceLanguage: 'Interface Language',

      // Messages and Notifications
      noResults: 'No results to export',
      batchResults: 'Batch Generation Results'
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
      grade: 'Grade',
      gradeFilter: 'Grade Filter',
      allGrades: 'All Grades',
      allTypes: 'All Types',
      allSubjects: 'All Subjects',
      allDifficulties: 'All Difficulties',
      save: 'Save',
      updateSuccess: 'Update Successful',
      
      // Question Types
      single_choice: 'Single Choice',
      cloze: 'Cloze Test',
      short_answer: 'Short Answer',
      // G1~G2 Question Types
      true_false: 'True/False',
      matching: 'Matching',
      sequence: 'Sequence',
      enumeration: 'Enumeration',
      symbol_identification: 'Symbol Identification',
      // System Question Types
      mixed: 'Mixed Type',
      auto: 'Auto Type',
      
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
      chapter: 'Chapter',
      
      // Questions Page Specific
      selectAll: 'Select All',
      examPaper: 'Exam Paper',
      customExamEditor: 'Custom Exam Editor',
      selectedQuestions: ' Questions',
      styleEditor: 'Style Editor',
      defaultStyleTemplate: 'Default Style Template',
      standardExam: 'Standard Exam',
      academicExam: 'Academic Exam',
      professionalExam: 'Professional Certification',
      simpleVersion: 'Simple Version',
      detailedVersion: 'Detailed Version',
      customStyleSettings: 'Custom Style Settings',
      hideEditor: 'Hide Editor',
      showEditor: 'Show Editor',
      exportContentSelection: 'Export Content Selection',
      questionsOnly: 'Questions Only',
      answerSheetOnly: 'Answer Sheet Only',
      completeExam: 'Complete Exam',
      examHeaderSettings: 'Exam Header Settings',
      enable: 'Enable',
      titlePrefix: 'Title Prefix',
      subtitle: 'Subtitle',
      timeLimit: 'Time Limit',
      totalScore: 'Total Score',
      questionSectionSettings: 'Question Section Settings',
      includeThisType: 'Include This Type',
      sectionTitle: 'Section Title',
      pointsPerQuestion: 'Points per Question',
      multipleChoiceSettings: 'Multiple Choice Settings',
      fillInBlankSettings: 'Fill-in-the-Blank Settings',
      shortAnswerSettings: 'Short Answer Settings',
      autoQuestionSettings: 'Auto Question Settings',
      answerSheetSettings: 'Answer Sheet Settings',
      answerSheetTitle: 'Answer Sheet Title',
      studentInfoFields: 'Student Information Fields',
      answerSheetFormat: 'Answer Sheet Format',
      tableFormat: 'Table Format',
      listFormat: 'List Format',
      gridFormat: 'Grid Format',
      includeExplanation: 'Include Answer Explanation',
      showDetailedExplanation: 'Show Detailed Explanation',
      styleManagement: 'Style Management',
      previewStyle: 'Preview Style',
      saveStyle: 'Save Style',
      loadStyle: 'Load Style',
      resetStyle: 'Reset Style',
      exportingInProgress: 'Exporting...',
      exportQuestions: 'Export Questions',
      exportAnswerSheet: 'Export Answer Sheet',
      exportCompleteExam: 'Export Complete Exam',
      cancel: 'Cancel',
      
      // UI elements
      headerTitle: 'Title and Action Buttons',
      statisticsCards: 'Statistics Cards',
      searchAndFilter: 'Search and Filter',
      questionList: 'Question List',
      pagination: 'Pagination',
      selectedQuestionsStyleEditor: 'Selected Questions Style Editor',
      exportOptionsDropdown: 'Selected Questions Export Options Dropdown',
      clickOutsideToClose: 'Click Outside to Close Dropdown',
      removedOldExportFeature: 'Removed old export feature, now using custom exam editor',
      
      // Placeholders
      examinationExample: 'e.g., Examination',
      finalExamExample: 'e.g., Final Exam',
      ninetyMinutesExample: 'e.g., 90 minutes',
      hundredPointsExample: 'e.g., 100 points',
      sectionTitlePlaceholder: 'Section Title',
      pointsPerQuestionPlaceholder: 'Points per Question',
      
      // Additional UI text
      multipleChoiceQuestions: 'Multiple Choice Questions',
      fillInBlankQuestions: 'Fill-in-the-Blank Questions',
      shortAnswerQuestions: 'Short Answer Questions',
      autoGeneratedQuestions: 'Auto-Generated Questions',
      name: 'Name',
      studentId: 'Student ID',
      class: 'Class',
      answerSheet: 'Answer Sheet',
      
      // Console messages
      savedSelectedQuestionIds: 'Saved selected question IDs',
      loadedSelectedQuestionIds: 'Loaded selected question IDs from localStorage',
      clearedSelectedQuestions: 'Cleared selected questions from localStorage',
      restoredSelectedQuestions: 'Restored selected questions for current page',
      selectedQuestionsChanged: 'Selected questions changed, saved to localStorage',
      failedToSave: 'Failed to save selected questions',
      failedToLoad: 'Failed to load selected questions',
      failedToClear: 'Failed to clear selected questions',
      
      // Batch selection
      batchSelection: 'Batch selection related',
      crossPagePersistence: 'Cross-page persistence for selected questions using localStorage',
      localStorageHelperFunctions: 'localStorage helper functions',
      editingRelated: 'Editing related',
      removedOldExportFunctions: 'Removed old export functions, now using batch selection custom exam editor',
      originalExportMarkdownRemoved: 'Original exportMarkdownExam function removed, now using batch selection custom exam editor',
      watchersSection: 'Watchers',
      watchForChanges: 'Watch for changes in selected questions and save to localStorage',
      loadData: 'Load Data',
      clearSelectionAndLocalStorage: 'Clear selection and localStorage',
      automaticallyCalled: 'saveSelectedQuestions() will be called automatically by the watcher'
    },

    // Exam Paper Generator
    examPaper: {
      title: 'Exam Paper Generator',
      subtitle: 'Select questions or generate with AI to create complete exam papers',
      createExam: 'Create Exam',
      examSettings: 'Exam Settings',

      // Generation Modes
      selectMode: 'Select Generation Mode',
      selectFromLibrary: 'Select from Library',
      selectFromLibraryDesc: 'Select from existing questions, suitable for using question bank',
      aiAutoGenerate: 'AI Auto Generate',
      aiAutoGenerateDesc: 'Automatically generate new questions based on configuration',

      // Basic Information
      basicInfo: 'Basic Information',
      examTitle: 'Exam Title',
      examTitlePlaceholder: 'e.g., First Midterm Exam',
      examSubtitle: 'Subtitle',
      examSubtitlePlaceholder: 'e.g., Health Education',
      schoolName: 'School Name',
      schoolNamePlaceholder: 'e.g., OO Elementary School',
      examDate: 'Exam Date',
      duration: 'Duration',
      durationPlaceholder: 'e.g., 40',
      minutes: 'minutes',
      totalScore: 'Total Score',
      totalScorePlaceholder: 'e.g., 100',
      subject: 'Subject',
      grade: 'Grade',

      // Question Type Settings
      questionTypeSettings: 'Question Type Settings',

      // Action Buttons
      saveDraft: 'Save Draft',
      designExam: 'Design Exam',
      exportPDF: 'Export PDF',

      // Selection Mode Related
      goToQuestionBank: 'Go to Question Bank',
      useSelectedQuestions: 'Use Selected Questions for Exam',
      questionsLoaded: 'Questions Loaded',
      syncToConfig: 'Sync to Config',
      syncConfigDesc: 'Auto-update question type config based on selected questions',
      removeQuestion: 'Remove Question',
      noQuestionsSelected: 'No Questions Selected',
      pleaseGoToQuestionBank: 'Please go to Question Bank to select questions, or click the button below',
      questionTypeStats: 'Question Type Stats',
      totalSelected: 'Total Selected',

      // Scope Settings
      scopeSettings: 'Scope Settings',
      selectSubject: 'Select Subject',
      selectGrade: 'Select Grade',
      selectChapters: 'Select Chapters',
      allChapters: 'All Chapters',

      // Question Type Configuration
      questionTypeConfig: 'Question Type Configuration',
      questionType: 'Question Type',
      questionCount: 'Question Count',
      pointsPerQuestion: 'Points per Question',
      autoCalculate: 'Auto Calculate',
      addQuestionType: 'Add Question Type',
      removeQuestionType: 'Remove Question Type',

      // Generation Options
      generationOptions: 'Generation Options',
      difficulty: 'Difficulty',
      easy: 'Easy',
      medium: 'Medium',
      hard: 'Hard',
      mixed: 'Mixed',
      includeAnswerSheet: 'Include Answer Sheet',
      includeExplanations: 'Include Explanations',
      randomOrder: 'Random Question Order',

      // Preview and Export
      preview: 'Preview',
      generate: 'Generate Exam',
      generating: 'Generating...',
      regenerate: 'Regenerate',
      exportPDF: 'Export PDF',
      exportWord: 'Export Word',
      print: 'Print',

      // Messages
      generationSuccess: 'Exam generated successfully!',
      generationFailed: 'Exam generation failed',
      noQuestionsAvailable: 'No questions available',
      invalidSettings: 'Incomplete settings',
      pleaseSelectSubject: 'Please select a subject',
      pleaseSelectGrade: 'Please select a grade',
      pleaseConfigureQuestionTypes: 'Please configure question types',
      totalScoreMismatch: 'Total score mismatch (configured: {configured}, calculated: {calculated})',

      // Exam Templates
      templates: 'Exam Templates',
      standardTemplate: 'Standard Template',
      academicTemplate: 'Academic Template',
      simpleTemplate: 'Simple Template',
      customTemplate: 'Custom Template',
      saveTemplate: 'Save Template',
      loadTemplate: 'Load Template'
    }
  }
}