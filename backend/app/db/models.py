from sqlalchemy import Column, Integer, String, Text, ARRAY, TIMESTAMP, ForeignKey, JSON
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

class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)  # prompt template
    params = Column(JSON, nullable=True)    # 溫度、top_p 等參數
    version = Column(Integer, default=1)
    is_active = Column(String(10), default='true')
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
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    question_type = Column(String(16), nullable=False)
    stem = Column(Text, nullable=False)
    options = Column(ARRAY(Text))
    answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    source_metadata = Column(JSON, nullable=True)  # 章節、頁數等資訊
    export_batch_id = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
