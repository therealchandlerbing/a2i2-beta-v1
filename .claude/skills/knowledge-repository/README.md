# Arcus Knowledge Repository

**Transform Claude from a stateless assistant into a learning, remembering AI companion.**

---

## Overview

The Arcus Knowledge Repository is a persistent memory system that enables Claude to:

- **Remember** everything across sessions
- **Learn** from every interaction
- **Build relationships** between people, organizations, and concepts
- **Anticipate needs** based on patterns
- **Act with increasing autonomy** as trust is earned

This is the foundation for building an AI companion like R2-D2 or the Enterprise computer - one that knows your organization deeply and grows more capable over time.

## Quick Start

### 1. Read the Architecture

Before implementation, understand the system design:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Complete technical architecture
- **[VISION.md](docs/VISION.md)** - Long-term vision (R2-D2/Enterprise computer)
- **[SKILL.md](SKILL.md)** - Claude's operational instructions

### 2. Deploy the Database Schema

Run the Supabase schema to create the knowledge tables:

```sql
-- In Supabase SQL Editor, run:
-- schemas/supabase-schema.sql
```

### 3. Initialize Session Memory

The `CLAUDE.memory.md` file at the repository root tracks session state:

```markdown
# User Preferences
- Response style: Concise, technical
- Emoji usage: Never unless requested
...
```

Claude reads this at session start and updates it with learnings.

### 4. Start Learning

Claude will automatically:
- Capture corrections as preferences
- Record decisions as episodic memory
- Extract entities and relationships
- Build patterns from successful workflows

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  ARCUS KNOWLEDGE REPOSITORY                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SESSION LAYER           PERSISTENT LAYER        GRAPH LAYER   │
│  ┌─────────────┐        ┌─────────────┐        ┌─────────────┐ │
│  │ CLAUDE      │        │  Supabase   │        │  Knowledge  │ │
│  │ .memory.md  │◄──────►│  Tables     │◄──────►│  Graph      │ │
│  └─────────────┘        └─────────────┘        └─────────────┘ │
│                                                                  │
│  MEMORY TYPES                                                    │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │
│  │Episodic│ │Semantic│ │Proced- │ │Working │ │ Graph  │       │
│  │(events)│ │(facts) │ │ural   │ │(session)│ │(relate)│       │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Memory Types

### Episodic Memory (What Happened)
- Conversations and interactions
- Decisions made and their outcomes
- Meetings and milestones
- Errors and successes (learning opportunities)

### Semantic Memory (What We Know)
- Facts about the organization, clients, industry
- Patterns observed over time
- Frameworks and mental models
- Best practices and insights

### Procedural Memory (How We Work)
- Workflows and step-by-step processes
- User preferences and standards
- Decision trees and shortcuts
- Successful automation patterns

### Knowledge Graph (How Things Connect)
- People and organizations
- Relationships (works_at, knows, client_of, etc.)
- Projects and their associations
- Influence and decision networks

## Core Operations

### LEARN - Capture Knowledge

Claude automatically captures:
- User corrections → Preferences
- Successful workflows → Procedures
- New information → Facts
- Decisions made → Events
- Relationships discovered → Graph edges

Manual capture:
```
"Remember that Sarah prefers email over Slack"
"Learn that TechCorp decisions require board approval"
```

### RECALL - Retrieve Knowledge

Claude automatically retrieves:
- Preferences at session start
- Relevant context when entities mentioned
- Similar past situations for guidance

Manual recall:
```
"What do you know about TechCorp?"
"How have we handled similar proposals before?"
```

### RELATE - Build Connections

Claude automatically connects:
- People to organizations
- Projects to stakeholders
- Decisions to outcomes

Manual relationships:
```
"Sarah introduced us to James at TechCorp"
"This project depends on the API integration"
```

### REFLECT - Synthesize Insights

Periodic synthesis:
- Patterns from multiple interactions
- Workflow optimizations
- Relationship network analysis

## File Structure

