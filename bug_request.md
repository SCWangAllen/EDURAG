亞伯

Dashboard頁面調整 
左邊欄位不管中英文都同時顯示中英 並 改成以下排序 
1-Dashboard 總覽 
2-Upload Documents 文件上傳 
3-Exam Generator 考題生成 
4-Exam Library 考題管理 
5-Exam Prompt Templates 題型模板 
6-Exam Paper Generator 考卷生成 

並且Dashboard的內容也要調整

Document 頁面改成 Upload  Document
- 文件新增欄位為 
* Grade 
* Subject 
* Chapter 
* Page 
* Contents 
* Image 
- 若有圖片新增圖片預覽
* 根據已調整的欄位 逐一顯示 標題 要改成章節 
* Grade 年級 
* Subject 科目 
* Chapter 章節 
* Page 頁數 
* Contents 內容 
* Image 圖片 
- Documents.deleteSelected(要新增對應字,i18n)
-  全選刪除後會出現 batchDeleteResult is not defile -> fix it
- 搜尋bar要新增年級篩選

Generate頁面修改為Exam Generator
- 上面傳統生成模式直接改成題目生成
- 模版篩選增加年級
- 文件的選擇數量要和資料庫一致，或是做優化 要有辦法選到全部的文字 目前只有20個
- 生成題數與實際回傳數不一樣 要確認
- 頁數顯示要依照上傳文件填寫的page
- 選擇文件改成選擇考提範圍
- 若生成題目失敗要有通知
-  把下面批次生成的部份功能移到 ExamPaper Generatort頁面

Questions頁面改成 Exam Library
- 標題改考提管理
- 搜尋頁面新增篩選年級
- 考題詳細察看新增增加年級以及頁數資訊
- Question.save（要新增對應字,i18n)
- Question.updateSuccess（要新增對應字,i18n)

Templates 改成 Exam Prompt Templates 

- Template編輯的內容中，要把題型的選擇對應上去 目前無法正確顯示以及對應
- 科目管理新增年級欄位且為必填
- 模版管理文字改成題型模版管理

Exam Paper Generator (新頁面、專門為考卷生成而生)
- 功能可以把之前的模版批次生成考卷以及Question的考券生成功能拿來用
- 下面是預計的 Flow
* Exam Paper Generator（考卷生成，主入口） 
* │ 
* ├─ 🧭 Step 1：選擇生成方式 
* │      ├─ 📑 手動組卷（Manual Assembly） 
* │      └─ ⚡️ 快速出卷（Quick Generation） 
* │ 
* ├─ 📑 Manual Assembly（手動組卷模式） 
* │      │ 
* │      ├─ Step 2：設定篩選條件 
* │      │      ├─ 題型（單選 / 填空 / 問答…） 
* │      │      ├─ 難度（初階 / 中階 / 高階） 
* │      │      └─ 範圍（章節 / 主題） 
* │      │ 
* │      ├─ Step 3：題庫篩選 + 勾選題目 
* │      │      ├─ 顯示篩選後題目清單（只讀，無編輯） 
* │      │      ├─ 勾選題目前方 ☑️ 
* │      │      ├─ 側邊/底部顯示「已選題數」 
* │      │      └─ 固定浮動按鈕「生成考卷」 
* │      │ 
* │      └─ Step 4：生成考卷 → 進入「考卷預覽頁」 
* │             ├─ 可檢視題目、順序、配分 
* │             └─ 確認後 → 匯出 PDF / Word ✅ 
* │ 
* └─ ⚡️ Quick Generation（快速出卷模式） 
*        │ 
*        ├─ Step 2：輸入題型需求 
*        │      ├─ 單選：10 題（章節 1–3） 
*        │      ├─ 填空：5 題（章節 4） 
*        │      └─ 問答：2 題（章節 5） 
*        │ 
*        ├─ Step 3：一鍵生成考卷 
*        │ 
*        └─ Step 4：進入「考卷預覽頁」 
*               ├─ AI 自動生成的題目、分配 
*               └─ 確認後 → 匯出 PDF / Word ✅ 
- 

