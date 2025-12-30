import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class EmailConfig(BaseSettings):
    """Email configuration settings - reads from .env"""
    
    # Email Templates Path
    email_templates_path: str = "app/templates/emails"
    
    # Alternative paths for different working directories
    @property
    def resolved_templates_path(self) -> str:
        import os
        paths = [
            self.email_templates_path,
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app", "templates", "emails"),
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return self.email_templates_path
    
    # Scheduler Settings
    reminder_days_before: int = int(os.getenv("REMINDER_DAYS_BEFORE", "3"))
    scheduler_time: str = os.getenv("SCHEDULER_TIME", "09:00")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global config instance
email_config = EmailConfig()

def get_email_config() -> dict:
    """Get email configuration from .env"""
    return {
        "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_username": os.getenv("SMTP_USERNAME", ""),
        "smtp_password": os.getenv("SMTP_PASSWORD", ""),
        "smtp_from_email": os.getenv("SMTP_FROM_EMAIL", ""),
        "smtp_from_name": os.getenv("SMTP_FROM_NAME", "Vega CRM"),
        "smtp_use_tls": os.getenv("SMTP_USE_TLS", "True").lower() == "true",
    }

def is_email_configured() -> bool:
    """Check if email is properly configured"""
    config = get_email_config()
    return bool(
        config.get("smtp_username") and 
        config.get("smtp_password") and 
        config.get("smtp_from_email")
    )

# For backward compatibility
class EmailSettings:
    """Backward compatibility class"""
    def __init__(self):
        config = get_email_config()
        self.smtp_host = config.get("smtp_host", "")
        self.smtp_port = config.get("smtp_port", 587)
        self.smtp_username = config.get("smtp_username", "")
        self.smtp_password = config.get("smtp_password", "")
        self.smtp_from_email = config.get("smtp_from_email", "")
        self.smtp_from_name = config.get("smtp_from_name", "Vega CRM")
        self.smtp_use_tls = config.get("smtp_use_tls", True)
        self.email_templates_path = email_config.email_templates_path
        self.reminder_days_before = email_config.reminder_days_before
        self.scheduler_time = email_config.scheduler_time

# Global email settings instance
email_settings = EmailSettings()

