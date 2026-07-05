"""
Pydantic models for appointment data.
"""

from pydantic import BaseModel, Field
from enum import Enum


class AppointmentStatus(str, Enum):
    """Appointment status values."""
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    NO_SHOW = "No Show"


class BookAppointmentRequest(BaseModel):
    """
    Request payload from Retell Function Node to book an appointment.

    This matches the structure Retell sends when a Function Node
    triggers the /book-appointment endpoint.
    """
    args: dict = Field(..., description="Function arguments extracted by Retell")
    call_id: str = Field(..., description="Retell call ID")

    @property
    def customer_name(self) -> str:
        return self.args.get("customer_name", "")

    @property
    def customer_phone(self) -> str:
        return self.args.get("customer_phone", "")

    @property
    def customer_email(self) -> str:
        return self.args.get("customer_email", "")

    @property
    def service_type(self) -> str:
        return self.args.get("service_type", "")

    @property
    def appointment_date(self) -> str:
        return self.args.get("appointment_date", "")

    @property
    def appointment_time(self) -> str:
        return self.args.get("appointment_time", "")


class AppointmentRecord(BaseModel):
    """
    Represents a single appointment row in Google Sheets.
    Used for both reading existing records and writing new ones.
    """
    booking_id: str = Field(..., description="Unique booking ID (BK-YYYYMMDD-NNN)")
    customer_name: str = Field(..., description="Patient full name")
    customer_phone: str = Field(..., description="Patient phone number")
    customer_email: str = Field(..., description="Patient email address")
    service_type: str = Field(..., description="Dental service requested")
    appointment_date: str = Field(..., description="Appointment date (YYYY-MM-DD)")
    appointment_time: str = Field(..., description="Appointment time (e.g., 10:00 AM)")
    status: AppointmentStatus = Field(default=AppointmentStatus.CONFIRMED, description="Booking status")
    booked_via: str = Field(default="Voice Agent", description="Booking channel")
    call_id: str = Field(default="", description="Associated Retell call ID")
    created_at: str = Field(default="", description="ISO timestamp of creation")


class BookingResponse(BaseModel):
    """Response returned to Retell after booking attempt."""
    booking_id: str = Field(default="", description="Generated booking ID")
    status: str = Field(..., description="confirmed | failed | conflict")
    message: str = Field(..., description="Human-readable message for the agent to speak")


class CheckAvailabilityRequest(BaseModel):
    """
    Request payload from Retell Function Node to check slot availability.
    """
    args: dict = Field(..., description="Function arguments")
    call_id: str = Field(..., description="Retell call ID")

    @property
    def service_type(self) -> str:
        return self.args.get("service_type", "")

    @property
    def preferred_date(self) -> str:
        return self.args.get("preferred_date", "")


class AvailabilityResponse(BaseModel):
    """Response returned to Retell with available slots."""
    available: bool = Field(..., description="Whether any slots are available")
    slots: list[str] = Field(default_factory=list, description="List of available time strings")
    message: str = Field(..., description="Human-readable message for the agent to speak")
