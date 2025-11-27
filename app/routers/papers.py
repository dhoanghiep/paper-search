from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Paper

router = APIRouter()

@router.get("/")
def list_papers(db: Session = Depends(get_db)):
    return db.query(Paper).all()

@router.get("/{paper_id}")
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    return db.query(Paper).filter(Paper.id == paper_id).first()
