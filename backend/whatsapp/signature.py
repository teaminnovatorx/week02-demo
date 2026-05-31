"""HMAC-SHA256 webhook signature verification for Meta Cloud API.

Meta signs every webhook POST with your App Secret and sends the
result in the `x-hub-signature-256: sha256=<hex>` header. Without
verification, anyone who knows the webhook URL can POST fabricated
events.

Reference:
  https://developers.facebook.com/docs/graph-api/webhooks/getting-started
"""

import hashlib
import hmac
import logging

logger = logging.getLogger("udara.whatsapp.signature")

# Cache the secret after first read so we fail fast on missing config
_SECRET: str | None = None


def _get_secret() -> str | None:
    """Lazy-load META_APP_SECRET from environment."""
    global _SECRET
    if _SECRET is None:
        import os
        _SECRET = os.environ.get("META_APP_SECRET")
    return _SECRET


def verify_meta_webhook_signature(
    raw_body: str,
    signature_header: str | None,
) -> bool:
    """Verify the HMAC-SHA256 signature on a Meta webhook POST.

    Args:
        raw_body: The raw request body as a string (must be the exact
            bytes Meta sent — re-encoding from parsed JSON will break
            the signature).
        signature_header: The value of the `x-hub-signature-256` header.

    Returns:
        True if the signature is valid, False otherwise.
    """
    secret = _get_secret()
    if not secret:
        logger.error(
            "META_APP_SECRET is not set — rejecting all webhooks. "
            "Set this env var to your Meta App Secret."
        )
        return False

    if not signature_header:
        logger.warning("Webhook missing signature header")
        return False

    if not signature_header.startswith("sha256="):
        logger.warning("Webhook signature header doesn't start with sha256=")
        return False

    expected = (
        "sha256="
        + hmac.new(secret.encode(), raw_body.encode(), hashlib.sha256).hexdigest()
    )

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(signature_header, expected)
