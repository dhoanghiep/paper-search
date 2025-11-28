# Daily Scraping Configuration

## ✅ Current Setup

The scheduler automatically fetches papers **every day at 6:00 AM**:

### 📚 bioRxiv
- **What:** All papers from bioRxiv
- **Time Range:** Last 7 days
- **Max Papers:** Up to 1000 papers
- **Duplicates:** Automatically skipped

### 🔬 PubMed
- **What:** Papers matching keyword "longread"
- **Max Papers:** Up to 1000 papers
- **Duplicates:** Automatically skipped

## 📊 Expected Daily Volume

### bioRxiv
- **Average:** ~100-200 new papers per day
- **Peak:** Up to 500 papers per day
- **7-day backlog:** ~700-1400 papers (first run)

### PubMed (longread)
- **Average:** ~10-50 papers per day
- **Varies by:** Research trends, publication cycles

## 🔧 Configuration

**File:** `app/config.py`

```python
# Daily Scraping Configuration
BIORXIV_SCRAPE_MAX: int = 1000      # Max papers to fetch
BIORXIV_DAYS_BACK: int = 7          # Look back 7 days
PUBMED_SCRAPE_QUERY: str = "longread"  # Search keyword
PUBMED_SCRAPE_MAX: int = 1000       # Max papers to fetch
```

## 🎯 How to Change

### Change PubMed Keyword

```python
# app/config.py

# Single keyword
PUBMED_SCRAPE_QUERY: str = "nanopore"

# Multiple keywords (OR)
PUBMED_SCRAPE_QUERY: str = "longread OR nanopore OR pacbio"

# Multiple keywords (AND)
PUBMED_SCRAPE_QUERY: str = "longread AND sequencing"

# Complex query
PUBMED_SCRAPE_QUERY: str = "(longread OR nanopore) AND genomics"
```

### Change bioRxiv Time Range

```python
# app/config.py

# Last 3 days (fewer papers)
BIORXIV_DAYS_BACK: int = 3

# Last 14 days (more papers)
BIORXIV_DAYS_BACK: int = 14

# Last 30 days (maximum)
BIORXIV_DAYS_BACK: int = 30
```

### Change Max Papers

```python
# app/config.py

# Fetch more papers
BIORXIV_SCRAPE_MAX: int = 2000
PUBMED_SCRAPE_MAX: int = 2000

# Fetch fewer papers
BIORXIV_SCRAPE_MAX: int = 500
PUBMED_SCRAPE_MAX: int = 500
```

## 🚀 Manual Scraping

### Trigger Scraping Now (Don't Wait for 6 AM)

```bash
# Scrape bioRxiv
./paper scrape biorxiv --max-results 1000

# Scrape PubMed with longread
./paper scrape pubmed --query "longread" --max-results 1000

# Scrape both
./paper jobs trigger-scrape --source all
```

### Test Different Queries

```bash
# Try nanopore
./paper scrape pubmed --query "nanopore" --max-results 100

# Try single-cell
./paper scrape pubmed --query "single-cell" --max-results 100

# Try CRISPR
./paper scrape pubmed --query "CRISPR" --max-results 100
```

## 📈 Processing Pipeline

```
6:00 AM Daily:
┌─────────────────────────────────────────┐
│ 1. Scrape bioRxiv (all papers, 7 days) │
│    → Fetch up to 1000 papers            │
│    → Skip duplicates                    │
│    → Save new papers to database        │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 2. Scrape PubMed (keyword: longread)   │
│    → Fetch up to 1000 papers            │
│    → Skip duplicates                    │
│    → Save new papers to database        │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 3. Processing (every 5 minutes)         │
│    → Process 10 papers at a time        │
│    → Classify (assign categories)       │
│    → Summarize (extract key info)       │
│    → Continue until all processed       │
└─────────────────────────────────────────┘
```

## 📊 Monitoring

### Check What Was Scraped Today

```bash
# View recent papers
./paper papers list --limit 50 --total

# Check by source
./paper papers list --limit 20 | grep bioRxiv
./paper papers list --limit 20 | grep PMID
```

### Check Processing Status

```bash
# Overall status
./paper jobs status

# Scheduler status
./paper jobs scheduler

# Job history
./paper jobs history --limit 20
```

### View Logs

```bash
# Check scraping logs
tail -f backend.log | grep "Scraping"

# Check processing logs
tail -f backend.log | grep "Processing"
```

## 🎯 Common Scenarios

### Scenario 1: Too Many Papers

**Problem:** Scraping 1000+ papers daily, processing can't keep up

**Solution:**
```python
# Reduce time range
BIORXIV_DAYS_BACK: int = 3  # Only last 3 days

# Or reduce max papers
BIORXIV_SCRAPE_MAX: int = 500
```

### Scenario 2: Too Few Papers

**Problem:** Not enough papers being scraped

**Solution:**
```python
# Increase time range
BIORXIV_DAYS_BACK: int = 14  # Last 14 days

# Or add more PubMed keywords
PUBMED_SCRAPE_QUERY: str = "longread OR nanopore OR pacbio"
```

### Scenario 3: Different Research Focus

**Problem:** Want papers on different topics

**Solution:**
```python
# Change PubMed query
PUBMED_SCRAPE_QUERY: str = "CRISPR"
# or
PUBMED_SCRAPE_QUERY: str = "single-cell AND RNA-seq"
# or
PUBMED_SCRAPE_QUERY: str = "cancer AND genomics"
```

## 🔄 After Changing Configuration

1. **Edit config:**
   ```bash
   nano app/config.py
   ```

2. **Restart API:**
   ```bash
   # Stop current process (Ctrl+C)
   # Then restart
   uvicorn app.main:app --reload
   ```

3. **Verify:**
   ```bash
   ./paper jobs scheduler
   ```

4. **Test manually (optional):**
   ```bash
   ./paper jobs trigger-scrape --source all
   ```

## ✅ Summary

**Current Configuration:**
- ✅ **bioRxiv:** All papers, last 7 days, up to 1000
- ✅ **PubMed:** Keyword "longread", up to 1000
- ✅ **Schedule:** Daily at 6:00 AM
- ✅ **Processing:** 10 papers every 5 minutes
- ✅ **Automatic:** No manual intervention needed

**To Customize:**
1. Edit `app/config.py`
2. Change `PUBMED_SCRAPE_QUERY` for different keywords
3. Change `BIORXIV_DAYS_BACK` for different time range
4. Restart API
5. Monitor with `./paper jobs status`
