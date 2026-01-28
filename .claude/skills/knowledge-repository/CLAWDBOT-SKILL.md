---
name: Arcus Memory Middleware
description: A2I2 memory and intelligence layer for ClawdBot — provides persistent memory, learning, trust, and knowledge graph capabilities as a ClawdBot-compatible skill
version: 1.0.0
author: Arcus Innovation Studios
created: 2026-01-28
updated: 2026-01-28
category: intelligence
complexity: high
engine: clawdbot
dependencies:
  - Supabase (persistent storage)
  - knowledge_operations.py (LEARN/RECALL/RELATE/REFLECT)
  - model_router.py (task-based model selection)
  - trust_engine.py (Autonomy Trust Ledger)
  - context_budget.py (context window management)
  - CLAUDE.memory.md (session state)
tools:
  - recall: Search knowledge graph
  - learn: Capture explicit knowledge
  - forget: Request knowledge removal
  - context: Show session memory state
  - preferences: Display learned preferences
  - autonomy: Show trust level
  - reflect: Trigger pattern synthesis
  - status: System health
  - compact: Compress context
  - verbose: Set detail level
outputs:
  - Memory context injection (per-message)
  - Knowledge entries (JSON via Supabase)
  - Trust ledger entries (audit trail)
  - Session summaries (on end)
hooks:
  - pre_message: Inject memory context before AI processing
  - post_message: Extract and persist learnings from AI response
  - on_session_start: Load user preferences and recent history
  - on_session_end: Flush pending learnings, update CLAUDE.memory.md
  - on_reaction: Capture feedback as reward signal
  - on_heartbeat: Periodic REFLECT synthesis (every 50 messages)
---

# Arcus Memory Middleware — ClawdBot Skill

## Purpose

This skill transforms ClawdBot from a stateless multi-channel assistant into a
**persistent, learning, trust-aware AI Chief of Staff**. It hooks into
ClawdBot's message pipeline to:

1. **Inject memory context** before each AI call (preferences, recent events, entities)
2. **Extract learnings** from every interaction (auto-capture corrections, decisions, facts)
3. **Track trust** via the Autonomy Trust Ledger (L0 Observer → L4 Full Autonomy)
4. **Manage context budgets** to fit knowledge within model token limits
5. **Route to optimal models** based on task type (Claude for reasoning, Gemini for search)

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  ClawdBot Runtime                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Channel Adapters (12+)                              │   │
│  │  WhatsApp │ Discord │ Siri │ Telegram │ Web │ ...   │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ★ Arcus Memory Middleware (this skill)              │   │
│  │                                                       │   │
│  │  PRE-MESSAGE HOOK                                    │   │
│  │  ├── Load user session (SessionManager)              │   │
│  │  ├── Query memory (KnowledgeRepository.recall)       │   │
│  │  ├── Allocate context budget (ContextBudgetManager)  │   │
│  │  ├── Check trust boundaries (TrustEngine)            │   │
│  │  └── Inject formatted context block                  │   │
│  │                                                       │   │
│  │  POST-MESSAGE HOOK                                   │   │
│  │  ├── Extract learnings from response                 │   │
│  │  ├── Auto-capture corrections/decisions              │   │
│  │  ├── Log interaction to Trust Ledger                 │   │
│  │  └── Update session state                            │   │
│  │                                                       │   │
│  │  COMMANDS: /recall /learn /forget /context            │   │
│  │            /preferences /autonomy /reflect            │   │
│  │            /status /compact /verbose /help            │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  AI Model (Claude / Gemini via ModelRouter)          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Supabase: arcus_* tables                            │   │
│  │  Episodic │ Semantic │ Procedural │ Entities │ Trust │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## How It Works

### 1. Pre-Message Hook (before AI sees the message)

```python
# Pseudocode — see memory_middleware.py for full implementation
async def pre_message(message, session):
    # Get or create session
    session = session_manager.get_or_create(user_id, channel, chat_id)

    # Query relevant memory
    memories = knowledge_repo.recall(message.text, memory_types=["all"])

    # Budget the context
    allocation = budget_manager.allocate_budget(
        task_context=detect_task_type(message.text),
        base_prompt_tokens=estimate_tokens(message.text),
    )
    packed = budget_manager.pack_knowledge(allocation, memories)

    # Inject into system prompt
    context_block = budget_manager.assemble_context(packed)
    message.system_prompt += context_block
```

### 2. Post-Message Hook (after AI responds)

```python
async def post_message(message, response, session):
    # Auto-learn from corrections
    if detected_correction(message.text):
        knowledge_repo.learn_preference(extract_preference(message.text))

    # Log to Trust Ledger
    trust_engine.record_outcome(action="respond", success=True, channel=session.channel)

    # Update session
    session.touch()
    session.history.append({"role": "user", "content": message.text})
    session.history.append({"role": "assistant", "content": response})
```

### 3. Commands

All commands work identically across WhatsApp, Discord, Siri, and any other
ClawdBot channel:

| Command | Description |
|:--------|:------------|
| `/recall <query>` | Search knowledge graph |
| `/learn <statement>` | Capture explicit knowledge |
| `/forget <topic>` | Mark knowledge for removal |
| `/context` | Show current session state |
| `/preferences` | Display learned preferences |
| `/autonomy` | Show trust level (L0-L4) |
| `/reflect` | Trigger pattern synthesis |
| `/status` | System health |
| `/compact` | Compress conversation context |
| `/verbose [0-3]` | Set response detail level |
| `/help` | List commands |

## Files

| File | Purpose |
|:-----|:--------|
| `src/memory_middleware.py` | Core middleware — pre/post hooks, session management, learning pipeline |
| `src/chat_commands.py` | Slash command implementations |
| `src/gateway.py` | Gateway control plane (standalone or ClawdBot-embedded) |
| `src/gateway_server.py` | Entry point for standalone mode |
| `src/channel_adapter.py` | Base adapter interface (standalone mode) |
| `src/adapter_whatsapp.py` | WhatsApp adapter (standalone mode) |
| `src/adapter_discord.py` | Discord adapter (standalone mode) |
| `src/adapter_siri.py` | Siri webhook adapter (standalone mode) |
| `src/knowledge_operations.py` | LEARN/RECALL/RELATE/REFLECT operations |
| `src/model_router.py` | Task-based model selection |
| `src/trust_engine.py` | Autonomy Trust Ledger |
| `src/context_budget.py` | Context window management |

## Running

### Mode 1: As a ClawdBot Skill (Recommended)

Place this skill directory in ClawdBot's `skills/` folder. ClawdBot will
automatically load the `CLAWDBOT-SKILL.md` manifest and register the hooks
and commands.

### Mode 2: Standalone Gateway

```bash
pip install -r src/requirements-gateway.txt
python src/gateway_server.py
```

Configure adapters via environment variables (see `.env.example`).
