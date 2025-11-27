import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Paper

class ArxivScraper:
    def __init__(self, base_url="http://export.arxiv.org/api/query"):
        self.base_url = base_url
    
    async def fetch_recent_papers(self, max_results=10):
        params = {
            "search_query": "all",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max_results
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            return response.text
    
    def save_papers(self, db: Session, papers_data):
        for paper_data in papers_data:
            paper = Paper(
                arxiv_id=paper_data["id"],
                title=paper_data["title"],
                authors=paper_data["authors"],
                abstract=paper_data["abstract"],
                published_date=paper_data["published"],
                pdf_url=paper_data["pdf_url"]
            )
            db.add(paper)
        db.commit()
