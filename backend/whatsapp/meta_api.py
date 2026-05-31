"""Meta WhatsApp Cloud API v21.0 client.

Every function takes named parameters (single args object) to prevent
the swapped-args bugs that plagued positional forms. The pattern is
lifted from a production WhatsApp CRM reference codebase.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger("udara.whatsapp")

META_API_VERSION = "v21.0"
META_API_BASE = f"https://graph.facebook.com/{META_API_VERSION}"

# Default timeout: 15s for normal sends, 60s for media downloads
_DEFAULT_TIMEOUT = 15.0
_MEDIA_TIMEOUT = 60.0


# ── Shared types ──


@dataclass
class MetaSendResult:
    """Result from a Meta message send call."""
    message_id: str


@dataclass
class MediaInfo:
    url: str
    mime_type: str


@dataclass
class PhoneInfo:
    id: str
    display_phone_number: str
    verified_name: str | None = None
    quality_rating: str | None = None


# ── Internal helpers ──


async def _meta_post(
    path: str,
    access_token: str,
    body: dict[str, Any],
    timeout: float = _DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """POST to Meta Graph API and return parsed JSON."""
    url = f"{META_API_BASE}/{path.lstrip('/')}"
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            url,
            json=body,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if not resp.is_success:
        error_body = ""
        try:
            error_body = resp.text[:500]
        except Exception:
            pass
        raise RuntimeError(f"Meta API error {resp.status_code}: {error_body}")
    return resp.json()


async def _meta_get(
    path: str,
    access_token: str,
    params: dict[str, str] | None = None,
    timeout: float = _DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """GET from Meta Graph API."""
    url = f"{META_API_BASE}/{path.lstrip('/')}"
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(
            url,
            params=params or {},
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if not resp.is_success:
        error_body = ""
        try:
            error_body = resp.text[:500]
        except Exception:
            pass
        raise RuntimeError(f"Meta API error {resp.status_code}: {error_body}")
    return resp.json()


# ── Sending ──


async def send_text_message(
    phone_number_id: str,
    access_token: str,
    to: str,
    text: str,
    context_message_id: str | None = None,
) -> MetaSendResult:
    """Send a free-form WhatsApp text message.

    Only works within the 24-hour customer service window.
    """
    body: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    if context_message_id:
        body["context"] = {"message_id": context_message_id}

    data = await _meta_post(f"{phone_number_id}/messages", access_token, body)
    return MetaSendResult(message_id=data["messages"][0]["id"])


async def send_template_message(
    phone_number_id: str,
    access_token: str,
    to: str,
    template_name: str,
    language: str = "en_US",
    params: list[str] | None = None,
    header_params: list[str] | None = None,
    context_message_id: str | None = None,
) -> MetaSendResult:
    """Send a pre-approved WhatsApp message template.

    Required outside the 24-hour window and for first-touch messaging.
    """
    components: list[dict[str, Any]] = []

    # Header (optional — text header only)
    if header_params and len(header_params) > 0:
        components.append({
            "type": "header",
            "parameters": [{"type": "text", "text": p} for p in header_params],
        })

    # Body
    if params and len(params) > 0:
        components.append({
            "type": "body",
            "parameters": [{"type": "text", "text": str(p)} for p in params],
        })

    template_payload: dict[str, Any] = {
        "name": template_name,
        "language": {"code": language},
    }
    if components:
        template_payload["components"] = components

    body: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": template_payload,
    }
    if context_message_id:
        body["context"] = {"message_id": context_message_id}

    data = await _meta_post(f"{phone_number_id}/messages", access_token, body)
    return MetaSendResult(message_id=data["messages"][0]["id"])


# ── Interactive message limits ──

INTERACTIVE_LIMITS = {
    "max_buttons": 3,
    "button_title_max_length": 20,
    "max_list_sections": 10,
    "max_list_rows_total": 10,
    "list_row_title_max_length": 24,
    "list_row_description_max_length": 72,
    "body_max_length": 1024,
    "footer_max_length": 60,
    "header_text_max_length": 60,
}


async def send_interactive_buttons(
    phone_number_id: str,
    access_token: str,
    to: str,
    body_text: str,
    buttons: list[dict[str, str]],
    header_text: str | None = None,
    footer_text: str | None = None,
    context_message_id: str | None = None,
) -> MetaSendResult:
    """Send interactive message with up to 3 reply buttons.

    Each button: { "id": "btn_1", "title": "Yes" }
    """
    if len(buttons) < 1 or len(buttons) > INTERACTIVE_LIMITS["max_buttons"]:
        raise ValueError(f"Need 1-{INTERACTIVE_LIMITS['max_buttons']} buttons")

    interactive: dict[str, Any] = {
        "type": "button",
        "body": {"text": body_text},
        "action": {
            "buttons": [
                {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}}
                for b in buttons
            ]
        },
    }
    if header_text:
        interactive["header"] = {"type": "text", "text": header_text}
    if footer_text:
        interactive["footer"] = {"text": footer_text}

    body: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": interactive,
    }
    if context_message_id:
        body["context"] = {"message_id": context_message_id}

    data = await _meta_post(f"{phone_number_id}/messages", access_token, body)
    return MetaSendResult(message_id=data["messages"][0]["id"])


async def send_interactive_list(
    phone_number_id: str,
    access_token: str,
    to: str,
    body_text: str,
    button_label: str,
    sections: list[dict[str, Any]],
    header_text: str | None = None,
    footer_text: str | None = None,
    context_message_id: str | None = None,
) -> MetaSendResult:
    """Send interactive list message with selectable rows.

    Sections: [{ "title": "Section", "rows": [{ "id": "opt_1", "title": "Option 1", "description": "..." }] }]
    """
    interactive: dict[str, Any] = {
        "type": "list",
        "body": {"text": body_text},
        "action": {
            "button": button_label,
            "sections": [
                {
                    "title": s.get("title", ""),
                    "rows": [
                        {
                            "id": r["id"],
                            "title": r["title"],
                            **({"description": r.get("description")} if r.get("description") else {}),
                        }
                        for r in s["rows"]
                    ],
                }
                for s in sections
            ],
        },
    }
    if header_text:
        interactive["header"] = {"type": "text", "text": header_text}
    if footer_text:
        interactive["footer"] = {"text": footer_text}

    body: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": interactive,
    }
    if context_message_id:
        body["context"] = {"message_id": context_message_id}

    data = await _meta_post(f"{phone_number_id}/messages", access_token, body)
    return MetaSendResult(message_id=data["messages"][0]["id"])


async def send_media_message(
    phone_number_id: str,
    access_token: str,
    to: str,
    kind: str,
    link: str,
    caption: str | None = None,
    filename: str | None = None,
    context_message_id: str | None = None,
) -> MetaSendResult:
    """Send image / video / document via public URL."""
    if kind not in ("image", "video", "document"):
        raise ValueError(f"Unsupported media kind: {kind}")

    media: dict[str, Any] = {"link": link}
    if caption:
        media["caption"] = caption
    if kind == "document" and filename:
        media["filename"] = filename

    body: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": kind,
        kind: media,
    }
    if context_message_id:
        body["context"] = {"message_id": context_message_id}

    data = await _meta_post(f"{phone_number_id}/messages", access_token, body)
    return MetaSendResult(message_id=data["messages"][0]["id"])


async def send_reaction_message(
    phone_number_id: str,
    access_token: str,
    to: str,
    target_message_id: str,
    emoji: str,
) -> MetaSendResult:
    """Send reaction (or removal) to a previous message."""
    body: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "reaction",
        "reaction": {"message_id": target_message_id, "emoji": emoji},
    }
    data = await _meta_post(f"{phone_number_id}/messages", access_token, body)
    return MetaSendResult(message_id=data["messages"][0]["id"])


# ── Media ──


async def get_media_url(media_id: str, access_token: str) -> MediaInfo:
    """Resolve a media ID to Meta's CDN URL + MIME type."""
    data = await _meta_get(media_id, access_token)
    if "url" not in data:
        raise RuntimeError("Media URL not found in Meta response")
    return MediaInfo(
        url=data["url"],
        mime_type=data.get("mime_type", "application/octet-stream"),
    )


