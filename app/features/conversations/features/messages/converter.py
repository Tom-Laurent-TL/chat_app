"""
Message conversion utilities for Pydantic AI integration.
Convert between our Message entities and Pydantic AI ModelMessage format.
"""

import json
from typing import List, Optional

from pydantic_ai import ModelMessage, ModelRequest, ModelResponse, UserPromptPart, TextPart, SystemPromptPart  # type: ignore
from pydantic_ai.messages import ModelMessagesTypeAdapter  # type: ignore
from pydantic_core import to_jsonable_python  # type: ignore

from .entities import Message


class MessageConverter:
    """Convert between our Message format and Pydantic AI ModelMessage format."""

    @staticmethod
    def serialize_pydantic_messages(messages: List[ModelMessage]) -> str:
        """Serialize Pydantic AI messages to JSON string for storage."""
        python_objects = to_jsonable_python(messages)
        return json.dumps(python_objects)

    @staticmethod
    def deserialize_pydantic_messages(json_str: str) -> List[ModelMessage]:
        """Deserialize JSON string back to Pydantic AI messages."""
        if not json_str:
            return []
        python_objects = json.loads(json_str)
        return ModelMessagesTypeAdapter.validate_python(python_objects)

    @staticmethod
    def user_message_to_pydantic(message: Message) -> ModelRequest:
        """Convert our user Message to Pydantic AI ModelRequest."""
        return ModelRequest(
            parts=[
                UserPromptPart(content=str(message.content))
            ]
        )

    @staticmethod
    def pydantic_response_to_message(response: ModelResponse, conversation_id: int, bot_user_id: int) -> Message:
        """Convert Pydantic AI ModelResponse to our Message format."""
        # Extract text content from response parts
        text_parts = [part for part in response.parts if isinstance(part, TextPart)]
        content = " ".join(part.content for part in text_parts) if text_parts else ""

        return Message(
            content=content,
            sender_id=bot_user_id,
            conversation_id=conversation_id,
            bot_conversation=None  # Bot responses don't need to store history
        )

    @staticmethod
    def get_conversation_history(message: Message) -> List[ModelMessage]:
        """Get Pydantic AI message history from a message."""
        if message.bot_conversation:  # type: ignore
            return MessageConverter.deserialize_pydantic_messages(message.bot_conversation)  # type: ignore
        return []

    @staticmethod
    def set_conversation_history(message: Message, history: List[ModelMessage]) -> None:
        """Set Pydantic AI message history on a message."""
        message.bot_conversation = MessageConverter.serialize_pydantic_messages(history)  # type: ignore

    @staticmethod
    def build_conversation_context(messages: List[Message], system_prompt: Optional[str] = None) -> List[ModelMessage]:
        """Build conversation context from message history for Pydantic AI."""

        context = []

        # Add system prompt if provided
        if system_prompt:
            context.append(ModelRequest(parts=[SystemPromptPart(content=system_prompt)]))

        # Convert our messages to Pydantic AI format
        for message in messages:
            if message.bot_conversation:  # type: ignore
                # If message has stored Pydantic AI history, use it
                context.extend(MessageConverter.get_conversation_history(message))
            else:
                # Otherwise convert our simple message format
                context.append(MessageConverter.user_message_to_pydantic(message))

        return context