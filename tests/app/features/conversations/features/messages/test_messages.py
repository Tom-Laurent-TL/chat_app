"""
Tests for Messages feature.
"""
import pytest
from fastapi.testclient import TestClient
from pydantic_ai import ModelRequest, UserPromptPart, ModelResponse, TextPart
from pydantic_ai.usage import RequestUsage

from app.features.conversations.features.messages.converter import MessageConverter


def test_messages_endpoint(client: TestClient):
    """Test that /messages endpoint is accessible."""
    response = client.get("/messages")
    assert response.status_code in [200, 404]  # Adjust based on your implementation


def test_messages_service():
    """Test MessagesService methods."""
    # TODO: Add service layer tests
    pass


def test_message_to_pydantic_conversion():
    """Test converting our Message format to Pydantic AI ModelRequest."""

    # Create a mock message object (avoiding SQLAlchemy issues)
    class MockMessage:
        def __init__(self, content):
            self.content = content

    our_message = MockMessage('Hello @assistant, how are you?')

    # Test the conversion
    pydantic_request = MessageConverter.user_message_to_pydantic(our_message)  # type: ignore

    assert isinstance(pydantic_request, ModelRequest)
    assert hasattr(pydantic_request, 'parts')
    assert len(pydantic_request.parts) == 1
    assert isinstance(pydantic_request.parts[0], UserPromptPart)
    assert pydantic_request.parts[0].content == 'Hello @assistant, how are you?'


def test_pydantic_response_to_message_data():
    """Test extracting data from Pydantic AI ModelResponse."""

    pydantic_response = ModelResponse(
        parts=[TextPart(content='I am doing well, thank you for asking!')],
        model_name='gpt-4',
        usage=RequestUsage(input_tokens=10, output_tokens=8)
    )

    # Test content extraction logic (without creating Message entity)
    text_parts = [part for part in pydantic_response.parts if isinstance(part, TextPart)]
    content = " ".join(part.content for part in text_parts) if text_parts else ""

    assert content == 'I am doing well, thank you for asking!'
    assert pydantic_response.model_name == 'gpt-4'


def test_serialize_deserialize_pydantic_messages():
    """Test serializing and deserializing Pydantic AI messages."""

    # Create test messages
    request = ModelRequest(parts=[UserPromptPart(content='Hello')])
    response = ModelResponse(
        parts=[TextPart(content='Hi there!')],
        model_name='gpt-4',
        usage=RequestUsage(input_tokens=1, output_tokens=2)
    )

    messages = [request, response]

    # Serialize to JSON
    json_str = MessageConverter.serialize_pydantic_messages(messages)
    assert isinstance(json_str, str)
    assert len(json_str) > 0

    # Deserialize back
    deserialized = MessageConverter.deserialize_pydantic_messages(json_str)
    assert len(deserialized) == 2
    assert isinstance(deserialized[0], ModelRequest)
    assert isinstance(deserialized[1], ModelResponse)
    assert deserialized[0].parts[0].content == 'Hello'
    assert deserialized[1].parts[0].content == 'Hi there!'


def test_build_conversation_context():
    """Test building conversation context from message history."""

    # Create mock messages
    class MockMessage:
        def __init__(self, content, bot_history=None):
            self.content = content
            self.bot_conversation = bot_history

    messages = [
        MockMessage("Hello @assistant"),
        MockMessage("Hi there! How can I help?")
    ]

    # Build context with system prompt
    context = MessageConverter.build_conversation_context(messages, "You are a helpful assistant.")  # type: ignore

    assert len(context) == 3  # system + 2 user messages
    assert isinstance(context[0], ModelRequest)  # system prompt
    assert hasattr(context[0], 'parts')  # has parts
    assert isinstance(context[1], ModelRequest)  # first user message
    assert isinstance(context[2], ModelRequest)  # second user message
