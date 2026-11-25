import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text

from app.routes import auth, profiles, projects


def create_app(engine=None, secret=None, origin=None):
    secret = secret or os.environ.get("SECRET_KEY", "")
    if len(secret) < 32 or secret.startswith("replace-with-"):
        raise RuntimeError("Set SECRET_KEY to a random value of at least 32 characters")
    app = FastAPI(title="Волонтёрский сервис", version="0.1.0")
    app.state.engine = engine or create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
    app.state.secret = secret
    app.state.origin = (origin or os.environ.get("APP_ORIGIN", "http://localhost:8080")).rstrip("/")
    app.state.secure_cookie = os.environ.get("COOKIE_SECURE", "false").lower() == "true"

    @app.middleware("http")
    async def origin_guard(request: Request, call_next):
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            if request.headers.get("origin") != app.state.origin:
                return JSONResponse({"detail": "Недопустимый источник запроса"}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/api/health")
    def health():
        with app.state.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok"}

    for router in (auth.router, profiles.router, projects.router):
        app.include_router(router, prefix="/api")
    return app
