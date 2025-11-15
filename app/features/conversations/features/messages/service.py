"""
Service layer for messages.
Encapsulates business logic and domain rules.
"""
from typing import List, Optional, Tuple
import re
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .entities import Message
from .schemas import MessageCreate, MessageUpdate, MessageResponse, MessageWithSenderResponse
from .converter import MessageConverter


class MessagesService:
    """Handles logic for the messages feature."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    async def create_message(self, message_data: MessageCreate, sender_user_id: Optional[int] = None, sender_bot_id: Optional[int] = None) -> Message:
        """Create a new message."""
        if not sender_user_id and not sender_bot_id:
            raise ValueError("Either sender_user_id or sender_bot_id must be provided")
        if sender_user_id and sender_bot_id:
            raise ValueError("Cannot specify both sender_user_id and sender_bot_id")

        message = Message(
            content=message_data.content,
            sender_user_id=sender_user_id,
            sender_bot_id=sender_bot_id,
            conversation_id=message_data.conversation_id
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        # Only handle bot triggers for user messages (not bot messages to avoid loops)
        if sender_user_id:
            await self._handle_bot_triggers(message)

        return message

    async def _handle_bot_triggers(self, message: Message) -> None:
        """Handle bot triggers for a newly created message."""
        # Import services for trigger detection and response generation
        from app.shared.trigger.service import BotTriggerService
        from app.shared.agents.service import AgentService

        # Initialize services
        bot_trigger_service = BotTriggerService(self.db)
        agent_service = AgentService(self.db)

        # STEP 1: Detect if bot should be triggered (pure detection logic)
        trigger_info = bot_trigger_service.detect_triggers(str(message.content))

        if not trigger_info:
            return  # No bot should respond

        # STEP 2: Build full conversation context using the converter
        # Get recent messages for context (including the current message)
        context_messages = self.get_recent_conversation_context(message.conversation_id, limit=10)  # type: ignore
        # Add the current message to the context
        full_context_messages = context_messages + [message]

        # Convert to Pydantic AI message history format
        from .converter import MessageConverter
        message_history = MessageConverter.build_conversation_context(
            messages=full_context_messages,
            system_prompt=trigger_info['bot_config']['system_prompt']
        )

        # STEP 3: Generate response using agent service with full message history
        response_text = await agent_service.generate_bot_response(
            bot_config=trigger_info['bot_config'],
            message_history=message_history
        )

        # STEP 4: Create bot response message
        self.create_bot_message(
            content=response_text,
            conversation_id=message.conversation_id,  # type: ignore
            bot_id=trigger_info['bot_config']['id'],
            conversation_history=None  # Could be populated with actual history
        )

    def get_message(self, message_id: int) -> Optional[Message]:
        """Get a message by ID."""
        return self.db.query(Message).filter(Message.id == message_id).first()

    def get_conversation_messages(self, conversation_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        """Get messages for a conversation, ordered by newest first."""
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id, Message.is_active == True)
            .order_by(desc(Message.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_conversation_messages_with_sender(self, conversation_id: int, limit: int = 50, offset: int = 0) -> List[MessageWithSenderResponse]:
        """Get messages for a conversation with sender information."""
        from sqlalchemy.orm import joinedload

        messages = (
            self.db.query(Message)
            .options(joinedload(Message.sender_user), joinedload(Message.sender_bot))
            .filter(Message.conversation_id == conversation_id, Message.is_active == True)
            .order_by(desc(Message.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

        # Convert to response schema with sender info
        result = []
        for message in messages:
            sender_type = "user" if message.sender_user_id is not None else "bot"
            sender_username = message.sender_user.username if message.sender_user else None
            sender_display_name = message.sender_bot.display_name if message.sender_bot else None

            result.append(MessageWithSenderResponse.model_validate({
                **message.__dict__,
                'sender_user_id': message.sender_user_id,
                'sender_bot_id': message.sender_bot_id,
                'sender_username': sender_username,
                'sender_display_name': sender_display_name,
                'sender_type': sender_type
            }))
        return result

    def update_message(self, message_id: int, update_data: MessageUpdate, user_id: int) -> Optional[Message]:
        """Update a message (only by the sender)."""
        message = self.get_message(message_id)
        if not message or message.sender_user_id != user_id:  # type: ignore
            return None

        if update_data.content is not None:
            message.content = update_data.content  # type: ignore
        if update_data.is_active is not None:
            message.is_active = update_data.is_active  # type: ignore

        self.db.commit()
        self.db.refresh(message)
        return message

    def delete_message(self, message_id: int, user_id: int) -> bool:
        """Soft delete a message (only by the sender)."""
        message = self.get_message(message_id)
        if not message or message.sender_user_id != user_id:  # type: ignore
            return False

        message.is_active = False  # type: ignore
        self.db.commit()
        return True

    def get_user_messages(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        """Get messages sent by a specific user."""
        return (
            self.db.query(Message)
            .filter(Message.sender_user_id == user_id, Message.is_active == True)
            .order_by(desc(Message.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def parse_mentions(self, content: str) -> List[str]:
        """Parse @mentions from message content and return list of mentioned usernames."""
        # Find all @username patterns (alphanumeric, underscore, dash)
        mention_pattern = r'@([a-zA-Z0-9_-]+)'
        mentions = re.findall(mention_pattern, content)
        return list(set(mentions))  # Remove duplicates

    def get_recent_conversation_context(self, conversation_id: int, limit: int = 10) -> List[Message]:
        """Get recent messages for conversation context (for bot interactions)."""
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id, Message.is_active == True)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .all()
        )[::-1]  # Reverse to get chronological order (oldest first)

    def create_bot_message(self, content: str, conversation_id: int, bot_id: int,
                          conversation_history: Optional[List] = None) -> Message:
        """Create a message from a bot with optional conversation history."""
        message = Message(
            content=content,
            sender_bot_id=bot_id,
            conversation_id=conversation_id,
            bot_conversation=MessageConverter.serialize_pydantic_messages(conversation_history) if conversation_history else None
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def status(self) -> dict:
        """Return the operational status of this feature."""
        return {"message": "Feature messages is ready!"}
