# PubMed Integration

**Added:** 2025-11-27  
**Status:** Ready to use

---

## What's New

✅ **PubMed Scraper** (`app/agents/pubmed_scraper.py`)
- Uses NCBI E-utilities API
- Two-step process: search → fetch details
- Supports custom search queries
- Rate limited to 3 req/sec (NCBI requirement)

---

## Usage

### CLI

**Scrape with default query (cancer OR diabetes):**
```bash
python -m app.cli --source=pubmed --max-results=10
```

**Scrape with custom query:**
```bash
python -m app.cli --source=pubmed --max-results=10 --query="machine learning AND medical imaging"
```

### API

**Default query:**
```bash
curl -X POST "http://localhost:8000/jobs/scrape?source=pubmed&max_results=10"
```

**Custom query:**
```bash
curl -X POST "http://localhost:8000/jobs/scrape?source=pubmed&max_results=10&query=alzheimer+AND+treatment"
```

---

## PubMed API Details

**Base URL:** `https://eutils.ncbi.nlm.nih.gov/entrez/eutils`

**Two-step process:**
1. **ESearch** - Search for PMIDs matching query
2. **EFetch** - Fetch full article details by PMID

**Response Format:** XML

**Fields:**
- `PMID` - PubMed ID (unique identifier)
- `ArticleTitle` - Paper title
- `AbstractText` - Abstract
- `Author` - Author list (LastName, ForeName)
- `PubDate` - Publication date

**Rate Limiting:** 3 requests/second (0.34s delay)

---

## Query Examples

**Disease research:**
```
cancer OR diabetes
alzheimer AND treatment
covid-19 AND vaccine
```

**By field:**
```
machine learning[Title/Abstract]
CRISPR[MeSH Terms]
```

**Date range:**
```
cancer AND 2024[PDAT]
```

**Combined:**
```
(cancer OR tumor) AND (treatment OR therapy) AND 2024[PDAT]
```

---

## Database Storage

Papers stored with PMID as identifier:
- Format: `PMID:12345678`
- Link: `https://pubmed.ncbi.nlm.nih.gov/12345678/`

---

## All Sources Summary

| Source | Identifier | API Type | Rate Limit |
|--------|-----------|----------|------------|
| arXiv | arXiv ID | XML | 3 req/sec |
| bioRxiv | DOI | JSON | 2 req/sec |
| PubMed | PMID | XML | 3 req/sec |

---

## Test It

```bash
# Scrape 5 papers about AI in medicine
curl -X POST "http://localhost:8000/jobs/scrape?source=pubmed&max_results=5&query=artificial+intelligence+AND+medicine"

# Check status
curl http://localhost:8000/jobs/status

# View papers
curl http://localhost:8000/papers/
```

---

## Next Steps

- Add more medical databases (Europe PMC, Semantic Scholar)
- Add source field to distinguish repositories
- Create unified search across all sources
