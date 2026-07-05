"""
Booking service — orchestrates appointment creation with validation.

Handles:
- Date/time validation
- Working hours enforcement
- Slot conflict detection
- Booking ID generation
- Google Sheets persistence
"""

import re
from datetime import datetime
from app.config import settings
from app.models.appointment import AppointmentRecord, BookingResponse, AppointmentStatus
from app.services.sheets_service import sheets_service
from app.utils.datetime_helpers import (
    parse_date,
    parse_time,
    is_working_day,
    is_future_date,
    is_within_working_hours,
    generate_time_slots,
    generate_booking_id,
    format_date_for_speech,
    format_time_for_speech,
)
from app.utils.logger import logger


class BookingService:
    """
    Business logic for appointment booking.

    Validates inputs, checks for conflicts, writes to Sheets,
    and returns speech-friendly responses for the Retell agent.
    """

    def book_appointment(
        self,
        customer_name: str,
        customer_phone: str,
        customer_email: str,
        service_type: str,
        appointment_date_str: str,
        appointment_time_str: str,
        call_id: str = "",
    ) -> BookingResponse:
        """
        Create a new appointment booking.

        Performs full validation, checks for slot conflicts,
        writes to Google Sheets, and returns a structured response.

        Args:
            customer_name: Patient's full name.
            customer_phone: Patient's phone number.
            customer_email: Patient's email address.
            service_type: Dental service type.
            appointment_date_str: Date string (flexible format).
            appointment_time_str: Time string (flexible format).
            call_id: Associated Retell call ID.

        Returns:
            BookingResponse with status and speech-ready message.
        """
        logger.info(
            f"INFO - Booking request: {customer_name} | {service_type} | "
            f"{appointment_date_str} {appointment_time_str}"
        )

        # --- Validate service type ---
        if service_type not in settings.available_services:
            logger.warning(f"WARNING - Invalid service requested: {service_type}")
            return BookingResponse(
                status="failed",
                message=(
                    f"I'm sorry, '{service_type}' is not one of our available services. "
                    f"We offer: {', '.join(settings.available_services)}."
                ),
            )

        # --- Validate email format ---
        # TODO: Replace basic regex with a dedicated domain validator and MX record check in production.
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not customer_email or not re.match(email_pattern, customer_email):
            logger.warning(f"WARNING - Invalid email format: {customer_email}")
            return BookingResponse(
                status="failed",
                message="That email address format seems invalid. Could you please repeat your email address?",
            )

        # --- Validate phone number format ---
        # Accepts E.164 and common digit sequences with spaces, hyphens, and parentheses
        phone_pattern = r"^\+?[\d\s\-()]{7,20}$"
        if not customer_phone or not re.match(phone_pattern, customer_phone):
            logger.warning(f"WARNING - Invalid phone format: {customer_phone}")
            return BookingResponse(
                status="failed",
                message="That phone number format seems invalid. Could you please repeat your phone number?",
            )

        # --- Parse and validate date ---
        parsed_date = parse_date(appointment_date_str)
        if parsed_date is None:
            logger.warning(f"WARNING - Invalid appointment date (unparseable): {appointment_date_str}")
            return BookingResponse(
                status="failed",
                message="I couldn't understand that date. Could you please provide the date again, such as July 5th, 2026?",
            )

        if not is_future_date(parsed_date):
            logger.warning(f"WARNING - Invalid appointment date (past date): {parsed_date}")
            return BookingResponse(
                status="failed",
                message="That date has already passed. Could you choose a future date?",
            )

        if not is_working_day(parsed_date):
            logger.warning(f"WARNING - Invalid appointment date (Sunday/Non-working): {parsed_date}")
            return BookingResponse(
                status="failed",
                message=(
                    f"{format_date_for_speech(parsed_date)} is a Sunday, and we're closed. "
                    "We're open Monday through Saturday. Would you like to pick another day?"
                ),
            )

        # --- Parse and validate time ---
        parsed_time = parse_time(appointment_time_str)
        if parsed_time is None:
            logger.warning(f"WARNING - Invalid appointment time (unparseable): {appointment_time_str}")
            return BookingResponse(
                status="failed",
                message="I couldn't understand that time. Could you say it again, like 10 AM or 2:30 PM?",
            )

        if not is_within_working_hours(parsed_time):
            logger.warning(f"WARNING - Invalid appointment time (outside working hours): {parsed_time}")
            return BookingResponse(
                status="failed",
                message=(
                    f"{format_time_for_speech(parsed_time)} is outside our working hours. "
                    "We're open from 9 AM to 6 PM. What time works for you?"
                ),
            )

        # --- Check for duplicate bookings ---
        # TODO: Support scanning across multiple sheets to prevent duplicate accounts.
        date_str = parsed_date.strftime("%Y-%m-%d")
        existing_bookings = sheets_service.get_appointments_by_date(date_str)
        for booking in existing_bookings:
            is_same_email = booking.get("Email", "").strip().lower() == customer_email.strip().lower()
            is_same_phone = booking.get("Phone", "").strip().replace(" ", "") == customer_phone.strip().replace(" ", "")
            if (is_same_email or is_same_phone) and booking.get("Service") == service_type:
                logger.warning(f"WARNING - Duplicate booking attempt for {customer_name} on {date_str}")
                return BookingResponse(
                    status="failed",
                    message=f"It looks like you already have an appointment booked for {service_type} on this day. We can only book one appointment per service type per day.",
                )

        # --- Check for slot conflicts ---
        booked_times = sheets_service.get_booked_times_for_date(date_str)
        formatted_time = format_time_for_speech(parsed_time)

        if formatted_time in booked_times or appointment_time_str in booked_times:
            # Find the next available slot
            # TODO: Integrate Google Calendar availability for real-time calendar synchronization.
            all_slots = generate_time_slots(parsed_date)
            available = [s for s in all_slots if s not in booked_times]

            if available:
                alternatives = ", ".join(available[:3])
                return BookingResponse(
                    status="conflict",
                    message=(
                        f"I'm sorry, {formatted_time} on {format_date_for_speech(parsed_date)} "
                        f"is already booked. Our next available slots are: {alternatives}. "
                        "Would any of these work for you?"
                    ),
                )
            else:
                return BookingResponse(
                    status="conflict",
                    message=(
                        f"I'm sorry, we're fully booked on {format_date_for_speech(parsed_date)}. "
                        "Would you like to try a different day?"
                    ),
                )

        # --- Generate booking ID ---
        sequence = sheets_service.get_next_booking_sequence(date_str)
        booking_id = generate_booking_id(parsed_date, sequence)

        # --- Create appointment record ---
        now = datetime.utcnow().isoformat() + "Z"
        record = AppointmentRecord(
            booking_id=booking_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            service_type=service_type,
            appointment_date=date_str,
            appointment_time=formatted_time,
            status=AppointmentStatus.CONFIRMED,
            booked_via="Voice Agent",
            call_id=call_id,
            created_at=now,
        )

        # --- Write to Google Sheets ---
        # TODO: Replace Google Sheets with PostgreSQL in production for improved locking, ACID, and performance.
        row_data = [
            record.booking_id,
            record.customer_name,
            record.customer_phone,
            record.customer_email,
            record.service_type,
            record.appointment_date,
            record.appointment_time,
            record.status.value,
            record.booked_via,
            record.call_id,
            record.created_at,
        ]

        success = sheets_service.append_appointment(row_data)

        if not success:
            logger.error(f"ERROR - Failed to write booking {booking_id} to Sheets")
            return BookingResponse(
                status="failed",
                message=(
                    "I'm sorry, I encountered an issue while booking your appointment. "
                    "Let me transfer you to our front desk to complete the booking."
                ),
            )

        logger.info(f"INFO - Appointment created: {booking_id} for {customer_name}")

        return BookingResponse(
            booking_id=booking_id,
            status="confirmed",
            message=(
                f"Your appointment has been confirmed! "
                f"Booking reference: {booking_id}. "
                f"{service_type} on {format_date_for_speech(parsed_date)} "
                f"at {formatted_time}. "
                f"A confirmation email will be sent to {customer_email}."
            ),
        )

    def check_availability(
        self,
        service_type: str,
        preferred_date_str: str,
    ) -> dict:
        """
        Check available appointment slots for a given date and service.

        Args:
            service_type: The dental service type.
            preferred_date_str: Date string (flexible format).

        Returns:
            Dict with 'available', 'slots', and 'message' keys.
        """
        logger.info(f"Availability check: {service_type} on {preferred_date_str}")

        # --- Parse date ---
        parsed_date = parse_date(preferred_date_str)
        if parsed_date is None:
            return {
                "available": False,
                "slots": [],
                "message": "I couldn't understand that date. Could you please provide it again?",
            }

        if not is_future_date(parsed_date):
            return {
                "available": False,
                "slots": [],
                "message": "That date has already passed. Could you choose a future date?",
            }

        if not is_working_day(parsed_date):
            return {
                "available": False,
                "slots": [],
                "message": (
                    f"{format_date_for_speech(parsed_date)} is a Sunday and we're closed. "
                    "We're open Monday through Saturday."
                ),
            }

        # --- Generate all slots and subtract booked ones ---
        date_str = parsed_date.strftime("%Y-%m-%d")
        all_slots = generate_time_slots(parsed_date)
        booked_times = sheets_service.get_booked_times_for_date(date_str)
        available_slots = [s for s in all_slots if s not in booked_times]

        if not available_slots:
            return {
                "available": False,
                "slots": [],
                "message": (
                    f"I'm sorry, we're fully booked on {format_date_for_speech(parsed_date)}. "
                    "Would you like to try a different day?"
                ),
            }

        # Limit to 5 slots for speech brevity
        spoken_slots = ", ".join(available_slots[:5])
        remaining = len(available_slots) - 5

        message = (
            f"We have {len(available_slots)} available slots on "
            f"{format_date_for_speech(parsed_date)}: {spoken_slots}"
        )
        if remaining > 0:
            message += f", and {remaining} more. Which time would you prefer?"
        else:
            message += ". Which time would you prefer?"

        return {
            "available": True,
            "slots": available_slots,
            "message": message,
        }


# Singleton instance
booking_service = BookingService()
