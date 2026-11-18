import secrets
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.models import User

hasher = PasswordHasher()
DUMMY_HASH = hasher.hash("not-a-real-password")


def get_db(request: Request):
    with Session(request.app.state.engine) as session:
        yield session


def verify_password(password: str, hashed: str) -> bool:
    try:
        return hasher.verify(hashed, password)
    except (VerificationError, InvalidHashError):
        return False


def issue_token(user_id: int, secret: str):
    csrf = secrets.token_urlsafe(32)
    token = jwt.encode(
        {"sub": str(user_id), "csrf": csrf, "exp": datetime.now(UTC) + timedelta(minutes=30)},
        secret,
        algorithm="HS256",
    )
    return token, csrf


def claims(request: Request):
    try:
        data = jwt.decode(
            request.cookies.get("session", ""),
            request.app.state.secret,
            algorithms=["HS256"],
            options={"require": ["exp", "sub", "csrf"]},
        )
        int(data["sub"])
        if not isinstance(data["csrf"], str):
            raise ValueError
        return data
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(401, "Войдите в аккаунт") from None


def current_user(request: Request, db: Session = Depends(get_db)):
    user = db.get(User, int(claims(request)["sub"]))
    if not user:
        raise HTTPException(401, "Войдите в аккаунт")
    return user


def csrf_guard(request: Request):
    data = claims(request)
    if not secrets.compare_digest(
        request.headers.get("X-CSRF-Token", "").encode(), data["csrf"].encode()
    ):
        raise HTTPException(403, "Обновите страницу и повторите действие")


def organizer(user: User = Depends(current_user)):
    if user.role != "ORGANIZER":
        raise HTTPException(403, "Действие доступно организатору")
    return user


def private_profile(user: User):
    fields = (
        "id",
        "email",
        "role",
        "name",
        "organization_name",
        "city",
        "description",
        "skills",
        "interests",
        "website",
        "avatar_url",
    )
    return {field: getattr(user, field) for field in fields}


def public_organization(user: User):
    return {
        field: getattr(user, field)
        for field in (
            "id",
            "organization_name",
            "city",
            "description",
            "website",
            "avatar_url",
        )
    }
