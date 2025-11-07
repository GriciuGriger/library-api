# 📚 Library Management System API

Async REST API for managing library books and loan operations.

## 🧱 Tech Stack

- **API**: FastAPI 0.104 (async)
- **Database**: PostgreSQL 16 (via `asyncpg`)
- **ORM**: SQLAlchemy 2 + AsyncSession
- **Validation**: Pydantic v2
- **Tests**: pytest, pytest-asyncio, httpx, pytest-cov
- **Containerization**: Docker & Docker Compose

## 🚀 Quick Start (local Python)

1. Ensure Python 3.11 is installed.
2. Create and activate a virtual environment:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Create `.env` at repo root (see template below) and update values if needed.
5. Run the API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
   ```

Visit `http://localhost:8000/docs` for interactive documentation.

## 🐳 Quick Start (Docker Compose)

```bash
docker compose up --build
```

- Spins up PostgreSQL and the FastAPI backend.
- Update `.env` or compose overrides for production secrets before deploying.

## 🔧 Environment Configuration

Create `.env` (or copy from `.env.example` once added):

```
POSTGRES_USER=library
POSTGRES_PASSWORD=library
POSTGRES_DB=library
DATABASE_URL=postgresql+asyncpg://library:library@localhost:5432/library
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
```

When using Docker Compose, `DATABASE_URL` is provided automatically via service environment variables.

## ✅ Tests & Coverage

Run unit/integration tests:

```bash
cd backend
pytest
```

With coverage report:

```bash
pytest --cov=app --cov-report=term-missing
```

Async FastAPI clients may under-report coverage on some lines; the suite still exercises all critical paths.

## 📘 API Overview

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/` | API metadata |
| `GET` | `/health` | Health check |
| `GET` | `/books/` | List books |
| `POST` | `/books/` | Add book |
| `DELETE` | `/books/{serial}` | Remove book |
| `PATCH` | `/books/{serial}/loan` | Borrow/return operations |

Example borrow request:

```bash
curl -X PATCH "http://localhost:8000/books/123456/loan" \
  -H "Content-Type: application/json" \
  -d '{"action": "borrow", "card_number": "654321"}'
```

## 🛣️ Roadmap

- Add Alembic migrations (currently using metadata auto-create).
- Introduce GitHub Actions workflow for lint/tests & docker smoke.
