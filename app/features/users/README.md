# 🧩 Feature: Users

User management feature providing complete CRUD operations for system users.

## Overview

The Users feature provides:
- User registration and authentication
- User profile management
- Soft delete functionality
- Password hashing and verification
- Email and username uniqueness validation

## API Endpoints

### Status
- `GET /users/status` - Get feature status and user count

### User Management
- `POST /users/` - Create a new user
- `GET /users/` - List users (paginated)
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Soft delete user

## Data Model

```python
User {
    id: int (auto-generated)
    email: str (unique, required)
    username: str (unique, required)
    full_name: str (required)
    hashed_password: str (hashed, not returned)
    created_at: datetime
    updated_at: datetime
    is_active: bool (default: true)
}
```

## Usage Examples

### Create User
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "securepassword123"
  }'
```

### List Users
```bash
curl "http://localhost:8000/users/?skip=0&limit=10"
```

## Structure
- `router.py` → HTTP routes and sub-feature mounting
- `service.py` → business logic class (UsersService)
- `entities.py` → User SQLAlchemy model
- `schemas.py` → Pydantic request/response schemas
- `features/` → recursive child features
- `shared/` → recursive shared utilities

Refer to `/docs` for architecture details.
