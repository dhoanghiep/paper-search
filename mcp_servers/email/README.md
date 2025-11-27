# Email MCP Server

Sends email notifications for new papers and reports.

## Tools

- `send_email` - Send email notification with SMTP configuration

## Usage

```json
{
  "mcpServers": {
    "email": {
      "command": "python3",
      "args": ["mcp_servers/email/server.py"]
    }
  }
}
```

## Example

```python
send_email(
  to="user@example.com",
  subject="New Papers Published",
  body="5 new papers in machine learning...",
  smtp_config={
    "host": "smtp.gmail.com",
    "port": 587,
    "from_email": "alerts@example.com",
    "username": "user",
    "password": "pass",
    "use_tls": True
  }
)
```
