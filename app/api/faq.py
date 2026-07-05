"""
FAQ endpoint — called by Retell Function Node to look up answers.
"""

import json
from fastapi import APIRouter, Request
from app.middleware.signature import verify_retell_signature
from app.models.faq import FAQRequest
from app.services.faq_service import faq_service
from app.utils.logger import logger

router = APIRouter()


@router.post("/check-faq")
async def check_faq(request: Request):
    """
    Look up an FAQ answer for the caller's question.

    Called by the Retell Conversation Flow's LookupFAQ Function Node.

    Request body (from Retell):
        {
            "args": {
                "question": "How much does teeth whitening cost?"
            },
            "call_id": "..."
        }

    Returns:
        {"result": {"found": bool, "answer": "...", "category": "...", "message": "..."}}
    """
    raw_body = await verify_retell_signature(request)

    try:
        payload = json.loads(raw_body)
        req = FAQRequest(**payload)
    except Exception as e:
        logger.error(f"ERROR - Failed to parse FAQ request: {e}")
        return {
            "result": {
                "found": False,
                "answer": "",
                "category": "",
                "message": "I had trouble looking that up. Could you repeat your question?",
            }
        }

    result = faq_service.lookup(req.question)

    return {
        "result": {
            "found": result.found,
            "answer": result.answer,
            "category": result.category,
            "message": result.message,
        }
    }
