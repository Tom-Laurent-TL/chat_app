"""
Shared schemas for config.
Reusable Pydantic models for features.
"""
from pydantic import BaseModel


class ConfigInfoResponse(BaseModel):
    """Response schema for config info."""
    message: str


# Example:
# class SharedExampleSchema(BaseModel):
#     id: int
#     name: str
