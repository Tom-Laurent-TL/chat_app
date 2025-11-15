# 🧩 Shared Module: Agents

Provides AI agent management utilities, configuration, entities, and schemas for Pydantic AI integration.

## Usage
Features in the same Octopus app can import this module directly:
```python
from app.shared.agents.service import BotService, AgentService
from app.shared.agents.entities import *
from app.shared.agents.schemas import *
```

## Services

### AgentService
Handles AI agent lifecycle and response generation:
- Agent creation and caching with provider support (OpenAI, Azure, etc.)
- Pydantic AI integration with Agent(model, system_prompt=...)
- Response generation via agent.run() and RunResult.output
- Bot-specific configurations and model settings

### BotService
Facade service providing unified access to bot functionality:
- Access to BotTriggerService for complete trigger detection and AI response generation
- Information about available bots and their configurations
- Status monitoring for AI integration health

The trigger service handles the complete bot interaction pipeline:
1. Detect triggers based on message content and mentions
2. Generate AI responses using AgentService
3. Return responses or None if no trigger activated

## Features
- **AI Agent Management**: Create, cache, and manage Pydantic AI agents
- **Provider Support**: OpenAI, Azure, and other AI providers
- **Response Generation**: Generate AI responses with proper context
- **Performance Optimization**: Agent caching to avoid recreation overhead

## Structure
- `service.py` → AgentService (AI logic) and BotService (facade)
- `entities.py` → ORM/domain entities
- `schemas.py` → Pydantic models for agent requests/responses
- `features/` → optional nested features
- `shared/` → optional sub-shared modules

**Note**: Trigger detection logic has been moved to `app.shared.trigger.service`

Refer to `/docs` for architecture details.
