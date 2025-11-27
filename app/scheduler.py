from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.pipeline import process_new_papers
from app.agents.scraper import ArxivScraper
from app.agents.biorxiv_scraper import BiorxivScraper
from app.agents.pubmed_scraper import PubmedScraper
from app.database import SessionLocal
from app.reports_job import generate_daily_report
import asyncio
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def scrape_all_sources():
    """Scrape papers from all sources"""
    db = SessionLocal()
    try:
        sources = [
            (ArxivScraper(), "arXiv", 10),
            (BiorxivScraper(), "bioRxiv", 10),
            (PubmedScraper(), "PubMed", 10)
        ]
        
        for scraper, name, max_results in sources:
            try:
                logger.info(f"Scraping {name}...")
                if name == "PubMed":
                    papers = asyncio.run(scraper.fetch_recent_papers(max_results, "cancer OR diabetes"))
                else:
                    papers = asyncio.run(scraper.fetch_recent_papers(max_results))
                scraper.save_papers(db, papers)
                logger.info(f"Scraped {len(papers)} papers from {name}")
            except Exception as e:
                logger.error(f"Error scraping {name}: {e}")
    finally:
        db.close()

def process_papers_job():
    """Process unprocessed papers"""
    try:
        logger.info("Processing papers...")
        result = process_new_papers(limit=50)
        logger.info(f"Processed {result['processed']} papers, {result['errors']} errors")
    except Exception as e:
        logger.error(f"Error processing papers: {e}")

def daily_report_job():
    """Generate daily report"""
    try:
        logger.info("Generating daily report...")
        report = generate_daily_report()
        logger.info(f"Daily report generated: {len(report)} characters")
    except Exception as e:
        logger.error(f"Error generating report: {e}")

def start_scheduler():
    """Start the scheduler with all jobs"""
    # Daily scraping at 6 AM
    scheduler.add_job(scrape_all_sources, CronTrigger(hour=6, minute=0), id="daily_scrape")
    
    # Process papers every 2 hours
    scheduler.add_job(process_papers_job, CronTrigger(hour="*/2"), id="process_papers")
    
    # Daily report at 9 AM
    scheduler.add_job(daily_report_job, CronTrigger(hour=9, minute=0), id="daily_report")
    
    scheduler.start()
    logger.info("Scheduler started")

def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")
