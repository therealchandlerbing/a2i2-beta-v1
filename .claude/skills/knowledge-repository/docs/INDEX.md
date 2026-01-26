# A2I2 Knowledge Repository Documentation Index

**Last Updated**: January 25, 2026
**Version**: 1.0.0-beta

---

## Quick Navigation

| Document | Purpose | Audience |
|:---------|:--------|:---------|
| [SKILL.md](../SKILL.md) | Core operational logic | All users |
| [README.md](../README.md) | Skill documentation | New users |
| [QUICK-START.md](../QUICK-START.md) | Fast reference | Everyone |

---

## Core Documentation

### Getting Started

| Document | Description |
|:---------|:------------|
| [README.md](../README.md) | Introduction to the Knowledge Repository skill |
| [QUICK-START.md](../QUICK-START.md) | 5-minute guide to get started |
| [SKILL.md](../SKILL.md) | Complete operational logic for Claude |

### Architecture & Vision

| Document | Description |
|:---------|:------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Complete technical architecture (1,300+ lines) |
| [VISION.md](VISION.md) | R2-D2 / Enterprise computer vision |
| [STRATEGIC-REVIEW.md](STRATEGIC-REVIEW.md) | Novel concepts and intellectual property |
| [PLATFORM-DESIGN.md](PLATFORM-DESIGN.md) | Interaction & access architecture |
| [EFFICIENT-AGENTS-INTEGRATION.md](EFFICIENT-AGENTS-INTEGRATION.md) | Research synthesis for platform enhancement |
| [CLAWDBOT-INTEGRATION.md](CLAWDBOT-INTEGRATION.md) | Multi-channel accessibility patterns from clawdbot |
| [VOICE-ARCHITECTURE.md](VOICE-ARCHITECTURE.md) | **NEW** Progressive voice strategy: Siri MVP → PersonaPlex |

---

## AI Model Integrations

A2I2 is a **multi-model platform** that leverages the strengths of different AI providers.

### Claude (Anthropic)

| Integration | Description |
|:------------|:------------|
| Primary AI | Extended thinking, nuanced conversation, tool use |
| Configuration | See [CLAUDE.md](../../../CLAUDE.md) for instructions |

### Google Gemini

| Document | Description |
|:---------|:------------|
| [GEMINI-INTEGRATION.md](GEMINI-INTEGRATION.md) | Complete Gemini integration guide |
| [gemini-config.json](../config/gemini-config.json) | Configuration options |

**Key Gemini Capabilities:**
- **Gemini 3 Pro**: Most intelligent model, complex reasoning, 1M context
- **Gemini 3 Flash**: Pro-level intelligence at Flash speed
- **Gemini 3 Pro Image**: High-quality image generation
- **Deep Research Agent**: Autonomous multi-step research
- **Search Grounding**: Real-time web information
- **Live API**: Real-time voice and video

### NVIDIA PersonaPlex (Voice)

| Document | Description |
|:---------|:------------|
| [PERSONAPLEX-INTEGRATION.md](PERSONAPLEX-INTEGRATION.md) | Full-duplex voice integration |
| [mcp-voice-config.json](../config/mcp-voice-config.json) | Voice provider configuration |

**Key PersonaPlex Capabilities:**
- 170ms turn-taking latency
- Full-duplex conversation (listens while speaking)
- 16 customizable voice personas
- Natural backchannels ("uh-huh", "I see")

---

## Model Selection Guide

| Task | Recommended Model | Why |
|:-----|:------------------|:----|
| Complex reasoning | Claude or Gemini 3 Pro | Both excel at deep analysis |
| Large document analysis | Gemini 3 Pro | 1M token context window |
| Image generation | Gemini 3 Pro Image | Only option with generation |
| Real-time information | Gemini 3 Flash + Search | Grounded in current data |
| Video/audio analysis | Gemini 3 Pro | Native multimodal |
| High-volume processing | Gemini 2.5 Flash | Best price-performance |
| Natural conversation | Claude | More nuanced, empathetic |
| Real-time voice | PersonaPlex or Gemini Live | Sub-200ms latency |
| Autonomous research | Gemini Deep Research | Multi-step planning |

---

## Configuration Files

| File | Purpose |
|:-----|:--------|
| [memory-template.md](../config/memory-template.md) | Session memory template |
| [hooks-config.json](../config/hooks-config.json) | Hooks configuration |
| [mcp-voice-config.json](../config/mcp-voice-config.json) | Voice provider options |
| [gemini-config.json](../config/gemini-config.json) | Gemini model configuration |

