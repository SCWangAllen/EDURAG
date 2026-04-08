from sqlalchemy import Column, Integer, String, Text, ARRAY, TIMESTAMP, ForeignKey, JSON, Boolean, UniqueConstraint
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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
    grade = Column(String(50), nullable=True)  # 年級（任意格式）
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # 關係定義
    questions = relationship("Question", back_populates="document")

class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(50), nullable=True, index=True)  # 保留舊欄位以兼容
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)  # 新的外鍵關聯
    name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)  # prompt template
    question_type = Column(String(32), nullable=True, default='single_choice')  # 題型（前端應明確指定，此為安全預設值）
    params = Column(JSON, nullable=True)    # 溫度、top_p 等參數
    grades = Column(JSON, nullable=True, default=[])  # 適用年級列表，例如 ["G1", "G2"]
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # 關聯到科目
    subject_obj = relationship("Subject", back_populates="templates")
    questions = relationship("Question", back_populates="template")

    @property
    def subject_name(self):
        """取得科目名稱（優先使用關聯，fallback 到舊欄位）"""
        if self.subject_obj:
            return self.subject_obj.name
        return self.subject

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "subject": self.subject_name,  # 對前端保持相容
            "subject_id": self.subject_id,
            "content": self.content,
            "question_type": self.question_type,  # 新增題型欄位
            "params": self.params,
            "grades": self.grades or [],  # 適用年級列表
            "version": self.version,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

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
    question_type = Column("question_type", String(32), nullable=False)  # 擴展長度支援新題型
    stem = Column("stem", Text, nullable=False)  # 題目內容 (原本叫 content)
    options = Column(ARRAY(Text), nullable=True)  # 選擇題選項 (ARRAY 而不是 JSON)
    answer = Column("answer", Text, nullable=False)  # 正確答案 (原本叫 correct_answer)
    explanation = Column(Text, nullable=False)  # 解釋
    
    # G1~G2 新增：題型專用資料
    question_data = Column(JSON, nullable=True)  # 配對項、排序項等題型專用資料
    
    # 來源資訊
    document_id = Column("document_id", Integer, ForeignKey("documents.id"))  # 來源文件ID (原本叫 source_document_id)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)  # 使用的模板
    source_metadata = Column(JSON, nullable=True)  # 來源元數據 (包含章節、頁數等)
    
    # 匯出相關
    export_batch_id = Column(String(50), nullable=True)  # 匯出批次ID
    
    # 時間戳
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # 關係定義
    document = relationship("Document", back_populates="questions")
    template = relationship("Template", back_populates="questions")
    
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
    def grade(self):
        return self.source_metadata.get('grade') if self.source_metadata else None

    @grade.setter
    def grade(self, value):
        if not self.source_metadata:
            self.source_metadata = {}
        self.source_metadata['grade'] = value

    @property
    def page(self):
        return self.source_metadata.get('page') if self.source_metadata else None

    @page.setter
    def page(self, value):
        if not self.source_metadata:
            self.source_metadata = {}
        self.source_metadata['page'] = value


class Subject(Base):
    """科目模型"""
    __tablename__ = "subjects"
    __table_args__ = (
        UniqueConstraint('name', 'grade', name='uq_subject_name_grade'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)  # 移除 unique=True，改為 name + grade 組合唯一
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#3B82F6")  # 預設藍色
    grade = Column(String(20), nullable=True)  # 年級：擴展長度，允許自訂年級
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # 關係定義
    templates = relationship("Template", back_populates="subject_obj")

    def __repr__(self):
        return f"<Subject(id={self.id}, name='{self.name}', grade='{self.grade}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "grade": self.grade,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ImageQuestion(Base):
    """圖片題目模型 - 用於管理基於圖片的題目"""
    __tablename__ = "image_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_image = Column(String(255), nullable=False, index=True)  # 問題圖片名（不含副檔名）
    answer_image = Column(String(255), nullable=True)  # 答案圖片名（可選）
    question_description = Column(Text, nullable=True)  # 題目類型描述
    subject = Column(String(50), nullable=False, index=True)
    chapter = Column(String(100), nullable=True)
    grade = Column(String(10), nullable=True, index=True)
    page = Column(String(20), nullable=True)
    question_image_ext = Column(String(10), default='jpg')  # 問題圖片副檔名
    answer_image_ext = Column(String(10), default='jpg')  # 答案圖片副檔名
    images_verified = Column(Boolean, default=False)  # 圖片是否已驗證存在
    import_batch_id = Column(String(50), nullable=True)  # 匯入批次 ID
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    @property
    def question_image_path(self) -> str:
        """取得問題圖片完整檔名"""
        return f"{self.question_image}.{self.question_image_ext}"

    @property
    def answer_image_path(self) -> str | None:
        """取得答案圖片完整檔名"""
        if self.answer_image:
            return f"{self.answer_image}.{self.answer_image_ext}"
        return None

    def __repr__(self):
        return f"<ImageQuestion(id={self.id}, question_image='{self.question_image}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "question_image": self.question_image,
            "answer_image": self.answer_image,
            "question_description": self.question_description,
            "subject": self.subject,
            "chapter": self.chapter,
            "grade": self.grade,
            "page": self.page,
            "question_image_ext": self.question_image_ext,
            "answer_image_ext": self.answer_image_ext,
            "question_image_path": self.question_image_path,
            "answer_image_path": self.answer_image_path,
            "images_verified": self.images_verified,
            "import_batch_id": self.import_batch_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
