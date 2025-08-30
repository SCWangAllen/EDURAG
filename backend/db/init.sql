-- EduRAG Database Initialization Script
-- Create necessary extensions and tables

-- Enable pgvector extension for vector storage
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Templates table
CREATE TABLE IF NOT EXISTS templates (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    params JSONB DEFAULT '{}',
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    subject VARCHAR(50),
    chapter VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Document chunks table for vector storage
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding VECTOR(1536), -- OpenAI ada-002 embedding size
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Generated questions table (for history/cache)
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_templates_subject ON templates(subject);
CREATE INDEX IF NOT EXISTS idx_templates_active ON templates(is_active);
CREATE INDEX IF NOT EXISTS idx_documents_subject ON documents(subject);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_questions_template_id ON generated_questions(template_id);
CREATE INDEX IF NOT EXISTS idx_questions_document_id ON generated_questions(document_id);

-- Insert default templates
INSERT INTO templates (subject, name, content, params) VALUES 
('健康', '健康單選題預設模板', '請根據以下健康教育文章內容，生成一道單選題。

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
{"stem": "題幹", "options": ["A選項", "B選項", "C選項", "D選項"], "answer": "正確選項字母", "explanation": "解釋"}', '{"temperature": 0.7, "max_tokens": 500}'),

('英文', '英文單選題預設模板', 'Based on the following English passage, create a multiple-choice question.

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
{"stem": "Question stem", "options": ["Option A", "Option B", "Option C", "Option D"], "answer": "Correct option letter", "explanation": "Explanation"}', '{"temperature": 0.7, "max_tokens": 500}'),

('歷史', '歷史單選題預設模板', '請根據以下歷史文章內容，生成一道單選題。

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
{"stem": "題幹", "options": ["A選項", "B選項", "C選項", "D選項"], "answer": "正確選項字母", "explanation": "解釋"}', '{"temperature": 0.7, "max_tokens": 500}')

ON CONFLICT DO NOTHING;

-- Insert sample documents for testing
INSERT INTO documents (title, content, subject, chapter) VALUES 
('健康飲食指南', '均衡飲食是維持身體健康的重要關鍵。每日應攝取適量的蛋白質、碳水化合物、脂肪、維生素和礦物質。建議多吃蔬菜水果，選擇全穀類食物，適量攝取優質蛋白質如豆類、魚類和瘦肉。同時要限制糖分和鹽分的攝取，多喝水保持身體水分平衡。', '健康', '營養教育'),

('Basic English Grammar', 'English grammar consists of several fundamental components. The sentence structure typically follows the Subject-Verb-Object pattern. Nouns represent people, places, things, or ideas. Verbs express actions or states of being. Adjectives describe nouns, while adverbs modify verbs, adjectives, or other adverbs. Understanding these basic elements helps in constructing clear and meaningful sentences.', '英文', 'Grammar Basics'),

('中國古代歷史', '中國古代歷史源遠流長，從夏朝開始經歷了商、周、秦、漢等多個朝代。秦始皇統一中國後建立了郡縣制，統一了文字、貨幣和度量衡。漢朝建立後開創了絲綢之路，促進了東西方文化交流。這些歷史事件對中華文明的發展產生了深遠影響。', '歷史', '中國古代史')

ON CONFLICT DO NOTHING;