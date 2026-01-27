---
name: Arcus Knowledge Repository
description: Persistent, modular knowledge system that enables Claude to learn, remember, and grow with Arcus Innovation Studios across all sessions
version: 1.0.0
author: Arcus Innovation Studios
created: 2026-01-24
updated: 2026-01-24
category: infrastructure
complexity: high
dependencies:
  - Supabase (persistent storage)
  - CLAUDE.memory.md (session state)
  - Git (version control)
outputs:
  - Knowledge entries (JSON)
  - Memory updates (Markdown)
  - Context injection (automatic)
---

# Arcus Knowledge Repository

## Purpose

The Arcus Knowledge Repository transforms Claude from a stateless assistant into a **living, learning partner** that:

1. **Remembers** - Retains learnings across sessions
2. **Learns** - Captures patterns from every interaction
3. **Adapts** - Customizes responses based on accumulated knowledge
4. **Grows** - Builds institutional memory over time

This is the **central nervous system** for the Arcus Innovation Studios workspace.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARCUS KNOWLEDGE REPOSITORY                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   SESSION   │    │  PERSISTENT │    │   MODULAR   │         │
│  │   MEMORY    │◄──►│   STORAGE   │◄──►│   MODULES   │         │
│  │ (memory.md) │    │  (Supabase) │    │  (plugins)  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌─────────────────────────────────────────────────────────────┐
│  │                    MEMORY TYPES                              │
│  ├─────────────┬─────────────┬─────────────┬─────────────┬─────┤
│  │  Episodic   │  Semantic   │ Procedural  │   Working   │Graph│
│  │ (events)    │ (facts)     │ (workflows) │ (context)   │(rel)│
│  └─────────────┴─────────────┴─────────────┴─────────────┴─────┘
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐
│  │                    RETRIEVAL LAYER                           │
│  │  • Semantic search (embeddings)                              │
│  │  • Pattern matching (templates)                              │
│  │  • Relationship traversal (graph)                            │
│  │  • Temporal queries (time-based)                             │
│  └─────────────────────────────────────────────────────────────┘
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Memory Types

### 1. Episodic Memory (What Happened)
- **Past interactions**: Conversations, outcomes, decisions
- **Events**: Meetings, milestones, deliverables
- **Learnings**: What worked, what didn't, lessons learned
- **Stored in**: `arcus_episodic_memory` table

### 2. Semantic Memory (What We Know)
- **Domain facts**: About Arcus, clients, partners, industry
- **Patterns**: Recurring themes, successful approaches
- **Frameworks**: Mental models, decision trees
- **Stored in**: `arcus_semantic_memory` table

### 3. Procedural Memory (How We Work)
- **Workflows**: Step-by-step processes
- **Preferences**: User preferences, communication styles
- **Standards**: Formatting, tone, output expectations
- **Stored in**: `arcus_procedural_memory` table + `CLAUDE.memory.md`

### 4. Working Memory (Current Context)
- **Active session**: Current task, conversation context
- **Relevant history**: Retrieved knowledge for current task
- **Temporary state**: Draft outputs, intermediate results
- **Stored in**: Session context (ephemeral)

### 5. Relationship Graph (How Things Connect)
- **Entities**: People, organizations, projects, concepts
- **Relationships**: Who knows who, what's related to what
- **Influence**: Who affects decisions, what drives outcomes
- **Stored in**: `arcus_entities` (nodes) + `arcus_relationships` (edges) tables

## Core Operations

### LEARN: Capture Knowledge

When Claude learns something new, it should be captured:

```
LEARN [memory_type] [content] [context]
```

**Auto-capture triggers:**
- User corrects Claude → Capture preference/standard
- Successful workflow → Capture procedural pattern
- New information shared → Capture semantic fact
- Decision made → Capture episodic event
- Relationship revealed → Update knowledge graph

**Example captures:**
```json
{
  "type": "procedural",
  "category": "preference",
  "content": "User prefers concise responses without emojis",
  "confidence": 0.9,
  "source": "user_correction",
  "timestamp": "2026-01-24T10:30:00Z"
}
```

### RECALL: Retrieve Knowledge

When Claude needs context, retrieve relevant knowledge:

```
RECALL [query] [memory_types] [limit]
```

**Auto-recall triggers:**
- Session start → Load user preferences, recent context
- Task matching → Retrieve relevant procedures
- Entity mentioned → Pull relationship graph
- Similar situation → Find episodic precedents

