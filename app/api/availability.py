"""
Availability endpoint — called by Retell Function Node to check open slots.
"""

import json
from fastapi import APIRouter, Request
from app.middleware.signature import verify_retell_signature
from app.models.appointment import CheckAvailabilityRequest
from app.services.booking_service import booking_service
from app.utils.logger import logger

router = APIRouter()


@router.post("/check-availability")
async def check_availability(request: Request):
    """
    Check available appointment slots for a given date.

    Called by the Retell Conversation Flow's CheckAvailability Function Node.

    Request body (from Retell):
        {
            "args": {
                "service_type": "Dental Cleaning",
                "preferred_date": "2026-07-05"
            },
            "call_id": "..."
        }

    Returns:
        {"result": {"available": bool, "slots": [...], "message": "..."}}
    """
    raw_body = await verify_retell_signature(request)

    try:
        payload = json.loads(raw_body)
        req = CheckAvailabilityRequest(**payload)
    except Exception as e:
        logger.error(f"ERROR - Failed to parse availability request: {e}")
        return {
            "result": {
                "available": False,
                "slots": [],
                "message": "I had trouble checking availability. Could you repeat the date?",
            }
        }

    result = booking_service.check_availability(
        service_type=req.service_type,
        preferred_date_str=req.preferred_date,
    )

    return {"result": result}
