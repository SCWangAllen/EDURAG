# EduRAG 使用手冊（教師版）

<p class="meta">版本 2.0 ・ 2026-09-30 ・ 截圖取自線上系統實際畫面（紅框編號對應內文的 ①②③）</p>

EduRAG 是一套給老師用的 **AI 智慧出題系統**：老師上傳課程教材，系統依教材、題型與數量，透過 AI 自動生成題目，並一鍵組成可列印的考卷（含答案卷）。

> **介面語言**：系統介面預設為**英文**（右上角可切換 **EN / 中**，選擇會記在你的瀏覽器）。**題目與考卷內容一律為英文**，不受介面語言影響。本手冊以中文說明操作，截圖為英文介面。

---

## 目錄

1. [系統總覽與導覽](#1-系統總覽與導覽)
2. [科目與年級管理](#2-科目與年級管理)
3. [題型範本（Exam Prompts）](#3-題型範本exam-prompts)
4. [上傳教材（Upload Documents）](#4-上傳教材upload-documents)
5. [圖片題管理（Upload Images）](#5-圖片題管理upload-images)
6. [單一範本生成題目（Exam Generator）](#6-單一範本生成題目exam-generator)
7. [組卷（Exam Paper Generator）](#7-組卷exam-paper-generator)
8. [題庫（Exam Library）](#8-題庫exam-library)
9. [系統設定（生成模型）](#9-系統設定生成模型)
10. [常見問題](#10-常見問題)
11. [附錄：年級代碼與題型名稱對照](#11-附錄年級代碼與題型名稱對照)

---

## 1. 系統總覽與導覽

登入後即進入主畫面。左側是功能選單，右上角可切換介面語言、查看 API 連線狀態與開啟系統設定。

![系統總覽：① 左側選單 ② EN / 中 語言切換 ③ API 連線狀態 ④ 系統設定（齒輪）](images/01-overview.png)

| 編號 | 位置 | 說明 |
|---|---|---|
| ① | 左側選單 | 六個功能頁，順序即建議的工作流程（見下表） |
| ② | **EN / 中** | 切換介面語言，選擇記在瀏覽器裡 |
| ③ | **API Status** | 綠色 Online 表示後端正常；紅色時請先重新整理，仍異常再聯絡維護者 |
| ④ | **⚙ 齒輪** | 系統設定：選擇 AI 生成模型（見第 9 章） |

**左側選單各頁用途：**

| 選單 | 用途 |
|---|---|
| **Exam Paper Generator** | 組卷（主要功能）：從題庫挑題或 AI 生成，設計版面並匯出考卷／答案卷 |
| **Exam Library** | 題庫：檢視／編輯／刪除已存的題目 |
| **Exam Generator** | 用單一範本生成一批題目，存入題庫 |
| **Upload Images** | 圖片題管理：Excel 匯入、上傳圖檔、驗證、批次改標籤 |
| **Upload Documents** | 上傳課程教材（AI 出題的內容來源） |
| **Subjects & Exam Prompts** | 科目／年級管理與題型範本 |

> **通用操作**
>
> - 所有彈出視窗都可以按 **Esc** 或**點視窗外面**關閉；已勾選的內容不會因此消失。
> - 切換到別頁再回來，篩選條件、勾選與捲動位置都會保留。
> - 搜尋框輸入後按 **Enter** 即可搜尋。

---

## 2. 科目與年級管理

科目是教材、範本、題目共同的分類依據。進入 **Subjects & Exam Prompts**，按右上 **Subject Management** 開啟科目管理視窗。

![科目管理：① 新增科目 ② 科目卡片（每格一個科目） ③ 科目顏色 ④ 展開後顯示該科目的年級](images/06-subject-management.png)

- ① **+ Add Subject**：新增科目。填科目名稱、選年級；顏色可自選，留空則由系統自動配色。
- ② 每張卡片是一個科目，顯示年級數與範本數。點卡片左側的 **›** 展開，可看到該科目的年級清單，並可對單一年級 ✏️ 編輯或 🗑 刪除。
- ③ **科目顏色**：同一科目在教材清單、範本、題目標籤、下拉選單裡都用同一個顏色顯示，方便一眼分辨。點卡片上的 ✏️ 可改名稱與顏色。
- ④ 年級依**學制**分組顯示：**ESL**（K1、K2、A1、A2）、**Grade Level**（G1–G6）、**Junior Class**（Jr. G4–Jr. G9）。

**同名科目、不同年級**：同一個科目名稱可以建立在多個年級（例如 Health 同時有 G4 與 G5）。若新增時出現「科目 X 已經有年級 Y」的錯誤，表示這個組合已存在；如果你只是想讓某個**範本**也適用該年級，請改到範本編輯的 **Applicable Grades** 勾選，不需要動科目本身。

> **舊資料提醒**：早期以「Junior Grade 6」這類名稱建立的年級已統一改為代碼 **JR6**（介面顯示 Jr. G6）。

---

## 3. 題型範本（Exam Prompts）

「範本」決定 AI 出題的方式與風格。一個範本綁定一個科目、一種題型與適用年級。

### 3.1 依題型建立範本

![範本頁：① 依題型建立範本（7 種起始範本） ② 科目管理 ③ 建立空白範本 ④ 初始化預設範本](images/02-template-gallery.png)

- ① **Create a Template by Question Type**：七種題型各有一個**起始範本**，點 **Use This Starter →** 會自動帶入正確的出題指示，照著填就不會生成失敗。題型有：Multiple Choice（選擇）、Fill in the Blanks（填空）、Questions and Answers（問答）、True/False（是非）、Matching（配對）、Sequence（排序）、Identification（辨識）。
- ② **Subject Management**：開啟科目管理（第 2 章）。
- ③ **+ Create Template**：從空白建立範本。
- ④ **Initialize Default Templates**：一鍵補齊系統預設範本（已存在的不會重複建立）。

### 3.2 填寫範本

![建立範本：① 範本名稱 ② 科目 ③ 適用年級 ④ 題型 ⑤ 出題指示 ⑥ 儲存](images/05-template-modal.png)

- ① **Template Name**：範本名稱，建議含科目與題型，例如 `G4 Health – Fill in the Blanks`。
- ② **Subject**：科目（沒有想要的科目請先到 Subject Management 建立）。
- ③ **Applicable Grades**：選了科目後會自動列出該科目的年級，可多選。
- ④ **Question Type**：題型。決定系統如何解析與排版 AI 的輸出。
- ⑤ **Prompt Template**：用白話寫「要出什麼、難度、風格」即可，**輸出格式由系統自動處理，不用寫 JSON**。內容必須包含 `{context}`（生成時你選的教材會填入這裡），可用 **Insert {context}** / **Insert {count}** 按鈕快速插入。
- ⑥ **Save** 儲存。

> 題目語言跟著範本文字走：英文指示產出英文題目。

### 3.3 搜尋、篩選與排序

![範本清單篩選：① 搜尋名稱 ② 科目篩選 ③ 下拉選單附科目顏色 ④ 年級篩選 ⑤ 排序 ⑥ 每頁筆數](images/03-template-filters.png)

- ① **Search**：依範本名稱搜尋。
- ②③ **Filter by Subject**：下拉清單每個科目前有顏色點，與其他頁面一致。
- ④ **Filter by Grade**：依年級篩選。
- ⑤ **Sort By**：**Subject / Grade**（依科目、年級）、**Newest First**（最新建立在前）、**Custom order**（自訂順序，見下節）。
- ⑥ **Items per Page**：每頁顯示筆數。分頁按鈕在清單**上方**，不用捲到最底。

### 3.4 自訂順序（拖曳或箭頭）與複製範本

![自訂順序：① 排序切到 Custom order ② 拖曳提示 ③ 左側拖曳把手 ④ ▲▼ 上移／下移 ⑤ View / Edit / Copy / Delete](images/04-template-custom-order.png)

1. ① 把 **Sort By** 切到 **Custom order**。
2. 用 ③ 左側的 **⋮⋮ 把手拖曳**範本到想要的位置，或用 ④ **▲ / ▼** 一次移動一格。順序會立刻存到系統，所有人看到的都一樣。
3. ⑤ 每個範本可 **View**（檢視）、**Edit**（編輯）、**Copy**（複製一份，名稱自動加 `(Copy)`，適合改給另一個科目或年級）、**Delete**（刪除）。

---

## 4. 上傳教材（Upload Documents）

進入 **Upload Documents**。教材是 AI 出題的內容來源；每一列教材代表一個章節（或一頁）的文字。

### 4.1 頁面總覽與篩選

![教材頁：① 上傳 Excel ② 下載匯入範本 ③ 搜尋 ④ 科目 ⑤ 年級 ⑥ 依上傳檔案篩選 ⑦ 排序 ⑧ 分頁（清單上方）](images/07-documents.png)

- ① **Upload Excel** 批次上傳教材；② **Download Template** 先下載範本照格式填。Excel 必要欄位：**Words、Chapter、Subject、Imagesrelated**；選填：**Grade、Page**。
- ③ 關鍵字搜尋（按 Enter）。④ 科目、⑤ 年級篩選。
- ⑥ **Upload File**：依「上傳檔案」篩選。每次上傳會記錄成一個批次（顯示為 `日期 時間 檔名`，也會標在每筆教材卡片上），方便只看某一次上傳的內容。
- ⑦ **Sort By**：**Chapter Order**（依章節編號 1、2、2.1、3… 自然排序）或 **Newest Upload**（最新上傳在前）。
- ⑧ 分頁在清單上方。

**重新上傳會取代舊資料**：上傳的 Excel 若含有**同科目、同年級、同章節（同頁碼）**的既有教材，上傳前的預覽會標示 `Will replace existing document #ID`，確認後以新內容**取代**舊的一筆，不會產生重複；上傳完成的訊息會顯示「取代幾筆、新增幾筆」。

### 4.2 批次操作與複製到其他年級

勾選一或多筆教材後，右上方會出現批次按鈕：

![批次操作：① 動作列 ② 複製到年級 ③ 刪除所選 ④ 全選本頁](images/08-documents-batch.png)

- ④ **Select All** 全選本頁；② **Copy to Grades (n)** 複製到其他年級；③ **Delete Selected (n)** 刪除所選（會再次確認）。

![複製到年級：① 勾選目標年級（可多選） ② 已選教材數 ③ 執行複製](images/09-copy-to-grades.png)

**Copy to Grades** 會把選取的教材**連同已建立的向量索引**複製一份到目標年級，不需要重新上傳、重新處理。典型用途：G4 的 Health 教材也要給 G5 出題，勾選後複製到 G5 即可。若目標年級已有同章節的教材，該筆會略過不重複建立。

---

## 5. 圖片題管理（Upload Images）

圖片題是「題目或答案以圖片呈現」的題型（例如看圖填空）。進入左側 **Upload Images**。

### 5.1 頁面總覽與匯入紀錄

![圖片題頁：① 匯入紀錄 ② 統計 ③ 篩選 ④ 動作按鈕 ⑤ 檢視此批 ⑥ 刪除此批](images/17-image-questions.png)

- ④ 右上動作：**Image Library Management**（圖庫管理）、**Upload Image**（上傳圖檔）、**Add Image Question**（手動新增一題）、**Upload Excel**（批次匯入圖片題）。
- ① **Import History**：每一次 Excel 匯入的紀錄，欄位為檔名、匯入時間、題數、已驗證數、缺圖數。⑤ **View Batch** 只顯示該批次的題目；⑥ **Delete Batch** 把該批次匯入的題目**整批刪除**（會再次確認），適合匯錯檔時一次清掉。舊的匯入沒有記錄檔名，顯示 *No filename recorded*。
- ② 統計：總題數、已驗證、未驗證、科目數。
- ③ 篩選：關鍵字、科目、年級、驗證狀態、章節；下方可依 **建立日期／圖片名稱／科目／年級** 排序與升降冪。
- 上方黃色 **Images to Upload** 提示條列出尚未上傳的圖檔名稱，預設收起，點 **Show list** 展開；展開／收起的狀態會記住。

### 5.2 圖片檔名規則與驗證

- Excel 裡的圖片名稱與實際上傳的檔名會**自動正規化**後比對：去掉副檔名，空白與特殊符號一律換成 `_`。因此 `ch4 image01.jpg`、`ch4-image01.JPG`、`ch4_image01` 都視為同一張圖，大小寫、副檔名不影響。
- 圖檔上傳後，勾選題目按 **Verify Selected** 重新驗證；卡片右上會由 *Image Not Verified* 變成 *Image Verified*。
- 仍顯示未驗證的常見原因：（a）圖檔尚未上傳；（b）Excel 裡的圖片名稱與檔名不一致；（c）Excel 該列缺少必要欄位。可用 **Verification Status** 篩選未驗證的題目逐一處理。

### 5.3 批次管理

![批次工具列：① 已選數量 ② 批次驗證 ③ 批次改標籤 ④ 批次刪除](images/18-image-batch-toolbar.png)

勾選卡片後上方出現工具列：② **Verify Selected** 批次驗證圖片是否存在；③ **Re-tag** 批次改科目／年級／章節（留空的欄位不會更動）；④ **Delete** 批次刪除；**Clear** 清除選取。

> 選取會**跨頁保留**；點一張卡片後按住 **Shift** 再點另一張，可一次選取中間的整段。

---

## 6. 單一範本生成題目（Exam Generator）

想用某一個範本，針對指定教材一次生成一批題目並存入題庫，用 **Exam Generator**。

### 6.1 三步驟生成

![Exam Generator：① 選範本 ② 選教材（彈出視窗） ③ 題數 ④ 開始生成](images/10-generate.png)

1. ① **Step 1. Select Template**：可先用 **Filter by Subject** 縮小範圍，再點一張範本卡片。
2. ② **Step 2. Select Exam Scope** → 按 **Select Documents…** 開啟教材選擇視窗（下節）。
3. ③ **Number to Generate**：本次要生成的題數，**1–50 題**。超過 20 題時系統會分批向 AI 索取並提示批數，等待時間相應拉長。配對題（Matching）範本會多一個 **Pairs per Question**（每題配對組數，2–20，預設 10）。
4. ④ **Generate Questions** 開始生成。

### 6.2 教材選擇視窗

![選擇教材：① 篩選（科目／年級／上傳檔案／搜尋） ② 全選符合篩選的教材 ③ 勾選清單 ④ 分頁 ⑤ 完成](images/11-document-picker.png)

- ① 上方可依科目、年級、**上傳檔案**與關鍵字篩選，清單有分頁 ④，不再受限於少數幾筆。
- ② **Select All Filtered (n)**：一鍵勾選**所有符合目前篩選**的教材（含其他頁）。
- ③ 逐筆勾選；下方會顯示已選數量。
- ⑤ **Done** 關閉視窗。按 **Esc** 或點視窗外面也會關閉，**已勾選的教材不會消失**。

### 6.3 生成結果、格式檢查與暫存

![生成結果：① 格式檢查摘要 ② 有問題的題目會標示原因 ③ 清除暫存 ④ 儲存到題庫](images/12-generate-results.png)

- 生成後系統會逐題**檢查格式**（填空題必須有空格、選擇題答案必須是選項之一、配對題左右數量一致等）。不合格的題目會標上紅色徽章 ② 並在 ① 提示「n 題有格式問題，儲存時會略過」。生成當下若有題目不合格，系統會自動補生成，通常不需要手動處理。
- ④ **Save** 把合格的題目存入題庫；**Export** 匯出本次結果。
- **自動暫存**：選好的範本、教材、題數與生成結果會自動存在**這台電腦的瀏覽器**裡。關掉頁面再回來會顯示 *Restored your last draft (n question(s), time)* 並還原；已 Save 的題目不會被重複儲存。③ **Clear Draft** 可清除暫存。

> 暫存跟著瀏覽器走，不跟著帳號：換一台電腦、換瀏覽器或清除瀏覽資料後就沒有了。要保留請按 Save 存入題庫。

---

## 7. 組卷（Exam Paper Generator）

進入 **Exam Paper Generator**，依 Step 1 → Step 4 操作。

### Step 1：選擇生成模式

![Step 1：① 生成模式 ② Review Test 多科目模式](images/13-exam-step1.png)

- ① **Select from Question Bank**：從題庫挑題組卷；**AI Auto-Generate**：依 Step 2 的設定直接由 AI 生成新題（快速組卷）。
- ② **Review Test Mode (Multiple Subjects Combined)**：跨多科目的複習卷／週考卷，見 7.5。

### Step 2：題型配置

![Step 2：① 題型設定表 ② 啟用開關 ③ 題數 ④ 每題配分 ⑤ 順序 ▲▼（也可拖曳左側把手）](images/14-exam-step2.png)

- 每一列是一種題型：② **Enabled** 開關、③ **Question Count** 題數、④ **Points per Question** 每題配分；右側小計與下方總題數、總分即時更新，**不需另外按儲存**。
- ⑤ 用 **↑↓** 或拖曳列首的 **⋮⋮** 調整題型在考卷上的順序。
- 題型名稱：Multiple Choice（選擇）、Fill in the Blanks（填空）、True/False（是非）、Questions and Answers（問答）、Matching（配對）、Sequencing（排序）、Identification（辨識）、Diagram Question（圖片題）。

### Step 3：選題或生成

依 Step 1 的模式：

- **Select from Question Bank**：下方列出題庫題目，可依科目、年級、章節、題型篩選，勾選要放進考卷的題目；每個題型的「已選／目標」進度會顯示在 Step 2。
- **AI Auto-Generate**：每個題型有獨立分頁，先選出題教材（Document Range Selection），Template 選 **Auto-match** 由系統配對最適合的範本，再按 **Generate**；生成完的題目會自動存檔並顯示 ✓ Saved。

### 草稿與自動暫存

![草稿按鈕：① 手動儲存草稿 ② 清除草稿 ③ 進入考卷設計](images/15-exam-draft.png)

- 組卷過程中的所有設定與已勾選的題目會**自動暫存**在這台電腦的瀏覽器（每次修改後自動儲存），下次進入頁面自動還原，不必重頭再來。① **Save Draft** 是立即手動存一次。
- ② **Clear Draft** 清除草稿（會再次確認，勾選與版面設定都會重設）。
- ③ **Design Exam Paper** 進入 Step 4。

### Step 4：設計與匯出考卷

![考卷設計器：① 校名／考卷標題／範圍 ② 題型順序 ③ 匯出考卷 ④ 匯出答案卷](images/16-exam-designer.png)

- ① **Exam Design**：School Name（校名）、Exam Title（考卷標題）、Range / Subtitle（範圍或副標，例如 Unit 1–3）。
- ② **Question Type Order**：拖曳或用 ↑↓ 調整各題型區塊的順序；每個區塊的 ✏️ 可改該區的作答說明。
- 右側 **Live Preview** 即時預覽（所見即所得），與最終列印一致；**Preview Mode** 可切成全寬預覽。
- ③ **Export Exam Paper** 匯出考卷（學生作答用）；④ **Export Answer Sheet** 匯出答案卷（含正解）。

考卷成品範例：抬頭、家長簽名欄、姓名／班級／日期／年級欄位、依題型分區（A. Multiple Choice ____/10）並附作答說明與配分：

![考卷成品範例](images/10-exam-preview.png)

### 7.5 Review Test（多科目）模式

![Review Test：① 勾選 Review Test Mode ② 選年級 ③ 選多個科目 ④ 每科題數 ⑤ 顯示方式](images/22-review-test.png)

在 Step 1 勾選 ① **Review Test Mode**，接著 ② **Select Grade** 選年級、③ **Select Subjects** 勾選多個科目、④ **Question Count per Subject** 設定每科題數、⑤ **Display Mode** 選擇 **By Subject Sections**（先分科目再分題型）或 **Mixed by Question Type**（依題型混合）。其餘 Step 2–4 與一般模式相同，匯出的考卷標題會標示 Review Test。

---

## 8. 題庫（Exam Library）

所有已儲存的題目都在 **Exam Library**。

![題庫：① 篩選 ② 全選（批次刪除／匯出） ③ 每題的檢視／編輯／刪除](images/19-questions.png)

- ① **Search** 輸入後自動搜尋題目內容；可再依 **題型、科目、年級、難度** 篩選。每題標籤會顯示科目顏色與章節。
- ② **Select All** 勾選後可批次刪除或匯出。
- ③ 每題右側三個圖示：👁 檢視、✏️ 編輯、🗑 刪除。

![題目詳情：① 詳情視窗（題目、正解、解析、來源教材） ② 關閉（或按 Esc／點視窗外）](images/20-question-detail.png)

- 詳情視窗會顯示題目內容、正確答案、解析、題型、難度、科目、年級、章節與**來源教材原文**，方便核對。
- 編輯題目儲存時，系統會用與生成時相同的規則檢查格式（例如填空題必須有 `____` 空格、選擇題答案必須是其中一個選項）；不符會顯示錯誤訊息且不會存檔。

---

## 9. 系統設定（生成模型）

點右上角 **⚙ 齒輪**。

![設定：① 生成模型 ② 儲存](images/21-settings.png)

- ① **Generation Model**：AI 出題使用的模型。**此設定為全站共用**，儲存後所有人的生成都改用這個模型；不同模型的速度與費用不同，若無特殊需求請維持預設。**Manage recommended list** 可展開管理建議清單。
- ② **Save** 儲存。

---

## 10. 常見問題

**Q：生成一直「0 題」或失敗？**
最常見原因是**沒有選教材**。Exam Generator 請確認 Step 2 已勾選教材（Select Documents… 視窗下方會顯示已選數量）；Exam Paper Generator 的 AI 模式請在 Step 3 選教材。另請確認範本內含 `{context}`；用「依題型建立範本」做出的範本已內建正確格式。

**Q：題目出成中文，我要英文？**
題目語言跟著**範本（Prompt Template）的語言**走。用起始範本建立的英文範本會產出英文題目。

**Q：一次最多能生成幾題？**
Exam Generator 一次最多 **50 題**。超過 20 題系統會自動分批向 AI 索取，時間會比較久，畫面上會提示批數。

**Q：新增科目時說「已經有年級 X」？**
表示「該科目名稱 + 該年級」已經存在。若只是想讓某個範本也適用該年級，請到範本編輯的 **Applicable Grades** 勾選，不需要新增科目。

**Q：G4 的教材想給 G5 用，要重新上傳嗎？**
不用。到 Upload Documents 勾選教材 → **Copy to Grades** → 勾 G5 → Copy，內容與索引會一起複製過去。

**Q：重新上傳同一份 Excel 會變成兩份嗎？**
不會。同科目、同年級、同章節的教材會被新內容**取代**，上傳前的預覽會標示哪幾筆會被取代。

**Q：圖片題一直是 Image Not Verified？**
依序檢查：圖檔是否已上傳、Excel 裡的圖片名稱是否與檔名一致（不含副檔名，空白與符號視同 `_`）、Excel 該列是否缺欄位。修正後勾選題目按 **Verify Selected**。上方 **Images to Upload** 提示條展開後會列出缺哪些檔。

**Q：我的草稿／暫存不見了？**
暫存存在**你使用的那台電腦的瀏覽器**裡，換電腦、換瀏覽器或清除瀏覽資料就不會有。需要保留的題目請 **Save** 進題庫；考卷請匯出檔案。

**Q：彈出視窗怎麼關？**
按 **Esc** 或點視窗外面即可，已勾選的內容不會消失。

**Q：年級選單為什麼只有部分年級？**
選教材時的年級是依你**實際擁有的教材**動態顯示的；上傳了哪些年級的教材就會出現哪些年級。科目的年級請到 Subject Management 設定。

**Q：介面想切回中文？**
右上角按 **中**；你的選擇會記在瀏覽器，下次自動沿用。

---

## 11. 附錄：年級代碼與題型名稱對照

### 年級代碼

| 學制 | 代碼 | 介面顯示 |
|---|---|---|
| ESL | K1、K2、A1、A2 | K1、K2、A1、A2 |
| Grade Level | G1–G6 | G1–G6 |
| Junior Class | JR4–JR9 | Jr. G4–Jr. G9 |
| 不分年級 | ALL | Generic (all grades) |

### 題型名稱（新舊對照）

| 現在的名稱 | 舊名稱 | 說明 |
|---|---|---|
| Multiple Choice | Single Choice | 單選題 |
| Fill in the Blanks | Cloze | 填空題，題幹必須含空格 `____` |
| Questions and Answers | Short Answer | 問答／簡答題 |
| True/False | True/False | 是非題 |
| Matching | Matching | 配對題，可設定每題配對組數 |
| Sequence / Sequencing | Sequence | 排序題 |
| Identification | Enumeration | 辨識題 |
| Diagram Question | — | 圖片題（組卷時可納入） |

### 快捷操作

| 操作 | 效果 |
|---|---|
| **Esc** 或點視窗外面 | 關閉彈出視窗（不清除已勾選） |
| 搜尋框按 **Enter** | 執行搜尋 |
| 圖片題卡片 **Shift + 點擊** | 範圍選取 |
| 範本／題型列的 **⋮⋮** 拖曳 | 調整順序 |

---

<p class="meta">本手冊由 docs/user-guide/tools/capture_guide.py 自動截圖加框、build_guide.py 產生 HTML 與 PDF。截圖存於 docs/user-guide/images/（未納入版本控制）；HTML 與 PDF 已內嵌圖片，可直接分享。</p>
