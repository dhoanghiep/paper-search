# Summarization MCP Server

Uses AWS Bedrock (Claude 3 Haiku) to generate paper summaries.

## Tools

- `summarize_abstract` - Brief 2-3 sentence summary
- `summarize_detailed` - Detailed analysis with methodology and findings
- `extract_key_points` - Extract 5-7 key points
- `generate_tldr` - One sentence summary
- `batch_summarize` - Summarize multiple papers

## Requirements

- AWS credentials configured
- boto3 installed
- Access to Bedrock Claude models

## Usage

```bash
python3 server.py
```
