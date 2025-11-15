"""
Pydantic schemas for bots.
"""
from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from app.shared.database.schemas import BaseEntitySchema


class BotBase(BaseModel):
    """Base schema for bot data."""
    name: str = Field(..., min_length=1, max_length=100, description="Bot username/handle (unique)")
    display_name: str = Field(..., min_length=1, max_length=200, description="Human-readable bot name")
    description: Optional[str] = Field(None, max_length=1000, description="Bot description")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Bot avatar image URL")

    # Bot configuration
    model_name: str = Field("gpt-4o-mini", min_length=1, max_length=100, description="AI model to use")
    provider: str = Field("openai", min_length=1, max_length=50, description="AI provider (openai, azure, deepseek, etc.)")
    system_prompt: Optional[str] = Field(None, max_length=5000, description="System prompt for the bot")
    temperature: int = Field(70, ge=0, le=200, description="Temperature * 100 (0-200)")
    max_tokens: int = Field(1000, ge=1, le=4000, description="Max response tokens")

    # Bot settings
    is_active: bool = Field(True, description="Whether bot is enabled")
    is_public: bool = Field(False, description="Whether bot can be used by anyone")
    auto_trigger: bool = Field(True, description="Whether bot responds to @mentions")

    # API configuration
    api_key: Optional[str] = Field(None, max_length=500, description="API key for the AI service")
    api_base_url: Optional[str] = Field(None, max_length=500, description="Custom API base URL")

    # Additional config
    config: Optional[Dict[str, Any]] = Field(None, description="Additional configuration as JSON")


class BotCreate(BaseModel):
    """Schema for creating a new bot."""
    name: str = Field(..., min_length=1, max_length=100, description="Bot username/handle (unique)")
    display_name: str = Field(..., min_length=1, max_length=200, description="Human-readable bot name")
    description: Optional[str] = Field(None, max_length=1000, description="Bot description")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Bot avatar image URL")

    # Bot configuration
    model_name: str = Field("gpt-4o-mini", min_length=1, max_length=100, description="AI model to use")
    provider: str = Field("openai", min_length=1, max_length=50, description="AI provider (openai, azure, deepseek, etc.)")
    system_prompt: Optional[str] = Field(None, max_length=5000, description="System prompt for the bot")
    temperature: int = Field(70, ge=0, le=200, description="Temperature * 100 (0-200)")
    max_tokens: int = Field(1000, ge=1, le=4000, description="Max response tokens")

    # Bot settings
    is_active: bool = Field(True, description="Whether bot is enabled")
    is_public: bool = Field(False, description="Whether bot can be used by anyone")
    auto_trigger: bool = Field(True, description="Whether bot responds to @mentions")

    # API configuration
    api_key: Optional[str] = Field(None, max_length=500, description="API key for the AI service")
    api_base_url: Optional[str] = Field(None, max_length=500, description="Custom API base URL")

    # Additional config
    config: Optional[Dict[str, Any]] = Field(None, description="Additional configuration as JSON")

    model_config = ConfigDict(from_attributes=True)


class BotUpdate(BaseModel):
    """Schema for updating an existing bot."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Bot username/handle (unique)")
    display_name: Optional[str] = Field(None, min_length=1, max_length=200, description="Human-readable bot name")
    description: Optional[str] = Field(None, max_length=1000, description="Bot description")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Bot avatar image URL")

    # Bot configuration
    model_name: Optional[str] = Field(None, min_length=1, max_length=100, description="AI model to use")
    provider: Optional[str] = Field(None, min_length=1, max_length=50, description="AI provider (openai, azure, deepseek, etc.)")
    system_prompt: Optional[str] = Field(None, max_length=5000, description="System prompt for the bot")
    temperature: Optional[int] = Field(None, ge=0, le=200, description="Temperature * 100 (0-200)")
    max_tokens: Optional[int] = Field(None, ge=1, le=4000, description="Max response tokens")

    # Bot settings
    is_active: Optional[bool] = Field(None, description="Whether bot is enabled")
    is_public: Optional[bool] = Field(None, description="Whether bot can be used by anyone")
    auto_trigger: Optional[bool] = Field(None, description="Whether bot responds to @mentions")

    # API configuration
    api_key: Optional[str] = Field(None, max_length=500, description="API key for the AI service")
    api_base_url: Optional[str] = Field(None, max_length=500, description="Custom API base URL")

    # Additional config
    config: Optional[Dict[str, Any]] = Field(None, description="Additional configuration as JSON")


class BotResponse(BotBase, BaseEntitySchema):
    """Response schema for bot data including common entity fields."""
    created_by_id: int = Field(..., description="User who created this bot")

    model_config = ConfigDict(from_attributes=True)


class BotListResponse(BaseModel):
    """Response schema for listing bots."""
    bots: list[BotResponse]
    total: int
    skip: int
    limit: int


class BotsStatusResponse(BaseModel):
    """Response schema for bots status."""
    message: str
    total_bots: int
    active_bots: int
