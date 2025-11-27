from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Report

router = APIRouter()

@router.get("/")
def list_reports(db: Session = Depends(get_db)):
    return db.query(Report).all()
