import httpx
import asyncio
from datetime import datetime, timedelta
from app.agents.base_scraper import BaseScraper

class BiorxivScraper(BaseScraper):
    def __init__(self):
        self.base_url = "https://api.biorxiv.org/details/biorxiv"

    async def fetch_recent_papers(self, max_results=10, days_back=7, query=None):
        """Fetch recent papers from bioRxiv API.

        If query is provided, pages through results and filters client-side,
        since the bioRxiv API does not support keyword search natively.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        keywords = [kw.lower() for kw in query.split()] if query else None

        seen_dois = set()
        results = []
        cursor = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            while len(results) < max_results:
                url = f"{self.base_url}/{start_str}/{end_str}/{cursor}/json"

                for attempt in range(3):
                    try:
                        response = await client.get(url)
                        response.raise_for_status()
                        break
                    except Exception as e:
                        if attempt == 2:
                            raise
                        await asyncio.sleep(1)

                data = response.json()
                collection = data.get("collection", [])

                if not collection:
                    break

                for entry in collection:
                    doi = entry.get("doi", "")
                    if doi in seen_dois:
                        continue
                    seen_dois.add(doi)

                    paper = self._parse_entry(entry)

                    if keywords is None or self._matches_query(paper, keywords):
                        results.append(paper)
                        if len(results) >= max_results:
                            break

                cursor += len(collection)
                await asyncio.sleep(0.5)  # Rate limiting

                msgs = data.get("messages", [{}])
                total = int(msgs[0].get("total", 0)) if msgs else 0
                if cursor >= total:
                    break

        return results

    def _parse_entry(self, entry):
        title = entry.get("title", "").strip()
        return {
            "id": entry.get("doi", ""),
            "title": title,
            "authors": entry.get("authors", ""),
            "abstract": entry.get("abstract", "").strip(),
            "published": datetime.fromisoformat(entry.get("date", "").split("T")[0]),
            "pdf_url": f"https://www.biorxiv.org/content/{entry.get('doi', '')}v1.full.pdf"
        }

    def _matches_query(self, paper, keywords):
        text = (paper["title"] + " " + paper["abstract"]).lower()
        return any(kw in text for kw in keywords)

    def parse_biorxiv_response(self, data, max_results):
        """Parse bioRxiv API JSON response (legacy, used when no query filter needed)"""
        papers = []
        collection = data.get("collection", [])

        for entry in collection:
            title = entry.get("title", "").strip()

            # Skip withdrawn papers
            if title.upper().startswith("WITHDRAWN:"):
                continue

            papers.append(self._parse_entry(entry))

            if len(papers) >= max_results:
                break

        return papers
