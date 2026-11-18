from datetime import UTC, date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Project, User
from app.schemas import Category, ProjectInput, Status, StatusInput
from app.security import claims, csrf_guard, get_db, organizer
from app.services import change_status, ensure_editable

router = APIRouter(tags=["projects"])


def serialize(project: Project):
    result = {column.name: getattr(project, column.name) for column in Project.__table__.columns}
    if result["starts_at"].tzinfo is None:  # SQLite-only local test adapter
        result["starts_at"] = result["starts_at"].replace(tzinfo=UTC)
    return result


def paginate(statement, db, page, page_size):
    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    rows = db.scalars(
        statement.order_by(Project.id.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    return {
        "items": [serialize(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def owned(project_id, user, db):
    project = db.scalar(select(Project).where(Project.id == project_id).with_for_update())
    if not project or project.owner_id != user.id:
        raise HTTPException(404, "Проект не найден")
    return project


@router.get("/projects")
def projects(
    search: str = Query("", max_length=160),
    city: str = Query("", max_length=100),
    category: Category | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    organization_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(422, "Начало интервала должно быть раньше окончания")
    statement = select(Project).where(Project.status == "PUBLISHED")
    if search.strip():
        statement = statement.where(
            or_(
                Project.title.icontains(search.strip(), autoescape=True),
                Project.description.icontains(search.strip(), autoescape=True),
            )
        )
    if city.strip():
        statement = statement.where(func.lower(Project.city) == city.strip().lower())
    if category:
        statement = statement.where(Project.category == category)
    if organization_id:
        statement = statement.where(Project.owner_id == organization_id)
    if date_from:
        statement = statement.where(Project.starts_at >= datetime.combine(date_from, time.min, UTC))
    if date_to:
        statement = statement.where(
            Project.starts_at < datetime.combine(date_to, time.min, UTC) + timedelta(days=1)
        )
    return paginate(statement, db, page, page_size)


@router.get("/my/projects")
def my_projects(
    status: Status | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    user: User = Depends(organizer),
    db: Session = Depends(get_db),
):
    statement = select(Project).where(Project.owner_id == user.id)
    if status:
        statement = statement.where(Project.status == status)
    return paginate(statement, db, page, page_size)


@router.get("/projects/{project_id}")
def project_detail(project_id: int, request: Request, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Проект не найден")
    if project.status != "PUBLISHED":
        try:
            user_id = int(claims(request)["sub"])
        except HTTPException:
            user_id = None
        if user_id != project.owner_id:
            raise HTTPException(404, "Проект не найден")
    return serialize(project)


@router.post("/projects", status_code=201, dependencies=[Depends(csrf_guard)])
def create_project(
    data: ProjectInput, user: User = Depends(organizer), db: Session = Depends(get_db)
):
    values = data.model_dump()
    values["cover_url"] = str(data.cover_url)
    values["starts_at"] = data.starts_at.astimezone(UTC)
    project = Project(**values, owner_id=user.id, status="DRAFT")
    db.add(project)
    db.commit()
    db.refresh(project)
    return serialize(project)


@router.patch("/projects/{project_id}", dependencies=[Depends(csrf_guard)])
def update_project(
    project_id: int,
    data: ProjectInput,
    user: User = Depends(organizer),
    db: Session = Depends(get_db),
):
    project = owned(project_id, user, db)
    ensure_editable(project.status)
    values = data.model_dump()
    values["cover_url"] = str(data.cover_url)
    values["starts_at"] = data.starts_at.astimezone(UTC)
    for key, value in values.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return serialize(project)


@router.post("/projects/{project_id}/status", dependencies=[Depends(csrf_guard)])
def transition(
    project_id: int,
    data: StatusInput,
    user: User = Depends(organizer),
    db: Session = Depends(get_db),
):
    project = owned(project_id, user, db)
    if data.status == "PUBLISHED":
        values = serialize(project)
        ProjectInput.model_validate({key: values[key] for key in ProjectInput.model_fields})
    project.status = change_status(project.status, data.status)
    db.commit()
    db.refresh(project)
    return serialize(project)
