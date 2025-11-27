from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import papers, categories, reports, jobs
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    
    # Start scheduler
    try:
        from app.scheduler import start_scheduler
        start_scheduler()
        logger.info("Scheduler started")
    except Exception as e:
        logger.warning(f"Scheduler not started: {e}")
    
    yield
    
    # Shutdown
    try:
        from app.scheduler import stop_scheduler
        stop_scheduler()
    except:
        pass

app = FastAPI(title="Paper Search API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    return {"message": "Paper Search API", "status": "running"}

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
