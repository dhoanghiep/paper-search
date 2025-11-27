# Phase 3: MCP Servers - Detailed Implementation Plan

**Start Date:** 2025-11-27  
**Estimated Duration:** 8-12 hours  
**Priority:** HIGH

---

## Overview

Build 6 MCP servers to extend functionality through Model Context Protocol integration with Kiro CLI.

---

## MCP Server 1: ArXiv MCP Server ⭐ PRIORITY 1

**Purpose:** Expose arXiv scraping as MCP tools  
**Estimated Time:** 1-2 hours

### Implementation Steps

1. **Setup MCP Server Structure**
   ```
   mcp_servers/
   └── arxiv/
       ├── __init__.py
       ├── server.py
       ├── tools.py
       └── config.json
   ```

2. **Tools to Implement**
   - `search_papers(query, max_results)` - Search arXiv by keywords
   - `get_recent_papers(category, max_results)` - Get latest papers
   - `get_paper_details(arxiv_id)` - Get full paper metadata
   - `scrape_and_store(max_results)` - Scrape and save to DB

3. **Configuration**
   ```json
   {
     "name": "arxiv-mcp",
     "version": "1.0.0",
     "tools": ["search_papers", "get_recent_papers", "get_paper_details", "scrape_and_store"]
   }
   ```

4. **Testing**
   - Test each tool independently
   - Verify rate limiting works
   - Test with Kiro CLI

**Deliverables:**
- [ ] MCP server running on port 3001
- [ ] 4 tools implemented and tested
- [ ] Integration with existing scraper code
- [ ] Documentation in README

---

## MCP Server 2: Database MCP Server ⭐ PRIORITY 2

**Purpose:** Query and manage papers database  
**Estimated Time:** 2-3 hours

### Implementation Steps

1. **Setup Structure**
   ```
   mcp_servers/
   └── database/
       ├── __init__.py
       ├── server.py
       ├── tools.py
       └── config.json
   ```

2. **Tools to Implement**
   - `query_papers(filters, limit, offset)` - Search papers with filters
   - `get_paper(paper_id)` - Get single paper
   - `add_paper(paper_data)` - Insert new paper
   - `update_paper(paper_id, updates)` - Update paper
   - `delete_paper(paper_id)` - Remove paper
   - `get_categories()` - List all categories
   - `add_category(name, description)` - Create category
   - `assign_category(paper_id, category_id)` - Link paper to category
   - `get_statistics()` - Database stats (counts, recent activity)

3. **Query Filters**
   - By date range
   - By category
   - By author
   - By keyword in title/abstract
   - Sort options (date, relevance)

4. **Testing**
   - CRUD operations
   - Complex queries
   - Performance with 100+ papers

**Deliverables:**
- [ ] MCP server running on port 3002
- [ ] 9 tools implemented
- [ ] Query optimization
- [ ] Error handling for DB operations

---

## MCP Server 3: Summarization MCP Server ⭐ PRIORITY 3

**Purpose:** Generate AI summaries of papers  
**Estimated Time:** 2-3 hours

### Implementation Steps

1. **Setup Structure**
   ```
   mcp_servers/
   └── summarization/
       ├── __init__.py
       ├── server.py
       ├── tools.py
       ├── prompts.py
       └── config.json
   ```

2. **LLM Integration Options**
   - **Option A:** AWS Bedrock (Claude 3)
   - **Option B:** OpenAI API
   - **Option C:** Local LLM (Ollama)

3. **Tools to Implement**
   - `summarize_abstract(paper_id)` - Brief summary (2-3 sentences)
   - `summarize_detailed(paper_id)` - In-depth analysis (1 paragraph)
   - `extract_key_points(paper_id)` - Bullet points (5-7 items)
   - `generate_tldr(paper_id)` - One-sentence summary
   - `batch_summarize(paper_ids)` - Summarize multiple papers

4. **Prompt Templates**
   ```python
   BRIEF_SUMMARY = """
   Summarize this research paper abstract in 2-3 sentences:
   Title: {title}
   Abstract: {abstract}
   """
   
   DETAILED_SUMMARY = """
   Provide a detailed analysis of this paper including:
   - Main contribution
   - Methodology
   - Key findings
   - Implications
   
   Title: {title}
   Abstract: {abstract}
   """
   ```

5. **Testing**
   - Test with sample papers
   - Verify summary quality
   - Check token usage/costs

**Deliverables:**
- [ ] MCP server running on port 3003
- [ ] 5 tools implemented
- [ ] LLM integration working
- [ ] Prompt templates optimized
- [ ] Cost tracking (if using paid API)

---

## MCP Server 4: Classification MCP Server ⭐ PRIORITY 4

**Purpose:** Auto-categorize papers  
**Estimated Time:** 2-3 hours

### Implementation Steps

1. **Setup Structure**
   ```
   mcp_servers/
   └── classification/
       ├── __init__.py
       ├── server.py
       ├── tools.py
       ├── taxonomy.py
       └── config.json
   ```

2. **Category Taxonomy**
   ```python
   CATEGORIES = {
       "Machine Learning": ["deep learning", "neural networks", "transformers"],
       "Computer Vision": ["image processing", "object detection", "segmentation"],
       "NLP": ["language models", "text generation", "sentiment analysis"],
       "Robotics": ["autonomous systems", "control", "manipulation"],
       "Theory": ["algorithms", "complexity", "optimization"],
       # ... more categories
   }
   ```

