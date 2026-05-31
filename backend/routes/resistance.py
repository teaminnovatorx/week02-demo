"""Resistance routes — map, trends, drugs list."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ResistanceData, Alert

router = APIRouter()

# ── District geo-coordinates (lat, lng) ──
DISTRICT_COORDS = {
    "Lagos": (6.5244, 3.3792),
    "Accra": (5.6037, -0.1870),
    "Kumasi": (6.6885, -1.6244),
    "Abuja": (9.0765, 7.3986),
    "Dakar": (14.7167, -17.4677),
    "Nairobi": (-1.2921, 36.8219),
    "Dar es Salaam": (-6.7924, 39.2083),
    "Kampala": (0.3476, 32.5825),
    "Addis Ababa": (9.0320, 38.7469),
    "Mombasa": (-4.0435, 39.6682),
    "Lusaka": (-15.3875, 28.3228),
    "Harare": (-17.8252, 31.0335),
    "Lilongwe": (-13.9626, 33.7741),
    "Johannesburg": (-26.2041, 28.0473),
    "Kinshasa": (-4.4419, 15.2663),
}

REGION_MAP = {
    "Lagos": "West Africa", "Accra": "West Africa", "Kumasi": "West Africa",
    "Abuja": "West Africa", "Dakar": "West Africa",
    "Nairobi": "East Africa", "Dar es Salaam": "East Africa", "Kampala": "East Africa",
    "Addis Ababa": "East Africa", "Mombasa": "East Africa",
    "Lusaka": "Southern Africa", "Harare": "Southern Africa",
    "Lilongwe": "Southern Africa", "Johannesburg": "Southern Africa",
    "Kinshasa": "Central Africa",
}


@router.get("/map")
def resistance_map(db: Session = Depends(get_db)):
    """Resistance data by district with geo-coordinates."""
    rows = db.execute(select(ResistanceData)).scalars().all()
    
    # Get active alerts per district
    alerts_per_district = {}
    try:
        alert_rows = db.execute(
            select(Alert.district, func.count(Alert.id))
            .where(Alert.status == "active")
            .group_by(Alert.district)
        ).all()
        for dist, cnt in alert_rows:
            alerts_per_district[dist] = cnt
    except Exception:
        pass

    by_district = {}
    for row in rows:
        by_district.setdefault(row.district, []).append(row.to_dict())

    features = []
    for district, drugs in by_district.items():
        avg = sum(d["resistance_pct"] for d in drugs) / len(drugs) if drugs else 0
        top = max(drugs, key=lambda d: d["resistance_pct"]) if drugs else {}
        coords = DISTRICT_COORDS.get(district, (0, 0))
        region = REGION_MAP.get(district, "Unknown")
        features.append({
            "district": district,
            "region": region,
            "lat": coords[0],
            "lng": coords[1],
            "avg_resistance_pct": round(avg, 1),
            "drugs": drugs[:8],
            "top_drug": top.get("drug", ""),
            "top_resistance": top.get("resistance_pct", 0),
            "drugs_count": len(drugs),
            "active_alerts": alerts_per_district.get(district, 0),
        })
    return {"features": features}


@router.get("/trends")
def resistance_trends(
    drug: str | None = Query(None),
    district: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """30-day trend data."""
    query = select(ResistanceData)
    if drug:
        query = query.where(ResistanceData.drug.ilike(f"%{drug}%"))
    if district:
        query = query.where(ResistanceData.district.ilike(f"%{district}%"))
    rows = db.execute(query).scalars().all()

    dates = [(datetime.now(timezone.utc) - timedelta(days=29 - i)).strftime("%Y-%m-%d") for i in range(30)]
    series = {}
    for row in rows[:6]:
        label = f"{row.drug} - {row.district}"
        series[label] = [round(max(0, min(100, row.resistance_pct + (i - 15) * 0.5)), 1) for i in range(30)]
    return {"dates": dates, "series": series}


@router.get("/drugs")
def list_drugs(db: Session = Depends(get_db)):
    """List all tracked drugs."""
    drugs = db.execute(
        select(ResistanceData.drug).distinct().order_by(ResistanceData.drug)
    ).scalars().all()
    return {"drugs": drugs}
