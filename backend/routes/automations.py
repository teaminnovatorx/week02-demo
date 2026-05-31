"""Simple automation engine for UDARA.

Pattern extracted from Ref_WACRM's automations/engine.ts:
- Trigger types: keyword_match, new_message_received
- Step types: send_message, set_severity, create_alert
- Execution with logging

Runs synchronously for simplicity in the Week 2 demo.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Case, Alert

logger = logging.getLogger("udara.automations")
router = APIRouter()

# ── Built-in automation rules ──
# In Ref_WACRM, these are stored in a DB table and evaluated dynamically.
# For the Week 2 demo, we define them in-code, matching the same pattern.

_AUTOMATION_RULES: list[dict[str, Any]] = [
    {
        "name": "Flag MDR cases",
        "trigger": "keyword_match",
        "keywords": ["mdr", "xdr", "multi-drug resistant", "pan-resistant"],
        "actions": [
            {"type": "set_severity", "value": "critical"},
            {"type": "create_alert", "severity": "critical",
             "title": "MDR Case Detected",
             "message": "Multi-drug resistant case reported via {source} — immediate review required."},
            {"type": "flag_resistance", "value": True},
        ],
    },
    {
        "name": "Flag treatment failure",
        "trigger": "keyword_match",
        "keywords": ["not responding", "treatment failure", "no improvement", "antibiotic failure"],
        "actions": [
            {"type": "set_status", "value": "requires_review"},
            {"type": "flag_resistance", "value": True},
            {"type": "create_alert", "severity": "high",
             "title": "Possible Treatment Failure",
             "message": "Case suggests possible treatment failure — review susceptibility data."},
        ],
    },
    {
        "name": "Escalate severe symptoms",
        "trigger": "keyword_match",
        "keywords": ["severe", "critical", "emergency", "unconscious", "bleeding", "icu", "intensive care"],
        "actions": [
            {"type": "set_severity", "value": "critical"},
            {"type": "set_status", "value": "urgent"},
            {"type": "create_alert", "severity": "critical",
             "title": "Critical Case Reported",
             "message": "Critical severity case reported from {source} — immediate attention needed."},
        ],
    },
    {
        "name": "Flag pediatric cases",
        "trigger": "keyword_match",
        "keywords": ["child", "infant", "neonatal", "pediatric", "baby", "newborn", "under 5"],
        "actions": [
            {"type": "set_status", "value": "pending_review"},
            {"type": "create_alert", "severity": "high",
             "title": "Pediatric Case Reported",
             "message": "Pediatric case requires careful antibiotic selection."},
        ],
    },
    {
        "name": "Flag specific pathogens",
        "trigger": "keyword_match",
        "keywords": ["tb", "tuberculosis", "malaria", "typhoid", "cholera", "dengue", " meningitis"],
        "actions": [
            {"type": "create_alert", "severity": "high",
             "title": "Notifiable Disease Reported",
             "message": "Case may involve a notifiable disease — verify and report to health authorities."},
        ],
    },
    {
        "name": "New case — welcome message",
        "trigger": "new_message_received",
        "keywords": [],
        "actions": [
            {"type": "set_status", "value": "pending_review"},
        ],
    },
]


def evaluate_automations(text: str, case: Case, db: Session) -> list[dict[str, Any]]:
    """Evaluate automation rules against a case's text content.

    Args:
        text: The inbound message text.
        case: The newly created Case object.
        db: Database session.

    Returns:
        List of action results for logging.
    """
    results: list[dict[str, Any]] = []
    text_lower = text.lower()

    for rule in _AUTOMATION_RULES:
        if rule["trigger"] == "keyword_match":
            keywords = rule.get("keywords", [])
            if not any(kw in text_lower for kw in keywords):
                continue
        elif rule["trigger"] == "new_message_received":
            # Always applies, but only if this is the first message
            # (in a real app we'd check a per-conversation flag)
            pass

        # Execute actions
        for action in rule["actions"]:
            try:
                result = _execute_action(action, case, db)
                if result:
                    results.append({
                        "rule": rule["name"],
                        "action": action["type"],
                        "result": result,
                    })
            except Exception as e:
                logger.warning("Automation action failed: %s — %s", action["type"], e)
                results.append({
                    "rule": rule["name"],
                    "action": action["type"],
                    "result": f"error: {e}",
                })

    return results


def _execute_action(action: dict[str, Any], case: Case, db: Session) -> str:
    """Execute a single automation action."""
    action_type = action.get("type", "")

    if action_type == "set_severity":
        severity_order = {"low": 0, "moderate": 1, "high": 2, "critical": 3}
        new_val = action["value"]
        if severity_order.get(new_val, 0) > severity_order.get(case.severity, 0):
            case.severity = new_val
            db.flush()
            return f"severity upgraded to {new_val}"
        return f"severity unchanged ({case.severity})"

    elif action_type == "set_status":
        case.status = action["value"]
        db.flush()
        return f"status set to {action['value']}"

    elif action_type == "flag_resistance":
        case.resistance_flag = True
        db.flush()
        return "resistance flagged"

    elif action_type == "create_alert":
        message = action["message"].format(
            source=case.source,
            severity=action.get("severity", "medium"),
        )
        alert = Alert(
            severity=action.get("severity", "medium"),
            title=action["title"],
            message=message,
            district=case.district,
            status="active",
        )
        db.add(alert)
        db.flush()
        return f"alert created: {action['title']}"

    return f"unknown action: {action_type}"


# ── API route to list automation rules ──


@router.get("/rules")
def list_rules():
    """List configured automation rules."""
    return {
        "rules": [
            {
                "name": r["name"],
                "trigger": r["trigger"],
                "keywords": r.get("keywords", []),
                "actions_count": len(r.get("actions", [])),
            }
            for r in _AUTOMATION_RULES
        ],
        "total": len(_AUTOMATION_RULES),
    }


@router.get("/log")
def list_automation_log(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List recent cases with automation results."""
    cases = (
        db.execute(
            select(Case)
            .order_by(Case.created_at.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )
    return {
        "cases": [
            {
                "id": c.id,
                "source": c.source,
                "severity": c.severity,
                "status": c.status,
                "resistance_flag": c.resistance_flag,
                "complaint": (c.complaint or "")[:100],
                "created_at": c.created_at.isoformat() if c.created_at else "",
            }
            for c in cases
        ],
    }
