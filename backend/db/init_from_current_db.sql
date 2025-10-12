-- EduRAG Database Schema - Generated from Current Production Database
-- Version: 3.0
-- Generated: 2025-09-28
-- Description: 基於實際運行中的資料庫結構生成的初始化腳本

-- ============================================
-- 1. 資料庫準備
-- ============================================
-- 建立資料庫（如果需要）
-- CREATE DATABASE edurag;

-- 連接到資料庫
-- \c edurag;

-- ============================================
-- 2. 擴充套件設定
-- ============================================
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 3. 清除舊資料（選擇性 - 注意這會刪除所有資料！）
-- ============================================
-- DROP TABLE IF EXISTS generated_questions CASCADE;
-- DROP TABLE IF EXISTS document_chunks CASCADE;
-- DROP TABLE IF EXISTS questions CASCADE;
-- DROP TABLE IF EXISTS embeddings CASCADE;
-- DROP TABLE IF EXISTS templates CASCADE;
-- DROP TABLE IF EXISTS documents CASCADE;
-- DROP TABLE IF EXISTS subjects CASCADE;

-- ============================================
-- 4. 科目表 (subjects)
-- ============================================
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#3B82F6',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 建立索引
CREATE INDEX IF NOT EXISTS ix_subjects_id ON subjects(id);
CREATE INDEX IF NOT EXISTS ix_subjects_name ON subjects(name);

-- ============================================
-- 5. 文件表 (documents)
-- ============================================
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    subject VARCHAR(50),
    chapter VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    image_filename VARCHAR(255),
    page_number VARCHAR(20),
    image_data TEXT,  -- base64 encoded image
    image_urls TEXT[],
    import_source VARCHAR(100) DEFAULT 'manual'
);

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_documents_subject ON documents(subject);

-- ============================================
-- 6. 模板表 (templates)
-- ============================================
CREATE TABLE IF NOT EXISTS templates (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    params JSONB DEFAULT '{}',
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    question_type VARCHAR(32) DEFAULT 'single_choice'
);

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_templates_subject ON templates(subject);
CREATE INDEX IF NOT EXISTS idx_templates_active ON templates(is_active);
CREATE INDEX IF NOT EXISTS ix_templates_subject_id ON templates(subject_id);

-- ============================================
-- 7. 向量嵌入表 (embeddings)
-- ============================================
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    slice_text TEXT NOT NULL,
    vector VECTOR(1536),  -- OpenAI ada-002 embedding size
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 建立索引
CREATE INDEX IF NOT EXISTS ix_embeddings_id ON embeddings(id);

-- ============================================
-- 8. 題目表 (questions)
-- ============================================
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    template_id INTEGER REFERENCES templates(id) ON DELETE SET NULL,
    question_type VARCHAR(32) NOT NULL,
    stem TEXT NOT NULL,
    options TEXT[],
    answer TEXT NOT NULL,
    explanation TEXT NOT NULL,
    source_metadata JSON,
    export_batch_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    question_data JSONB
);

-- 建立索引
CREATE INDEX IF NOT EXISTS ix_questions_id ON questions(id);
CREATE INDEX IF NOT EXISTS idx_questions_question_type ON questions(question_type);
CREATE INDEX IF NOT EXISTS idx_questions_question_data ON questions USING GIN(question_data);

-- ============================================
-- 9. 文件切片表 (document_chunks)
-- ============================================
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);

