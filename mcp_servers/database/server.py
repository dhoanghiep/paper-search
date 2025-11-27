#!/usr/bin/env python3
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from sqlalchemy import create_engine, desc, or_
from sqlalchemy.orm import sessionmaker
from app.models import Paper, Category, Report, Base
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://paper_user:paper_pass@localhost:5432/paper_search")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def query_papers(filters=None, limit=10, offset=0):
    db = SessionLocal()
    try:
        query = db.query(Paper)
        if filters:
            if filters.get("category"):
                query = query.join(Paper.categories).filter(Category.name == filters["category"])
            if filters.get("author"):
                query = query.filter(Paper.authors.ilike(f"%{filters['author']}%"))
            if filters.get("keyword"):
                kw = f"%{filters['keyword']}%"
                query = query.filter(or_(Paper.title.ilike(kw), Paper.abstract.ilike(kw)))
        query = query.order_by(desc(Paper.published_date)).limit(limit).offset(offset)
        papers = [{"id": p.id, "arxiv_id": p.arxiv_id, "title": p.title, "authors": p.authors, 
                   "abstract": p.abstract, "published_date": str(p.published_date)} for p in query.all()]
        return {"papers": papers, "count": len(papers)}
    finally:
        db.close()

def get_paper(paper_id):
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise Exception("Paper not found")
        return {"id": paper.id, "arxiv_id": paper.arxiv_id, "title": paper.title, 
                "authors": paper.authors, "abstract": paper.abstract, "summary": paper.summary,
                "published_date": str(paper.published_date), "pdf_url": paper.pdf_url,
                "categories": [c.name for c in paper.categories]}
    finally:
        db.close()

def add_paper(paper_data):
    db = SessionLocal()
    try:
        paper = Paper(
            arxiv_id=paper_data["arxiv_id"],
            title=paper_data["title"],
            authors=", ".join(paper_data["authors"]) if isinstance(paper_data["authors"], list) else paper_data["authors"],
            abstract=paper_data["abstract"],
            summary=paper_data.get("summary"),
            published_date=datetime.fromisoformat(paper_data["published"].replace('Z', '+00:00')),
            pdf_url=paper_data.get("pdf_url")
        )
        db.add(paper)
        db.commit()
        db.refresh(paper)
        return {"id": paper.id, "arxiv_id": paper.arxiv_id}
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def update_paper(paper_id, updates):
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise Exception("Paper not found")
        for key, value in updates.items():
            if hasattr(paper, key):
                setattr(paper, key, value)
        db.commit()
        return {"id": paper.id, "status": "updated"}
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def get_categories():
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        return {"categories": [{"id": c.id, "name": c.name, "description": c.description} for c in categories]}
    finally:
        db.close()

def add_category(name, description=""):
    db = SessionLocal()
    try:
        category = Category(name=name, description=description)
        db.add(category)
        db.commit()
        db.refresh(category)
        return {"id": category.id, "name": category.name}
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def assign_category(paper_id, category_name):
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        category = db.query(Category).filter(Category.name == category_name).first()
        if not paper or not category:
            raise Exception("Paper or category not found")
        if category not in paper.categories:
            paper.categories.append(category)
            db.commit()
        return {"status": "assigned"}
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def save_report(report_type, content):
    db = SessionLocal()
    try:
        report = Report(report_type=report_type, content=content)
        db.add(report)
        db.commit()
        db.refresh(report)
        return {"id": report.id, "created_at": str(report.created_at)}
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def get_statistics():
    db = SessionLocal()
    try:
        total_papers = db.query(Paper).count()
        total_categories = db.query(Category).count()
        recent = db.query(Paper).order_by(desc(Paper.created_at)).limit(5).all()
        return {
            "total_papers": total_papers,
            "total_categories": total_categories,
            "recent_papers": [{"id": p.id, "title": p.title} for p in recent]
        }
    finally:
        db.close()

TOOLS = {
    "query_papers": {"description": "Query papers with filters", "params": ["filters", "limit", "offset"]},
    "get_paper": {"description": "Get paper by ID", "params": ["paper_id"]},
    "add_paper": {"description": "Add new paper", "params": ["paper_data"]},
    "update_paper": {"description": "Update paper fields", "params": ["paper_id", "updates"]},
    "get_categories": {"description": "List all categories", "params": []},
    "add_category": {"description": "Create category", "params": ["name", "description"]},
    "assign_category": {"description": "Assign category to paper", "params": ["paper_id", "category_name"]},
    "save_report": {"description": "Save report to database", "params": ["report_type", "content"]},
    "get_statistics": {"description": "Get database statistics", "params": []}
}

def handle_message(msg):
    method = msg.get("method")
    params = msg.get("params", {})
    msg_id = msg.get("id")
    
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"protocolVersion": "1.0", "serverInfo": {"name": "database", "version": "1.0"}}}
    elif method == "tools/list":
        tools = [{"name": name, "description": info["description"], "inputSchema": {"type": "object", "properties": {p: {"type": "string"} for p in info["params"]}}} for name, info in TOOLS.items()]
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": tools}}
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        try:
            result = globals()[tool_name](**args)
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": json.dumps(result)}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -1, "message": str(e)}}
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -1, "message": "Unknown method"}}

if __name__ == "__main__":
    for line in sys.stdin:
        msg = json.loads(line)
        response = handle_message(msg)
        print(json.dumps(response), flush=True)