**Example recall:**
```json
{
  "query": "How does Arcus typically handle client proposals?",
  "memory_types": ["procedural", "episodic"],
  "results": [
    {
      "type": "procedural",
      "content": "Use 360-proposal-builder skill with executive-grade formatting",
      "confidence": 0.95,
      "last_used": "2026-01-20"
    },
    {
      "type": "episodic",
      "content": "Last proposal for TechCorp used innovation-focused framing, well received",
      "relevance": 0.87
    }
  ]
}
```

### RELATE: Build Connections

Connect entities in the knowledge graph:

```
RELATE [entity1] [relationship] [entity2] [properties]
```

**Example relationships:**
```json
{
  "entity1": {"type": "person", "name": "Sarah Chen"},
  "relationship": "decision_maker_at",
  "entity2": {"type": "organization", "name": "TechCorp"},
  "properties": {
    "role": "Chief Innovation Officer",
    "influence_level": "high",
    "communication_style": "direct",
    "first_contact": "2025-11-15"
  }
}
```

### REFLECT: Synthesize Learnings

Periodically synthesize raw captures into higher-level insights:

```
REFLECT [time_period] [focus_area]
```

**Example reflection:**
```json
{
  "period": "2026-01",
  "insights": [
    {
      "pattern": "Client proposals with SROI metrics have 40% higher acceptance",
      "evidence_count": 5,
      "confidence": 0.85,
      "recommendation": "Include SROI calculations in all future proposals"
    },
    {
      "pattern": "Eduardo prefers email communication before 2pm São Paulo time",
      "evidence_count": 8,
      "confidence": 0.92,
      "recommendation": "Schedule Eduardo-related tasks for morning"
    }
  ]
}
```

## Modular Architecture

### Module System

Knowledge repository is **extensible through modules**:

```
modules/
├── client-intelligence/     # Client-specific knowledge
├── project-memory/          # Project histories and patterns
├── team-preferences/        # Individual team member settings
├── industry-knowledge/      # Domain expertise
├── workflow-patterns/       # Successful workflow templates
└── custom/                  # User-defined modules
```

### Module Interface

Each module follows a standard interface:

```typescript
interface KnowledgeModule {
  name: string;
  version: string;

  // What this module captures
  captureTypes: string[];

  // How to extract knowledge from interactions
  extractors: Extractor[];

  // How to retrieve relevant knowledge
  retrievers: Retriever[];

  // How to synthesize insights
  reflectors: Reflector[];

  // Schema for stored data
  schema: JSONSchema;
}
```

### Built-in Modules

#### 1. Client Intelligence Module
Captures and retrieves client-specific knowledge:
- Communication preferences
- Decision-making patterns
- Past project outcomes
- Key stakeholders
- Strategic priorities

#### 2. Project Memory Module
Tracks project histories:
- Successful approaches
- Lessons learned
- Deliverable templates
- Timeline patterns
- Risk factors

#### 3. Team Preferences Module
Learns individual team member preferences:
- Communication styles
- Work patterns
- Tool preferences
- Formatting standards
- Review requirements

#### 4. Workflow Patterns Module
Captures successful workflows:
- Skill combinations
- Sequencing patterns
- Error recovery approaches
- Optimization opportunities

## Integration Points

### 1. CLAUDE.memory.md Integration

The `CLAUDE.memory.md` file serves as **session state**:

```markdown
---
last_updated: 2026-01-24T10:30:00Z
session_count: 147
---

# User Preferences
- Response style: Concise, technical
- Emoji usage: Never unless requested
- Code style: TypeScript preferred
- Documentation: Inline comments only when complex

# Active Projects
- AI Agent Planning Dashboard (priority: high)
- Knowledge Repository Setup (priority: high)
- 990-EZ Filing Q4 (priority: medium)

# Recent Learnings
- User prefers modular architecture patterns
- Arcus Innovation Studios is the organization name
- Team includes: Chandler, Eduardo, Felipe

# Pending Actions
- [ ] Complete knowledge repository setup
- [ ] Run skill validation
- [ ] Update README
```

### 2. Supabase Tables

**Core tables:**

