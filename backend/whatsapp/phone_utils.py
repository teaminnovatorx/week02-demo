"""Phone number utilities for WhatsApp Cloud API integration.

Patterns lifted from a production WhatsApp CRM reference codebase:
  - E.164 sanitization and validation
  - Flexible phone matching (last 8 digits)
  - Variant generation for country-code / trunk-prefix retry
"""

import re


def sanitize_phone_for_meta(phone: str) -> str:
    """Strip everything non-digit for Meta's API.

    Meta requires digits only — no + prefix, no spaces, no dashes.
    Example: "+234 803 123 4567" → "2348031234567"
    """
    if not phone:
        return ""
    return re.sub(r"\D", "", phone)


def normalize_phone(phone: str) -> str:
    """Normalize to digits only for comparison."""
    if not phone:
        return ""
    return re.sub(r"\D", "", phone)


def phones_match(phone1: str, phone2: str) -> bool:
    """Compare two phone numbers flexibly using last 8 digits.

    Handles trunk prefix differences (e.g., "234063949836" with trunk 0
    matches "23463949836" without trunk 0).
    """
    n1 = normalize_phone(phone1)
    n2 = normalize_phone(phone2)
    if n1 == n2:
        return True
    if len(n1) >= 8 and len(n2) >= 8:
        return n1[-8:] == n2[-8:]
    return False


def is_valid_e164(phone: str) -> bool:
    """Check if phone is valid E.164 format (7-15 digits, no leading 0).

    Accepts with or without + prefix.
    """
    return bool(re.match(r"^\+?[1-9]\d{6,14}$", phone))


def phone_variants(sanitized: str) -> list[str]:
    """Generate plausible phone variants for sandbox retry.

    Meta's sandbox sometimes registers numbers with or without a domestic
    trunk prefix 0. This generates up to 3 deduplicated variants:

    1. The original sanitized number (first attempt)
    2. With trunk 0 inserted after the country code (if absent)
    3. With trunk 0 removed after the country code (if present)

    Args:
        sanitized: Digits-only phone number (from `sanitize_phone_for_meta`).

    Returns:
        Deduplicated list of variants, original first.
    """
    if not sanitized:
        return []

    seen: set[str] = set()
    variants: list[str] = []

    def push(v: str) -> None:
        if v and v not in seen:
            seen.add(v)
            variants.append(v)

    push(sanitized)

    for cc_len in (1, 2, 3):
        if len(sanitized) <= cc_len:
            continue
        cc = sanitized[:cc_len]
        rest = sanitized[cc_len:]
        # Insert 0 after CC
        if not rest.startswith("0"):
            push(cc + "0" + rest)
        # Remove 0 after CC
        if len(sanitized) > cc_len + 1 and rest.startswith("0"):
            push(cc + rest[1:])

    return variants


def is_recipient_not_allowed_error(message: str) -> bool:
    """Check if a Meta API error is the sandbox restriction.

    Meta error code 131030 or text "not in allowed list" indicates the
    recipient phone number isn't in the allowed list.
    """
    return bool(re.search(r"131030|not in allowed list|not in the allowed list", message, re.IGNORECASE))
