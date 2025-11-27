# Phase 4 Quick Start

**Created:** 2025-11-27  
**Goal:** Test the integration layer

---

## What Was Just Created

✅ **Orchestrator** (`app/orchestrator.py`)
- MCPClient class to call MCP servers
- `process_paper()` function - classify + summarize

✅ **Pipeline** (`app/pipeline.py`)
- `process_new_papers()` - auto-process unprocessed papers
- Finds papers without summaries
- Processes them through orchestrator

✅ **Jobs API** (`app/routers/jobs.py`)
- POST /jobs/scrape - Manual scrape
- POST /jobs/process - Process papers (background)
- POST /jobs/process-sync - Process papers (sync)
- GET /jobs/status - Check processing status

---

## Test It Now

### 1. Restart Backend (to load new routes)

```bash
cd /workshop/paper-search
./stop.sh
./start.sh
```

### 2. Check Job Status

```bash
curl http://localhost:8000/jobs/status
```

Expected output:
```json
{
  "total_papers": 10,
  "processed": 0,
  "unprocessed": 10
}
```

### 3. Process One Paper (Test)

```bash
curl -X POST http://localhost:8000/jobs/process-sync?limit=1
```

This will:
- Find first unprocessed paper
- Classify it (using classification MCP)
- Summarize it (using summarization MCP)
- Update database

### 4. Check Status Again

```bash
curl http://localhost:8000/jobs/status
```

Should show:
```json
{
  "total_papers": 10,
  "processed": 1,
  "unprocessed": 9
}
```

### 5. Process All Papers

```bash
curl -X POST http://localhost:8000/jobs/process-sync?limit=10
```

---

## View Results

### Via API
```bash
curl http://localhost:8000/papers/1
```

Look for `summary` field - should be populated!

### Via Frontend
```
http://localhost:5173
```

Click on any paper to see its summary.

---

## Troubleshooting

**Error: "MCP call failed"**
- Check MCP servers are executable: `chmod +x mcp_servers/*/server.py`
- Check Python path in orchestrator.py

**Error: "AWS credentials not found"**
- Summarization needs AWS Bedrock
- Set AWS credentials: `aws configure`
- Or skip summarization for now

**Backend won't restart**
- Kill old process: `pkill -f uvicorn`
- Check logs: `cat backend.log`

---

## Next Steps

Once basic processing works:

1. **Add Scheduling** - Auto-process daily
2. **Add Reports** - Generate daily reports
3. **Add Email** - Send notifications
4. **Add Error Handling** - Retry failed papers

See `PHASE4_GUIDE.md` for full implementation.

---

## Quick Commands

```bash
# Process all papers
curl -X POST http://localhost:8000/jobs/process-sync?limit=10

# Scrape more papers
curl -X POST "http://localhost:8000/jobs/scrape?max_results=5"

# Check status
curl http://localhost:8000/jobs/status

# View API docs
open http://localhost:8000/docs
```
