"""
Entities for bots.
Define ORM or domain models here.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from app.shared.database.entities import BaseEntity


class Bot(BaseEntity):
    """Bot entity representing an AI assistant in the system."""

    __tablename__ = "bots"

    name = Column(String(100), nullable=False, unique=True, index=True)  # Bot username/handle
    display_name = Column(String(200), nullable=False)  # Human-readable name
    description = Column(Text, nullable=True)  # Bot description
    avatar_url = Column(String(500), nullable=True)  # Bot avatar image URL

    # Bot configuration
    model_name = Column(String(100), nullable=False, default="gpt-4o-mini")  # AI model to use
    provider = Column(String(50), nullable=False, default="openai")  # AI provider (openai, azure, etc.)
    system_prompt = Column(Text, nullable=True)  # System prompt for the bot
    temperature = Column(Integer, nullable=False, default=70)  # Temperature * 100 (0-200)
    max_tokens = Column(Integer, nullable=False, default=1000)  # Max response tokens

    # Bot settings
    is_active = Column(Boolean, nullable=False, default=True)  # Whether bot is enabled
    is_public = Column(Boolean, nullable=False, default=False)  # Whether bot can be used by anyone
    auto_trigger = Column(Boolean, nullable=False, default=True)  # Whether bot responds to @mentions

    # API configuration (stored encrypted in production)
    api_key = Column(String(500), nullable=True)  # API key for the AI service
    api_base_url = Column(String(500), nullable=True)  # Custom API base URL (for OpenAI-style providers)

    # Metadata
    config = Column(JSON, nullable=True)  # Additional configuration as JSON
    created_by_id = Column(Integer, nullable=False)  # User who created this bot

    # Relationships
    # messages = relationship("Message", back_populates="bot")  # Bot's messages (if we add this later)
