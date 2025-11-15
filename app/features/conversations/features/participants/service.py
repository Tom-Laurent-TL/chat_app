"""
Service layer for participants.
Encapsulates business logic and domain rules.
"""
from sqlalchemy.orm import Session
from sqlalchemy import insert
from app.features.conversations.entities import conversation_participants


class ParticipantsService:
    """Handles logic for the participants feature."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def add_participant(self, conversation_id: int, user_id: int, role: str = 'participant') -> bool:
        """Add a participant to a conversation."""
        # Check if user is already a participant
        existing = self.db.execute(
            conversation_participants.select().where(
                conversation_participants.c.conversation_id == conversation_id,
                conversation_participants.c.user_id == user_id
            )
        ).first()

        if existing:
            return False  # Already a participant

        # Add the participant
        self.db.execute(
            insert(conversation_participants).values(
                conversation_id=conversation_id,
                user_id=user_id,
                role=role
            )
        )
        self.db.commit()
        return True

    def add_bot_participant(self, conversation_id: int, bot_id: int, role: str = 'bot') -> bool:
        """Add a bot as a participant to a conversation."""
        # Check if bot is already a participant
        existing = self.db.execute(
            conversation_participants.select().where(
                conversation_participants.c.conversation_id == conversation_id,
                conversation_participants.c.bot_id == bot_id
            )
        ).first()

        if existing:
            return False  # Already a participant

        # Add the bot participant
        self.db.execute(
            insert(conversation_participants).values(
                conversation_id=conversation_id,
                bot_id=bot_id,
                role=role
            )
        )
        self.db.commit()
        return True

    def remove_bot_participant(self, conversation_id: int, bot_id: int) -> bool:
        """Remove a bot participant from a conversation."""
        result = self.db.execute(
            conversation_participants.delete().where(
                conversation_participants.c.conversation_id == conversation_id,
                conversation_participants.c.bot_id == bot_id
            )
        )
        self.db.commit()
        return True  # Assume success if no exception

    def remove_participant(self, conversation_id: int, user_id: int) -> bool:
        """Remove a user participant from a conversation."""
        # Check if the participant exists first
        existing = self.db.execute(
            conversation_participants.select().where(
                conversation_participants.c.conversation_id == conversation_id,
                conversation_participants.c.user_id == user_id
            )
        ).first()

        if not existing:
            return False  # Participant doesn't exist

        # Remove the participant
        self.db.execute(
            conversation_participants.delete().where(
                conversation_participants.c.conversation_id == conversation_id,
                conversation_participants.c.user_id == user_id
            )
        )
        self.db.commit()
        return True

    def get_participants(self, conversation_id: int) -> list[dict]:
        """Get all participants (users and bots) for a conversation."""
        from app.features.users.entities import User
        from app.features.bots.entities import Bot

        # Get user participants
        user_result = self.db.execute(
            conversation_participants.select()
            .where(
                conversation_participants.c.conversation_id == conversation_id,
                conversation_participants.c.user_id != None
            )
            .join(User, conversation_participants.c.user_id == User.id)
            .add_columns(
                User.id,
                User.username,
                User.full_name,
                User.email,
                conversation_participants.c.joined_at,
                conversation_participants.c.role
            )
        ).all()

        # Get bot participants
        bot_result = self.db.execute(
            conversation_participants.select()
            .where(
                conversation_participants.c.conversation_id == conversation_id,
                conversation_participants.c.bot_id != None
            )
            .join(Bot, conversation_participants.c.bot_id == Bot.id)
            .add_columns(
                Bot.id,
                Bot.name,
                Bot.display_name,
                Bot.description,
                conversation_participants.c.joined_at,
                conversation_participants.c.role
            )
        ).all()

        participants = []

        # Add users
        for row in user_result:
            participants.append({
                'type': 'user',
                'id': row.id,
                'username': row.username,
                'full_name': row.full_name,
                'email': row.email,
                'joined_at': row.joined_at,
                'role': row.role
            })

        # Add bots
        for row in bot_result:
            participants.append({
                'type': 'bot',
                'id': row.id,
                'username': row.name,  # Use name as username for bots
                'full_name': row.display_name,
                'description': row.description,
                'joined_at': row.joined_at,
                'role': row.role
            })

        return participants

    def is_participant(self, conversation_id: int, user_id: int) -> bool:
        """Check if a user is a participant in a conversation."""
        result = self.db.execute(
            conversation_participants.select().where(
                conversation_participants.c.conversation_id == conversation_id,
                conversation_participants.c.user_id == user_id
            )
        ).first()
        return result is not None

    def is_bot_participant(self, conversation_id: int, bot_id: int) -> bool:
        """Check if a bot is a participant in a conversation."""
        result = self.db.execute(
            conversation_participants.select().where(
                conversation_participants.c.conversation_id == conversation_id,
                conversation_participants.c.bot_id == bot_id
            )
        ).first()
        return result is not None

    def status(self) -> dict:
        """Return the operational status of this feature."""
        return {"message": "Feature participants is ready!"}
