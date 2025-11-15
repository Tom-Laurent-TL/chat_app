# Scripts Directory

This directory contains utility scripts for the Chat App project.

## test_api.py

A comprehensive API testing script that demonstrates the main endpoints of the chat application.

**Features tested:**
- Health check endpoint
- User creation and management
- Conversation creation and retrieval
- Adding user participants to conversations
- Adding bot participants to conversations
- Retrieving conversations with mixed participant types
- Schema validation for polymorphic participants (users vs bots)

**Usage:**
```bash
# Make sure the server is running
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Run the test script
uv run python scripts/test_api.py
```

**What it demonstrates:**
This script showcases the fix for the schema validation issue where `ConversationParticipantResponse` needed to handle both user and bot participants with different field requirements. Users have emails, while bots have descriptions instead.

The script creates a conversation with both a human user and a bot participant, then retrieves the conversation to show that both participant types are properly serialized according to their respective schemas.