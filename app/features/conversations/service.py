"""
Service layer for conversations.
Encapsulates business logic and domain rules.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, insert, delete
from .entities import Conversation, conversation_participants
from .schemas import ConversationCreate, ConversationUpdate


class ConversationsService:
    """Handles logic for the conversations feature."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def create_conversation(self, conversation_data: ConversationCreate, created_by_id: int) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            title=conversation_data.title,
            description=conversation_data.description,
            created_by_id=created_by_id
        )
        self.db.add(conversation)
        self.db.flush()  # Get the conversation ID without committing

        # Add the creator as the first participant with 'owner' role
        self.db.execute(
            insert(conversation_participants).values(
                conversation_id=conversation.id,
                user_id=created_by_id,
                role='owner'
            )
        )

        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def add_user_participant(self, conversation_id: int, user_id: int, role: str = 'participant') -> bool:
        """Add a user as a participant to a conversation."""
        # Check if conversation exists
        conversation = self.get_conversation_by_id(conversation_id)
        if not conversation:
            return False

        # Check if user is already a participant
        existing = self.db.execute(
            conversation_participants.select().where(
                conversation_participants.c.conversation_id == conversation_id,
                conversation_participants.c.user_id == user_id
            )
        ).first()
        if existing:
            return True  # Already a participant

        # Add user as participant
        self.db.execute(
            insert(conversation_participants).values(
                conversation_id=conversation_id,
                user_id=user_id,
                role=role
            )
        )
        self.db.commit()
        return True

    def add_bot_participant(self, conversation_id: int, bot_id: int, role: str = 'participant') -> bool:
        """Add a bot as a participant to a conversation."""
        # Check if conversation exists
        conversation = self.get_conversation_by_id(conversation_id)
        if not conversation:
            return False

        # Check if bot is already a participant
        existing = self.db.execute(
            conversation_participants.select().where(
                conversation_participants.c.conversation_id == conversation_id,
                conversation_participants.c.bot_id == bot_id
            )
        ).first()
        if existing:
            return True  # Already a participant

        # Add bot as participant
        self.db.execute(
            insert(conversation_participants).values(
                conversation_id=conversation_id,
                bot_id=bot_id,
                role=role
            )
        )
        self.db.commit()
        return True

    def remove_user_participant(self, conversation_id: int, user_id: int) -> bool:
        """Remove a user from conversation participants."""
        result = self.db.execute(
            delete(conversation_participants).where(
                conversation_participants.c.conversation_id == conversation_id,
                conversation_participants.c.user_id == user_id
            )
        )
        self.db.commit()
        return True  # Assume success if no exception

    def remove_bot_participant(self, conversation_id: int, bot_id: int) -> bool:
        """Remove a bot from conversation participants."""
        result = self.db.execute(
            delete(conversation_participants).where(
                conversation_participants.c.conversation_id == conversation_id,
                conversation_participants.c.bot_id == bot_id
            )
        )
        self.db.commit()
        return True  # Assume success if no exception

    def list_conversations(self, skip: int = 0, limit: int = 100, user_id: int | None = None) -> list[Conversation]:
        """List conversations with pagination. Optionally filter by user_id."""
        query = self.db.query(Conversation).filter(Conversation.is_active == True)
        
        if user_id is not None:
            query = query.filter(Conversation.created_by_id == user_id)
        
        return (
            query
            .order_by(desc(Conversation.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_conversation_by_id(self, conversation_id: int) -> Conversation | None:
        """Get a conversation by ID."""
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.is_active == True)
            .first()
        )

    def update_conversation(self, conversation_id: int, conversation_data: ConversationUpdate) -> Conversation | None:
        """Update an existing conversation."""
        conversation = self.get_conversation_by_id(conversation_id)
        if not conversation:
            return None

        update_data = conversation_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(conversation, field, value)

        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def delete_conversation(self, conversation_id: int) -> bool:
        """Soft delete a conversation."""
        conversation = self.get_conversation_by_id(conversation_id)
        if not conversation:
            return False

        # Soft delete by setting is_active to False
        self.db.query(Conversation).filter(Conversation.id == conversation_id).update({"is_active": False})
        self.db.commit()
        return True

    def get_total_conversations(self, user_id: int | None = None) -> int:
        """Get total number of active conversations. Optionally filter by user_id."""
        query = self.db.query(Conversation).filter(Conversation.is_active == True)
        
        if user_id is not None:
            query = query.filter(Conversation.created_by_id == user_id)
        
        return query.count()

    def status(self) -> dict:
        """Return the operational status of this feature."""
        return {"message": "Feature conversations is ready!"}