3. **Tools to Implement**
   - `classify_paper(paper_id)` - Auto-assign categories
   - `suggest_category(paper_id)` - Suggest new category
   - `find_similar_papers(paper_id, limit)` - Find related papers
   - `get_category_distribution()` - Stats on categories
   - `reclassify_all()` - Batch reclassification

4. **Classification Methods**
   - **Method 1:** Keyword matching (fast, simple)
   - **Method 2:** LLM-based (accurate, slower)
   - **Method 3:** Embedding similarity (balanced)

5. **Testing**
   - Test accuracy on known papers
   - Verify similar paper recommendations
   - Performance benchmarks

**Deliverables:**
- [ ] MCP server running on port 3004
- [ ] 5 tools implemented
- [ ] Category taxonomy defined
- [ ] Classification accuracy >80%

---

## MCP Server 5: Report Generation MCP Server

**Purpose:** Create daily/weekly/monthly reports  
**Estimated Time:** 2 hours

### Implementation Steps

1. **Setup Structure**
   ```
   mcp_servers/
   └── reports/
       ├── __init__.py
       ├── server.py
       ├── tools.py
       ├── templates.py
       └── config.json
   ```

2. **Tools to Implement**
   - `generate_daily_report()` - Papers from last 24h
   - `generate_weekly_report()` - Weekly digest
   - `generate_monthly_report()` - Monthly summary
   - `generate_paper_report(paper_id, depth)` - Single paper report
   - `generate_category_report(category_id)` - Category-specific report

3. **Report Templates**
   - Markdown format
   - HTML format
   - PDF format (optional)

4. **Report Contents**
   - Summary statistics
   - Top papers
   - Category breakdown
   - Trending topics
   - Key findings

5. **Testing**
   - Generate sample reports
   - Verify formatting
   - Check data accuracy

**Deliverables:**
- [ ] MCP server running on port 3005
- [ ] 5 tools implemented
- [ ] Report templates created
- [ ] Export formats working

---

## MCP Server 6: Email Notification MCP Server

**Purpose:** Send email alerts  
**Estimated Time:** 1-2 hours

### Implementation Steps

1. **Setup Structure**
   ```
   mcp_servers/
   └── email/
       ├── __init__.py
       ├── server.py
       ├── tools.py
       ├── templates.py
       └── config.json
   ```

2. **Tools to Implement**
   - `send_new_paper_alert(paper_ids, recipients)` - New paper notification
   - `send_report(report_id, recipients)` - Email report
   - `send_digest(frequency, recipients)` - Daily/weekly digest
   - `configure_alerts(user_id, preferences)` - Set preferences

3. **Email Templates**
   - New paper alert (HTML)
   - Daily digest (HTML)
   - Weekly summary (HTML)

4. **SMTP Configuration**
   - Gmail SMTP
   - AWS SES (optional)
   - SendGrid (optional)

5. **Testing**
   - Send test emails
   - Verify formatting
   - Check spam score

**Deliverables:**
- [ ] MCP server running on port 3006
- [ ] 4 tools implemented
- [ ] Email templates created
- [ ] SMTP working

---

## Integration & Testing

### MCP Server Registry
Create central registry for all servers:
```json
{
  "servers": [
    {"name": "arxiv", "port": 3001, "status": "active"},
    {"name": "database", "port": 3002, "status": "active"},
    {"name": "summarization", "port": 3003, "status": "active"},
    {"name": "classification", "port": 3004, "status": "active"},
    {"name": "reports", "port": 3005, "status": "active"},
    {"name": "email", "port": 3006, "status": "active"}
  ]
}
```

### Kiro CLI Configuration
Add to `~/.kiro/config.json`:
```json
{
  "mcp_servers": [
    {"name": "arxiv-mcp", "url": "http://localhost:3001"},
    {"name": "database-mcp", "url": "http://localhost:3002"},
    {"name": "summarization-mcp", "url": "http://localhost:3003"},
    {"name": "classification-mcp", "url": "http://localhost:3004"},
    {"name": "reports-mcp", "url": "http://localhost:3005"},
    {"name": "email-mcp", "url": "http://localhost:3006"}
  ]
}
```

### End-to-End Workflow Test
1. Scrape papers (ArXiv MCP)
2. Store in database (Database MCP)
3. Generate summaries (Summarization MCP)
4. Auto-categorize (Classification MCP)
5. Create report (Reports MCP)
6. Email digest (Email MCP)

---

## Success Criteria

- [ ] All 6 MCP servers running
- [ ] All tools implemented and tested
- [ ] Integration with Kiro CLI working
- [ ] End-to-end workflow functional
- [ ] Documentation complete
- [ ] Performance acceptable (<2s per tool call)

---

## Timeline

**Week 1:**
- Day 1-2: ArXiv + Database MCP Servers
- Day 3-4: Summarization + Classification MCP Servers
- Day 5: Reports + Email MCP Servers
- Day 6-7: Integration testing and documentation

---

## Dependencies

**Python Packages:**
```txt
mcp-sdk>=1.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
boto3>=1.28.0  # for AWS Bedrock
openai>=1.0.0  # for OpenAI
aiosmtplib>=2.0.0  # for email
jinja2>=3.1.0  # for templates
```

**External Services:**
- AWS Bedrock (optional, for LLM)
- OpenAI API (optional, for LLM)
- SMTP server (Gmail/SES)

---

## Next Steps

1. Review this plan
2. Choose LLM provider (Bedrock vs OpenAI vs Local)
3. Start with ArXiv MCP Server (Priority 1)
4. Implement servers in order
5. Test integration with Kiro CLI
