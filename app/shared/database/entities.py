"""
Shared entities for database.
Define reusable ORM models and base classes.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .service import Base


class BaseEntity(Base):
    """
    Base entity with common fields for all database models.

    Provides automatic timestamps and ID field.
    All feature entities should inherit from this class.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


# Example shared entity (uncomment and modify as needed):
# class SharedExample(BaseEntity):
#     __tablename__ = "shared_examples"
#
#     name = Column(String, nullable=False, index=True)
#     description = Column(String)
#     metadata = Column(JSON)  # For flexible data storage
