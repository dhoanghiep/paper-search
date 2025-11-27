from app.database import SessionLocal
from app.models import Paper, Report
from datetime import datetime, timedelta
from sqlalchemy import desc

def generate_daily_report() -> str:
    """Generate daily report of papers"""
    db = SessionLocal()
    try:
        yesterday = datetime.now() - timedelta(days=1)
        
        # Get papers from last 24 hours
        recent_papers = db.query(Paper).filter(
            Paper.created_at >= yesterday
        ).order_by(desc(Paper.created_at)).all()
        
        # Get total stats
        total_papers = db.query(Paper).count()
        processed = db.query(Paper).filter(
            Paper.summary != None, Paper.summary != ""
        ).count()
        
        # Generate markdown report
        report = f"""# Daily Paper Report - {datetime.now().strftime('%Y-%m-%d')}

## Summary
- **Total Papers in Database:** {total_papers}
- **Processed Papers:** {processed}
- **New Papers (Last 24h):** {len(recent_papers)}

## Recent Papers

"""
        
        for paper in recent_papers[:10]:  # Top 10
            report += f"""### {paper.title}
- **Authors:** {paper.authors}
- **Published:** {paper.published_date}
- **ID:** {paper.arxiv_id}
- **Summary:** {paper.summary or 'Not yet processed'}

---

"""
        
        # Save report to database
        report_obj = Report(
            report_type="daily",
            content=report
        )
        db.add(report_obj)
        db.commit()
        
        return report
    finally:
        db.close()

def generate_weekly_report() -> str:
    """Generate weekly report"""
    db = SessionLocal()
    try:
        week_ago = datetime.now() - timedelta(days=7)
        
        papers = db.query(Paper).filter(
            Paper.created_at >= week_ago
        ).order_by(desc(Paper.created_at)).all()
        
        report = f"""# Weekly Paper Report - {datetime.now().strftime('%Y-%m-%d')}

## Summary
- **Papers Added This Week:** {len(papers)}

## Papers

"""
        for paper in papers:
            report += f"- **{paper.title}** ({paper.arxiv_id})\n"
        
        report_obj = Report(report_type="weekly", content=report)
        db.add(report_obj)
        db.commit()
        
        return report
    finally:
        db.close()
