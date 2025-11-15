"""
Shared schemas for tools.
Reusable Pydantic models for features.
"""
from pydantic import BaseModel


class ToolsInfoResponse(BaseModel):
    """Response schema for tools info."""
    message: str


# Example:
# class SharedExampleSchema(BaseModel):
#     id: int
#     name: str
