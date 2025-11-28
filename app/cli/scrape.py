import click
import asyncio
import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
from rich.table import Table
from app.cli import console

@click.group()
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

@scrape.command(name='pubmed')
@click.option('--max-results', default=10, help='Maximum papers to fetch')
@click.option('--query', default='cancer OR diabetes', help='Search query')
@click.option('--search-only', is_flag=True, help='Search without saving')
@click.option('--fetch-ids', help='Fetch specific PMIDs (comma-separated)')
@click.option('--daily', is_flag=True, help='Get today\'s papers')
@click.option('--date', help='Date for daily search (YYYY/MM/DD)')
@click.option('--topic', help='Topic filter for daily search')
def pubmed(max_results, query, search_only, fetch_ids, daily, date, topic):
    """PubMed operations: search, fetch, or daily tracking"""
    from app.database import SessionLocal
    from app.models import Paper
    
    if fetch_ids:
        db = SessionLocal()
        pmid_list = [p.strip() for p in fetch_ids.split(',')]
        console.print(f"[cyan]Fetching {len(pmid_list)} papers from PubMed...[/cyan]\n")
        
        try:
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
            fetch_url = f"{base_url}/efetch.fcgi"
            params = {"db": "pubmed", "id": ",".join(pmid_list), "retmode": "xml"}
            
            response = httpx.get(fetch_url, params=params, timeout=30.0)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            saved = 0
            skipped = 0
            
            for article in root.findall(".//PubmedArticle"):
                try:
                    pmid = article.find(".//PMID").text
                    paper_id = f"PMID:{pmid}"
                    
                    existing = db.query(Paper).filter(Paper.arxiv_id == paper_id).first()
                    if existing:
                        console.print(f"[yellow]⚠ PMID:{pmid} already exists[/yellow]")
                        skipped += 1
                        continue
                    
                    title_elem = article.find(".//ArticleTitle")
                    title = title_elem.text if title_elem is not None else "No title"
                    
                    abstract_elem = article.find(".//AbstractText")
                    abstract = abstract_elem.text if abstract_elem is not None else ""
                    
                    authors = []
                    for author in article.findall(".//Author"):
                        lastname = author.find("LastName")
                        forename = author.find("ForeName")
                        if lastname is not None and forename is not None:
                            authors.append(f"{forename.text} {lastname.text}")
                    
                    pub_date = article.find(".//PubDate")
                    year = pub_date.find("Year").text if pub_date.find("Year") is not None else "2024"
                    month = pub_date.find("Month").text if pub_date.find("Month") is not None else "01"
                    day = pub_date.find("Day").text if pub_date.find("Day") is not None else "01"
                    
                    month_map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                                "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
                    month = month_map.get(month, month if month.isdigit() else "01")
                    
                    published = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
                    
                    paper = Paper(
                        arxiv_id=paper_id,
                        title=title,
                        authors=", ".join(authors) if authors else "Unknown",
                        abstract=abstract,
                        published_date=published,
                        pdf_url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    )
                    
                    db.add(paper)
                    db.commit()
                    console.print(f"[green]✓ Added PMID:{pmid}: {title[:60]}...[/green]")
                    saved += 1
                    
                except Exception as e:
                    console.print(f"[red]✗ Error processing article: {e}[/red]")
                    db.rollback()
                    continue
            
            console.print(f"\n[green]✓ Saved: {saved}[/green]")
            if skipped > 0:
                console.print(f"[yellow]⚠ Skipped: {skipped}[/yellow]")
                
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
        finally:
            db.close()
        return
    
    if daily:
        if not date:
            date = datetime.now().strftime("%Y/%m/%d")
        
        if topic:
            query = f"{topic} AND {date}[PDAT]"
        else:
            query = f"{date}[PDAT]"
        
        console.print(f"[cyan]Searching PubMed for articles on {date}[/cyan]")
        if topic:
            console.print(f"[cyan]Topic filter: {topic}[/cyan]")
        console.print()
        search_only = True
    
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
        
        if len(ids) > 0:
            table = Table(title="PubMed Search Results")
            table.add_column("PMID", style="cyan")
            
            for pmid in ids[:20]:
                table.add_row(pmid)
            
            console.print(table)
            
            if len(ids) > 20:
                console.print(f"\n[yellow]... and {len(ids) - 20} more[/yellow]")
            
            console.print(f"\n[yellow]To fetch: ./paper scrape pubmed --fetch-ids {','.join(ids[:10])}[/yellow]")
            
            if not search_only:
                from app.agents.pubmed_scraper import PubmedScraper
                from app.database import SessionLocal
                
                db = SessionLocal()
                try:
                    console.print(f"\n[cyan]Fetching and saving papers...[/cyan]")
                    scraper = PubmedScraper()
                    papers = asyncio.run(scraper.fetch_recent_papers(max_results, query))
                    saved = scraper.save_papers(db, papers)
                    console.print(f"[green]✓ Successfully saved {saved} papers[/green]")
                except Exception as e:
                    console.print(f"[red]✗ Error: {e}[/red]")
                finally:
                    db.close()
        else:
            console.print("[yellow]No papers found[/yellow]")
        
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

@scrape.command()
@click.option('--max-results', default=10, help='Maximum papers per source')
def all(max_results):
    """Scrape from all sources"""
    from app.agents.scraper import ArxivScraper
    from app.agents.biorxiv_scraper import BiorxivScraper
    from app.agents.pubmed_scraper import PubmedScraper
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        console.print(f"[cyan]Scraping {max_results} papers from all sources...[/cyan]\n")
        
        arxiv_scraper = ArxivScraper()
        arxiv_papers = asyncio.run(arxiv_scraper.fetch_recent_papers(max_results))
        arxiv_saved = arxiv_scraper.save_papers(db, arxiv_papers)
        console.print(f"[green]✓ arXiv: {arxiv_saved} papers[/green]")
        
        biorxiv_scraper = BiorxivScraper()
        biorxiv_papers = asyncio.run(biorxiv_scraper.fetch_recent_papers(max_results))
        biorxiv_saved = biorxiv_scraper.save_papers(db, biorxiv_papers)
        console.print(f"[green]✓ bioRxiv: {biorxiv_saved} papers[/green]")
        
        pubmed_scraper = PubmedScraper()
        pubmed_papers = asyncio.run(pubmed_scraper.fetch_recent_papers(max_results))
        pubmed_saved = pubmed_scraper.save_papers(db, pubmed_papers)
        console.print(f"[green]✓ PubMed: {pubmed_saved} papers[/green]")
        
        total = arxiv_saved + biorxiv_saved + pubmed_saved
        console.print(f"\n[green]✓ Total: {total} papers saved[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    finally:
        db.close()
