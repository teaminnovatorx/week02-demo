"""WhatsApp Cloud API integration for UDARA."""

from .meta_api import (
    MetaSendResult,
    send_text_message,
    send_template_message,
    send_interactive_buttons,
    send_interactive_list,
    send_media_message,
    send_reaction_message,
    get_media_url,
    download_media,
    verify_phone_number,
    register_phone_number,
    submit_message_template,
    INTERACTIVE_LIMITS,
)
from .signature import verify_meta_webhook_signature
from .phone_utils import (
    sanitize_phone_for_meta,
    normalize_phone,
    phones_match,
    is_valid_e164,
    phone_variants,
    is_recipient_not_allowed_error,
)

__all__ = [
    "MetaSendResult",
    "send_text_message",
    "send_template_message",
    "send_interactive_buttons",
    "send_interactive_list",
    "send_media_message",
    "send_reaction_message",
    "get_media_url",
    "download_media",
    "verify_phone_number",
    "register_phone_number",
    "submit_message_template",
    "INTERACTIVE_LIMITS",
    "verify_meta_webhook_signature",
    "sanitize_phone_for_meta",
    "normalize_phone",
    "phones_match",
    "is_valid_e164",
    "phone_variants",
    "is_recipient_not_allowed_error",
]
