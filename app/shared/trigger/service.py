"""
Shared service for trigger detection and management.
Provides reusable trigger logic accessible across features.
"""
from typing import List, Dict, Any, Optional


class TriggerService:
    """Shared service for detecting and managing triggers across the application.

    TRIGGER DETECTION FRAMEWORK:
    This service provides generic trigger detection capabilities that can be used by:
    - Bot systems for @mention detection
    - Notification systems for keyword triggers
    - Workflow systems for event triggers
    - Any feature needing pattern-based activation

    Key capabilities:
    - Mention detection (@username, @keyword patterns)
    - Keyword-based triggering
    - Pattern matching and analysis
    - Context-aware trigger evaluation
    """

    def __init__(self):
        """Initialize shared trigger resources."""
        pass

    def is_mentioned(self, mentions: List[str], keywords: List[str]) -> bool:
        """Check if any of the specified keywords are mentioned.

        Args:
            mentions: List of mention strings (e.g., ['@bot', '@assistant'])
            keywords: List of keywords to check for (e.g., ['bot', 'assistant', 'help'])

        Returns:
            True if any keyword is found in mentions (case-insensitive)
        """
        if not mentions or not keywords:
            return False

        return any(
            any(keyword.lower() in mention.lower() for keyword in keywords)
            for mention in mentions
        )

    def is_specific_mentioned(self, mentions: List[str], target: str) -> bool:
        """Check if a specific target is mentioned.

        Args:
            mentions: List of mention strings
            target: The specific target to check for

        Returns:
            True if target is found in mentions (case-insensitive)
        """
        if not mentions or not target:
            return False

        return target.lower() in [mention.lower() for mention in mentions]

    def should_trigger(self,
                      content: str,
                      mentions: List[str],
                      keywords: Optional[List[str]] = None,
                      patterns: Optional[List[str]] = None) -> bool:
        """Determine if a trigger should activate based on content and mentions.

        Args:
            content: The content to analyze
            mentions: List of mentions found in the content
            keywords: Optional keywords that should trigger activation
            patterns: Optional patterns to match against content

        Returns:
            True if any trigger condition is met
        """
        # Check for explicit mentions of keywords
        if keywords and self.is_mentioned(mentions, keywords):
            return True

        # Could add more sophisticated logic here:
        # - Pattern matching in content
        # - Question detection (?)
        # - Sentiment analysis
        # - Context awareness

        if patterns:
            content_lower = content.lower()
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    return True

        return False

    def extract_mentions(self, content: str) -> List[str]:
        """Extract @mentions from content.

        Args:
            content: The text content to parse

        Returns:
            List of mention strings (without @ prefix)
        """
        import re
        # Find all @mentions (word characters after @)
        mentions = re.findall(r'@(\w+)', content)
        return mentions

    def info(self) -> dict:
        """Return information about this shared module."""
        return {
            "message": "Shared module trigger is ready.",
            "capabilities": [
                "mention_detection",
                "keyword_triggering",
                "pattern_matching",
                "content_analysis"
            ]
        }


