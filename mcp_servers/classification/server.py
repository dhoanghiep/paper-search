#!/usr/bin/env python3
import json
import sys
from typing import Any

def read_message():
    line = sys.stdin.readline()
    return json.loads(line) if line else None

def write_message(msg: dict[str, Any]):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def classify_paper(title: str, abstract: str, existing_categories: list[str]) -> dict:
    """Classify paper into existing category or suggest new one"""
    keywords = (title + " " + abstract).lower()
    
    # Simple keyword matching
    category_keywords = {
        "machine learning": ["learning", "neural", "model", "training"],
        "computer vision": ["image", "vision", "visual", "detection"],
        "nlp": ["language", "text", "nlp", "linguistic"],
        "robotics": ["robot", "autonomous", "control"],
        "security": ["security", "attack", "vulnerability", "encryption"]
    }
    
    scores = {}
    for cat in existing_categories:
        cat_lower = cat.lower()
        if cat_lower in category_keywords:
            scores[cat] = sum(1 for kw in category_keywords[cat_lower] if kw in keywords)
    
    if scores and max(scores.values()) > 0:
        return {"category": max(scores, key=scores.get), "confidence": "existing"}
    
    # Suggest new category based on keywords
    for cat, kws in category_keywords.items():
        if sum(1 for kw in kws if kw in keywords) >= 2:
            return {"category": cat, "confidence": "suggested"}
    
    return {"category": "uncategorized", "confidence": "low"}

def handle_request(req: dict) -> dict:
    method = req.get("method")
    params = req.get("params", {})
    
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "classification-server", "version": "1.0.0"}
        }
    
    if method == "tools/list":
        return {
            "tools": [{
                "name": "classify_paper",
                "description": "Classify paper into existing or new category",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "abstract": {"type": "string"},
                        "existing_categories": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["title", "abstract", "existing_categories"]
                }
            }]
        }
    
    if method == "tools/call":
        tool = params.get("name")
        args = params.get("arguments", {})
        
        if tool == "classify_paper":
            result = classify_paper(
                args.get("title", ""),
                args.get("abstract", ""),
                args.get("existing_categories", [])
            )
            return {
                "content": [{"type": "text", "text": json.dumps(result)}]
            }
    
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
