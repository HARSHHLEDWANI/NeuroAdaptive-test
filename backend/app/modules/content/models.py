from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    topic = Column(String, index=True)
    
    # Relationships
    paragraphs = relationship("Paragraph", back_populates="article", cascade="all, delete-orphan")
    readings = relationship("ArticleReading", back_populates="article", cascade="all, delete-orphan")

class Paragraph(Base):
    __tablename__ = "paragraphs"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    order_index = Column(Integer) # To keep the paragraphs in the right order (1, 2, 3...)
    original_text = Column(Text)  # The raw, unadapted text
    
    # A paragraph belongs to one article
    article = relationship("Article", back_populates="paragraphs")

class ArticleReading(Base):
    __tablename__ = "article_readings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    read_at = Column(DateTime(timezone=True), server_default=func.now())

    article = relationship("Article", back_populates="readings")
    user = relationship("User", back_populates="article_readings")