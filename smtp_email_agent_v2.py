#!/usr/bin/env python3
"""
SMTP EMAIL AGENT V2 - PRODUCTION READY
Autonomous email delivery with retry logic, HTML support, attachments, and hardened security
"""

import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import json
import logging
from pathlib import Path

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/smtp_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SMTPEmailAgent')

class SMTPEmailAgentV2:
    def __init__(self):
        self.name = "SMTP Email Agent V2"
        self.smtp_config = self.load_smtp_config()
        self.delivery_stats = {
            "total_attempts": 0,
            "successful": 0,
            "failed": 0,
            "retries": 0
        }
        
    def load_smtp_config(self):
        """Load SMTP configuration from environment (credentials sanitized in logs)"""
        config = {
            "gmail": {
                "server": "smtp.gmail.com",
                "port": 587,
                "use_tls": True,
                "username": os.getenv("GMAIL_USERNAME", ""),
                "password": os.getenv("GMAIL_APP_PASSWORD", ""),
            },
            "outlook": {
                "server": "smtp-mail.outlook.com",
                "port": 587,
                "use_tls": True,
                "username": os.getenv("OUTLOOK_USERNAME", ""),
                "password": os.getenv("OUTLOOK_PASSWORD", ""),
            },
            "custom": {
                "server": os.getenv("SMTP_SERVER", ""),
                "port": int(os.getenv("SMTP_PORT", "587")),
                "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
                "username": os.getenv("SMTP_USERNAME", ""),
                "password": os.getenv("SMTP_PASSWORD", ""),
            }
        }
        
        # Log configuration status (WITHOUT passwords)
        for provider, cfg in config.items():
            has_creds = bool(cfg["username"] and cfg["password"])
            logger.info(f"{provider.upper()}: {'configured' if has_creds else 'not configured'}")
        
        return config
    
    def _sanitize_for_log(self, text):
        """Remove sensitive data from log messages"""
        # Never log passwords or tokens
        return text.replace(os.getenv("GMAIL_APP_PASSWORD", ""), "***")
    
    def _retry_with_backoff(self, func, max_retries=3, initial_delay=2):
        """Exponential backoff retry logic"""
        delay = initial_delay
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_error = e
                self.delivery_stats["retries"] += 1
                
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.error(f"All {max_retries} attempts failed: {e}")
        
        raise last_error
    
    def send_email(self, provider, to_emails, subject, body, 
                   from_email=None, html_body=None, attachments=None):
        """
        Send email via SMTP with retry logic
        
        Args:
            provider: 'gmail', 'outlook', or 'custom'
            to_emails: List of recipient emails
            subject: Email subject
            body: Plain text body
            from_email: Optional sender email (defaults to username)
            html_body: Optional HTML version of body
            attachments: List of file paths to attach
        """
        self.delivery_stats["total_attempts"] += 1
        logger.info(f"Sending email via {provider.upper()}: '{subject}' to {len(to_emails)} recipients")
        
        config = self.smtp_config.get(provider)
        if not config:
            logger.error(f"Unknown provider: {provider}")
            self.delivery_stats["failed"] += 1
            return False
        
        # Validate credentials
        if not config["username"] or not config["password"]:
            logger.error(f"{provider.upper()}: Missing credentials")
            self.delivery_stats["failed"] += 1
            return False
        
        def _send():
            # Create message
            msg = MIMEMultipart('alternative') if html_body else MIMEMultipart()
            msg['From'] = from_email or config["username"]
            msg['To'] = ", ".join(to_emails)
            msg['Subject'] = subject
            
            # Attach plain text body
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Attach files if provided
            if attachments:
                for filepath in attachments:
                    if not Path(filepath).exists():
                        logger.warning(f"Attachment not found: {filepath}")
                        continue
                    
                    with open(filepath, 'rb') as f:
                        attachment = MIMEApplication(f.read())
                        attachment.add_header(
                            'Content-Disposition', 
                            'attachment', 
                            filename=Path(filepath).name
                        )
                        msg.attach(attachment)
                        logger.info(f"Attached: {Path(filepath).name}")
            
            # Connect to SMTP server
            if config["use_tls"]:
                server = smtplib.SMTP(config["server"], config["port"], timeout=30)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(config["server"], config["port"], timeout=30)
            
            # Login
            server.login(config["username"], config["password"])
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            return True
        
        try:
            # Use retry logic
            self._retry_with_backoff(_send, max_retries=3)
            logger.info(f"✓ Email sent successfully via {provider.upper()}")
            self.delivery_stats["successful"] += 1
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            logger.info(f"For Gmail: Use App Password from https://myaccount.google.com/apppasswords")
            self.delivery_stats["failed"] += 1
            return False
            
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"Recipients refused: {e}")
            self.delivery_stats["failed"] += 1
            return False
            
        except smtplib.SMTPSenderRefused as e:
            logger.error(f"Sender refused: {e}")
            self.delivery_stats["failed"] += 1
            return False
            
        except smtplib.SMTPDataError as e:
            logger.error(f"Data error: {e}")
            self.delivery_stats["failed"] += 1
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.delivery_stats["failed"] += 1
            return False
    
    def send_capital_flow_alert(self, analysis_data, to_emails):
        """Send capital flow analysis alert"""
        subject = f"Capital Flow Alert: {analysis_data.get('trend', 'N/A')} in {analysis_data.get('sector', 'N/A')}"
        
        # Plain text body
        body = f"""
AUTONOMOUS CAPITAL FLOW REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

KEY FINDING: {analysis_data.get('summary', 'N/A')}

TOP MOVERS:
"""
        for mover in analysis_data.get('movers', []):
            body += f"- {mover}\n"
        
        body += f"""
RECOMMENDED ACTION: {analysis_data.get('action', 'Monitor')}

(This is an automated report from the Echonate tracking system.)
"""
        
        # HTML body
        html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; }}
        .content {{ padding: 20px; }}
        .finding {{ background-color: #ecf0f1; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }}
        .movers {{ list-style-type: none; padding: 0; }}
        .movers li {{ padding: 5px 0; }}
        .action {{ background-color: #e74c3c; color: white; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>AUTONOMOUS CAPITAL FLOW REPORT</h2>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    <div class="content">
        <div class="finding">
            <h3>KEY FINDING</h3>
            <p>{analysis_data.get('summary', 'N/A')}</p>
        </div>
        <h3>TOP MOVERS</h3>
        <ul class="movers">
"""
        for mover in analysis_data.get('movers', []):
            html_body += f"<li>• {mover}</li>\n"
        
        html_body += f"""
        </ul>
        <div class="action">
            <strong>RECOMMENDED ACTION:</strong> {analysis_data.get('action', 'Monitor')}
        </div>
        <p><em>(This is an automated report from the Echonate tracking system.)</em></p>
    </div>
</body>
</html>
"""
        
        # Try all providers
        for provider in ["gmail", "outlook", "custom"]:
            if self.send_email(provider, to_emails, subject, body, html_body=html_body):
                return True
        
        return False
    
    def send_agent_reports(self, report_file, to_emails, attachments=None):
        """Send all agent reports with optional attachments"""
        logger.info(f"Sending agent reports from {report_file}")
        
        # Load reports
        with open(report_file, 'r') as f:
            reports = f.read()
        
        subject = "ECHONATE: All 12 Agent Reports - Autonomous Delivery"
        
        # Try providers in order
        for provider in ["gmail", "outlook", "custom"]:
            if self.send_email(provider, to_emails, subject, reports, attachments=attachments):
                return True
        
        logger.error("All SMTP providers failed")
        return False
    
    def get_stats(self):
        """Get delivery statistics"""
        return self.delivery_stats

def main():
    """Main execution"""
    agent = SMTPEmailAgentV2()
    
    logger.info("="*80)
    logger.info("SMTP EMAIL AGENT V2 - PRODUCTION READY")
    logger.info("="*80)
    
    # Send agent reports
    report_file = "/tmp/agent_reports_20260109_123551.txt"
    to_emails = ["npoinsette@gmail.com", "king.thedros@gmail.com"]
    
    if Path(report_file).exists():
        success = agent.send_agent_reports(report_file, to_emails)
    else:
        logger.warning(f"Report file not found: {report_file}")
        success = False
    
    # Print statistics
    stats = agent.get_stats()
    logger.info("="*80)
    logger.info("DELIVERY STATISTICS")
    logger.info("="*80)
    logger.info(f"Total Attempts: {stats['total_attempts']}")
    logger.info(f"Successful: {stats['successful']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Retries: {stats['retries']}")
    logger.info(f"Success Rate: {stats['successful']/stats['total_attempts']*100 if stats['total_attempts'] > 0 else 0:.1f}%")
    logger.info("="*80)
    
    # Save stats
    stats_file = f"/tmp/smtp_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(stats_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "success": success
        }, f, indent=2)
    
    logger.info(f"Statistics saved: {stats_file}")

if __name__ == "__main__":
    main()
