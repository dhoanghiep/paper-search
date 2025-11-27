# MCP Servers for Paper Search

Model Context Protocol servers to extend functionality.

## Available Servers

### 1. ArXiv MCP Server ✅
**Location:** `mcp_servers/arxiv/`  
**Status:** Completed

**Tools:**
- `search_papers` - Search arXiv by query
- `get_recent_papers` - Get latest papers by category
- `get_paper_details` - Get metadata for specific paper

**Usage:**
```bash
python mcp_servers/arxiv/server.py
```

### 2. Database MCP Server ✅
**Location:** `mcp_servers/database/`  
**Status:** Completed

**Tools:**
- `query_papers` - Query papers with filters (category, author, keyword)
- `get_paper` - Get single paper by ID
- `add_paper` - Add new paper to database
- `get_categories` - List all categories
- `add_category` - Create new category
- `get_statistics` - Get database stats

**Usage:**
```bash
python mcp_servers/database/server.py
```

## Testing

Test ArXiv server:
```bash
echo '{"method": "search_papers", "params": {"query": "machine learning", "max_results": 5}}' | python mcp_servers/arxiv/server.py
```

Test Database server:
```bash
echo '{"method": "get_statistics", "params": {}}' | python mcp_servers/database/server.py
```

## Integration with Kiro CLI

Add to Kiro CLI configuration to use these MCP servers for enhanced paper search capabilities.
