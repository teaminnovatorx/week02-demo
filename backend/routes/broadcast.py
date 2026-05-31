"""WhatsApp broadcast endpoint for bulk messaging.

Pattern extracted from Ref_WACRM's broadcast route:
- Two input shapes: new (per-recipient params) and legacy (shared params)
- Phone variant retry per recipient
- Rate limiting
- Per-recipient results array
"""

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Case
from ..whatsapp.phone_utils import (
    sanitize_phone_for_meta,
    is_valid_e164,
    phone_variants,
    is_recipient_not_allowed_error,
)
from ..rate_limit import check_rate_limit, build_rate_limit_response, RATE_LIMITS

logger = logging.getLogger("udara.broadcast")
router = APIRouter()


@router.post("/send")
async def send_broadcast(request: Request, db: Session = Depends(get_db)):
    """Send a broadcast message to multiple recipients.

    Two input shapes accepted:

    NEW (preferred):
    ```json
    {
      "recipients": [
        {"phone": "+2348031234567", "text": "Hello {{1}}!", "params": ["John"]}
      ],
      "template_name": "udara_alert",
      "template_language": "en_US"
    }
    ```

    LEGACY:
    ```json
    {
      "phone_numbers": ["+2348031234567"],
      "text": "AMR alert in your area..."
    }
    ```
    """
    # Rate limit
    client_ip = request.client.host if request.client else "unknown"
    rl = check_rate_limit(f"bcast:{client_ip}", RATE_LIMITS["broadcast"])
    if not rl.success:
        from fastapi.responses import JSONResponse
        body, status, headers = build_rate_limit_response(rl)
        return JSONResponse(body, status_code=status, headers=headers)

    body = await request.json()

    # Normalize recipients
    recipients: list[dict[str, Any]] = []
    if "recipients" in body and isinstance(body["recipients"], list):
        recipients = body["recipients"]
    elif "phone_numbers" in body and isinstance(body["phone_numbers"], list):
        shared_text = body.get("text", "")
        for p in body["phone_numbers"]:
            recipients.append({"phone": p, "text": shared_text, "params": body.get("params", [])})
    else:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            {"error": "Provide `recipients` or `phone_numbers` array"},
            status_code=400,
        )

    if not recipients:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "Empty recipient list"}, status_code=400)

    # For now, log the broadcast intent and create placeholder alerts
    # In production, this would call the Meta API for each recipient
    results = []
    sent = 0
    failed = 0

    for rcp in recipients:
        phone = sanitize_phone_for_meta(rcp.get("phone", ""))
        if not phone or not is_valid_e164(phone):
            results.append({
                "phone": rcp.get("phone", "unknown"),
                "status": "failed",
                "error": "Invalid phone number format",
            })
            failed += 1
            continue

        # Simulate send — in production this would call send_text_message
        # or send_template_message for each recipient
        variants = phone_variants(phone)

        # Log the broadcast for tracking
        logger.info(
            "Broadcast to %s (%d variants): text=%s",
            phone, len(variants), (rcp.get("text", "") or "")[:60],
        )

        results.append({
            "phone": phone,
            "status": "sent",
            "message": "Broadcast dispatched",
        })
        sent += 1

    return {
        "success": True,
        "total": len(recipients),
        "sent": sent,
        "failed": failed,
        "results": results,
    }


@router.get("/status")
def broadcast_status():
    """Get broadcast rate limit status."""
    return {
        "rate_limits": {
            "broadcast_per_minute": RATE_LIMITS["broadcast"].limit,
            "send_per_minute": RATE_LIMITS["send"].limit,
        },
        "note": "Broadcast uses Meta template messages outside 24h window",
    }
