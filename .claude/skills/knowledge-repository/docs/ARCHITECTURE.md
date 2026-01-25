# Arcus Knowledge Repository - System Architecture

**Version:** 1.0.0
**Author:** Arcus Innovation Studios
**Date:** 2026-01-24
**Status:** Design Phase

---

## Executive Summary

The Arcus Knowledge Repository is a **living knowledge system** that transforms the Claude workspace from a collection of stateless skills into an **intelligent, learning environment** that:

- **Remembers** everything across sessions
- **Learns** from every interaction
- **Reasons** using accumulated knowledge
- **Acts** with increasing autonomy over time
- **Speaks** through real-time voice interfaces

This document defines the complete architecture from current state to full autonomous operation.

---

## Table of Contents

1. [Vision & North Star](#vision--north-star)
2. [Current State Analysis](#current-state-analysis)
3. [Target Architecture](#target-architecture)
4. [Phased Implementation Roadmap](#phased-implementation-roadmap)
5. [Core System Architecture](#core-system-architecture)
6. [Memory Architecture](#memory-architecture)
7. [Voice Agent Architecture](#voice-agent-architecture)
8. [Autonomy Progression Model](#autonomy-progression-model)
9. [Data Model & Schemas](#data-model--schemas)
10. [Integration Architecture](#integration-architecture)
11. [Security & Governance](#security--governance)
12. [Technology Stack](#technology-stack)

---

## Vision & North Star

### The Ultimate Goal

An **AI Chief of Staff** for Arcus Innovation Studios that:

1. **Knows everything** about the organization, clients, projects, and relationships
2. **Speaks naturally** through real-time voice interfaces
3. **Makes decisions autonomously** within defined boundaries
4. **Learns continuously** from every interaction
5. **Coordinates work** across team members and systems
6. **Anticipates needs** before they're expressed

### Design Principles

| Principle | Description |
|-----------|-------------|
| **Memory-First** | Every interaction is an opportunity to learn |
| **Modular** | Components can be added, replaced, or upgraded independently |
| **Progressive Autonomy** | Start assisted, earn trust, expand authority |
| **Voice-Native** | Designed for natural conversation, not just text |
| **Human-in-the-Loop** | Clear escalation paths, never autonomous without guardrails |
| **Transparent** | Always explainable why a decision was made |

---

## Current State Analysis

### What Exists Today

```
┌─────────────────────────────────────────────────────────────────┐
│                     CURRENT STATE (v2.8.0)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Skills    │    │   Agents    │    │  Dashboard  │         │
│  │    (33)     │    │    (18)     │    │  (Next.js)  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                    ┌───────▼───────┐                           │
│                    │   CLAUDE.md   │  ← Instructions only      │
│                    │  (static)     │    No persistent memory   │
│                    └───────────────┘                           │
│                                                                  │
│  GAPS:                                                          │
│  ✗ No cross-session memory                                      │
│  ✗ No learning from interactions                                │
│  ✗ No voice interface                                           │
│  ✗ No autonomous decision-making                                │
│  ✗ No relationship graph                                        │
│  ✗ Context resets every session                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Existing Assets to Leverage

| Asset | Value | Integration Opportunity |
|-------|-------|------------------------|
| **Intelligence Extractor** | Structured data extraction | Knowledge ingestion pipeline |
| **Agent Planning Dashboard** | Knowledge layer types defined | Schema foundation |
| **Supabase Integration** | Real-time database | Persistent storage |
| **18 Specialized Agents** | Domain expertise | Voice agent personas |
| **33 Skills** | Workflow automation | Procedural memory |
| **Hooks System** | Event automation | Knowledge capture triggers |

---

## Target Architecture

### The Complete System (North Star)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARCUS KNOWLEDGE REPOSITORY (FUTURE STATE)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        INTERFACE LAYER                               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │  Voice   │  │   Chat   │  │   API    │  │ Webhooks │            │   │
│  │  │ (Realtime)│  │  (Web)   │  │  (REST)  │  │ (Events) │            │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │   │
│  └───────┼─────────────┼─────────────┼─────────────┼────────────────────┘   │
│          │             │             │             │                        │
│          └─────────────┴──────┬──────┴─────────────┘                        │
│                               │                                             │
│  ┌────────────────────────────▼───────────────────────────────────────┐    │
│  │                      ORCHESTRATION LAYER                            │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │    │
│  │  │  Context    │  │  Decision   │  │   Action    │                 │    │
│  │  │  Manager    │  │   Engine    │  │  Executor   │                 │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                               │                                             │
│  ┌────────────────────────────▼───────────────────────────────────────┐    │
│  │                       REASONING LAYER                               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │    │
│  │  │   Claude    │  │  Autonomy   │  │  Learning   │                 │    │
│  │  │   Engine    │  │  Controller │  │   Engine    │                 │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                               │                                             │
│  ┌────────────────────────────▼───────────────────────────────────────┐    │
│  │                        MEMORY LAYER                                 │    │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐           │    │
│  │  │Episodic│ │Semantic│ │Proced- │ │Working │ │ Graph  │           │    │
│  │  │Memory  │ │Memory  │ │ural   │ │Memory  │ │Memory  │           │    │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘           │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                               │                                             │
│  ┌────────────────────────────▼───────────────────────────────────────┐    │
│  │                       STORAGE LAYER                                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │    │
│  │  │  Supabase   │  │   Vector    │  │    Git      │                 │    │
│  │  │ (Postgres)  │  │   Store     │  │ (Versioned) │                 │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                               │                                             │
│  ┌────────────────────────────▼───────────────────────────────────────┐    │
│  │                     INTEGRATION LAYER                               │    │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐         │    │
│  │  │Asana│ │Gmail│ │Drive│ │Slack│ │Zoom │ │CRM  │ │ ... │         │    │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘         │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phased Implementation Roadmap

### Phase 1: Foundation (Now - 4 weeks)
**Goal:** Persistent memory and basic learning

```
PHASE 1 DELIVERABLES
━━━━━━━━━━━━━━━━━━━━
✓ CLAUDE.memory.md - Session state file
✓ Supabase schema - Persistent storage
✓ Memory types - Episodic, semantic, procedural, working
✓ Basic capture - Manual and auto-trigger learning
✓ Basic recall - Context injection at session start
✓ Knowledge skill - CRUD operations for memory
```

**Autonomy Level:** Assisted (human approves all actions)

### Phase 2: Intelligence (Weeks 5-8)
**Goal:** Smart retrieval and relationship tracking

```
PHASE 2 DELIVERABLES
━━━━━━━━━━━━━━━━━━━━
□ Vector embeddings - Semantic search
□ Knowledge graph - Relationship tracking
□ Pattern detection - Learn from successful workflows
□ Context injection - Automatic relevant context
□ Reflection engine - Synthesize insights from data
□ Quality scoring - Confidence and relevance metrics
```

**Autonomy Level:** Supervised (Claude proposes, human confirms)

### Phase 3: Voice Integration (Weeks 9-12)
**Goal:** Real-time voice interface with memory

```
PHASE 3 DELIVERABLES
━━━━━━━━━━━━━━━━━━━━
□ Voice interface - Real-time speech I/O
□ Voice memory - Remember voice conversations
□ Voice personas - Different agents via voice
□ Multimodal - Voice + text + visual
□ Meeting assistant - Join calls, take notes, act
□ Voice commands - Trigger skills by voice
```

**Autonomy Level:** Autonomous (pre-approved action categories)

### Phase 4: Autonomy (Weeks 13-20)
**Goal:** Trusted autonomous decision-making

```
PHASE 4 DELIVERABLES
━━━━━━━━━━━━━━━━━━━━
□ Decision boundaries - What Claude can decide alone
□ Confidence thresholds - When to escalate
□ Action execution - Direct integration with systems
□ Proactive mode - Claude initiates based on patterns
□ Learning loops - Improve from outcomes
□ Governance dashboard - Monitor autonomous actions
```

**Autonomy Level:** Fully Autonomous (within defined scope)

### Phase 5: Chief of Staff (Weeks 21+)
**Goal:** Full AI partner for Arcus operations

```
PHASE 5 DELIVERABLES
━━━━━━━━━━━━━━━━━━━━
□ Cross-team coordination - Manage across people
□ Strategic planning - Anticipate and recommend
□ External communication - Handle routine comms
□ Decision support - Brief leaders on options
□ Continuous optimization - Self-improve workflows
□ Institutional memory - Full organizational knowledge
```

**Autonomy Level:** Trusted Partner (peer-level collaboration)

---

## Core System Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CORE COMPONENTS                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    CONTEXT MANAGER                               │   │
│  │                                                                   │   │
│  │  Responsibilities:                                                │   │
│  │  • Load relevant context at interaction start                     │   │
│  │  • Maintain working memory during session                         │   │
│  │  • Decide what context to inject into prompts                     │   │
│  │  • Manage context window limits                                   │   │
│  │                                                                   │   │
│  │  Inputs:                          Outputs:                        │   │
│  │  • User query                     • Enriched prompt               │   │
│  │  • Session state                  • Context package               │   │
│  │  • Memory retrieval               • Token budget                  │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    DECISION ENGINE                               │   │
│  │                                                                   │   │
│  │  Responsibilities:                                                │   │
│  │  • Classify request intent                                        │   │
│  │  • Route to appropriate skill/agent                               │   │
│  │  • Determine autonomy level for action                            │   │
│  │  • Check boundaries and constraints                               │   │
│  │                                                                   │   │
│  │  Decision Tree:                                                   │   │
│  │  1. Can I do this autonomously? → Check boundaries                │   │
│  │  2. Do I have enough confidence? → Check threshold                │   │
│  │  3. Is this reversible? → Assess risk                             │   │
│  │  4. Should I ask for approval? → Route to human                   │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    ACTION EXECUTOR                               │   │
│  │                                                                   │   │
│  │  Responsibilities:                                                │   │
│  │  • Execute approved actions                                       │   │
│  │  • Call skills with context                                       │   │
│  │  • Interface with external systems                                │   │
│  │  • Log all actions for audit                                      │   │
│  │                                                                   │   │
│  │  Action Types:                                                    │   │
│  │  • Read-only (always allowed)                                     │   │
│  │  • Write (check boundaries)                                       │   │
│  │  • External (requires approval)                                   │   │
│  │  • Financial (always escalate)                                    │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    LEARNING ENGINE                               │   │
│  │                                                                   │   │
│  │  Responsibilities:                                                │   │
│  │  • Capture learnings from interactions                            │   │
│  │  • Extract patterns from successful workflows                     │   │
│  │  • Update memory with new knowledge                               │   │
│  │  • Synthesize insights periodically                               │   │
│  │                                                                   │   │
│  │  Learning Triggers:                                               │   │
│  │  • User correction → Preference/Standard                          │   │
│  │  • Successful outcome → Workflow pattern                          │   │
│  │  • New information → Semantic fact                                │   │
│  │  • Decision made → Episodic event                                 │   │
│  │  • Relationship discovered → Graph update                         │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   AUTONOMY CONTROLLER                            │   │
│  │                                                                   │   │
│  │  Responsibilities:                                                │   │
│  │  • Enforce autonomy boundaries                                    │   │
│  │  • Track trust level over time                                    │   │
│  │  • Escalate when confidence low                                   │   │
│  │  • Request permission expansion                                   │   │
│  │                                                                   │   │
│  │  Autonomy Levels:                                                 │   │
│  │  0: Assisted     - Human does, Claude advises                     │   │
│  │  1: Supervised   - Claude proposes, human confirms                │   │
│  │  2: Autonomous   - Claude acts, human reviews after               │   │
│  │  3: Trusted      - Claude acts, exceptions only                   │   │
│  │  4: Partner      - Full collaboration, peer-level                 │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Memory Architecture

### Memory System Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MEMORY ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────┐    ┌─────────────────────┐                    │
│  │   EPISODIC MEMORY   │    │   SEMANTIC MEMORY   │                    │
│  │   (What Happened)   │    │   (What We Know)    │                    │
│  ├─────────────────────┤    ├─────────────────────┤                    │
│  │ • Conversations     │    │ • Domain facts      │                    │
│  │ • Decisions made    │    │ • Learned patterns  │                    │
│  │ • Outcomes          │    │ • Frameworks        │                    │
│  │ • Meetings          │    │ • Definitions       │                    │
│  │ • Milestones        │    │ • Best practices    │                    │
│  │                     │    │                     │                    │
│  │ Time-indexed        │    │ Concept-indexed     │                    │
│  │ Confidence-scored   │    │ Validity-tracked    │                    │
│  └─────────────────────┘    └─────────────────────┘                    │
│                                                                          │
│  ┌─────────────────────┐    ┌─────────────────────┐                    │
│  │  PROCEDURAL MEMORY  │    │   WORKING MEMORY    │                    │
│  │   (How We Work)     │    │  (Current Context)  │                    │
│  ├─────────────────────┤    ├─────────────────────┤                    │
│  │ • Workflows         │    │ • Active task       │                    │
│  │ • Preferences       │    │ • Conversation      │                    │
│  │ • Standards         │    │ • Retrieved context │                    │
│  │ • Templates         │    │ • Draft outputs     │                    │
│  │ • Decision trees    │    │ • Intermediate      │                    │
│  │                     │    │                     │                    │
│  │ Trigger-based       │    │ Session-scoped      │                    │
│  │ Success-rated       │    │ Ephemeral           │                    │
│  └─────────────────────┘    └─────────────────────┘                    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    KNOWLEDGE GRAPH                               │   │
│  │                   (How Things Connect)                           │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │                                                                   │   │
│  │    [Person]───works_at───>[Organization]                         │   │
│  │        │                        │                                 │   │
│  │    knows                    partner_of                            │   │
│  │        │                        │                                 │   │
│  │        ▼                        ▼                                 │   │
│  │    [Person]<───client_of───[Organization]                        │   │
│  │        │                        │                                 │   │
│  │    decided_on               worked_on                             │   │
│  │        │                        │                                 │   │
│  │        ▼                        ▼                                 │   │
│  │    [Decision]<───related_to───[Project]                          │   │
│  │                                                                   │   │
│  │  Entity Types: Person, Organization, Project, Decision,          │   │
│  │                Concept, Document, Meeting, Milestone              │   │
│  │                                                                   │   │
│  │  Relationship Properties: confidence, first_seen, last_seen,     │   │
│  │                          strength, context                        │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Memory Operations Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       MEMORY OPERATIONS FLOW                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  SESSION START                                                           │
│  ━━━━━━━━━━━━━━                                                         │
│  1. Read CLAUDE.memory.md (preferences, active projects)                 │
│  2. Query recent episodic (last 7 days)                                  │
│  3. Load relevant procedural (matching context)                          │
│  4. Initialize working memory with context package                       │
│                                                                          │
│  DURING INTERACTION                                                      │
│  ━━━━━━━━━━━━━━━━━━                                                     │
│  1. Entity mentioned → Query knowledge graph                             │
│  2. Similar situation → Retrieve episodic precedents                     │
│  3. Workflow triggered → Load procedural memory                          │
│  4. New information → Queue for capture                                  │
│  5. Correction made → Capture preference                                 │
│                                                                          │
│  SESSION END                                                             │
│  ━━━━━━━━━━━━                                                           │
│  1. Batch capture queued learnings                                       │
│  2. Update CLAUDE.memory.md with changes                                 │
│  3. Update knowledge graph relationships                                 │
│  4. Run reflection if significant learnings                              │
│  5. Archive session transcript (if configured)                           │
│                                                                          │
│  PERIODIC (Daily/Weekly)                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━                                                 │
│  1. Synthesize patterns from episodic → semantic                         │
│  2. Identify successful workflows → procedural                           │
│  3. Prune low-confidence/stale knowledge                                 │
│  4. Generate insights report                                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Voice Agent Architecture

### Voice System Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      VOICE AGENT ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     VOICE INTERFACE LAYER                        │   │
│  │                                                                   │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │   │
│  │  │   Speech    │    │   Speech    │    │   Voice     │          │   │
│  │  │ Recognition │───►│ Processing  │───►│  Synthesis  │          │   │
│  │  │   (STT)     │    │  (Claude)   │    │   (TTS)     │          │   │
│  │  └─────────────┘    └─────────────┘    └─────────────┘          │   │
│  │        │                   │                  │                  │   │
│  │        │                   ▼                  │                  │   │
│  │        │         ┌─────────────────┐         │                  │   │
│  │        └────────►│  Voice Memory   │◄────────┘                  │   │
│  │                  │  (Transcript +  │                            │   │
│  │                  │   Audio refs)   │                            │   │
│  │                  └─────────────────┘                            │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      VOICE PERSONAS                              │   │
│  │                                                                   │   │
│  │  Based on existing agents, each persona has:                      │   │
│  │  • Unique voice characteristics                                   │   │
│  │  • Domain expertise                                               │   │
│  │  • Communication style                                            │   │
│  │  • Autonomy boundaries                                            │   │
│  │                                                                   │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │Executive│ │Research │ │Financial│ │ Design  │ │ Client  │   │   │
│  │  │ Advisor │ │Coordina-│ │ Analyst │ │Reviewer │ │ Success │   │   │
│  │  │         │ │  tor    │ │         │ │         │ │         │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      VOICE CAPABILITIES                          │   │
│  │                                                                   │   │
│  │  REAL-TIME CONVERSATION                                          │   │
│  │  • Natural back-and-forth dialogue                                │   │
│  │  • Interrupt handling                                             │   │
│  │  • Context maintenance across turns                               │   │
│  │  • Emotion/tone detection                                         │   │
│  │                                                                   │   │
│  │  MEETING INTEGRATION                                              │   │
│  │  • Join video calls (Zoom, Meet, Teams)                           │   │
│  │  • Real-time transcription                                        │   │
│  │  • Action item extraction                                         │   │
│  │  • Follow-up scheduling                                           │   │
│  │                                                                   │   │
│  │  VOICE COMMANDS                                                   │   │
│  │  • "Hey Arcus, [command]"                                         │   │
│  │  • Skill invocation by voice                                      │   │
│  │  • Quick queries and lookups                                      │   │
│  │  • Status updates and briefings                                   │   │
│  │                                                                   │   │
│  │  PROACTIVE VOICE                                                  │   │
│  │  • Morning briefings                                              │   │
│  │  • Meeting reminders with context                                 │   │
│  │  • Deadline alerts                                                │   │
│  │  • Decision prompts                                               │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Voice Technology Options

| Component | Options | Recommendation |
|-----------|---------|----------------|
| **STT (Speech-to-Text)** | Whisper, Deepgram, AssemblyAI | Deepgram (real-time, low latency) |
| **TTS (Text-to-Speech)** | ElevenLabs, PlayHT, OpenAI TTS | ElevenLabs (natural voices, cloning) |
| **Voice Activity Detection** | WebRTC VAD, Silero VAD | Silero VAD (accurate, lightweight) |
| **Real-time Transport** | WebSockets, WebRTC | WebRTC (low latency, peer-to-peer) |
| **Meeting Integration** | Zoom SDK, Google Meet API | Start with Zoom SDK |

### Voice Memory Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    VOICE MEMORY INTEGRATION                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  VOICE CONVERSATION                                                      │
│        │                                                                 │
│        ▼                                                                 │
│  ┌──────────────┐                                                       │
│  │ Transcription │  ──────────────────────────────────────┐             │
│  └──────────────┘                                          │             │
│        │                                                   │             │
│        ▼                                                   │             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐│             │
│  │   Speaker    │    │   Emotion    │    │   Intent     ││             │
│  │ Diarization  │    │  Detection   │    │  Extraction  ││             │
│  └──────────────┘    └──────────────┘    └──────────────┘│             │
│        │                    │                   │         │             │
│        └────────────────────┴───────────────────┘         │             │
│                             │                             │             │
│                             ▼                             │             │
│                    ┌──────────────┐                       │             │
│                    │   Episodic   │                       │             │
│                    │   Memory     │◄──────────────────────┘             │
│                    │  (Enhanced)  │                                     │
│                    └──────────────┘                                     │
│                             │                                           │
│                             ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  STORED FOR EACH VOICE INTERACTION:                               │  │
│  │  • Full transcript with speaker attribution                       │  │
│  │  • Audio reference (if retention enabled)                         │  │
│  │  • Detected emotions per speaker                                  │  │
│  │  • Extracted intents and actions                                  │  │
│  │  • Commitments and follow-ups                                     │  │
│  │  • Relationship signals (rapport, tension)                        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Autonomy Progression Model

### The Trust Ladder

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      AUTONOMY PROGRESSION MODEL                          │
│                       (The Trust Ladder)                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  LEVEL 4: TRUSTED PARTNER                                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━                                              │
│  • Full peer-level collaboration                                         │
│  • Strategic decision participation                                      │
│  • External stakeholder communication                                    │
│  • Resource allocation recommendations                                   │
│  • Exception-based human review                                          │
│                                                                          │
│  Requirements to reach:                                                  │
│  □ 500+ successful autonomous actions                                    │
│  □ <1% error rate over 90 days                                          │
│  □ Human approval for level upgrade                                      │
│                                                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                          │
│  LEVEL 3: FULLY AUTONOMOUS                                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━                                              │
│  • Act within defined boundaries without asking                          │
│  • Proactive task initiation                                             │
│  • Multi-step workflow execution                                         │
│  • Self-correction on errors                                             │
│  • Post-action notification                                              │
│                                                                          │
│  Requirements to reach:                                                  │
│  □ 200+ successful supervised actions                                    │
│  □ <2% escalation rate                                                   │
│  □ Demonstrated judgment in edge cases                                   │
│                                                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                          │
│  LEVEL 2: AUTONOMOUS (Current Target)                                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                    │
│  • Execute pre-approved action types                                     │
│  • No confirmation needed for routine tasks                              │
│  • Escalate for new situations                                           │
│  • Human review after action                                             │
│                                                                          │
│  Requirements to reach:                                                  │
│  □ 50+ successful assisted actions                                       │
│  □ Clear boundary definitions                                            │
│  □ Audit trail in place                                                  │
│                                                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                          │
│  LEVEL 1: SUPERVISED                                                    │
│  ━━━━━━━━━━━━━━━━━━━━                                                   │
│  • Claude proposes actions                                               │
│  • Human confirms before execution                                       │
│  • Learning from confirmations                                           │
│  • Building trust baseline                                               │
│                                                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                          │
│  LEVEL 0: ASSISTED (Starting Point)                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                       │
│  • Human requests, Claude advises                                        │
│  • Human executes all actions                                            │
│  • Claude provides information only                                      │
│  • Observing patterns and preferences                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Autonomy Boundaries by Category

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     AUTONOMY BOUNDARIES BY CATEGORY                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CATEGORY          │ L0 │ L1 │ L2 │ L3 │ L4 │ NOTES                     │
│  ──────────────────┼────┼────┼────┼────┼────┼─────────────────────────  │
│  Read files        │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │ Always allowed           │
│  Search/research   │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │ Always allowed           │
│  Generate content  │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │ Draft requires review L0 │
│  Write files       │ ✗  │ P  │ ✓  │ ✓  │ ✓  │ P = with permission      │
│  Edit code         │ ✗  │ P  │ ✓  │ ✓  │ ✓  │ Tests required L2+       │
│  Git commit        │ ✗  │ P  │ ✓  │ ✓  │ ✓  │ Branch restrictions      │
│  Git push          │ ✗  │ ✗  │ P  │ ✓  │ ✓  │ Non-main branches only   │
│  Send email        │ ✗  │ ✗  │ ✗  │ P  │ ✓  │ Templates only L3        │
│  Create tasks      │ ✗  │ P  │ ✓  │ ✓  │ ✓  │ Asana integration        │
│  Schedule meetings │ ✗  │ ✗  │ P  │ ✓  │ ✓  │ Internal only L2         │
│  External comms    │ ✗  │ ✗  │ ✗  │ ✗  │ P  │ Always human review      │
│  Financial actions │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │ Never autonomous         │
│  Delete data       │ ✗  │ ✗  │ ✗  │ P  │ P  │ Soft delete only         │
│  System config     │ ✗  │ ✗  │ ✗  │ P  │ ✓  │ Non-security settings    │
│                                                                          │
│  Legend: ✓ = Autonomous, P = With Permission, ✗ = Not Allowed           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Training Process

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TRAINING PROCESS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PHASE 1: OBSERVATION                                                   │
│  ━━━━━━━━━━━━━━━━━━━━━                                                  │
│  • Watch human perform tasks                                             │
│  • Capture patterns and preferences                                      │
│  • Build workflow library                                                │
│  • Establish baseline understanding                                      │
│                                                                          │
│  PHASE 2: SUGGESTION                                                    │
│  ━━━━━━━━━━━━━━━━━━━                                                    │
│  • Propose actions before human asks                                     │
│  • "I notice you usually do X next..."                                   │
│  • Track acceptance/rejection rate                                       │
│  • Learn from corrections                                                │
│                                                                          │
│  PHASE 3: CONFIRMATION                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━                                                  │
│  • Ask "Should I do X?"                                                  │
│  • Execute on confirmation                                               │
│  • Report results                                                        │
│  • Learn from feedback                                                   │
│                                                                          │
│  PHASE 4: NOTIFICATION                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━                                                  │
│  • Do action, then notify                                                │
│  • "I did X because Y"                                                   │
│  • Allow undo window                                                     │
│  • Learn from overrides                                                  │
│                                                                          │
│  PHASE 5: SILENT EXECUTION                                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━                                               │
│  • Do action silently                                                    │
│  • Log for audit                                                         │
│  • Only notify on exception                                              │
│  • Full trust established                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Model & Schemas

### Core Entity Schema

```typescript
// Base entity for all knowledge items
interface KnowledgeEntity {
  id: string;                    // UUID
  type: KnowledgeType;          // 'episodic' | 'semantic' | 'procedural' | 'graph'
  content: unknown;              // Type-specific content
  confidence: number;            // 0.0 - 1.0
  source: KnowledgeSource;      // How we learned this
  created_at: Date;
  updated_at: Date;
  valid_until?: Date;           // For time-sensitive knowledge
  embedding?: number[];         // Vector embedding for semantic search
  metadata: Record<string, unknown>;
}

type KnowledgeType = 'episodic' | 'semantic' | 'procedural' | 'graph';

interface KnowledgeSource {
  type: 'user_explicit' | 'user_implicit' | 'extraction' | 'inference' | 'integration';
  session_id?: string;
  interaction_id?: string;
  document_ref?: string;
}
```

### Memory Type Schemas

```typescript
// Episodic Memory (What Happened)
interface EpisodicMemory extends KnowledgeEntity {
  type: 'episodic';
  content: {
    event_type: 'conversation' | 'decision' | 'meeting' | 'milestone' | 'error' | 'success';
    summary: string;
    participants: string[];
    outcome?: string;
    learnings: string[];
    related_entities: EntityReference[];
  };
  timestamp: Date;
}

// Semantic Memory (What We Know)
interface SemanticMemory extends KnowledgeEntity {
  type: 'semantic';
  content: {
    category: 'fact' | 'pattern' | 'framework' | 'definition' | 'best_practice';
    statement: string;
    evidence: string[];
    domain: string;
    related_concepts: string[];
  };
}

// Procedural Memory (How We Work)
interface ProceduralMemory extends KnowledgeEntity {
  type: 'procedural';
  content: {
    procedure_type: 'workflow' | 'preference' | 'standard' | 'template' | 'decision_tree';
    name: string;
    description: string;
    steps?: WorkflowStep[];
    trigger_conditions: string[];
    success_criteria: string[];
  };
  usage_count: number;
  success_rate: number;
  last_used?: Date;
}

// Knowledge Graph (How Things Connect)
interface GraphEdge extends KnowledgeEntity {
  type: 'graph';
  content: {
    source: EntityReference;
    relationship: RelationshipType;
    target: EntityReference;
    properties: Record<string, unknown>;
    bidirectional: boolean;
  };
  first_observed: Date;
  last_observed: Date;
  observation_count: number;
}

// Supporting Types
interface EntityReference {
  type: 'person' | 'organization' | 'project' | 'concept' | 'document' | 'decision';
  id: string;
  name: string;
}

interface WorkflowStep {
  order: number;
  action: string;
  skill?: string;
  conditions?: string[];
  on_success?: string;
  on_failure?: string;
}

type RelationshipType =
  | 'works_at' | 'manages' | 'reports_to'
  | 'partner_of' | 'client_of' | 'vendor_of'
  | 'owns' | 'created' | 'modified'
  | 'related_to' | 'depends_on' | 'blocks'
  | 'knows' | 'introduced' | 'collaborated_with'
  | 'decided_on' | 'participated_in' | 'influenced';
```

### Supabase Schema

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Episodic Memory
CREATE TABLE arcus_episodic_memory (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_type TEXT NOT NULL CHECK (event_type IN (
    'conversation', 'decision', 'meeting', 'milestone', 'error', 'success'
  )),
  summary TEXT NOT NULL,
  participants TEXT[] DEFAULT '{}',
  outcome TEXT,
  learnings TEXT[] DEFAULT '{}',
  related_entities JSONB DEFAULT '[]',
  confidence FLOAT DEFAULT 0.8 CHECK (confidence >= 0 AND confidence <= 1),
  source JSONB NOT NULL,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}',
  embedding VECTOR(1536)
);

-- Semantic Memory
CREATE TABLE arcus_semantic_memory (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  category TEXT NOT NULL CHECK (category IN (
    'fact', 'pattern', 'framework', 'definition', 'best_practice'
  )),
  statement TEXT NOT NULL,
  evidence TEXT[] DEFAULT '{}',
  domain TEXT,
  related_concepts TEXT[] DEFAULT '{}',
  confidence FLOAT DEFAULT 0.8 CHECK (confidence >= 0 AND confidence <= 1),
  source JSONB NOT NULL,
  valid_from TIMESTAMPTZ DEFAULT NOW(),
  valid_until TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}',
  embedding VECTOR(1536)
);

-- Procedural Memory
CREATE TABLE arcus_procedural_memory (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  procedure_type TEXT NOT NULL CHECK (procedure_type IN (
    'workflow', 'preference', 'standard', 'template', 'decision_tree'
  )),
  name TEXT NOT NULL,
  description TEXT,
  steps JSONB DEFAULT '[]',
  trigger_conditions TEXT[] DEFAULT '{}',
  success_criteria TEXT[] DEFAULT '{}',
  usage_count INT DEFAULT 0,
  success_rate FLOAT DEFAULT 0.0,
  last_used TIMESTAMPTZ,
  confidence FLOAT DEFAULT 0.8 CHECK (confidence >= 0 AND confidence <= 1),
  source JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}',
  embedding VECTOR(1536)
);

-- Knowledge Graph Edges
CREATE TABLE arcus_knowledge_graph (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_type TEXT NOT NULL,
  source_id TEXT NOT NULL,
  source_name TEXT NOT NULL,
  relationship TEXT NOT NULL,
  target_type TEXT NOT NULL,
  target_id TEXT NOT NULL,
  target_name TEXT NOT NULL,
  properties JSONB DEFAULT '{}',
  bidirectional BOOLEAN DEFAULT FALSE,
  confidence FLOAT DEFAULT 0.8 CHECK (confidence >= 0 AND confidence <= 1),
  first_observed TIMESTAMPTZ DEFAULT NOW(),
  last_observed TIMESTAMPTZ DEFAULT NOW(),
  observation_count INT DEFAULT 1,
  source JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'
);

-- Entities Registry (for graph node management)
CREATE TABLE arcus_entities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  entity_type TEXT NOT NULL CHECK (entity_type IN (
    'person', 'organization', 'project', 'concept', 'document', 'decision'
  )),
  external_id TEXT,
  name TEXT NOT NULL,
  aliases TEXT[] DEFAULT '{}',
  attributes JSONB DEFAULT '{}',
  first_seen TIMESTAMPTZ DEFAULT NOW(),
  last_seen TIMESTAMPTZ DEFAULT NOW(),
  mention_count INT DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  embedding VECTOR(1536),
  UNIQUE(entity_type, external_id)
);

-- Autonomy Audit Log
CREATE TABLE arcus_autonomy_audit (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  action_type TEXT NOT NULL,
  action_description TEXT NOT NULL,
  autonomy_level INT NOT NULL CHECK (autonomy_level >= 0 AND autonomy_level <= 4),
  decision_reasoning TEXT,
  confidence FLOAT NOT NULL,
  boundary_check JSONB NOT NULL,
  outcome TEXT CHECK (outcome IN ('success', 'failure', 'pending', 'cancelled', 'overridden')),
  human_override BOOLEAN DEFAULT FALSE,
  override_reason TEXT,
  session_id TEXT,
  executed_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'
);

-- Session State (for CLAUDE.memory.md sync)
CREATE TABLE arcus_session_state (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id TEXT UNIQUE NOT NULL,
  user_preferences JSONB DEFAULT '{}',
  active_projects JSONB DEFAULT '[]',
  recent_learnings JSONB DEFAULT '[]',
  pending_actions JSONB DEFAULT '[]',
  working_memory JSONB DEFAULT '{}',
  started_at TIMESTAMPTZ DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  sync_status TEXT DEFAULT 'active' CHECK (sync_status IN ('active', 'synced', 'archived'))
);

-- Indexes for efficient retrieval
CREATE INDEX idx_episodic_event_type ON arcus_episodic_memory(event_type);
CREATE INDEX idx_episodic_timestamp ON arcus_episodic_memory(timestamp DESC);
CREATE INDEX idx_episodic_participants ON arcus_episodic_memory USING GIN(participants);

CREATE INDEX idx_semantic_category ON arcus_semantic_memory(category);
CREATE INDEX idx_semantic_domain ON arcus_semantic_memory(domain);
CREATE INDEX idx_semantic_valid ON arcus_semantic_memory(valid_from, valid_until);

CREATE INDEX idx_procedural_type ON arcus_procedural_memory(procedure_type);
CREATE INDEX idx_procedural_name ON arcus_procedural_memory(name);
CREATE INDEX idx_procedural_last_used ON arcus_procedural_memory(last_used DESC);

CREATE INDEX idx_graph_source ON arcus_knowledge_graph(source_type, source_id);
CREATE INDEX idx_graph_target ON arcus_knowledge_graph(target_type, target_id);
CREATE INDEX idx_graph_relationship ON arcus_knowledge_graph(relationship);

CREATE INDEX idx_entities_type ON arcus_entities(entity_type);
CREATE INDEX idx_entities_name ON arcus_entities(name);

CREATE INDEX idx_audit_action ON arcus_autonomy_audit(action_type);
CREATE INDEX idx_audit_level ON arcus_autonomy_audit(autonomy_level);
CREATE INDEX idx_audit_executed ON arcus_autonomy_audit(executed_at DESC);

-- Vector similarity search indexes (for semantic search)
CREATE INDEX idx_episodic_embedding ON arcus_episodic_memory
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_semantic_embedding ON arcus_semantic_memory
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_procedural_embedding ON arcus_procedural_memory
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_entities_embedding ON arcus_entities
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Functions for common operations
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update triggers
CREATE TRIGGER update_episodic_modtime
  BEFORE UPDATE ON arcus_episodic_memory
  FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_semantic_modtime
  BEFORE UPDATE ON arcus_semantic_memory
  FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_procedural_modtime
  BEFORE UPDATE ON arcus_procedural_memory
  FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_graph_modtime
  BEFORE UPDATE ON arcus_knowledge_graph
  FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_entities_modtime
  BEFORE UPDATE ON arcus_entities
  FOR EACH ROW EXECUTE FUNCTION update_modified_column();
```

---

## Integration Architecture

### External System Integrations

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      INTEGRATION ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    INTEGRATION HUB                               │   │
│  │                                                                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │
│  │  │ Webhooks │  │   APIs   │  │   MCP    │  │  Zapier  │        │   │
│  │  │   In     │  │  Direct  │  │ Servers  │  │  Bridge  │        │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │   │
│  │       │             │             │             │               │   │
│  │       └─────────────┴──────┬──────┴─────────────┘               │   │
│  │                            │                                    │   │
│  │                    ┌───────▼───────┐                           │   │
│  │                    │  Integration  │                           │   │
│  │                    │   Manager     │                           │   │
│  │                    └───────────────┘                           │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  CONNECTED SYSTEMS                                                       │
│  ━━━━━━━━━━━━━━━━━                                                      │
│                                                                          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐             │
│  │  Asana  │    │  Gmail  │    │  Drive  │    │Supabase │             │
│  │ (Tasks) │    │ (Comms) │    │ (Docs)  │    │  (DB)   │             │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘             │
│       │              │              │              │                   │
│       ▼              ▼              ▼              ▼                   │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                  KNOWLEDGE EXTRACTION                         │    │
│  │                                                               │    │
│  │  Asana:                                                       │    │
│  │  • Task creation → Episodic (decision)                        │    │
│  │  • Project updates → Semantic (status)                        │    │
│  │  • Assignment → Graph (person-project)                        │    │
│  │                                                               │    │
│  │  Gmail:                                                       │    │
│  │  • Thread analysis → Relationship signals                     │    │
│  │  • Commitments → Procedural (follow-ups)                      │    │
│  │  • Tone → Graph (relationship temperature)                    │    │
│  │                                                               │    │
│  │  Drive:                                                       │    │
│  │  • Document edits → Episodic (collaboration)                  │    │
│  │  • Comments → Semantic (feedback)                             │    │
│  │  • Sharing → Graph (access relationships)                     │    │
│  │                                                               │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  FUTURE INTEGRATIONS                                                     │
│  ━━━━━━━━━━━━━━━━━━━                                                    │
│                                                                          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐             │
│  │  Slack  │    │  Zoom   │    │Calendar │    │  CRM    │             │
│  │ (Chat)  │    │ (Video) │    │ (Events)│    │(Clients)│             │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘             │
│                                                                          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐             │
│  │ GitHub  │    │ Notion  │    │ Linear  │    │QuickBook│             │
│  │ (Code)  │    │ (Wiki)  │    │ (Issues)│    │(Finance)│             │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA FLOW ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  INBOUND FLOW (Learning)                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━                                                │
│                                                                          │
│  [External Event] ──► [Webhook/API] ──► [Extraction Pipeline]           │
│         │                                        │                       │
│         │                                        ▼                       │
│         │                              ┌──────────────────┐             │
│         │                              │ Knowledge Router │             │
│         │                              └────────┬─────────┘             │
│         │                                       │                        │
│         │              ┌────────────────────────┼────────────────────┐  │
│         │              ▼            ▼           ▼          ▼         │  │
│         │         [Episodic]   [Semantic]  [Procedural]  [Graph]    │  │
│         │                                                            │  │
│         │                              │                             │  │
│         │                              ▼                             │  │
│         │                     [Vector Embedding]                     │  │
│         │                              │                             │  │
│         │                              ▼                             │  │
│         └─────────────────────► [Supabase Storage]                   │  │
│                                                                          │
│  OUTBOUND FLOW (Retrieval)                                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━                                              │
│                                                                          │
│  [Query/Context Need] ──► [Context Manager]                             │
│                                   │                                      │
│                    ┌──────────────┼──────────────┐                      │
│                    ▼              ▼              ▼                       │
│             [Semantic      [Pattern        [Graph                       │
│              Search]        Match]        Traversal]                    │
│                    │              │              │                       │
│                    └──────────────┼──────────────┘                      │
│                                   ▼                                      │
│                         [Context Assembler]                              │
│                                   │                                      │
│                                   ▼                                      │
│                         [Token Budget Check]                             │
│                                   │                                      │
│                                   ▼                                      │
│                         [Enriched Prompt]                                │
│                                                                          │
│  LEARNING LOOP                                                          │
│  ━━━━━━━━━━━━━━                                                         │
│                                                                          │
│  [Action Executed] ──► [Outcome Observed] ──► [Learning Engine]         │
│                                                        │                 │
│                              ┌─────────────────────────┘                 │
│                              ▼                                           │
│                    [Pattern Detection]                                   │
│                              │                                           │
│         ┌────────────────────┼────────────────────┐                     │
│         ▼                    ▼                    ▼                      │
│  [Workflow Success]   [Preference Signal]   [Error Pattern]            │
│         │                    │                    │                      │
│         ▼                    ▼                    ▼                      │
│  [Update Procedural] [Update Procedural] [Update Semantic]             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Security & Governance

### Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SECURITY ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  DATA PROTECTION                                                         │
│  ━━━━━━━━━━━━━━━━                                                       │
│                                                                          │
│  • All data encrypted at rest (Supabase)                                 │
│  • TLS 1.3 for all data in transit                                       │
│  • PII detection and redaction before storage                            │
│  • Secrets never stored in knowledge base                                │
│  • Row-level security for multi-tenant support                           │
│                                                                          │
│  ACCESS CONTROL                                                          │
│  ━━━━━━━━━━━━━━                                                         │
│                                                                          │
│  • Role-based access (admin, team, viewer)                               │
│  • API key authentication for integrations                               │
│  • Session-based access for Claude interactions                          │
│  • Audit logging for all access events                                   │
│                                                                          │
│  AUTONOMY GOVERNANCE                                                     │
│  ━━━━━━━━━━━━━━━━━━━                                                    │
│                                                                          │
│  • Explicit boundary definitions per autonomy level                      │
│  • All autonomous actions logged to audit table                          │
│  • Human override always available                                       │
│  • Automatic escalation on low confidence                                │
│  • Rate limiting on action types                                         │
│  • Financial actions always require human approval                       │
│                                                                          │
│  PRIVACY                                                                 │
│  ━━━━━━━━                                                               │
│                                                                          │
│  • User preference for data retention                                    │
│  • Right to deletion (with cascade)                                      │
│  • Anonymization for aggregate analysis                                  │
│  • No training on user data without consent                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Audit Requirements

| Event Type | Data Captured | Retention |
|------------|---------------|-----------|
| Knowledge capture | Source, type, confidence | 2 years |
| Knowledge retrieval | Query, results, context used | 1 year |
| Autonomous action | Action, reasoning, boundary check | 3 years |
| Human override | Original action, override reason | 3 years |
| Session activity | Start/end, interactions count | 1 year |
| Integration sync | System, records synced, errors | 6 months |

---

## Technology Stack

### Recommended Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **LLM** | Claude (Anthropic) | Already integrated, extended thinking |
| **Database** | Supabase (PostgreSQL) | Already integrated, real-time, vectors |
| **Vector Store** | pgvector (via Supabase) | No additional infra needed |
| **File Storage** | Git + Google Drive | Version control + collaboration |
| **Voice STT** | Deepgram | Low latency, real-time streaming |
| **Voice TTS** | ElevenLabs | Natural voices, voice cloning |
| **Real-time Transport** | WebRTC + WebSockets | Low latency voice + state sync |
| **Framework** | Next.js 14 | Already using for dashboard |
| **Automation** | Zapier + Hooks | Already integrated |
| **Meeting Integration** | Zoom SDK | Widest enterprise adoption |

### Infrastructure Requirements

**Phase 1-2 (Foundation + Intelligence)**
- Supabase Pro plan ($25/month) - for pgvector and higher limits
- No additional infrastructure needed

**Phase 3 (Voice)**
- Deepgram API (~$0.0125/minute)
- ElevenLabs API (~$0.30/1000 characters)
- WebRTC server (can use Twilio or self-hosted)
- Estimated: $100-300/month for moderate usage

**Phase 4-5 (Autonomy + Chief of Staff)**
- Dedicated vector search (if scale requires)
- Background job processing (can use Vercel Cron or dedicated)
- Monitoring/observability (Datadog, Sentry)
- Estimated: $200-500/month

---

## Next Steps

### Immediate Actions (This Session)

1. **Create CLAUDE.memory.md** - Initialize session state file
2. **Create Supabase schema** - SQL file for Phase 1 tables
3. **Build knowledge capture hooks** - Basic learning triggers
4. **Update hooks.json** - Add knowledge repository hooks

### Week 1 Goals

1. Basic LEARN operation working (manual capture)
2. Basic RECALL operation working (session start context)
3. CLAUDE.memory.md syncing preferences
4. First knowledge entries stored

### Success Metrics

| Metric | Phase 1 Target | Ultimate Target |
|--------|----------------|-----------------|
| Knowledge entries | 100+ | 10,000+ |
| Session context injection | 80% relevance | 95% relevance |
| Autonomous action success | N/A | 98%+ |
| Voice response latency | N/A | <500ms |
| User correction rate | Baseline | 50% reduction |

---

## Appendix: Reference Documents

- Agent Planning Dashboard types: `intelligence-dashboard/src/components/agent-planning/data/types.ts`
- Intelligence Extractor patterns: `.claude/skills/intelligence-extractor/SKILL.md`
- Existing hooks: `.claude/hooks/hooks.json`
- Plugin manifest: `plugin.json`
- CLAUDE.md: Main workspace documentation

---

**Document Status:** Draft
**Next Review:** After Phase 1 implementation
**Owner:** Arcus Innovation Studios
