from fastapi import APIRouter, BackgroundTasks, Depends
from app.services.processing import process_papers_batch
from app.agents.biorxiv_scraper import BiorxivScraper
from app.agents.pubmed_scraper import PubmedScraper
from app.database import get_db
from sqlalchemy.orm import Session
import asyncio

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/scrape")
async def trigger_scrape(source: str = "biorxiv", max_results: int = 10, query: str = None, days_back: int = 30, db: Session = Depends(get_db)):
    """Manually trigger scraping from biorxiv or pubmed"""
    if source == "biorxiv":
        from app.config import settings
        biorxiv_query = query or settings.BIORXIV_SCRAPE_QUERY or None
        scraper = BiorxivScraper()
        papers = await scraper.fetch_recent_papers(max_results, days_back=days_back, query=biorxiv_query)
    elif source == "pubmed":
        scraper = PubmedScraper()
        papers = await scraper.fetch_recent_papers(max_results, query or "longread")
    else:
        return {"error": f"Unknown source: {source}. Use 'biorxiv' or 'pubmed'"}

    saved_count = scraper.save_papers(db, papers)
    return {"status": "completed", "source": source, "papers_fetched": len(papers), "papers_saved": saved_count}

@router.post("/process")
async def trigger_process(background_tasks: BackgroundTasks, limit: int = 10):
    """Process unprocessed papers in the background"""
    background_tasks.add_task(process_papers_batch, limit)
    return {"status": "started", "message": f"Processing up to {limit} papers in background"}

@router.post("/process-sync")
async def trigger_process_sync(limit: int = 10):
    """Process papers synchronously (for testing)"""
    result = process_papers_batch(limit)
    return {"status": "completed", "result": result}

@router.get("/status")
async def job_status():
    """Get processing status"""
    from app.database import SessionLocal
    from app.models import Paper

    db = SessionLocal()
    try:
        total = db.query(Paper).count()
        processed = db.query(Paper).filter(Paper.summary != None, Paper.summary != "").count()
        return {
            "total_papers": total,
            "processed": processed,
            "unprocessed": total - processed,
        }
    finally:
        db.close()

@router.get("/scheduler/status")
async def scheduler_status():
    """Get scheduler status"""
    try:
        from app.scheduler import scheduler
        jobs = [
            {"id": job.id, "name": job.name, "next_run": str(job.next_run_time) if job.next_run_time else None}
            for job in scheduler.get_jobs()
        ]
        return {"status": "running", "jobs": jobs}
    except Exception as e:
        return {"status": "not_running", "error": str(e)}
