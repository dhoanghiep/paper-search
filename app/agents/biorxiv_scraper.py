import httpx
import asyncio
from datetime import datetime, timedelta
from app.agents.base_scraper import BaseScraper

class BiorxivScraper(BaseScraper):
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
        collection = data.get("collection", [])
        
        for entry in collection:
            title = entry.get("title", "").strip()
            
            # Skip withdrawn papers
            if title.upper().startswith("WITHDRAWN:"):
                continue
            
            paper = {
                "id": entry.get("doi", ""),
                "title": title,
                "authors": entry.get("authors", ""),
                "abstract": entry.get("abstract", "").strip(),
                "published": datetime.fromisoformat(entry.get("date", "").split("T")[0]),
                "pdf_url": f"https://www.biorxiv.org/content/{entry.get('doi', '')}v1.full.pdf"
            }
            papers.append(paper)
            
            if len(papers) >= max_results:
                break
        
        return papers
