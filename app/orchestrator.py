import json
import subprocess
import os
from typing import Dict, Any

class MCPClient:
    """Client to communicate with MCP servers via stdin/stdout"""
    
    def __init__(self, server_path: str):
        self.server_path = server_path
        self.python_path = os.path.join(os.path.dirname(__file__), '../venv/bin/python3')
    
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
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"MCP call failed: {result.stderr}")
        
        response = json.loads(result.stdout)
        if "error" in response:
            raise Exception(f"MCP error: {response['error']}")
        
        # Extract text from content array
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

def process_paper(paper_id: int) -> Dict[str, Any]:
    """Process a paper through classification and summarization"""
    from app.database import SessionLocal
    from app.models import Paper
    
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise Exception(f"Paper {paper_id} not found")
        
        # Get existing categories
        categories = [c.name for c in paper.categories]
        
        # Classify
        classification = classification_client.call("classify_paper", {
            "title": paper.title,
            "abstract": paper.abstract,
            "existing_categories": categories
        })
        
        # Summarize
        summary = summarization_client.call("summarize_abstract", {
            "title": paper.title,
            "abstract": paper.abstract
        })
        
        # Update paper
        paper.summary = summary.get("summary", "")
        db.commit()
        
        return {
            "paper_id": paper_id,
            "classification": classification,
            "summary": summary
        }
    finally:
        db.close()
