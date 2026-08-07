"""
Email Service — SendGrid Integration
"""
import logging
from typing import Optional, Dict, Any

from ..config import Config

logger = logging.getLogger(__name__)


class EmailService:
    """Email service using SendGrid"""

    def __init__(self):
        self.api_key = Config.EMAIL_HOST_PASSWORD
        self.from_email = Config.EMAIL_FROM
        self.client = None
        
        if self.api_key:
            try:
                from sendgrid import SendGridAPIClient
                self.client = SendGridAPIClient(self.api_key)
            except ImportError:
                logger.warning("SendGrid not installed. Email features will be disabled.")
        else:
            logger.warning("SendGrid API key not configured. Email features will be disabled.")

    def send_email(self, to_email: str, subject: str, html_content: str, plain_text: Optional[str] = None) -> bool:
        """Send an email"""
        if not self.client:
            logger.warning("Email client not configured. Skipping email send.")
            return False
        
        try:
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            if plain_text:
                message.plain_text_content = Content("text/plain", plain_text)
            
            response = self.client.send(message)
            
            if response.status_code == 202:
                logger.info(f"Email sent to {to_email} with subject: {subject}")
                return True
            else:
                logger.error(f"Email send failed with status: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Email send error: {str(e)}")
            return False

    def send_otp_email(self, to_email: str, otp: str, name: str = "User") -> bool:
        """Send OTP verification email"""
        subject = "Your Legal Combines OS Verification Code"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #1a365d;">Legal Combines OS</h1>
            <p>Hello {name},</p>
            <p>Your verification code is:</p>
            <div style="background: #f0f0f0; padding: 15px; border-radius: 8px; text-align: center; font-size: 24px; font-weight: bold;">
                {otp}
            </div>
            <p>This code will expire in 5 minutes.</p>
        </body>
        </html>
        """
        
        plain_text = f"Your Legal Combines OS verification code is: {otp}"
        return self.send_email(to_email, subject, html_content, plain_text)

    def send_welcome_email(self, to_email: str, name: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to Legal Combines OS!"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #1a365d;">Welcome to Legal Combines OS</h1>
            <p>Hello {name},</p>
            <p>Thank you for joining Legal Combines OS — the AI-Powered Global Legal Compliance Platform.</p>
            <p>Here's what you can do next:</p>
            <ul>
                <li>Upload your first document for AI analysis</li>
                <li>Check compliance score for your business</li>
                <li>Connect with verified lawyers</li>
            </ul>
        </body>
        </html>
        """
        
        plain_text = f"Welcome to Legal Combines OS {name}!"
        return self.send_email(to_email, subject, html_content, plain_text)

    def send_payment_confirmation(self, to_email: str, amount: float, plan: str) -> bool:
        """Send payment confirmation email"""
        subject = "Payment Confirmation — Legal Combines OS"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #1a365d;">Payment Confirmed</h1>
            <p>Your payment of <strong>₹{amount}</strong> for the <strong>{plan}</strong> plan has been successfully processed.</p>
            <p>Your subscription is now active.</p>
        </body>
        </html>
        """
        
        plain_text = f"Payment confirmed for {plan} plan. Amount: ₹{amount}."
        return self.send_email(to_email, subject, html_content, plain_text)
