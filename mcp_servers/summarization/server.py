#!/usr/bin/env python3
import json
import sys
import os
import warnings
import io
warnings.filterwarnings('ignore')

# Capture stdout/stderr during imports to suppress library errors
_original_stdout = sys.stdout
_original_stderr = sys.stderr
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

try:
    import google.generativeai as genai
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import Paper
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://paper_user:paper_pass@localhost:5432/paper_search")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    model = genai.GenerativeModel('gemini-2.0-flash')
finally:
    # Restore stdout/stderr
    sys.stdout = _original_stdout
    sys.stderr = _original_stderr

def call_llm(prompt):
    response = model.generate_content(prompt)
    return response.text

def get_paper(paper_id):
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise Exception("Paper not found")
        return paper
    finally:
        db.close()

def summarize_abstract(paper_id):
    paper = get_paper(int(paper_id))
    prompt = f"Summarize in 2-3 sentences:\nTitle: {paper.title}\nAbstract: {paper.abstract}"
    return {"summary": call_llm(prompt)}

def summarize_detailed(paper_id):
    paper = get_paper(int(paper_id))
    prompt = f"Provide detailed analysis with main contribution, methodology, key findings, implications:\nTitle: {paper.title}\nAbstract: {paper.abstract}"
    return {"summary": call_llm(prompt)}

def extract_key_points(paper_id):
    paper = get_paper(int(paper_id))
    prompt = f"Extract 5-7 key points as bullet list:\nTitle: {paper.title}\nAbstract: {paper.abstract}"
    return {"points": call_llm(prompt)}

def generate_tldr(paper_id):
    paper = get_paper(int(paper_id))
    prompt = f"One sentence summary:\nTitle: {paper.title}\nAbstract: {paper.abstract}"
    return {"tldr": call_llm(prompt)}

def batch_summarize(paper_ids):
    summaries = {}
    for pid in paper_ids:
        try:
            summaries[str(pid)] = summarize_abstract(pid)["summary"]
        except Exception as e:
            summaries[str(pid)] = f"Error: {str(e)}"
    return {"summaries": summaries}

TOOLS = {
    "summarize_abstract": {"description": "Brief 2-3 sentence summary", "params": ["paper_id"]},
    "summarize_detailed": {"description": "Detailed analysis", "params": ["paper_id"]},
    "extract_key_points": {"description": "Extract key points", "params": ["paper_id"]},
    "generate_tldr": {"description": "One sentence summary", "params": ["paper_id"]},
    "batch_summarize": {"description": "Summarize multiple papers", "params": ["paper_ids"]}
}

def handle_message(msg):
    method = msg.get("method")
    params = msg.get("params", {})
    msg_id = msg.get("id")
    
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"protocolVersion": "1.0", "serverInfo": {"name": "summarization", "version": "1.0"}}}
    elif method == "tools/list":
        tools = [{"name": name, "description": info["description"], "inputSchema": {"type": "object", "properties": {p: {"type": "string"} for p in info["params"]}}} for name, info in TOOLS.items()]
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": tools}}
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        try:
            result = globals()[tool_name](**args)
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": json.dumps(result)}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -1, "message": str(e)}}
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -1, "message": "Unknown method"}}

if __name__ == "__main__":
    for line in sys.stdin:
        msg = json.loads(line)
        response = handle_message(msg)
        print(json.dumps(response), flush=True)
