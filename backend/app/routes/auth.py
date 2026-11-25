from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import Credentials, Register
from app.security import (
    DUMMY_HASH,
    claims,
    csrf_guard,
    current_user,
    get_db,
    hasher,
    issue_token,
    private_profile,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(data: Register, db: Session = Depends(get_db)):
    user = User(**data.model_dump(exclude={"password"}), password_hash=hasher.hash(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Аккаунт с таким email уже существует") from None
    db.refresh(user)
    return private_profile(user)


@router.post("/login")
def login(data: Credentials, request: Request, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email))
    valid = verify_password(data.password, user.password_hash if user else DUMMY_HASH)
    if not user or not valid:
        raise HTTPException(401, "Неверный email или пароль")
    token, csrf = issue_token(user.id, request.app.state.secret)
    response.set_cookie(
        "session",
        token,
        httponly=True,
        secure=request.app.state.secure_cookie,
        samesite="strict",
        max_age=1800,
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"
    return {"user": private_profile(user), "csrf_token": csrf}


@router.get("/me")
def me(request: Request, response: Response, user: User = Depends(current_user)):
    response.headers["Cache-Control"] = "no-store"
    return {"user": private_profile(user), "csrf_token": claims(request)["csrf"]}


@router.post("/logout", status_code=204, dependencies=[Depends(csrf_guard)])
def logout(response: Response):
    response.delete_cookie("session", path="/")
