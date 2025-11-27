#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from typing import Any

def read_message():
    line = sys.stdin.readline()
    return json.loads(line) if line else None

def write_message(msg: dict[str, Any]):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def generate_paper_report(paper: dict, depth: str) -> str:
    """Generate brief or in-depth report for a paper"""
    title = paper.get('title', 'Untitled')
    authors = paper.get('authors', [])
    abstract = paper.get('abstract', '')
    
    if depth == 'brief':
        return f"**{title}**\nAuthors: {', '.join(authors)}\n\n{abstract[:200]}..."
    
    return f"""# {title}

**Authors:** {', '.join(authors)}
**Published:** {paper.get('published', 'N/A')}
**Category:** {paper.get('category', 'N/A')}

## Abstract
{abstract}

## Key Points
{paper.get('summary', 'No summary available')}
"""

def generate_period_report(papers: list[dict], period: str) -> str:
    """Generate daily, weekly, or monthly report"""
    count = len(papers)
    categories = {}
    for p in papers:
        cat = p.get('category', 'uncategorized')
        categories[cat] = categories.get(cat, 0) + 1
    
    report = f"# {period.capitalize()} Paper Report\n"
    report += f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n"
    report += f"**Total Papers:** {count}\n\n"
    
    report += "## Categories\n"
    for cat, cnt in sorted(categories.items(), key=lambda x: -x[1]):
        report += f"- {cat}: {cnt}\n"
    
    report += "\n## Papers\n"
    for p in papers:
        report += f"\n### {p.get('title', 'Untitled')}\n"
        report += f"*{', '.join(p.get('authors', []))}*\n"
        report += f"{p.get('abstract', '')[:150]}...\n"
    
    return report

def handle_request(req: dict) -> dict:
    method = req.get("method")
    params = req.get("params", {})
    
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "reports-server", "version": "1.0.0"}
        }
    
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "generate_paper_report",
                    "description": "Generate brief or in-depth report for a single paper",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "paper": {"type": "object"},
                            "depth": {"type": "string", "enum": ["brief", "in-depth"]}
                        },
                        "required": ["paper", "depth"]
                    }
                },
                {
                    "name": "generate_period_report",
                    "description": "Generate daily, weekly, or monthly report",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "papers": {"type": "array"},
                            "period": {"type": "string", "enum": ["daily", "weekly", "monthly"]}
                        },
                        "required": ["papers", "period"]
                    }
                }
            ]
        }
    
    if method == "tools/call":
        tool = params.get("name")
        args = params.get("arguments", {})
        
        if tool == "generate_paper_report":
            result = generate_paper_report(args.get("paper", {}), args.get("depth", "brief"))
            return {"content": [{"type": "text", "text": result}]}
        
        if tool == "generate_period_report":
            result = generate_period_report(args.get("papers", []), args.get("period", "daily"))
            return {"content": [{"type": "text", "text": result}]}
    
    return {"error": "Unknown method"}

def main():
    while True:
        msg = read_message()
        if not msg:
            break
        
        response = {"jsonrpc": "2.0", "id": msg.get("id")}
        response["result"] = handle_request(msg)
        write_message(response)

if __name__ == "__main__":
    main()
