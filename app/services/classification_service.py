"""Business logic for paper classification"""
from sqlalchemy.orm import Session
from app.models import Paper
from app.repositories import PaperRepository, CategoryRepository
from app.orchestrator import classification_client
from app.exceptions import PaperNotFoundException, MCPException
from typing import List, Dict, Any

class ClassificationService:
    """Service layer for classification operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.paper_repo = PaperRepository(db)
        self.category_repo = CategoryRepository(db)
    
    def classify_paper(self, paper_id: int) -> Dict[str, Any]:
        """Classify a paper and assign categories"""
        paper = self.paper_repo.get_by_id(paper_id)
        if not paper:
            raise PaperNotFoundException(f"Paper {paper_id} not found")
        
        # Get existing categories
        existing_categories = [c.name for c in paper.categories]
        
        try:
            # Call MCP classification service
            result = classification_client.call("classify_paper", {
                "title": paper.title,
                "abstract": paper.abstract,
                "existing_categories": existing_categories
            })
            
            # Add new categories
            category_names = result.get("categories", [])
            added_categories = []
            
            for category_name in category_names:
                if category_name and category_name not in existing_categories:
                    category = self.category_repo.get_or_create(category_name)
                    if category not in paper.categories:
                        paper.categories.append(category)
                        added_categories.append(category_name)
            
            self.paper_repo.update(paper)
            
            return {
                "paper_id": paper_id,
                "existing_categories": existing_categories,
                "new_categories": added_categories,
                "all_categories": [c.name for c in paper.categories]
            }
            
        except Exception as e:
            raise MCPException(f"Classification failed: {str(e)}")
    
    def bulk_classify(self, paper_ids: List[int]) -> Dict[str, Any]:
        """Classify multiple papers"""
        results = {"processed": 0, "errors": 0, "details": []}
        
        for paper_id in paper_ids:
            try:
                result = self.classify_paper(paper_id)
                results["processed"] += 1
                results["details"].append(result)
            except Exception as e:
                results["errors"] += 1
                results["details"].append({
                    "paper_id": paper_id,
                    "error": str(e)
                })
        
        return results
    
    def get_category_statistics(self) -> Dict[str, Any]:
        """Get statistics about categories"""
        categories = self.category_repo.get_all()
        
        stats = {
            "total_categories": len(categories),
            "categories": []
        }
        
        for cat in categories:
            stats["categories"].append({
                "name": cat.name,
                "paper_count": len(cat.papers),
                "description": cat.description
            })
        
        # Sort by paper count
        stats["categories"].sort(key=lambda x: x["paper_count"], reverse=True)
        
        return stats
