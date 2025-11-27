# Phase 4: Integration & Automation Guide

**Start Date:** 2025-11-27  
**Goal:** Connect all MCP servers into automated workflows

---

## Overview

Build the orchestration layer that connects:
- ArXiv scraper → Database → Classification → Summarization → Reports → Email

---

## Step 1: Create Orchestrator Service (30 min)

**File:** `app/orchestrator.py`

**Purpose:** Coordinate MCP server calls

**Tasks:**
- [ ] Create MCPClient class to call MCP servers via stdin/stdout
- [ ] Implement paper processing pipeline
- [ ] Add error handling and logging

**Test:** Process one paper through full pipeline

---

## Step 2: Scheduled Scraping (15 min)

**File:** `app/scheduler.py`

**Purpose:** Auto-scrape arXiv daily

**Tasks:**
- [ ] Use APScheduler for cron-like scheduling
- [ ] Schedule daily scrape at specific time
- [ ] Configure max papers per run

**Test:** Trigger manual scrape, verify papers added

---

## Step 3: Auto-Processing Pipeline (20 min)

**File:** `app/pipeline.py`

**Purpose:** Process new papers automatically

**Workflow:**
```
New Paper → Classify → Summarize → Store Results
```

**Tasks:**
- [ ] Detect unprocessed papers
- [ ] Call classification MCP
- [ ] Call summarization MCP
- [ ] Update database with results

**Test:** Add raw paper, verify it gets classified and summarized

---

## Step 4: Daily Report Generation (15 min)

**File:** `app/reports_job.py`

**Purpose:** Generate and store daily reports

**Tasks:**
- [ ] Schedule daily report at 9 AM
- [ ] Call reports MCP server
- [ ] Save to database
- [ ] Optional: Save to file

**Test:** Generate report manually, check output

---

## Step 5: Email Notifications (20 min)

**File:** `app/notifications.py`

**Purpose:** Send email alerts

**Tasks:**
- [ ] Configure SMTP in .env
- [ ] Send daily digest
- [ ] Send new paper alerts (optional)

**Test:** Send test email to yourself

---

## Step 6: API Endpoints for Jobs (15 min)

**File:** `app/routers/jobs.py`

**Purpose:** Trigger jobs via API

**Endpoints:**
- POST /jobs/scrape - Manual scrape
- POST /jobs/process - Process unprocessed papers
- POST /jobs/report - Generate report
- GET /jobs/status - Check job status

**Test:** Call endpoints via curl or Swagger UI

---

## Step 7: Background Task Runner (15 min)

**File:** `app/worker.py`

**Purpose:** Run jobs in background

**Tasks:**
- [ ] Set up FastAPI BackgroundTasks
- [ ] Or use Celery for production
- [ ] Add job queue

**Test:** Trigger long-running job, verify non-blocking

---

## Implementation Order

### Quick Win (1 hour)
1. **Orchestrator** - Core integration
2. **Pipeline** - Auto-processing
3. **API endpoints** - Manual triggers

### Full Automation (2 hours)
4. **Scheduler** - Cron jobs
5. **Reports** - Daily generation
6. **Email** - Notifications

---

## File Structure

```
app/
├── orchestrator.py      # MCP client & coordination
├── pipeline.py          # Paper processing workflow
├── scheduler.py         # APScheduler setup
├── reports_job.py       # Report generation job
├── notifications.py     # Email sending
├── worker.py            # Background tasks
└── routers/
    └── jobs.py          # Job trigger endpoints
```

---

## Dependencies to Add

```txt
apscheduler>=3.10.0      # Scheduling
aiosmtplib>=3.0.0        # Async email
```

---

## Testing Strategy

**Unit Tests:**
- Test each MCP client call
- Test pipeline steps individually

**Integration Tests:**
- Full pipeline: scrape → classify → summarize
- Report generation with real data
- Email sending (use test SMTP)

**Manual Tests:**
- Trigger jobs via API
- Check logs for errors
- Verify database updates

---

## Success Criteria

- [ ] Can scrape papers on schedule
- [ ] New papers auto-classified
- [ ] New papers auto-summarized
- [ ] Daily reports generated
- [ ] Email notifications sent
- [ ] All jobs accessible via API
- [ ] Error handling in place
- [ ] Logging configured

---

## Quick Start Commands

```bash
# Install new dependencies
pip install apscheduler aiosmtplib

# Start with orchestrator
python -c "from app.orchestrator import process_paper; process_paper(1)"

# Test pipeline
python -c "from app.pipeline import process_new_papers; process_new_papers()"

# Generate report
python -c "from app.reports_job import generate_daily_report; generate_daily_report()"
```

---

## Next Steps

1. Start with **Step 1: Orchestrator** - this is the foundation
2. Test with one paper through full pipeline
3. Add API endpoints for manual control
4. Then add scheduling for automation

**Estimated Time:** 2-3 hours for full implementation
