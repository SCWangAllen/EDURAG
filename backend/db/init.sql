-- EduRAG Complete Database Schema
-- Version: 2.1.0
-- Description: 完整的資料庫初始化腳本，與 models.py 完全同步
-- Updated: 2025-01 - 新增 grade 欄位和 questions.updated_at

-- ============================================
-- 1. 擴充套件設定
-- ============================================
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 2. 科目表 (subjects)
-- ============================================
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#3B82F6',
    grade VARCHAR(10),  -- 年級 (G1-G6, ALL)
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_subjects_name ON subjects(name);
CREATE INDEX IF NOT EXISTS idx_subjects_grade ON subjects(grade);

-- ============================================
-- 3. 文件表 (documents)
-- ============================================
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(32) NOT NULL,
    title VARCHAR(200),
    content TEXT NOT NULL,
    image_urls TEXT[],
    image_filename VARCHAR(255),
    chapter VARCHAR(100),
    page_number VARCHAR(20),
    image_data TEXT,  -- base64 儲存
    import_source VARCHAR(100) DEFAULT 'manual',
    grade VARCHAR(10),  -- 年級 (G1-G6, ALL)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_documents_subject ON documents(subject);
CREATE INDEX IF NOT EXISTS idx_documents_grade ON documents(grade);

-- ============================================
-- 4. 模板表 (templates)
-- ============================================
CREATE TABLE IF NOT EXISTS templates (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(50),  -- 保留舊欄位以兼容
    subject_id INTEGER REFERENCES subjects(id),  -- 新的外鍵關聯
    name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,  -- prompt template
    question_type VARCHAR(32) DEFAULT 'single_choice',
    params JSONB DEFAULT '{}',
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_templates_subject ON templates(subject);
CREATE INDEX IF NOT EXISTS idx_templates_subject_id ON templates(subject_id);
CREATE INDEX IF NOT EXISTS idx_templates_active ON templates(is_active);

-- ============================================
-- 5. 向量嵌入表 (embeddings)
-- ============================================
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    slice_text TEXT NOT NULL,
    vector VECTOR(1536),  -- OpenAI ada-002 embedding size
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_embeddings_document_id ON embeddings(document_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING ivfflat (vector vector_cosine_ops);

-- ============================================
-- 6. 題目表 (questions)
-- ============================================
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    question_type VARCHAR(32) NOT NULL,
    stem TEXT NOT NULL,  -- 題目內容
    options TEXT[],  -- 選擇題選項
    answer TEXT NOT NULL,  -- 正確答案
    explanation TEXT NOT NULL,  -- 解釋
    question_data JSONB,  -- 配對項、排序項等題型專用資料
    document_id INTEGER REFERENCES documents(id),  -- 來源文件ID
    template_id INTEGER REFERENCES templates(id),  -- 使用的模板
    source_metadata JSONB,  -- 來源元數據
    export_batch_id VARCHAR(50),  -- 匯出批次ID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP  -- 新增 updated_at
);

CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(question_type);
CREATE INDEX IF NOT EXISTS idx_questions_document_id ON questions(document_id);
CREATE INDEX IF NOT EXISTS idx_questions_template_id ON questions(template_id);
CREATE INDEX IF NOT EXISTS idx_questions_batch_id ON questions(export_batch_id);
CREATE INDEX IF NOT EXISTS idx_questions_data ON questions USING GIN(question_data);
CREATE INDEX IF NOT EXISTS idx_questions_metadata ON questions USING GIN(source_metadata);

-- ============================================
-- 7. 相容性支援（舊表結構）
-- ============================================
-- 如果有舊表 document_chunks，建立視圖對應到 embeddings
DROP VIEW IF EXISTS document_chunks CASCADE;
CREATE VIEW document_chunks AS
SELECT
    id,
    document_id,
    slice_text AS chunk_text,
    ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY id) - 1 AS chunk_index,
    vector AS embedding,
    '{}' ::JSONB AS metadata,
    created_at
FROM embeddings;

