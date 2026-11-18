"""Container entry point: configure database URL, apply migrations, start API."""

import os
import subprocess

from sqlalchemy import URL

if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = URL.create(
        "postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
    ).render_as_string(hide_password=False)

subprocess.run(["alembic", "upgrade", "head"], check=True)
os.execvp(
    "uvicorn",
    ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"],
)
