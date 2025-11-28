#!/usr/bin/env python3
import json
import sys
import os
import warnings
import io
from typing import Any

warnings.filterwarnings('ignore')

# Suppress stdout/stderr during imports
_original_stdout = sys.stdout
_original_stderr = sys.stderr
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    model = genai.GenerativeModel('gemini-2.0-flash')
finally:
    sys.stdout = _original_stdout
    sys.stderr = _original_stderr

def read_message():
    line = sys.stdin.readline()
    return json.loads(line) if line else None

def write_message(msg: dict[str, Any]):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def classify_paper(title: str, abstract: str, existing_categories: list[str]) -> dict:
    """Classify paper into multiple categories using LLM"""
    
    categories = ["AI", "singlecell", "longread", "methods", "benchmark", "dataset", 
                  "epigenetics", "transcriptomics", "genomics", "microbial", "ecology",
                  "spatial", "assembly", "alignment", "isoforms", "splicing", "cancer", "immunology"]
    
    prompt = f"""Classify this research paper into relevant categories. Select ALL applicable categories.

Categories:
- AI: artificial intelligence, machine learning, deep learning, neural networks
- singlecell: single-cell sequencing, scRNA-seq, cell types
- longread: long-read sequencing, nanopore, PacBio
- methods: new methods, algorithms, tools, frameworks
- benchmark: benchmarking, comparison studies, evaluations
- dataset: new datasets, databases, data collections
- epigenetics: DNA methylation, histone modifications, chromatin
- transcriptomics: RNA-seq, gene expression, transcriptome
- genomics: genome sequencing, DNA analysis, variants
- microbial: bacteria, microbiome, pathogens
- ecology: ecosystems, biodiversity, species
- spatial: spatial transcriptomics, spatial omics, tissue mapping
- assembly: genome assembly, sequence assembly, scaffolding
- alignment: sequence alignment, mapping, read alignment
- isoforms: alternative splicing, transcript isoforms, variants
- splicing: RNA splicing, splice sites, splicing regulation
- cancer: oncology, tumors, cancer biology, cancer genomics
- immunology: immune system, T cells, B cells, antibodies

Paper:
Title: {title}
Abstract: {abstract[:500]}

Return ONLY a JSON array of category names. Example: ["AI", "methods"]"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Remove markdown code blocks if present
        if '```' in text:
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        
        # Extract JSON array
        text = text.strip()
        result = json.loads(text)
        
        # Validate categories
        valid_cats = [c for c in result if c in categories]
        return {"categories": valid_cats}
    except Exception as e:
        return {"categories": []}

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
