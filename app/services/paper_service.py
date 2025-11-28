"""Business logic for paper operations"""
from sqlalchemy.orm import Session
from app.models import Paper
from app.repositories import PaperRepository
from app.exceptions import PaperNotFoundException, ValidationException
from typing import List, Dict, Any
from datetime import datetime

class PaperService:
    """Service layer for paper business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = PaperRepository(db)
    
    def get_paper(self, paper_id: int) -> Paper:
        """Get paper by ID with validation"""
        paper = self.repo.get_by_id(paper_id)
        if not paper:
            raise PaperNotFoundException(f"Paper {paper_id} not found")
        return paper
    
    def search_papers(self, query: str, limit: int = 20) -> List[Paper]:
        """Search papers with validation"""
        if not query or len(query.strip()) < 2:
            raise ValidationException("Search query must be at least 2 characters")
        return self.repo.search(query, limit)
    
    def get_unprocessed_papers(self, limit: int = 10) -> List[Paper]:
        """Get papers that need processing"""
        return self.repo.get_unprocessed(limit)
    
    def filter_papers(self, categories: List[str] = None, 
                     start_date: datetime = None, 
                     end_date: datetime = None,
                     unprocessed_only: bool = False,
                     limit: int = 100) -> List[Paper]:
        """Filter papers with multiple criteria"""
        if start_date and end_date:
            return self.repo.filter_by_date_range(start_date, end_date, categories)
        elif categories:
            return self.repo.filter_by_categories(categories, limit)
        elif unprocessed_only:
            return self.repo.get_unprocessed(limit)
        else:
            return self.repo.get_all(limit)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        total = self.repo.count_all()
        processed = self.repo.count_processed()
        recent = self.repo.count_recent(7)
        
        return {
            "total_papers": total,
            "processed_papers": processed,
            "unprocessed_papers": total - processed,
            "papers_this_week": recent,
            "processing_rate": round(processed / total * 100, 2) if total > 0 else 0
        }
    
    def create_paper(self, arxiv_id: str, title: str, authors: str, 
                    abstract: str, published_date: datetime, pdf_url: str) -> Paper:
        """Create new paper with validation"""
        # Check if already exists
        existing = self.repo.get_by_arxiv_id(arxiv_id)
        if existing:
            raise ValidationException(f"Paper {arxiv_id} already exists")
        
        # Validate withdrawn papers
        if title.upper().startswith("WITHDRAWN:"):
            raise ValidationException(f"Paper is withdrawn: {title}")
        
        paper = Paper(
            arxiv_id=arxiv_id,
            title=title,
            authors=authors,
            abstract=abstract,
            published_date=published_date,
            pdf_url=pdf_url
        )
        
        return self.repo.create(paper)
    
    def update_paper_summary(self, paper_id: int, summary: str) -> Paper:
        """Update paper summary"""
        paper = self.get_paper(paper_id)
        paper.summary = summary
        return self.repo.update(paper)
    
    def delete_paper(self, paper_id: int) -> bool:
        """Delete paper"""
        if not self.repo.get_by_id(paper_id):
            raise PaperNotFoundException(f"Paper {paper_id} not found")
        return self.repo.delete(paper_id)
