# AI Usage in Paper Search

## Overview

The app uses **AWS Bedrock** with **Claude 3 Haiku** for AI-powered paper summarization.

## AI Stack

- **Library:** `boto3` (AWS SDK for Python)
- **Service:** AWS Bedrock (Managed AI service)
- **Model:** `anthropic.claude-3-haiku-20240307-v1:0`
- **Region:** us-west-2 (configurable via AWS_REGION env var)

## Where AI is Used

### Location: `mcp_servers/summarization/server.py`

This MCP server handles all AI operations:

```python
import boto3

# Initialize AWS Bedrock client
bedrock = boto3.client(
    'bedrock-runtime', 
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

def call_llm(prompt):
    """Call Claude 3 Haiku via AWS Bedrock"""
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        })
    )
    
    # Extract text from response
    result = json.loads(response['body'].read())
    return result['content'][0]['text']
```

## AI Functions

### 1. Summarize Abstract (Main Function)
```python
def summarize_abstract(paper_id):
    paper = get_paper(paper_id)
    prompt = f"""Summarize in 2-3 sentences:
Title: {paper.title}
Abstract: {paper.abstract}"""
    
    return {"summary": call_llm(prompt)}
```

### 2. Detailed Summary
```python
def summarize_detailed(paper_id):
    paper = get_paper(paper_id)
    prompt = f"""Provide detailed analysis with:
- Main contribution
- Methodology
- Key findings
- Implications

Title: {paper.title}
Abstract: {paper.abstract}"""
    
    return {"summary": call_llm(prompt)}
```

### 3. Extract Key Points
```python
def extract_key_points(paper_id):
    paper = get_paper(paper_id)
    prompt = f"""Extract 5-7 key points as bullet list:
Title: {paper.title}
Abstract: {paper.abstract}"""
    
    return {"points": call_llm(prompt)}
```

### 4. Generate TL;DR
```python
def generate_tldr(paper_id):
    paper = get_paper(paper_id)
    prompt = f"""One sentence summary:
Title: {paper.title}
Abstract: {paper.abstract}"""
    
    return {"tldr": call_llm(prompt)}
```

### 5. Batch Summarize
```python
def batch_summarize(paper_ids):
    summaries = {}
    for pid in paper_ids:
        summaries[str(pid)] = summarize_abstract(pid)["summary"]
    return {"summaries": summaries}
```

## How AI is Called in the Workflow

### Step 1: User triggers processing
```bash
./paper process --limit 5
```

### Step 2: Pipeline calls orchestrator
```python
# app/pipeline.py
from app.orchestrator import process_paper

def process_new_papers(limit=10):
    unprocessed = get_unprocessed_papers(limit)
    for paper in unprocessed:
        process_paper(paper.id)
```

### Step 3: Orchestrator calls MCP server
```python
# app/orchestrator.py
summarization_client = MCPClient("mcp_servers/summarization/server.py")

def process_paper(paper_id):
    # Call AI summarization via MCP
    summary = summarization_client.call("summarize_abstract", {
        "paper_id": paper_id
    })
    
    # Save to database
    paper.summary = summary.get("summary", "")
    db.commit()
```

### Step 4: MCP server calls AWS Bedrock
```python
# mcp_servers/summarization/server.py
def summarize_abstract(paper_id):
    paper = get_paper(paper_id)
    
    # Build prompt
    prompt = f"Summarize in 2-3 sentences:\nTitle: {paper.title}\nAbstract: {paper.abstract}"
    
    # Call Claude 3 Haiku via AWS Bedrock
    summary = call_llm(prompt)
    
    return {"summary": summary}
```

### Step 5: AI response flows back
```
AWS Bedrock (Claude 3 Haiku)
    ↓ (AI-generated summary)
MCP Server
    ↓ (JSON-RPC response)
Orchestrator
    ↓ (saves to database)
User sees summary
```

## Example AI Request/Response

### Request to AWS Bedrock:
```json
{
  "anthropic_version": "bedrock-2023-05-31",
  "max_tokens": 1024,
  "messages": [{
    "role": "user",
    "content": "Summarize in 2-3 sentences:\nTitle: Matrix: Peer-to-Peer Multi-Agent Synthetic Data Generation Framework\nAbstract: Synthetic data has become increasingly important for training large language models..."
  }]
}
```

### Response from Claude 3 Haiku:
```json
{
  "content": [{
    "type": "text",
    "text": "The paper presents Matrix, a decentralized framework for peer-to-peer multi-agent synthetic data generation, which eliminates the need for a centralized orchestrator and scales to tens of thousands of concurrent workflows. Matrix represents control and data flow as serialized messages passed through distributed queues, allowing each task to progress independently through lightweight agents while delegating compute-intensive operations to distributed services. The authors evaluate Matrix across diverse synthesis scenarios and demonstrate significant improvements in data generation throughput compared to existing frameworks, without compromising output quality."
  }]
}
```

## Configuration

### Environment Variables
```bash
# .env file
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

### AWS Credentials
The app uses standard AWS credential chain:
1. Environment variables
2. ~/.aws/credentials
3. IAM role (if running on AWS)

## Cost Considerations

**Claude 3 Haiku Pricing (as of 2024):**
- Input: $0.25 per 1M tokens
- Output: $1.25 per 1M tokens

**Typical paper processing:**
- Input: ~500 tokens (title + abstract)
- Output: ~150 tokens (summary)
- Cost per paper: ~$0.0003 (less than 1 cent)

**Daily automation (30 papers):**
- Cost: ~$0.01 per day
- Monthly: ~$0.30

## Why Claude 3 Haiku?

1. **Fast:** 3-5 second response time
2. **Cheap:** Most cost-effective Claude model
3. **Accurate:** Good quality for summarization tasks
4. **Managed:** No infrastructure to maintain via Bedrock
5. **Scalable:** Handles concurrent requests

## Alternative AI Options

The MCP architecture makes it easy to swap AI providers:

### OpenAI GPT-4
```python
import openai

def call_llm(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

### Local LLM (Ollama)
```python
import requests

def call_llm(prompt):
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama2",
        "prompt": prompt
    })
    return response.json()["response"]
```

### Anthropic Direct API
```python
import anthropic

def call_llm(prompt):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
```

## Testing AI Locally

```bash
# Test summarization MCP server directly
cd /workshop/paper-search
source venv/bin/activate

# Create test request
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"summarize_abstract","arguments":{"paper_id":1}}}' | \
python3 mcp_servers/summarization/server.py
```

## Monitoring AI Usage

Check AWS CloudWatch for:
- Bedrock invocation count
- Token usage
- Latency metrics
- Error rates

## Summary

**AI is used in ONE place:** `mcp_servers/summarization/server.py`

**Library:** `boto3` (AWS SDK)

**Model:** Claude 3 Haiku via AWS Bedrock

**Purpose:** Generate concise summaries of research papers

**Cost:** ~$0.01 per day for 30 papers
