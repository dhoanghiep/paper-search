from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import papers, categories, reports, jobs

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Paper Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router, prefix="/papers", tags=["papers"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(jobs.router)

@app.get("/")
def root():
    return {"message": "Paper Search API"}

@app.get("/stats")
def get_stats():
    from app.database import SessionLocal
    from app.models import Paper, Category
    from datetime import datetime, timedelta
    
    db = SessionLocal()
    try:
        total_papers = db.query(Paper).count()
        total_categories = db.query(Category).count()
        week_ago = datetime.now() - timedelta(days=7)
        papers_this_week = db.query(Paper).filter(Paper.created_at >= week_ago).count()
        
        return {
            "total_papers": total_papers,
            "total_categories": total_categories,
            "papers_this_week": papers_this_week
        }
    finally:
        db.close()
