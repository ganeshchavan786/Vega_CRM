import logging
from typing import Optional, Dict, Any
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from app.config.email_config import get_email_config, is_email_configured

logger = logging.getLogger(__name__)

# Setup Jinja2 environment for email templates
from app.config.email_config import email_config
env = Environment(
    loader=FileSystemLoader(email_config.email_templates_path),
    autoescape=True
)

# FastMail configuration - only create if email is configured
fast_mail = None

def initialize_email_service():
    """Initialize email service with current settings"""
    global fast_mail
    if is_email_configured():
        try:
            config = get_email_config()
            mail_config = ConnectionConfig(
                MAIL_USERNAME=config.get("smtp_username", ""),
                MAIL_PASSWORD=config.get("smtp_password", ""),
                MAIL_FROM=config.get("smtp_from_email", ""),
                MAIL_FROM_NAME=config.get("smtp_from_name", "Vega CRM"),
                MAIL_PORT=config.get("smtp_port", 587),
                MAIL_SERVER=config.get("smtp_host", ""),
                MAIL_STARTTLS=config.get("smtp_use_tls", True),
                MAIL_SSL_TLS=False,
                USE_CREDENTIALS=True,
                TEMPLATE_FOLDER=email_config.email_templates_path,
            )
            fast_mail = FastMail(mail_config)
            logger.info("Email service initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize email service: {str(e)}")
            fast_mail = None
    else:
        logger.warning("Email not configured. Email service disabled.")
        fast_mail = None

# Initialize on import
initialize_email_service()

async def send_email(
    to_email: str,
    subject: str,
    template_name: str,
    template_data: Dict[str, Any]
) -> bool:
    """
    Generic function to send email using template
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        template_name: Name of the template file
        template_data: Data to render in template
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not is_email_configured() or fast_mail is None:
        logger.warning("Email not configured. Skipping email send.")
        return False
    
    try:
        # Render template
        template = env.get_template(template_name)
        html_body = template.render(**template_data)
        
        # Create message
        message = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=html_body,
            subtype="html"
        )
        
        # Send email
        await fast_mail.send_message(message)
        logger.info(f"Email sent successfully to {to_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

async def send_welcome_email(
    user_email: str,
    user_name: str,
    role: Optional[str] = None
) -> bool:
    """Send welcome email to new user"""
    template_data = {
        'user_name': user_name,
        'user_email': user_email,
        'role': role or 'user'
    }
    
    subject = "Welcome to Vega CRM!"
    
    return await send_email(
        to_email=user_email,
        subject=subject,
        template_name="welcome.html",
        template_data=template_data
    )

async def send_password_reset_email(
    user_email: str,
    user_name: str,
    reset_token: str,
    reset_url: str
) -> bool:
    """Send password reset email"""
    template_data = {
        'user_name': user_name,
        'user_email': user_email,
        'reset_token': reset_token,
        'reset_url': reset_url
    }
    
    subject = "Password Reset Request - Vega CRM"
    
    return await send_email(
        to_email=user_email,
        subject=subject,
        template_name="password_reset.html",
        template_data=template_data
    )

