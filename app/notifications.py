import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str, html: bool = False):
    """Send email via SMTP"""
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    from_email = os.getenv("FROM_EMAIL", smtp_user)
    
    if not smtp_user or not smtp_pass:
        logger.warning("SMTP credentials not configured. Skipping email.")
        return False
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        
        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def send_daily_digest(to_email: str, report_content: str):
    """Send daily digest email"""
    subject = f"Daily Paper Digest - {os.getenv('APP_NAME', 'Paper Search')}"
    
    html_body = f"""
    <html>
    <body>
        <h1>Daily Paper Digest</h1>
        <pre>{report_content}</pre>
        <hr>
        <p><small>Automated email from Paper Search System</small></p>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_body, html=True)

def send_new_paper_alert(to_email: str, paper_title: str, paper_id: str):
    """Send alert for new paper"""
    subject = "New Paper Alert"
    body = f"""
New paper added to the system:

Title: {paper_title}
ID: {paper_id}

View at: http://localhost:8000/papers/{paper_id}
"""
    return send_email(to_email, subject, body)
