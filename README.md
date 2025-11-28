# Paper Search - Automated Research Paper Management

Multi-source research paper aggregator with AI-powered classification, summarization, and reporting.

## 🎯 Features

### Core Functionality
- **Multi-Source Scraping**: arXiv, bioRxiv, PubMed
- **AI Processing**: Auto-classification (18 categories) and summarization via Google Gemini
- **Smart Filtering**: Filter by date range, categories (AND/OR logic), processing status
- **LLM Reports**: Generate comprehensive research reports with AI analysis
- **MCP Architecture**: 5 JSON-RPC 2.0 servers for extensibility
- **CLI Interface**: Beautiful terminal interface with Rich
- **REST API**: FastAPI backend with Swagger UI
- **Web Interface**: Vanilla JavaScript frontend

### Advanced Features
- Abstract-first summarization (skips LLM when abstract available)
- Withdrawn paper filtering
- Multiple category classification per paper
- PubMed search and selective fetch
- Daily paper tracking by topic
- Duplicate detection
- Batch processing

## 📊 Current Status

**Database:** 81 papers | 60 processed | 15 categories
**Sources:** bioRxiv (primary), PubMed (secondary), arXiv (available)
**Categories:** methods, transcriptomics, genomics, AI, cancer, immunology, splicing, and more

## 🚀 Quick Start

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
# Edit .env with your GOOGLE_API_KEY
```

### Basic Usage

```bash
# Scrape papers
./paper scrape biorxiv --max-results 50
./paper papers add "10.1101/2024.11.28.625751"  # Add specific paper

# PubMed operations
./paper pubmed daily --topic "bioinformatics"
./paper pubmed search "CRISPR gene editing" --max-results 20
./paper pubmed fetch "41280279,41208948"

# Process papers (classify + summarize)
./paper papers process --limit 10
./paper papers process --ids "1,2,3"  # Process specific papers

# View papers
./paper papers list --limit 20 --total
./paper papers list --category genomics --category transcriptomics
./paper papers show 1
./paper categories list

# Generate reports
./paper report generate --start-date 2025-11-20 --end-date 2025-11-28 --category genomics --save report.md

# Statistics
./paper categories stats
```

## 📁 Architecture

```
paper-search/
├── app/                    # FastAPI backend
│   ├── agents/            # Scrapers (arXiv, bioRxiv, PubMed)
│   │   ├── base_scraper.py    # Base class for all scrapers
│   │   ├── scraper.py         # ArxivScraper
│   │   ├── biorxiv_scraper.py # BiorxivScraper
│   │   └── pubmed_scraper.py  # PubmedScraper
│   ├── routers/           # API endpoints
│   ├── orchestrator.py    # MCP coordination
│   ├── pipeline.py        # Auto-processing
│   ├── scheduler.py       # Automated jobs
│   └── cli_main.py        # CLI interface (800+ lines)
├── mcp_servers/           # MCP servers (5 total)
│   ├── classification/   # AI classification (18 categories)
│   ├── database/         # Database operations
│   ├── summarization/    # AI summarization
│   ├── reports/          # Report generation with LLM
│   └── email/            # Email notifications
├── frontend/              # Web interface
│   ├── js/               # Components (Papers, Categories, Dashboard)
│   └── css/              # Styling
└── paper                  # CLI executable
```

## 🔧 CLI Commands

### Scraping
```bash
./paper scrape biorxiv --max-results 50
./paper scrape arxiv --max-results 10
./paper scrape pubmed --query "cancer" --max-results 20
./paper scrape pubmed --search-only --query "CRISPR"
./paper scrape pubmed --fetch-ids "41280279,41208948"
./paper scrape pubmed --daily --topic "bioinformatics"
./paper scrape pubmed --daily --date 2024/11/28 --topic "CRISPR"
./paper scrape all --max-results 10
```

### PubMed Operations (Legacy - Deprecated)
```bash
# Old commands still work but show deprecation warning
./paper pubmed search "query" --max-results 20
./paper pubmed fetch "PMID1,PMID2,PMID3"
./paper pubmed daily --topic "topic"
```

### Paper Management
```bash
./paper papers add <doi-or-url>                   # Add specific paper
./paper papers list --limit 20 --total
./paper papers list --category genomics
./paper papers list --category genomics --category AI  # AND logic
./paper papers list --unprocessed
./paper papers show <paper-id>
./paper papers search "keyword"
./paper papers process --limit 10                 # Process next 10 unprocessed
./paper papers process --ids "1,2,3"              # Process specific papers
```

### Categories & Statistics
```bash
./paper categories list
./paper categories stats
```

### Reports
```bash
./paper report generate \
  --start-date 2025-11-20 \
  --end-date 2025-11-28 \
  --category genomics \
  --category transcriptomics \
  --save report.md

