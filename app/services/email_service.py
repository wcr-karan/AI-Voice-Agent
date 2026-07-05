"""
Email service — sends appointment confirmation emails via SMTP.

Uses aiosmtplib for async sending and Jinja2 for HTML templating.
Designed to be called from FastAPI BackgroundTasks to avoid blocking.
"""

import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.config import settings
from app.utils.logger import logger


# Initialize Jinja2 template engine
TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=True,
)


class EmailService:
    """
    Async email sender for appointment confirmations.

    Features:
    - HTML templated emails via Jinja2
    - Async SMTP via aiosmtplib (non-blocking)
    - Single retry with backoff on failure
    - Structured logging for send status
    """

    MAX_RETRIES = 1
    RETRY_DELAY_SECONDS = 5

    async def send_confirmation_email(
        self,
        to_email: str,
        customer_name: str,
        service_type: str,
        appointment_date: str,
        appointment_time: str,
        booking_id: str,
    ) -> bool:
        """
        Send an appointment confirmation email.

        Args:
            to_email: Recipient email address.
            customer_name: Patient's name.
            service_type: Booked dental service.
            appointment_date: Formatted date string.
            appointment_time: Formatted time string.
            booking_id: Unique booking reference.

        Returns:
            True if email was sent successfully.
        """
        logger.info(f"INFO - Sending confirmation email to {to_email} for booking {booking_id}")

        # Render HTML template
        try:
            template = jinja_env.get_template("confirmation_email.html")
            html_body = template.render(
                customer_name=customer_name,
                service_type=service_type,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                booking_id=booking_id,
                clinic_name=settings.clinic_name,
                clinic_phone=settings.clinic_phone,
                clinic_address=settings.clinic_address,
            )
        except Exception as e:
            logger.error(f"ERROR - Failed to render email template: {e}")
            return False

        # Build MIME message
        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.email_from_name} <{settings.email_from_address}>"
        message["To"] = to_email
        message["Subject"] = f"Appointment Confirmed — {service_type} on {appointment_date} | {settings.clinic_name}"

        # Plain-text fallback
        plain_text = (
            f"Hi {customer_name},\n\n"
            f"Your appointment has been confirmed!\n\n"
            f"Service: {service_type}\n"
            f"Date: {appointment_date}\n"
            f"Time: {appointment_time}\n"
            f"Booking Reference: {booking_id}\n\n"
            f"Location: {settings.clinic_address}\n"
            f"Phone: {settings.clinic_phone}\n\n"
            f"If you need to reschedule or cancel, please call us at {settings.clinic_phone}.\n\n"
            f"Thank you,\n{settings.clinic_name}"
        )

        message.attach(MIMEText(plain_text, "plain"))
        message.attach(MIMEText(html_body, "html"))

        # Send with retry
        # TODO: Migrate from standard SMTP to a reliable email provider API (like SendGrid or Resend) in production.
        # TODO: Add support for SMS or WhatsApp confirmations.
        for attempt in range(1, self.MAX_RETRIES + 2):
            try:
                await aiosmtplib.send(
                    message,
                    hostname=settings.smtp_host,
                    port=settings.smtp_port,
                    username=settings.smtp_username,
                    password=settings.smtp_password,
                    start_tls=True,
                )
                logger.info(f"INFO - Confirmation email sent to {to_email} (attempt {attempt})")
                return True
            except Exception as e:
                logger.warning(f"WARNING - Email send attempt {attempt} failed: {e}")
                if attempt <= self.MAX_RETRIES:
                    await asyncio.sleep(self.RETRY_DELAY_SECONDS)

        logger.error(f"ERROR - Failed to send confirmation email to {to_email} after {self.MAX_RETRIES + 1} attempts")
        return False

    def send_confirmation_email_sync(self, **kwargs) -> bool:
        """
        Synchronous wrapper for send_confirmation_email.

        Used when called from FastAPI BackgroundTasks which
        can run async functions but sometimes needs a sync interface.
        """
        return asyncio.run(self.send_confirmation_email(**kwargs))


# Singleton instance
email_service = EmailService()
