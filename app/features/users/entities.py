"""
Entities for users.
Define ORM models for user management.
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.shared.database.entities import BaseEntity


class User(BaseEntity):
    """
    User entity representing a system user.

    Inherits common fields from BaseEntity:
    - id: Primary key
    - created_at: Creation timestamp
    - updated_at: Last update timestamp
    - is_active: Soft delete flag
    """
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationship to conversations created by this user
    owned_conversations = relationship("Conversation", back_populates="created_by", foreign_keys="Conversation.created_by_id")

    # Many-to-many relationship with conversations they're participating in
    conversations = relationship(
        "Conversation",
        secondary="conversation_participants",
        back_populates="user_participants",
        lazy="selectin",
        overlaps="bot_participants",
        primaryjoin="and_(User.id == conversation_participants.c.user_id, conversation_participants.c.user_id != None)",
        secondaryjoin="Conversation.id == conversation_participants.c.conversation_id"
    )

    # One-to-many relationship with messages sent by this user
    messages = relationship("Message", back_populates="sender_user", cascade="all, delete-orphan")

    def __repr__(self):
        """String representation of User."""
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
