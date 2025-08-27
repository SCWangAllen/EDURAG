from sqlalchemy import Column, Integer, String, Text, ARRAY, TIMESTAMP, ForeignKey
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
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

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
    question_type = Column(String(16), nullable=False)
    stem = Column(Text, nullable=False)
    options = Column(ARRAY(Text))
    answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
