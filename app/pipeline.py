from app.database import SessionLocal
from app.models import Paper
from app.orchestrator import process_paper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_new_papers(limit: int = 10) -> dict:
    """Process papers that haven't been summarized yet"""
    db = SessionLocal()
    try:
        # Find papers without summaries
        papers = db.query(Paper).filter(
            (Paper.summary == None) | (Paper.summary == "")
        ).limit(limit).all()
        
        results = {"processed": 0, "errors": 0, "paper_ids": []}
        
        for paper in papers:
            try:
                logger.info(f"Processing paper {paper.id}: {paper.title}")
                result = process_paper(paper.id)
                results["processed"] += 1
                results["paper_ids"].append(paper.id)
                logger.info(f"Successfully processed paper {paper.id}")
            except Exception as e:
                logger.error(f"Error processing paper {paper.id}: {e}")
                results["errors"] += 1
        
        return results
    finally:
        db.close()

if __name__ == "__main__":
    result = process_new_papers()
    print(f"Processed: {result['processed']}, Errors: {result['errors']}")
