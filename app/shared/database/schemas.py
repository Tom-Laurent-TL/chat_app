"""
Shared schemas for database.
Reusable Pydantic models for database-related operations.
"""
from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


class DatabaseInfoResponse(BaseModel):
    """Response schema for database information."""
    message: str
    connection_info: Dict[str, Any]
    health: Dict[str, Any]


class HealthCheckResponse(BaseModel):
    """Response schema for database health check."""
    status: str = Field(..., description="Health status: 'healthy' or 'unhealthy'")
    database: Optional[str] = Field(None, description="Database connection status")
    error: Optional[str] = Field(None, description="Error message if unhealthy")


class ConnectionInfoResponse(BaseModel):
    """Response schema for database connection information."""
    database_url: str
    engine_type: str
    pool_size: int
    environment: str


# Base schemas for common entity fields
class BaseEntitySchema(BaseModel):
    """Base schema with common entity fields."""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


# Example shared schema (uncomment and modify as needed):
# class SharedExampleSchema(BaseEntitySchema):
#     name: str
#     description: Optional[str] = None
#     metadata: Optional[Dict[str, Any]] = None