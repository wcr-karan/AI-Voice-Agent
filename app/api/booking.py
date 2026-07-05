"""
Booking endpoint — called by Retell Function Node during live calls.

Receives customer details and appointment preferences,
validates and books the appointment, triggers confirmation email.
"""

import json
from fastapi import APIRouter, Request, BackgroundTasks
from app.middleware.signature import verify_retell_signature
from app.models.appointment import BookAppointmentRequest
from app.services.booking_service import booking_service
from app.services.email_service import email_service
from app.utils.logger import logger
from app.utils.datetime_helpers import parse_date, format_date_for_speech

router = APIRouter()


@router.post("/book-appointment")
async def book_appointment(request: Request, background_tasks: BackgroundTasks):
    """
    Book an appointment during a live call.

    Called by the Retell Conversation Flow's BookAppointment Function Node.
    Validates inputs, writes to Google Sheets, and sends a confirmation email
    asynchronously via BackgroundTasks.

    Request body (from Retell):
        {
            "args": {
                "customer_name": "...",
                "customer_phone": "...",
                "customer_email": "...",
                "service_type": "...",
                "appointment_date": "...",
                "appointment_time": "..."
            },
            "call_id": "..."
        }

    Returns:
        {"result": {"booking_id": "...", "status": "...", "message": "..."}}
    """
    # Verify signature
    raw_body = await verify_retell_signature(request)

    try:
        payload = json.loads(raw_body)
        req = BookAppointmentRequest(**payload)
    except Exception as e:
        logger.error(f"ERROR - Failed to parse booking request: {e}")
        return {
            "result": {
                "status": "failed",
                "message": "I encountered a technical issue. Let me transfer you to our front desk.",
            }
        }

    # Attempt booking
    result = booking_service.book_appointment(
        customer_name=req.customer_name,
        customer_phone=req.customer_phone,
        customer_email=req.customer_email,
        service_type=req.service_type,
        appointment_date_str=req.appointment_date,
        appointment_time_str=req.appointment_time,
        call_id=req.call_id,
    )

    # If booking succeeded, queue confirmation email
    if result.status == "confirmed" and req.customer_email:
        # Format date for the email
        parsed_date = parse_date(req.appointment_date)
        formatted_date = format_date_for_speech(parsed_date) if parsed_date else req.appointment_date

        background_tasks.add_task(
            email_service.send_confirmation_email,
            to_email=req.customer_email,
            customer_name=req.customer_name,
            service_type=req.service_type,
            appointment_date=formatted_date,
            appointment_time=result.message.split("at ")[-1].split(".")[0] if "at " in result.message else req.appointment_time,
            booking_id=result.booking_id,
        )
        logger.info(f"INFO - Confirmation email queued for {req.customer_email}")

    return {
        "result": {
            "booking_id": result.booking_id,
            "status": result.status,
            "message": result.message,
        }
    }