./paper report daily --save daily.md
./paper report weekly --save weekly.md
```

### Exploration Tools
```bash
./paper explore tldr <paper-id>       # One-sentence summary
./paper explore points <paper-id>     # Key points
./paper explore detailed <paper-id>   # Detailed analysis
./paper explore all <paper-id>        # All analysis
```

## 🤖 AI Classification Categories

**18 Categories:**
- **Methods**: algorithms, tools, frameworks, benchmarks
- **Genomics**: genome sequencing, DNA analysis, variants
- **Transcriptomics**: RNA-seq, gene expression
- **AI**: machine learning, deep learning, neural networks
- **Cancer**: oncology, tumors, cancer biology
- **Immunology**: immune system, T cells, antibodies
- **Epigenetics**: DNA methylation, chromatin
- **Spatial**: spatial transcriptomics, tissue mapping
- **Assembly**: genome assembly, scaffolding
- **Alignment**: sequence alignment, mapping
- **Isoforms**: alternative splicing, transcript variants
- **Splicing**: RNA splicing, splice sites
- **Single-cell**: scRNA-seq, cell types
- **Long-read**: nanopore, PacBio
- **Microbial**: bacteria, microbiome
- **Ecology**: ecosystems, biodiversity
- **Dataset**: new datasets, databases
- **Benchmark**: comparison studies, evaluations

## 🌐 API Endpoints

**Backend:** http://localhost:8000

```bash
# Papers
GET  /papers/              # List all papers
GET  /papers/{id}          # Get paper details
POST /papers/scrape        # Trigger scraping

# Categories
GET  /categories/          # List categories with counts

# Jobs
POST /jobs/scrape          # Scrape papers
POST /jobs/process         # Process papers
GET  /jobs/status          # Job status
POST /jobs/report/daily    # Generate report

# API Documentation
GET  /docs                 # Swagger UI
```

## 🔄 Automated Workflows

Configured in `app/scheduler.py`:
- **6:00 AM**: Scrape all sources (30 papers)
- **Every 2 hours**: Process unprocessed papers
- **9:00 AM**: Generate and email daily report

## 🛠️ Technology Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite/PostgreSQL
- **AI**: Google Gemini 2.0 Flash (via MCP)
- **MCP**: JSON-RPC 2.0 protocol
- **CLI**: Click, Rich
- **Frontend**: Vanilla JavaScript, CSS3
- **Automation**: APScheduler
- **APIs**: arXiv, bioRxiv, PubMed E-utilities

## 📝 Configuration

**Required in `.env`:**
```bash
DATABASE_URL=sqlite:///./paper_search.db
GOOGLE_API_KEY=your-google-api-key-here
ARXIV_API_BASE=http://export.arxiv.org/api/query
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

## 🎨 Key Features Detail

### Abstract-First Summarization
- Uses paper abstract directly when available (bioRxiv, PubMed)
- Only calls LLM for papers without abstracts
- Saves API costs and processing time

### Multi-Category Classification
- Papers can have multiple categories
- AND logic for filtering (papers must have ALL specified categories)
- AI-powered classification using Google Gemini

### LLM Report Generation
- Analyzes multiple papers across date ranges
- Filters by categories
- Generates comprehensive markdown reports with:
  - Executive Summary
  - Key Themes and Trends
  - Notable Findings by Category
  - Emerging Research Directions
  - Conclusion

### Withdrawn Paper Filtering
- Automatically skips papers with "WITHDRAWN:" prefix
- Applied during scraping and manual additions

## 📚 Documentation

- **PROGRESS.md** - Development progress tracker
- **PROJECT_STATUS.md** - Current project state
- **FINAL_STATUS.md** - Project completion summary
- **docs/** - Detailed guides and plans

## 🚦 Development

```bash
# Run tests
pytest

# Start development server
uvicorn app.main:app --reload

# Access logs
tail -f backend.log

# Database operations
./paper categories stats
./paper papers list --total
```

## 📊 Example Workflows

### Daily Research Monitoring
```bash
# Morning: Get today's papers
./paper pubmed daily --topic "bioinformatics"
./paper scrape biorxiv --max-results 50

# Process new papers
./paper papers process --limit 50

# Review by category
./paper papers list --category genomics --category AI --total
```

### Weekly Report Generation
```bash
# Generate comprehensive report
./paper report generate \
  --start-date 2025-11-21 \
  --end-date 2025-11-28 \
  --category genomics \
  --category transcriptomics \
  --save weekly_report.md
```

### Targeted Research
```bash
# Search PubMed
./paper pubmed search "CRISPR base editing" --max-results 50

# Fetch specific papers
./paper pubmed fetch "41280279,41208948,41141487"

# Process and review
./paper papers process --ids "62,63,64"
./paper papers show 62
```

## 🔐 Security Notes

- Never commit `.env` file
- Use app passwords for email
- Keep API keys secure
- Database contains research data only (no PII)

## 📄 License

MIT

## 🎯 Status

✅ **Production Ready** - Core features complete (95%)

**Recent Updates:**
- BaseScraper class eliminates code duplication
- Unified PubMed commands under scrape group
- Removed redundant arXiv MCP server
- LLM-based report generation
- PubMed daily tracking
- Multiple category filtering (AND logic)
- Abstract-first summarization
- Withdrawn paper filtering
- Enhanced CLI with 15+ commands

**Next Steps:**
- Additional data sources
- Advanced analytics
- Export formats (PDF, CSV)
- Collaboration features
