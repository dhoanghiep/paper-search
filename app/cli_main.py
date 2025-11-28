#!/usr/bin/env python3
import click
import asyncio
from rich.console import Console
from rich.table import Table
from rich.progress import track
from datetime import datetime, timedelta

console = Console()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Paper Search CLI - Manage research papers from multiple sources"""
    pass

# ============= SCRAPE COMMANDS =============

@cli.group()
def scrape():
    """Scrape papers from various sources"""
    pass

@scrape.command()
@click.option('--max-results', default=10, help='Maximum papers to fetch')
def arxiv(max_results):
    """Scrape papers from arXiv"""
    from app.agents.scraper import ArxivScraper
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        console.print(f"[cyan]Scraping {max_results} papers from arXiv...[/cyan]")
        scraper = ArxivScraper()
        papers = asyncio.run(scraper.fetch_recent_papers(max_results))
        scraper.save_papers(db, papers)
        console.print(f"[green]✓ Successfully scraped {len(papers)} papers[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    finally:
        db.close()

@scrape.command()
@click.option('--max-results', default=10, help='Maximum papers to fetch')
def biorxiv(max_results):
    """Scrape papers from bioRxiv"""
    from app.agents.biorxiv_scraper import BiorxivScraper
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        console.print(f"[cyan]Scraping {max_results} papers from bioRxiv...[/cyan]")
        scraper = BiorxivScraper()
        papers = asyncio.run(scraper.fetch_recent_papers(max_results))
        scraper.save_papers(db, papers)
        console.print(f"[green]✓ Successfully scraped {len(papers)} papers[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    finally:
        db.close()

@scrape.command()
@click.option('--max-results', default=10, help='Maximum papers to fetch')
@click.option('--query', default='cancer OR diabetes', help='Search query')
def pubmed(max_results, query):
    """Scrape papers from PubMed"""
    from app.agents.pubmed_scraper import PubmedScraper
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        console.print(f"[cyan]Scraping {max_results} papers from PubMed (query: {query})...[/cyan]")
        scraper = PubmedScraper()
        papers = asyncio.run(scraper.fetch_recent_papers(max_results, query))
        scraper.save_papers(db, papers)
        console.print(f"[green]✓ Successfully scraped {len(papers)} papers[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    finally:
        db.close()

@scrape.command()
@click.option('--max-results', default=10, help='Maximum papers per source')
def all(max_results):
    """Scrape papers from all sources"""
    sources = ['arxiv', 'biorxiv', 'pubmed']
    for source in track(sources, description="Scraping sources..."):
        ctx = click.get_current_context()
        ctx.invoke(globals()[source], max_results=max_results)

@scrape.command()
@click.argument('url')
def add(url):
    """Add a specific bioRxiv paper by URL or DOI"""
    import re
    import httpx
    from datetime import datetime
    from app.database import SessionLocal
    from app.models import Paper
    
    db = SessionLocal()
    try:
        # Extract DOI from URL (format: 10.1101/2024.11.20.624567)
        doi_match = re.search(r'10\.\d+/[\d.]+', url)
        if not doi_match:
            console.print("[red]✗ Invalid bioRxiv URL or DOI[/red]")
            return
        
        doi = doi_match.group(0)
        console.print(f"[cyan]Fetching paper with DOI: {doi}...[/cyan]")
        
        # Check if already exists
        existing = db.query(Paper).filter(Paper.arxiv_id == doi).first()
        if existing:
            console.print(f"[yellow]⚠ Paper already exists (ID: {existing.id})[/yellow]")
            return
        
        # Fetch from bioRxiv API
        api_url = f"https://api.biorxiv.org/details/biorxiv/{doi}"
        response = httpx.get(api_url, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        
        collection = data.get("collection", [])
        if not collection:
            console.print("[red]✗ Paper not found in bioRxiv API[/red]")
            return
        
        entry = collection[0]
        paper = Paper(
            arxiv_id=doi,
            title=entry.get("title", "").strip(),
            authors=entry.get("authors", ""),
            abstract=entry.get("abstract", "").strip(),
            published_date=datetime.fromisoformat(entry.get("date", "").split("T")[0]),
            pdf_url=f"https://www.biorxiv.org/content/{doi}v1.full.pdf"
        )
        
        db.add(paper)
        db.commit()
        console.print(f"[green]✓ Added paper (ID: {paper.id}): {paper.title[:60]}...[/green]")
        
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        db.rollback()
    finally:
        db.close()

# ============= PROCESS COMMANDS =============

@cli.command()
@click.argument('doi')
def add(doi):
    """Add a paper by DOI (bioRxiv format: 10.1101/...)"""
    import re
    import httpx
    from datetime import datetime
    from app.database import SessionLocal
    from app.models import Paper
    
    db = SessionLocal()
    try:
        # Clean DOI
        doi_match = re.search(r'10\.\d+/[\d.]+', doi)
        if not doi_match:
            console.print("[red]✗ Invalid DOI format. Expected: 10.1101/YYYY.MM.DD.XXXXXX[/red]")
            return
        
        doi = doi_match.group(0)
        
        # Check if exists
        existing = db.query(Paper).filter(Paper.arxiv_id == doi).first()
        if existing:
            console.print(f"[yellow]⚠ Paper already exists (ID: {existing.id})[/yellow]")
            return
        
        console.print(f"[cyan]Fetching DOI: {doi}...[/cyan]")
        
        # Try bioRxiv API
        api_url = f"https://api.biorxiv.org/details/biorxiv/{doi}"
        response = httpx.get(api_url, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        
        collection = data.get("collection", [])
        if not collection:
            console.print("[red]✗ Paper not found in bioRxiv API[/red]")
            return
        
        entry = collection[0]
        paper = Paper(
            arxiv_id=doi,
            title=entry.get("title", "").strip(),
            authors=entry.get("authors", ""),
            abstract=entry.get("abstract", "").strip(),
            published_date=datetime.fromisoformat(entry.get("date", "").split("T")[0]),
            pdf_url=f"https://www.biorxiv.org/content/{doi}v1.full.pdf"
        )
        
        db.add(paper)
        db.commit()
        console.print(f"[green]✓ Added paper (ID: {paper.id})[/green]")
        console.print(f"[white]{paper.title}[/white]")
        
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        db.rollback()
    finally:
        db.close()

@cli.command()
@click.option('--limit', default=10, help='Number of papers to process')
@click.option('--ids', help='Comma-separated paper IDs to process (e.g., 1,2,3)')
def process(limit, ids):
    """Process unprocessed papers (classify + summarize)"""
    from app.pipeline import process_new_papers
    from app.orchestrator import process_paper
    
    if ids:
        # Process specific papers by ID
        paper_ids = [int(id.strip()) for id in ids.split(',')]
        console.print(f"[cyan]Processing {len(paper_ids)} specific papers...[/cyan]")
        
        processed = 0
        errors = 0
        for paper_id in paper_ids:
            try:
                console.print(f"[cyan]Processing paper {paper_id}...[/cyan]")
                process_paper(paper_id)
                processed += 1
                console.print(f"[green]✓ Paper {paper_id} processed[/green]")
            except Exception as e:
                console.print(f"[red]✗ Error processing paper {paper_id}: {e}[/red]")
                errors += 1
        
        console.print(f"\n[green]✓ Processed: {processed}[/green]")
        if errors > 0:
            console.print(f"[yellow]⚠ Errors: {errors}[/yellow]")
    else:
        # Process unprocessed papers
        console.print(f"[cyan]Processing up to {limit} papers...[/cyan]")
        result = process_new_papers(limit)
        console.print(f"[green]✓ Processed: {result['processed']}[/green]")
        if result['errors'] > 0:
            console.print(f"[yellow]⚠ Errors: {result['errors']}[/yellow]")

# ============= LIST COMMANDS =============

@cli.command()
@click.option('--limit', default=20, help='Number of papers to show')
@click.option('--unprocessed', is_flag=True, help='Show only unprocessed papers')
@click.option('--category', multiple=True, help='Filter by category name (can specify multiple)')
@click.option('--total', is_flag=True, help='Show total count in database')
def list(limit, unprocessed, category, total):
    """List papers"""
    from app.database import SessionLocal
    from app.models import Paper, Category
    from sqlalchemy import or_
    
    db = SessionLocal()
    try:
        query = db.query(Paper)
        
        # Get total count before filtering
        if total:
            total_count = query.count()
        
        if unprocessed:
            query = query.filter((Paper.summary == None) | (Paper.summary == ""))
        if category:
            query = query.join(Paper.categories).filter(
                or_(*[Category.name.ilike(f"%{cat}%") for cat in category])
            ).distinct()
        
        # Get filtered count
        filtered_count = query.count()
        papers = query.order_by(Paper.created_at.desc()).limit(limit).all()
        
        title = f"Papers ({len(papers)} shown"
        if total:
            title += f" of {filtered_count} filtered, {total_count} total"
        else:
            title += f" of {filtered_count}"
        title += ")"
        
        if category:
            title += f" - Categories: {', '.join(category)}"
        
        table = Table(title=title)
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="white", max_width=50)
        table.add_column("Source", style="yellow")
        table.add_column("Categories", style="magenta", max_width=30)
        table.add_column("Processed", style="green")
        
        for paper in papers:
            source = "arXiv" if "arxiv" in paper.arxiv_id.lower() else \
                     "PubMed" if "PMID" in paper.arxiv_id else "bioRxiv"
            processed = "✓" if paper.summary else "✗"
            cats = ", ".join([c.name for c in paper.categories]) if paper.categories else "-"
            table.add_row(str(paper.id), paper.title[:50], source, cats[:30], processed)
        
        console.print(table)
    finally:
        db.close()

@cli.command()
@click.argument('query')
def search(query):
    """Search papers by keyword"""
    from app.database import SessionLocal
    from app.models import Paper
    
    db = SessionLocal()
    try:
        papers = db.query(Paper).filter(
            (Paper.title.ilike(f"%{query}%")) | (Paper.abstract.ilike(f"%{query}%"))
        ).limit(20).all()
        
        console.print(f"[cyan]Found {len(papers)} papers matching '{query}'[/cyan]\n")
        
        for paper in papers:
            console.print(f"[bold]{paper.id}. {paper.title}[/bold]")
            console.print(f"   {paper.arxiv_id} | {paper.published_date}")
            console.print()
    finally:
        db.close()

@cli.command()
def categories():
    """List all categories with paper counts"""
    from app.database import SessionLocal
    from app.models import Category
    from sqlalchemy import func
    
    db = SessionLocal()
    try:
        cats = db.query(Category).all()
        
        if not cats:
            console.print("[yellow]No categories found. Process papers first to generate categories.[/yellow]")
            return
        
        table = Table(title=f"Categories ({len(cats)} total)")
        table.add_column("Name", style="cyan")
        table.add_column("Papers", style="green", justify="right")
        table.add_column("Description", style="white", max_width=60)
        
        for cat in cats:
            paper_count = len(cat.papers)
            desc = cat.description[:60] if cat.description else "-"
            table.add_row(cat.name, str(paper_count), desc)
        
        console.print(table)
    finally:
        db.close()

# ============= VIEW COMMANDS =============

@cli.command()
@click.argument('paper_id', type=int)
@click.option('--full', is_flag=True, help='Show full abstract')
def show(paper_id, full):
    """Show paper details"""
    from app.database import SessionLocal
    from app.models import Paper
    
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            console.print(f"[red]✗ Paper {paper_id} not found[/red]")
            return
        
        console.print(f"\n[bold cyan]Paper #{paper.id}[/bold cyan]")
        console.print(f"[bold]{paper.title}[/bold]\n")
        console.print(f"[yellow]ID:[/yellow] {paper.arxiv_id}")
        console.print(f"[yellow]Authors:[/yellow] {paper.authors}")
        console.print(f"[yellow]Published:[/yellow] {paper.published_date}")
        console.print(f"[yellow]URL:[/yellow] {paper.pdf_url}")
        
        if paper.categories:
            cats = ", ".join([c.name for c in paper.categories])
            console.print(f"[yellow]Categories:[/yellow] {cats}")
        console.print()
        
        if full:
            console.print(f"[bold]Abstract:[/bold]")
            console.print(paper.abstract)
        else:
            console.print(f"[bold]Abstract:[/bold] {paper.abstract[:200]}...")
        
        if paper.summary:
            console.print(f"\n[bold]Summary:[/bold]")
            console.print(paper.summary)
        else:
            console.print(f"\n[yellow]⚠ Not yet processed[/yellow]")
    finally:
        db.close()

@cli.group()
def explore():
    """Explore papers with detailed analysis tools"""
    pass

@explore.command()
@click.argument('paper_id', type=int)
def tldr(paper_id):
    """Generate one-sentence summary"""
    from app.database import SessionLocal
    from app.models import Paper
    from app.orchestrator import summarization_client
    
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            console.print(f"[red]✗ Paper {paper_id} not found[/red]")
            return
        
        console.print(f"\n[bold cyan]Paper #{paper.id}:[/bold cyan] {paper.title}\n")
        with console.status("[cyan]Generating TLDR...", spinner="dots"):
            result = summarization_client.call("generate_tldr", {"paper_id": paper_id})
        console.print(f"[yellow]TLDR:[/yellow] {result.get('tldr', 'N/A')}")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    finally:
        db.close()

@explore.command()
@click.argument('paper_id', type=int)
def points(paper_id):
    """Extract key points"""
    from app.database import SessionLocal
    from app.models import Paper
    from app.orchestrator import summarization_client
    
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            console.print(f"[red]✗ Paper {paper_id} not found[/red]")
            return
        
        console.print(f"\n[bold cyan]Paper #{paper.id}:[/bold cyan] {paper.title}\n")
        with console.status("[cyan]Extracting key points...", spinner="dots"):
            result = summarization_client.call("extract_key_points", {"paper_id": paper_id})
        console.print(f"[bold]Key Points:[/bold]")
        console.print(result.get('points', 'N/A'))
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    finally:
        db.close()

@explore.command()
@click.argument('paper_id', type=int)
def detailed(paper_id):
    """Generate detailed analysis"""
    from app.database import SessionLocal
    from app.models import Paper
    from app.orchestrator import summarization_client
    
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            console.print(f"[red]✗ Paper {paper_id} not found[/red]")
            return
        
        console.print(f"\n[bold cyan]Paper #{paper.id}:[/bold cyan] {paper.title}\n")
        with console.status("[cyan]Generating detailed analysis...", spinner="dots"):
            result = summarization_client.call("summarize_detailed", {"paper_id": paper_id})
        console.print(f"[bold]Detailed Analysis:[/bold]")
        console.print(result.get('summary', 'N/A'))
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    finally:
        db.close()

@explore.command()
@click.argument('paper_id', type=int)
def all(paper_id):
    """Show all analysis (TLDR, key points, detailed)"""
    from app.database import SessionLocal
    from app.models import Paper
    from app.orchestrator import summarization_client
    
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            console.print(f"[red]✗ Paper {paper_id} not found[/red]")
            return
        
        console.print(f"\n[bold cyan]Exploring Paper #{paper.id}[/bold cyan]")
        console.print(f"[bold]{paper.title}[/bold]\n")
        
        with console.status("[cyan]Generating TLDR...", spinner="dots"):
            tldr_result = summarization_client.call("generate_tldr", {"paper_id": paper_id})
        console.print(f"[yellow]TLDR:[/yellow] {tldr_result.get('tldr', 'N/A')}\n")
        
        with console.status("[cyan]Extracting key points...", spinner="dots"):
            points_result = summarization_client.call("extract_key_points", {"paper_id": paper_id})
        console.print(f"[bold]Key Points:[/bold]")
        console.print(points_result.get('points', 'N/A'))
        console.print()
        
        with console.status("[cyan]Generating detailed analysis...", spinner="dots"):
            detailed_result = summarization_client.call("summarize_detailed", {"paper_id": paper_id})
        console.print(f"[bold]Detailed Analysis:[/bold]")
        console.print(detailed_result.get('summary', 'N/A'))
        
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    finally:
        db.close()

@cli.command()
def stats():
    """Show database statistics"""
    from app.database import SessionLocal
    from app.models import Paper, Category
    
    db = SessionLocal()
    try:
        total = db.query(Paper).count()
        processed = db.query(Paper).filter(Paper.summary != None, Paper.summary != "").count()
        week_ago = datetime.now() - timedelta(days=7)
        recent = db.query(Paper).filter(Paper.created_at >= week_ago).count()
        categories = db.query(Category).count()
        
        table = Table(title="Database Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Papers", str(total))
        table.add_row("Processed Papers", str(processed))
        table.add_row("Unprocessed Papers", str(total - processed))
        table.add_row("Papers This Week", str(recent))
        table.add_row("Categories", str(categories))
        
        console.print(table)
    finally:
        db.close()

# ============= REPORT COMMANDS =============

@cli.group()
def report():
    """Generate reports"""
    pass

@report.command()
@click.option('--save', help='Save to file')
def daily(save):
    """Generate daily report"""
    from app.reports_job import generate_daily_report
    
    console.print("[cyan]Generating daily report...[/cyan]")
    report_content = generate_daily_report()
    
    if save:
        with open(save, 'w') as f:
            f.write(report_content)
        console.print(f"[green]✓ Report saved to {save}[/green]")
    else:
        console.print(report_content)

@report.command()
@click.option('--save', help='Save to file')
def weekly(save):
    """Generate weekly report"""
    from app.reports_job import generate_weekly_report
    
    console.print("[cyan]Generating weekly report...[/cyan]")
    report_content = generate_weekly_report()
    
    if save:
        with open(save, 'w') as f:
            f.write(report_content)
        console.print(f"[green]✓ Report saved to {save}[/green]")
    else:
        console.print(report_content)

# ============= JOBS COMMANDS =============

@cli.group()
def jobs():
    """Job management"""
    pass

@jobs.command()
def status():
    """Show job status"""
    from app.database import SessionLocal
    from app.models import Paper
    
    db = SessionLocal()
    try:
        total = db.query(Paper).count()
        processed = db.query(Paper).filter(Paper.summary != None, Paper.summary != "").count()
        
        table = Table(title="Job Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Papers", str(total))
        table.add_row("Processed", str(processed))
        table.add_row("Unprocessed", str(total - processed))
        table.add_row("Processing Rate", f"{(processed/total*100):.1f}%" if total > 0 else "0%")
        
        console.print(table)
    finally:
        db.close()

if __name__ == '__main__':
    cli()
