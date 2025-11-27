# Workstream: arXiv Crawler

**Status:** Ready to implement
**Priority:** CRITICAL
**Estimated Time:** 2-3 hours

---

## Tasks

### 1. Complete arXiv Scraper Agent
- [ ] Parse XML responses from arXiv API
- [ ] Handle pagination
- [ ] Add rate limiting (3 req/sec max)
- [ ] Error handling and retries

### 2. Create Scheduled Job
- [ ] Daily scraper job
- [ ] Store new papers in database
- [ ] Log scraping results

### 3. Test with Real Data
- [ ] Fetch 10 recent papers
- [ ] Verify database storage
- [ ] Check data quality

---

## Implementation Steps

### Step 1: Update scraper.py with XML parsing
```python
import xml.etree.ElementTree as ET
import asyncio
from datetime import datetime

# Add parse_arxiv_response method
# Add rate limiting with asyncio.sleep(0.34)
```

### Step 2: Create CLI command
```bash
# app/cli.py
python -m app.cli scrape --max-results=10
```

### Step 3: Test
```bash
source venv/bin/activate
python -m app.cli scrape
```

---

## Files to Modify
- `app/agents/scraper.py` - Complete implementation
- `app/cli.py` - Create CLI commands (NEW)
- `app/routers/papers.py` - Add scrape endpoint

---

## Testing Checklist
- [ ] Can fetch papers from arXiv
- [ ] XML parsing works correctly
- [ ] Papers saved to database
- [ ] Rate limiting respected
- [ ] Error handling works

---

## Next Steps After Completion
- Integrate with Database MCP Server
- Add category extraction from arXiv subjects
- Schedule daily cron job