```
.claude/skills/knowledge-repository/
├── SKILL.md              # Claude's operational instructions
├── README.md             # This file
├── QUICK-START.md        # Fast reference guide
│
├── docs/
│   ├── ARCHITECTURE.md   # Complete technical architecture
│   └── VISION.md         # Long-term vision document
│
├── schemas/
│   └── supabase-schema.sql  # Database schema
│
├── src/
│   └── types.ts          # TypeScript type definitions
│
├── config/
│   └── memory-template.md   # Template for CLAUDE.memory.md
│
└── modules/              # Future: modular extensions
    ├── client-intelligence/
    ├── project-memory/
    └── team-preferences/
```

## Integration Points

### Existing Skills
The knowledge repository enhances all existing skills:
- **Intelligence Extractor** → Feeds extracted data into knowledge graph
- **CEO Advisor** → Uses historical context for briefings
- **Skill Orchestrator** → Retrieves relevant procedures

### Supabase
Already integrated for the Intelligence Dashboard. Knowledge repository uses the same connection.

### Hooks
Knowledge capture hooks can be added to `.claude/hooks/hooks.json`:
```json
{
  "PostToolUse": [
    "knowledge-repository: Capture successful tool patterns"
  ],
  "SessionStart": [
    "knowledge-repository: Load user preferences"
  ]
}
```

## Autonomy Progression

The system tracks trust and expands autonomy over time:

| Level | Name | Description |
|-------|------|-------------|
| 0 | Assisted | Claude advises, human executes |
| 1 | Supervised | Claude proposes, human confirms |
| 2 | Autonomous | Claude acts, human reviews after |
| 3 | Trusted | Claude acts, exceptions only |
| 4 | Partner | Full peer-level collaboration |

Currently starting at Level 0, building trust through successful interactions.

## Future Capabilities

### Phase 2: Intelligence (Planned)
- Vector embeddings for semantic search
- Pattern detection and recommendations
- Automatic context injection

### Phase 3: Voice (Planned)
- Real-time voice interface
- Voice memory (transcription + context)
- Meeting integration

### Phase 4: Autonomy (Planned)
- Pre-approved action categories
- Proactive task execution
- Self-correction and learning

## Configuration

### Environment Variables

For Supabase integration (already configured in project):
```
NEXT_PUBLIC_SUPABASE_URL=your-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### CLAUDE.memory.md

Located at repository root, this file:
- Is read at every session start
- Contains current preferences and context
- Is updated with new learnings
- Can be manually edited (changes preserved)

## Best Practices

### For Effective Learning

1. **Provide corrections explicitly** - "Actually, I prefer X over Y"
2. **Share context** - "We've worked with TechCorp before on..."
3. **Confirm outcomes** - "That worked well" or "Let's try differently"

### For Privacy

1. **Sensitive data** - Automatically flagged, not stored without review
2. **Credentials** - Never stored in knowledge base
3. **External data** - PII redacted before storage

### For Trust Building

1. **Start supervised** - Confirm actions to build baseline
2. **Provide feedback** - Corrections help Claude learn faster
3. **Be consistent** - Regular patterns are easier to learn

## Troubleshooting

### Knowledge Not Persisting
- Check Supabase connection
- Verify schema is deployed
- Check CLAUDE.memory.md exists

### Wrong Context Retrieved
- Confidence scores may need adjustment
- Check entity names for consistency
- Review recent captures in memory log

### Autonomy Not Progressing
- Review boundary definitions
- Check audit log for patterns
- Ensure feedback is being provided

## Version History

### v1.0.0 (2026-01-24)
- Initial architecture design
- Five memory types implemented
- Supabase schema created
- Session state file (CLAUDE.memory.md)
- TypeScript type definitions
- Autonomy progression framework

## Contributing

This skill is part of the Arcus Innovation Studios workspace. For changes:

1. Create feature branch from `main`
2. Update relevant documentation
3. Test with sample interactions
4. Submit PR for review

## License

Internal use - Arcus Innovation Studios

---

**"The journey of a thousand light years begins with a single knowledge entry."**

*Building the AI companion we'll need for tomorrow, starting today.*
