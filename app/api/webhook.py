"""
Webhook endpoint — receives post-call events from Retell AI.

Handles three event types:
- call_started: Logs call initiation
- call_ended: Logs call metadata
- call_analyzed: Logs call analysis (summary, sentiment)
"""

import json
from fastapi import APIRouter, Request, HTTPException
from app.models.webhook_event import WebhookEvent
from app.services.sheets_service import sheets_service
from app.middleware.signature import verify_retell_signature
from app.utils.logger import logger
from datetime import datetime, timezone

router = APIRouter()

# Track processed call IDs for idempotency
_processed_calls: set[str] = set()


@router.post("/webhook")
async def handle_webhook(request: Request):
    """
    Receive and process Retell AI webhook events.

    Events:
    - call_started: Log call start
    - call_ended: Write call metadata to Call Logs sheet
    - call_analyzed: Update call log with post-call analysis

    Returns:
        {"status": "success"} on successful processing.
    """
    # Verify signature
    raw_body = await verify_retell_signature(request)

    # Parse payload
    try:
        payload = json.loads(raw_body)
        event = WebhookEvent(**payload)
    except Exception as e:
        logger.error(f"ERROR - Failed to parse webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")

    call = event.call
    logger.info(f"INFO - Webhook received: event={event.event}, call_id={call.call_id}")

    # --- call_started ---
    if event.event == "call_started":
        logger.info(
            f"INFO - Call started: {call.call_id} | "
            f"from={call.from_number} | direction={call.direction}"
        )
        return {"status": "success"}

    # --- call_ended ---
    if event.event == "call_ended":
        # Idempotency check
        # TODO: Add Redis-based distributed lock for idempotency in production to support horizontal scaling.
        idempotency_key = f"{call.call_id}_ended"
        if idempotency_key in _processed_calls:
            logger.warning(f"WARNING - Duplicate call_ended event for {call.call_id}, skipping")
            return {"status": "success"}

        _processed_calls.add(idempotency_key)

        # Determine call outcome from dynamic variables
        variables = call.retell_llm_dynamic_variables
        outcome = "unknown"
        if variables.get("booking_id"):
            outcome = "appointment_booked"
        elif variables.get("faq_answer"):
            outcome = "faq_answered"
        else:
            outcome = "general_inquiry"

        # Format timestamps
        start_time = ""
        end_time = ""
        if call.start_timestamp:
            start_time = datetime.fromtimestamp(
                call.start_timestamp / 1000, tz=timezone.utc
            ).isoformat()
        if call.end_timestamp:
            end_time = datetime.fromtimestamp(
                call.end_timestamp / 1000, tz=timezone.utc
            ).isoformat()

        # Write to Call Logs sheet
        row_data = [
            call.call_id,
            call.direction,
            call.from_number,
            start_time,
            end_time,
            call.duration_seconds,
            outcome,
            "",  # sentiment — filled by call_analyzed
            "",  # summary — filled by call_analyzed
            "No",  # transferred
        ]

        sheets_service.log_call(row_data)
        logger.info(f"INFO - Call ended and logged: {call.call_id} | outcome={outcome}")
        return {"status": "success"}

    # --- call_analyzed ---
    if event.event == "call_analyzed":
        # Idempotency check
        idempotency_key = f"{call.call_id}_analyzed"
        if idempotency_key in _processed_calls:
            logger.warning(f"WARNING - Duplicate call_analyzed event for {call.call_id}, skipping")
            return {"status": "success"}

        _processed_calls.add(idempotency_key)

        # Extract analysis data
        analysis = call.call_analysis
        if analysis:
            updates = {
                "Sentiment": analysis.user_sentiment,
                "Summary": analysis.call_summary,
            }
            sheets_service.update_call_log(call.call_id, updates)
            logger.info(
                f"INFO - Call analyzed: {call.call_id} | "
                f"sentiment={analysis.user_sentiment}"
            )
        else:
            logger.warning(f"WARNING - call_analyzed event for {call.call_id} had no analysis data")

        return {"status": "success"}

    # Unknown event type
    logger.warning(f"WARNING - Unknown webhook event: {event.event}")
    return {"status": "success"}
