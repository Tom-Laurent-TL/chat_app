"""
Pydantic schemas for participants.
"""
from pydantic import BaseModel


class ParticipantsStatusResponse(BaseModel):
    """Response schema for participants status."""
    message: str
