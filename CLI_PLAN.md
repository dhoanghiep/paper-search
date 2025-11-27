# CLI Interface Plan

**Created:** 2025-11-27  
**Goal:** Build comprehensive CLI for paper management

---

## Current CLI Status

**Existing:** `app/cli.py` - Basic scraping only
```bash
python -m app.cli --source=arxiv --max-results=10
```

**Limitations:**
- Only supports scraping
- No paper management
- No processing control
- No report viewing

---

## Proposed CLI Structure

### Option 1: Click-based CLI (Recommended)
```bash
paper-search scrape --source arxiv --max 10
paper-search process --limit 10
paper-search list --category "Machine Learning"
paper-search show 123
paper-search report daily
paper-search search "neural networks"
```

### Option 2: Typer-based CLI (Modern)
```bash
paper scrape arxiv --max-results 10
paper process --all
paper list --filter category=ML
paper show 123
paper report --type daily
```

---

## Commands to Implement

### 1. Scraping Commands
```bash
paper scrape arxiv [--max-results N]
paper scrape biorxiv [--max-results N]
paper scrape pubmed [--query "text"] [--max-results N]
paper scrape all [--max-results N]  # All sources
```

### 2. Processing Commands
```bash
paper process [--limit N]           # Process unprocessed papers
paper process --paper-id 123        # Process specific paper
paper process --all                 # Process all papers
paper classify 123                  # Classify specific paper
paper summarize 123                 # Summarize specific paper
```

### 3. Listing & Search Commands
```bash
paper list [--limit N]              # List all papers
paper list --unprocessed            # List unprocessed only
paper list --category "ML"          # Filter by category
paper list --source arxiv           # Filter by source
paper search "neural networks"      # Search by keyword
paper recent [--days N]             # Recent papers
```

### 4. View Commands
```bash
paper show 123                      # Show paper details
paper show 123 --full               # Show with full abstract
paper categories                    # List all categories
paper stats                         # Show statistics
```

### 5. Report Commands
```bash
paper report daily                  # Generate daily report
paper report weekly                 # Generate weekly report
paper report --save report.md       # Save to file
paper reports                       # List all reports
```

### 6. Job Commands
```bash
paper jobs status                   # Show job status
paper jobs scheduler                # Show scheduled jobs
paper jobs run scrape               # Run job manually
paper jobs run process              # Run processing job
```

### 7. Config Commands
```bash
paper config show                   # Show configuration
paper config set SMTP_HOST smtp.gmail.com
paper config test-email user@example.com
```

---

## Implementation Plan

### Phase 1: Core CLI Framework (1 hour)

**File:** `app/cli_main.py`

**Tasks:**
- [ ] Install Click or Typer
- [ ] Create main CLI group
- [ ] Add version command
- [ ] Add help text
- [ ] Create command groups (scrape, process, list, etc.)

**Example structure:**
```python
import click

@click.group()
def cli():
    """Paper Search CLI"""
    pass

@cli.group()
def scrape():
    """Scraping commands"""
    pass

@scrape.command()
@click.option('--max-results', default=10)
def arxiv(max_results):
    """Scrape arXiv papers"""
    pass
```

### Phase 2: Scraping Commands (30 min)

**Tasks:**
- [ ] Implement scrape arxiv
- [ ] Implement scrape biorxiv
- [ ] Implement scrape pubmed
- [ ] Implement scrape all
- [ ] Add progress bars
- [ ] Add error handling

### Phase 3: Processing Commands (30 min)

**Tasks:**
- [ ] Implement process command
- [ ] Implement classify command
- [ ] Implement summarize command
- [ ] Add progress indicators
- [ ] Show processing results

### Phase 4: Listing & Search (45 min)

**Tasks:**
- [ ] Implement list command with filters
- [ ] Implement search command
- [ ] Implement recent command
- [ ] Format output as table
- [ ] Add pagination

### Phase 5: View & Stats (30 min)

**Tasks:**
- [ ] Implement show command
- [ ] Implement categories command
- [ ] Implement stats command
- [ ] Format output nicely

### Phase 6: Reports & Jobs (30 min)

**Tasks:**
- [ ] Implement report commands
- [ ] Implement jobs commands
- [ ] Add file export
- [ ] Show scheduler status

### Phase 7: Config & Setup (30 min)

**Tasks:**
- [ ] Implement config commands
- [ ] Add interactive setup
- [ ] Test email configuration
- [ ] Validate settings

---

## Dependencies

```txt
click>=8.1.0          # CLI framework (recommended)
# OR
typer>=0.9.0          # Modern CLI framework
rich>=13.0.0          # Beautiful terminal output
tabulate>=0.9.0       # Table formatting
tqdm>=4.66.0          # Progress bars
```

---

## Output Formatting

### Table Output (using rich)
```
┌────┬─────────────────────────────────┬──────────┬────────────┐
│ ID │ Title                           │ Source   │ Processed  │
├────┼─────────────────────────────────┼──────────┼────────────┤
│ 1  │ Neural Networks for...          │ arXiv    │ ✓          │
│ 2  │ Deep Learning in Medicine       │ PubMed   │ ✗          │
└────┴─────────────────────────────────┴──────────┴────────────┘
```

### Progress Bars (using tqdm)
```
Scraping arXiv: 100%|████████████| 10/10 [00:05<00:00, 2.00it/s]
Processing papers: 80%|████████  | 8/10 [00:15<00:03, 1.87s/it]
```

### Colored Output (using rich)
```
✓ Successfully scraped 10 papers from arXiv
✗ Failed to process paper 123: AWS credentials not found
⚠ Warning: 5 papers remain unprocessed
```

---

## Usage Examples

### Daily Workflow
```bash
# Morning: Scrape new papers
paper scrape all --max-results 20

# Process them
paper process --all

# View results
paper list --recent --days 1

# Generate report
paper report daily --save daily-report.md
```

### Search & Explore
```bash
# Search for papers
paper search "machine learning"

# View specific paper
paper show 123 --full

# List by category
paper list --category "Computer Vision"
```

### Job Management
```bash
# Check status
paper jobs status

# View scheduler
paper jobs scheduler

# Run manual job
paper jobs run scrape
```

---

## Entry Point

**Setup in setup.py or pyproject.toml:**
```python
[project.scripts]
paper = "app.cli_main:cli"
```

**Or create executable:**
```bash
#!/usr/bin/env python3
# paper-search/bin/paper
from app.cli_main import cli
if __name__ == '__main__':
    cli()
```

---

## Testing

```bash
# Test each command
paper --help
paper scrape --help
paper scrape arxiv --max-results 5
paper list
paper show 1
paper stats
paper jobs status
```

---

## Success Criteria

- [ ] All commands implemented
- [ ] Beautiful terminal output
- [ ] Progress indicators
- [ ] Error handling
- [ ] Help text for all commands
- [ ] Tab completion (optional)
- [ ] Config file support
- [ ] Works without API running

---

## Estimated Time

**Total:** 4-5 hours

- Phase 1: Core framework (1h)
- Phase 2: Scraping (30m)
- Phase 3: Processing (30m)
- Phase 4: Listing (45m)
- Phase 5: View/Stats (30m)
- Phase 6: Reports/Jobs (30m)
- Phase 7: Config (30m)
- Testing & Polish (30m)

---

## Next Steps

1. Choose CLI framework (Click recommended)
2. Install dependencies
3. Start with Phase 1 (core framework)
4. Implement commands incrementally
5. Test each command as you go

**Recommendation:** Start with Click + Rich for best developer experience and beautiful output.
