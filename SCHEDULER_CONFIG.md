# Scheduler Configuration Guide

## Current Settings

### Daily Scraping (6:00 AM)
- **bioRxiv:** All papers from last 7 days (up to 1000 papers)
- **PubMed:** All papers with keyword "longread" (up to 1000 papers)

### Paper Processing (Every 5 minutes)
- **Batch Size:** 10 papers per run
- **Continues until all papers are processed**

### Daily Report (9:00 AM)
- Generates daily summary report

## Configuration Location

**File:** `app/config.py`

```python
# Daily Scraping Configuration
BIORXIV_SCRAPE_MAX: int = 1000      # Fetch up to 1000 papers
BIORXIV_DAYS_BACK: int = 7          # From last 7 days
PUBMED_SCRAPE_QUERY: str = "longread"  # Search query
PUBMED_SCRAPE_MAX: int = 1000       # Fetch up to 1000 papers

# Processing
PROCESS_BATCH_SIZE: int = 10           # Papers to process per job run
PROCESS_INTERVAL_MINUTES: int = 5      # Process every 5 minutes
```

### Scheduler Jobs

**File:** `app/scheduler.py`

1. **Daily Scraping** - 6:00 AM
   - **bioRxiv:** Fetches all papers from last 7 days (up to 1000)
   - **PubMed:** Fetches all papers matching "longread" (up to 1000)
   - Skips duplicates automatically
   
2. **Paper Processing** - Every 5 minutes
   - Processes 10 unprocessed papers
   - Continues until all papers are processed
   - Logs remaining count after each run
   
3. **Daily Report** - 9:00 AM
   - Generates daily summary report

## Adjusting Daily Scraping

### Change bioRxiv Settings

```python
# app/config.py

# Fetch more papers
BIORXIV_SCRAPE_MAX: int = 2000

# Look back further
BIORXIV_DAYS_BACK: int = 14  # Last 14 days
```

### Change PubMed Query

```python
# app/config.py

# Different keyword
PUBMED_SCRAPE_QUERY: str = "nanopore"

# Multiple keywords
PUBMED_SCRAPE_QUERY: str = "longread OR nanopore OR pacbio"

# More specific
PUBMED_SCRAPE_QUERY: str = "longread AND sequencing"

# Fetch more results
PUBMED_SCRAPE_MAX: int = 2000
```

### Common PubMed Queries

```python
# Long-read sequencing
PUBMED_SCRAPE_QUERY: str = "longread OR nanopore OR pacbio"

# Single-cell
PUBMED_SCRAPE_QUERY: str = "single-cell OR scRNA-seq"

# Cancer genomics
PUBMED_SCRAPE_QUERY: str = "cancer AND genomics"

# CRISPR
PUBMED_SCRAPE_QUERY: str = "CRISPR"

# Bioinformatics tools
PUBMED_SCRAPE_QUERY: str = "bioinformatics AND tool"
```

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│  Scheduler Loop (Every 5 minutes)                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Check for unprocessed papers                        │
│  2. Process batch of 10 papers:                         │
│     - Classify (assign categories)                      │
│     - Summarize (use abstract or LLM)                   │
│  3. Log results:                                        │
│     - Processed: X papers                               │
│     - Errors: Y papers                                  │
│     - Remaining: Z papers                               │
│  4. Wait 5 minutes                                      │
│  5. Repeat until remaining = 0                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Adjusting Processing Rate

### To Process Faster

**Option 1: Increase batch size**
```python
# app/config.py
PROCESS_BATCH_SIZE: int = 20  # Process 20 papers per run
```

**Option 2: Decrease interval**
```python
# app/config.py
PROCESS_INTERVAL_MINUTES: int = 2  # Run every 2 minutes
```

**Option 3: Both**
```python
# app/config.py
PROCESS_BATCH_SIZE: int = 20
PROCESS_INTERVAL_MINUTES: int = 2
# Result: 20 papers every 2 minutes = 600 papers/hour
```

### To Process Slower

```python
# app/config.py
PROCESS_BATCH_SIZE: int = 5
PROCESS_INTERVAL_MINUTES: int = 10
# Result: 5 papers every 10 minutes = 30 papers/hour
```

