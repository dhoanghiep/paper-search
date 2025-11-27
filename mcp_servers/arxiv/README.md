# ArXiv MCP Server

MCP server for searching and retrieving papers from arXiv.

## Tools

### search_papers
Search arXiv papers by query string.

**Parameters:**
- `query` (string, required): Search query
- `max_results` (integer, default: 10): Max results to return

**Example:**
```json
{"method": "search_papers", "params": {"query": "machine learning", "max_results": 5}}
```

### get_recent_papers
Get recent papers from arXiv, optionally filtered by category.

**Parameters:**
- `category` (string, default: "all"): arXiv category (e.g., cs.AI, math.CO)
- `max_results` (integer, default: 10): Max results to return

**Example:**
```json
{"method": "get_recent_papers", "params": {"category": "cs.AI", "max_results": 5}}
```

### get_paper_details
Get detailed metadata for a specific arXiv paper.

**Parameters:**
- `arxiv_id` (string, required): arXiv paper ID (e.g., 2301.12345)

**Example:**
```json
{"method": "get_paper_details", "params": {"arxiv_id": "2301.12345"}}
```

## Testing

Run the test script:
```bash
python test_server.py
```

## Usage with Kiro CLI

Add to your MCP configuration:
```json
{
  "mcpServers": {
    "arxiv": {
      "command": "python",
      "args": ["/workshop/paper-search/mcp_servers/arxiv/server.py"]
    }
  }
}
```

## Rate Limiting

Implements 0.34s delay between requests (max 3 req/sec) per arXiv guidelines.