-- ============================================
-- 10. 生成的問題表 (generated_questions)
-- ============================================
CREATE TABLE IF NOT EXISTS generated_questions (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES templates(id) ON DELETE SET NULL,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    question_type VARCHAR(20) NOT NULL,
    prompt TEXT NOT NULL,
    options JSONB,
    answer TEXT NOT NULL,
    explanation TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_questions_template_id ON generated_questions(template_id);
CREATE INDEX IF NOT EXISTS idx_questions_document_id ON generated_questions(document_id);

-- ============================================
-- 11. 更新時間戳觸發器
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 為有 updated_at 欄位的表添加觸發器
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

-- ============================================
-- 12. 初始資料 - 科目
-- ============================================
INSERT INTO subjects (name, description, color) VALUES
    ('健康', '健康教育相關內容', '#10B981'),
    ('英文', '英語學習相關內容', '#3B82F6'),
    ('歷史', '歷史知識相關內容', '#F59E0B'),
    ('數學', '數學相關內容', '#EF4444'),
    ('自然', '自然科學相關內容', '#8B5CF6'),
    ('國文', '國語文相關內容', '#EC4899'),
    ('地理', '地理知識相關內容', '#06B6D4'),
    ('公民', '公民與社會相關內容', '#84CC16'),
    ('資訊', '資訊科技相關內容', '#6366F1'),
    ('藝術', '藝術與人文相關內容', '#F97316')
ON CONFLICT (name) DO UPDATE
    SET description = EXCLUDED.description,
        color = EXCLUDED.color;

-- ============================================
-- 13. 初始資料 - 模板範例
-- ============================================
-- 先取得科目 ID
DO $$
DECLARE
    health_id INTEGER;
    english_id INTEGER;
    history_id INTEGER;
    math_id INTEGER;
BEGIN
    SELECT id INTO health_id FROM subjects WHERE name = '健康';
    SELECT id INTO english_id FROM subjects WHERE name = '英文';
    SELECT id INTO history_id FROM subjects WHERE name = '歷史';
    SELECT id INTO math_id FROM subjects WHERE name = '數學';

    -- 插入模板
    INSERT INTO templates (subject, subject_id, name, content, question_type, params) VALUES

    -- 健康科模板
    ('健康', health_id, '健康單選題模板',
'請根據以下健康教育文章內容，生成一道單選題。

文章內容：
{context}

要求：
1. 題目要與健康知識直接相關
2. 四個選項要合理且有鑑別度
3. 解釋要詳細且具教育意義

請以 JSON 格式回答：
{"stem": "題幹", "options": ["A選項", "B選項", "C選項", "D選項"], "answer": "正確答案字母", "explanation": "詳細解釋"}',
    'single_choice',
    '{"temperature": 0.7, "max_tokens": 500, "top_p": 0.95}'::JSONB),

    -- 英文科模板
    ('英文', english_id, '英文閱讀理解模板',
'Based on the following passage, generate a reading comprehension question.

Passage:
{context}

Requirements:
1. Focus on comprehension and vocabulary
2. Provide 4 reasonable options
3. Include detailed explanation

Please respond in JSON format:
{"stem": "Question", "options": ["Option A", "Option B", "Option C", "Option D"], "answer": "Correct letter", "explanation": "Detailed explanation"}',
    'single_choice',
    '{"temperature": 0.7, "max_tokens": 500, "top_p": 0.95}'::JSONB),

    -- 歷史科模板
    ('歷史', history_id, '歷史單選題模板',
'請根據以下歷史文章內容，生成一道單選題。

文章內容：
{context}

要求：
1. 題目要涉及重要歷史事件、人物或概念
2. 選項要有歷史依據
3. 解釋要包含歷史背景

請以 JSON 格式回答：
{"stem": "題幹", "options": ["A選項", "B選項", "C選項", "D選項"], "answer": "正確答案字母", "explanation": "詳細解釋"}',
    'single_choice',
    '{"temperature": 0.7, "max_tokens": 500, "top_p": 0.95}'::JSONB),

    -- 數學科模板
    ('數學', math_id, '數學應用題模板',
'請根據以下數學概念，生成一道應用題。

概念內容：
{context}

要求：
1. 題目要涉及實際應用場景
2. 需要運用所學概念解決
3. 提供詳細的解題過程

請以 JSON 格式回答：
{"stem": "題目描述", "options": ["A選項", "B選項", "C選項", "D選項"], "answer": "正確答案字母", "explanation": "詳細解題過程"}',
    'single_choice',
    '{"temperature": 0.6, "max_tokens": 600, "top_p": 0.9}'::JSONB)

    ON CONFLICT DO NOTHING;
END $$;

-- ============================================
-- 14. 初始資料 - 範例文件
-- ============================================
INSERT INTO documents (title, content, subject, chapter, import_source) VALUES
('均衡飲食的重要性',
'均衡飲食是維持身體健康的基礎。人體需要六大類營養素：蛋白質、碳水化合物、脂肪、維生素、礦物質和水。每種營養素都有其特定功能，缺乏任何一種都可能導致健康問題。

蛋白質是身體組織的主要成分，幫助生長和修復。優質蛋白質來源包括瘦肉、魚類、蛋類、豆類和乳製品。碳水化合物提供能量，應選擇全穀類如糙米、燕麥等。脂肪雖然熱量高，但也是必需的，特別是不飽和脂肪酸。

維生素和礦物質雖然需求量少，但對身體機能極為重要。維生素C增強免疫力，維生素D幫助鈣質吸收，鐵質預防貧血。建議每天攝取五份蔬果，確保獲得足夠的微量營養素。

水分佔人體60-70%，參與所有生理活動。建議每天飲用8杯水，運動時要額外補充。避免過多含糖飲料，以免攝取過多熱量。',
'健康', '第一章：營養與健康', 'manual'),

('English Grammar Basics',
'English grammar forms the foundation of effective communication. Understanding the basic components helps construct clear and meaningful sentences.

The eight parts of speech are: nouns, pronouns, verbs, adjectives, adverbs, prepositions, conjunctions, and interjections. Nouns name people, places, things, or ideas. Verbs express actions or states of being. Adjectives modify nouns, while adverbs modify verbs, adjectives, or other adverbs.

Sentence structure typically follows the Subject-Verb-Object (SVO) pattern. For example: "The cat (S) caught (V) the mouse (O)." However, English allows for various sentence types: simple, compound, complex, and compound-complex.

Tense indicates when an action occurs. The three main tenses are past, present, and future, each with four aspects: simple, continuous, perfect, and perfect continuous. Mastering tenses enables precise time expression.

Common grammar mistakes include subject-verb disagreement, incorrect pronoun usage, and misplaced modifiers. Regular practice and reading help internalize correct grammar patterns.',
'英文', 'Chapter 1: Grammar Foundation', 'manual'),

('臺灣的歷史發展',
'臺灣的歷史可追溯至數千年前的史前時代。原住民族是最早的居民，發展出獨特的文化體系。16世紀開始，荷蘭和西班牙相繼在臺灣建立據點，開啟了臺灣的大航海時代。

1661年，鄭成功驅逐荷蘭人，建立明鄭政權。這是漢人大規模移民臺灣的開始，帶來了農業技術和文化傳統。1683年，清朝納入版圖，臺灣成為福建省的一部分，後來升格為臺灣省。

日治時期(1895-1945)是臺灣現代化的重要階段。日本引進現代教育、醫療衛生、交通建設等。雖然是殖民統治，但客觀上促進了臺灣的現代化進程。

1945年後，臺灣進入中華民國時期。經歷了戒嚴、經濟起飛、民主化等重要階段。1960-1990年代的經濟奇蹟，使臺灣成為亞洲四小龍之一。1987年解嚴後，臺灣逐步實現民主化，成為華人世界的民主典範。',
'歷史', '第三章：臺灣史', 'manual'),

('基礎代數概念',
'代數是數學的重要分支，使用字母和符號來表示數字和數量關係。變數是代數的核心概念，通常用x、y、z等字母表示未知數或可變的量。

一元一次方程式是最基本的代數方程，形式為ax + b = c。解方程的目標是找出使等式成立的變數值。基本步驟包括：移項、合併同類項、係數化為1。例如：3x + 5 = 20，解得x = 5。

代數表達式可以進行運算。加法和減法要合併同類項，如3x + 2x = 5x。乘法運用分配律，如2(x + 3) = 2x + 6。因式分解是乘法的逆運算，將多項式寫成因式的乘積。

函數描述變數之間的對應關係。線性函數y = mx + b的圖形是直線，m是斜率，b是y截距。二次函數y = ax² + bx + c的圖形是拋物線，在物理和工程中應用廣泛。

代數不僅是抽象的數學理論，更是解決實際問題的工具。從計算購物折扣到分析科學數據，代數無處不在。',
'數學', '第二章：代數基礎', 'manual')

ON CONFLICT DO NOTHING;

-- ============================================
-- 15. 資料庫健康檢查函數
-- ============================================
CREATE OR REPLACE FUNCTION check_database_health()
RETURNS TABLE(
    table_name TEXT,
    row_count BIGINT,
    status TEXT,
    comment TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'subjects'::TEXT,
           COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'EMPTY' END::TEXT,
           CASE WHEN COUNT(*) > 0 THEN COUNT(*) || ' subjects' ELSE 'No subjects found' END::TEXT
    FROM subjects

    UNION ALL
    SELECT 'templates'::TEXT,
           COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'EMPTY' END::TEXT,
           CASE WHEN COUNT(*) > 0 THEN COUNT(*) || ' templates' ELSE 'No templates found' END::TEXT
    FROM templates

    UNION ALL
    SELECT 'documents'::TEXT,
           COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'EMPTY' END::TEXT,
           CASE WHEN COUNT(*) > 0 THEN COUNT(*) || ' documents' ELSE 'No documents found' END::TEXT
    FROM documents

    UNION ALL
    SELECT 'questions'::TEXT,
           COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) >= 0 THEN 'OK' ELSE 'ERROR' END::TEXT,
           COUNT(*) || ' questions'::TEXT
    FROM questions

    UNION ALL
    SELECT 'embeddings'::TEXT,
           COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) >= 0 THEN 'OK' ELSE 'ERROR' END::TEXT,
           COUNT(*) || ' embeddings'::TEXT
    FROM embeddings

    UNION ALL
    SELECT 'document_chunks'::TEXT,
           COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) >= 0 THEN 'OK' ELSE 'ERROR' END::TEXT,
           COUNT(*) || ' chunks'::TEXT
    FROM document_chunks

    UNION ALL
    SELECT 'generated_questions'::TEXT,
           COUNT(*)::BIGINT,
           CASE WHEN COUNT(*) >= 0 THEN 'OK' ELSE 'ERROR' END::TEXT,
           COUNT(*) || ' generated questions'::TEXT
    FROM generated_questions;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 16. 版本資訊表
