import click
from datetime import datetime
from rich.table import Table
from app.cli import console

@click.group()
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

@report.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--category', multiple=True, help='Filter by categories (can specify multiple)')
@click.option('--save', help='Save to file')
def generate(start_date, end_date, category, save):
    """Generate LLM-based report for papers in date range and categories"""
    from app.database import SessionLocal
    from app.models import Paper, Category
    from app.orchestrator import reports_client
    from sqlalchemy.orm import aliased
    
    console.print(f"[cyan]Generating report for {start_date} to {end_date}[/cyan]")
    if category:
        console.print(f"[cyan]Categories: {', '.join(category)}[/cyan]")
    
    db = SessionLocal()
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        query = db.query(Paper).filter(
            Paper.published_date >= start,
            Paper.published_date <= end,
            Paper.summary != None,
            Paper.summary != ""
        )
        
        if category:
            for cat in category:
                cat_alias = aliased(Category)
                query = query.join(cat_alias, Paper.categories).filter(
                    cat_alias.name.ilike(f"%{cat}%")
                )
            query = query.distinct()
        
        papers = query.all()
        
        if not papers:
            console.print("[yellow]No papers found for the specified criteria[/yellow]")
            return
        
        console.print(f"[cyan]Found {len(papers)} papers. Generating report...[/cyan]")
        
        papers_data = []
        for p in papers:
            papers_data.append({
                "title": p.title,
                "authors": p.authors,
                "published_date": p.published_date.strftime("%Y-%m-%d"),
                "categories": ", ".join([c.name for c in p.categories]),
                "summary": p.summary
            })
        
        with console.status("[cyan]Generating LLM report...", spinner="dots"):
            result = reports_client.call("generate_llm_report", {
                "papers_data": papers_data,
                "start_date": start_date,
                "end_date": end_date,
                "categories": list(category) if category else []
            })
        
        report_content = result.get("report", "")
        
        if save:
            with open(save, 'w') as f:
                f.write(report_content)
            console.print(f"[green]✓ Report saved to {save}[/green]")
        else:
            console.print("\n" + report_content)
            
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    finally:
        db.close()

@click.group()
def explore():
    """Explore papers with AI analysis"""
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

@click.group()
def categories():
    """View categories and statistics"""
    pass

@categories.command()
def list():
    """List all categories"""
    from app.database import SessionLocal
    from app.models import Category
    
    db = SessionLocal()
    try:
        cats = db.query(Category).all()
        
        table = Table(title=f"Categories ({len(cats)} total)")
        table.add_column("Name", style="cyan")
        table.add_column("Papers", style="green")
        table.add_column("Description", style="white", max_width=60)
        
        for cat in cats:
            paper_count = len(cat.papers)
            desc = cat.description[:60] if cat.description else "-"
            table.add_row(cat.name, str(paper_count), desc)
        
        console.print(table)
    finally:
        db.close()

@categories.command()
def stats():
    """Show database statistics"""
    from app.database import SessionLocal
    from app.models import Paper, Category
    from datetime import datetime, timedelta
    
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
