"""Initial profiles and projects schema."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("organization_name", sa.String(160)),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("skills", sa.String(1000), nullable=False),
        sa.Column("interests", sa.String(1000), nullable=False),
        sa.Column("website", sa.String(2000), nullable=False),
        sa.Column("avatar_url", sa.String(2000), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("location", sa.String(300), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("duration_unit", sa.String(16), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("cover_url", sa.String(2000), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
    )
    for field in ("owner_id", "city", "starts_at", "category", "status"):
        op.create_index(f"ix_projects_{field}", "projects", [field])


def downgrade():
    op.drop_table("projects")
    op.drop_table("users")
