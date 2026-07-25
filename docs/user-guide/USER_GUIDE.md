# EduRAG 使用手冊(教師版)

EduRAG 是一套給國小老師用的 **RAG 智慧出題系統**:老師上傳課程教材,系統依教材、題型與數量,透過 AI 自動生成題目,並一鍵組成可列印的考卷(含答案卷)。

> **介面語言**:系統介面預設為**英文**(右上角可切換 **EN / 中**,選擇會記在你的瀏覽器)。**題目與考卷內容一律為英文**,不受介面語言影響。
>
> 本手冊以中文說明操作;截圖為實際的英文介面畫面。

---

## 目錄

1. [系統總覽與導覽](#1-系統總覽與導覽)
2. [建立題型範本](#2-建立題型範本)
3. [上傳教材](#3-上傳教材)
4. [生成考卷(一般模式)](#4-生成考卷一般模式)
5. [生成考卷(Weekly Test 多科目模式)](#5-生成考卷weekly-test-多科目模式)
6. [匯出考卷與答案卷](#6-匯出考卷與答案卷)
7. [常見問題](#7-常見問題)

---

## 1. 系統總覽與導覽

登入後即進入主畫面。左側是功能選單,右上角可切換介面語言(**EN / 中**)與查看 API 連線狀態。

![系統總覽與側邊欄導覽](images/01-overview.png)

**左側選單各頁用途:**

| 選單 | 用途 |
|---|---|
| **Exam Paper Generator** | 生成考卷(主要功能) |
| **Upload Documents** | 上傳課程教材(出題的來源) |
| **Upload Images** | 上傳圖片(圖片題用) |
| **Exam Generator** | 單題快速生成 |
| **Exam Library** | 題庫管理(檢視/編輯/刪除既有題目) |
| **Exam Prompts & Subjects** | 題型範本與科目管理 |

> 右上角 **EN / 中** 按鈕可隨時切換介面語言;你(開發者)切成「中」後會被記住,老師端維持英文。

---

## 2. 建立題型範本

「範本」決定 AI 出題的方式與風格。進入 **Exam Prompts & Subjects**,最上方的 **Create a Template by Question Type**(依題型建立範本)提供 7 種題型的起始範本,照著填就不會生成失敗。

![題型範本庫](images/02-template-gallery.png)

**7 種題型**:Single Choice(單選)、Cloze(填空)、Short Answer(簡答)、True/False(是非)、Matching(配對)、Sequence(排序)、Enumeration(列舉)。

點任一題型的 **Use This Starter →**,系統會開啟建立視窗並**自動帶入該題型的正確起始內容**。你只要用白話寫「要出什麼、難度、風格」即可 —— **輸出的 JSON 格式由系統自動處理,你不用自己寫 JSON**。

![建立範本:自動帶入起始內容 + 輸出格式由系統處理](images/03-template-modal.png)

**填寫重點:**

- **Template Name**:範本名稱。
- **Subject**:科目(若沒有想要的科目,先到 *Subject Management* 建立)。
- **Applicable Grades**:適用年級 —— 選了科目後會自動列出該科目的年級。
- **Prompt Template**:出題指示。必須包含 `{context}`(生成時你選的教材會自動填入這裡);可用下方按鈕快速插入 `{context}` 與 `{count}`(題數)。

填好按 **Save** 儲存。

---

## 3. 上傳教材

進入 **Upload Documents**。這裡管理所有課程教材 —— 教材是 AI 出題的內容來源。

![上傳教材](images/04-documents.png)

- 右上 **Upload Excel** 批次上傳教材;**Download Template** 可下載匯入範本。
- 上方統計:教材總數、科目數、含圖片數、章節數。
- 可依 **Subject / Grade** 篩選、以關鍵字搜尋。

---

## 4. 生成考卷(一般模式)

進入 **Exam Paper Generator**,依 Step 1 → Step 4 操作。

### Step 1:選擇生成模式

- **Select from Question Bank**:從既有題庫挑題組卷。
- **AI Auto-Generate**:依你的設定用 AI 生成新題(快速組卷)。

![Step 1:選擇生成模式](images/05-step1-mode.png)

### Step 2:題型配置

設定每個題型的**啟用與否、題數、每題配分**;下方即時顯示啟用題型數、總題數、總分。也提供 Quick Setup(標準卷/簡易卷/綜合卷)一鍵套用。

![Step 2:題型配置](images/06-step2-config.png)

> 題數與配分**改了會即時反映到下一步**,不需另外按儲存。

### Step 3:選教材並生成

每個題型有獨立分頁。選擇要出題的教材(**Document Range Selection**),Template 選 **Auto-match**(系統自動配對最適合的範本),再按 **Generate**。

![Step 3:選教材並生成](images/07-step3-docrange.png)

> **年級篩選會依你實際擁有的教材動態顯示**(例如目前只有 G1–G3 的教材,就只列 G1–G3)。

按下 Generate 後,AI 會依教材生成題目並自動存檔(顯示 **✓ Saved**):

![Step 3:生成結果](images/08-generated-results.png)

### Step 4:設計考卷

生成後按 **Design Exam Paper** 進入 **Exam Designer**。左側可設定校名、考卷標題、拖曳調整題型順序;右側是**即時 WYSIWYG 預覽**(所見即所得),與最終列印一致。

![Step 4:設計考卷 + 即時預覽](images/09-exam-designer.png)

考卷成品長這樣 —— 抬頭、姓名/班級/日期/年級欄位、依題型分區(A. Multiple Choice…)、每題含選項:

![考卷成品預覽](images/10-exam-preview.png)

---

## 5. 生成考卷(Weekly Test 多科目模式)

若要出一份**跨多科目**的週考卷,在 Step 1 勾選 **Weekly Test Mode (Multiple Subjects Combined)**。

![Weekly Test 多科目模式](images/11-weekly-test.png)

- **Select Grade**:選年級。
- **Select Subjects**:選多個科目(例如 English + Health Education)。
- **Question Count per Subject**:設定每個科目的題數。
- **Display Mode**:
  - **By Subject Sections** —— 依科目分區(先分科目,再分題型)。
  - **Mixed by Question Type** —— 依題型混合。

其餘 Step 2–4 與一般模式相同,最後一樣可設計與匯出。考卷會依你選的顯示模式,把各科目組成分區。

---

## 6. 匯出考卷與答案卷

在 **Exam Designer**(Step 4)左下角:

- **Export Exam Paper** —— 匯出考卷(給學生作答)。
- **Export Answer Sheet** —— 匯出答案卷(含正解)。

匯出前可用右側即時預覽確認版面。

---

## 7. 常見問題

**Q：生成一直「0 題」或失敗?**
最常見原因是**沒有選教材**(Step 3 會提示 "Please select at least one document")。另外請確認範本內含 `{context}` 佔位符。用「題型範本庫」建立的範本已內建正確格式,照著填即可。

**Q:題目出成中文,我要英文?**
題目語言跟著**範本(prompt)的語言**走。用題型範本庫建立的英文起始範本會產出英文題目;若範本用中文寫,就會出中文題。

**Q:改了題數,但下一步沒變?**
題數/配分改了會即時同步到 Step 3,不需按儲存。若沒反映,重新整理頁面即可。

**Q:年級選單為什麼只有部分年級?**
年級是依你**實際擁有的教材/科目**動態顯示的,不是固定 G1–G6。上傳了哪些年級的教材,就會出現哪些年級。

**Q:介面想切回中文?**
右上角按 **中**;你的選擇會記在瀏覽器,下次自動沿用。

---

> **附註**:本手冊的截圖存放於 `docs/user-guide/images/`,該資料夾**未納入版本控制**(gitignore)。從版控 clone 專案的人不會取得這些圖片,需自行依本手冊重新截圖,或向維護者索取。
