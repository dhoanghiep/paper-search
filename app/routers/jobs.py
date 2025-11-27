from fastapi import APIRouter, BackgroundTasks, Depends
from app.pipeline import process_new_papers
from app.agents.scraper import ArxivScraper
from app.agents.biorxiv_scraper import BiorxivScraper
from app.agents.pubmed_scraper import PubmedScraper
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/scrape")
async def trigger_scrape(source: str = "arxiv", max_results: int = 10, query: str = None, db: Session = Depends(get_db)):
    """Manually trigger scraping from arxiv, biorxiv, or pubmed"""
    if source == "arxiv":
        scraper = ArxivScraper()
        papers = await scraper.fetch_recent_papers(max_results)
    elif source == "biorxiv":
        scraper = BiorxivScraper()
        papers = await scraper.fetch_recent_papers(max_results)
    elif source == "pubmed":
        scraper = PubmedScraper()
        query = query or "cancer OR diabetes"
        papers = await scraper.fetch_recent_papers(max_results, query)
    else:
        return {"error": f"Unknown source: {source}. Use 'arxiv', 'biorxiv', or 'pubmed'"}
    
    scraper.save_papers(db, papers)
    return {"status": "completed", "source": source, "papers_scraped": len(papers)}

@router.post("/process")
async def trigger_process(background_tasks: BackgroundTasks, limit: int = 10):
    """Process unprocessed papers"""
    background_tasks.add_task(process_new_papers, limit)
    return {"status": "started", "message": "Processing papers in background"}

@router.post("/process-sync")
async def trigger_process_sync(limit: int = 10):
    """Process papers synchronously (for testing)"""
    result = process_new_papers(limit)
    return {"status": "completed", "result": result}

@router.post("/report/daily")
async def generate_daily_report_endpoint():
    """Generate daily report"""
    from app.reports_job import generate_daily_report
    report = generate_daily_report()
    return {"status": "completed", "report_length": len(report)}

@router.post("/report/weekly")
async def generate_weekly_report_endpoint():
    """Generate weekly report"""
    from app.reports_job import generate_weekly_report
    report = generate_weekly_report()
    return {"status": "completed", "report_length": len(report)}

@router.post("/email/test")
async def send_test_email(to_email: str):
    """Send test email"""
    from app.notifications import send_email
    success = send_email(to_email, "Test Email", "This is a test email from Paper Search API")
    return {"status": "sent" if success else "failed"}

@router.get("/status")
async def job_status():
    """Get job status"""
    from app.database import SessionLocal
    from app.models import Paper
    
    db = SessionLocal()
    try:
        total = db.query(Paper).count()
        processed = db.query(Paper).filter(Paper.summary != None, Paper.summary != "").count()
        unprocessed = total - processed
        
        return {
            "total_papers": total,
            "processed": processed,
            "unprocessed": unprocessed
        }
    finally:
        db.close()

@router.get("/scheduler/status")
async def scheduler_status():
    """Get scheduler status"""
    try:
        from app.scheduler import scheduler
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None
            })
        return {"status": "running", "jobs": jobs}
    except Exception as e:
        return {"status": "not_running", "error": str(e)}
