# 🧩 Feature: Messages

This feature is part of the Octopus architecture and provides message CRUD operations for conversations.

## Overview
The Messages feature allows users to create, read, update, and delete messages within conversations. It serves as the foundation for conversation-based communication and will later support AI bot interactions through @mention triggering.

## Structure
- `router.py` → HTTP routes for message CRUD operations
- `service.py` → business logic class (MessagesService)
- `entities.py` → Message ORM model with relationships
- `schemas.py` → Pydantic schemas for API validation
- `features/` → recursive child features
- `shared/` → recursive shared utilities

## API Endpoints

### Message Operations
- `POST /messages/` - Create a new message
- `GET /messages/{message_id}` - Get a specific message
- `PUT /messages/{message_id}` - Update a message (sender only)
- `DELETE /messages/{message_id}` - Soft delete a message (sender only)

### Conversation Messages
- `GET /messages/conversation/{conversation_id}` - Get messages for a conversation (with sender info)

### User Messages
- `GET /messages/user/{user_id}` - Get messages sent by a user

## Database Schema

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    content VARCHAR(2000) NOT NULL,
    sender_id INTEGER REFERENCES users(id),
    conversation_id INTEGER REFERENCES conversations(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    bot_conversation_history TEXT  -- Serialized Pydantic AI messages for bot interactions
);
```

## AI Bot Integration

The Messages feature supports AI bot integration through Pydantic AI:

### @Mention Parsing
- Messages are automatically parsed for `@username` mentions
- `parse_mentions()` extracts bot usernames from message content
- Supports triggering AI agents when bots are mentioned

### Conversation Context
- `get_recent_conversation_context()` provides recent messages for bot context
- `build_conversation_context()` converts our messages to Pydantic AI format
- Maintains conversation history across bot interactions

### Bot Message Creation
- `create_bot_message()` creates messages from bots with conversation history
- Stores serialized Pydantic AI messages for complex bot interactions
- Supports tool calls, multi-turn conversations, and rich responses

### Message Conversion
The `converter.py` module provides utilities to:
- Convert between our Message format and Pydantic AI ModelMessage format
- Serialize/deserialize conversation history for storage
- Build conversation context for AI agents

## Relationships
- **Message → User**: `sender` relationship (many-to-one)
- **Message → Conversation**: `conversation` relationship (many-to-one)
- **Conversation → Messages**: `messages` relationship (one-to-many)
- **User → Messages**: `messages` relationship (one-to-many)

## Future Enhancements
- **@Mention Parsing**: Detect and trigger bot mentions
- **Real-time Updates**: WebSocket support for live messaging
- **Message Reactions**: Like, emoji reactions
- **Message Threads**: Nested conversation threads
- **File Attachments**: Support for media uploads

Refer to `/docs` for architecture details.
