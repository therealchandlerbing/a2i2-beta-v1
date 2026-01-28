# CLAUDE.md - A2I2 Platform Guide

**Repository**: a2i2-beta-v1
**Purpose**: Enterprise AI Chief of Staff - Building AI companions that remember, learn, and grow with organizations
**Organization**: Arcus Innovation Studios
**Version**: 1.0.0-beta
**Last Updated**: 2026-01-25

---

## Quick Start for AI Assistants

This repository contains the **A2I2 (Arcus Intelligence)** platform - an Enterprise AI Chief of Staff system. When working with this repo:

1. **Check `.claude/skills/knowledge-repository/`** for the core skill implementation
2. **Read `SKILL.md`** for operational logic (how to execute knowledge operations)
3. **Follow memory operations**: LEARN, RECALL, RELATE, REFLECT
4. **Update `CLAUDE.memory.md`** to persist session learnings

---

## Repository Structure

```
a2i2-beta-v1/
├── .claude/skills/knowledge-repository/   # Core A2I2 skill
│   ├── SKILL.md                           # Operational logic
│   ├── README.md                          # User documentation
│   ├── QUICK-START.md                     # Fast reference
│   ├── INDEX.md                           # Navigation guide
│   ├── docs/                              # Extended documentation
│   │   ├── VISION.md                      # R2-D2 vision
│   │   ├── ARCHITECTURE.md                # Technical architecture
│   │   ├── STRATEGIC-REVIEW.md            # Novel concepts
│   │   ├── GEMINI-INTEGRATION.md          # Gemini multi-model guide
│   │   └── PERSONAPLEX-INTEGRATION.md     # Voice integration
│   ├── schemas/supabase-schema.sql        # Database schema
│   ├── config/                            # Configuration files
│   ├── CLAWDBOT-SKILL.md                  # ClawdBot skill manifest
│   └── src/                               # Implementation code
│       ├── knowledge_operations.py        # LEARN/RECALL/RELATE/REFLECT
│       ├── model_router.py                # Task-based model selection
│       ├── trust_engine.py                # Autonomy Trust Ledger
│       ├── context_budget.py              # Context window management
│       ├── memory_middleware.py            # Core middleware (pre/post hooks)
│       ├── gateway.py                     # Multi-channel gateway control plane
│       ├── gateway_server.py              # Gateway entry point
│       ├── chat_commands.py               # Slash command implementations
│       ├── channel_adapter.py             # Base adapter interface
│       ├── adapter_whatsapp.py            # WhatsApp adapter (Baileys bridge)
│       ├── adapter_discord.py             # Discord adapter (discord.py)
│       └── adapter_siri.py               # Siri webhook adapter
├── brand-standards/arcus-innovation-studios/  # Brand guidelines
├── docs/A2I2-REFERENCE.md                 # Platform reference
├── CLAUDE.memory.md                       # Session memory (UPDATE THIS)
└── README.md                              # User-facing docs
```

---

## Core Operations

### Memory Operations

When Claude should capture or retrieve knowledge:

| Operation | When to Use | Example |
|-----------|-------------|---------|
| **LEARN** | User correction, new info, decision made | "Actually, I prefer TypeScript" |
| **RECALL** | Entity mentioned, similar situation | "How did we handle proposals before?" |
| **RELATE** | New connection discovered | "Sarah works at TechCorp" |
| **REFLECT** | Periodic review, pattern detection | End of week synthesis |

### Auto-Capture Triggers

Automatically capture when:
- User corrects Claude → Capture preference/standard
- Successful workflow → Capture procedural pattern
- New information shared → Capture semantic fact
- Decision made → Capture episodic event
- Relationship revealed → Update knowledge graph

---

## Memory Types

| Type | Purpose | What to Store |
|------|---------|---------------|
| **Episodic** | What happened | Events, decisions, outcomes, learnings |
| **Semantic** | What we know | Facts, patterns, domain knowledge |
| **Procedural** | How we work | Workflows, preferences, standards |
| **Working** | Current context | Active session state |
| **Relational** | Connections | Entity relationships, influence networks |

---

## Seven Novel Concepts

A2I2 introduces genuinely novel concepts:

