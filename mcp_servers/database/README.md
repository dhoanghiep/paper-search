# Database MCP Server

Provides database operations for paper management.

## Tools

- `query_papers` - Query papers with filters (category, author, keyword)
- `get_paper` - Get paper by ID
- `add_paper` - Add new paper
- `update_paper` - Update paper fields
- `get_categories` - List all categories
- `add_category` - Create category
- `assign_category` - Assign category to paper
- `save_report` - Save report to database
- `get_statistics` - Get database statistics

## Usage

```bash
python3 server.py
```

Communicates via JSON-RPC over stdin/stdout.
