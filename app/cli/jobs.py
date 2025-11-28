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
    try:
        response = httpx.get(f"{API_BASE}/jobs/status", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        
        table = Table(title="Processing Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Papers", str(data.get("total_papers", 0)))
        table.add_row("Processed", str(data.get("processed", 0)))
        table.add_row("Unprocessed", str(data.get("unprocessed", 0)))
        
        if data.get("processed", 0) > 0:
            rate = round(data["processed"] / data["total_papers"] * 100, 2)
            table.add_row("Processing Rate", f"{rate}%")
        
        console.print(table)
        
    except httpx.ConnectError:
        console.print("[red]✗ Error: API not running. Start with: uvicorn app.main:app[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

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
@click.option('--source', type=click.Choice(['arxiv', 'biorxiv', 'pubmed', 'all']), default='all', help='Source to scrape')
@click.option('--max-results', default=10, help='Maximum papers to fetch')
def trigger_scrape(source, max_results):
    """Manually trigger scraping job"""
    try:
        if source == 'all':
            sources = ['arxiv', 'biorxiv', 'pubmed']
        else:
            sources = [source]
        
        console.print(f"[cyan]Triggering scrape for: {', '.join(sources)}[/cyan]\n")
        
        for src in sources:
            response = httpx.post(
                f"{API_BASE}/jobs/scrape",
                params={"source": src, "max_results": max_results},
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "completed":
                console.print(f"[green]✓ {src}: {data.get('papers_saved', 0)} papers saved[/green]")
            else:
                console.print(f"[yellow]⚠ {src}: {data.get('error', 'Unknown error')}[/yellow]")
        
    except httpx.ConnectError:
        console.print("[red]✗ Error: API not running. Start with: uvicorn app.main:app[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

@jobs.command()
@click.option('--limit', default=10, help='Number of papers to process')
@click.option('--sync', is_flag=True, help='Run synchronously (wait for completion)')
def trigger_process(limit, sync):
    """Manually trigger paper processing job"""
    try:
        endpoint = "/jobs/process-sync" if sync else "/jobs/process"
        
        console.print(f"[cyan]Triggering processing of {limit} papers...[/cyan]")
        
        response = httpx.post(
            f"{API_BASE}{endpoint}",
            params={"limit": limit},
            timeout=300.0 if sync else 10.0
        )
        response.raise_for_status()
        data = response.json()
        
        if sync:
            result = data.get("result", {})
            console.print(f"[green]✓ Processed: {result.get('processed', 0)}[/green]")
            if result.get('errors', 0) > 0:
                console.print(f"[yellow]⚠ Errors: {result.get('errors', 0)}[/yellow]")
        else:
            console.print(f"[green]✓ {data.get('message', 'Job started')}[/green]")
        
    except httpx.ConnectError:
        console.print("[red]✗ Error: API not running. Start with: uvicorn app.main:app[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

@jobs.command()
def stats():
    """Show comprehensive job statistics"""
    try:
        # Get processing status
        status_response = httpx.get(f"{API_BASE}/jobs/status", timeout=5.0)
        status_response.raise_for_status()
        status_data = status_response.json()
        
        # Get scheduler status
        scheduler_response = httpx.get(f"{API_BASE}/jobs/scheduler/status", timeout=5.0)
        scheduler_response.raise_for_status()
        scheduler_data = scheduler_response.json()
        
        # Get general stats
        stats_response = httpx.get(f"{API_BASE}/stats", timeout=5.0)
        stats_response.raise_for_status()
        stats_data = stats_response.json()
        
        console.print("[bold cyan]Job Statistics[/bold cyan]\n")
        
        # Processing Status
        table1 = Table(title="Processing Status")
        table1.add_column("Metric", style="cyan")
        table1.add_column("Value", style="green")
        
        table1.add_row("Total Papers", str(status_data.get("total_papers", 0)))
        table1.add_row("Processed", str(status_data.get("processed", 0)))
        table1.add_row("Unprocessed", str(status_data.get("unprocessed", 0)))
        table1.add_row("Papers This Week", str(stats_data.get("papers_this_week", 0)))
        
        console.print(table1)
        console.print()
        
        # Scheduler Status
        console.print(f"[bold]Scheduler:[/bold] {scheduler_data.get('status', 'unknown')}")
        
        if scheduler_data.get("status") == "running":
            jobs_list = scheduler_data.get("jobs", [])
            console.print(f"[bold]Active Jobs:[/bold] {len(jobs_list)}")
        
    except httpx.ConnectError:
        console.print("[red]✗ Error: API not running. Start with: uvicorn app.main:app[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

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
