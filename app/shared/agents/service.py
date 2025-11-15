"""
Shared service for AI agents.
Provides reusable agent management logic accessible across features.

PYDANTIC AI INTEGRATION CENTRAL POINT:
All Pydantic AI functionality is implemented in this module:
- Agent creation and management with Agent(model, system_prompt=...)
- AI model interactions using agent.run(), agent.run_sync(), agent.run_stream()
- Bot-specific configurations with provider support (OpenAI, Azure, etc.)
- Response generation via RunResult.output
- Agent caching for performance

Key Pydantic AI patterns used:
- Agent(model=model, system_prompt=bot_config['system_prompt'])
- result = await agent.run(user_message)
- return result.output

This keeps AI logic centralized and allows other features (messages, etc.)
to use bot capabilities without knowing AI implementation details.

Note: Trigger detection logic has been moved to app.shared.trigger.service
"""
from typing import List, Optional, Dict, Any
import asyncio

from pydantic_ai import Agent, ModelMessage  # type: ignore


class AgentService:
    """Service for managing Pydantic AI agents and their lifecycle.

    PYDANTIC AI AGENT MANAGEMENT:
    This service handles the complete lifecycle of AI agents:
    - Agent creation and caching per bot configuration
    - Provider-specific model initialization (OpenAI, Azure, etc.)
    - Agent execution and response generation
    - Performance optimization through agent reuse

    Key responsibilities:
    - Create agents with proper model and provider configuration
    - Cache agents to avoid recreation overhead
    - Execute agents with user messages and return responses
    - Handle provider-specific authentication and settings
    """

    def __init__(self, db_session=None):
        """Initialize the bot agent service."""
        self.db = db_session
        self.agents_cache = {}  # Cache for bot agents

    @staticmethod
    async def _summarize_old_messages(messages: List[ModelMessage]) -> List[ModelMessage]:
        """History processor to summarize old messages and manage token usage.

        When conversations get long (>10 messages), summarize the oldest messages
        to keep context while managing token costs and maintaining focus.
        """
        if len(messages) <= 10:
            return messages

        try:
            # Use a lightweight summarization agent
            summarize_agent = Agent(
                'openai:gpt-4o-mini',  # Use a cheaper/faster model for summarization
                system_prompt="""
                Summarize this conversation segment, focusing on:
                - Key technical points and decisions
                - Important context and requirements
                - Action items and next steps
                - Omit small talk, greetings, and casual conversation
                Keep the summary concise but informative.
                """
            )

            # Summarize the oldest messages (keep the 8 most recent intact)
            oldest_messages = messages[:-8]
            recent_messages = messages[-8:]

            if oldest_messages:
                # Create a summary of the old conversation
                summary_result = await summarize_agent.run(
                    user_prompt="Please summarize the key points from this conversation segment:",
                    message_history=oldest_messages
                )

                # Create a summary message to replace the old messages
                from pydantic_ai import ModelRequest, UserPromptPart

                summary_message = ModelRequest(parts=[
                    UserPromptPart(content=f"[Conversation Summary: {summary_result.output}]")
                ])

                # Return summary + recent messages
                return [summary_message] + recent_messages

        except Exception as e:
            # If summarization fails, just keep recent messages to avoid breaking the conversation
            print(f"History summarization failed: {e}")
            return messages[-8:] if len(messages) > 8 else messages

        return messages

    def get_or_create_agent(self, bot_config: Dict[str, Any]) -> Optional[Agent]:
        """Get or create a Pydantic AI agent for the bot.

        PYDANTIC AI INTEGRATION POINT:
        This method implements the full Pydantic AI agent lifecycle:
        1. Check agent cache for existing agent using bot_id + model_name as key
        2. If not cached, create new agent using Agent() constructor
        3. Configure agent with bot's system prompt, model, temperature, max_tokens
        4. Set up API credentials and base URL for the model
        5. Cache the agent for future use
        6. Return the configured agent

        Example implementation:
        ```python
        from pydantic_ai import Agent
        from pydantic_ai.models.openai import OpenAIChatModel

        # For OpenAI provider
        model = OpenAIChatModel(
            model_name=bot_config['model_name'],
            provider='openai'
        )

        # For Azure OpenAI provider
        from openai import AsyncAzureOpenAI
        from pydantic_ai.providers.openai import OpenAIProvider

        client = AsyncAzureOpenAI(
            azure_endpoint=bot_config['config']['azure_endpoint'],
            api_version=bot_config['config']['api_version'],
            api_key=bot_config['api_key'],
        )
        provider = OpenAIProvider(openai_client=client)

        model = OpenAIChatModel(
            model_name=bot_config['model_name'],
            provider=provider
        )

        # Create agent with bot configuration
        agent = Agent(
            model=model,
            system_prompt=bot_config['system_prompt'],
            # deps_type=...,  # Optional: dependencies for tools
            # output_type=str,  # Optional: structured output type
        )

        # Run the agent
        result = await agent.run(user_message)
        return result.output
        ```

        """
        bot_id = bot_config['id']
        cache_key = f"{bot_id}_{bot_config['model_name']}"

        if cache_key in self.agents_cache:
            return self.agents_cache[cache_key]

        try:
            agent = self._create_pydantic_agent(bot_config)
            self.agents_cache[cache_key] = agent
            return agent

        except Exception as e:
            print(f"Error creating Pydantic AI agent: {e}")
            return None

    def _create_pydantic_agent(self, bot_config: Dict[str, Any]) -> Optional[Agent]:
        """Create a Pydantic AI agent from bot configuration.

        PYDANTIC AI INTEGRATION POINT:
        This private method contains the actual Pydantic AI agent creation logic:
        1. Extract model configuration from bot_config
        2. Create the appropriate model instance (OpenAI, Anthropic, etc.)
        3. Initialize the Agent with system prompt and model
        4. Configure additional settings (temperature, max_tokens, tools)
        5. Return the configured agent

        Example implementation:
        ```python
        from pydantic_ai import Agent
        from pydantic_ai.models.openai import OpenAIChatModel

        provider_name = bot_config['provider']

        # For OpenAI provider
        if provider_name == 'openai':
            model = OpenAIChatModel(
                model_name=bot_config['model_name'],
                provider='openai'
            )

        # For Azure OpenAI provider
        elif provider_name == 'azure':
            from openai import AsyncAzureOpenAI
            from pydantic_ai.providers.openai import OpenAIProvider

            client = AsyncAzureOpenAI(
                azure_endpoint=bot_config['config']['azure_endpoint'],
                api_version=bot_config['config']['api_version'],
                api_key=bot_config['api_key'],
            )
            provider = OpenAIProvider(openai_client=client)

            model = OpenAIChatModel(
                model_name=bot_config['model_name'],
                provider=provider
            )

        # Create agent with bot configuration
        agent = Agent(
            model=model,
            system_prompt=bot_config['system_prompt'],
            # deps_type=...,  # Optional: dependencies for tools
            # output_type=str,  # Optional: structured output type
        )

        # Run the agent
        result = await agent.run(user_message)
        return result.output
        ```

        Called by get_or_create_agent() when creating new agents.
        """
        try:
            from pydantic_ai.models.openai import OpenAIChatModel

            provider_name = bot_config['provider']

            # Create provider based on type
            if provider_name == 'azure':
                from openai import AsyncAzureOpenAI
                from pydantic_ai.providers.openai import OpenAIProvider

                # Azure-specific configuration from bot config
                azure_config = bot_config.get('config', {})
                client = AsyncAzureOpenAI(
                    azure_endpoint=azure_config.get('azure_endpoint', bot_config.get('api_base_url')),
                    api_version=azure_config.get('api_version', '2024-07-01-preview'),
                    api_key=bot_config['api_key'],
                )
                provider = OpenAIProvider(openai_client=client)
            else:
                # For other providers (openai, deepseek, etc.), use string provider name
                provider = provider_name

            # Create the model instance
            model = OpenAIChatModel(
                model_name=bot_config['model_name'],
                provider=provider
                # TODO: Add profile and settings when bot config supports them
                # profile=bot_config.get('profile'),
                # settings=bot_config.get('settings')
            )

            # Create agent with bot configuration
            agent = Agent(
                model=model,
                system_prompt=bot_config['system_prompt'],
                history_processors=[self._summarize_old_messages]
                # TODO: Add additional configuration when Pydantic AI supports it
                # deps_type=...,  # Dependencies for tools
                # output_type=str,  # Structured output type
                # retries=1,  # Retry configuration
            )

            return agent  # type: ignore

        except Exception as e:
            print(f"Error creating Pydantic AI agent: {e}")
            return None

    async def generate_bot_response(
        self,
        bot_config: Dict[str, Any],
        message_history: List[Any]
    ) -> str:
        """Generate a bot response using the specified bot's configuration.

        PYDANTIC AI INTEGRATION POINT:
        This method implements the complete AI response generation:
        1. Get/create the bot's agent using get_or_create_agent()
        2. Call agent.run() with the message history for full conversation context
        3. Return result.output from the RunResult

        The agent handles all AI model interactions, provider configurations,
        and response generation based on the bot's system prompt and settings.
        """
        # Get/create agent for this bot
        agent = self.get_or_create_agent(bot_config)

        if not agent:
            # Fallback response with bot's display name
            display_name = bot_config.get('display_name', 'Assistant')
            return f"I'm {display_name}! I understand you said: '{message_history[-1].parts[0].content if message_history else 'something'}'. This is a placeholder response until AI integration is complete."

        try:
            # Use the last message in history as the current user message
            # The message_history already includes full conversation context
            current_message = message_history[-1] if message_history else None
            if not current_message:
                return "I apologize, but I couldn't process your message."

            result = await agent.run(
                user_prompt=current_message.parts[0].content,
                message_history=message_history[:-1]  # Exclude the current message from history
            )
            return result.output

        except Exception as e:
            display_name = bot_config.get('display_name', 'Assistant')
            return f"I apologize, but I encountered an error: {str(e)}"
