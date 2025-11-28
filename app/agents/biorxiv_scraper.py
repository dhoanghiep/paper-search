import httpx
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Paper

class BiorxivScraper:
    def __init__(self):
        self.base_url = "https://api.biorxiv.org/details/biorxiv"
    
    async def fetch_recent_papers(self, max_results=10, days_back=7):
        """Fetch recent papers from bioRxiv API"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        url = f"{self.base_url}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}/0/json"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(3):
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    await asyncio.sleep(0.5)  # Rate limiting
                    return self.parse_biorxiv_response(response.json(), max_results)
                except Exception as e:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(1)
    
    def parse_biorxiv_response(self, data, max_results):
        """Parse bioRxiv API JSON response"""
        papers = []
        collection = data.get("collection", [])[:max_results]
        
        for entry in collection:
            paper = {
                "id": entry.get("doi", ""),
                "title": entry.get("title", "").strip(),
                "authors": entry.get("authors", ""),
                "abstract": entry.get("abstract", "").strip(),
                "published": datetime.fromisoformat(entry.get("date", "").split("T")[0]),
                "pdf_url": f"https://www.biorxiv.org/content/{entry.get('doi', '')}v1.full.pdf"
            }
            papers.append(paper)
        
        return papers
    
    def save_papers(self, db: Session, papers_data):
        """Save papers to database"""
        from sqlalchemy.exc import IntegrityError
        saved_count = 0
        for paper_data in papers_data:
            try:
                # Use DOI as unique identifier for bioRxiv
                existing = db.query(Paper).filter(Paper.arxiv_id == paper_data["id"]).first()
                if not existing:
                    paper = Paper(
                        arxiv_id=paper_data["id"],  # Store DOI in arxiv_id field
                        title=paper_data["title"],
                        authors=paper_data["authors"],
                        abstract=paper_data["abstract"],
                        published_date=paper_data["published"],
                        pdf_url=paper_data["pdf_url"]
                    )
                    db.add(paper)
                    db.commit()
                    saved_count += 1
            except IntegrityError:
                db.rollback()
                continue
        return saved_count
