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
    selectAll: '全選',

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
      selectGrade: '選擇年級',
      customGrade: '自訂年級',
      customGradePlaceholder: '輸入自訂年級',
      gradePlaceholder: '例：G1, G2-G3, 國小',
      gradeHint: '必填：此科目適用的年級',
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
      imageQuestionSection: '圖片題',
      imageQuestionInstruction: '根據圖片回答下列問題',

      // ExamPreviewModal
      modal: {
        title: '考券預覽 - {title}',
        print: '列印',
        questionCount: '題目數量: {count} 題',
        subject: '科目: {subjects}',
        generatedTime: '生成時間: {time}',
        hint: '提示：這是預覽效果，點擊「列印」可開啟列印視窗',
        openPrintWindow: '開啟列印視窗',
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

    // 導航（側邊欄保持中英文雙語）
    nav: {
      dashboard: '總覽',
      dashboardBilingual: 'Dashboard\n總覽',
      templates: '題型及科目管理',
      templatesBilingual: 'Exam Prompt & Subjects\n題型及科目管理',
      documents: '文件上傳',
      documentsBilingual: 'Upload Documents\n文件上傳',
      questions: '考題管理',
      questionsBilingual: 'Exam Library\n考題管理',
      generate: '考題生成',
      generateBilingual: 'Exam Generator\n考題生成',
      examPaper: '考卷生成',
      examPaperBilingual: 'Exam Paper Generator\n考卷生成',
      imageQuestions: '圖片題目',
      imageQuestionsBilingual: 'Image Questions\n圖片題目'
    },

    // 儀表板（總覽）
    dashboard: {
      title: '總覽',
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

    // 模板管理（題型及科目管理）
    templates: {
      title: '題型及科目管理',
      createTemplate: '新增模板',
      initializeDefaults: '初始化預設模板',
      filterBySubject: '科目篩選',
      filterByGrade: '年級篩選',
      allSubjects: '全部科目',
      allGrades: '全部年級',
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
      subjectManagementTitle: '科目管理',
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
      gradeRequired: '適用年級為必填欄位',
      duplicateSubjectName: '科目「{name}」已存在，請使用其他名稱',

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
        subjectManageHint: '如需新增科目，請先到模板頁面的「科目管理」建立',
        questionType: '問題類型',
        selectQuestionType: '請選擇題型',
        questionTypeHint: '選擇此模板要生成的問題類型，這將決定 AI 如何解析和生成題目格式',
        applicableGrades: '適用年級',
        applicableGradesHint: '選擇此模板適用的年級，可多選',
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
          loadSubjects: '載入科目選項',
          updateSubjects: '更新科目選項 (從 props)',
          foundSubject: '找到對應科目',
          createSubject: '建立新科目',
          successCreateSubject: '成功建立新科目',
          handleSubjectFailed: '處理舊科目資料失敗',
          sendTemplateData: '發送模板資料',
          saveTemplateFailed: '儲存模板失敗',
          autoCreateSubject: '自動從模板建立的科目'
        }
      }
    },

    // 文件管理（文件上傳）
    documents: {
      title: '文件上傳',
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
      page: '頁數',
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
      excelTitle: '標題',
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

      // 科目選擇
      selectSubject: '選擇科目',
      selectExisting: '選擇現有',
      addNew: '新增',
      newSubjectPlaceholder: '輸入新科目名稱',

      // 訊息
      uploadError: '上傳失敗: ',
      saveError: '儲存失敗: ',
      deleteConfirm: '確定要刪除文件',
      deleteSuccess: '文件已刪除',
      deleteError: '刪除失敗: ',
      deleting: '刪除中...',
      noSelection: '請先選擇要刪除的文件',

      comingSoon: '文件管理功能開發中',
      phase2Features: '此功能將在 Phase 2 中實作，包括：',
      features: {
        excelImport: 'Excel 批量匯入',
        chapterManagement: '章節篩選與管理',
        imageTextAssociation: '圖片與文字關聯',
        multiSelectInterface: '多選勾選介面'
      }
    },

    // 題目生成（考題生成）
    generate: {
      title: '考題生成',
      generating: '生成中...',
      generateQuestions: '生成題目',
      clearAllSettings: '清空全部設定',
      autodect: '自動偵測',

      // 設定面板（使用 Step 格式）
      selectTemplate: 'Step1. 選擇模板',
      selectDocuments: 'Step2. 選擇考題範圍',
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
      trueFalse: '是非題',
      matching: '配對題',
      sequence: '排序題',
      enumeration: '列舉題',
      symbolIdentification: '符號識別題',
      auto: '自動',
      mixed: '混合題型',
      unknown: '未知',

      // 題型 (底線命名 - 用於 API 回傳)
      single_choice: '單選題',
      true_false: '是非題',
      short_answer: '簡答題',
      symbol_identification: '符號識別題',
      image_question: '圖片題',

      totalQuestions: '總題數',
      questionCount: '生成數量',

      // 目標年級
      targetGrade: '目標年級',
      selectGrade: '請選擇',
      targetGradeDesc: '生成的題目將標記為此年級',

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

      // 生成模式（移除標題）
      traditionalGenerate: '生成題目',
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
      characters: '字符',
      bilingualPreview: '雙語預覽',
      enableBilingual: '開啟雙語',
      disableBilingual: '關閉雙語',
      previewContent: '預覽內容',

      // 訊息和通知
      noResults: '沒有可匯出的結果',
      batchResults: '批次生成結果'
    },

    // 問題管理（考題管理）
    questions: {
      title: '考題管理',

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
      true_false: '是非題',
      matching: '配對題',
      sequence: '排序題',
      enumeration: '列舉題',
      symbol_identification: '符號識別題',
      image_question: '圖片題',
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
      batchDelete: '批量刪除',
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
      noQuestionsHint: '請先到「考題生成」頁面生成題目',
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
      pageNumber: '頁數',
      gradeInfo: '年級',
      gradePlaceholder: '例如: G1, 一年級',

      // 科目選擇
      selectSubject: '選擇科目',
      selectExisting: '選擇現有',
      addNew: '新增',
      newSubjectPlaceholder: '輸入新科目名稱',

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

      // ExamDesigner 相關
      examDesigner: {
        title: '考券設計器',
        questionsSelected: '道題目已選擇',
        editMode: '編輯模式',
        previewMode: '預覽模式',
        livePreview: '即時預覽',
        reset: '重置',
        saveTemplate: '儲存樣式',
        export: '匯出',
        exportPDF: '匯出試題卷',
        exportAnswerSheet: '匯出答案卷',
        print: '列印',
        close: '關閉',

        // 題型管理
        examDesign: '考券設計',
        examDesignDescription: '設計你的專屬考券格式',
        questionTypeOrder: '題型排序',
        questionTypeOrderDescription: '拖拽調整不同題型在考券中的順序',
        questions: '題',
        noQuestions: '無題目',
        moveUp: '向上移動',
        moveDown: '向下移動',
        examStructurePreview: '考券結構預覽',

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
        titlePrefixPlaceholder: '例：期中考試',
        subtitle: '副標題',
        subtitlePlaceholder: '例：健康教育科',
        duration: '時間限制',
        durationPlaceholder: '例：90 分鐘',
        totalScore: '總分',
        totalScorePlaceholder: '例：100 分',
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
        answerSheetTitlePlaceholder: '例：答案卷',
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

      // 錯誤訊息
      contentRequired: '題目內容不能為空',
      answerRequired: '正確答案不能為空',
      optionsRequired: '至少需要兩個選項',
      updateError: '更新失敗：'
    },

    // 考券設計器
    examDesigner: {
      title: '考券設計器',
      questionsSelected: '道題目已選擇',
      editMode: '編輯模式',
      previewMode: '預覽模式',
      livePreview: '即時預覽',
      exportPDF: '匯出試題卷',
      exportAnswerSheet: '匯出答案卷',
      close: '關閉',

      // 題型管理
      examDesign: '考券設計',
      examDesignDescription: '設計你的專屬考券格式',
      questionTypeOrder: '題型排序',
      questionTypeOrderDescription: '拖拽調整不同題型在考券中的順序',
      questions: '題',
      noQuestions: '無題目',
      moveUp: '向上移動',
      moveDown: '向下移動',
      examStructurePreview: '考券結構預覽',

      // 樣式設定
      styleSettings: '樣式設定',
      styleSettingsDescription: '調整考券的字體、行距和圖片大小',
      fontSize: '字體大小',
      lineHeight: '行距',
      imageSize: '圖片大小',
      fontSizeSmall: '小',
      fontSizeStandard: '標準',
      fontSizeLarge: '大',
      lineHeightCompact: '緊湊',
      lineHeightStandard: '標準',
      lineHeightLoose: '寬鬆',
      lineHeightVeryLoose: '很寬',
      imageSizeSmall: '小',
      imageSizeMedium: '中',
      imageSizeLarge: '大',

      // 進階字體設定
      advancedTypography: '進階字體設定',
      advancedTypographyDescription: '個別調整各元素的字體大小、粗體、對齊',
      resetToDefault: '重置為預設值',

      // 元素標籤
      elementSchoolName: '校名',
      elementSectionTitle: '大題',
      elementSectionInstruction: '題目指示',
      elementStudentInfo: '學生資訊',
      elementParentSignature: '家長簽名',
      elementQuestionContent: '題目內容',
      elementExamScope: '範圍/副標題',

      // 顯示選項
      displayOptions: '顯示選項',
      displayOptionsDescription: '控制考券上顯示的區域',
      enableStudentInfo: '啟用學生資訊欄位',
      enableParentSignature: '啟用家長簽名框（左上角）'
    },

    // 圖片題目管理
    imageQuestions: {
      title: '圖片題目管理',
      uploadExcel: '上傳 Excel',
      downloadTemplate: '下載範本',
      verifyImages: '驗證圖片',
      verifySelected: '驗證選中',
      createNew: '新增圖片題目',
      createTitle: '新增圖片題目',
      create: '建立',

      // 統計
      totalQuestions: '總題目數',
      verified: '已驗證',
      unverified: '未驗證',
      bySubject: '按科目',
      byGrade: '按年級',

      // 搜尋和篩選
      search: '搜尋',
      searchPlaceholder: '搜尋題目描述或圖片名稱...',
      subject: '科目',
      allSubjects: '全部科目',
      grade: '年級',
      allGrades: '全部年級',
      chapter: '章節',
      allChapters: '全部章節',
      verificationStatus: '驗證狀態',
      allStatus: '全部狀態',
      verifiedOnly: '已驗證',
      unverifiedOnly: '未驗證',

      // 題目清單
      questionList: '圖片題目清單',
      totalCount: '筆題目',
      loading: '載入中...',
      noQuestions: '尚無圖片題目',
      noQuestionsHint: '請上傳 Excel 檔案來匯入圖片題目',

      // 題目卡片
      questionImage: '問題圖片',
      answerImage: '答案圖片',
      page: '頁碼',
      imageVerified: '圖片已驗證',
      imageNotVerified: '圖片未驗證',
      questionImageMissing: '問題圖片缺失',
      answerImageMissing: '答案圖片缺失',

      // 分頁
      previous: '上一頁',
      next: '下一頁',
      showing: '顯示',
      to: '到',
      of: '筆，共',
      results: '筆結果',

      // 上傳 Modal
      uploadPreview: 'Excel 上傳預覽',
      uploadSuccess: '成功解析 Excel 文件',
      fileName: '檔案名稱',
      totalRows: '總行數',
      validRows: '有效行數',
      errorRows: '錯誤行數',
      row: '行',
      error: '錯誤',
      warnings: '警告',
      confirmSave: '確認儲存',
      cancel: '取消',
      saving: '儲存中...',
      saveSuccess: '成功儲存 {count} 筆圖片題目',
      saveError: '儲存失敗：',

      // 詳情 Modal
      questionDetail: '圖片題目詳情',
      edit: '編輯',
      delete: '刪除',
      close: '關閉',
      description: '題目描述',
      createdAt: '建立時間',
      updatedAt: '更新時間',
      importBatch: '匯入批次',

      // 創建 Modal
      searchQuestionImage: '搜尋問題圖片...',
      searchAnswerImage: '搜尋答案圖片...',
      selectSubject: '請選擇科目',
      selectExisting: '選擇現有',
      addNew: '新增科目',
      newSubjectPlaceholder: '輸入新科目名稱',
      newSubjectHint: '系統將自動建立此科目',
      chapterPlaceholder: '例如：Chapter 1',
      pagePlaceholder: '例如：1-5',
      descriptionPlaceholder: '選填：描述題目類型或內容...',
      questionImageRequired: '請選擇問題圖片',
      subjectRequired: '請選擇或輸入科目',
      noImagesFound: '找不到符合的圖片',
      clearSelection: '清除',

      // 訊息
      uploadError: '上傳失敗：',
      deleteConfirm: '確定要刪除此圖片題目嗎？',
      deleteSuccess: '圖片題目已刪除',
      deleteError: '刪除失敗：',
      verifySuccess: '驗證完成：{verified} 個成功，{failed} 個失敗',
      verifyError: '驗證失敗：',
      updateSuccess: '更新成功',
      updateError: '更新失敗：',
      createSuccess: '圖片題目建立成功',
      createError: '建立失敗',

      // 自由輸入與缺失圖片提醒
      enterImageName: '輸入圖片名稱（不含副檔名）',
      imageNameHint: '輸入圖片名稱，稍後可上傳對應圖片檔案',
      missingImagesTitle: '需要上傳的圖片',
      missingQuestionImages: '問題圖片缺失',
      missingAnswerImages: '答案圖片缺失',
      missingImagesHint: '請將上述圖片檔案上傳至對應目錄後，點擊「驗證選中」按鈕進行驗證',
      missingImage: '缺少: {filename}',

      // 圖片上傳
      uploadImage: '上傳圖片',
      uploadImageTitle: '上傳圖片檔案',
      imageTypeLabel: '圖片類型',
      questionImageType: '問題圖片',
      answerImageType: '答案圖片',
      customImageName: '圖片名稱',
      customNamePlaceholder: '輸入圖片名稱（不含副檔名）',
      customNameHint: '留空則使用原始檔案名稱',
      dropImageHere: '拖放圖片到此處，或點擊下方按鈕選擇檔案',
      supportedFormats: '支援格式: JPG, PNG, GIF, WebP（最大 10MB）',
      selectFile: '選擇檔案',
      removeFile: '移除',
      uploading: '上傳中...',
      uploadButton: '上傳',
      uploadNow: '上傳',
      imageUploadSuccess: '圖片上傳成功',

      // 圖片庫管理
      imageLibrary: '圖片庫管理',
      questionImages: '問題圖片',
      answerImages: '答案圖片',
      imageReferences: '引用此圖片的題目',
      noReferences: '無題目引用此圖片',
      renameImage: '重命名',
      newImageName: '新名稱',
      updateRelatedQuestions: '同時更新所有引用此圖片的題目',
      renameSuccess: '圖片重命名成功，已更新 {count} 筆題目',
      renameError: '重命名失敗',
      imageNameExists: '此名稱已存在',
      invalidImageName: '圖片名稱只能包含字母、數字、底線和連字號',
      selectedImage: '選中圖片',
      referenceCount: '{count} 筆引用',
      noImagesInLibrary: '圖片庫中沒有圖片',
      searchImages: '搜尋圖片...',
      loadingReferences: '載入引用資料中...',
      renaming: '重命名中...'
    },

    // 考卷生成
    examPaper: {
      title: '考卷生成',
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
      saveSettings: '儲存設定',
      settingsSaved: '已儲存',
      unsavedChanges: '有未儲存的變更',

      // 操作按鈕
      saveDraft: '儲存草稿',
      designExam: '設計考券',
      exportPDF: '匯出 PDF',
      exportExamPaper: '匯出試題卷',
      exportAnswerSheet: '匯出答案券',
      examSheet: '試題卷',
      answerSheet: '答案券',
      answerSheetForTeacher: '教師答案券',
      showAnswerImages: '顯示答案圖片',
      showExplanations: '顯示解釋說明',

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

  // 英文翻譯保留但不會被使用（語言已鎖定為中文）
  en: {
    // 保留英文翻譯作為備用，但系統已鎖定為中文
  }
}
