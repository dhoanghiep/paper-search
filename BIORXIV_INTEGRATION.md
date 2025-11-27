# bioRxiv Integration

**Added:** 2025-11-27  
**Status:** Ready to use

---

## What's New

✅ **BioRxiv Scraper** (`app/agents/biorxiv_scraper.py`)
- Fetches papers from bioRxiv API
- Supports date range queries (default: last 7 days)
- Stores DOI as unique identifier

✅ **Updated CLI** - Now supports both sources
✅ **Updated API** - Scrape endpoint accepts source parameter

---

## Usage

### CLI

**Scrape from arXiv (default):**
```bash
python -m app.cli --source=arxiv --max-results=10
```

**Scrape from bioRxiv:**
```bash
python -m app.cli --source=biorxiv --max-results=10
```

### API

**Scrape from arXiv:**
```bash
curl -X POST "http://localhost:8000/jobs/scrape?source=arxiv&max_results=10"
```

**Scrape from bioRxiv:**
```bash
curl -X POST "http://localhost:8000/jobs/scrape?source=biorxiv&max_results=10"
```

---

## bioRxiv API Details

**Endpoint:** `https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}/0/json`

**Response Format:** JSON (not XML like arXiv)

**Fields:**
- `doi` - Unique identifier (e.g., "10.1101/2024.11.20.624567")
- `title` - Paper title
- `authors` - Comma-separated author list
- `abstract` - Paper abstract
- `date` - Publication date
- `category` - Subject category

**Rate Limiting:** 0.5 seconds between requests

---

## Database Storage

Papers from both sources stored in same `papers` table:
- arXiv papers: `arxiv_id` = arXiv ID (e.g., "2311.12345")
- bioRxiv papers: `arxiv_id` = DOI (e.g., "10.1101/2024.11.20.624567")

---

## Test It

```bash
# Scrape 5 papers from bioRxiv
curl -X POST "http://localhost:8000/jobs/scrape?source=biorxiv&max_results=5"

# Check status
curl http://localhost:8000/jobs/status

# View papers
curl http://localhost:8000/papers/
```

---

## Next Steps

- Add medRxiv support (similar API)
- Add source field to Paper model to distinguish repositories
- Create separate MCP server for bioRxiv
