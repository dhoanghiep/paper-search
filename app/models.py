from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

paper_categories = Table('paper_categories', Base.metadata,
    Column('paper_id', Integer, ForeignKey('papers.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

class Paper(Base):
    __tablename__ = "papers"
    
    id = Column(Integer, primary_key=True, index=True)
    arxiv_id = Column(String, unique=True, index=True)
    title = Column(String)
    authors = Column(Text)
    abstract = Column(Text)
    summary = Column(Text)
    published_date = Column(DateTime)
    pdf_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    categories = relationship("Category", secondary=paper_categories, back_populates="papers")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    
    papers = relationship("Paper", secondary=paper_categories, back_populates="categories")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class JobHistory(Base):
    __tablename__ = "job_history"
    
    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String, index=True)  # scrape, process, report
    source = Column(String)  # arxiv, biorxiv, pubmed (for scrape jobs)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)
    status = Column(String)  # running, success, failed
    result = Column(JSON)  # Store job results
    error = Column(Text)  # Store error if failed
