from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Paper
from app.agents.scraper import ArxivScraper
from typing import List

router = APIRouter()

@router.get("/")
def list_papers(db: Session = Depends(get_db)):
    papers = db.query(Paper).all()
    return [
        {
            "id": p.id,
            "arxiv_id": p.arxiv_id,
            "title": p.title,
            "authors": p.authors,
            "abstract": p.abstract,
            "summary": p.summary,
            "published_date": p.published_date.isoformat() if p.published_date else None,
            "pdf_url": p.pdf_url,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "categories": [{"id": c.id, "name": c.name} for c in p.categories]
        }
        for p in papers
    ]

@router.get("/{paper_id}")
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    p = db.query(Paper).filter(Paper.id == paper_id).first()
    if not p:
        return None
    return {
        "id": p.id,
        "arxiv_id": p.arxiv_id,
        "title": p.title,
        "authors": p.authors,
        "abstract": p.abstract,
        "summary": p.summary,
        "published_date": p.published_date.isoformat() if p.published_date else None,
        "pdf_url": p.pdf_url,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "categories": [{"id": c.id, "name": c.name} for c in p.categories]
    }

@router.post("/scrape")
async def scrape_papers(max_results: int = 10, db: Session = Depends(get_db)):
    scraper = ArxivScraper()
    papers = await scraper.fetch_recent_papers(max_results)
    scraper.save_papers(db, papers)
    return {"status": "success", "count": len(papers)}
