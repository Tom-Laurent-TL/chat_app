# 🧩 Shared Module: Database

Provides SQLAlchemy database engine, session management, and utilities shared across features.

## Usage

Features can import database utilities directly:
```python
from app.shared.database.service import get_db, init_db, DatabaseService
from app.shared.database.entities import BaseEntity
from app.shared.database.schemas import BaseEntitySchema
```

## Features

### Database Engine & Sessions
- **SQLAlchemy 2.0** engine with connection pooling
- **Session management** with automatic cleanup
- **Dependency injection** support for FastAPI routes

### Base Entities
- `BaseEntity` class with common fields (id, timestamps, is_active)
- Automatic table creation and management

### Health Checks & Monitoring
- Database connection health checks
- Connection information reporting

## Database Dependency Injection

Use `get_db()` in your FastAPI routes:
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.shared.database.service import get_db

@router.get("/items")
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

## Database Initialization

Initialize tables on app startup:
```python
from fastapi import FastAPI
from app.shared.database.service import init_db

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()
```

## Configuration

Database URL is configured via environment variables:
```env
DATABASE_URL="sqlite:///./app.db"          # Development
DATABASE_URL="postgresql://user:pass@localhost/dbname"  # Production
```

## Structure

- `service.py` → Engine, sessions, utilities
- `entities.py` → Base entity classes
- `schemas.py` → Pydantic models for DB operations

Refer to `/docs` for architecture details.
