# MCP (Model Context Protocol) - Core Concept

## What is MCP?

**MCP (Model Context Protocol)** is a standardized way for applications to communicate with external tools/services using **JSON-RPC 2.0** over stdin/stdout.

Think of it as: **"Microservices, but for AI tools"**

## Core Idea

Instead of tightly coupling AI functionality into your main app, you:
1. Create **independent server processes** that expose tools
2. Communicate via **standardized JSON-RPC messages**
3. Each server is **isolated, testable, and swappable**

## Architecture Comparison

### WITHOUT MCP (Monolithic)
```
┌─────────────────────────────────────────────────┐
│           Main Application                      │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  import boto3                            │  │
│  │  import openai                           │  │
│  │  import anthropic                        │  │
│  │                                          │  │
│  │  def process_paper():                    │  │
│  │      # Classification logic here         │  │
│  │      category = classify(title, abstract)│  │
│  │                                          │  │
│  │      # Summarization logic here          │  │
│  │      bedrock = boto3.client(...)         │  │
│  │      summary = bedrock.invoke_model(...) │  │
│  │                                          │  │
│  │      # Report logic here                 │  │
│  │      report = generate_report(...)       │  │
│  │                                          │  │
│  │      # Email logic here                  │  │
│  │      smtp.send(...)                      │  │
│  │                                          │  │
│  │      return result                       │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  Everything is tightly coupled!                 │
└─────────────────────────────────────────────────┘
```

### WITH MCP (Microservices)
```
┌──────────────────────────────────────────────────────────────┐
│                    Main Application                          │
│                                                              │
│  def process_paper():                                        │
│      # Just coordinate, don't implement                      │
│      category = mcp_call("classification", "classify", {...})│
│      summary = mcp_call("summarization", "summarize", {...}) │
│      report = mcp_call("reports", "generate", {...})         │
│      mcp_call("email", "send", {...})                        │
└────────────┬─────────────────────────────────────────────────┘
             │ JSON-RPC over stdin/stdout
             │
    ┌────────┴────────┬────────────┬──────────┬─────────┐
    │                 │            │          │         │
┌───▼────┐  ┌────────▼───┐  ┌─────▼────┐  ┌──▼───┐  ┌─▼────┐
│Classify│  │Summarize   │  │Reports   │  │Email │  │ArXiv │
│MCP     │  │MCP         │  │MCP       │  │MCP   │  │MCP   │
│Server  │  │Server      │  │Server    │  │Server│  │Server│
└────────┘  └────────────┘  └──────────┘  └──────┘  └──────┘
   │             │               │            │         │
   │             │               │            │         │
Keywords    AWS Bedrock     Markdown      SMTP    arXiv API
```

## Code Comparison

### WITHOUT MCP - Monolithic Approach

```python
# app/processor.py - Everything in one place
import boto3
import smtplib
from email.mime.text import MIMEText

# All dependencies loaded in main app
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
smtp_server = smtplib.SMTP('smtp.gmail.com', 587)

def classify_paper(title, abstract):
    """Classification logic embedded in main app"""
    keywords = {
        'Machine Learning': ['neural', 'learning', 'model', 'training'],
        'Physics': ['quantum', 'particle', 'energy'],
        'Biology': ['cell', 'protein', 'gene']
    }
    
    text = (title + ' ' + abstract).lower()
    for category, words in keywords.items():
        if any(word in text for word in words):
            return category
    return 'Other'

def summarize_paper(title, abstract):
    """Summarization logic embedded in main app"""
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{
                "role": "user",
                "content": f"Summarize: {title}\n{abstract}"
            }]
        })
    )
    return json.loads(response['body'].read())['content'][0]['text']

def generate_report(papers):
    """Report logic embedded in main app"""
    report = "# Daily Report\n\n"
    for paper in papers:
        report += f"## {paper.title}\n{paper.summary}\n\n"
    return report

def send_email(to, subject, body):
    """Email logic embedded in main app"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['To'] = to
    smtp_server.send_message(msg)

def process_paper(paper_id):
    """Main processing - everything coupled together"""
    paper = db.query(Paper).get(paper_id)
    
    # All logic in one place
    category = classify_paper(paper.title, paper.abstract)
    summary = summarize_paper(paper.title, paper.abstract)
    
    paper.category = category
    paper.summary = summary
    db.commit()
    
    # Can't test classification without loading AWS Bedrock
    # Can't test summarization without SMTP server
    # Everything is interdependent!
```

