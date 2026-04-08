# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

**All Python commands must use the conda base environment.** There is no `venv` in this project.

- Python interpreter: `/Users/danghiep/miniforge3/bin/python`
- CLI entry point: `/Users/danghiep/miniforge3/bin/python -m app.cli_main` (or `./paper` if it resolves correctly)
- Never use `source venv/bin/activate` or `python3` — always use the full miniforge path or prefix commands with the miniforge Python.

## What This Project Does

Paper Search is an AI-powered research paper aggregator that scrapes papers from bioRxiv, PubMed, and arXiv, then uses Google Gemini to classify them into 18 categories and generate summaries. It exposes a FastAPI REST backend, a Vanilla JS frontend, and a Click-based CLI.

## Commands

### Running the App

```bash
# Start both backend (port 8000) and frontend (port 5173)
./start.sh

# Stop all services
./stop.sh

# Backend only (dev mode with reload)
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend only
cd frontend && python3 server.py
```

Logs: `backend.log`, `frontend/frontend.log`

### CLI (`./paper`)

The CLI entry point is `./paper` (symlinks to `app/cli_main.py`).

```bash
# Scraping
./paper jobs trigger-scrape --source biorxiv
./paper jobs trigger-scrape --source pubmed
./paper scrape biorxiv --max-results 50       # deprecated but works

# Processing (classify + summarize via Gemini)
./paper papers process --limit 10
./paper papers process --ids "1,2,3"
./paper jobs trigger-process

# Viewing
./paper papers list --limit 20 --total
./paper papers list --category genomics --category transcriptomics
./paper papers show <id>
./paper papers search "CRISPR"
./paper categories list
./paper categories stats

# Reports
./paper report generate --start-date 2025-11-20 --end-date 2025-11-28 --category genomics --save report.md
./paper explore tldr --category AI       # Quick summaries
./paper explore all --category methods  # Full exploration

# Job status
./paper jobs status
```

### Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set GOOGLE_API_KEY in .env (required for AI features)
```

## Architecture

### Layer Overview

```
CLI (app/cli_main.py + app/cli/)
    ↓
FastAPI Routers (app/routers/)
    ↓
Services (app/services/)
    ↓
Orchestrator (app/orchestrator.py) — MCP client coordinator
    ↓
MCP Servers (mcp_servers/) — 5 standalone JSON-RPC 2.0 processes
    ↓
Database (SQLAlchemy via app/repositories/)
```

### Key Directories

| Path | Purpose |
|------|---------|
| `app/agents/` | Paper scrapers (`BaseScraper`, `ArxivScraper`, `BiorxivScraper`, `PubmedScraper`) |
| `app/cli/` | Click command groups: `scrape`, `papers`, `reports`, `jobs` |
| `app/routers/` | FastAPI endpoints for papers, categories, reports, jobs |
| `app/services/` | Business logic (`ClassificationService`, `SummarizationService`, `PaperService`) |
| `app/repositories/` | Data access layer (`PaperRepository`, `CategoryRepository`) |
| `app/orchestrator.py` | MCP client — spawns subprocess per MCP call, sends JSON-RPC |
| `app/scheduler.py` | APScheduler jobs: scrape @ 6 AM, process every 2h, report @ 9 AM |
| `app/models.py` | SQLAlchemy models: `Paper`, `Category`, `Report`, `JobHistory` |
| `app/config.py` | All configuration (env vars, rate limits, batch sizes, schedule times) |
| `mcp_servers/` | 5 MCP servers: classification, summarization, reports, email, database |
| `frontend/js/components/` | Vanilla JS components: Dashboard, PapersList, PaperDetail, Categories, Reports |

### MCP Architecture

MCP servers are **standalone Python subprocesses** called via JSON-RPC 2.0. The `MCPClient` in `app/orchestrator.py` spawns a new subprocess per call:

```python
subprocess.run([python, server.py], input=json_request, capture_output=True)
```

Each MCP server has a `tools/call` method accepting `{"name": "tool_name", "arguments": {...}}`.

### Data Flow: Scraping → Processing

1. Scraper fetches papers from external API (async, rate-limited)
2. `BaseScraper.save_papers()` deduplicates and inserts into DB
3. `process_papers_job()` picks unprocessed papers in batches of 10
4. `orchestrator.process_paper(id)` calls classification MCP → Gemini → 18-category assignment
5. Then calls summarization MCP → uses abstract directly if `len(abstract) >= 50`, else calls Gemini
6. Paper updated with categories and summary

### Database

- Default: SQLite (`paper_search.db`)
- Production: PostgreSQL via `DATABASE_URL` env var
- Schema: `Paper` ↔ `Category` many-to-many via `paper_categories` junction table; `Report` and `JobHistory` standalone
- No Alembic migrations in active use — schema created via `Base.metadata.create_all()`

### Configuration

All settings live in `app/config.py` as class attributes on `Settings`. Key values:
- `GOOGLE_API_KEY` — required for classification and summarization
- `BIORXIV_DAYS_BACK=30`, `BIORXIV_SCRAPE_MAX=1000`
- `PUBMED_SCRAPE_QUERY="longread"`
- `PROCESS_BATCH_SIZE=10`
- `MIN_ABSTRACT_LENGTH=50` — threshold for skipping LLM summarization

## Important Patterns

- **`scrape` commands are deprecated** — use `jobs trigger-scrape` instead
- **Abstract-first summarization**: papers with abstracts ≥ 50 chars skip LLM, using abstract directly as summary
- **Withdrawn paper filtering**: papers with titles starting with `"WITHDRAWN:"` are skipped during scraping
- **Multiple categories per paper**: classification assigns multiple categories; list filtering uses AND logic by default
