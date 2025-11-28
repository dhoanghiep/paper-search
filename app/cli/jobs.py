import click
import httpx
from rich.table import Table
from datetime import datetime
from app.cli import console
from app.config import settings

API_BASE = "http://localhost:8000"

@click.group()
def jobs():
    """Monitor and manage background jobs"""
    pass

@jobs.command()
def status():
    """Show processing status"""
    from app.database import SessionLocal
    from app.models import Paper
    
    db = SessionLocal()
    try:
        total = db.query(Paper).count()
        processed = db.query(Paper).filter(Paper.summary != None, Paper.summary != "").count()
        unprocessed = total - processed
        
        table = Table(title="Processing Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Papers", str(total))
        table.add_row("Processed", str(processed))
        table.add_row("Unprocessed", str(unprocessed))
        
        if processed > 0:
            rate = round(processed / total * 100, 2)
            table.add_row("Processing Rate", f"{rate}%")
        
        console.print(table)
    finally:
        db.close()

@jobs.command()
def scheduler():
    """Show scheduler status and upcoming jobs"""
    try:
        response = httpx.get(f"{API_BASE}/jobs/scheduler/status", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "not_running":
            console.print("[yellow]⚠ Scheduler is not running[/yellow]")
            console.print(f"[yellow]Error: {data.get('error', 'Unknown')}[/yellow]")
            return
        
        console.print(f"[green]✓ Scheduler Status: {data.get('status')}[/green]\n")
        
        jobs_list = data.get("jobs", [])
        if jobs_list:
            table = Table(title="Scheduled Jobs")
            table.add_column("Job ID", style="cyan")
            table.add_column("Name", style="white")
            table.add_column("Next Run", style="yellow")
            
            for job in jobs_list:
                job_id = job.get("id", "N/A")
                name = job.get("name", "N/A")
                next_run = job.get("next_run", "N/A")
                
                # Parse and format next_run if it's a datetime string
                if next_run != "N/A" and next_run != "None":
                    try:
                        dt = datetime.fromisoformat(next_run.replace("Z", "+00:00"))
                        next_run = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                
                table.add_row(job_id, name, next_run)
            
            console.print(table)
        else:
            console.print("[yellow]No scheduled jobs found[/yellow]")
        
    except httpx.ConnectError:
        console.print("[red]✗ Error: API not running. Start with: uvicorn app.main:app[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

@jobs.command()
@click.option('--source', type=click.Choice(['biorxiv', 'pubmed', 'all']), default='all', help='Source to scrape')
@click.option('--max-results', type=int, help='Maximum papers to fetch (default: use config)')
@click.option('--days-back', type=int, help='Days to look back for bioRxiv (default: use config)')
@click.option('--query', type=str, help='Search query for PubMed (default: use config)')
def trigger_scrape(source, max_results, days_back, query):
    """Manually trigger scraping with custom options"""
    import asyncio
    from datetime import datetime
    from app.agents.biorxiv_scraper import BiorxivScraper
    from app.agents.pubmed_scraper import PubmedScraper
    from app.database import SessionLocal
    from app.models import JobHistory
    
    db = SessionLocal()
    try:
        sources = ['biorxiv', 'pubmed'] if source == 'all' else [source]
        console.print(f"[cyan]Scraping: {', '.join(sources)}[/cyan]\n")
        
        for src in sources:
            job = JobHistory(job_type='scrape', source=src, started_at=datetime.utcnow(), status='running')
            db.add(job)
            db.commit()
            
            try:
                if src == 'biorxiv':
                    max_res = max_results or settings.BIORXIV_SCRAPE_MAX
                    days = days_back or settings.BIORXIV_DAYS_BACK
                    
                    console.print(f"[cyan]bioRxiv: {max_res} papers, last {days} days[/cyan]")
                    scraper = BiorxivScraper()
                    papers = asyncio.run(scraper.fetch_recent_papers(
                        max_results=max_res,
                        days_back=days
                    ))
                    saved = scraper.save_papers(db, papers)
                    console.print(f"[green]✓ bioRxiv: fetched {len(papers)}, saved {saved}[/green]\n")
                    
                    job.completed_at = datetime.utcnow()
                    job.status = 'success'
                    job.result = {'fetched': len(papers), 'saved': saved}
                
                elif src == 'pubmed':
                    max_res = max_results or settings.PUBMED_SCRAPE_MAX
                    search_query = query or settings.PUBMED_SCRAPE_QUERY
                    
                    console.print(f"[cyan]PubMed: query='{search_query}', max={max_res}[/cyan]")
                    scraper = PubmedScraper()
                    papers = asyncio.run(scraper.fetch_recent_papers(
                        max_results=max_res,
                        query=search_query
                    ))
                    saved = scraper.save_papers(db, papers)
                    console.print(f"[green]✓ PubMed: fetched {len(papers)}, saved {saved}[/green]\n")
                    
                    job.completed_at = datetime.utcnow()
                    job.status = 'success'
                    job.result = {'fetched': len(papers), 'saved': saved}
                
                db.commit()
            
            except Exception as e:
                console.print(f"[red]✗ {src}: {e}[/red]\n")
                job.completed_at = datetime.utcnow()
                job.status = 'failed'
                job.error = str(e)
                db.commit()
        
    finally:
        db.close()

@jobs.command()
@click.option('--limit', default=10, help='Number of papers to process')
def trigger_process(limit):
    """Manually trigger paper processing job"""
    from datetime import datetime
    from app.pipeline import process_new_papers
    from app.database import SessionLocal
    from app.models import JobHistory
    
    db = SessionLocal()
    job = JobHistory(job_type='process', started_at=datetime.utcnow(), status='running')
    db.add(job)
    db.commit()
    
    try:
        console.print(f"[cyan]Processing {limit} papers...[/cyan]\n")
        
        result = process_new_papers(limit)
        
        job.completed_at = datetime.utcnow()
        job.status = 'success'
        job.result = result
        db.commit()
        
        console.print(f"\n[green]✓ Processed: {result.get('processed', 0)}[/green]")
        if result.get('errors', 0) > 0:
            console.print(f"[yellow]⚠ Errors: {result.get('errors', 0)}[/yellow]")
        if result.get('paper_ids'):
            console.print(f"[dim]Paper IDs: {', '.join(map(str, result['paper_ids']))}[/dim]")
        
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        job.completed_at = datetime.utcnow()
        job.status = 'failed'
        job.error = str(e)
        db.commit()
    finally:
        db.close()

@jobs.command()
def stats():
    """Show comprehensive job statistics"""
    from datetime import datetime, timedelta
    from app.database import SessionLocal
    from app.models import Paper, Category
    
    db = SessionLocal()
    try:
        total = db.query(Paper).count()
        processed = db.query(Paper).filter(Paper.summary != None, Paper.summary != "").count()
        unprocessed = total - processed
        
        week_ago = datetime.now() - timedelta(days=7)
        papers_this_week = db.query(Paper).filter(Paper.created_at >= week_ago).count()
        
        total_categories = db.query(Category).count()
        
        console.print("[bold cyan]Job Statistics[/bold cyan]\n")
        
        # Processing Status
        table1 = Table(title="Processing Status")
        table1.add_column("Metric", style="cyan")
        table1.add_column("Value", style="green")
        
        table1.add_row("Total Papers", str(total))
        table1.add_row("Processed", str(processed))
        table1.add_row("Unprocessed", str(unprocessed))
        table1.add_row("Papers This Week", str(papers_this_week))
        table1.add_row("Total Categories", str(total_categories))
        
        console.print(table1)
        console.print()
        
        # Scheduler Status
        try:
            response = httpx.get(f"{API_BASE}/jobs/scheduler/status", timeout=5.0)
            scheduler_data = response.json()
            console.print(f"[bold]Scheduler:[/bold] {scheduler_data.get('status', 'unknown')}")
            if scheduler_data.get("status") == "running":
                jobs_list = scheduler_data.get("jobs", [])
                console.print(f"[bold]Active Jobs:[/bold] {len(jobs_list)}")
        except:
            console.print(f"[bold]Scheduler:[/bold] [yellow]API not available[/yellow]")
    finally:
        db.close()

@jobs.command()
@click.option('--limit', default=20, help='Number of recent jobs to show')
@click.option('--job-type', type=click.Choice(['scrape', 'process', 'report', 'all']), default='all', help='Filter by job type')
def history(limit, job_type):
    """Show recent job execution history"""
    from app.database import SessionLocal
    from app.models import JobHistory
    
    db = SessionLocal()
    try:
        query = db.query(JobHistory)
        
        if job_type != 'all':
            query = query.filter(JobHistory.job_type == job_type)
        
        jobs = query.order_by(JobHistory.started_at.desc()).limit(limit).all()
        
        if not jobs:
            console.print("[yellow]No job history found[/yellow]")
            return
        
        table = Table(title=f"Job History (Last {len(jobs)} jobs)")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Source", style="magenta")
        table.add_column("Started", style="white")
        table.add_column("Duration", style="blue")
        table.add_column("Status", style="green")
        
        for job in jobs:
            job_id = str(job.id)
            job_type_str = job.job_type or "N/A"
            source = job.source or "-"
            started = job.started_at.strftime("%Y-%m-%d %H:%M:%S") if job.started_at else "N/A"
            
            # Calculate duration
            if job.completed_at and job.started_at:
                duration = job.completed_at - job.started_at
                duration_str = f"{duration.total_seconds():.1f}s"
            else:
                duration_str = "N/A"
            
            # Status with color
            status = job.status or "unknown"
            if status == "success":
                status_display = "[green]✓ success[/green]"
            elif status == "failed":
                status_display = "[red]✗ failed[/red]"
            elif status == "running":
                status_display = "[yellow]⟳ running[/yellow]"
            else:
                status_display = status
            
            table.add_row(job_id, job_type_str, source, started, duration_str, status_display)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    finally:
        db.close()