**Problems:**
- ❌ All dependencies loaded even if not used
- ❌ Can't test classification without AWS credentials
- ❌ Can't swap AI providers easily
- ❌ Hard to debug individual components
- ❌ No isolation between features
- ❌ Main app becomes bloated

### WITH MCP - Microservices Approach

```python
# mcp_servers/classification/server.py - Independent process
#!/usr/bin/env python3
import json
import sys

def classify_paper(title, abstract):
    """Isolated classification logic"""
    keywords = {
        'Machine Learning': ['neural', 'learning', 'model'],
        'Physics': ['quantum', 'particle', 'energy'],
        'Biology': ['cell', 'protein', 'gene']
    }
    
    text = (title + ' ' + abstract).lower()
    for category, words in keywords.items():
        if any(word in text for word in words):
            return {"category": category, "confidence": 0.9}
    return {"category": "Other", "confidence": 0.5}

def handle_message(msg):
    """JSON-RPC 2.0 handler"""
    if msg["method"] == "tools/call":
        args = msg["params"]["arguments"]
        result = classify_paper(args["title"], args["abstract"])
        return {
            "jsonrpc": "2.0",
            "id": msg["id"],
            "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
        }

# Run as independent process
if __name__ == "__main__":
    for line in sys.stdin:
        msg = json.loads(line)
        response = handle_message(msg)
        print(json.dumps(response), flush=True)
```

```python
# mcp_servers/summarization/server.py - Independent process
#!/usr/bin/env python3
import json
import sys
import boto3

# Only loads AWS when THIS server runs
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def summarize_abstract(paper_id):
    """Isolated summarization logic"""
    paper = get_paper(paper_id)
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{
                "role": "user",
                "content": f"Summarize: {paper.title}\n{paper.abstract}"
            }]
        })
    )
    return {"summary": json.loads(response['body'].read())['content'][0]['text']}

def handle_message(msg):
    if msg["method"] == "tools/call":
        args = msg["params"]["arguments"]
        result = summarize_abstract(args["paper_id"])
        return {
            "jsonrpc": "2.0",
            "id": msg["id"],
            "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
        }

if __name__ == "__main__":
    for line in sys.stdin:
        msg = json.loads(line)
        response = handle_message(msg)
        print(json.dumps(response), flush=True)
```

```python
# app/orchestrator.py - Thin coordination layer
import json
import subprocess

class MCPClient:
    """Generic client for any MCP server"""
    def __init__(self, server_path):
        self.server_path = server_path
    
    def call(self, method, params):
        """Call MCP server via stdin/stdout"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": method, "arguments": params}
        }
        
        # Spawn independent process
        result = subprocess.run(
            ["python3", self.server_path],
            input=json.dumps(request),
            capture_output=True,
            text=True
        )
        
        response = json.loads(result.stdout)
        content = response["result"]["content"][0]["text"]
        return json.loads(content)

# Initialize clients
classification_client = MCPClient("mcp_servers/classification/server.py")
summarization_client = MCPClient("mcp_servers/summarization/server.py")

def process_paper(paper_id):
    """Thin orchestration - no business logic"""
    paper = db.query(Paper).get(paper_id)
    
    # Delegate to MCP servers
    classification = classification_client.call("classify_paper", {
        "title": paper.title,
        "abstract": paper.abstract
    })
    
    summary = summarization_client.call("summarize_abstract", {
        "paper_id": paper_id
    })
    
    # Just save results
    paper.category = classification["category"]
    paper.summary = summary["summary"]
    db.commit()
```

