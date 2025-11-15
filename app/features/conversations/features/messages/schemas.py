"""
Pydantic schemas for messages.
Define request/response models for message operations.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.shared.database.schemas import BaseEntitySchema


class MessageBase(BaseModel):
    """Base schema for message data."""
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")
    conversation_id: int = Field(..., description="ID of the conversation this message belongs to")
    sender_user_id: Optional[int] = Field(None, description="ID of the user sending the message (if sent by user)")
    sender_bot_id: Optional[int] = Field(None, description="ID of the bot sending the message (if sent by bot)")


class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")
    conversation_id: int = Field(..., description="ID of the conversation this message belongs to")

    model_config = ConfigDict(from_attributes=True)


class MessageUpdate(BaseModel):
    """Schema for updating an existing message."""
    content: Optional[str] = Field(None, min_length=1, max_length=2000, description="Updated message content")
    is_active: Optional[bool] = Field(None, description="Whether the message is active (soft delete)")


class MessageResponse(MessageBase, BaseEntitySchema):
    """Response schema for message data including common entity fields."""

    model_config = ConfigDict(from_attributes=True)


class MessageWithSenderResponse(BaseEntitySchema):
    """Response schema for message with sender information."""
    content: str
    conversation_id: int
    sender_user_id: Optional[int] = None
    sender_bot_id: Optional[int] = None
    sender_username: Optional[str] = None  # For user senders
    sender_display_name: Optional[str] = None  # For bot senders
    sender_type: str  # "user" or "bot"

    model_config = ConfigDict(from_attributes=True)


class MessagesStatusResponse(BaseModel):
    """Response schema for messages status."""
    message: str
