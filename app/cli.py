import asyncio
import sys
from app.agents.scraper import ArxivScraper
from app.agents.biorxiv_scraper import BiorxivScraper
from app.agents.pubmed_scraper import PubmedScraper
from app.database import SessionLocal

async def scrape(source="arxiv", max_results=10, query=None):
    db = SessionLocal()
    try:
        if source == "arxiv":
            scraper = ArxivScraper()
            print(f"Fetching {max_results} papers from arXiv...")
            papers = await scraper.fetch_recent_papers(max_results)
        elif source == "biorxiv":
            scraper = BiorxivScraper()
            print(f"Fetching {max_results} papers from bioRxiv...")
            papers = await scraper.fetch_recent_papers(max_results)
        elif source == "pubmed":
            scraper = PubmedScraper()
            query = query or "cancer OR diabetes"
            print(f"Fetching {max_results} papers from PubMed (query: {query})...")
            papers = await scraper.fetch_recent_papers(max_results, query)
        else:
            print(f"Unknown source: {source}. Use 'arxiv', 'biorxiv', or 'pubmed'")
            return
        
        print(f"Found {len(papers)} papers")
        scraper.save_papers(db, papers)
        print(f"Saved papers to database")
    finally:
        db.close()

if __name__ == "__main__":
    source = "arxiv"
    max_results = 10
    query = None
    
    for arg in sys.argv:
        if arg.startswith("--source="):
            source = arg.split("=")[1]
        elif arg.startswith("--max-results="):
            max_results = int(arg.split("=")[1])
        elif arg.startswith("--query="):
            query = arg.split("=", 1)[1]
    
    asyncio.run(scrape(source, max_results, query))