```sql
-- Episodic memory (events and interactions)
CREATE TABLE arcus_episodic_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type TEXT NOT NULL,
  content JSONB NOT NULL,
  participants TEXT[],
  outcome TEXT,
  learnings TEXT[],
  confidence FLOAT DEFAULT 0.8,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  session_id TEXT,
  embedding VECTOR(1536)
);

-- Semantic memory (facts and patterns)
CREATE TABLE arcus_semantic_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category TEXT NOT NULL,
  content TEXT NOT NULL,
  metadata JSONB,
  confidence FLOAT DEFAULT 0.8,
  source TEXT,
  valid_from TIMESTAMPTZ DEFAULT NOW(),
  valid_until TIMESTAMPTZ,
  embedding VECTOR(1536)
);

-- Procedural memory (workflows and preferences)
CREATE TABLE arcus_procedural_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  procedure_type TEXT NOT NULL,  -- 'workflow' | 'preference' | 'standard'
  name TEXT NOT NULL,
  content JSONB NOT NULL,
  trigger_conditions TEXT[],
  success_rate FLOAT,
  usage_count INT DEFAULT 0,
  last_used TIMESTAMPTZ,
  embedding VECTOR(1536)
);

-- Knowledge graph: entities (nodes)
CREATE TABLE arcus_entities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_type TEXT NOT NULL,  -- person, organization, project, concept
  name TEXT NOT NULL,
  description TEXT,
  aliases TEXT[],
  attributes JSONB,
  embedding VECTOR(1536),
  confidence FLOAT DEFAULT 0.8,
  first_seen TIMESTAMPTZ DEFAULT NOW(),
  last_seen TIMESTAMPTZ DEFAULT NOW()
);

-- Knowledge graph: relationships (edges)
CREATE TABLE arcus_relationships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_entity_id UUID NOT NULL REFERENCES arcus_entities(id),
  source_type TEXT NOT NULL,
  source_name TEXT NOT NULL,
  relationship TEXT NOT NULL,  -- works_at, reports_to, owns, etc.
  target_entity_id UUID NOT NULL REFERENCES arcus_entities(id),
  target_type TEXT NOT NULL,
  target_name TEXT NOT NULL,
  properties JSONB,
  confidence FLOAT DEFAULT 0.8,
  first_observed TIMESTAMPTZ DEFAULT NOW(),
  last_observed TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for fast retrieval
CREATE INDEX idx_episodic_event_type ON arcus_episodic_memory(event_type);
CREATE INDEX idx_episodic_timestamp ON arcus_episodic_memory(timestamp);
CREATE INDEX idx_semantic_category ON arcus_semantic_memory(category);
CREATE INDEX idx_procedural_type ON arcus_procedural_memory(procedure_type);
CREATE INDEX idx_entities_type ON arcus_entities(entity_type);
CREATE INDEX idx_entities_name ON arcus_entities(name);
CREATE INDEX idx_rel_source ON arcus_relationships(source_entity_id);
CREATE INDEX idx_rel_target ON arcus_relationships(target_entity_id);
CREATE INDEX idx_rel_relationship ON arcus_relationships(relationship);
```

### 3. Hook Integration

Knowledge capture hooks in `.claude/hooks/hooks.json`:

```json
{
  "PostToolUse": [
    "knowledge-repository: Capture successful tool usage patterns",
    "knowledge-repository: Extract entities from tool outputs"
  ],
  "SessionStart": [
    "knowledge-repository: Load user preferences from CLAUDE.memory.md",
    "knowledge-repository: Retrieve recent context from Supabase"
  ],
  "SessionEnd": [
    "knowledge-repository: Sync session learnings to persistent storage",
    "knowledge-repository: Update CLAUDE.memory.md with new insights"
  ],
  "PreToolUse": [
    "knowledge-repository: Inject relevant context for tool"
  ]
}
```

## Execution Instructions

### When to Use This Skill

**Automatically invoke when:**
- Session starts (load preferences, recent context)
- User mentions a known entity (retrieve relationships)
- Task matches a known workflow (retrieve procedure)
- User provides correction or feedback (capture learning)
- Decision is made (capture episodic event)
- Session ends (sync learnings)

**Manually invoke when:**
- User says "remember this" or "learn this"
- User asks "what do you know about X?"
- User says "how have we handled Y before?"
- User requests context from past interactions

### Step-by-Step Execution

#### 1. Session Start (Automatic)

1. Read `CLAUDE.memory.md` for preferences and active context
2. Query recent episodic memories (last 7 days)
3. Load active project context
4. Inject preferences into system prompt

#### 2. During Interaction

1. Monitor for capture triggers (corrections, decisions, new info)
2. Queue learnings for batch capture
3. Retrieve relevant context when entities mentioned
4. Update working memory with current task context

#### 3. Explicit Knowledge Request

When user asks about knowledge:

1. Parse query intent (recall vs. learn vs. relate)
2. Determine relevant memory types
3. Execute appropriate operation
4. Format response for user

#### 4. Session End (Automatic)

