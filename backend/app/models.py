from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16))
    name: Mapped[str] = mapped_column(String(100))
    organization_name: Mapped[str | None] = mapped_column(String(160))
    city: Mapped[str] = mapped_column(String(100), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    skills: Mapped[str] = mapped_column(String(1000), default="")
    interests: Mapped[str] = mapped_column(String(1000), default="")
    website: Mapped[str] = mapped_column(String(2000), default="")
    avatar_url: Mapped[str] = mapped_column(String(2000), default="")


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    city: Mapped[str] = mapped_column(String(100), index=True)
    location: Mapped[str] = mapped_column(String(300))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration: Mapped[int]
    duration_unit: Mapped[str] = mapped_column(String(16))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(32), index=True)
    cover_url: Mapped[str] = mapped_column(String(2000))
    status: Mapped[str] = mapped_column(String(16), default="DRAFT", index=True)
