"""Database models for UDARA Week 02 Demo."""

import ast
import json
import re
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text

from .database import Base, generate_uuid, utcnow


def safe_json_loads(val: str | None) -> list:
    """Parse a JSON array, falling back to ast.literal_eval for Python repr."""
    if not val or val == "[]":
        return []
    val = val.strip()
    # Try real JSON first
    try:
        return json.loads(val)
    except (json.JSONDecodeError, ValueError):
        pass
    # Fallback: Python literal (e.g., "['Amoxicillin', 'Ciprofloxacin']")
    try:
        result = ast.literal_eval(val)
        if isinstance(result, (list, tuple)):
            return list(result)
    except (ValueError, SyntaxError, MemoryError):
        pass
    # Last resort: split by comma and strip brackets
    cleaned = val.strip("[]()")
    parts = [p.strip().strip("'\"") for p in cleaned.split(",") if p.strip()]
    return parts


class Case(Base):
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source = Column(String(20), default="telegram")
    language = Column(String(10), default="en")
    patient_age_years = Column(Integer, nullable=True)
    patient_sex = Column(String(10), default="unknown")
    complaint = Column(Text, default="")
    symptoms = Column(Text, default="")
    duration = Column(String(100), default="")
    medications = Column(Text, default="")
    specimen = Column(String(100), nullable=True)
    pathogen = Column(String(200), nullable=True)
    resistance_pattern = Column(String(200), nullable=True)
    drugs_prescribed = Column(Text, default="[]")
    severity = Column(String(20), default="moderate")
    status = Column(String(20), default="pending_review")
    district = Column(String(100), default="")
    facility = Column(String(200), nullable=True)
    reported_by = Column(String(100), nullable=True)
    resistance_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    def to_dict(self) -> dict:
        return {
            "case_id": self.id,
            "source": self.source,
            "language": self.language,
            "patient_age_years": self.patient_age_years,
            "patient_sex": self.patient_sex,
            "complaint": self.complaint,
            "symptoms": self.symptoms.split(",") if self.symptoms else [],
            "duration": self.duration,
            "medications": self.medications.split(",") if self.medications else [],
            "specimen": self.specimen,
            "pathogen": self.pathogen,
            "resistance_pattern": self.resistance_pattern,
            "drugs_prescribed": safe_json_loads(self.drugs_prescribed),
            "severity": self.severity,
            "status": self.status,
            "district": self.district,
            "facility": self.facility,
            "reported_by": self.reported_by,
            "resistance_flag": self.resistance_flag,
            "created_at": self.created_at.isoformat() if self.created_at else "",
            "updated_at": self.updated_at.isoformat() if self.updated_at else "",
        }


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    severity = Column(String(20), default="medium")
    title = Column(String(200), default="")
    message = Column(Text, default="")
    district = Column(String(100), nullable=True)
    drug = Column(String(100), nullable=True)
    resistance_pct = Column(Float, nullable=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "district": self.district,
            "drug": self.drug,
            "resistance_pct": self.resistance_pct,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else "",
        }


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(200), unique=True)
    name = Column(String(200), default="")
    password_hash = Column(String(200), default="")
    role = Column(String(50), default="admin")
    district = Column(String(100), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "district": self.district,
        }


class ResistanceData(Base):
    __tablename__ = "resistance_data"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    drug = Column(String(100))
    district = Column(String(100))
    resistance_pct = Column(Float)
    category = Column(String(20), default="susceptible")
    confidence = Column(Float, default=0.85)
    sample_size = Column(Integer, default=100)
    alternatives = Column(Text, default="[]")
    year = Column(Integer, default=2026)
    month = Column(Integer, default=1)

    def to_dict(self) -> dict:
        return {
            "drug": self.drug,
            "resistance_pct": self.resistance_pct,
            "category": self.category,
            "confidence": self.confidence,
            "alternatives": safe_json_loads(self.alternatives),
            "sample_size": self.sample_size,
        }
