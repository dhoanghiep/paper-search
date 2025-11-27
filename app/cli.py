import asyncio
import sys
from app.agents.scraper import ArxivScraper
from app.database import SessionLocal

async def scrape(max_results=10):
    scraper = ArxivScraper()
    db = SessionLocal()
    try:
        print(f"Fetching {max_results} papers from arXiv...")
        papers = await scraper.fetch_recent_papers(max_results)
        print(f"Found {len(papers)} papers")
        scraper.save_papers(db, papers)
        print(f"Saved papers to database")
    finally:
        db.close()

if __name__ == "__main__":
    max_results = 10
    for arg in sys.argv:
        if arg.startswith("--max-results="):
            max_results = int(arg.split("=")[1])
    asyncio.run(scrape(max_results))
