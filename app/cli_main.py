#!/usr/bin/env python3
import click
from app.cli import console
from app.cli.scrape import scrape
from app.cli.papers import papers
from app.cli.reports import report, explore, categories
from app.cli.jobs import jobs

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Paper Search CLI - Manage research papers from multiple sources"""
    pass

# Register command groups
cli.add_command(scrape)
cli.add_command(papers)
cli.add_command(report)
cli.add_command(explore)
cli.add_command(categories)
cli.add_command(jobs)

# Deprecated pubmed group
@cli.group()
def pubmed():
    """[DEPRECATED] Use './paper scrape pubmed' instead"""
    console.print("[yellow]⚠ Warning: 'pubmed' commands are deprecated. Use './paper scrape pubmed' instead[/yellow]\n")

# Keep old pubmed commands for backward compatibility
@pubmed.command()
@click.argument('query')
@click.option('--max-results', default=20, help='Maximum results to show')
def search(query, max_results):
    """Search PubMed and display results (without saving)"""
    import httpx
    from rich.table import Table
    
    console.print(f"[cyan]Searching PubMed for: {query}[/cyan]\n")
    
    try:
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        search_url = f"{base_url}/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "sort": "pub_date",
            "retmode": "json"
        }
        
        response = httpx.get(search_url, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        
        ids = data["esearchresult"]["idlist"]
        count = data["esearchresult"]["count"]
        
        console.print(f"[green]Found {count} papers, showing {len(ids)}:[/green]\n")
        
        table = Table(title="PubMed Search Results")
        table.add_column("PMID", style="cyan")
        
        for pmid in ids:
            table.add_row(pmid)
        
        console.print(table)
        console.print(f"\n[yellow]To fetch and save: ./paper scrape pubmed --fetch-ids {','.join(ids[:5])}[/yellow]")
        
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

@pubmed.command()
@click.argument('pmids')
def fetch(pmids):
    """Fetch and save specific PubMed papers by PMID (comma-separated)"""
    console.print("[yellow]⚠ Use: ./paper scrape pubmed --fetch-ids {pmids}[/yellow]")
    import sys
    from click import Context
    ctx = Context(cli)
    ctx.invoke(scrape.commands['pubmed'], fetch_ids=pmids)

@pubmed.command()
@click.option('--date', default=None, help='Date in YYYY/MM/DD format (default: today)')
@click.option('--topic', default=None, help='Filter by topic (e.g., cancer, genomics)')
@click.option('--max-results', default=100, help='Maximum results')
def daily(date, topic, max_results):
    """Get all PubMed articles from a specific day"""
    console.print("[yellow]⚠ Use: ./paper scrape pubmed --daily[/yellow]")
    import sys
    from click import Context
    ctx = Context(cli)
    ctx.invoke(scrape.commands['pubmed'], daily=True, date=date, topic=topic, max_results=max_results)

if __name__ == '__main__':
    cli()
