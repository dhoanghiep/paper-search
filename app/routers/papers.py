from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Paper, Category
from typing import Optional

router = APIRouter()


def _serialize(p: Paper) -> dict:
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
        "categories": [{"id": c.id, "name": c.name} for c in p.categories],
    }


@router.get("/")
def list_papers(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    category: Optional[str] = None,
):
    """List papers with optional search and category filter, paginated."""
    q = db.query(Paper)
    if search:
        q = q.filter(
            Paper.title.ilike(f"%{search}%") | Paper.abstract.ilike(f"%{search}%")
        )
    if category:
        q = q.join(Paper.categories).filter(Category.name == category)
    total = q.count()
    papers = q.order_by(Paper.created_at.desc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "papers": [_serialize(p) for p in papers],
    }


@router.get("/{paper_id}")
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    """Get a single paper by ID."""
    p = db.query(Paper).filter(Paper.id == paper_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paper not found")
    return _serialize(p)
