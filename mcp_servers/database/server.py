#!/usr/bin/env python3
import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from sqlalchemy import create_engine, desc, or_
from sqlalchemy.orm import sessionmaker
from app.models import Paper, Category, Base
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://paper_user:paper_pass@localhost:5432/paper_search")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

async def query_papers(filters: dict = None, limit: int = 10, offset: int = 0) -> dict:
    """Query papers with filters"""
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

async def get_paper(paper_id: int) -> dict:
    """Get single paper by ID"""
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            return {"error": "Paper not found"}
        return {"id": paper.id, "arxiv_id": paper.arxiv_id, "title": paper.title, 
                "authors": paper.authors, "abstract": paper.abstract, "summary": paper.summary,
                "published_date": str(paper.published_date), "pdf_url": paper.pdf_url}
    finally:
        db.close()

async def add_paper(paper_data: dict) -> dict:
    """Add new paper to database"""
    db = SessionLocal()
    try:
        paper = Paper(
            arxiv_id=paper_data["arxiv_id"],
            title=paper_data["title"],
            authors=", ".join(paper_data["authors"]) if isinstance(paper_data["authors"], list) else paper_data["authors"],
            abstract=paper_data["abstract"],
            published_date=datetime.fromisoformat(paper_data["published"].replace('Z', '+00:00')),
            pdf_url=paper_data.get("pdf_url")
        )
        db.add(paper)
        db.commit()
        db.refresh(paper)
        return {"id": paper.id, "arxiv_id": paper.arxiv_id, "status": "created"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

async def get_categories() -> dict:
    """List all categories"""
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        return {"categories": [{"id": c.id, "name": c.name, "description": c.description} for c in categories]}
    finally:
        db.close()

async def add_category(name: str, description: str = "") -> dict:
    """Create new category"""
    db = SessionLocal()
    try:
        category = Category(name=name, description=description)
        db.add(category)
        db.commit()
        db.refresh(category)
        return {"id": category.id, "name": category.name, "status": "created"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

async def get_statistics() -> dict:
    """Get database statistics"""
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

async def handle_request(request: dict) -> dict:
    """Handle MCP tool requests"""
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "query_papers":
        return await query_papers(params.get("filters"), params.get("limit", 10), params.get("offset", 0))
    elif method == "get_paper":
        return await get_paper(params["paper_id"])
    elif method == "add_paper":
        return await add_paper(params["paper_data"])
    elif method == "get_categories":
        return await get_categories()
    elif method == "add_category":
        return await add_category(params["name"], params.get("description", ""))
    elif method == "get_statistics":
        return await get_statistics()
    else:
        return {"error": f"Unknown method: {method}"}

async def main():
    """MCP server main loop"""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line)
            result = await handle_request(request)
            print(json.dumps(result), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
