"""
Transfer endpoint — initiates call transfer to a human receptionist.
"""

import json
from fastapi import APIRouter, Request
from app.middleware.signature import verify_retell_signature
from app.config import settings
from app.utils.logger import logger

router = APIRouter()


@router.post("/transfer-call")
async def transfer_call(request: Request):
    """
    Initiate transfer to a human receptionist.

    Called by the Retell Conversation Flow's HumanTransfer Function Node.
    Returns a message for the agent to speak before the transfer,
    along with transfer instructions for Retell.

    Request body (from Retell):
        {
            "args": {
                "reason": "Caller requested human assistance",
                "context_summary": "Patient asking about insurance..."
            },
            "call_id": "..."
        }

    Returns:
        {"result": {"status": "transferring", "message": "...", "transfer_number": "..."}}
    """
    raw_body = await verify_retell_signature(request)

    try:
        payload = json.loads(raw_body)
        args = payload.get("args", {})
        call_id = payload.get("call_id", "")
    except Exception as e:
        logger.error(f"ERROR - Failed to parse transfer request: {e}")
        return {
            "result": {
                "status": "failed",
                "message": "I'm having trouble right now. Please try calling back.",
            }
        }

    reason = args.get("reason", "No reason provided")
    context = args.get("context_summary", "")

    logger.info(
        f"INFO - Transfer requested: call_id={call_id} | "
        f"reason={reason} | context={context}"
    )

    return {
        "result": {
            "status": "transferring",
            "transfer_number": settings.transfer_phone_number,
            "message": (
                "I'll transfer you to our front desk team right away. "
                "Please hold for just a moment while I connect you."
            ),
        }
    }
