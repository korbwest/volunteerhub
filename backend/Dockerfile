FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY pyproject.toml requirements-dev.lock.txt ./
COPY app ./app
RUN pip install -c requirements-dev.lock.txt .
COPY alembic.ini ./
COPY migrations ./migrations
COPY start.py ./

FROM base AS test
RUN pip install -c requirements-dev.lock.txt '.[dev]'
COPY tests ./tests
CMD ["pytest", "--cov=app", "--cov-branch"]

FROM base AS runtime
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["python", "start.py"]
