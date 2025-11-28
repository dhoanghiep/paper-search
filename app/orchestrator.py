import json
import subprocess
import os
import sys
from typing import Dict, Any, List

class MCPClient:
    """Client to communicate with MCP servers via stdin/stdout"""
    
    def __init__(self, server_path: str):
        self.server_path = server_path
        self.python_path = sys.executable
    
    def call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP server tool"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": method,
                "arguments": params
            }
        }
        
        result = subprocess.run(
            [self.python_path, self.server_path],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            env=os.environ.copy()
        )
        
        if result.returncode != 0:
            raise Exception(f"MCP call failed: {result.stderr}")
        
        response = json.loads(result.stdout)
        if "error" in response:
            raise Exception(f"MCP error: {response['error']}")
        
        content = response.get("result", {}).get("content", [])
        if content and content[0].get("type") == "text":
            return json.loads(content[0]["text"])
        return response.get("result", {})

# Initialize MCP clients
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
classification_client = MCPClient(os.path.join(BASE_DIR, "mcp_servers/classification/server.py"))
summarization_client = MCPClient(os.path.join(BASE_DIR, "mcp_servers/summarization/server.py"))
reports_client = MCPClient(os.path.join(BASE_DIR, "mcp_servers/reports/server.py"))
email_client = MCPClient(os.path.join(BASE_DIR, "mcp_servers/email/server.py"))

class PaperOrchestrator:
    """Orchestrates paper processing through MCP services"""
    
    def __init__(self):
        self.classification = classification_client
        self.summarization = summarization_client
        self.reports = reports_client
        self.email = email_client
    
    def process_paper(self, paper_id: int) -> Dict[str, Any]:
        """Process a single paper through classification and summarization"""
        from app.database import SessionLocal
        from app.models import Paper
        from app.repositories import PaperRepository, CategoryRepository
        
        db = SessionLocal()
        try:
            paper_repo = PaperRepository(db)
            category_repo = CategoryRepository(db)
            
            paper = paper_repo.get_by_id(paper_id)
            if not paper:
                raise Exception(f"Paper {paper_id} not found")
            
            # Get existing categories
            categories = [c.name for c in paper.categories]
            
            # Classify
            classification = self.classification.call("classify_paper", {
                "title": paper.title,
                "abstract": paper.abstract,
                "existing_categories": categories
            })
            
            # Add multiple categories
            category_names = classification.get("categories", [])
            for category_name in category_names:
                if category_name:
                    category = category_repo.get_or_create(category_name)
                    if category not in paper.categories:
                        paper.categories.append(category)
            
            # Use abstract as summary if available, otherwise use LLM
            if paper.abstract and len(paper.abstract.strip()) > 50:
                summary_text = paper.abstract
                summary = {"summary": summary_text, "source": "abstract"}
            else:
                summary = self.summarization.call("summarize_abstract", {
                    "paper_id": paper_id
                })
                summary["source"] = "llm"
            
            # Update paper
            paper.summary = summary.get("summary", "")
            paper_repo.update(paper)
            
            return {
                "paper_id": paper_id,
                "classification": classification,
                "summary": summary
            }
        finally:
            db.close()
    
    def bulk_process(self, paper_ids: List[int]) -> Dict[str, Any]:
        """Process multiple papers with progress tracking"""
        results = {"processed": 0, "errors": 0, "details": []}
        
        for paper_id in paper_ids:
            try:
                result = self.process_paper(paper_id)
                results["processed"] += 1
                results["details"].append({"paper_id": paper_id, "status": "success"})
            except Exception as e:
                results["errors"] += 1
                results["details"].append({"paper_id": paper_id, "status": "error", "error": str(e)})
        
        return results
    
    def generate_insights(self, start_date, end_date, categories: List[str] = None) -> Dict[str, Any]:
        """Generate cross-paper insights for date range and categories"""
        from app.database import SessionLocal
        from app.repositories import PaperRepository
        from datetime import datetime
        
        db = SessionLocal()
        try:
            paper_repo = PaperRepository(db)
            
            start = datetime.strptime(start_date, "%Y-%m-%d") if isinstance(start_date, str) else start_date
            end = datetime.strptime(end_date, "%Y-%m-%d") if isinstance(end_date, str) else end_date
            
            papers = paper_repo.filter_by_date_range(start, end, categories)
            
            if not papers:
                return {"error": "No papers found for criteria"}
            
            papers_data = []
            for p in papers:
                papers_data.append({
                    "title": p.title,
                    "authors": p.authors,
                    "published_date": p.published_date.strftime("%Y-%m-%d"),
                    "categories": ", ".join([c.name for c in p.categories]),
                    "summary": p.summary
                })
            
            report = self.reports.call("generate_llm_report", {
                "papers_data": papers_data,
                "start_date": start_date if isinstance(start_date, str) else start_date.strftime("%Y-%m-%d"),
                "end_date": end_date if isinstance(end_date, str) else end_date.strftime("%Y-%m-%d"),
                "categories": categories or []
            })
            
            return report
        finally:
            db.close()

# Create singleton instance
orchestrator = PaperOrchestrator()

# Backward compatibility functions
def process_paper(paper_id: int) -> Dict[str, Any]:
    """Process a paper - backward compatible function"""
    return orchestrator.process_paper(paper_id)
