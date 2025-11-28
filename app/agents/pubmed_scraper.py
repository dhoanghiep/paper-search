import httpx
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
from app.agents.base_scraper import BaseScraper

class PubmedScraper(BaseScraper):
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    async def fetch_recent_papers(self, max_results=10, query="cancer OR diabetes"):
        """Fetch recent papers from PubMed"""
        # Step 1: Search for paper IDs
        search_url = f"{self.base_url}/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "sort": "pub_date",
            "retmode": "json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get IDs
            search_response = await client.get(search_url, params=search_params)
            search_response.raise_for_status()
            await asyncio.sleep(0.34)  # NCBI rate limit: 3 req/sec
            
            ids = search_response.json()["esearchresult"]["idlist"]
            if not ids:
                return []
            
            # Step 2: Fetch paper details
            fetch_url = f"{self.base_url}/efetch.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(ids),
                "retmode": "xml"
            }
            
            fetch_response = await client.get(fetch_url, params=fetch_params)
            fetch_response.raise_for_status()
            await asyncio.sleep(0.34)
            
            return self.parse_pubmed_response(fetch_response.text)
    
    def parse_pubmed_response(self, xml_text):
        """Parse PubMed XML response"""
        root = ET.fromstring(xml_text)
        papers = []
        
        for article in root.findall(".//PubmedArticle"):
            try:
                pmid = article.find(".//PMID").text
                
                title_elem = article.find(".//ArticleTitle")
                title = title_elem.text if title_elem is not None else "No title"
                
                abstract_elem = article.find(".//AbstractText")
                abstract = abstract_elem.text if abstract_elem is not None else "No abstract available"
                
                # Authors
                authors = []
                for author in article.findall(".//Author"):
                    lastname = author.find("LastName")
                    forename = author.find("ForeName")
                    if lastname is not None and forename is not None:
                        authors.append(f"{forename.text} {lastname.text}")
                
                # Publication date
                pub_date = article.find(".//PubDate")
                year = pub_date.find("Year").text if pub_date.find("Year") is not None else "2024"
                month = pub_date.find("Month").text if pub_date.find("Month") is not None else "01"
                day = pub_date.find("Day").text if pub_date.find("Day") is not None else "01"
                
                # Convert month name to number if needed
                month_map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                            "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
                month = month_map.get(month, month if month.isdigit() else "01")
                
                published = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
                
                papers.append({
                    "id": f"PMID:{pmid}",
                    "title": title,
                    "authors": ", ".join(authors) if authors else "Unknown",
                    "abstract": abstract,
                    "published": published,
                    "pdf_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
            except Exception as e:
                continue
        
        return papers
