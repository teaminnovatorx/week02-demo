"""Cases CRUD routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Case

router = APIRouter()


class CaseCreate(BaseModel):
    source: str = "telegram"
    patient_age_years: int | None = None
    patient_sex: str = "unknown"
    complaint: str = ""
    symptoms: list[str] = []
    duration: str = ""
    medications: list[str] = []
    specimen: str | None = None
    pathogen: str | None = None
    severity: str = "moderate"
    district: str = ""
    facility: str | None = None
    reported_by: str | None = None


@router.get("")
def list_cases(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=500),
    district: str | None = None,
    source: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    """List cases with pagination & filtering."""
    query = select(Case).order_by(Case.created_at.desc())
    if district:
        query = query.where(Case.district == district)
    if source:
        query = query.where(Case.source == source)
    if status:
        query = query.where(Case.status == status)

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar() or 0
    query = query.offset((page - 1) * per_page).limit(per_page)
    cases = db.execute(query).scalars().all()

    return {
        "cases": [c.to_dict() for c in cases],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, (total + per_page - 1) // per_page),
    }


@router.get("/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.execute(select(Case).where(Case.id == case_id)).scalar_one_or_none()
    if not case:
        raise HTTPException(404, "Case not found")
    return case.to_dict()


@router.post("")
def create_case(data: CaseCreate, db: Session = Depends(get_db)):
    case = Case(
        source=data.source,
        patient_age_years=data.patient_age_years,
        patient_sex=data.patient_sex,
        complaint=data.complaint,
        symptoms=",".join(data.symptoms),
        duration=data.duration,
        medications=",".join(data.medications),
        specimen=data.specimen,
        pathogen=data.pathogen,
        severity=data.severity,
        district=data.district,
        facility=data.facility,
        reported_by=data.reported_by,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case.to_dict()
