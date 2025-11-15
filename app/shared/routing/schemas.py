"""
Shared schemas for routing.
Reusable Pydantic models for features.
"""
from pydantic import BaseModel


class RoutingInfoResponse(BaseModel):
    """Response schema for routing info."""
    message: str


# Example:
# class SharedExampleSchema(BaseModel):
#     id: int
#     name: str
