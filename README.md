# Backend TestLive MVP

FastAPI backend for the TestLive MVP application.

## Stack

- Python 3.14
- FastAPI
- SQLAlchemy 2.x async ORM
- PostgreSQL
- Alembic
- Pydantic v2
- MinIO for attachments
- pytest / pytest-asyncio / httpx

## Current backend structure

```text
backend/
├── alembic/
│   ├── env.py
│   └── versions/
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── security.py
│   └── storage.py
├── tests/
├── Dockerfile
├── alembic.ini
├── requirements.txt
└── start.py
```

## Environment

Backend reads settings from the repo-level `.env` file.

Common values:

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=test_live_mvp
DATABASE_USER=devuser
DATABASE_PASSWORD=devpassword
SECRET_KEY=change-me-for-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=testlive-files
MINIO_SECURE=false
MINIO_PRESIGNED_EXPIRE_SECONDS=300
ATTACHMENT_MAX_SIZE_BYTES=26214400
```

## Install and run

From repo root:

```bash
python3.14 -m venv venv
./venv/bin/pip install -r backend/requirements.txt
```

Run locally:

```bash
cd backend
PYTHONPATH=. ../venv/bin/alembic upgrade head
../venv/bin/python start.py
```

Or:

```bash
cd backend
PYTHONPATH=. ../venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Migrations

The project now uses a single Alembic baseline revision that creates the full current schema.

```bash
cd backend
PYTHONPATH=. ../venv/bin/alembic upgrade head
```

Notes:

- baseline migration also inserts required reference statuses
- no separate seed step is needed

## Tests and checks

```bash
cd backend
../venv/bin/ruff format .
../venv/bin/ruff check .
PYTHONPATH=. ../venv/bin/pytest tests -v
PYTHONPATH=. ../venv/bin/pytest tests --collect-only -q
```

## Current API surface

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `GET /api/auth/me`

### Projects

- `GET /api/projects`
- `POST /api/projects`
- `PATCH /api/projects/{id}`
- `DELETE /api/projects/{id}`

### Project members

- `GET /api/projects/{project_id}/members`
- `GET /api/projects/{project_id}/members/me`
- `POST /api/projects/{project_id}/members`
- `PATCH /api/projects/{project_id}/members/{user_id}`
- `DELETE /api/projects/{project_id}/members/{user_id}`

### Releases and scope

- `GET /api/releases?project_id=...`
- `POST /api/releases`
- `PATCH /api/releases/{id}`
- `DELETE /api/releases/{id}`
- `GET /api/releases/{id}/scope`
- `POST /api/releases/{id}/test-plans`
- `DELETE /api/releases/{id}/test-plans/{plan_id}`
- `POST /api/releases/{id}/test-cases`
- `DELETE /api/releases/{id}/test-cases/{case_id}`

### Test library

- `GET /api/test-plans?project_id=...`
- `POST /api/test-plans`
- `PATCH /api/test-plans/{id}`
- `DELETE /api/test-plans/{id}`
- `GET /api/test-cases?test_plan_id=...`
- `POST /api/test-cases`
- `PATCH /api/test-cases/{id}`
- `DELETE /api/test-cases/{id}`

### Results and attachments

- `GET /api/statuses?category=result`
- `POST /api/results`
- `PATCH /api/results/{id}`
- `POST /api/results/{id}/attachments`
- `GET /api/results/{id}/attachments/{attachment_id}/download`
- `DELETE /api/results/{id}/attachments/{attachment_id}`

## MinIO behavior

- `minio-init` in Docker Compose creates the configured bucket
- backend also runs `ensure_minio_bucket()` on startup
- uploads use MinIO object storage and downloads use presigned URLs
