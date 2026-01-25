# Arcus Knowledge Repository - Index

**Quick navigation for all skill components.**

---

## Core Documentation

| File | Purpose | Read When... |
|------|---------|--------------|
| [SKILL.md](SKILL.md) | Operational logic for Claude | Understanding how to use the skill |
| [README.md](README.md) | User documentation | Getting started, overview |
| [QUICK-START.md](QUICK-START.md) | Fast reference | Quick setup, daily usage |

## Architecture & Vision

| File | Purpose | Read When... |
|------|---------|--------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Complete system design | Deep technical understanding |
| [docs/VISION.md](docs/VISION.md) | North star (R2-D2 vision) | Understanding long-term goals |
| [docs/COMPANION-ENHANCEMENTS.md](docs/COMPANION-ENHANCEMENTS.md) | R2-D2/Enterprise companion features | Building proactive intelligence |
| [docs/PRACTICAL-IMPLEMENTATION.md](docs/PRACTICAL-IMPLEMENTATION.md) | **What we can build TODAY** | Ready to start building |
| [docs/PERSONAPLEX-INTEGRATION.md](docs/PERSONAPLEX-INTEGRATION.md) | **NVIDIA PersonaPlex full-duplex voice** | True R2-D2 experience |
| [docs/STRATEGIC-REVIEW.md](docs/STRATEGIC-REVIEW.md) | **Novel IP & Enterprise Architecture** | Building defensible platform |

## Schemas & Types

| File | Purpose | Read When... |
|------|---------|--------------|
| [schemas/supabase-schema.sql](schemas/supabase-schema.sql) | Database schema | Deploying to Supabase |
| [src/types.ts](src/types.ts) | TypeScript definitions | Building integrations |

## Configuration

| File | Purpose | Read When... |
|------|---------|--------------|
| [config/hooks-config.json](config/hooks-config.json) | Hook definitions | Setting up auto-capture |
| [config/memory-template.md](config/memory-template.md) | CLAUDE.memory.md template | Initializing new workspaces |
| [config/mcp-voice-config.json](config/mcp-voice-config.json) | Voice MCP server setup | Adding voice capabilities |

## Implementation

| File | Purpose | Status |
|------|---------|--------|
| [src/knowledge_operations.py](src/knowledge_operations.py) | Python LEARN/RECALL/RELATE/REFLECT | **Ready** |
| [src/types.ts](src/types.ts) | TypeScript type definitions | **Ready** |
| src/knowledge-client.ts | Supabase client wrapper | Planned |
| src/context-manager.ts | Session context loading | Planned |

## Session State

| File | Purpose | Location |
|------|---------|----------|
| CLAUDE.memory.md | Active session state | Repository root (`/CLAUDE.memory.md`) |

---

## Quick Links by Task

### "I want to understand this system"
1. Start with [README.md](README.md)
2. Then [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. For vision: [docs/VISION.md](docs/VISION.md)

### "I want to deploy this"
1. [QUICK-START.md](QUICK-START.md) for overview
2. [schemas/supabase-schema.sql](schemas/supabase-schema.sql) for database
3. [config/memory-template.md](config/memory-template.md) for session file

### "I want to build integrations"
1. [src/types.ts](src/types.ts) for type definitions
2. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for data flow
3. [config/hooks-config.json](config/hooks-config.json) for triggers

### "I want to extend this"
1. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for module system
2. Check `modules/` directory for examples
3. Follow module interface in [SKILL.md](SKILL.md)

### "I want to add voice capabilities"
1. **Start here**: [docs/PRACTICAL-IMPLEMENTATION.md](docs/PRACTICAL-IMPLEMENTATION.md)
2. [config/mcp-voice-config.json](config/mcp-voice-config.json) for MCP setup
3. Choose: VoiceMode (quick start) or Pipecat/LiveKit (advanced)
4. **For full-duplex (R2-D2 experience)**: [docs/PERSONAPLEX-INTEGRATION.md](docs/PERSONAPLEX-INTEGRATION.md)

---

## Version

- **Skill Version:** 1.0.0
- **Last Updated:** 2026-01-24
- **Status:** Foundation Phase
