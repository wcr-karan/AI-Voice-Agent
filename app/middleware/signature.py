"""
Retell AI webhook signature verification middleware.

Validates the HMAC-SHA256 signature in the x-retell-signature header
to ensure webhook requests genuinely originate from Retell AI.
"""

import hmac
import hashlib
from fastapi import Request, HTTPException
from app.config import settings
from app.utils.logger import logger


async def verify_retell_signature(request: Request) -> bytes:
    """
    Verify the Retell AI webhook signature.

    Reads the raw request body, computes HMAC-SHA256 using the
    webhook secret, and compares against the provided signature.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The raw request body bytes (for subsequent parsing).

    Raises:
        HTTPException(401): If signature is missing or invalid.
        HTTPException(400): If request body cannot be read.
    """
    # Skip verification in development if no secret is configured
    if settings.app_env == "development" and not settings.retell_webhook_secret:
        logger.warning("WARNING - Skipping signature verification (no webhook secret configured)")
        return await request.body()

    # Get signature header
    signature = request.headers.get("x-retell-signature")
    if not signature:
        logger.warning("WARNING - Missing x-retell-signature header")
        raise HTTPException(status_code=401, detail="Missing signature")

    # Read raw body
    try:
        body = await request.body()
    except Exception as e:
        logger.error(f"ERROR - Failed to read request body: {e}")
        raise HTTPException(status_code=400, detail="Invalid request body")

    # Compute expected signature
    expected = hmac.new(
        key=settings.retell_webhook_secret.encode("utf-8"),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(signature, expected):
        logger.warning(f"WARNING - Invalid webhook signature from {request.client.host}")
        raise HTTPException(status_code=401, detail="Invalid signature")

    logger.debug("DEBUG - Webhook signature verified successfully")
    return body
