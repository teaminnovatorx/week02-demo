"""Auth routes — zero-friction demo login."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from jose import jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User

router = APIRouter()
SECRET = "udara-week02-demo-secret"


class LoginReq(BaseModel):
    email: str
    password: str = "demo"


class RegisterReq(BaseModel):
    email: str
    password: str
    name: str = ""


@router.post("/login")
def login(req: LoginReq, db: Session = Depends(get_db)):
    """Login with any email — auto-creates user on first access."""
    user = db.execute(select(User).where(User.email == req.email)).scalar_one_or_none()
    if not user:
        user = User(
            email=req.email,
            name=req.email.split("@")[0].title(),
            password_hash="demo",
            role="admin",
            district="Lagos",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = jwt.encode(
        {"sub": user.id, "email": user.email, "role": user.role,
         "exp": datetime.now(timezone.utc) + timedelta(days=7)},
        SECRET, algorithm="HS256",
    )
    return {"user": user.to_dict(), "access_token": token, "token_type": "bearer"}


@router.post("/register")
def register(req: RegisterReq, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = db.execute(select(User).where(User.email == req.email)).scalar_one_or_none()
    if existing:
        from fastapi import HTTPException
        raise HTTPException(400, "Email already registered")

    user = User(
        email=req.email,
        name=req.name or req.email.split("@")[0].title(),
        password_hash="demo",
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = jwt.encode(
        {"sub": user.id, "email": user.email, "role": user.role,
         "exp": datetime.now(timezone.utc) + timedelta(days=7)},
        SECRET, algorithm="HS256",
    )
    return {"user": user.to_dict(), "access_token": token, "token_type": "bearer"}


@router.post("/logout")
def logout():
    return {"message": "Logged out"}
