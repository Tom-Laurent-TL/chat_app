# 🤖 AI Agents & Bots Architecture

## Overview
Transform chat conversations into AI-powered interactions using Pydantic AI agents, tools, and bot management.

## 🏗️ Architecture

### Shared Modules
- **`shared/agents/`** - Pydantic AI agent creation, configuration, and execution
- **`shared/tools/`** - Tool definitions and functions agents can call

### Features
- **`features/bots/`** - Bot CRUD management and deployment to conversations

### Nested Features
- **`conversations/features/participants/`** - User/bot participation in conversations
- **`conversations/features/messages/`** - Message CRUD and @mention parsing/triggering

## 🎯 @Mention Bot Triggering

### User Experience
```
User: @assistant what's the weather?
Assistant: Sunny, 72°F in your area.

User: @moderator review this message
Moderator: Message approved ✓
```

### Technical Flow
1. **Parse** message for `@botname` mentions
2. **Verify** bot is conversation participant
3. **Trigger** bot's Pydantic AI agent
4. **Generate** intelligent response
5. **Post** response to conversation

## 🚀 Implementation Phases

### Phase 1: Infrastructure
- [ ] Extend User model with `is_bot`, `bot_config` fields
- [ ] Implement `shared/tools/` - tool registration system
- [ ] Implement `shared/agents/` - Pydantic AI integration

### Phase 2: Bot Management
- [ ] Build `features/bots/` - bot CRUD operations
- [ ] Link bots to agents and tools
- [ ] Deploy bots to conversations

### Phase 3: Message Integration
- [ ] Add message parsing for @mentions
- [ ] Implement bot triggering system
- [ ] Integrate responses into conversation flow

## 💡 Key Benefits

- **Natural Interaction** - Bots feel like conversation participants
- **AI-Powered** - Intelligent responses via Pydantic AI
- **Extensible** - Easy to add new tools and agent types
- **Scalable** - Shared modules work across features
- **Discoverable** - Users learn bot capabilities through conversation

## 🛠️ Core Components

### Agent Types
- **Assistant Bots** - General AI help
- **Moderation Bots** - Content monitoring
- **Integration Bots** - External service connections
- **Workflow Bots** - Business process automation

### Tool Ecosystem
- **Web Search** - Internet access
- **Calculator** - Math operations
- **Conversation History** - Context awareness
- **API Integrations** - External services

### Bot Features
- **@Mention Triggering** - Natural activation
- **Context Awareness** - Conversation history
- **Multi-Bot Support** - Multiple bots per conversation
- **Permission System** - Granular access control

---

**Result**: Transform messaging into AI collaboration platform with intelligent, conversational bots. 🚀