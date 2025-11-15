# 🧩 Shared Module: Trigger

Provides utilities, configuration, entities, and schemas shared across features for trigger detection and management.

## Usage
Features in the same Octopus app can import this module directly:
```python
from app.shared.trigger.service import TriggerService, BotTriggerService
from app.shared.trigger.entities import *
from app.shared.trigger.schemas import *
```

## Services

### TriggerService
Generic trigger detection capabilities for any feature:
- Mention detection (@username, @keyword patterns)
- Keyword-based triggering
- Pattern matching and content analysis
- Context-aware trigger evaluation

### BotTriggerService
Bot-specific trigger logic that handles the complete bot interaction flow:
- Mention detection (@botname, @assistant, etc.)
- Bot availability checking from database
- Bot configuration retrieval
- **Complete AI response generation** using AgentService
- Integration with bot database entities

**Key Method**: `detect_and_respond()` - Handles trigger detection AND response generation in one call.

## Features
- **Mention Detection**: Extract and analyze @mentions from content
- **Keyword Triggering**: Check for specific keywords in mentions or content
- **Pattern Matching**: Support for custom trigger patterns
- **Content Analysis**: Parse and analyze text content for triggers
- **Bot Integration**: Specialized bot trigger detection and configuration

## Structure
- `service.py` → TriggerService (generic) and BotTriggerService (bot-specific)
- `entities.py` → ORM/domain entities (extensible for future use)
- `schemas.py` → Pydantic models for trigger requests/responses
- `features/` → optional nested features
- `shared/` → optional sub-shared modules

## Integration Examples
```python
# Basic mention detection
trigger_service = TriggerService()
mentions = trigger_service.extract_mentions("@bot help me")
# Returns: ['bot']

# Keyword-based triggering
should_trigger = trigger_service.should_trigger(
    content="I need help with this",
    mentions=["help"],
    keywords=["help", "assist"]
)
# Returns: True

# Bot-specific mention checking
is_mentioned = trigger_service.is_specific_mentioned(["@assistant"], "assistant")
# Returns: True
```

Refer to `/docs` for architecture details.