-- ============================================
CREATE TABLE IF NOT EXISTS schema_version (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (version, description) VALUES
('3.0.0', '基於實際生產資料庫結構的完整初始化腳本')
ON CONFLICT (version) DO UPDATE
    SET description = EXCLUDED.description,
        applied_at = CURRENT_TIMESTAMP;

-- ============================================
-- 17. 權限設定（根據需要調整用戶名）
-- ============================================
-- 如果有特定的應用程式用戶，授予適當權限
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO edurag_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO edurag_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO edurag_user;

-- ============================================
-- 18. 執行健康檢查
-- ============================================
SELECT * FROM check_database_health();

-- ============================================
-- 完成訊息
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'EduRAG 資料庫初始化完成！';
    RAISE NOTICE '版本: 3.0.0';
    RAISE NOTICE '========================================';
    RAISE NOTICE '已建立的表格:';
    RAISE NOTICE '  - subjects (科目)';
    RAISE NOTICE '  - documents (文件)';
    RAISE NOTICE '  - templates (模板)';
    RAISE NOTICE '  - embeddings (向量嵌入)';
    RAISE NOTICE '  - questions (題目)';
    RAISE NOTICE '  - document_chunks (文件切片)';
    RAISE NOTICE '  - generated_questions (生成的問題)';
    RAISE NOTICE '========================================';
END $$;