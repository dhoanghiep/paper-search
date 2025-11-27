# CLI Usage Guide

**Created:** 2025-11-27  
**Status:** Implemented and tested

---

## Installation

```bash
# Install dependencies
pip install click rich

# Make executable
chmod +x paper
```

---

## Usage

### Run CLI

```bash
# Using executable
./paper --help

# Or with venv python
venv/bin/python paper --help
```

---

## Commands

### 1. Scraping

**Scrape from arXiv:**
```bash
./paper scrape arxiv --max-results 10
```

**Scrape from bioRxiv:**
```bash
./paper scrape biorxiv --max-results 10
```

**Scrape from PubMed:**
```bash
./paper scrape pubmed --max-results 10 --query "machine learning"
```

**Scrape from all sources:**
```bash
./paper scrape all --max-results 10
```

---

### 2. Processing

**Process unprocessed papers:**
```bash
./paper process --limit 10
```

This will:
- Find papers without summaries
- Classify them using MCP classification server
- Summarize them using MCP summarization server
- Update database

---

### 3. Listing & Search

**List all papers:**
```bash
./paper list --limit 20
```

**List only unprocessed papers:**
```bash
./paper list --unprocessed
```

**Search papers:**
```bash
./paper search "neural networks"
./paper search "cancer treatment"
```

---

### 4. Viewing

**Show paper details:**
```bash
./paper show 1
```

**Show with full abstract:**
```bash
./paper show 1 --full
```

**Show statistics:**
```bash
./paper stats
```

Output:
```
     Database Statistics      
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric             ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Papers       │ 10    │
│ Processed Papers   │ 0     │
│ Unprocessed Papers │ 10    │
│ Papers This Week   │ 10    │
│ Categories         │ 0     │
└────────────────────┴───────┘
```

---

### 5. Reports

**Generate daily report:**
```bash
./paper report daily
```

**Save to file:**
```bash
./paper report daily --save daily-report.md
./paper report weekly --save weekly-report.md
```

---

### 6. Jobs

**Check job status:**
```bash
./paper jobs status
```

---

## Example Workflows

### Daily Workflow

```bash
# 1. Scrape new papers
./paper scrape all --max-results 20

# 2. Check what we got
./paper stats

# 3. Process them
./paper process --limit 20

# 4. View results
./paper list

# 5. Generate report
./paper report daily --save daily-$(date +%Y%m%d).md
```

### Search & Explore

```bash
# Search for papers
./paper search "deep learning"

# View specific paper
./paper show 5 --full

# List unprocessed
./paper list --unprocessed
```

### Quick Stats

```bash
# Database overview
./paper stats

# Job status
./paper jobs status
```

---

## Output Examples

### List Command
```
                                Papers (5 shown)                                 
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓
┃ ID ┃ Title                                              ┃ Source  ┃ Processed ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━┩
│ 9  │ PhysChoreo: Physics-Controllable Video Generation  │ bioRxiv │ ✗         │
│ 8  │ On the rigidity of special and exceptional geometr │ bioRxiv │ ✗         │
│ 7  │ Can Vibe Coding Beat Graduate CS Students?         │ bioRxiv │ ✗         │
└────┴────────────────────────────────────────────────────┴─────────┴───────────┘
```

### Show Command
```
Paper #1
Neural Networks for Image Classification

ID: 2311.12345
Authors: John Doe, Jane Smith
Published: 2024-11-20
URL: https://arxiv.org/pdf/2311.12345

Abstract: This paper presents a novel approach to...

Summary: The paper introduces a new neural network architecture...
```

### Stats Command
```
     Database Statistics      
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric             ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Papers       │ 10    │
│ Processed Papers   │ 0     │
│ Unprocessed Papers │ 10    │
│ Papers This Week   │ 10    │
│ Categories         │ 0     │
└────────────────────┴───────┘
```

---

## Features

✅ **Beautiful Output**
- Rich tables with borders
- Color-coded status (✓ ✗ ⚠)
- Formatted text

✅ **Progress Indicators**
- Shows progress when scraping multiple sources
- Real-time feedback

✅ **Error Handling**
- Clear error messages
- Graceful failures

✅ **Offline Support**
- Works without API running
- Direct database access

---

## Tips

**Alias for convenience:**
```bash
# Add to ~/.bashrc or ~/.zshrc
alias paper='cd /workshop/paper-search && venv/bin/python paper'
```

**Chain commands:**
```bash
./paper scrape all --max-results 5 && ./paper process --limit 5 && ./paper stats
```

**Save reports regularly:**
```bash
./paper report daily --save reports/daily-$(date +%Y%m%d).md
```

---

## Troubleshooting

**Module not found:**
```bash
# Ensure dependencies installed
pip install click rich
```

**Database connection error:**
```bash
# Check .env file has correct DATABASE_URL
cat .env | grep DATABASE_URL
```

**Permission denied:**
```bash
# Make executable
chmod +x paper
```

---

## Next Enhancements

Possible future additions:
- Tab completion
- Interactive mode
- Export to CSV/JSON
- Batch operations
- Configuration file
- Color themes
