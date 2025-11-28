from sqlalchemy.orm import Session, aliased
from app.models import Paper, Category
from typing import List, Optional
from datetime import datetime

class PaperRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, paper_id: int) -> Optional[Paper]:
        """Get paper by ID"""
        return self.db.query(Paper).filter(Paper.id == paper_id).first()
    
    def get_by_arxiv_id(self, arxiv_id: str) -> Optional[Paper]:
        """Get paper by arXiv/DOI/PMID"""
        return self.db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Paper]:
        """Get all papers with pagination"""
        return self.db.query(Paper).order_by(Paper.created_at.desc()).limit(limit).offset(offset).all()
    
    def get_unprocessed(self, limit: int = 10) -> List[Paper]:
        """Get unprocessed papers (no summary)"""
        return self.db.query(Paper).filter(
            (Paper.summary == None) | (Paper.summary == "")
        ).limit(limit).all()
    
    def search(self, query: str, limit: int = 20) -> List[Paper]:
        """Search papers by title or abstract"""
        return self.db.query(Paper).filter(
            (Paper.title.ilike(f"%{query}%")) | (Paper.abstract.ilike(f"%{query}%"))
        ).limit(limit).all()
    
    def filter_by_categories(self, category_names: List[str], limit: int = 100) -> List[Paper]:
        """Filter papers by categories (AND logic)"""
        query = self.db.query(Paper)
        for cat_name in category_names:
            cat_alias = aliased(Category)
            query = query.join(cat_alias, Paper.categories).filter(
                cat_alias.name.ilike(f"%{cat_name}%")
            )
        return query.distinct().limit(limit).all()
    
    def filter_by_date_range(self, start_date: datetime, end_date: datetime, 
                            category_names: List[str] = None) -> List[Paper]:
        """Filter papers by date range and optionally by categories"""
        query = self.db.query(Paper).filter(
            Paper.published_date >= start_date,
            Paper.published_date <= end_date,
            Paper.summary != None,
            Paper.summary != ""
        )
        
        if category_names:
            for cat_name in category_names:
                cat_alias = aliased(Category)
                query = query.join(cat_alias, Paper.categories).filter(
                    cat_alias.name.ilike(f"%{cat_name}%")
                )
            query = query.distinct()
        
        return query.all()
    
    def count_all(self) -> int:
        """Count all papers"""
        return self.db.query(Paper).count()
    
    def count_processed(self) -> int:
        """Count processed papers"""
        return self.db.query(Paper).filter(
            Paper.summary != None, Paper.summary != ""
        ).count()
    
    def count_recent(self, days: int = 7) -> int:
        """Count papers added in last N days"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        return self.db.query(Paper).filter(Paper.created_at >= cutoff).count()
    
    def create(self, paper: Paper) -> Paper:
        """Create new paper"""
        self.db.add(paper)
        self.db.commit()
        self.db.refresh(paper)
        return paper
    
    def update(self, paper: Paper) -> Paper:
        """Update paper"""
        self.db.commit()
        self.db.refresh(paper)
        return paper
    
    def delete(self, paper_id: int) -> bool:
        """Delete paper"""
        paper = self.get_by_id(paper_id)
        if paper:
            self.db.delete(paper)
            self.db.commit()
            return True
        return False
