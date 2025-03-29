"""
Module for sending email reports.
"""

import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Dict, Any, Optional
from datetime import datetime

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailSender:
    """Class for sending email reports."""
    
    def __init__(
        self,
        sender_email: str = None,
        sender_password: str = None,
        recipient_email: str = None,
        smtp_server: str = None,
        smtp_port: int = None
    ):
        """
        Initialize the email sender.
        
        Args:
            sender_email: Email address to send from. If None, uses the value from config.
            sender_password: Password or app password for the sender email. If None, uses the value from config.
            recipient_email: Email address to send to. If None, uses the value from config.
            smtp_server: SMTP server to use. If None, uses the value from config.
            smtp_port: SMTP port to use. If None, uses the value from config.
        """
        self.sender_email = sender_email or config.EMAIL_SENDER
        self.sender_password = sender_password or config.EMAIL_PASSWORD
        self.recipient_email = recipient_email or config.EMAIL_RECIPIENT
        self.smtp_server = smtp_server or config.EMAIL_SMTP_SERVER
        self.smtp_port = smtp_port or config.EMAIL_SMTP_PORT
        
        logger.info("Email sender initialized")
    
    def send_email(
        self,
        subject: str,
        body_html: str,
        body_text: str = None,
        attachments: List[str] = None
    ) -> bool:
        """
        Send an email.
        
        Args:
            subject: Email subject
            body_html: HTML content of the email
            body_text: Plain text content of the email. If None, uses the HTML content.
            attachments: List of file paths to attach to the email
            
        Returns:
            True if the email was sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))
            
            msg.attach(MIMEText(body_html, 'html'))
            
            if attachments:
                for attachment_path in attachments:
                    if os.path.exists(attachment_path):
                        with open(attachment_path, 'rb') as f:
                            attachment = MIMEApplication(f.read())
                            attachment_filename = os.path.basename(attachment_path)
                            attachment.add_header(
                                'Content-Disposition',
                                f'attachment; filename="{attachment_filename}"'
                            )
                            msg.attach(attachment)
                    else:
                        logger.warning(f"Attachment not found: {attachment_path}")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to: {self.recipient_email}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_summary_report(
        self,
        summaries: List[Dict[str, Any]],
        report_title: str = "Crypto YouTube Summary Report",
        attachments: List[str] = None
    ) -> bool:
        """
        Send a summary report email.
        
        Args:
            summaries: List of summary information dictionaries
            report_title: Title of the report
            attachments: List of file paths to attach to the email
            
        Returns:
            True if the email was sent successfully, False otherwise
        """
        if not summaries:
            logger.warning("No summaries provided for the report")
            return False
        
        try:
            report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            subject = f"{report_title} - {report_date}"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                    h2 {{ color: #3498db; margin-top: 30px; }}
                    .video-summary {{ margin-bottom: 30px; border-left: 4px solid #3498db; padding-left: 15px; }}
                    .video-title {{ font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
                    .video-meta {{ font-size: 14px; color: #7f8c8d; margin-bottom: 10px; }}
                    .video-summary-text {{ margin-top: 10px; }}
                    .video-link {{ color: #3498db; text-decoration: none; }}
                    .video-link:hover {{ text-decoration: underline; }}
                    .footer {{ margin-top: 40px; font-size: 12px; color: #7f8c8d; border-top: 1px solid #eee; padding-top: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>{report_title}</h1>
                    <p>Report generated on {report_date}</p>
                    <p>Here are the latest summaries from cryptocurrency YouTube channels:</p>
            """
            
            for summary in summaries:
                video_title = summary.get('title', 'Untitled Video')
                channel_title = summary.get('channel_title', 'Unknown Channel')
                video_url = summary.get('url', '#')
                published_at = summary.get('published_at', 'Unknown date')
                view_count = summary.get('view_count', 'N/A')
                summary_text = summary.get('summary', 'No summary available')
                
                html_content += f"""
                    <div class="video-summary">
                        <div class="video-title">
                            <a href="{video_url}" class="video-link" target="_blank">{video_title}</a>
                        </div>
                        <div class="video-meta">
                            Channel: {channel_title} | Published: {published_at} | Views: {view_count}
                        </div>
                        <div class="video-summary-text">
                            <p>{summary_text}</p>
                        </div>
                    </div>
                """
            
            html_content += """
                    <div class="footer">
                        <p>This is an automated report generated by the Crypto YouTube News Summarizer.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"{report_title}\n\nReport generated on {report_date}\n\n"
            text_content += "Here are the latest summaries from cryptocurrency YouTube channels:\n\n"
            
            for summary in summaries:
                video_title = summary.get('title', 'Untitled Video')
                channel_title = summary.get('channel_title', 'Unknown Channel')
                video_url = summary.get('url', '#')
                published_at = summary.get('published_at', 'Unknown date')
                view_count = summary.get('view_count', 'N/A')
                summary_text = summary.get('summary', 'No summary available')
                
                text_content += f"""
                {video_title}
                Channel: {channel_title} | Published: {published_at} | Views: {view_count}
                URL: {video_url}
                
                {summary_text}
                
                ----------------------------------------
                
                """
            
            return self.send_email(
                subject=subject,
                body_html=html_content,
                body_text=text_content,
                attachments=attachments
            )
        
        except Exception as e:
            logger.error(f"Error sending summary report: {e}")
            return False
