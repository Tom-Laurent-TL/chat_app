from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.shared.database.service import get_db
from app.shared.routing import auto_discover_routers
from .service import UsersService
from .schemas import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, UsersStatusResponse
)

router = APIRouter(
    prefix="/users", 
    tags=["users"],
    dependencies=[Depends(get_db)]
)


@router.get("/status", response_model=UsersStatusResponse)
def get_status(db: Session = Depends(get_db)):
    """Get status of the users feature."""
    service = UsersService(db)
    return service.status()


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user."""
    service = UsersService(db)
    try:
        user = service.create_user(user_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=UserListResponse)
def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    db: Session = Depends(get_db)
):
    """List users with pagination."""
    service = UsersService(db)
    users = service.list_users(skip=skip, limit=limit)
    total = service.get_total_users()
    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get a user by ID."""
    service = UsersService(db)
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing user."""
    service = UsersService(db)
    try:
        user = service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete a user (soft delete)."""
    service = UsersService(db)
    if not service.delete_user(user_id):
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")


# Automatically mount sub-feature routers
auto_discover_routers(router, __file__, __package__)
