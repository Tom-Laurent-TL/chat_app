# 🐙 Octopus Architecture Guide

## Overview

This project follows the **Octopus Recursive Fractal Architecture** - a scalable pattern where every component (app, feature, shared module) follows the same structure recursively.

## 🤖 AI Agents & Bots

For comprehensive documentation on the AI-powered conversation features, see [`AI_AGENTS_BOTS.md`](./AI_AGENTS_BOTS.md).

## Core Principles

### 1. Fractal Structure
Every unit (app, feature, or shared module) has the same structure:
```
unit/
├── router.py       # HTTP routes (features only)
├── service.py      # Business logic
├── entities.py     # Database/ORM models
├── schemas.py      # Pydantic models for API
├── features/       # Nested sub-features
└── shared/         # Nested shared modules
```

### 2. Onion Architecture Layers

**Outer Layer → Inner Layer:**
- `router.py` → API/HTTP layer
- `service.py` → Business logic layer
- `entities.py` → Domain/Data layer
- `schemas.py` → Contracts/Validation layer

**Dependencies flow inward:** Routers use Services, Services use Entities.

### 3. Auto-Discovery Pattern
Routes are automatically mounted using Python's module inspection:
- Parent routers discover and mount child routers
- No manual registration needed
- Add a feature, it's automatically available

## File Responsibilities

### router.py
- Defines HTTP endpoints
- Handles request/response
- Uses Service classes for logic
- Auto-mounts sub-feature routers

**Example:**
```python
from fastapi import APIRouter
from .service import UserService

router = APIRouter(prefix="/users", tags=["users"])
service = UserService()

@router.get("/")
def list_users():
    return service.get_all_users()
```

### service.py
- Contains business logic
- Orchestrates operations
- Uses entities for data access
- No HTTP-specific code

**Example:**
```python
class UserService:
    def __init__(self):
        # Initialize dependencies (DB, other services)
        pass
    
    def get_all_users(self):
        # Business logic here
        return []
```

### entities.py
- Database models (SQLAlchemy/ORM)
- Domain entities
- Database schema definitions

**Example:**
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
```

### schemas.py
- Pydantic models for API validation
- Request/Response schemas
- Data transfer objects (DTOs)

**Example:**
```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
```

## Entity vs Schema

**When to use entities.py:**
- Database table definitions
- ORM model relationships
- Database constraints
- Internal data structures

**When to use schemas.py:**
- API request validation
- API response serialization
- External data contracts
- Type safety for API layer

**Typical flow:**
1. Client sends JSON → Validated by `UserCreate` schema
2. Service creates entity → `User(name=..., email=...)`
3. Entity saved to database
4. Entity converted to schema → Returns `UserResponse`

## Features vs Shared

### Use Features when:
- Exposing HTTP endpoints
- Implementing business domains (users, products, orders)
- Building vertical slices of functionality
- Need to nest sub-features

### Use Shared when:
- Creating utilities/helpers (database, auth, logging)
- Defining common models/entities
- Building cross-cutting concerns that should be available everywhere
- Configuration and settings
- No HTTP endpoints needed

### Shared Module Cascading (Key Philosophy)

**Shared modules automatically cascade down to all nested features:**

```
app/shared/config/          # Available to ALL features at any depth
app/shared/database/        # Available to ALL features at any depth

app/features/users/
├── __init__.py            # Has: ...shared.config, ...shared.database
├── shared/validation/     # Available to users and its nested features
└── features/profile/
    └── __init__.py        # Has: ....shared.config (from app)
                           #      ....shared.database (from app)  
                           #      ...shared.validation (from parent)
```

**Benefits:**
- ✅ App-level shared modules (config, database) accessible everywhere
- ✅ Feature-level shared modules cascade to nested features
- ✅ No manual imports needed - automatically commented in `__init__.py`
- ✅ Just uncomment the imports you need

**Example imports in a nested feature:**
```python
# app/features/users/features/profile/__init__.py
"""Feature module initialization."""

# Auto-imported shared module: config
# from ....shared.config.service import *
# from ....shared.config.schemas import *

# Auto-imported shared module: database
# from ....shared.database.service import *
# from ....shared.database.schemas import *

# Auto-imported shared module: validation
# from ...shared.validation.service import *
# from ...shared.validation.schemas import *
```

## Nesting Guidelines

### Recommended Depth Limits
- **Maximum 3 levels** recommended for clarity
- Beyond 3 levels, consider if the feature hierarchy makes sense
- **Note:** With cascading shared modules, deep nesting is more viable than before

### Good Nesting Examples:
```
app/features/users/             # Level 1: User domain
├── features/profile/           # Level 2: User profile
│   └── features/avatar/        # Level 3: Profile avatar (still has access to app/shared/*)
└── features/settings/          # Level 2: User settings
```

### Why Cascading Changes the Game:
**Before:** Deep nesting meant losing access to app-level utilities
**Now:** All features inherit shared modules from parent scopes (with absolute imports)

```python
# Even at depth 3, you still have clean imports:
from app.shared.config.service import settings      # App config
from app.shared.database.service import get_db      # App database
from app.features.users.shared.user_utils import validate   # Parent's shared module

