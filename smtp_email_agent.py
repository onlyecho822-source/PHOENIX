#!/usr/bin/env python3
"""
SMTP EMAIL AGENT
Direct email sending using SMTP (Gmail, Outlook, or custom SMTP server)
No UI confirmation required - fully autonomous
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

class SMTPEmailAgent:
    def __init__(self):
        self.name = "SMTP Email Agent"
        self.smtp_config = self.load_smtp_config()
        
    def log(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {self.name}: {message}")
    
    def load_smtp_config(self):
        """Load SMTP configuration from environment or defaults"""
        config = {
            # Gmail SMTP (most common)
            "gmail": {
                "server": "smtp.gmail.com",
                "port": 587,
                "use_tls": True,
                "username": os.getenv("GMAIL_USERNAME", ""),
                "password": os.getenv("GMAIL_APP_PASSWORD", ""),  # App Password, not regular password
            },
            # Outlook/Hotmail SMTP
            "outlook": {
                "server": "smtp-mail.outlook.com",
                "port": 587,
                "use_tls": True,
                "username": os.getenv("OUTLOOK_USERNAME", ""),
                "password": os.getenv("OUTLOOK_PASSWORD", ""),
            },
            # Custom SMTP
            "custom": {
                "server": os.getenv("SMTP_SERVER", ""),
                "port": int(os.getenv("SMTP_PORT", "587")),
                "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
                "username": os.getenv("SMTP_USERNAME", ""),
                "password": os.getenv("SMTP_PASSWORD", ""),
            }
        }
        return config
    
    def send_email(self, provider, to_emails, subject, body, from_email=None):
        """Send email via SMTP"""
        self.log(f"Attempting to send via {provider.upper()} SMTP...")
        
        config = self.smtp_config.get(provider)
        if not config:
            self.log(f"✗ Unknown provider: {provider}")
            return False
        
        # Validate credentials
        if not config["username"] or not config["password"]:
            self.log(f"✗ {provider.upper()}: Missing credentials (username or password)")
            self.log(f"   Set environment variables:")
            if provider == "gmail":
                self.log(f"   - GMAIL_USERNAME=your-email@gmail.com")
                self.log(f"   - GMAIL_APP_PASSWORD=your-16-char-app-password")
            elif provider == "outlook":
                self.log(f"   - OUTLOOK_USERNAME=your-email@outlook.com")
                self.log(f"   - OUTLOOK_PASSWORD=your-password")
            else:
                self.log(f"   - SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email or config["username"]
            msg['To'] = ", ".join(to_emails)
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            self.log(f"Connecting to {config['server']}:{config['port']}...")
            
            if config["use_tls"]:
                server = smtplib.SMTP(config["server"], config["port"])
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(config["server"], config["port"])
            
            # Login
            self.log(f"Logging in as {config['username']}...")
            server.login(config["username"], config["password"])
            
            # Send email
            self.log(f"Sending to {len(to_emails)} recipients...")
            server.send_message(msg)
            server.quit()
            
            self.log(f"✓ Email sent successfully via {provider.upper()}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            self.log(f"✗ Authentication failed: {e}")
            self.log(f"   For Gmail: Use App Password, not regular password")
            self.log(f"   Generate at: https://myaccount.google.com/apppasswords")
            return False
            
        except Exception as e:
            self.log(f"✗ Error: {e}")
            return False
    
    def test_connection(self, provider):
        """Test SMTP connection without sending"""
        self.log(f"Testing {provider.upper()} connection...")
        
        config = self.smtp_config.get(provider)
        if not config or not config["username"] or not config["password"]:
            self.log(f"✗ {provider.upper()}: No credentials configured")
            return False
        
        try:
            if config["use_tls"]:
                server = smtplib.SMTP(config["server"], config["port"], timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(config["server"], config["port"], timeout=10)
            
            server.login(config["username"], config["password"])
            server.quit()
            
            self.log(f"✓ {provider.upper()}: Connection successful")
            return True
            
        except Exception as e:
            self.log(f"✗ {provider.upper()}: Connection failed - {e}")
            return False
    
    def send_agent_reports(self, report_file, to_emails):
        """Send all agent reports"""
        self.log("="*80)
        self.log("SENDING AGENT REPORTS VIA SMTP")
        self.log("="*80)
        
        # Load reports
        with open(report_file, 'r') as f:
            reports = f.read()
        
        subject = "ECHONATE: All 12 Agent Reports - Autonomous Delivery"
        
        # Try providers in order
        providers = ["gmail", "outlook", "custom"]
        
        for provider in providers:
            self.log(f"\nTrying {provider.upper()}...")
            if self.send_email(provider, to_emails, subject, reports):
                return True
        
        self.log("\n✗ All SMTP providers failed")
        self.log("SOLUTION: Set up credentials for at least one provider")
        return False

def print_setup_instructions():
    """Print setup instructions"""
    print("\n" + "="*80)
    print("SMTP EMAIL AGENT - SETUP INSTRUCTIONS")
    print("="*80)
    print("\nTo enable automatic email sending, you need to configure SMTP credentials.")
    print("\n--- OPTION 1: Gmail (Recommended) ---")
    print("1. Go to: https://myaccount.google.com/apppasswords")
    print("2. Generate a 16-character App Password")
    print("3. Set environment variables:")
    print("   export GMAIL_USERNAME='your-email@gmail.com'")
    print("   export GMAIL_APP_PASSWORD='your-16-char-app-password'")
    print("\n--- OPTION 2: Outlook ---")
    print("1. Use your Outlook/Hotmail email and password")
    print("2. Set environment variables:")
    print("   export OUTLOOK_USERNAME='your-email@outlook.com'")
    print("   export OUTLOOK_PASSWORD='your-password'")
    print("\n--- OPTION 3: Custom SMTP Server ---")
    print("1. Get SMTP server details from your email provider")
    print("2. Set environment variables:")
    print("   export SMTP_SERVER='smtp.example.com'")
    print("   export SMTP_PORT='587'")
    print("   export SMTP_USERNAME='your-username'")
    print("   export SMTP_PASSWORD='your-password'")
    print("   export SMTP_USE_TLS='true'")
    print("\n" + "="*80)
    print("After setting credentials, run this script again to send emails.")
    print("="*80 + "\n")

def main():
    """Main execution"""
    agent = SMTPEmailAgent()
    
    print("\n" + "="*80)
    print("SMTP EMAIL AGENT - AUTONOMOUS EMAIL DELIVERY")
    print("="*80)
    
    # Test all configured providers
    print("\nTesting SMTP connections...")
    gmail_ok = agent.test_connection("gmail")
    outlook_ok = agent.test_connection("outlook")
    custom_ok = agent.test_connection("custom")
    
    if not (gmail_ok or outlook_ok or custom_ok):
        print("\n✗ No SMTP credentials configured")
        print_setup_instructions()
        return
    
    # Send agent reports
    report_file = "/tmp/agent_reports_20260109_123551.txt"
    to_emails = ["npoinsette@gmail.com", "king.thedros@gmail.com"]
    
    success = agent.send_agent_reports(report_file, to_emails)
    
    print("\n" + "="*80)
    print("EXECUTION COMPLETE")
    print("="*80)
    print(f"Status: {'SUCCESS' if success else 'FAILED'}")
    print("="*80 + "\n")
    
    # Save execution log
    log_file = f"/tmp/smtp_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "gmail_configured": gmail_ok,
            "outlook_configured": outlook_ok,
            "custom_configured": custom_ok,
        }, f, indent=2)
    
    print(f"Execution log: {log_file}\n")

if __name__ == "__main__":
    main()
