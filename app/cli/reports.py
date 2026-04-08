import click
from datetime import datetime, timedelta, date
from rich.table import Table
from app.cli import console


@click.group()
def report():
    """Generate reports"""
    pass


@report.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--category', multiple=True, help='Filter by category name (can specify multiple)')
@click.option('--keyword', multiple=True, help='Filter by keyword in title or abstract (can specify multiple)')
@click.option('--save', help='Save report to file')
def generate(start_date, end_date, category, keyword, save):
    """Generate a report for papers in a date range, optionally filtered by category or keyword"""
    from app.database import SessionLocal
    from app.models import Paper, Category
    from sqlalchemy.orm import aliased

    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    except ValueError as e:
        console.print(f"[red]✗ Invalid date format: {e}[/red]")
        return

    db = SessionLocal()
    try:
        query = db.query(Paper).filter(
            Paper.created_at >= start_dt,
            Paper.created_at <= end_dt
        )

        for cat in category:
            cat_alias = aliased(Category)
            query = query.join(cat_alias, Paper.categories).filter(
                cat_alias.name.ilike(f"%{cat}%")
            )

        if category:
            query = query.distinct()

        papers = query.order_by(Paper.created_at.desc()).all()

        # Further filter by keyword in title or abstract
        if keyword:
            filtered = []
            for p in papers:
                text = ((p.title or '') + ' ' + (p.abstract or '')).lower()
                if all(kw.lower() in text for kw in keyword):
                    filtered.append(p)
            papers = filtered

        # Build report
        cat_label = ', '.join(category) if category else 'all'
        kw_label = ', '.join(keyword) if keyword else None
        title_parts = [f"# Research Paper Report: {start_date} to {end_date}"]
        if category:
            title_parts.append(f"**Categories:** {cat_label}")
        if kw_label:
            title_parts.append(f"**Keywords:** {kw_label}")
        title_parts.append(f"**Papers found:** {len(papers)}\n")

        lines = title_parts[:]
        lines.append("")

        for p in papers:
            cats = ", ".join(c.name for c in p.categories) or "uncategorized"
            lines.append(f"## {p.title}")
            lines.append(f"- **Authors:** {p.authors}")
            lines.append(f"- **Categories:** {cats}")
            lines.append(f"- **Published:** {p.published_date}")
            if p.pdf_url:
                lines.append(f"- **PDF:** {p.pdf_url}")
            if p.summary:
                lines.append(f"\n**Summary:** {p.summary}")
            elif p.abstract:
                abstract_preview = p.abstract[:400] + ("..." if len(p.abstract) > 400 else "")
                lines.append(f"\n**Abstract:** {abstract_preview}")
            lines.append("")

        if not papers:
            lines.append("_No papers found for the specified filters._\n")

        content = "\n".join(lines)

        if save:
            import os
            os.makedirs(os.path.dirname(save), exist_ok=True) if os.path.dirname(save) else None
            with open(save, 'w') as f:
                f.write(content)
            console.print(f"[green]✓ Report saved to {save}[/green]")
            console.print(f"[dim]{len(papers)} papers | {start_date} → {end_date}[/dim]")
        else:
            console.print(content)

    finally:
        db.close()


@report.command('longread-transcriptomic')
@click.option('--days-back', default=1, show_default=True, help='Number of days to look back')
@click.option('--save-dir', default=None, help='Directory to save report (default: ./reports/)')
def longread_transcriptomic(days_back, save_dir):
    """Generate a daily report for long-read transcriptomic methods papers"""
    from app.database import SessionLocal
    from app.models import Paper, Category
    from sqlalchemy.orm import aliased
    import os

    since_dt = datetime.utcnow() - timedelta(days=days_back)
    today_str = date.today().strftime('%Y-%m-%d')
    since_str = (date.today() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    KEYWORDS = ['long-read', 'long read', 'nanopore', 'pacbio', 'ont', 'full-length', 'isoform']
    TOPIC_KEYWORDS = ['transcriptom', 'rna', 'mrna', 'splicing', 'isoform', 'transcript']
    TARGET_CATEGORIES = ['methods', 'transcriptomics', 'genomics', 'sequencing']

    db = SessionLocal()
    try:
        query = db.query(Paper).filter(Paper.created_at >= since_dt)

        # Category filter (OR logic across target categories)
        cat_filters = []
        for cat_name in TARGET_CATEGORIES:
            cat_alias = aliased(Category)
            # Collect IDs from category-filtered subqueries
            cat_filters.append(
                db.query(Paper.id).join(cat_alias, Paper.categories).filter(
                    cat_alias.name.ilike(f"%{cat_name}%")
                ).subquery()
            )

        from sqlalchemy import or_, exists
        category_paper_ids = set()
        for sq in cat_filters:
            ids = [row[0] for row in db.execute(sq)]
            category_paper_ids.update(ids)

        papers_all = query.order_by(Paper.created_at.desc()).all()

        # Score and filter papers
        scored = []
        for p in papers_all:
            text = ((p.title or '') + ' ' + (p.abstract or '')).lower()
            lr_hits = sum(1 for kw in KEYWORDS if kw in text)
            topic_hits = sum(1 for kw in TOPIC_KEYWORDS if kw in text)
            cat_match = p.id in category_paper_ids

            # Must match at least one long-read keyword and one topic keyword, or be in a target category with either
            if lr_hits >= 1 and topic_hits >= 1:
                scored.append((p, lr_hits + topic_hits + (2 if cat_match else 0)))
            elif cat_match and (lr_hits >= 1 or topic_hits >= 1):
                scored.append((p, lr_hits + topic_hits + 1))

        scored.sort(key=lambda x: -x[1])
        papers = [p for p, _ in scored]

        # Build report
        lines = [
            f"# Long-Read Transcriptomic Methods — Daily Report",
            f"**Date:** {today_str}  |  **Period:** last {days_back} day(s) (since {since_str})",
            f"**Papers found:** {len(papers)}\n",
            ""
        ]

        if papers:
            for p in papers:
                cats = ", ".join(c.name for c in p.categories) or "uncategorized"
                lines.append(f"## {p.title}")
                lines.append(f"- **Authors:** {p.authors}")
                lines.append(f"- **Categories:** {cats}")
                lines.append(f"- **Published:** {p.published_date}")
                if p.pdf_url:
                    lines.append(f"- **PDF:** {p.pdf_url}")
                if p.summary:
                    lines.append(f"\n**Summary:** {p.summary}")
                elif p.abstract:
                    preview = p.abstract[:400] + ("..." if len(p.abstract) > 400 else "")
                    lines.append(f"\n**Abstract:** {preview}")
                lines.append("")
        else:
            lines.append("_No long-read transcriptomic papers found in this period._\n")
            lines.append("> **Tip:** Run `./paper jobs trigger-scrape --source biorxiv --query \"long-read transcriptomics\"` to fetch more papers.\n")

        content = "\n".join(lines)

        save_dir = save_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'reports'
        )
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.join(save_dir, f"longread-transcriptomic-{today_str}.md")

        with open(filename, 'w') as f:
            f.write(content)

        console.print(f"[green]✓ Long-read transcriptomic report saved[/green]")
        console.print(f"[dim]{len(papers)} papers → {filename}[/dim]")

        if not papers:
            console.print("[yellow]⚠ No matching papers found. Consider running a targeted scrape first.[/yellow]")

    finally:
        db.close()


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
