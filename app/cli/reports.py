import click
from datetime import datetime, timedelta
from rich.table import Table
from app.cli import console


@click.group()
def report():
    """Generate reports"""
    pass


@report.command()
@click.option('--save', help='Save to file')
def daily(save):
    """Generate daily report (papers from the last 24 hours)"""
    from app.database import SessionLocal
    from app.models import Paper

    db = SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(days=1)
        papers = db.query(Paper).filter(Paper.created_at >= since).order_by(Paper.created_at.desc()).all()

        lines = [f"# Daily Paper Report — {datetime.utcnow().strftime('%Y-%m-%d')}\n"]
        lines.append(f"**{len(papers)} new papers in the last 24 hours**\n")
        for p in papers:
            cats = ", ".join(c.name for c in p.categories) or "uncategorized"
            lines.append(f"## {p.title}")
            lines.append(f"- **Authors:** {p.authors}")
            lines.append(f"- **Categories:** {cats}")
            lines.append(f"- **Published:** {p.published_date}")
            if p.pdf_url:
                lines.append(f"- **PDF:** {p.pdf_url}")
            lines.append("")

        content = "\n".join(lines)

        if save:
            with open(save, 'w') as f:
                f.write(content)
            console.print(f"[green]✓ Report saved to {save}[/green]")
        else:
            console.print(content)
    finally:
        db.close()


@report.command()
@click.option('--save', help='Save to file')
def weekly(save):
    """Generate weekly report (papers from the last 7 days)"""
    from app.database import SessionLocal
    from app.models import Paper

    db = SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(days=7)
        papers = db.query(Paper).filter(Paper.created_at >= since).order_by(Paper.created_at.desc()).all()

        lines = [f"# Weekly Paper Report — {datetime.utcnow().strftime('%Y-%m-%d')}\n"]
        lines.append(f"**{len(papers)} new papers in the last 7 days**\n")
        for p in papers:
            cats = ", ".join(c.name for c in p.categories) or "uncategorized"
            lines.append(f"## {p.title}")
            lines.append(f"- **Authors:** {p.authors}")
            lines.append(f"- **Categories:** {cats}")
            lines.append(f"- **Published:** {p.published_date}")
            if p.pdf_url:
                lines.append(f"- **PDF:** {p.pdf_url}")
            lines.append("")

        content = "\n".join(lines)

        if save:
            with open(save, 'w') as f:
                f.write(content)
            console.print(f"[green]✓ Report saved to {save}[/green]")
        else:
            console.print(content)
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

    db = SessionLocal()
    try:
        total = db.query(Paper).count()
        processed = db.query(Paper).filter(Paper.summary != None, Paper.summary != "").count()
        week_ago = datetime.now() - timedelta(days=7)
        recent = db.query(Paper).filter(Paper.created_at >= week_ago).count()
        cat_count = db.query(Category).count()

        table = Table(title="Database Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Papers", str(total))
        table.add_row("Processed Papers", str(processed))
        table.add_row("Unprocessed Papers", str(total - processed))
        table.add_row("Papers This Week", str(recent))
        table.add_row("Categories", str(cat_count))

        console.print(table)
    finally:
        db.close()
