# Paper Search - Automated Research Paper Management

Multi-source research paper aggregator with AI-powered classification and summarization.

## Features

- **Multi-Source Scraping**: arXiv, bioRxiv, PubMed
- **AI Processing**: Auto-classification and summarization via AWS Bedrock
- **MCP Servers**: 6 JSON-RPC 2.0 servers for extensibility
- **Automated Workflows**: Scheduled scraping, processing, and reporting
- **CLI Interface**: Beautiful terminal interface with Rich
- **REST API**: FastAPI backend with Swagger UI
- **Web Interface**: Vanilla JavaScript frontend

## Quick Start

### Installation

```bash
# Clone repository
git clone <repo-url>
cd paper-search

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Usage

**CLI:**
```bash
# Scrape papers
./paper scrape arxiv --max-results 10
./paper scrape all

# Process papers
./paper process --limit 10

# View papers
./paper list
./paper show 1
./paper stats

# Generate reports
./paper report daily --save report.md
```

**API:**
```bash
# Start backend
./start.sh

# Access API
curl http://localhost:8000/jobs/status
curl http://localhost:8000/papers/

# Swagger UI
open http://localhost:8000/docs
```

**Web Interface:**
```
http://localhost:5173
```

## Architecture

```
paper-search/
├── app/                    # FastAPI backend
│   ├── agents/            # Scrapers (arXiv, bioRxiv, PubMed)
│   ├── routers/           # API endpoints
│   ├── orchestrator.py    # MCP coordination
│   ├── pipeline.py        # Auto-processing
│   ├── scheduler.py       # Automated jobs
│   └── cli_main.py        # CLI interface
├── mcp_servers/           # MCP servers (6 total)
│   ├── arxiv/
│   ├── database/
│   ├── classification/
│   ├── summarization/
│   ├── reports/
│   └── email/
├── frontend/              # Web interface
├── docs/                  # Documentation
└── paper                  # CLI executable
```

## Documentation

- **PROGRESS.md** - Development progress tracker
- **PROJECT_STATUS.md** - Current project state
- **FINAL_STATUS.md** - Project completion summary
- **docs/** - Detailed guides and plans

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **MCP**: JSON-RPC 2.0, AWS Bedrock (Claude 3 Haiku)
- **CLI**: Click, Rich
- **Frontend**: Vanilla JavaScript, CSS3
- **Automation**: APScheduler
- **APIs**: arXiv, bioRxiv, PubMed

## Automated Workflows

- **6:00 AM**: Scrape all sources (30 papers)
- **Every 2 hours**: Process unprocessed papers
- **9:00 AM**: Generate and email daily report

## API Endpoints

- `POST /jobs/scrape` - Scrape papers
- `POST /jobs/process` - Process papers
- `GET /jobs/status` - Job status
- `GET /papers/` - List papers
- `GET /papers/{id}` - Get paper
- `POST /jobs/report/daily` - Generate report

## Development

```bash
# Run tests
pytest

# Start development server
uvicorn app.main:app --reload

# Access logs
tail -f backend.log
```

## License

MIT

## Status

✅ Production ready - Core features complete (85%)
