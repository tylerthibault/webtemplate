"""
Email utilities for sending notifications and confirmations.

Handles email composition and delivery.
"""

from typing import Dict, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class EmailUtils:
    """
    Email sending utilities.

    Constitutional compliance: Utility layer for email operations.
    """

    @staticmethod
    def get_email_config(app):
        """
        Get email configuration from Flask app config.

        Args:
            app: Flask application instance

        Returns:
            dict: Email configuration
        """
        return {
            "smtp_server": app.config.get("SMTP_SERVER", "localhost"),
            "smtp_port": app.config.get("SMTP_PORT", 587),
            "smtp_username": app.config.get("SMTP_USERNAME", ""),
            "smtp_password": app.config.get("SMTP_PASSWORD", ""),
            "smtp_use_tls": app.config.get("SMTP_USE_TLS", True),
            "from_email": app.config.get("FROM_EMAIL", "noreply@example.com"),
            "from_name": app.config.get("FROM_NAME", "Flask Portfolio"),
            "admin_email": app.config.get("ADMIN_EMAIL", "admin@example.com"),
            "email_enabled": app.config.get("EMAIL_ENABLED", False),
        }

    @staticmethod
    def create_contact_confirmation_email(
        name: str, email: str, subject: str, message: str
    ) -> Dict[str, str]:
        """
        Create confirmation email for contact form submitter.

        Args:
            name: Sender's name
            email: Sender's email
            subject: Message subject
            message: Message content

        Returns:
            dict: Email data with subject and body
        """
        email_subject = f"Contact Form Confirmation - {subject}"

        email_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #0d6efd;">Thank You for Contacting Us!</h2>
                    
                    <p>Hi {name},</p>
                    
                    <p>We've received your message and will get back to you as soon as possible.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #0d6efd; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Your Message:</h3>
                        <p><strong>Subject:</strong> {subject}</p>
                        <p><strong>Message:</strong></p>
                        <p style="white-space: pre-wrap;">{message}</p>
                    </div>
                    
                    <p>If you have any additional questions, feel free to reply to this email.</p>
                    
                    <p>Best regards,<br>
                    The Portfolio Team</p>
                    
                    <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #6c757d;">
                        This is an automated confirmation email. Please do not reply directly to this message.
                    </p>
                </div>
            </body>
        </html>
        """

        return {
            "subject": email_subject,
            "body": email_body,
            "to_email": email,
            "to_name": name,
        }

    @staticmethod
    def create_contact_notification_email(
        name: str, email: str, subject: str, message: str, submitted_at: datetime
    ) -> Dict[str, str]:
        """
        Create notification email for admin about new contact form submission.

        Args:
            name: Sender's name
            email: Sender's email
            subject: Message subject
            message: Message content
            submitted_at: Submission timestamp

        Returns:
            dict: Email data with subject and body
        """
        email_subject = f"New Contact Form Submission: {subject}"

        formatted_time = submitted_at.strftime("%Y-%m-%d %H:%M:%S UTC")

        email_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #198754;">New Contact Form Submission</h2>
                    
                    <p>A new message has been submitted via the contact form.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #198754; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Submission Details:</h3>
                        <p><strong>From:</strong> {name} ({email})</p>
                        <p><strong>Subject:</strong> {subject}</p>
                        <p><strong>Submitted:</strong> {formatted_time}</p>
                        <hr style="border: none; border-top: 1px solid #dee2e6; margin: 15px 0;">
                        <p><strong>Message:</strong></p>
                        <p style="white-space: pre-wrap;">{message}</p>
                    </div>
                    
                    <p>
                        <a href="mailto:{email}" style="display: inline-block; background-color: #0d6efd; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            Reply to {name}
                        </a>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #6c757d;">
                        This is an automated notification from your portfolio contact form.
                    </p>
                </div>
            </body>
        </html>
        """

        return {"subject": email_subject, "body": email_body}

    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_body: str,
        from_email: str,
        from_name: str,
        smtp_config: Dict,
        to_name: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Send an email using SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            from_email: Sender email address
            from_name: Sender name
            smtp_config: SMTP configuration dict
            to_name: Optional recipient name

        Returns:
            tuple: (success: bool, error_message: Optional[str])
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{from_name} <{from_email}>"
            msg["To"] = f"{to_name} <{to_email}>" if to_name else to_email

            # Attach HTML body
            html_part = MIMEText(html_body, "html")
            msg.attach(html_part)

            # Connect to SMTP server and send
            if smtp_config.get("smtp_use_tls", True):
                server = smtplib.SMTP(
                    smtp_config["smtp_server"], smtp_config["smtp_port"]
                )
                server.starttls()
            else:
                server = smtplib.SMTP(
                    smtp_config["smtp_server"], smtp_config["smtp_port"]
                )

            # Login if credentials provided
            if smtp_config.get("smtp_username") and smtp_config.get("smtp_password"):
                server.login(smtp_config["smtp_username"], smtp_config["smtp_password"])

            # Send email
            server.send_message(msg)
            server.quit()

            return True, None

        except Exception as e:
            error_message = f"Failed to send email: {str(e)}"
            return False, error_message

    @staticmethod
    def send_contact_confirmation(
        contact_data: Dict, app
    ) -> tuple[bool, Optional[str]]:
        """
        Send confirmation email to contact form submitter.

        Args:
            contact_data: Contact form data dict
            app: Flask application instance

        Returns:
            tuple: (success: bool, error_message: Optional[str])
        """
        config = EmailUtils.get_email_config(app)

        # Check if email is enabled
        if not config["email_enabled"]:
            return False, "Email sending is disabled in configuration"

        # Create email
        email_data = EmailUtils.create_contact_confirmation_email(
            name=contact_data["name"],
            email=contact_data["email"],
            subject=contact_data["subject"],
            message=contact_data["message"],
        )

        # Send email
        return EmailUtils.send_email(
            to_email=email_data["to_email"],
            subject=email_data["subject"],
            html_body=email_data["body"],
            from_email=config["from_email"],
            from_name=config["from_name"],
            smtp_config=config,
            to_name=email_data["to_name"],
        )

    @staticmethod
    def send_contact_notification(
        contact_data: Dict, app
    ) -> tuple[bool, Optional[str]]:
        """
        Send notification email to admin about new contact form submission.

        Args:
            contact_data: Contact form data dict
            app: Flask application instance

        Returns:
            tuple: (success: bool, error_message: Optional[str])
        """
        config = EmailUtils.get_email_config(app)

        # Check if email is enabled
        if not config["email_enabled"]:
            return False, "Email sending is disabled in configuration"

        # Create email
        email_data = EmailUtils.create_contact_notification_email(
            name=contact_data["name"],
            email=contact_data["email"],
            subject=contact_data["subject"],
            message=contact_data["message"],
            submitted_at=contact_data.get("submitted_at", datetime.utcnow()),
        )

        # Send email
        return EmailUtils.send_email(
            to_email=config["admin_email"],
            subject=email_data["subject"],
            html_body=email_data["body"],
            from_email=config["from_email"],
            from_name=config["from_name"],
            smtp_config=config,
        )
