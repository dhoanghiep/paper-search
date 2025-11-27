# Database MCP Server

Database management MCP server for querying and managing papers.

## Tools

### query_papers
Query papers with filters:
```json
{
  "method": "query_papers",
  "params": {
    "filters": {"category": "Machine Learning", "keyword": "transformer"},
    "limit": 10,
    "offset": 0
  }
}
```

### get_paper
Get single paper by ID:
```json
{"method": "get_paper", "params": {"paper_id": 1}}
```

### add_paper
Add new paper:
```json
{
  "method": "add_paper",
  "params": {
    "paper_data": {
      "arxiv_id": "2301.12345",
      "title": "Paper Title",
      "authors": ["Author 1", "Author 2"],
      "abstract": "Abstract text",
      "published": "2023-01-15T00:00:00Z",
      "pdf_url": "https://arxiv.org/pdf/2301.12345"
    }
  }
}
```

### get_categories
List all categories:
```json
{"method": "get_categories"}
```

### add_category
Create new category:
```json
{"method": "add_category", "params": {"name": "Machine Learning", "description": "ML papers"}}
```

### get_statistics
Get database stats:
```json
{"method": "get_statistics"}
```

## Usage

Run the server:
```bash
python mcp_servers/database/server.py
```
