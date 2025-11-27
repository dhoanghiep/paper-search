# Reports MCP Server

Generates brief or in-depth reports for papers and period summaries.

## Tools

- `generate_paper_report` - Generate brief or in-depth report for a single paper
- `generate_period_report` - Generate daily, weekly, or monthly aggregate report

## Usage

```json
{
  "mcpServers": {
    "reports": {
      "command": "python3",
      "args": ["mcp_servers/reports/server.py"]
    }
  }
}
```

## Examples

```python
# Single paper report
generate_paper_report(
  paper={"title": "...", "authors": [...], "abstract": "..."},
  depth="in-depth"
)

# Period report
generate_period_report(
  papers=[...],
  period="weekly"
)
```
