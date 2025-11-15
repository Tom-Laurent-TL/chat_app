#!/usr/bin/env python3
"""
Data Seeding Script for Chat App

Creates sample data for development and testing:
- Users with different roles
- Bots with various configurations
- Conversations with participants
- Messages demonstrating the chat functionality

Usage:
    uv run python scripts/seed_data.py [options]

Options:
    --users     - Create sample users
    --bots      - Create sample bots
    --conversations - Create sample conversations
    --messages  - Create sample messages
    --all       - Create all sample data (default)
    --clean     - Clean existing data before seeding
    --confirm   - Confirm destructive operations

Environment Variables:
    DATABASE_URL - Database connection URL (uses app settings if not set)
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import random
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.shared.database.service import SessionLocal
from app.features.users.entities import User
from app.features.bots.entities import Bot
from app.features.conversations.entities import Conversation
from app.features.conversations.features.messages.entities import Message
from app.features.conversations.entities import conversation_participants
from sqlalchemy.orm import Session


class DataSeeder:
    """Data seeding utilities for the chat application."""

    def __init__(self):
        """Initialize the data seeder."""
        self.db: Session = SessionLocal()
        self.created_users: List[User] = []
        self.created_bots: List[Bot] = []
        self.created_conversations: List[Conversation] = []

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.db.close()

    def clean_existing_data(self) -> Dict[str, Any]:
        """Clean existing data."""
        try:
            # Delete in reverse dependency order
            self.db.query(Message).delete()
            self.db.execute(conversation_participants.delete())
            self.db.query(Conversation).delete()
            self.db.query(Bot).delete()
            self.db.query(User).delete()
            self.db.commit()

            return {"status": "cleaned", "message": "Existing data cleaned"}
        except Exception as e:
            self.db.rollback()
            return {"status": "failed", "error": str(e)}

    def create_sample_users(self) -> Dict[str, Any]:
        """Create sample users."""
        try:
            users_data = [
                {
                    "username": "alice_dev",
                    "email": "alice@example.com",
                    "full_name": "Alice Developer",
                    "hashed_password": "hashed_password_123",  # In real app, this would be properly hashed
                    "is_active": True
                },
                {
                    "username": "bob_manager",
                    "email": "bob@example.com",
                    "full_name": "Bob Manager",
                    "hashed_password": "hashed_password_456",
                    "is_active": True
                },
                {
                    "username": "charlie_user",
                    "email": "charlie@example.com",
                    "full_name": "Charlie User",
                    "hashed_password": "hashed_password_789",
                    "is_active": True
                },
                {
                    "username": "diana_admin",
                    "email": "diana@example.com",
                    "full_name": "Diana Admin",
                    "hashed_password": "hashed_password_admin",
                    "is_active": True
                }
            ]

            for user_data in users_data:
                user = User(**user_data)
                self.db.add(user)
                self.created_users.append(user)

            self.db.commit()

            return {
                "status": "created",
                "count": len(users_data),
                "users": [u.username for u in self.created_users]
            }

        except Exception as e:
            self.db.rollback()
            return {"status": "failed", "error": str(e)}

    def create_sample_bots(self) -> Dict[str, Any]:
        """Create sample bots."""
        try:
            if not self.created_users:
                return {"status": "failed", "error": "No users available. Create users first."}

            bots_data = [
                {
                    "name": "assistant_bot",
                    "display_name": "AI Assistant",
                    "description": "A helpful AI assistant for general tasks",
                    "model_name": "gpt-3.5-turbo",
                    "provider": "openai",
                    "system_prompt": "You are a helpful AI assistant. Be friendly and informative.",
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "is_active": True,
                    "is_public": True,
                    "auto_trigger": True,
                    "created_by_id": self.created_users[0].id,  # Alice
                    "config": {"temperature": 0.7, "max_tokens": 1000}
                },
                {
                    "name": "code_reviewer",
                    "display_name": "Code Review Bot",
                    "description": "Specialized bot for code review and suggestions",
                    "model_name": "gpt-4",
                    "provider": "openai",
                    "system_prompt": "You are an expert code reviewer. Provide constructive feedback on code quality, best practices, and potential improvements.",
                    "temperature": 0.3,
                    "max_tokens": 2000,
                    "is_active": True,
                    "is_public": False,
                    "auto_trigger": False,
                    "created_by_id": self.created_users[1].id,  # Bob
                    "config": {"temperature": 0.3, "max_tokens": 2000, "expertise": "code_review"}
                },
                {
                    "name": "meeting_summarizer",
                    "display_name": "Meeting Summarizer",
                    "description": "Bot that summarizes meeting discussions and action items",
                    "model_name": "claude-3-haiku",
                    "provider": "anthropic",
                    "system_prompt": "You are a meeting summarizer. Extract key points, decisions, and action items from conversations.",
                    "temperature": 0.2,
                    "max_tokens": 1500,
                    "is_active": True,
                    "is_public": True,
                    "auto_trigger": True,
                    "created_by_id": self.created_users[3].id,  # Diana
                    "config": {"temperature": 0.2, "max_tokens": 1500, "focus": "meetings"}
                }
            ]

            for bot_data in bots_data:
                bot = Bot(**bot_data)
                self.db.add(bot)
                self.created_bots.append(bot)

            self.db.commit()

            return {
                "status": "created",
                "count": len(bots_data),
                "bots": [b.name for b in self.created_bots]
            }

        except Exception as e:
            self.db.rollback()
            return {"status": "failed", "error": str(e)}

    def create_sample_conversations(self) -> Dict[str, Any]:
        """Create sample conversations."""
        try:
            if not self.created_users:
                return {"status": "failed", "error": "No users available. Create users first."}

            conversations_data = [
                {
                    "title": "Team Standup",
                    "description": "Daily team standup meeting",
                    "created_by_id": self.created_users[0].id  # Alice
                },
                {
                    "title": "Code Review Session",
                    "description": "Reviewing the latest pull request",
                    "created_by_id": self.created_users[1].id  # Bob
                },
                {
                    "title": "Project Planning",
                    "description": "Planning the next sprint",
                    "created_by_id": self.created_users[3].id  # Diana
                }
            ]

            for conv_data in conversations_data:
                conversation = Conversation(**conv_data)
                self.db.add(conversation)
                self.created_conversations.append(conversation)

            self.db.commit()

            # Add participants to conversations
            self._add_conversation_participants()

            return {
                "status": "created",
                "count": len(conversations_data),
                "conversations": [c.title for c in self.created_conversations]
            }

        except Exception as e:
            self.db.rollback()
            return {"status": "failed", "error": str(e)}

    def _add_conversation_participants(self):
        """Add participants to conversations."""
        from datetime import datetime

        participants_data = [
            # Team Standup: Alice (owner), Bob, Charlie, and Assistant Bot
            {"conversation": self.created_conversations[0], "user": self.created_users[0], "role": "owner"},
            {"conversation": self.created_conversations[0], "user": self.created_users[1], "role": "participant"},
            {"conversation": self.created_conversations[0], "user": self.created_users[2], "role": "participant"},
            {"conversation": self.created_conversations[0], "bot": self.created_bots[0], "role": "bot"},

            # Code Review: Bob (owner), Alice, and Code Reviewer Bot
            {"conversation": self.created_conversations[1], "user": self.created_users[1], "role": "owner"},
            {"conversation": self.created_conversations[1], "user": self.created_users[0], "role": "participant"},
            {"conversation": self.created_conversations[1], "bot": self.created_bots[1], "role": "bot"},

            # Project Planning: Diana (owner), all users, and Meeting Summarizer Bot
            {"conversation": self.created_conversations[2], "user": self.created_users[3], "role": "owner"},
            {"conversation": self.created_conversations[2], "user": self.created_users[0], "role": "participant"},
            {"conversation": self.created_conversations[2], "user": self.created_users[1], "role": "participant"},
            {"conversation": self.created_conversations[2], "user": self.created_users[2], "role": "participant"},
            {"conversation": self.created_conversations[2], "bot": self.created_bots[2], "role": "bot"},
        ]

        for participant_data in participants_data:
            user = participant_data.get("user")
            bot = participant_data.get("bot")
            
            user_id = user.id if user is not None else None
            bot_id = bot.id if bot is not None else None
            
            # Insert into the association table
            self.db.execute(
                conversation_participants.insert().values(
                    conversation_id=participant_data["conversation"].id,
                    user_id=user_id,
                    bot_id=bot_id,
                    joined_at=datetime.now(),
                    role=participant_data["role"]
                )
            )

        self.db.commit()

    def create_sample_messages(self) -> Dict[str, Any]:
        """Create sample messages."""
        try:
            if not self.created_conversations:
                return {"status": "failed", "error": "No conversations available. Create conversations first."}

            messages_data = [
                # Team Standup messages
                {
                    "conversation_id": self.created_conversations[0].id,
                    "sender_user_id": self.created_users[0].id,  # Alice
                    "content": "Good morning team! Let's start our standup. What did everyone work on yesterday?",
                    "is_active": True
                },
                {
                    "conversation_id": self.created_conversations[0].id,
                    "sender_user_id": self.created_users[1].id,  # Bob
                    "content": "I worked on the authentication system and fixed the JWT token validation.",
                    "is_active": True
                },
                {
                    "conversation_id": self.created_conversations[0].id,
                    "sender_user_id": self.created_users[2].id,  # Charlie
                    "content": "I completed the user profile page and added form validation.",
                    "is_active": True
                },
                {
                    "conversation_id": self.created_conversations[0].id,
                    "sender_bot_id": self.created_bots[0].id,  # Assistant Bot
                    "content": "Thanks for the updates! The team has made good progress on the authentication and UI components.",
                    "bot_conversation": "Acknowledged the team updates and provided positive feedback.",
                    "is_active": True
                },

                # Code Review messages
                {
                    "conversation_id": self.created_conversations[1].id,
                    "sender_user_id": self.created_users[1].id,  # Bob
                    "content": "I've submitted a PR for the new API endpoints. Can you take a look?",
                    "is_active": True
                },
                {
                    "conversation_id": self.created_conversations[1].id,
                    "sender_bot_id": self.created_bots[1].id,  # Code Reviewer
                    "content": "I've reviewed your PR. Overall looks good! Just a few suggestions: 1) Add more comprehensive error handling, 2) Consider adding input validation, 3) The function could be split into smaller, more focused methods.",
                    "bot_conversation": "Provided code review feedback with specific suggestions for improvement.",
                    "is_active": True
                },

                # Project Planning messages
                {
                    "conversation_id": self.created_conversations[2].id,
                    "sender_user_id": self.created_users[3].id,  # Diana
                    "content": "Let's plan our next sprint. What are the top priorities?",
                    "is_active": True
                },
                {
                    "conversation_id": self.created_conversations[2].id,
                    "sender_user_id": self.created_users[0].id,  # Alice
                    "content": "I think we should focus on completing the user authentication flow and then move to the dashboard.",
                    "is_active": True
                },
                {
                    "conversation_id": self.created_conversations[2].id,
                    "sender_bot_id": self.created_bots[2].id,  # Meeting Summarizer
                    "content": "Meeting Summary: Sprint Planning\n\nKey Points:\n- Complete user authentication flow\n- Develop dashboard components\n- Focus on user experience improvements\n\nAction Items:\n- Alice: Finish auth system\n- Bob: Start dashboard design\n- Charlie: Prepare user testing scenarios",
                    "bot_conversation": "Summarized the meeting discussion and extracted action items.",
                    "is_active": True
                }
            ]

            created_messages = []
            for msg_data in messages_data:
                message = Message(**msg_data)
                self.db.add(message)
                created_messages.append(message)

            self.db.commit()

            return {
                "status": "created",
                "count": len(messages_data),
                "messages": len(created_messages)
            }

        except Exception as e:
            self.db.rollback()
            return {"status": "failed", "error": str(e)}

    def create_seed_data(self, options: Dict[str, bool]) -> Dict[str, Any]:
        """Create all seed data based on options."""
        results = {}

        try:
            if options.get("clean"):
                print("🧹 Cleaning existing data...")
                clean_result = self.clean_existing_data()
                results["clean"] = clean_result
                if clean_result["status"] == "failed":
                    return {"status": "failed", "error": "Failed to clean data", "results": results}

            if options.get("users", True):
                print("👥 Creating sample users...")
                results["users"] = self.create_sample_users()

            if options.get("bots", True):
                print("🤖 Creating sample bots...")
                results["bots"] = self.create_sample_bots()

            if options.get("conversations", True):
                print("💬 Creating sample conversations...")
                results["conversations"] = self.create_sample_conversations()

            if options.get("messages", True):
                print("📝 Creating sample messages...")
                results["messages"] = self.create_sample_messages()

            # Check for failures
            failed_operations = [k for k, v in results.items() if v.get("status") == "failed"]
            if failed_operations:
                return {
                    "status": "partial",
                    "message": f"Some operations failed: {', '.join(failed_operations)}",
                    "results": results
                }

            return {
                "status": "success",
                "message": "All seed data created successfully",
                "results": results
            }

        except Exception as e:
            return {"status": "failed", "error": str(e), "results": results}


def create_seed_data(options: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
    """Convenience function to create seed data."""
    if options is None:
        options = {"users": True, "bots": True, "conversations": True, "messages": True}

    with DataSeeder() as seeder:
        return seeder.create_seed_data(options)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Data Seeding Script for Chat App")
    parser.add_argument("--users", action="store_true", help="Create sample users")
    parser.add_argument("--bots", action="store_true", help="Create sample bots")
    parser.add_argument("--conversations", action="store_true", help="Create sample conversations")
    parser.add_argument("--messages", action="store_true", help="Create sample messages")
    parser.add_argument("--all", action="store_true", help="Create all sample data")
    parser.add_argument("--clean", action="store_true", help="Clean existing data before seeding")
    parser.add_argument("--confirm", action="store_true", help="Confirm destructive operations")

    args = parser.parse_args()

    # Determine what to create
    if args.all:
        options = {"users": True, "bots": True, "conversations": True, "messages": True}
    else:
        options = {
            "users": args.users,
            "bots": args.bots,
            "conversations": args.conversations,
            "messages": args.messages
        }

    # If no specific options, create everything
    if not any(options.values()):
        options = {"users": True, "bots": True, "conversations": True, "messages": True}

    # Handle clean option
    if args.clean and not args.confirm:
        print("❌ --clean requires --confirm flag")
        sys.exit(1)

    options["clean"] = args.clean

    try:
        result = create_seed_data(options)

        if result["status"] == "success":
            print("✅ Seed data created successfully!")
            for operation, op_result in result.get("results", {}).items():
                if op_result.get("status") == "created":
                    count = op_result.get("count", 0)
                    print(f"  • {operation}: {count} items created")
        elif result["status"] == "partial":
            print("⚠️  Seed data created partially")
            print(f"   {result.get('message', '')}")
        else:
            print(f"❌ Failed to create seed data: {result.get('error', 'Unknown error')}")

        sys.exit(0 if result["status"] in ["success", "partial"] else 1)

    except KeyboardInterrupt:
        print("\n🛑 Operation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()