-- 如果有舊表 generated_questions，建立視圖對應到 questions
DROP VIEW IF EXISTS generated_questions CASCADE;
CREATE VIEW generated_questions AS
SELECT
    id,
    template_id,
    document_id,
    question_type,
    stem AS prompt,
    options,
    answer,
    explanation,
    source_metadata AS metadata,
    created_at
FROM questions;

-- ============================================
-- 8. 初始資料 - 科目
-- ============================================
INSERT INTO subjects (name, description, color, grade) VALUES
    ('健康', '健康教育相關內容', '#10B981', 'ALL'),
    ('英文', '英語學習相關內容', '#3B82F6', 'ALL'),
    ('歷史', '歷史知識相關內容', '#F59E0B', 'ALL'),
    ('數學', '數學相關內容', '#EF4444', 'ALL'),
    ('自然', '自然科學相關內容', '#8B5CF6', 'ALL'),
    ('國文', '國語文相關內容', '#EC4899', 'ALL')
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- 9. 初始資料 - 模板
-- ============================================
-- 先取得科目 ID
DO $$
DECLARE
    health_id INTEGER;
    english_id INTEGER;
    history_id INTEGER;
BEGIN
    SELECT id INTO health_id FROM subjects WHERE name = '健康';
    SELECT id INTO english_id FROM subjects WHERE name = '英文';
    SELECT id INTO history_id FROM subjects WHERE name = '歷史';

    -- 插入模板，同時設定 subject 和 subject_id
    INSERT INTO templates (subject, subject_id, name, content, question_type, params) VALUES
    ('健康', health_id, '健康單選題預設模板',
'請根據以下健康教育文章內容，生成一道單選題。

文章內容：
{context}

請生成一道關於健康知識的單選題，包含：
1. 題幹：清楚的問題描述
2. 四個選項：A、B、C、D
3. 正確答案：明確指出正確選項
4. 解釋：說明為何此選項正確

格式要求：
- 題幹要具體明確，與健康知識相關
- 選項要合理且有辨識度
- 解釋要簡潔清楚，有助於學習

請以 JSON 格式回答：
{"stem": "題幹", "options": ["A選項", "B選項", "C選項", "D選項"], "answer": "正確選項字母", "explanation": "解釋"}',
    'single_choice',
    '{"temperature": 0.7, "max_tokens": 500}'::JSONB),

    ('英文', english_id, '英文單選題預設模板',
'Based on the following English passage, create a multiple-choice question.

Passage:
{context}

Please generate a multiple-choice question about this English passage, including:
1. Question stem: Clear question description
2. Four options: A, B, C, D
3. Correct answer: Clearly indicate the correct option
4. Explanation: Explain why this option is correct

Requirements:
- The question stem should be specific and clear, related to English learning
- Options should be reasonable and distinguishable
- Explanation should be concise and clear for educational purposes

Please respond in JSON format:
{"stem": "Question stem", "options": ["Option A", "Option B", "Option C", "Option D"], "answer": "Correct option letter", "explanation": "Explanation"}',
    'single_choice',
    '{"temperature": 0.7, "max_tokens": 500}'::JSONB),

    ('歷史', history_id, '歷史單選題預設模板',
'請根據以下歷史文章內容，生成一道單選題。

文章內容：
{context}

請生成一道關於歷史知識的單選題，包含：
1. 題幹：清楚的問題描述
2. 四個選項：A、B、C、D
3. 正確答案：明確指出正確選項
4. 解釋：說明為何此選項正確

格式要求：
- 題幹要具體明確，與歷史事件或人物相關
- 選項要合理且有辨識度
- 解釋要簡潔清楚，提供歷史背景

請以 JSON 格式回答：
{"stem": "題幹", "options": ["A選項", "B選項", "C選項", "D選項"], "answer": "正確選項字母", "explanation": "解釋"}',
    'single_choice',
    '{"temperature": 0.7, "max_tokens": 500}'::JSONB)

    ON CONFLICT DO NOTHING;
END $$;

-- ============================================
-- 10. 初始資料 - 範例文件
-- ============================================
INSERT INTO documents (title, content, subject, chapter, grade) VALUES
('健康飲食指南',
'均衡飲食是維持身體健康的重要關鍵。每日應攝取適量的蛋白質、碳水化合物、脂肪、維生素和礦物質。建議多吃蔬菜水果，選擇全穀類食物，適量攝取優質蛋白質如豆類、魚類和瘦肉。同時要限制糖分和鹽分的攝取，多喝水保持身體水分平衡。',
'健康', '營養教育', 'ALL'),

