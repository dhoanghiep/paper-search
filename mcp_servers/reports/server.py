#!/usr/bin/env python3
import json
import sys
import os
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

def generate_llm_report(papers_data: list[dict], start_date: str, end_date: str, categories: list[str]) -> str:
    """Generate comprehensive LLM-based report"""
    import google.generativeai as genai
    
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Prepare summaries
    summaries_text = ""
    for i, paper in enumerate(papers_data, 1):
        summaries_text += f"\n{i}. {paper['title']}\n"
        summaries_text += f"   Categories: {paper.get('categories', 'Uncategorized')}\n"
        summaries_text += f"   Published: {paper.get('published_date', 'N/A')}\n"
        summaries_text += f"   Summary: {paper.get('summary', 'No summary')[:500]}...\n"
    
    prompt = f"""Generate a comprehensive research report based on these papers published between {start_date} and {end_date}.

Categories: {', '.join(categories) if categories else 'All'}
Number of papers: {len(papers_data)}

Papers and their summaries:
{summaries_text}

Please provide:
1. Executive Summary (2-3 paragraphs)
2. Key Themes and Trends
3. Notable Findings by Category
4. Emerging Research Directions
5. Conclusion

Format the report in markdown."""

    response = model.generate_content(prompt)
    return response.text

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
                },
                {
                    "name": "generate_llm_report",
                    "description": "Generate comprehensive LLM-based research report",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "papers_data": {"type": "array"},
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                            "categories": {"type": "array"}
                        },
                        "required": ["papers_data", "start_date", "end_date", "categories"]
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
        
        if tool == "generate_llm_report":
            result = generate_llm_report(
                args.get("papers_data", []),
                args.get("start_date", ""),
                args.get("end_date", ""),
                args.get("categories", [])
            )
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
