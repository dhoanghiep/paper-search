from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Paper
from typing import List, Dict, Any

class BaseScraper:
    """Base class for all paper scrapers"""
    
    def save_papers(self, db: Session, papers_data: List[Dict[str, Any]]) -> int:
        """Save papers to database, skip duplicates"""
        saved_count = 0
        for paper_data in papers_data:
            try:
                existing = db.query(Paper).filter(Paper.arxiv_id == paper_data["id"]).first()
                if not existing:
                    paper = Paper(
                        arxiv_id=paper_data["id"],
                        title=paper_data["title"],
                        authors=paper_data["authors"],
                        abstract=paper_data["abstract"],
                        published_date=paper_data["published"],
                        pdf_url=paper_data["pdf_url"]
                    )
                    db.add(paper)
                    db.commit()
                    saved_count += 1
            except IntegrityError:
                db.rollback()
                continue
        return saved_count
    
    async def fetch_recent_papers(self, max_results: int, **kwargs) -> List[Dict[str, Any]]:
        """Fetch recent papers - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement fetch_recent_papers()")
