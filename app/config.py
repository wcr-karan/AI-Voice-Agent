"""
QuensultingAI Dental Clinic — AI Voice Agent
Application configuration via environment variables.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- App ---
    app_env: str = Field(default="development", description="Environment: development | staging | production")
    app_port: int = Field(default=8000, description="Server port")
    app_host: str = Field(default="0.0.0.0", description="Server host")

    # --- RetellAI ---
    retell_api_key: str = Field(default="", description="Retell AI API key")
    retell_agent_id: str = Field(default="", description="Retell AI Agent ID")
    retell_webhook_secret: str = Field(default="", description="Retell webhook signing secret")

    # --- Google Sheets ---
    google_sheets_spreadsheet_id: str = Field(default="", description="Google Sheets spreadsheet ID")
    google_service_account_file: str = Field(default="service_account.json", description="Path to GCP service account JSON")

    # --- Email (SMTP) ---
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_username: str = Field(default="", description="SMTP username")
    smtp_password: str = Field(default="", description="SMTP password or app password")
    email_from_name: str = Field(default="QuensultingAI Dental Clinic", description="Sender display name")
    email_from_address: str = Field(default="", description="Sender email address")

    # --- Clinic Configuration ---
    clinic_name: str = Field(default="QuensultingAI Dental Clinic", description="Clinic display name")
    clinic_phone: str = Field(default="", description="Clinic phone number")
    clinic_address: str = Field(default="", description="Clinic physical address")
    transfer_phone_number: str = Field(default="", description="Human receptionist phone for call transfers")

    # --- Logging ---
    log_level: str = Field(default="INFO", description="Log level: DEBUG | INFO | WARNING | ERROR")

    # --- Clinic Services ---
    @property
    def available_services(self) -> list[str]:
        """Dental services offered by the clinic."""
        return [
            "Dental Cleaning",
            "Root Canal Treatment",
            "Teeth Whitening",
            "Braces Consultation",
            "Tooth Extraction",
            "General Dental Consultation",
        ]

    # --- Working Hours ---
    @property
    def working_days(self) -> list[int]:
        """Working days as weekday integers (0=Monday, 5=Saturday)."""
        return [0, 1, 2, 3, 4, 5]  # Monday to Saturday

    @property
    def opening_hour(self) -> int:
        return 9  # 9 AM

    @property
    def closing_hour(self) -> int:
        return 18  # 6 PM

    @property
    def slot_duration_minutes(self) -> int:
        return 30  # 30-minute appointment slots

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton instance — import this across the app
settings = Settings()
