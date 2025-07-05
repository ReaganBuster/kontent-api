# FastAPI Project

A production-ready FastAPI project with SQLAlchemy, Alembic, and authentication.

## Features

- FastAPI with async support
- SQLAlchemy ORM with Alembic migrations
- JWT authentication
- User management
- Database agnostic (SQLite for development, easily portable to PostgreSQL/Supabase)
- Comprehensive testing setup
- Docker support
- Production-ready structure

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run the application:
```bash
python main.py
# or
python scripts/run_dev.py
```

## Database Migrations

Create a new migration:
```bash
./scripts/create_migration.sh "Add user table"
```

Apply migrations:
```bash
./scripts/run_migration.sh
```

## Testing

Run tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Docker

Build and run with Docker:
```bash
docker-compose up --build
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Migration

To switch from SQLite to PostgreSQL/Supabase:

1. Update `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

2. Install PostgreSQL dependencies (already in requirements.txt):
```bash
pip install asyncpg
```

3. Run migrations:
```bash
alembic upgrade head
```

## Project Structure

```
.
├── app/
│   ├── api/v1/          # API routes
│   ├── core/            # Core functionality (config, database, security)
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── utils/           # Utility functions
├── tests/               # Test files
├── alembic/             # Database migrations
├── scripts/             # Utility scripts
└── docs/                # Documentation
```
