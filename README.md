# 🐙 Octopus App

A FastAPI application built with the Octopus recursive fractal architecture.

## Architecture

This project follows the **Octopus** pattern where every component is a self-contained unit with:
- `router.py` - FastAPI routes with automatic sub-feature mounting
- `service.py` - Business logic
- `entities.py` - Domain models
- `schemas.py` - Pydantic schemas
- `features/` - Recursive child features
- `shared/` - Recursive shared utilities

## Quick Start

```bash
# Install dependencies (already done during init)
uv sync

# Run the application
uv run fastapi dev

# Or with uvicorn directly
uv run uvicorn app.main:app --reload
```

Visit:
- **http://localhost:8000/health** - Health check endpoint
- **http://localhost:8000/docs** - Interactive API documentation (Swagger UI)
- **http://localhost:8000/redoc** - Alternative API documentation (ReDoc)

## Development Commands

```bash
# Add a new feature
octopus add feature users
octopus add feature auth/permissions  # Nested feature

# Add a shared module
octopus add shared database
octopus add shared utils/validators   # Nested shared

# Remove components
octopus remove feature users
octopus remove shared database

# View project structure with routes
octopus structure

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app
```

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── router.py            # Auto-mounting root router
├── __init__.py          # Exports: settings, auto_discover_routers
├── features/            # Feature modules (recursive)
│   └── <feature>/
│       ├── router.py
│       ├── service.py
│       ├── entities.py
│       ├── schemas.py
│       ├── README.md
│       ├── TODO.md
│       ├── features/    # Nested features
│       └── shared/      # Nested shared modules
└── shared/              # Shared utilities (recursive)
    ├── config/          # Application settings
    │   └── service.py   # Settings, settings instance
    └── routing/         # Auto-discovery utilities
        └── service.py   # auto_discover_routers function

tests/                   # Mirrors app/ structure
├── conftest.py          # Test fixtures (client fixture)
└── app/
    ├── test_health.py   # Health endpoint tests
    ├── features/        # Feature tests
    └── shared/          # Shared module tests

docs/                    # Documentation
├── ARCHITECTURE.md      # Architecture guide
├── BEST_PRACTICES.md    # Coding standards
└── EXAMPLES.md          # Real-world examples

.env.example             # Environment variables template
```

## Default Shared Modules

Every new app includes two essential shared modules:

### `shared/config/`
Application configuration using pydantic-settings:
```python
from app.shared.config import settings

# Access configuration
print(settings.app_name)
print(settings.environment)
print(settings.database_url)
```

### `shared/routing/`
Router auto-discovery utility:
```python
from app.shared.routing import auto_discover_routers

router = APIRouter(prefix="/users")
# ... add routes ...

# Automatically mount nested feature routers
auto_discover_routers(router, __file__, __package__)
```

## Environment Variables

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```env
APP_NAME="My Octopus App"
ENVIRONMENT="development"
DATABASE_URL="postgresql://user:pass@localhost/dbname"
```

3. Access in code:
```python
from app import settings

print(settings.app_name)  # "My Octopus App"
```

## Database Migrations

This project uses Alembic for database schema migrations:

```bash
# Create a new migration (after making model changes)
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations to database
uv run alembic upgrade head

# View migration history
uv run alembic history

# View current migration status
uv run alembic current

# Downgrade to previous migration
uv run alembic downgrade -1

# Downgrade to specific revision
uv run alembic downgrade <revision_id>
```

**Note**: The initial migration has already been created and applied. For production deployments, always run migrations after updating the application.

## Testing

Run the test suite:
```bash
# All tests
uv run pytest

# With output
uv run pytest -v

# With coverage
uv run pytest --cov=app --cov-report=html

# Specific test file
uv run pytest tests/app/test_health.py

# Watch mode (requires pytest-watch)
uv run ptw
```

## Adding Features

```bash
# Create a users feature
octopus add feature users

# This creates:
# - app/features/users/ (router, service, entities, schemas)
# - tests/app/features/users/ (test files)
# - docs/app/features/users/ (documentation)

# Add nested features
octopus add feature users/profile
octopus add feature users/settings
```

## Learn More

- **`docs/ARCHITECTURE.md`** - Detailed architecture guide
- **`docs/BEST_PRACTICES.md`** - Coding standards and patterns
- **`docs/EXAMPLES.md`** - Real-world implementation examples
- **`TODO.md`** - Project tasks and next steps
- Each feature has its own `README.md` and `TODO.md`

## Support

Generated with [Octopus CLI](https://github.com/yourusername/octopus) 🐙