## Processing Rate Examples

| Batch Size | Interval | Papers/Hour | Papers/Day |
|------------|----------|-------------|------------|
| 5          | 10 min   | 30          | 720        |
| 10         | 5 min    | 120         | 2,880      |
| 20         | 5 min    | 240         | 5,760      |
| 10         | 2 min    | 300         | 7,200      |
| 20         | 2 min    | 600         | 14,400     |

**Current:** 10 papers every 5 minutes = **120 papers/hour** = **2,880 papers/day**

## Monitoring

### Check Scheduler Status
```bash
./paper jobs scheduler
```

### Check Processing Status
```bash
./paper jobs status
```

### View Job History
```bash
./paper jobs history --job-type process
```

### Watch Logs
```bash
# If running with uvicorn
tail -f backend.log

# Or check application logs
./paper jobs stats
```

## Manual Scraping

### Trigger Daily Scraping Now (Don't Wait for 6 AM)
```bash
# Scrape all sources (bioRxiv + PubMed longread)
./paper jobs trigger-scrape --source all

# Or use API
curl -X POST "http://localhost:8000/jobs/scrape?source=biorxiv&max_results=1000"
curl -X POST "http://localhost:8000/jobs/scrape?source=pubmed&max_results=1000&query=longread"
```

### Scrape Specific Sources
```bash
# bioRxiv only
./paper scrape biorxiv --max-results 1000

# PubMed with custom query
./paper scrape pubmed --query "longread" --max-results 1000

# PubMed with different query
./paper scrape pubmed --query "nanopore" --max-results 500
```

## Manual Processing

### Process Immediately (Don't Wait for Scheduler)
```bash
# Process 10 papers now
./paper jobs trigger-process --limit 10 --sync

# Process 50 papers now
./paper jobs trigger-process --limit 50 --sync

# Process in background
./paper jobs trigger-process --limit 100
```

### Process Specific Papers
```bash
./paper papers process --ids "1,2,3,4,5"
```

## Troubleshooting

### Scheduler Not Running
```bash
# Check if API is running
curl http://localhost:8000/jobs/scheduler/status

# Start API (scheduler starts automatically)
uvicorn app.main:app --reload
```

### Processing Too Slow
1. Increase `PROCESS_BATCH_SIZE`
2. Decrease `PROCESS_INTERVAL_MINUTES`
3. Check for errors: `./paper jobs history`

### Processing Too Fast (API Slow)
1. Decrease `PROCESS_BATCH_SIZE`
2. Increase `PROCESS_INTERVAL_MINUTES`

### Papers Not Being Processed
```bash
# Check unprocessed count
./paper jobs status

# Check for errors
./paper jobs history --limit 50

# Try manual processing
./paper jobs trigger-process --limit 1 --sync
```

## Environment Variables

You can override config via environment variables:

```bash
# .env file
PROCESS_BATCH_SIZE=20
PROCESS_INTERVAL_MINUTES=3
```

Then restart the API:
```bash
uvicorn app.main:app --reload
```

## Best Practices

1. **Start Conservative**
   - Use default: 10 papers every 5 minutes
   - Monitor performance
   - Adjust as needed

2. **Monitor Regularly**
   - Check `./paper jobs status` daily
   - Review `./paper jobs history` for errors
   - Watch API performance

3. **Scale Gradually**
   - Increase batch size first
   - Then decrease interval if needed
   - Don't exceed API capacity

4. **Consider API Load**
   - Processing uses Google Gemini API
   - Each paper = 2 API calls (classify + summarize)
   - 10 papers = 20 API calls
   - Monitor API rate limits

## Summary

✅ **Current Configuration:**
- **Batch Size:** 10 papers
- **Interval:** 5 minutes
- **Rate:** 120 papers/hour
- **Automatic:** Runs until all papers processed

✅ **To Change:**
1. Edit `app/config.py`
2. Restart API: `uvicorn app.main:app --reload`
3. Verify: `./paper jobs scheduler`

✅ **To Monitor:**
- `./paper jobs status` - Current status
- `./paper jobs scheduler` - Scheduled jobs
- `./paper jobs history` - Execution history