---

## Implementation

### Source Code

| File | Purpose |
|:-----|:--------|
| [knowledge_operations.py](../src/knowledge_operations.py) | Python implementation |
| [types.ts](../src/types.ts) | TypeScript type definitions |

### Database Schema

| File | Purpose |
|:-----|:--------|
| [supabase-schema.sql](../schemas/supabase-schema.sql) | PostgreSQL schema (Supabase/Neon compatible) |

---

## Extended Documentation

### Implementation Guides

| Document | Description |
|:---------|:------------|
| [PRACTICAL-IMPLEMENTATION.md](PRACTICAL-IMPLEMENTATION.md) | Step-by-step implementation guide |
| [COMPANION-ENHANCEMENTS.md](COMPANION-ENHANCEMENTS.md) | Companion feature enhancements |

### Deployment

| Document | Description |
|:---------|:------------|
| [VERCEL-NEON-INTEGRATION.md](../../docs/VERCEL-NEON-INTEGRATION.md) | Vercel + Neon deployment guide |

---

## Memory Operations

A2I2 uses four core memory operations:

| Operation | Purpose | Example |
|:----------|:--------|:--------|
| **LEARN** | Capture new knowledge | User correction, new fact |
| **RECALL** | Retrieve relevant context | "What do you know about..." |
| **RELATE** | Connect entities | "Sarah works at TechCorp" |
| **REFLECT** | Synthesize patterns | Periodic analysis |

---

## Memory Types

| Type | Storage | Purpose |
|:-----|:--------|:--------|
| **Episodic** | `arcus_episodic_memory` | What happened |
| **Semantic** | `arcus_semantic_memory` | What we know |
| **Procedural** | `arcus_procedural_memory` | How we work |
| **Working** | Session memory | Current context |
| **Relational** | `arcus_knowledge_graph` | How things connect |

---

## Autonomy Levels

| Level | Name | Description |
|:------|:-----|:------------|
| L0 | Assisted | Human requests, Claude advises |
| L1 | Supervised | Claude proposes, human confirms |
| L2 | Autonomous | Pre-approved actions, review after |
| L3 | Fully Autonomous | Act within boundaries |
| L4 | Trusted Partner | Full peer-level collaboration |

---

## Novel Concepts

| Concept | Acronym | Description |
|:--------|:--------|:------------|
| Cognitive Architecture Protocol | CAP | Open standard for org memory |
| Digital Twin Modeling | DTM | Model HOW users think |
| Autonomy Trust Ledger | ATL | Auditable trust progression |
| Voice-Native Knowledge Graph | VNKG | Knowledge for spoken retrieval |
| Institutional Memory Crystallization | IMC | Automated tacit knowledge capture |
| Chief of Staff Protocol | CoSP | AI work coordination spec |
| Federated Organizational Intelligence | FOI | Privacy-preserving learning |

---

## External Resources

### Google Gemini

- [Google AI Studio](https://aistudio.google.com)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Gemini Cookbook](https://github.com/google-gemini/cookbook)
- [Gemini Pricing](https://ai.google.dev/gemini-api/docs/pricing)

### NVIDIA PersonaPlex

- [GitHub Repository](https://github.com/NVIDIA/personaplex)
- [Hugging Face Model](https://huggingface.co/nvidia/personaplex-7b-v1)
- [Research Page](https://research.nvidia.com/labs/adlr/personaplex/)

### Anthropic Claude

- [Claude Documentation](https://docs.anthropic.com)
- [Claude Code](https://github.com/anthropics/claude-code)

---

## Document Changelog

| Date | Change |
|:-----|:-------|
| 2026-01-26 | Added VOICE-ARCHITECTURE.md - progressive voice strategy (Siri → PersonaPlex) |
| 2026-01-26 | Added CLAWDBOT-INTEGRATION.md - multi-channel accessibility patterns |
| 2026-01-26 | Added EFFICIENT-AGENTS-INTEGRATION.md - research synthesis from 28+ papers |
| 2026-01-26 | Added PLATFORM-DESIGN.md for interaction architecture |
| 2026-01-25 | Added Gemini Integration documentation |
| 2026-01-25 | Created INDEX.md |
| 2026-01-24 | Initial documentation structure |

---

*"The journey of a thousand light years begins with a single knowledge entry."*