**Benefits:**
- ✅ Each server is independent
- ✅ Test classification without AWS
- ✅ Swap AI providers by changing one file
- ✅ Debug servers in isolation
- ✅ Main app stays thin
- ✅ Dependencies only loaded when needed

## JSON-RPC Communication

### Request (Main App → MCP Server)
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "classify_paper",
    "arguments": {
      "title": "Neural Networks for Image Recognition",
      "abstract": "We present a deep learning approach..."
    }
  }
}
```

### Response (MCP Server → Main App)
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"category\": \"Machine Learning\", \"confidence\": 0.95}"
    }]
  }
}
```

## Real-World Analogy

### WITHOUT MCP (Monolithic Restaurant)
```
One chef does everything:
- Takes orders
- Cooks appetizers
- Cooks main course
- Makes desserts
- Serves food
- Handles payment

Problem: Chef must know everything, can't specialize, bottleneck
```

### WITH MCP (Restaurant with Stations)
```
Specialized stations:
- Order taker (orchestrator)
- Appetizer chef (classification MCP)
- Main course chef (summarization MCP)
- Dessert chef (reports MCP)
- Server (email MCP)

Benefit: Each station specializes, can work in parallel, easy to replace
```

## Key MCP Concepts

### 1. **Isolation**
Each MCP server runs as a separate process with its own dependencies.

### 2. **Standardization**
All servers use the same JSON-RPC 2.0 protocol.

### 3. **Composability**
Mix and match servers like LEGO blocks.

### 4. **Testability**
Test each server independently without the main app.

### 5. **Swappability**
Replace one server without touching others.

## Example: Swapping AI Providers

### Current: AWS Bedrock
```python
# mcp_servers/summarization/server.py
import boto3
bedrock = boto3.client('bedrock-runtime')
summary = bedrock.invoke_model(...)
```

### Swap to OpenAI (just change one file!)
```python
# mcp_servers/summarization/server.py
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
summary = openai.ChatCompletion.create(...)
```

### Swap to Local Ollama
```python
# mcp_servers/summarization/server.py
import requests
response = requests.post("http://localhost:11434/api/generate", ...)
summary = response.json()["response"]
```

**Main app doesn't change at all!** The orchestrator still calls:
```python
summary = summarization_client.call("summarize_abstract", {"paper_id": 1})
```

## Testing Comparison

### WITHOUT MCP
```python
# Must mock everything
@mock.patch('boto3.client')
@mock.patch('smtplib.SMTP')
@mock.patch('requests.get')
def test_process_paper(mock_requests, mock_smtp, mock_boto3):
    # Complex setup for all dependencies
    mock_boto3.return_value.invoke_model.return_value = ...
    mock_smtp.return_value.send_message.return_value = ...
    
    result = process_paper(1)
    assert result.category == "Machine Learning"
```

### WITH MCP
```python
# Test classification server independently
def test_classification():
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "classify_paper",
            "arguments": {
                "title": "Neural Networks",
                "abstract": "Deep learning model..."
            }
        }
    }
    
    # Run server directly
    result = subprocess.run(
        ["python3", "mcp_servers/classification/server.py"],
        input=json.dumps(request),
        capture_output=True,
        text=True
    )
    
    response = json.loads(result.stdout)
    assert "Machine Learning" in response["result"]["content"][0]["text"]
```

## Summary

| Aspect | Without MCP | With MCP |
|--------|-------------|----------|
| **Architecture** | Monolithic | Microservices |
| **Dependencies** | All loaded always | Loaded per server |
| **Testing** | Complex mocking | Independent tests |
| **Swapping** | Rewrite main app | Change one file |
| **Debugging** | Hard to isolate | Debug one server |
| **Scaling** | Vertical only | Horizontal possible |
| **Communication** | Direct function calls | JSON-RPC stdin/stdout |

## Core Idea in One Sentence

**MCP turns your AI tools into independent microservices that communicate via a standard protocol, making your app modular, testable, and maintainable.**
