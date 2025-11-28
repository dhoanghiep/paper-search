import click
import re
import httpx
from datetime import datetime
from rich.table import Table
from app.cli import console

@click.group()
def papers():
    """Manage papers (add, list, show, search, process)"""
    pass

@papers.command()
@click.argument('doi')
def add(doi):
    """Add a paper by DOI (bioRxiv format: 10.1101/...)"""
    from app.database import SessionLocal
    from app.models import Paper
    
    db = SessionLocal()
    try:
        if doi.startswith('http'):
            doi_match = re.search(r'10\.\d+/[\d.]+', doi)
            if doi_match:
                doi = doi_match.group(0)
        
        existing = db.query(Paper).filter(Paper.arxiv_id == doi).first()
        if existing:
            console.print(f"[yellow]⚠ Paper already exists (ID: {existing.id})[/yellow]")
            return
        
        url = f"https://api.biorxiv.org/details/biorxiv/{doi}"
        response = httpx.get(url, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("collection"):
            console.print(f"[red]✗ Paper not found: {doi}[/red]")
            return
        
        entry = data["collection"][0]
        title = entry.get("title", "").strip()
        
        if title.upper().startswith("WITHDRAWN:"):
            console.print(f"[red]✗ Paper is withdrawn: {title}[/red]")
            return
        
        paper = Paper(
            arxiv_id=doi,
            title=title,
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

@papers.command()
@click.option('--limit', default=10, help='Number of papers to process')
@click.option('--ids', help='Comma-separated paper IDs to process (e.g., 1,2,3)')
def process(limit, ids):
    """Process unprocessed papers (classify + summarize)"""
    from app.pipeline import process_new_papers
    from app.orchestrator import process_paper
    
    if ids:
        paper_ids = [int(id.strip()) for id in ids.split(',')]
        console.print(f"[cyan]Processing {len(paper_ids)} papers...[/cyan]")
        
        processed = 0
        errors = 0
        for paper_id in paper_ids:
            try:
                process_paper(paper_id)
                console.print(f"[green]✓ Paper {paper_id} processed[/green]")
                processed += 1
            except Exception as e:
                console.print(f"[red]✗ Error processing paper {paper_id}: {e}[/red]")
                errors += 1
        
        console.print(f"\n[green]✓ Processed: {processed}[/green]")
        if errors > 0:
            console.print(f"[yellow]⚠ Errors: {errors}[/yellow]")
    else:
        console.print(f"[cyan]Processing up to {limit} papers...[/cyan]")
        result = process_new_papers(limit)
        console.print(f"[green]✓ Processed: {result['processed']}[/green]")
        if result['errors'] > 0:
            console.print(f"[yellow]⚠ Errors: {result['errors']}[/yellow]")

@papers.command()
@click.option('--limit', default=20, help='Number of papers to show')
@click.option('--unprocessed', is_flag=True, help='Show only unprocessed papers')
@click.option('--category', multiple=True, help='Filter by category name (can specify multiple)')
@click.option('--total', is_flag=True, help='Show total count in database')
def list(limit, unprocessed, category, total):
    """List papers"""
    from app.database import SessionLocal
    from app.models import Paper, Category
    from sqlalchemy.orm import aliased
    
    db = SessionLocal()
    try:
        query = db.query(Paper)
        
        if total:
            total_count = query.count()
        
        if unprocessed:
            query = query.filter((Paper.summary == None) | (Paper.summary == ""))
        if category:
            for cat in category:
                cat_alias = aliased(Category)
                query = query.join(cat_alias, Paper.categories).filter(
                    cat_alias.name.ilike(f"%{cat}%")
                )
            query = query.distinct()
        
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

@papers.command()
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

@papers.command()
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
        console.print(f"[yellow]PDF:[/yellow] {paper.pdf_url}")
        
        if paper.categories:
            cats = ", ".join([c.name for c in paper.categories])
            console.print(f"[yellow]Categories:[/yellow] {cats}")
        
        console.print(f"\n[bold]Abstract:[/bold]")
        if full:
            console.print(paper.abstract)
        else:
            console.print(paper.abstract[:500] + "..." if len(paper.abstract) > 500 else paper.abstract)
        
        if paper.summary:
            console.print(f"\n[bold]Summary:[/bold]")
            console.print(paper.summary)
    finally:
        db.close()
