# MCP Servers for Paper Search

Model Context Protocol servers to extend functionality.

## Available Servers

### 1. ArXiv MCP Server ✅
**Location:** `mcp_servers/arxiv/`  
**Status:** Completed  
**Port:** 3001

**Tools:**
- `search_papers` - Search arXiv by query
- `get_recent_papers` - Get latest papers by category
- `get_paper_details` - Get metadata for specific paper

### 2. Database MCP Server ✅
**Location:** `mcp_servers/database/`  
**Status:** Completed  
**Port:** 3002

**Tools:**
- `query_papers` - Query papers with filters
- `get_paper` - Get single paper by ID
- `add_paper` - Add new paper to database
- `get_categories` - List all categories
- `add_category` - Create new category
- `get_statistics` - Get database stats

### 3. Summarization MCP Server 🚧
**Location:** `mcp_servers/summarization/`  
**Status:** Boilerplate created  
**Port:** 3003

**Tools:**
- `summarize_abstract` - Brief 2-3 sentence summary
- `summarize_detailed` - In-depth analysis
- `extract_key_points` - 5-7 bullet points
- `generate_tldr` - One-sentence summary
- `batch_summarize` - Multiple papers

### 4. Classification MCP Server 🚧
**Location:** `mcp_servers/classification/`  
**Status:** Boilerplate created  
**Port:** 3004

**Tools:**
- `classify_paper` - Auto-assign categories
- `suggest_category` - Suggest new category
- `find_similar_papers` - Find related papers
- `get_category_distribution` - Category stats
- `reclassify_all` - Batch reclassification

### 5. Report Generation MCP Server 🚧
**Location:** `mcp_servers/reports/`  
**Status:** Boilerplate created  
**Port:** 3005

**Tools:**
- `generate_daily_report` - Last 24h papers
- `generate_weekly_report` - Weekly digest
- `generate_monthly_report` - Monthly summary
- `generate_paper_report` - Single paper report
- `generate_category_report` - Category-specific

### 6. Email Notification MCP Server 🚧
**Location:** `mcp_servers/email/`  
**Status:** Boilerplate created  
**Port:** 3006

**Tools:**
- `send_new_paper_alert` - New paper notification
- `send_report` - Email reports
- `send_digest` - Daily/weekly digest
- `configure_alerts` - User preferences

## Testing

Test completed servers:
```bash
echo '{"method": "search_papers", "params": {"query": "machine learning", "max_results": 5}}' | python mcp_servers/arxiv/server.py
echo '{"method": "get_statistics", "params": {}}' | python mcp_servers/database/server.py
```

## Next Steps

1. Implement Classification MCP (keyword matching)
2. Implement Summarization MCP (choose LLM provider)
3. Implement Reports MCP (markdown templates)
4. Implement Email MCP (optional)
