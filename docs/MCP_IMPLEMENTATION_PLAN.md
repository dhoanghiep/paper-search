# MCP Servers Implementation Plan

**Created:** 2025-11-27  
**Status:** 2/6 Completed

---

## Progress Overview

| Server | Status | Priority | Time Est. |
|--------|--------|----------|-----------|
| ArXiv | ✅ Done | 1 | - |
| Database | ✅ Done | 2 | - |
| Classification | 🚧 Boilerplate | 3 | 2-3h |
| Summarization | 🚧 Boilerplate | 4 | 2-3h |
| Reports | 🚧 Boilerplate | 5 | 2h |
| Email | 🚧 Boilerplate | 6 | 1-2h |

---

## Implementation Order

### Phase 1: Classification (NEXT)
**Why first:** Most useful for organizing existing 10 papers, no external dependencies

**Tasks:**
1. Add database connection to server.py
2. Implement keyword matching against TAXONOMY
3. Test with existing papers
4. Store classifications in DB

**Files to modify:**
- `mcp_servers/classification/server.py`

---

### Phase 2: Summarization
**Why second:** Requires LLM decision, adds value to papers

**Decision needed:** Choose LLM provider
- AWS Bedrock (boto3) - Production ready
- OpenAI API (openai) - Easy setup
- Local Ollama - Free, slower

**Tasks:**
1. Choose and configure LLM provider
2. Add database connection
3. Implement prompt templates
4. Test with sample papers
5. Store summaries in DB

**Files to modify:**
- `mcp_servers/summarization/server.py`
- `.env` (add API keys)

---

### Phase 3: Reports
**Why third:** Builds on classification data

**Tasks:**
1. Add database connection
2. Create markdown templates
3. Implement date filtering
4. Test report generation

**Files to modify:**
- `mcp_servers/reports/server.py`

---

### Phase 4: Email (Optional)
**Why last:** Optional feature, can be skipped

**Tasks:**
1. Configure SMTP credentials
2. Create HTML email templates
3. Implement email sending
4. Test with real email

**Files to modify:**
- `mcp_servers/email/server.py`
- `.env` (add SMTP credentials)

---

## Common Implementation Pattern

All servers follow this structure:

```python
#!/usr/bin/env python3
import json
import sys

def tool_function(param1, param2):
    # Implementation
    return {"result": "data"}

TOOLS = {
    "tool_name": tool_function
}

def main():
    request = json.loads(sys.stdin.read())
    method = request.get("method")
    params = request.get("params", {})
    
    if method in TOOLS:
        result = TOOLS[method](**params)
        print(json.dumps({"result": result}))
    else:
        print(json.dumps({"error": f"Unknown method: {method}"}))

if __name__ == "__main__":
    main()
```

---

## Database Connection Template

Add to each server that needs DB access:

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/paper_search")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
```

---

## Testing Strategy

1. **Unit test each tool** with echo/stdin
2. **Integration test** with real database
3. **End-to-end test** full workflow

Example test:
```bash
echo '{"method": "classify_paper", "params": {"paper_id": 1}}' | python mcp_servers/classification/server.py
```

---

## Success Criteria

- [ ] All 6 servers have working implementations
- [ ] Each tool returns valid JSON
- [ ] Database operations work correctly
- [ ] Error handling in place
- [ ] Documentation updated
- [ ] Basic testing completed

---

## Next Action

Start with Classification MCP Server - implement keyword matching algorithm.
