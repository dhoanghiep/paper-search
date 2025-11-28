import click
from app.cli import console

@click.group()
def scrape():
    """[DEPRECATED] Use 'jobs trigger-scrape' instead"""
    pass

@scrape.command()
@click.option('--max-results', type=int, help='Maximum papers to fetch')
@click.option('--days-back', type=int, help='Days to look back')
def biorxiv(max_results, days_back):
    """[DEPRECATED] Scrape bioRxiv papers - Use 'jobs trigger-scrape' instead"""
    console.print("[yellow]⚠️  DEPRECATED: This command is deprecated[/yellow]")
    console.print("[yellow]   Use instead: ./paper jobs trigger-scrape --source biorxiv[/yellow]\n")
    
    cmd = "./paper jobs trigger-scrape --source biorxiv"
    if max_results:
        cmd += f" --max-results {max_results}"
    if days_back:
        cmd += f" --days-back {days_back}"
    
    console.print(f"[cyan]Suggested command:[/cyan] {cmd}\n")
    
    # Still execute for backward compatibility
    import asyncio
    from app.agents.biorxiv_scraper import BiorxivScraper
    from app.database import SessionLocal
    from app.config import settings
    
    db = SessionLocal()
    try:
        max_res = max_results or settings.BIORXIV_SCRAPE_MAX
        days = days_back or settings.BIORXIV_DAYS_BACK
        
        console.print(f"[cyan]Scraping bioRxiv: {max_res} papers, last {days} days[/cyan]")
        scraper = BiorxivScraper()
        papers = asyncio.run(scraper.fetch_recent_papers(max_res, days))
        saved = scraper.save_papers(db, papers)
        console.print(f"[green]✓ Fetched {len(papers)}, saved {saved}[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    finally:
        db.close()

@scrape.command()
@click.option('--max-results', type=int, help='Maximum papers to fetch')
@click.option('--query', type=str, help='Search query')
def pubmed(max_results, query):
    """[DEPRECATED] Scrape PubMed papers - Use 'jobs trigger-scrape' instead"""
    console.print("[yellow]⚠️  DEPRECATED: This command is deprecated[/yellow]")
    console.print("[yellow]   Use instead: ./paper jobs trigger-scrape --source pubmed[/yellow]\n")
    
    cmd = "./paper jobs trigger-scrape --source pubmed"
    if max_results:
        cmd += f" --max-results {max_results}"
    if query:
        cmd += f' --query "{query}"'
    
    console.print(f"[cyan]Suggested command:[/cyan] {cmd}\n")
    
    # Still execute for backward compatibility
    import asyncio
    from app.agents.pubmed_scraper import PubmedScraper
    from app.database import SessionLocal
    from app.config import settings
    
    db = SessionLocal()
    try:
        max_res = max_results or settings.PUBMED_SCRAPE_MAX
        search_query = query or settings.PUBMED_SCRAPE_QUERY
        
        console.print(f"[cyan]Scraping PubMed: query='{search_query}', max={max_res}[/cyan]")
        scraper = PubmedScraper()
        papers = asyncio.run(scraper.fetch_recent_papers(max_res, search_query))
        saved = scraper.save_papers(db, papers)
        console.print(f"[green]✓ Fetched {len(papers)}, saved {saved}[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    finally:
        db.close()

@scrape.command()
@click.option('--max-results', type=int, default=10, help='Maximum papers per source')
def all(max_results):
    """[DEPRECATED] Scrape all sources - Use 'jobs trigger-scrape' instead"""
    console.print("[yellow]⚠️  DEPRECATED: This command is deprecated[/yellow]")
    console.print("[yellow]   Use instead: ./paper jobs trigger-scrape[/yellow]\n")
    console.print(f"[cyan]Suggested command:[/cyan] ./paper jobs trigger-scrape --max-results {max_results}\n")
    
    # Still execute for backward compatibility
    import asyncio
    from app.agents.biorxiv_scraper import BiorxivScraper
    from app.agents.pubmed_scraper import PubmedScraper
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        console.print(f"[cyan]Scraping {max_results} papers from all sources...[/cyan]\n")
        
        biorxiv_scraper = BiorxivScraper()
        biorxiv_papers = asyncio.run(biorxiv_scraper.fetch_recent_papers(max_results))
        biorxiv_saved = biorxiv_scraper.save_papers(db, biorxiv_papers)
        console.print(f"[green]✓ bioRxiv: {biorxiv_saved} papers[/green]")
        
        pubmed_scraper = PubmedScraper()
        pubmed_papers = asyncio.run(pubmed_scraper.fetch_recent_papers(max_results))
        pubmed_saved = pubmed_scraper.save_papers(db, pubmed_papers)
        console.print(f"[green]✓ PubMed: {pubmed_saved} papers[/green]")
        
        total = biorxiv_saved + pubmed_saved
        console.print(f"\n[green]✓ Total: {total} papers saved[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    finally:
        db.close()
