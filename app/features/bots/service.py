"""
Service layer for bots.
Encapsulates business logic and domain rules.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .entities import Bot
from .schemas import BotCreate, BotUpdate, BotResponse


class BotsService:
    """Handles logic for the bots feature."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def create_bot(self, bot_data: BotCreate, created_by_id: int) -> Bot:
        """Create a new bot."""
        # Check if bot name already exists
        existing_bot = self.db.query(Bot).filter(Bot.name == bot_data.name).first()
        if existing_bot:
            raise ValueError(f"Bot with name '{bot_data.name}' already exists")

        bot = Bot(
            name=bot_data.name,
            display_name=bot_data.display_name,
            description=bot_data.description,
            avatar_url=bot_data.avatar_url,
            model_name=bot_data.model_name,
            system_prompt=bot_data.system_prompt,
            temperature=bot_data.temperature,
            max_tokens=bot_data.max_tokens,
            is_active=bot_data.is_active,
            is_public=bot_data.is_public,
            auto_trigger=bot_data.auto_trigger,
            api_key=bot_data.api_key,
            api_base_url=bot_data.api_base_url,
            config=bot_data.config,
            created_by_id=created_by_id
        )

        self.db.add(bot)
        self.db.commit()
        self.db.refresh(bot)
        return bot

    def get_bot(self, bot_id: int) -> Optional[Bot]:
        """Get a bot by ID."""
        return self.db.query(Bot).filter(Bot.id == bot_id).first()

    def get_bot_by_name(self, name: str) -> Optional[Bot]:
        """Get a bot by name."""
        return self.db.query(Bot).filter(Bot.name == name).first()

    def list_bots(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Bot]:
        """List bots with pagination."""
        query = self.db.query(Bot)
        if active_only:
            query = query.filter(Bot.is_active == True)
        return query.offset(skip).limit(limit).all()

    def update_bot(self, bot_id: int, update_data: BotUpdate, user_id: int) -> Optional[Bot]:
        """Update a bot (only by the creator)."""
        bot = self.get_bot(bot_id)
        if not bot or bot.created_by_id != user_id:  # type: ignore
            return None

        # Check name uniqueness if name is being updated
        if update_data.name and update_data.name != bot.name:
            existing_bot = self.db.query(Bot).filter(Bot.name == update_data.name).first()
            if existing_bot:
                raise ValueError(f"Bot with name '{update_data.name}' already exists")

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(bot, field, value)

        self.db.commit()
        self.db.refresh(bot)
        return bot

    def delete_bot(self, bot_id: int, user_id: int) -> bool:
        """Delete a bot (soft delete, only by the creator)."""
        bot = self.get_bot(bot_id)
        if not bot or bot.created_by_id != user_id:  # type: ignore
            return False

        bot.is_active = False  # type: ignore  # Soft delete
        self.db.commit()
        return True

    def get_user_bots(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Bot]:
        """Get bots created by a specific user."""
        return (
            self.db.query(Bot)
            .filter(Bot.created_by_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_public_bots(self, skip: int = 0, limit: int = 100) -> List[Bot]:
        """Get public bots that anyone can use."""
        return (
            self.db.query(Bot)
            .filter(Bot.is_public == True, Bot.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_total_bots(self, user_id: Optional[int] = None, active_only: bool = False) -> int:
        """Get total count of bots."""
        query = self.db.query(Bot)
        if user_id:
            query = query.filter(Bot.created_by_id == user_id)
        if active_only:
            query = query.filter(Bot.is_active == True)
        return query.count()

    def get_active_bots_count(self) -> int:
        """Get count of active bots."""
        return self.db.query(Bot).filter(Bot.is_active == True).count()

    def status(self) -> dict:
        """Return the operational status of this feature."""
        total_bots = self.get_total_bots()
        active_bots = self.get_active_bots_count()

        return {
            "message": "Feature bots is ready!",
            "total_bots": total_bots,
            "active_bots": active_bots
        }
