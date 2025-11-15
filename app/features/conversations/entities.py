"""
Entities for conversations.
Define ORM or domain models here.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.shared.database.entities import BaseEntity


# Association table for conversation participants (many-to-many with users and bots)
conversation_participants = Table(
    'conversation_participants',
    BaseEntity.metadata,
    Column('conversation_id', Integer, ForeignKey('conversations.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True, nullable=True),
    Column('bot_id', Integer, ForeignKey('bots.id'), primary_key=True, nullable=True),
    Column('joined_at', DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False),
    Column('role', String(50), default='participant', nullable=False),  # 'owner', 'participant', etc.
)


class Conversation(BaseEntity):
    """Conversation entity representing a chat conversation."""

    __tablename__ = "conversations"

    title = Column(String(200), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Relationship to the user who created this conversation
    created_by = relationship("User", back_populates="owned_conversations", foreign_keys=[created_by_id])

    # Many-to-many relationship with participants (users and bots)
    user_participants = relationship(
        "User",
        secondary=conversation_participants,
        back_populates="conversations",
        lazy="selectin",
        primaryjoin="and_(Conversation.id == conversation_participants.c.conversation_id, conversation_participants.c.user_id != None)",
        secondaryjoin="User.id == conversation_participants.c.user_id"
    )

    bot_participants = relationship(
        "Bot",
        secondary=conversation_participants,
        lazy="selectin",
        overlaps="user_participants",
        primaryjoin="and_(Conversation.id == conversation_participants.c.conversation_id, conversation_participants.c.bot_id != None)",
        secondaryjoin="Bot.id == conversation_participants.c.bot_id"
    )

    # Combined participants property for convenience
    @property
    def participants(self):
        """Get all participants (users and bots) as a combined list."""
        from app.features.bots.entities import Bot
        result = []
        # Add users
        for user in self.user_participants:
            result.append({"type": "user", "entity": user})
        # Add bots
        for bot in self.bot_participants:
            result.append({"type": "bot", "entity": bot})
        return result

    # One-to-many relationship with messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}', created_by_id={self.created_by_id})>"
