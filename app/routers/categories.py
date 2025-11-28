from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Category

router = APIRouter()

@router.get("/")
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "paper_count": len(c.papers)
        }
        for c in categories
    ]
