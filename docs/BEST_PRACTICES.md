# 🎯 Best Practices Guide

## Code Organization

### Feature Structure
✅ **DO:**
```python
# Clear separation of concerns
features/users/
├── router.py       # HTTP layer
├── service.py      # Business logic
├── entities.py     # Data models
└── schemas.py      # API contracts
```

❌ **DON'T:**
```python
# Mixing concerns
features/users/
└── users.py        # Everything in one file
```

### Naming Conventions

#### Files
- Use `snake_case` for feature names: `user_profile`, `blog_posts`
- Standard filenames: `router.py`, `service.py`, `entities.py`, `schemas.py`

#### Classes
- Services: `{Feature}Service` → `UserService`, `BlogPostService`
- Entities: Singular nouns → `User`, `BlogPost`
- Schemas: Descriptive names → `UserCreate`, `UserResponse`

#### Functions
- Router functions: Verb + noun → `create_user()`, `list_posts()`
- Service methods: Business-focused → `authenticate()`, `publish_post()`

## Shared Modules & Cascading Imports

### Philosophy: Shared Modules Cascade Down

**Key Concept:** Shared modules at any level are automatically available to all nested features below them.

```
app/shared/config/          ← Available to ALL features
app/shared/database/        ← Available to ALL features

app/features/users/
├── __init__.py            # Auto-imports: config, database
├── shared/validation/     ← Available to users and nested features
└── features/profile/
    └── __init__.py        # Auto-imports: config, database, validation
```

### When to Create Shared Modules

#### App-Level Shared (`app/shared/`)
✅ **Use for:**
- Configuration (already created: `config/`)
- Database connections and sessions
- Authentication & authorization
- Logging utilities
- Common validators
- Email/notification services

**These are available EVERYWHERE in your app.**

#### Feature-Level Shared (`features/users/shared/`)
✅ **Use for:**
- Feature-specific utilities
- Domain-specific validators
- Feature-scoped helpers
- Only needed by this feature and its children

### Using Shared Modules

Every feature's `__init__.py` contains auto-generated import comments:

```python
# app/features/users/features/profile/__init__.py
"""Feature module initialization."""

# Auto-imported shared module: config
# from app.shared.config.service import settings
# from app.shared.config.schemas import *

# Auto-imported shared module: database
# from app.shared.database.service import get_db
# from app.shared.database.schemas import *

# Auto-imported shared module: validation  
# from app.features.users.shared.validation.service import *
# from app.features.users.shared.validation.schemas import *
```

**To use them:**
1. Uncomment the imports you need
2. Or import directly in your service/router files

```python
# In profile/service.py
from app.shared.config.service import settings
from app.shared.database.service import get_db

class ProfileService:
    def __init__(self):
        self.db_url = settings.database_url  # ✅ Works!
```

**Why absolute imports?**
- ✅ **Readable** - `app.shared.config` is clear, not `......shared.config`
- ✅ **Refactorable** - Move features without breaking imports
- ✅ **IDE-friendly** - Better autocomplete and navigation
- ✅ **Explicit** - Always know exactly where code comes from

### Benefits of Cascading

✅ **No manual wiring** - Just create the shared module, it propagates automatically  
✅ **Deep nesting viable** - Even at depth 5, you still have access to app/shared/config  
✅ **Clear dependencies** - See all available shared modules in `__init__.py`  
✅ **Opt-in usage** - Imports are commented, enable only what you need

## Service Layer Best Practices

### 1. Single Responsibility
```python
# ✅ GOOD: Focused service
class UserService:
    def create_user(self, data: UserCreate) -> User:
        # User creation logic only
        pass
    
    def update_user(self, user_id: int, data: UserUpdate) -> User:
        # User update logic only
        pass

# ❌ BAD: Too many responsibilities
class UserService:
    def create_user(self, data): pass
    def send_email(self, to): pass
    def generate_report(self): pass
    def process_payment(self): pass
```

