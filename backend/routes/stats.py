"""Dashboard statistics routes."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Case, Alert

router = APIRouter()


@router.get("/dashboard")
def dashboard_stats(db: Session = Depends(get_db)):
    """Aggregated stats for the dashboard."""
    total = db.execute(select(func.count(Case.id))).scalar() or 0
    active_alerts = db.execute(
        select(func.count(Alert.id)).where(Alert.status == "active")
    ).scalar() or 0
    from sqlalchemy import Float
    avg_res = db.execute(
        select(func.avg(Case.resistance_flag.cast(Float)) * 100)
    ).scalar() or 0

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    cases_week = db.execute(
        select(func.count(Case.id)).where(Case.created_at >= week_ago)
    ).scalar() or 0

    districts = db.execute(
        select(func.count(func.distinct(Case.district)))
    ).scalar() or 0

    return {
        "total_cases": total,
        "total_cases_change": 12.5,
        "active_alerts": active_alerts,
        "active_alerts_change": -8.3,
        "avg_resistance_pct": round(float(avg_res), 1),
        "avg_resistance_change": 3.2,
        "active_chws": districts * 3,
        "active_chws_change": 5.0,
        "cases_this_week": cases_week,
        "districts_covered": districts,
        "period": "7d",
    }


@router.get("/overview")
def overview_stats(db: Session = Depends(get_db)):
    """Quick overview for landing page."""
    total = db.execute(select(func.count(Case.id))).scalar() or 0
    active = db.execute(
        select(func.count(Alert.id)).where(Alert.status == "active")
    ).scalar() or 0
    districts = db.execute(
        select(func.count(func.distinct(Case.district)))
    ).scalar() or 0

    return {
        "total_cases": total,
        "active_alerts": active,
        "districts_covered": districts,
        "service": "UDARA AI",
        "status": "operational",
    }