async def download_media(download_url: str, access_token: str) -> tuple[bytes, str]:
    """Fetch binary bytes from a Meta media URL."""
    async with httpx.AsyncClient(timeout=_MEDIA_TIMEOUT) as client:
        resp = await client.get(
            download_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if not resp.is_success:
        raise RuntimeError(f"Media download failed: {resp.status_code}")
    content_type = resp.headers.get("content-type", "application/octet-stream")
    return resp.content, content_type


# ── Account / Registration ──


async def verify_phone_number(phone_number_id: str, access_token: str) -> PhoneInfo:
    """Fetch metadata for a Meta phone number ID."""
    data = await _meta_get(
        phone_number_id,
        access_token,
        params={"fields": "id,display_phone_number,verified_name,quality_rating"},
    )
    return PhoneInfo(
        id=data["id"],
        display_phone_number=data.get("display_phone_number", ""),
        verified_name=data.get("verified_name"),
        quality_rating=data.get("quality_rating"),
    )


async def register_phone_number(
    phone_number_id: str,
    access_token: str,
    pin: str,
) -> bool:
    """Register a phone number for inbound webhook events.

    Returns True on success (or if already registered).
    """
    try:
        await _meta_post(
            f"{phone_number_id}/register",
            access_token,
            {"messaging_product": "whatsapp", "pin": pin},
        )
        return True
    except RuntimeError as e:
        msg = str(e)
        if "already registered" in msg.lower():
            return True
        raise


async def submit_message_template(
    waba_id: str,
    access_token: str,
    name: str,
    category: str,
    components: list[dict[str, Any]],
    language: str = "en_US",
) -> str:
    """Submit a message template to Meta for approval.

    Returns Meta's assigned template id.
    """
    payload = {
        "name": name,
        "language": language,
        "category": category,
        "components": components,
    }
    data = await _meta_post(
        f"{waba_id}/message_templates",
        access_token,
        payload,
    )
    return str(data.get("id", ""))
