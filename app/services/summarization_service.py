"""Business logic for paper summarization"""
from sqlalchemy.orm import Session
from app.models import Paper
from app.repositories import PaperRepository
from app.orchestrator import summarization_client
from app.exceptions import PaperNotFoundException, MCPException
from app.config import settings
from typing import Dict, Any

class SummarizationService:
    """Service layer for summarization operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.paper_repo = PaperRepository(db)
    
    def get_summary(self, paper_id: int, force_llm: bool = False) -> Dict[str, Any]:
        """Get or generate summary for a paper"""
        paper = self.paper_repo.get_by_id(paper_id)
        if not paper:
            raise PaperNotFoundException(f"Paper {paper_id} not found")
        
        # Return existing summary if available
        if paper.summary and not force_llm:
            return {
                "paper_id": paper_id,
                "summary": paper.summary,
                "source": "cached"
            }
        
        # Use abstract if available and not forcing LLM
        if not force_llm and paper.abstract and len(paper.abstract.strip()) > settings.MIN_ABSTRACT_LENGTH:
            paper.summary = paper.abstract
            self.paper_repo.update(paper)
            return {
                "paper_id": paper_id,
                "summary": paper.abstract,
                "source": "abstract"
            }
        
        # Generate with LLM
        try:
            result = summarization_client.call("summarize_abstract", {
                "paper_id": paper_id
            })
            
            summary_text = result.get("summary", "")
            paper.summary = summary_text
            self.paper_repo.update(paper)
            
            return {
                "paper_id": paper_id,
                "summary": summary_text,
                "source": "llm"
            }
        except Exception as e:
            raise MCPException(f"Summarization failed: {str(e)}")
    
    def generate_tldr(self, paper_id: int) -> Dict[str, Any]:
        """Generate one-sentence TLDR"""
        paper = self.paper_repo.get_by_id(paper_id)
        if not paper:
            raise PaperNotFoundException(f"Paper {paper_id} not found")
        
        try:
            result = summarization_client.call("generate_tldr", {
                "paper_id": paper_id
            })
            return {
                "paper_id": paper_id,
                "tldr": result.get("tldr", "")
            }
        except Exception as e:
            raise MCPException(f"TLDR generation failed: {str(e)}")
    
    def extract_key_points(self, paper_id: int) -> Dict[str, Any]:
        """Extract key points from paper"""
        paper = self.paper_repo.get_by_id(paper_id)
        if not paper:
            raise PaperNotFoundException(f"Paper {paper_id} not found")
        
        try:
            result = summarization_client.call("extract_key_points", {
                "paper_id": paper_id
            })
            return {
                "paper_id": paper_id,
                "key_points": result.get("points", "")
            }
        except Exception as e:
            raise MCPException(f"Key point extraction failed: {str(e)}")
    
    def generate_detailed_analysis(self, paper_id: int) -> Dict[str, Any]:
        """Generate detailed analysis"""
        paper = self.paper_repo.get_by_id(paper_id)
        if not paper:
            raise PaperNotFoundException(f"Paper {paper_id} not found")
        
        try:
            result = summarization_client.call("summarize_detailed", {
                "paper_id": paper_id
            })
            return {
                "paper_id": paper_id,
                "detailed_analysis": result.get("summary", "")
            }
        except Exception as e:
            raise MCPException(f"Detailed analysis failed: {str(e)}")
