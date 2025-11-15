# 🧩 Feature: Conversations

This feature is part of the Octopus architecture and provides conversation management functionality.

## Overview

The conversations feature allows users to create and manage chat conversations. Each conversation has a title, optional description, and is associated with the user who created it. Conversations support soft deletion and full CRUD operations.

## API Endpoints

### Status
- `GET /conversations/status` - Get feature status

### Conversations CRUD
- `POST /conversations/` - Create a new conversation
  - Body: `{"title": "string", "description": "string?"}`
  - Query params (for testing): `created_by_id` (optional)
  - Returns: Created conversation with ID and timestamps

- `GET /conversations/` - List conversations with pagination
  - Query params: `skip` (default: 0), `limit` (default: 100, max: 1000), `user_id` (optional filter)
  - Returns: `{"conversations": [...], "total": number, "skip": number, "limit": number}`

- `GET /conversations/{id}` - Get a specific conversation by ID
  - Returns: Conversation details or 404 if not found

- `PUT /conversations/{id}` - Update a conversation
  - Body: `{"title": "string?", "description": "string?", "is_active": "boolean?"}`
  - Returns: Updated conversation or 404 if not found

- `DELETE /conversations/{id}` - Soft delete a conversation
  - Returns: 204 No Content or 404 if not found

## Data Model

### Conversation Entity
- `id`: Primary key (auto-generated)
- `title`: Conversation title (required, 1-200 chars)
- `description`: Optional description (max 500 chars)
- `created_by_id`: Foreign key to user who created the conversation
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `is_active`: Soft delete flag

### Relationships
- `created_by`: Relationship to User entity
- `User.conversations`: Back-reference to user's conversations

## Structure
- `router.py` → HTTP routes and sub-feature mounting
- `service.py` → business logic class (ConversationsService)
- `entities.py` → domain entities
- `schemas.py` → Pydantic schemas
- `features/` → recursive child features
- `shared/` → recursive shared utilities

Refer to `/docs` for architecture details.
