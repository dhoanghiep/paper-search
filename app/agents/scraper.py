import httpx
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
from app.agents.base_scraper import BaseScraper

class ArxivScraper(BaseScraper):
    def __init__(self, base_url="https://export.arxiv.org/api/query"):
        self.base_url = base_url
    
    async def fetch_recent_papers(self, max_results=10):
        params = {
            "search_query": "all",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max_results
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(3):
                try:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()
                    await asyncio.sleep(0.34)
                    return self.parse_arxiv_response(response.text)
                except Exception as e:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(1)
    
    def parse_arxiv_response(self, xml_text):
        root = ET.fromstring(xml_text)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
        papers = []
        for entry in root.findall('atom:entry', ns):
            arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
            title = entry.find('atom:title', ns).text.strip()
            abstract = entry.find('atom:summary', ns).text.strip()
            published = datetime.fromisoformat(entry.find('atom:published', ns).text.replace('Z', '+00:00'))
            authors = ', '.join([a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)])
            pdf_url = next((link.get('href') for link in entry.findall('atom:link', ns) if link.get('title') == 'pdf'), None)
            papers.append({"id": arxiv_id, "title": title, "authors": authors, "abstract": abstract, "published": published, "pdf_url": pdf_url})
        return papers