### 2. Dependency Injection
```python
# ✅ GOOD: Injectable dependencies
class UserService:
    def __init__(self, db: Database, email_service: EmailService):
        self.db = db
        self.email_service = email_service
    
    def create_user(self, data: UserCreate) -> User:
        user = User(**data.dict())
        self.db.add(user)
        self.email_service.send_welcome(user.email)
        return user

# Usage in router
@router.post("/")
def create_user(
    data: UserCreate,
    db: Database = Depends(get_db),
    email: EmailService = Depends(get_email_service)
):
    service = UserService(db, email)
    return service.create_user(data)
```

### 3. Error Handling
```python
# ✅ GOOD: Service raises domain exceptions
class UserService:
    def get_user(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

# Router translates to HTTP errors
@router.get("/{user_id}")
def get_user(user_id: int):
    try:
        return service.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

## Router Layer Best Practices

### 1. Thin Routers
```python
# ✅ GOOD: Router delegates to service
@router.post("/")
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create_user(data)

# ❌ BAD: Business logic in router
@router.post("/")
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    # Validation logic
    if len(data.password) < 8:
        raise HTTPException(400, "Password too short")
    
    # Business logic
    hashed = hash_password(data.password)
    user = User(name=data.name, password=hashed)
    
    # Database logic
    db.add(user)
    db.commit()
    
    # Email logic
    send_welcome_email(user.email)
    
    return user
```

### 2. Use Response Models
```python
# ✅ GOOD: Explicit response schema
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    return service.get_user(user_id)

# ❌ BAD: No type safety
@router.get("/{user_id}")
def get_user(user_id: int):
    return service.get_user(user_id)
```

### 3. Status Codes
```python
# ✅ GOOD: Explicit status codes
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate):
    return service.create_user(data)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    service.delete_user(user_id)
```

## Entity Best Practices

### 1. Clear Relationships
```python
# ✅ GOOD: Well-defined relationships
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    # Clear relationship definition
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    
    author = relationship("User", back_populates="posts")
```

### 2. Constraints & Validation
```python
# ✅ GOOD: Database-level constraints
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
```

## Schema Best Practices

### 1. Request vs Response Schemas
```python
# ✅ GOOD: Separate schemas for different use cases
class UserCreate(BaseModel):
    """Schema for creating a user."""
    name: str
    email: EmailStr
    password: str  # Password in create request

class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: str | None = None
    email: EmailStr | None = None

class UserResponse(BaseModel):
    """Schema for returning user data."""
    id: int
    name: str
    email: str
    # No password in response!
    
    class Config:
        from_attributes = True  # Works with ORM models
```

### 2. Validation
```python
# ✅ GOOD: Schema-level validation
from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    age: int = Field(..., ge=18, le=120)
    
    @validator('name')
    def name_must_not_contain_spaces(cls, v):
        if ' ' in v:
            raise ValueError('name cannot contain spaces')
        return v
```

## Testing Best Practices

### 1. Test Structure Mirrors App Structure
```
tests/
└── app/
    ├── features/
    │   └── users/
    │       ├── test_router.py
    │       ├── test_service.py
    │       └── test_integration.py
    └── shared/
        └── auth/
            └── test_service.py
```

### 2. Unit Test Services
```python
# ✅ GOOD: Test service independently
def test_create_user():
    # Mock dependencies
    mock_db = Mock()
    mock_email = Mock()
    
    service = UserService(mock_db, mock_email)
    user = service.create_user(UserCreate(name="Test", email="test@example.com"))
    
    assert user.name == "Test"
    mock_db.add.assert_called_once()
    mock_email.send_welcome.assert_called_once()
```

### 3. Integration Test Routers
```python
# ✅ GOOD: Test full request/response cycle
from fastapi.testclient import TestClient

