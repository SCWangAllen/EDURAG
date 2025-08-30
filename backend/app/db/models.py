from sqlalchemy import Column, Integer, String, Text, ARRAY, TIMESTAMP, ForeignKey, JSON, Boolean
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func
from .database import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(32), nullable=False)
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    image_urls = Column(ARRAY(Text))
    # 新增欄位支援 Excel 匯入
    image_filename = Column(String(255), nullable=True)
    chapter = Column(String(100), nullable=True)
    page_number = Column(String(20), nullable=True)
    image_data = Column(Text, nullable=True)  # base64 儲存
    import_source = Column(String(100), default='manual')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)  # prompt template
    params = Column(JSON, nullable=True)    # 溫度、top_p 等參數
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class Embedding(Base):
    __tablename__ = "embeddings"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    slice_text = Column(Text, nullable=False)
    vector = Column(Vector(1536))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Question(Base):
    __tablename__ = "questions"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    # 使用與現有表結構匹配的欄位名稱
    question_type = Column("question_type", String(16), nullable=False)  # single_choice, cloze, short_answer
    stem = Column("stem", Text, nullable=False)  # 題目內容 (原本叫 content)
    options = Column(ARRAY(Text), nullable=True)  # 選擇題選項 (ARRAY 而不是 JSON)
    answer = Column("answer", Text, nullable=False)  # 正確答案 (原本叫 correct_answer)
    explanation = Column(Text, nullable=False)  # 解釋
    
    # 來源資訊
    document_id = Column("document_id", Integer, ForeignKey("documents.id"))  # 來源文件ID (原本叫 source_document_id)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)  # 使用的模板
    source_metadata = Column(JSON, nullable=True)  # 來源元數據 (包含章節、頁數等)
    
    # 匯出相關
    export_batch_id = Column(String(50), nullable=True)  # 匯出批次ID
    
    # 時間戳
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # 為了兼容性，我們提供屬性別名
    @property
    def type(self):
        return self.question_type
    
    @type.setter  
    def type(self, value):
        self.question_type = value
        
    @property
    def content(self):
        return self.stem
        
    @content.setter
    def content(self, value):
        self.stem = value
        
    @property
    def correct_answer(self):
        return self.answer
        
    @correct_answer.setter
    def correct_answer(self, value):
        self.answer = value
        
    @property
    def source_document_id(self):
        return self.document_id
        
    @source_document_id.setter
    def source_document_id(self, value):
        self.document_id = value
        
    @property
    def source_content(self):
        return self.source_metadata.get('source_content') if self.source_metadata else None
        
    @source_content.setter
    def source_content(self, value):
        if not self.source_metadata:
            self.source_metadata = {}
        self.source_metadata['source_content'] = value
        
    @property
    def subject(self):
        return self.source_metadata.get('subject') if self.source_metadata else None
        
    @subject.setter
    def subject(self, value):
        if not self.source_metadata:
            self.source_metadata = {}
        self.source_metadata['subject'] = value
        
    @property
    def chapter(self):
        return self.source_metadata.get('chapter') if self.source_metadata else None
        
    @chapter.setter
    def chapter(self, value):
        if not self.source_metadata:
            self.source_metadata = {}
        self.source_metadata['chapter'] = value
        
    @property
    def difficulty(self):
        return self.source_metadata.get('difficulty', 'medium') if self.source_metadata else 'medium'
        
    @difficulty.setter
    def difficulty(self, value):
        if not self.source_metadata:
            self.source_metadata = {}
        self.source_metadata['difficulty'] = value
        
    @property
    def updated_at(self):
        return self.created_at  # 原表沒有 updated_at