1. Batch capture queued learnings to Supabase
2. Update `CLAUDE.memory.md` with new preferences
3. Run reflection on session (if significant learnings)
4. Update relationship graph with new entities

## Quality Standards

### Confidence Scoring

- **0.9-1.0**: Explicit user statement, direct evidence
- **0.7-0.9**: Strong inference, multiple indicators
- **0.5-0.7**: Reasonable inference, limited evidence
- **0.3-0.5**: Weak inference, should verify
- **0.0-0.3**: Speculation, flagged for review

### Knowledge Validation

Before storing:
- Check for contradictions with existing knowledge
- Validate entity references exist
- Ensure minimum confidence threshold (0.5)
- Flag sensitive information for review

### Privacy and Security

- Never store credentials, API keys, or secrets
- Redact PII when storing external communications
- Flag confidential information
- Respect user privacy preferences

## Error Handling

### Storage Failures

If Supabase unavailable:
1. Store in local queue (session memory)
2. Retry on next session
3. Fall back to `CLAUDE.memory.md` for critical preferences

### Retrieval Failures

If retrieval fails:
1. Proceed without context injection
2. Note gap in working memory
3. Ask user for clarification if needed

### Conflict Resolution

When new knowledge conflicts with existing:
1. Compare confidence scores
2. Consider recency (newer typically wins)
3. Flag for user review if both high confidence
4. Store both with conflict metadata

## Usage Examples

### Example 1: Learning a Preference

**User says:** "Actually, I prefer TypeScript over Python for new projects"

**Claude captures:**
```json
{
  "type": "procedural",
  "procedure_type": "preference",
  "name": "language_preference",
  "content": {
    "preference": "TypeScript",
    "over": "Python",
    "context": "new projects",
    "strength": "prefer"
  },
  "confidence": 0.95,
  "source": "explicit_user_statement"
}
```

### Example 2: Recording a Decision

**Context:** User decides to use LangGraph for their agent framework

**Claude captures:**
```json
{
  "type": "episodic",
  "event_type": "decision",
  "content": {
    "decision": "Use LangGraph as primary agent framework",
    "context": "AI Agent Planning Dashboard project",
    "rationale": "Team expertise, existing Python stack",
    "alternatives_considered": ["CrewAI", "Claude Code native"]
  },
  "participants": ["Chandler"],
  "outcome": "Selected LangGraph",
  "confidence": 0.95
}
```

### Example 3: Building a Relationship

**Extracted from meeting notes:**
```json
{
  "entity1": {"type": "organization", "name": "TechCorp"},
  "relationship": "potential_client",
  "entity2": {"type": "organization", "name": "Arcus Innovation Studios"},
  "properties": {
    "stage": "initial_contact",
    "interest_area": "AI strategy",
    "key_contact": "Sarah Chen",
    "introduced_by": "Board connection"
  }
}
```

### Example 4: Recalling Context

**User asks:** "How did we approach the last innovation assessment?"

**Claude retrieves:**
```json
{
  "query_result": {
    "episodic": [
      {
        "event": "TRL Assessment for BioTech Startup",
        "date": "2025-12-15",
        "approach": "Used innovation-compass-assessment skill",
        "outcome": "Client satisfied, led to follow-on engagement"
      }
    ],
    "procedural": [
      {
        "workflow": "Innovation Assessment Standard",
        "steps": [
          "Gather technology documentation",
          "Run innovation-compass-assessment",
          "Generate executive summary",
          "Schedule findings review"
        ]
      }
    ]
  }
}
```

## Version History

### v1.0.0 (2026-01-24)
- Initial release
- Four memory types: episodic, semantic, procedural, working
- Knowledge graph for relationships
- Modular architecture
- CLAUDE.memory.md integration
- Supabase persistence layer
- Auto-capture triggers
- Hook integration

---

## Quick Reference

| Operation | Command | When to Use |
|-----------|---------|-------------|
| LEARN | Capture new knowledge | User correction, new info, decision |
| RECALL | Retrieve relevant knowledge | Entity mentioned, similar situation |
| RELATE | Build relationship graph | New connection discovered |
| REFLECT | Synthesize insights | Periodic review, pattern detection |

## Integration Checklist

- [ ] Create Supabase tables (see `schemas/supabase-schema.sql`)
- [ ] Initialize `CLAUDE.memory.md` (see `config/memory-template.md`)
- [ ] Configure hooks (see `config/hooks-config.json`)
- [ ] Load initial knowledge (import existing data)
- [ ] Test retrieval with sample queries
- [ ] Enable auto-capture triggers
