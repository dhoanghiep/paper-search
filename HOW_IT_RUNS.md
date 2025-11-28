# How the Paper Search App Runs

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                                  │
│  arXiv API  │  bioRxiv API  │  PubMed E-utilities               │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SCRAPERS (app/agents/)                        │
│  • scraper.py (arXiv)                                           │
│  • biorxiv_scraper.py (bioRxiv)                                 │
│  • pubmed_scraper.py (PubMed)                                   │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                         │
│  Papers Table: id, title, abstract, authors, pdf_url, summary   │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR (app/orchestrator.py)                  │
│  Coordinates MCP servers for AI processing                       │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP SERVERS (6 total)                         │
│  1. Classification MCP  → Categorize papers                      │
│  2. Summarization MCP   → AWS Bedrock (Claude 3 Haiku)          │
│  3. Database MCP        → Query/manage papers                    │
│  4. Reports MCP         → Generate markdown reports              │
│  5. Email MCP           → Send notifications                     │
│  6. ArXiv MCP           → Direct arXiv queries                   │
└─────────────────────────────────────────────────────────────────┘
```

## Running Services

### Backend API (FastAPI)
- **URL:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Process:** uvicorn app.main:app --host 0.0.0.0 --port 8000

### Frontend
- **URL:** http://localhost:5173
- **Process:** python3 frontend/server.py

### Scheduler (APScheduler)
- **Embedded in backend**
- **Jobs:**
  - Daily 6 AM: Scrape 30 papers (10 from each source)
  - Every 2 hours: Process unprocessed papers
  - Daily 9 AM: Generate and email daily report

## Usage Examples

### 1. CLI Workflow

```bash
# Scrape papers from arXiv
./paper scrape arxiv --max-results 5

# List all papers
./paper list

# View paper details
./paper show 1

# Process papers (classify + summarize with AI)
./paper process --limit 2

# View processed paper with AI summary
./paper show 1

# Generate daily report
./paper report daily

# Check statistics
./paper stats
```

### 2. API Workflow

```bash
# Scrape from PubMed
curl -X POST "http://localhost:8000/jobs/scrape?source=pubmed&max_results=3&query=machine+learning"

# Get all papers
curl http://localhost:8000/papers/

# Get specific paper
curl http://localhost:8000/papers/1

# Process papers synchronously
curl -X POST "http://localhost:8000/jobs/process-sync?limit=5"

# Check job status
curl http://localhost:8000/jobs/status

# Generate daily report
curl -X POST "http://localhost:8000/jobs/report/daily"

# Check scheduler status
curl http://localhost:8000/jobs/scheduler/status
```

### 3. Web Interface

1. Open http://localhost:5173
2. View dashboard with statistics
3. Browse papers list
4. Click paper to view details
5. See AI-generated summaries for processed papers

## Complete Workflow Example

### Step 1: Scrape Papers
```bash
./paper scrape arxiv --max-results 5
```
**Output:**
```
Scraping 5 papers from arXiv...
✓ Successfully scraped 5 papers
```

### Step 2: View Papers
```bash
./paper list
```
**Output:**
```
                                Papers (5 shown)                                 
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓
┃ ID ┃ Title                                              ┃ Source  ┃ Processed ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━┩
│ 5  │ EvilGenie: A Reward Hacking Benchmark              │ bioRxiv │ ✗         │
│ 4  │ Escaping the Verifier: Learning to Reason via Demo │ bioRxiv │ ✗         │
│ 3  │ Through the telecom lens: Are all training samples │ bioRxiv │ ✗         │
│ 2  │ Intensity doubling for Brownian loop-soups in high │ bioRxiv │ ✗         │
│ 1  │ Matrix: Peer-to-Peer Multi-Agent Synthetic Data Ge │ bioRxiv │ ✓         │
└────┴────────────────────────────────────────────────────┴─────────┴───────────┘
```

### Step 3: Process Papers (AI Classification + Summarization)
```bash
./paper process --limit 2
```
**What happens:**
1. Orchestrator fetches unprocessed papers from database
2. For each paper:
   - Classification MCP analyzes title/abstract → assigns category
   - Summarization MCP calls AWS Bedrock → generates summary
   - Database MCP updates paper with results
3. Results stored in PostgreSQL

**Output:**
```
Processing up to 2 papers...
INFO:app.pipeline:Processing paper 1: Matrix: Peer-to-Peer Multi-Agent...
INFO:app.pipeline:Successfully processed paper 1
INFO:app.pipeline:Processing paper 2: Intensity doubling for Brownian...
INFO:app.pipeline:Successfully processed paper 2
✓ Processed: 2
```

### Step 4: View AI-Generated Summary
```bash
./paper show 1
```
**Output:**
```
Paper #1
Matrix: Peer-to-Peer Multi-Agent Synthetic Data Generation Framework

