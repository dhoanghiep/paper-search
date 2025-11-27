#!/usr/bin/env python3
import asyncio
import json
import sys
from typing import Any
import httpx
import xml.etree.ElementTree as ET
from datetime import datetime

async def search_papers(query: str, max_results: int = 10) -> dict[str, Any]:
    """Search arXiv papers by query"""
    params = {
        "search_query": f"all:{query}",
        "sortBy": "relevance",
        "max_results": max_results
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get("https://export.arxiv.org/api/query", params=params)
        await asyncio.sleep(0.34)
        return {"papers": parse_arxiv_xml(response.text)}

async def get_recent_papers(category: str = "all", max_results: int = 10) -> dict[str, Any]:
    """Get recent papers from arXiv"""
    query = f"cat:{category}" if category != "all" else "all"
    params = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get("https://export.arxiv.org/api/query", params=params)
        await asyncio.sleep(0.34)
        return {"papers": parse_arxiv_xml(response.text)}

async def get_paper_details(arxiv_id: str) -> dict[str, Any]:
    """Get detailed metadata for a specific paper"""
    params = {"id_list": arxiv_id}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get("https://export.arxiv.org/api/query", params=params)
        await asyncio.sleep(0.34)
        papers = parse_arxiv_xml(response.text)
        return papers[0] if papers else {"error": "Paper not found"}

def parse_arxiv_xml(xml_text: str) -> list[dict]:
    """Parse arXiv API XML response"""
    root = ET.fromstring(xml_text)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    papers = []
    for entry in root.findall('atom:entry', ns):
        arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
        title = entry.find('atom:title', ns).text.strip()
        abstract = entry.find('atom:summary', ns).text.strip()
        published = entry.find('atom:published', ns).text
        authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
        pdf_link = next((link.get('href') for link in entry.findall('atom:link', ns) if link.get('title') == 'pdf'), None)
        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "published": published,
            "pdf_url": pdf_link
        })
    return papers

async def handle_request(request: dict) -> dict:
    """Handle MCP tool requests"""
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "search_papers":
        return await search_papers(params.get("query", ""), params.get("max_results", 10))
    elif method == "get_recent_papers":
        return await get_recent_papers(params.get("category", "all"), params.get("max_results", 10))
    elif method == "get_paper_details":
        return await get_paper_details(params["arxiv_id"])
    else:
        return {"error": f"Unknown method: {method}"}

async def main():
    """MCP server main loop"""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line)
            result = await handle_request(request)
            print(json.dumps(result), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
