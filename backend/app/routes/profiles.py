from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import ProfilePatch
from app.security import (
    csrf_guard,
    current_user,
    get_db,
    private_profile,
    public_organization,
)

router = APIRouter(tags=["profiles"])


@router.get("/profile")
def profile(user: User = Depends(current_user)):
    return private_profile(user)


@router.patch("/profile", dependencies=[Depends(csrf_guard)])
def update_profile(
    data: ProfilePatch, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    updates = data.model_dump(exclude_unset=True)
    if user.role == "ORGANIZER" and "organization_name" in updates and not data.organization_name:
        raise HTTPException(422, "Укажите название организации")
    if user.role == "VOLUNTEER":
        updates.pop("organization_name", None)
    for key, value in updates.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return private_profile(user)


@router.get("/organizations")
def organizations(
    search: str = Query("", max_length=160),
    city: str = Query("", max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
):
    statement = select(User).where(User.role == "ORGANIZER")
    if search.strip():
        statement = statement.where(
            User.organization_name.icontains(search.strip(), autoescape=True)
        )
    if city.strip():
        statement = statement.where(func.lower(User.city) == city.strip().lower())
    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    rows = db.scalars(
        statement.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    return {
        "items": [public_organization(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/organizations/{organization_id}")
def organization(organization_id: int, db: Session = Depends(get_db)):
    user = db.get(User, organization_id)
    if not user or user.role != "ORGANIZER":
        raise HTTPException(404, "Организация не найдена")
    return public_organization(user)
