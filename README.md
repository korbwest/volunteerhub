# VolunteerHub — «Рядом»

Веб-приложение для управления волонтёрскими проектами. Курсовой проект по дисциплине «Конструирование программного обеспечения».

## Возможности прототипа

- Регистрация и вход для волонтёра и организатора.
- Просмотр и редактирование собственного профиля.
- Каталоги проектов и организаций, поиск, фильтры и постраничная навигация.
- Создание и редактирование проектов организатором.
- Публикация, возврат в черновик и архивация проектов.
- Разграничение доступа: организатор управляет только своими проектами.

Заявки на участие, уведомления, баллы и рейтинг волонтёров пока не реализованы. Архивные проекты доступны только для чтения. Изображения задаются ссылками; загрузка файлов не предусмотрена.

## Технологии и структура

Backend: Python 3.11+, FastAPI, SQLAlchemy, Alembic, PostgreSQL.
Frontend: React, TypeScript, Vite.
Тесты: pytest, pytest-cov, Vitest, Testing Library.

```text
backend/
  app/          модели, схемы, серверная логика и маршруты API
  migrations/   миграции Alembic
  tests/        модульные тесты и проверки API
frontend/
  src/          страницы, компоненты, API-клиент и тесты
docs/           правила работы с репозиторием
compose.yaml    локальный запуск приложения и PostgreSQL
```

## Запуск приложения

Нужны Git и Docker Compose v2 (например, Docker Desktop с Linux containers). Команды выполняются из корня репозитория.

```powershell
Copy-Item .env.example .env
```

В `.env` замените `POSTGRES_PASSWORD` и `SECRET_KEY` собственными случайными значениями. Для `SECRET_KEY` используйте не менее 32 символов. Файл `.env` исключён из Git.

```powershell
docker compose up --build -d
docker compose ps
```

Откройте http://localhost:8080. Создайте аккаунт организатора, затем проект и опубликуйте его. В опубликованном каталоге проект будет доступен волонтёрам.

Перед запуском API автоматически применяются миграции. PostgreSQL хранит данные в именованном томе. Для остановки с сохранением данных:

```powershell
docker compose down
```

Опция `-v` удаляет том с базой данных. При изменении порта одновременно измените `APP_PORT` и `APP_ORIGIN` в `.env`.

## Локальные проверки

Для проверок вне Docker нужны Python 3.11+ и Node.js 22 с npm. Установка зависимостей:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -c backend/requirements-dev.lock.txt -e './backend[dev]'
Push-Location frontend
npm.cmd ci --no-audit --no-fund
Pop-Location
```

Backend:

```powershell
.venv/Scripts/ruff check backend
.venv/Scripts/ruff format --check backend
Push-Location backend
../.venv/Scripts/python -m pytest --cov=app --cov-report=term-missing
Pop-Location
```

Без `TEST_DATABASE_URL` тесты используют временную SQLite. Это облегчённая проверка API: тест конкурентного доступа требует PostgreSQL и пропускается на SQLite.

Для интеграционных проверок задайте `TEST_DATABASE_URL` в формате `postgresql+psycopg://USER:PASSWORD@HOST:PORT/volunteerhub_test`, указывающий на отдельную тестовую базу. Имя должно содержать `test`. Тесты создают и удаляют таблицы: базу приложения использовать нельзя.

Frontend:

```powershell
Push-Location frontend
npm.cmd run lint
npm.cmd run format:check
npm.cmd run test:coverage
npm.cmd run build
Pop-Location
```

Команда сборки проверяет TypeScript и создаёт `frontend/dist`. Отчёт тестов сохраняется в `frontend/reports/junit.xml`, покрытие — в `frontend/coverage`.

## Разработка

Используются GitHub Flow и Conventional Commits. Правила ветвления, коммитов и слияния описаны в [docs/git-workflow.md](docs/git-workflow.md).

Автоматические проверки GitHub Actions, защита основной ветки и выпуск релизов на текущем этапе ещё не настроены.