('Basic English Grammar',
'English grammar consists of several fundamental components. The sentence structure typically follows the Subject-Verb-Object pattern. Nouns represent people, places, things, or ideas. Verbs express actions or states of being. Adjectives describe nouns, while adverbs modify verbs, adjectives, or other adverbs. Understanding these basic elements helps in constructing clear and meaningful sentences.',
'英文', 'Grammar Basics', 'ALL'),

('中國古代歷史',
'中國古代歷史源遠流長，從夏朝開始經歷了商、周、秦、漢等多個朝代。秦始皇統一中國後建立了郡縣制，統一了文字、貨幣和度量衡。漢朝建立後開創了絲綢之路，促進了東西方文化交流。這些歷史事件對中華文明的發展產生了深遠影響。',
'歷史', '中國古代史', 'ALL')

ON CONFLICT DO NOTHING;

-- ============================================
-- 11. 設定 Trigger 自動更新 updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 為需要的表添加 trigger
DROP TRIGGER IF EXISTS update_subjects_updated_at ON subjects;
CREATE TRIGGER update_subjects_updated_at
    BEFORE UPDATE ON subjects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_templates_updated_at ON templates;
CREATE TRIGGER update_templates_updated_at
    BEFORE UPDATE ON templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_questions_updated_at ON questions;
CREATE TRIGGER update_questions_updated_at
    BEFORE UPDATE ON questions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 12. 權限設定
-- ============================================
-- 確保應用程式用戶有適當權限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO edurag_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO edurag_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO edurag_user;

-- ============================================
-- 13. 資料庫健康檢查
-- ============================================
-- 建立健康檢查函數
CREATE OR REPLACE FUNCTION check_database_health()
RETURNS TABLE(
    table_name TEXT,
    row_count BIGINT,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'subjects'::TEXT, COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'EMPTY' END::TEXT
    FROM subjects
    UNION ALL
    SELECT 'templates'::TEXT, COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'EMPTY' END::TEXT
    FROM templates
    UNION ALL
    SELECT 'documents'::TEXT, COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'EMPTY' END::TEXT
    FROM documents
    UNION ALL
    SELECT 'questions'::TEXT, COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) >= 0 THEN 'OK' ELSE 'ERROR' END::TEXT
    FROM questions
    UNION ALL
    SELECT 'embeddings'::TEXT, COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) >= 0 THEN 'OK' ELSE 'ERROR' END::TEXT
    FROM embeddings;
END;
$$ LANGUAGE plpgsql;

-- 執行健康檢查
SELECT * FROM check_database_health();

-- ============================================
-- 14. 版本資訊
-- ============================================
CREATE TABLE IF NOT EXISTS schema_version (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (version, description) VALUES
('2.1.0', '完整資料庫結構 - 新增 grade 欄位和 questions.updated_at')
ON CONFLICT (version) DO UPDATE SET
    description = EXCLUDED.description,
    applied_at = CURRENT_TIMESTAMP;

-- 顯示安裝完成訊息
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'EduRAG 資料庫初始化完成！';
    RAISE NOTICE '========================================';
    RAISE NOTICE '版本: 2.1.0';
    RAISE NOTICE '已建立表: subjects, documents, templates, embeddings, questions';
    RAISE NOTICE '已插入初始資料:';
    RAISE NOTICE '  - % 個科目', (SELECT COUNT(*) FROM subjects);
    RAISE NOTICE '  - % 個模板', (SELECT COUNT(*) FROM templates);
    RAISE NOTICE '  - % 個範例文件', (SELECT COUNT(*) FROM documents);
    RAISE NOTICE '========================================';
    RAISE NOTICE '健康檢查結果：';
END $$;

-- 顯示健康檢查結果
SELECT
    table_name AS "表名稱",
    row_count AS "資料筆數",
    status AS "狀態"
FROM check_database_health();