def test_create_user_endpoint():
    client = TestClient(app)
    response = client.post(
        "/users/",
        json={"name": "Test", "email": "test@example.com", "password": "secret"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test"
    assert "password" not in data  # Verify password not returned
```

## Database Best Practices

### 1. Connection Management
```python
# shared/database/service.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2. Transactions
```python
# ✅ GOOD: Explicit transaction handling
class UserService:
    def create_user_with_profile(self, user_data, profile_data):
        try:
            user = User(**user_data.dict())
            self.db.add(user)
            self.db.flush()  # Get user.id without committing
            
            profile = Profile(user_id=user.id, **profile_data.dict())
            self.db.add(profile)
            
            self.db.commit()
            return user
        except Exception:
            self.db.rollback()
            raise
```

## Security Best Practices

### 1. Never Return Sensitive Data
```python
# ✅ GOOD: UserResponse excludes password
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    # password field not included

# ❌ BAD: Returns everything
@router.get("/{user_id}")
def get_user(user_id: int):
    return db.query(User).filter(User.id == user_id).first()
    # Returns password hash!
```

### 2. Validate All Inputs
```python
# ✅ GOOD: Pydantic validates automatically
class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    age: int = Field(ge=18)  # Must be >= 18
    website: HttpUrl | None = None  # Validates URL format
```

### 3. Use Dependencies for Auth
```python
# shared/auth/service.py
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Verify token and return user
    pass

# features/users/router.py
@router.get("/me")
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

## Performance Best Practices

### 1. Lazy Loading vs Eager Loading
```python
# ✅ GOOD: Eager load related data when needed
from sqlalchemy.orm import joinedload

def get_user_with_posts(user_id: int):
    return db.query(User)\
        .options(joinedload(User.posts))\
        .filter(User.id == user_id)\
        .first()

# ❌ BAD: N+1 query problem
user = db.query(User).filter(User.id == user_id).first()
for post in user.posts:  # Triggers a query for each post!
    print(post.title)
```

### 2. Pagination
```python
# ✅ GOOD: Always paginate lists
@router.get("/", response_model=list[UserResponse])
def list_users(skip: int = 0, limit: int = 100):
    return service.list_users(skip=skip, limit=limit)
```

### 3. Caching
```python
# ✅ GOOD: Cache expensive operations
from functools import lru_cache

class UserService:
    @lru_cache(maxsize=128)
    def get_user_stats(self, user_id: int):
        # Expensive calculation
        return calculate_stats(user_id)
```

## Code Quality

### 1. Type Hints
```python
# ✅ GOOD: Full type hints
def create_user(self, data: UserCreate, db: Session) -> User:
    user = User(**data.dict())
    db.add(user)
    db.commit()
    return user
```

### 2. Docstrings
```python
# ✅ GOOD: Clear docstrings
class UserService:
    """Service for managing user operations.
    
    Handles user creation, updates, and authentication.
    """
    
    def create_user(self, data: UserCreate) -> User:
        """Create a new user account.
        
        Args:
            data: User creation data with name, email, and password.
            
        Returns:
            The newly created User instance.
            
        Raises:
            DuplicateEmailError: If email already exists.
        """
        pass
```

### 3. Constants
```python
# ✅ GOOD: Use constants
MAX_NAME_LENGTH = 50
MIN_PASSWORD_LENGTH = 8
DEFAULT_PAGE_SIZE = 20

class UserCreate(BaseModel):
    name: str = Field(..., max_length=MAX_NAME_LENGTH)
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH)
```

## When to Refactor

### Signs It's Time to Extract a Feature:
- Single file > 500 lines
- Router has > 10 endpoints
- Service has > 10 methods
- Multiple unrelated responsibilities

### Signs It's Time to Extract Shared Module:
- Same code duplicated across 3+ features
- Utility functions scattered everywhere
- Cross-cutting concern (logging, auth, etc.)

### Signs It's Time to Stop Nesting:
- Already at depth 3
- Feature relationships unclear
- Hard to explain the hierarchy
- Circular dependency issues
