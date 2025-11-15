"""
Entities for messages.
Define ORM or domain models here.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.shared.database.entities import BaseEntity


class Message(BaseEntity):
    """Message entity representing a chat message in a conversation."""

    __tablename__ = "messages"

    content = Column(String(2000), nullable=False)  # Message content (supports @mentions)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)

    # Polymorphic sender: can be either a user or a bot
    sender_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    sender_bot_id = Column(Integer, ForeignKey("bots.id"), nullable=True, index=True)

    # For bot conversations: store serialized Pydantic AI message history
    # This allows bots to maintain conversation context across multiple interactions
    bot_conversation = Column(Text, nullable=True)  # JSON serialized ModelMessages

    # Relationships
    sender_user = relationship("User", back_populates="messages", foreign_keys=[sender_user_id])
    sender_bot = relationship("Bot", foreign_keys=[sender_bot_id])
    conversation = relationship("Conversation", back_populates="messages")
