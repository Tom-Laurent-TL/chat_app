"""
Service layer for users.
Encapsulates business logic and domain rules.
"""
import hashlib
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .entities import User
from .schemas import UserCreate, UserUpdate, UserResponse


class UsersService:
    """Handles business logic for user management."""

    def __init__(self, db: Optional[Session] = None):
        """Initialize service with optional database session."""
        self.db = db

    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self._hash_password(plain_password) == hashed_password

    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user entity

        Raises:
            ValueError: If user with email or username already exists
        """
        if not self.db:
            raise RuntimeError("Database session required for user operations")

        # Check if user already exists
        existing_user = self.db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        if existing_user:
            if existing_user.email == user_data.email:
                raise ValueError(f"User with email {user_data.email} already exists")
            else:
                raise ValueError(f"User with username {user_data.username} already exists")

        # Create new user
        hashed_password = self._hash_password(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Failed to create user due to database constraint violation")

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            user_id: User ID to retrieve

        Returns:
            User entity if found, None otherwise
        """
        if not self.db:
            raise RuntimeError("Database session required for user operations")

        return self.db.query(User).filter(User.id == user_id, User.is_active == True).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email: Email address to search for

        Returns:
            User entity if found, None otherwise
        """
        if not self.db:
            raise RuntimeError("Database session required for user operations")

        return self.db.query(User).filter(User.email == email, User.is_active == True).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.

        Args:
            username: Username to search for

        Returns:
            User entity if found, None otherwise
        """
        if not self.db:
            raise RuntimeError("Database session required for user operations")

        return self.db.query(User).filter(User.username == username, User.is_active == True).first()

    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        List users with pagination.

        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return

        Returns:
            List of active users
        """
        if not self.db:
            raise RuntimeError("Database session required for user operations")

        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Update an existing user.

        Args:
            user_id: ID of user to update
            user_data: Updated user data

        Returns:
            Updated user entity if found, None otherwise

        Raises:
            ValueError: If update would create duplicate email/username
        """
        if not self.db:
            raise RuntimeError("Database session required for user operations")

        user = self.get_user_by_id(user_id)
        if not user:
            return None

        # Check for conflicts if email or username are being updated
        update_data = user_data.model_dump(exclude_unset=True)
        if 'email' in update_data:
            existing = self.db.query(User).filter(
                User.email == update_data['email'],
                User.id != user_id
            ).first()
            if existing:
                raise ValueError(f"User with email {update_data['email']} already exists")

        if 'username' in update_data:
            existing = self.db.query(User).filter(
                User.username == update_data['username'],
                User.id != user_id
            ).first()
            if existing:
                raise ValueError(f"User with username {update_data['username']} already exists")

        # Hash password if provided
        if 'password' in update_data:
            update_data['hashed_password'] = self._hash_password(update_data.pop('password'))

        try:
            for key, value in update_data.items():
                setattr(user, key, value)

            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Failed to update user due to database constraint violation")

    def delete_user(self, user_id: int) -> bool:
        """
        Soft delete a user by setting is_active to False.

        Args:
            user_id: ID of user to delete

        Returns:
            True if user was deleted, False if not found
        """
        if not self.db:
            raise RuntimeError("Database session required for user operations")

        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        self.db.commit()
        return True

    def get_total_users(self) -> int:
        """
        Get total count of active users.

        Returns:
            Number of active users
        """
        if not self.db:
            raise RuntimeError("Database session required for user operations")

        return self.db.query(User).filter(User.is_active == True).count()

    def status(self) -> dict:
        """Return the operational status of this feature."""
        if self.db:
            try:
                total_users = self.get_total_users()
                return {
                    "message": "Users feature is ready!",
                    "database_connected": True,
                    "total_users": total_users
                }
            except Exception as e:
                return {
                    "message": "Users feature has database issues",
                    "database_connected": False,
                    "error": str(e)
                }
        else:
            return {
                "message": "Users feature is ready (no database session)",
                "database_connected": False,
                "total_users": 0
            }
