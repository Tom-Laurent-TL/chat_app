"""
Pydantic schemas for users.
Define request/response models for user operations.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.shared.database.schemas import BaseEntitySchema


class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    full_name: str = Field(..., min_length=1, max_length=100, description="User's full name")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, description="User's password")


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    email: Optional[EmailStr] = Field(None, description="User's email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Unique username")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's full name")
    password: Optional[str] = Field(None, min_length=8, description="User's password")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")


class UserResponse(UserBase, BaseEntitySchema):
    """Schema for user response data."""
    pass

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    users: list[UserResponse]
    total: int
    skip: int = 0
    limit: int = 100


class UsersStatusResponse(BaseModel):
    """Response schema for users status."""
    message: str
