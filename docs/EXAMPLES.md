# 📚 Real-World Examples

## Example 1: Simple CRUD Feature

### Structure
```
features/products/
├── router.py
├── service.py
├── entities.py
└── schemas.py
```

### entities.py
```python
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
```

### schemas.py
```python
from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    stock: int
    
    class Config:
        from_attributes = True
```

### service.py
```python
from sqlalchemy.orm import Session
from .entities import Product
from .schemas import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_product(self, data: ProductCreate) -> Product:
        product = Product(**data.dict())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def get_product(self, product_id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def list_products(self, skip: int = 0, limit: int = 100) -> list[Product]:
        return self.db.query(Product).offset(skip).limit(limit).all()
    
    def update_product(self, product_id: int, data: ProductUpdate) -> Product | None:
        product = self.get_product(product_id)
        if not product:
            return None
        
        for key, value in data.dict(exclude_unset=True).items():
            setattr(product, key, value)
        
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def delete_product(self, product_id: int) -> bool:
        product = self.get_product(product_id)
        if not product:
            return False
        
        self.db.delete(product)
        self.db.commit()
        return True
```

### router.py
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.shared.database.service import get_db
from .service import ProductService
from .schemas import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])

def get_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    service: ProductService = Depends(get_service)
):
    """Create a new product."""
    return service.create_product(data)

@router.get("/", response_model=list[ProductResponse])
def list_products(
    skip: int = 0,
    limit: int = 100,
    service: ProductService = Depends(get_service)
):
    """List all products with pagination."""
    return service.list_products(skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    service: ProductService = Depends(get_service)
):
    """Get a single product by ID."""
    product = service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    service: ProductService = Depends(get_service)
):
    """Update a product."""
    product = service.update_product(product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    service: ProductService = Depends(get_service)
):
    """Delete a product."""
    if not service.delete_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
```

## Example 2: Nested Feature (Blog with Posts and Comments)

### Structure
```
features/blog/
├── router.py                   # Blog home
├── service.py
├── features/
│   ├── posts/                  # Blog posts
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── entities.py
│   │   ├── schemas.py
│   │   └── features/
│   │       └── comments/       # Post comments
│   │           ├── router.py
│   │           ├── service.py
│   │           ├── entities.py
│   │           └── schemas.py
│   └── authors/                # Blog authors
│       ├── router.py
│       ├── service.py
│       ├── entities.py
│       └── schemas.py
```

### Result URLs:
- `GET /blog/` - Blog home
- `GET /blog/posts/` - List posts
- `POST /blog/posts/` - Create post
- `GET /blog/posts/{post_id}/comments/` - List comments
- `POST /blog/posts/{post_id}/comments/` - Create comment
- `GET /blog/authors/` - List authors

## Example 3: Shared Authentication Module

### Structure
```
shared/auth/
├── service.py      # No router.py!
├── entities.py
└── schemas.py
```

### entities.py
```python
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### schemas.py
```python
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

### service.py
```python
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .entities import User
from .schemas import LoginRequest, TokenResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session, secret_key: str):
        self.db = db
        self.secret_key = secret_key
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, user_id: int, expires_delta: timedelta = None) -> str:
        if expires_delta is None:
            expires_delta = timedelta(minutes=15)
        
        expire = datetime.utcnow() + expires_delta
        to_encode = {"sub": str(user_id), "exp": expire}
        return jwt.encode(to_encode, self.secret_key, algorithm="HS256")
    
    def login(self, credentials: LoginRequest) -> TokenResponse:
        user = self.authenticate_user(credentials.email, credentials.password)
        if not user:
            raise ValueError("Invalid credentials")
        
        access_token = self.create_access_token(user.id)
        return TokenResponse(access_token=access_token)
```

### Usage in a feature:
```python
# features/users/router.py
from fastapi import Depends
from app.shared.auth.service import AuthService
from app.shared.auth.schemas import LoginRequest

@router.post("/login")
def login(
    credentials: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.login(credentials)
```

## Example 4: Database Setup (Shared Module)

### shared/database/service.py
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.shared.config.service import settings

# Create engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()

def get_db() -> Session:
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    # Import all models here to register them
    from app.features.users.entities import User
    from app.features.products.entities import Product
    
    Base.metadata.create_all(bind=engine)
```

### Usage in main.py:
```python
from fastapi import FastAPI
from app.shared.database.service import init_db

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()
```

## Example 5: Error Handling Pattern

### shared/exceptions/service.py
```python
class AppException(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(AppException):
    def __init__(self, resource: str, identifier: any):
        super().__init__(
            message=f"{resource} with id {identifier} not found",
            status_code=404
        )

class DuplicateError(AppException):
    def __init__(self, resource: str, field: str, value: any):
        super().__init__(
            message=f"{resource} with {field}='{value}' already exists",
            status_code=409
        )

class ValidationError(AppException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=422)
```

### Error handler in main.py:
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.shared.exceptions.service import AppException

app = FastAPI()

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
```

### Usage in service:
```python
from app.shared.exceptions.service import NotFoundError, DuplicateError

class UserService:
    def get_user(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User", user_id)
        return user
    
    def create_user(self, data: UserCreate) -> User:
        # Check for duplicate email
        existing = self.db.query(User).filter(User.email == data.email).first()
        if existing:
            raise DuplicateError("User", "email", data.email)
        
        user = User(**data.dict())
        self.db.add(user)
        self.db.commit()
        return user
```