ID: 2511.21686v1
Authors: Dong Wang, Yang Li, Ansong Ni, ...
Published: 2025-11-26 18:59:28
URL: https://arxiv.org/pdf/2511.21686v1

Abstract: Synthetic data has become increasingly important for training...

Summary:
The paper presents Matrix, a decentralized framework for peer-to-peer 
multi-agent synthetic data generation, which eliminates the need for a 
centralized orchestrator and scales to tens of thousands of concurrent 
workflows. Matrix represents control and data flow as serialized messages 
passed through distributed queues, allowing each task to progress 
independently through lightweight agents while delegating compute-intensive 
operations to distributed services...
```

### Step 5: Generate Report
```bash
./paper report daily
```
**Output:** Markdown report with all papers from last 24 hours, including summaries

### Step 6: Check Statistics
```bash
./paper stats
```
**Output:**
```
     Database Statistics      
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric             ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Papers       │ 8     │
│ Processed Papers   │ 2     │
│ Unprocessed Papers │ 6     │
│ Papers This Week   │ 8     │
│ Categories         │ 0     │
└────────────────────┴───────┘
```

## MCP Server Communication

The orchestrator communicates with MCP servers via JSON-RPC 2.0:

```python
# Example: Classify a paper
request = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "classify_paper",
        "arguments": {
            "title": "Matrix: Peer-to-Peer Multi-Agent...",
            "abstract": "Synthetic data has become..."
        }
    },
    "id": 1
}

# MCP server responds with category
response = {
    "jsonrpc": "2.0",
    "result": {
        "content": [{
            "type": "text",
            "text": '{"category": "Machine Learning", "confidence": 0.95}'
        }]
    },
    "id": 1
}
```

## Automated Workflows

The scheduler runs these jobs automatically:

### Daily Scraping (6:00 AM)
```python
# Scrapes 10 papers from each source
scrape_arxiv(max_results=10)
scrape_biorxiv(max_results=10)
scrape_pubmed(max_results=10, query="AI")
```

### Processing (Every 2 hours)
```python
# Processes all unprocessed papers
process_new_papers(limit=50)
```

### Daily Report (9:00 AM)
```python
# Generates report and emails it
report = generate_daily_report()
send_email(to=recipients, subject="Daily Paper Digest", body=report)
```

## Technology Stack

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **MCP:** JSON-RPC 2.0 protocol, stdin/stdout communication
- **AI:** AWS Bedrock (Claude 3 Haiku) for summarization
- **Automation:** APScheduler for cron jobs
- **CLI:** Click + Rich for beautiful terminal UI
- **Frontend:** Vanilla JavaScript + CSS3

## Key Features

✅ Multi-source scraping (arXiv, bioRxiv, PubMed)
✅ AI-powered classification and summarization
✅ Automated daily workflows
✅ Beautiful CLI with Rich tables
✅ REST API with Swagger UI
✅ Web interface
✅ Email notifications
✅ Report generation
