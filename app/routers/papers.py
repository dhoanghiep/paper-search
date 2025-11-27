from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Paper
from app.agents.scraper import ArxivScraper

router = APIRouter()

@router.get("/")
def list_papers(db: Session = Depends(get_db)):
    return db.query(Paper).all()

@router.get("/{paper_id}")
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    return db.query(Paper).filter(Paper.id == paper_id).first()

@router.post("/scrape")
async def scrape_papers(max_results: int = 10, db: Session = Depends(get_db)):
    scraper = ArxivScraper()
    papers = await scraper.fetch_recent_papers(max_results)
    scraper.save_papers(db, papers)
    return {"status": "success", "count": len(papers)}
