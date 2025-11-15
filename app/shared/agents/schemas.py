"""
Shared schemas for agents.
Reusable Pydantic models for features.
"""
from pydantic import BaseModel
from typing import List, Optional


class BotTriggerRequest(BaseModel):
    """Request schema for bot trigger evaluation."""
    message_content: str
    mentions: List[str]
    conversation_id: int


class BotTriggerResponse(BaseModel):
    """Response schema for bot trigger evaluation."""
    should_trigger: bool
    bot_mentioned: bool


class BotResponseRequest(BaseModel):
    """Request schema for generating bot responses."""
    user_message: str
    conversation_context: Optional[List[str]] = None


class BotResponseResponse(BaseModel):
    """Response schema for bot responses."""
    response: str
    success: bool
    error_message: Optional[str] = None


class AgentsInfoResponse(BaseModel):
    """Response schema for agents info."""
    message: str