class BotTriggerService:
    """Service for detecting when bots should respond to messages.

    BOT TRIGGER DETECTION:
    This service handles the logic for determining when AI bots should be activated:
    - Mention detection (@botname, @assistant, etc.)
    - Keyword-based triggering
    - Context-aware trigger patterns
    - Bot availability checking

    Key responsibilities:
    - Analyze message content for bot mentions
    - Check if bots are available and active
    - Provide trigger recommendations
    - Support multiple trigger patterns

    This service works with AgentService for actual response generation.
    """

    def __init__(self, db_session=None):
        """Initialize the bot trigger service."""
        self.db = db_session
        # Use the shared trigger service for generic trigger functionality
        self.trigger_service = TriggerService()
        # Import agent service for response generation
        from app.shared.agents.service import AgentService
        self.agent_service = AgentService(db_session)

    def is_bot_mentioned(self, mentions: List[str]) -> bool:
        """Check if any bot-related mentions are present."""
        bot_keywords = ['assistant', 'bot', 'ai', 'help']
        return self.trigger_service.is_mentioned(mentions, bot_keywords)

    def is_specific_bot_mentioned(self, mentions: List[str], bot_name: str) -> bool:
        """Check if a specific bot is mentioned."""
        return self.trigger_service.is_specific_mentioned(mentions, bot_name)

    def get_bot_config(self, bot_name: str) -> Optional[Dict[str, Any]]:
        """Get bot configuration from the database."""
        if not self.db:
            return None

        try:
            from app.features.bots.entities import Bot
            bot = self.db.query(Bot).filter(Bot.name == bot_name, Bot.is_active == True).first()  # type: ignore
            if not bot:
                return None

            return {
                'id': bot.id,
                'name': bot.name,
                'display_name': bot.display_name,
                'model_name': bot.model_name,
                'provider': bot.provider,
                'system_prompt': bot.system_prompt,
                'temperature': bot.temperature / 100.0,  # Convert from 0-200 to 0.0-2.0
                'max_tokens': bot.max_tokens,
                'api_key': bot.api_key,
                'api_base_url': bot.api_base_url,
                'config': bot.config or {}
            }
        except Exception:
            return None

    def should_trigger_bot(self, message_content: str, mentions: List[str]) -> bool:
        """Determine if a bot response should be triggered based on message content and mentions.

        PYDANTIC AI INTEGRATION POINT:
        This method controls when AI responses are generated. It can be enhanced with:
        1. Natural language understanding to detect intent
        2. Context awareness (conversation history)
        3. Bot-specific trigger patterns from configuration
        4. Sentiment analysis for appropriate responses

        Currently triggers on:
        - Explicit bot mentions (@botname)
        - Can be extended to include keywords, questions, or patterns

        Returns True if any bot should respond to this message.
        """
        bot_keywords = ['assistant', 'bot', 'ai', 'help']
        return self.trigger_service.should_trigger(
            content=message_content,
            mentions=mentions,
            keywords=bot_keywords
        )

    def extract_mentions(self, content: str) -> List[str]:
        """Extract @mentions from message content.

        Args:
            content: The message content to parse

        Returns:
            List of mention strings (without @ prefix)
        """
        return self.trigger_service.extract_mentions(content)

    def get_available_bots(self) -> List[Dict[str, Any]]:
        """Get list of available active bots for triggering and response generation.

        PYDANTIC AI INTEGRATION POINT:
        This method provides the bot configurations that will be used to:
        1. Create or retrieve Pydantic AI agents
        2. Generate responses using appropriate models and prompts
        3. Apply bot-specific settings (temperature, max_tokens, etc.)

        Returns a list of active bot configurations with essential metadata
        for agent creation and response generation.
        """
        if not self.db:
            return []

        try:
            from app.features.bots.entities import Bot
            bots = self.db.query(Bot).filter(Bot.is_active == True).all()  # type: ignore
            return [{
                'id': bot.id,
                'name': bot.name,
                'display_name': bot.display_name,
                'description': bot.description,
                'is_public': bot.is_public
            } for bot in bots]
        except Exception:
            return []


    def detect_triggers(self, message_content: str) -> Optional[Dict[str, Any]]:
        """Detect if a bot should be triggered by the message content.

        TRIGGER DETECTION ONLY:
        This method handles pure trigger detection logic:
        1. Extract mentions from message content
        2. Check if bot should be triggered based on mentions/content
        3. Return trigger information if triggered, None otherwise

        Does NOT generate responses - that's handled separately by AgentService.

        Args:
            message_content: The user's message content

        Returns:
            Dict with 'bot_config' if triggered, None otherwise
        """
        # Extract mentions from the message
        mentions = self.extract_mentions(message_content)

        # Check if bot should be triggered
        if not self.should_trigger_bot(message_content, mentions):
            return None

        # Find the most appropriate bot to respond
        # For now, use the first available bot, but could be enhanced to:
        # - Match specific bot mentions (@botname)
        # - Use conversation context to determine appropriate bot
        # - Implement bot selection logic

        available_bots = self.get_available_bots()
        if not available_bots:
            return None

        # Use the first available bot (could be enhanced with smarter selection)
        bot_info = available_bots[0]
        bot_config = self.get_bot_config(bot_info['name'])

        if not bot_config:
            return None

        return {
            'bot_config': bot_config,
            'bot_name': bot_config['name']
        }


    async def detect_and_respond(
        self,
        message_content: str,
        conversation_context: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Detect if a bot should respond and generate a response if triggered.

        COMPLETE BOT INTERACTION FLOW:
        This method implements the full bot interaction pipeline:
        1. Extract mentions from message content
        2. Check if bot should be triggered based on mentions/content
        3. If triggered, get appropriate bot configuration
        4. Generate AI response using AgentService
        5. Return response data or None if no trigger

        Args:
            message_content: The user's message content
            conversation_context: Optional list of previous messages for context

        Returns:
            Dict with 'response', 'bot_id', and 'conversation_history' if triggered, None otherwise
        """
        # Extract mentions from the message
        mentions = self.extract_mentions(message_content)

        # Check if bot should be triggered
        if not self.should_trigger_bot(message_content, mentions):
            return None

        # Find the most appropriate bot to respond
        # For now, use the first available bot, but could be enhanced to:
        # - Match specific bot mentions (@botname)
        # - Use conversation context to determine appropriate bot
        # - Implement bot selection logic

        available_bots = self.get_available_bots()
        if not available_bots:
            return None

        # Use the first available bot (could be enhanced with smarter selection)
        bot_info = available_bots[0]
        bot_config = self.get_bot_config(bot_info['name'])

        if not bot_config:
            return None

        # Generate response using the agent service
        response_text = await self.agent_service.generate_bot_response(
            bot_config=bot_config,
            user_message=message_content,
            conversation_context=conversation_context
        )

        return {
            'response': response_text,
            'bot_id': bot_config['id'],
            'bot_name': bot_config['name'],
            'conversation_history': None  # Could be populated with actual history
        }
