# Using ArXiv MCP Server with Kiro CLI

## Setup

1. **Configuration file created at:** `~/.config/kiro-cli/mcp.json`

```json
{
  "mcpServers": {
    "arxiv": {
      "command": "/workshop/paper-search/venv/bin/python",
      "args": ["/workshop/paper-search/mcp_servers/arxiv/server.py"]
    }
  }
}
```

2. **Restart Kiro CLI** to load the MCP server

## Usage Examples

Once configured, you can use natural language to interact with the ArXiv MCP tools:

### Search for papers
```
"Search arXiv for papers about quantum computing"
"Find recent papers on neural networks"
"Look up papers about transformers in machine learning"
```

### Get recent papers by category
```
"Get the 5 most recent papers from cs.AI category"
"Show me recent papers in math.CO"
"What are the latest papers in physics?"
```

### Get specific paper details
```
"Get details for arXiv paper 2301.12345"
"Show me information about paper 2311.09876"
```

## Available Tools

The MCP server provides these tools that Kiro can automatically invoke:

- **search_papers** - Search by keywords
- **get_recent_papers** - Get latest papers (optionally by category)
- **get_paper_details** - Get metadata for a specific paper ID

## Testing

To verify the MCP server works independently:
```bash
cd /workshop/paper-search/mcp_servers/arxiv
source ../../venv/bin/activate
python test_server.py
```
