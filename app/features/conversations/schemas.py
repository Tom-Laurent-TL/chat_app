"""
Pydantic schemas for conversations.
Define request/response models for conversation operations.
"""
from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, Field, ConfigDict
from app.shared.database.schemas import BaseEntitySchema


class ConversationBase(BaseModel):
    """Base schema for conversation data."""
    title: str = Field(..., min_length=1, max_length=200, description="Conversation title")
    description: Optional[str] = Field(None, max_length=500, description="Optional conversation description")


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""
    description: Optional[str] = Field(None, max_length=500, description="Optional conversation description")


class ConversationUpdate(BaseModel):
    """Schema for updating an existing conversation."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Conversation title")
    description: Optional[str] = Field(None, max_length=500, description="Optional conversation description")
    is_active: Optional[bool] = Field(None, description="Whether the conversation is active")


class UserParticipantResponse(BaseModel):
    """Schema for user participant information."""
    type: str = Field("user", description="Participant type")
    id: int
    username: str
    full_name: str
    email: str
    joined_at: datetime
    role: str

    model_config = ConfigDict(from_attributes=True)


class BotParticipantResponse(BaseModel):
    """Schema for bot participant information."""
    type: str = Field("bot", description="Participant type")
    id: int
    username: str  # Bot name used as username
    full_name: str  # Bot display name
    description: Optional[str] = None  # Bots have description instead of email
    joined_at: datetime
    role: str

    model_config = ConfigDict(from_attributes=True)


# Union type for participants
ConversationParticipantResponse = Union[UserParticipantResponse, BotParticipantResponse]


class ConversationResponse(ConversationBase, BaseEntitySchema):
    """Schema for conversation response data."""
    created_by_id: int = Field(..., description="ID of the user who created this conversation")
    participants: list[ConversationParticipantResponse] = Field(default_factory=list, description="List of conversation participants")

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """Schema for paginated conversation list response."""
    conversations: list[ConversationResponse]
    total: int
    skip: int = 0
    limit: int = 100


class ConversationsStatusResponse(BaseModel):
    """Response schema for conversations status."""
    message: str