1. **Cognitive Architecture Protocol (CAP)** - Open standard for organizational memory
2. **Digital Twin Modeling (DTM)** - Model HOW users think
3. **Autonomy Trust Ledger (ATL)** - Auditable trust progression
4. **Voice-Native Knowledge Graph (VNKG)** - Knowledge for spoken retrieval
5. **Institutional Memory Crystallization (IMC)** - Automated tacit knowledge capture
6. **Chief of Staff Protocol (CoSP)** - AI work coordination spec
7. **Federated Organizational Intelligence (FOI)** - Privacy-preserving learning

---

## Key Files to Read

| Priority | File | Purpose |
|----------|------|---------|
| 1 | `.claude/skills/knowledge-repository/SKILL.md` | Core operational logic |
| 2 | `CLAUDE.memory.md` | Current session state and preferences |
| 3 | `.claude/skills/knowledge-repository/QUICK-START.md` | Fast reference |
| 4 | `.claude/skills/knowledge-repository/docs/ARCHITECTURE.md` | System design |
| 5 | `.claude/skills/knowledge-repository/docs/GEMINI-INTEGRATION.md` | Gemini multi-model guide |
| 6 | `.claude/skills/knowledge-repository/docs/INDEX.md` | Documentation navigation |

---

## Development Guidelines

### Code Style
- **Python**: 3.11+, type hints, docstrings
- **TypeScript**: Strict mode, proper types
- **Markdown**: Clear headings, tables for structured data

### Git Conventions
- Branch naming: `claude/feature-name-{session-id}`
- Descriptive commit messages
- Push to feature branches, PR to main

### Quality Standards
- Confidence scoring for all knowledge (0.0-1.0)
- Never store credentials, API keys, or secrets
- Flag sensitive information for review
- Respect privacy preferences

---

## Integration Points

### Supabase Tables
Core persistent storage:
- `arcus_episodic_memory` - Events and interactions
- `arcus_semantic_memory` - Facts and patterns
- `arcus_procedural_memory` - Workflows and preferences
- `arcus_entities` - Knowledge graph nodes (people, orgs, projects)
- `arcus_relationships` - Knowledge graph edges (connections between entities)

### CLAUDE.memory.md
Session state file - update this with:
- User preferences discovered
- Active projects
- Recent learnings
- Pending actions

### Voice Integration
NVIDIA PersonaPlex for natural conversation:
- 170ms latency for responses
- Full-duplex conversation
- See `docs/PERSONAPLEX-INTEGRATION.md`

### Gemini Multi-Model Integration
Google Gemini models for advanced capabilities:
- **Gemini 3 Pro**: 1M context, complex reasoning, agentic tasks
- **Gemini 3 Flash**: Pro-level intelligence at Flash speed
- **Gemini 3 Pro Image**: 4K image generation, grounded visuals
- **Deep Research Agent**: Autonomous multi-step research
- **Search Grounding**: Real-time information from Google Search
- **Thinking Levels**: Control reasoning depth (minimal, low, medium, high)
- See `docs/GEMINI-INTEGRATION.md`

### Model Selection
A2I2 uses a model router to select optimal AI for each task:
| Task | Recommended Model |
|------|-------------------|
| Complex reasoning | Claude or Gemini 3 Pro |
| Large documents (>200K) | Gemini 3 Pro |
| Image generation | Gemini 3 Pro Image |
| Real-time information | Gemini 3 Flash + Search |
| Natural conversation | Claude |
| Autonomous research | Deep Research Agent |

---

## Common Tasks

### Starting a Session
1. Read `CLAUDE.memory.md` for preferences
2. Query recent episodic memories (if Supabase configured)
3. Load active project context
4. Apply preferences to responses

### Ending a Session
1. Capture queued learnings
2. Update `CLAUDE.memory.md` with new preferences
3. Run reflection if significant learnings
4. Update relationship graph with new entities

### Handling a Knowledge Request
1. Parse query intent (recall vs. learn vs. relate)
2. Determine relevant memory types
3. Execute appropriate operation
4. Format response for user

---

## Organization Context

**Arcus Innovation Studios** builds AI companions that:
- Remember everything across sessions
- Learn continuously from interactions
- Think like users through Digital Twin modeling
- Speak naturally via voice interfaces
- Act autonomously within trust boundaries

Vision: Build the R2-D2 / Enterprise computer experience for organizations.

---

## Contact

**Repository**: https://github.com/therealchandlerbing/a2i2-beta-v1
**Origin**: [claude-usecases](https://github.com/therealchandlerbing/claude-usecases)
**Organization**: Arcus Innovation Studios

---

*"The journey of a thousand light years begins with a single knowledge entry."*
