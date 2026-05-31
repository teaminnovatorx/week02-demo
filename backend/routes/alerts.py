"""Alert routes — list, acknowledge, resolve."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Alert

router = APIRouter()


class AlertUpdate(BaseModel):
    notes: str | None = None


@router.get("")
def list_alerts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    severity: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(Alert).order_by(Alert.created_at.desc())
    if severity:
        query = query.where(Alert.severity == severity)
    if status:
        query = query.where(Alert.status == status)

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar() or 0
    query = query.offset((page - 1) * per_page).limit(per_page)
    alerts = db.execute(query).scalars().all()

    return {
        "alerts": [a.to_dict() for a in alerts],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, (total + per_page - 1) // per_page),
    }


@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.execute(select(Alert).where(Alert.id == alert_id)).scalar_one_or_none()
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.status = "acknowledged"
    db.commit()
    return {"status": "acknowledged", "alert": alert.to_dict()}


@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: str, data: AlertUpdate = AlertUpdate(), db: Session = Depends(get_db)):
    alert = db.execute(select(Alert).where(Alert.id == alert_id)).scalar_one_or_none()
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.status = "resolved"
    if data.notes:
        alert.message += f"\n\nResolved: {data.notes}"
    db.commit()
    return {"status": "resolved", "alert": alert.to_dict()}
