# Classification MCP Server

Classifies papers into existing categories or suggests new ones using keyword matching.

## Tools

- `classify_paper` - Classify paper based on title, abstract, and existing categories

## Usage

```json
{
  "mcpServers": {
    "classification": {
      "command": "python3",
      "args": ["mcp_servers/classification/server.py"]
    }
  }
}
```

## Example

```python
classify_paper(
  title="Deep Learning for Computer Vision",
  abstract="This paper presents...",
  existing_categories=["machine learning", "nlp"]
)
```
