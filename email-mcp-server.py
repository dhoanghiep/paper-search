#!/usr/bin/env python3
import json
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any

def read_message():
    line = sys.stdin.readline()
    return json.loads(line) if line else None

def write_message(msg: dict[str, Any]):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def send_email(to: str, subject: str, body: str, smtp_config: dict) -> dict:
    """Send email notification"""
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_config.get('from_email')
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_config.get('host', 'localhost'), smtp_config.get('port', 587))
        if smtp_config.get('use_tls', True):
            server.starttls()
        if smtp_config.get('username') and smtp_config.get('password'):
            server.login(smtp_config['username'], smtp_config['password'])
        
        server.send_message(msg)
        server.quit()
        return {"status": "sent", "to": to}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def handle_request(req: dict) -> dict:
    method = req.get("method")
    params = req.get("params", {})
    
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "email-server", "version": "1.0.0"}
        }
    
    if method == "tools/list":
        return {
            "tools": [{
                "name": "send_email",
                "description": "Send email notification about new papers",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "smtp_config": {
                            "type": "object",
                            "properties": {
                                "host": {"type": "string"},
                                "port": {"type": "integer"},
                                "from_email": {"type": "string"},
                                "username": {"type": "string"},
                                "password": {"type": "string"},
                                "use_tls": {"type": "boolean"}
                            }
                        }
                    },
                    "required": ["to", "subject", "body", "smtp_config"]
                }
            }]
        }
    
    if method == "tools/call":
        tool = params.get("name")
        args = params.get("arguments", {})
        
        if tool == "send_email":
            result = send_email(
                args.get("to", ""),
                args.get("subject", ""),
                args.get("body", ""),
                args.get("smtp_config", {})
            )
            return {
                "content": [{"type": "text", "text": json.dumps(result)}]
            }
    
    return {"error": "Unknown method"}

def main():
    while True:
        msg = read_message()
        if not msg:
            break
        
        response = {"jsonrpc": "2.0", "id": msg.get("id")}
        response["result"] = handle_request(msg)
        write_message(response)

if __name__ == "__main__":
    main()