# No more confusing relative imports:
# from ......shared.config import settings  ❌ Avoid this!
```

### When to Stop Nesting:
- If relationships become unclear (not truly nested concepts)
- If features are too granular (single endpoint with no sub-features)
- If URLs become confusing (`/users/profile/avatar/settings/theme/colors`)

### Refactoring Pattern:
```
# Instead of unclear deep nesting:
app/features/ecommerce/features/products/features/reviews/features/moderation/

# Prefer flat, clear structure:
app/features/ecommerce/
app/features/product_reviews/
app/features/review_moderation/
```

**Rule of Thumb:** Nest when there's a true parent-child relationship, not just for code organization.

## Auto-Mounting Mechanism

### How It Works:

The Octopus architecture uses a **centralized auto-discovery utility** (`app.shared.routing`) to automatically mount sub-feature routers:

1. **Dynamic Path Resolution**: Uses `Path(__file__).parent` to find `features/` relative to caller
2. **Relative Imports**: Uses `__package__` for correct module resolution at any nesting level
3. **Error Handling**: Gracefully handles missing or malformed router modules
4. **Consistent Everywhere**: Same function works from root to deeply nested features

### Implementation:

Every `router.py` file ends with:
```python
from app.shared.routing import auto_discover_routers

# ... define your routes ...

# Automatically mount sub-feature routers
auto_discover_routers(router, __file__, __package__)
```

### What Gets Mounted:

The utility scans `features/` subdirectory and:
- ✅ Imports each module's `router.py`
- ✅ Mounts `router` attribute onto parent
- ✅ Preserves child's prefix/tags
- ✅ Skips modules without valid routers
- ❌ Silent failures prevented with optional verbose logging

### Example:
```python
# app/features/users/router.py
router = APIRouter(prefix="/users", tags=["users"])

# Auto-discovers: app/features/users/features/profile/router.py
# Result: /users/profile/* endpoints (prefix preserved)
```

### Benefits:

- **No Manual Registration**: Just create files, they're auto-mounted
- **AI-Friendly**: Consistent pattern at all levels
- **Bulletproof**: Works regardless of CWD or nesting depth
- **Debuggable**: Enable verbose mode to see what's being discovered

```python
# Debug mode (in development)
auto_discover_routers(router, __file__, __package__, verbose=True)
```

## Best Practices

### 1. Service Layer
- Keep services focused (Single Responsibility)
- Use dependency injection
- Handle errors at service level
- Return domain objects, not HTTP responses

### 2. Router Layer
- Thin routers (delegate to services)
- Use Pydantic schemas for validation
- Handle HTTP-specific logic only
- Use FastAPI's Depends for DI

### 3. Testing
- Test services independently
- Mock external dependencies
- Integration tests for routers
- Mirror test structure to app structure

### 4. Error Handling
```python
# In service.py
class UserService:
    def get_user(self, user_id: int):
        user = # ... fetch from DB
        if not user:
            raise ValueError(f"User {user_id} not found")
        return user

# In router.py
from fastapi import HTTPException

@router.get("/{user_id}")
def get_user(user_id: int):
    try:
        return service.get_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

### 5. Dependency Injection
```python
# shared/database/service.py
from sqlalchemy.orm import Session

def get_db() -> Session:
    # Database connection logic
    pass

# features/users/router.py
from fastapi import Depends
from app.shared.database.service import get_db

@router.get("/")
def list_users(db: Session = Depends(get_db)):
    return service.get_all_users(db)
```

## Common Patterns

### Pattern 1: CRUD Feature
```
features/users/
├── router.py       # GET, POST, PUT, DELETE endpoints
├── service.py      # UserService with CRUD methods
├── entities.py     # User ORM model
└── schemas.py      # UserCreate, UserUpdate, UserResponse
```

### Pattern 2: Authentication (Shared)
```
shared/auth/
├── service.py      # AuthService (no router!)
├── entities.py     # Session, Token models
└── schemas.py      # LoginRequest, TokenResponse
```

### Pattern 3: Nested Feature Domain
```
features/blog/
├── router.py               # Blog home endpoints
├── features/posts/         # Blog posts
│   ├── router.py           # CRUD for posts
│   └── features/comments/  # Post comments
└── features/authors/       # Blog authors
```

## Migration & Refactoring

### Adding a Feature to Existing Code:
1. Create feature directory in appropriate location
2. Move relevant routes to `router.py`
3. Extract business logic to `service.py`
4. Define models in `entities.py` and `schemas.py`
5. Auto-mounting handles the rest!

### Splitting a Large Feature:
1. Identify logical sub-domains
2. Create `features/` subdirectory
3. Move routes/services to sub-features
4. Update imports
5. Test auto-mounting works

## Performance Considerations

### Auto-Discovery Overhead:
- Happens once at startup
- Minimal performance impact
- Use caching for production

### Deep Nesting:
- Can increase import complexity
- Impacts cold start time
- Keep depth ≤ 3 levels

## Troubleshooting

### Routes Not Showing:
1. Check router has correct prefix
2. Verify `router` is exported in `router.py`
3. Ensure parent is importing correctly
4. Check for import errors in logs

### Circular Imports:
1. Use lazy imports in services
2. Move shared code to `shared/` modules
3. Avoid cross-feature imports (use shared instead)

## Further Reading

- `/docs/BEST_PRACTICES.md` - Coding standards
- `/docs/EXAMPLES.md` - Real-world patterns
- `/docs/TESTING.md` - Testing strategies
