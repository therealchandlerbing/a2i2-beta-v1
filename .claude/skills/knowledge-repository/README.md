# Arcus Knowledge Repository

**Transform Claude from a stateless assistant into a learning, remembering, orchestrating AI companion.**

---

## Overview

The Arcus Knowledge Repository is a persistent memory and orchestration system that enables Claude to:

- **Remember** everything across sessions
- **Learn** from every interaction
- **Build relationships** between people, organizations, and concepts
- **Anticipate needs** based on patterns
- **Act with increasing autonomy** as trust is earned
- **Orchestrate** multiple models and tools efficiently *(NEW)*

This is the foundation for building an AI companion like R2-D2 or the Enterprise computer - one that knows your organization deeply, coordinates intelligently, and grows more capable over time.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                    🧠 ARCUS KNOWLEDGE REPOSITORY                             │
│                                                                              │
│         Memory Foundation  ──►  Learn from every interaction                 │
│         Model Orchestration ──►  Route to optimal models/tools               │
│         Trust Progression  ──►  Earn autonomy over time                      │
│                                                                              │
│                   "The AI companion that remembers and improves"             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

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

### Model/Tool Patterns *(NEW - ToolOrchestra-inspired)*
- Which models work best for which task types
- Successful tool sequences and combinations
- Cost/latency optimization over time
- Cross-session learning from outcomes

---

## Model Orchestration *(NEW)*

Inspired by NVIDIA's [ToolOrchestra](https://github.com/NVlabs/ToolOrchestra), the knowledge repository now includes intelligent model routing.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MODEL ORCHESTRATION FLOW                              │
│                                                                              │
│   ┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐        │
│   │   Request   │ ──►  │   Model Router   │ ──►  │  Selected Model │        │
│   └─────────────┘      └──────────────────┘      └─────────────────┘        │
│                               │                                              │
│                   ┌───────────┼───────────┐                                  │
│                   ▼           ▼           ▼                                  │
│            ┌──────────┐ ┌──────────┐ ┌──────────┐                           │
│            │ User     │ │Historical│ │   Cost/  │                           │
│            │Preference│ │ Patterns │ │ Latency  │                           │
│            │ Vectors  │ │          │ │Constraints│                           │
│            └──────────┘ └──────────┘ └──────────┘                           │
│                                                                              │
│   AVAILABLE MODELS:                                                          │
│   ┌────────────┬────────────┬────────────┬────────────┬────────────┐        │
│   │ Claude     │ Gemini 3   │ Gemini 3   │ PersonaPlex│ Deep       │        │
│   │ Opus/Sonnet│ Pro        │ Flash      │ (Voice)    │ Research   │        │
│   └────────────┴────────────┴────────────┴────────────┴────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **User Preference Vectors** | Numerical preferences that modify routing (accuracy vs cost vs latency) |
| **Model Patterns** | Learn which models succeed for which task types |
| **Efficiency Tracking** | Track cost, latency, tokens for every action |
| **Outcome Learning** | Improve routing based on historical success rates |

### Quick Example

```python
from model_router import ModelRouter

router = ModelRouter()

# Route to best model for a task
decision = router.route(
    task="Analyze this financial document",
    context="document_analysis",
    preference_context="cost_sensitive"  # Use cost-optimized preferences
)

print(f"Model: {decision.model_id}")        # gemini-3-flash
print(f"Thinking: {decision.thinking_level}")  # medium
print(f"Cost: ${decision.estimated_cost:.4f}") # $0.0012

# After task completes, record outcome
router.record_outcome(
    decision=decision,
    success=True,
    actual_cost=0.0015,
    actual_latency=800
)  # This improves future routing!
```

### Preference Vectors

Customize routing behavior per user and context:

```
┌─────────────────────────────────────────────────────────────┐
│              USER PREFERENCE VECTOR                          │
│                                                              │
│   Objective Weights (sum to 1.0):                            │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Accuracy: 0.5  │  Cost: 0.3  │  Latency: 0.2     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   Model Preferences (0.0 = avoid, 1.0 = prefer):            │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  claude-opus: 0.3   (avoid expensive)              │   │
│   │  gemini-3-flash: 0.8 (prefer balanced)             │   │
│   │  personaplex: 0.9   (strongly prefer for voice)    │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   Context Overrides:                                         │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  confidential_data: {web_search: 0.0}              │   │
│   │  time_critical: {latency_weight: 0.7}              │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

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
├── SKILL.md                 # Claude's operational instructions
├── README.md                # This file
├── QUICK-START.md           # Fast reference guide
├── INDEX.md                 # Navigation guide
│
├── docs/
│   ├── ARCHITECTURE.md      # Complete technical architecture
│   ├── VISION.md            # Long-term vision document
│   └── TOOLORCHESTRA-REVIEW.md  # ToolOrchestra analysis & enhancements
│
├── schemas/
│   └── supabase-schema.sql  # Database schema (incl. orchestration tables)
│
├── src/
│   ├── types.ts             # TypeScript type definitions
│   ├── knowledge_operations.py  # Core Python operations
│   └── model_router.py      # Intelligent model routing (NEW)
│
├── config/
│   └── memory-template.md   # Template for CLAUDE.memory.md
│
└── modules/                 # Future: modular extensions
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

### Phase 1.5: Orchestration Enhancements (In Progress)
- RL-based routing optimization
- Real-time constraint adaptation
- A/B testing framework for models
- Complexity classifier integration

### Phase 2: Intelligence (Planned)
- Vector embeddings for semantic search
- Pattern detection and recommendations
- Automatic context injection

### Phase 3: Voice (Planned)
- Real-time voice interface via PersonaPlex
- Voice memory (transcription + context)
- Meeting integration with knowledge extraction

### Phase 4: Autonomy (Planned)
- Pre-approved action categories
- Proactive task execution
- Self-correction and learning
- Federated organizational intelligence

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

### v1.1.0 (2026-01-25)
- **Model Orchestration** - Intelligent routing inspired by NVIDIA ToolOrchestra
- **User Preference Vectors** - Customizable accuracy/cost/latency weights
- **Model Patterns** - Cross-session learning from outcomes
- **Efficiency Tracking** - Cost, latency, and token tracking per request
- New `model_router.py` for intelligent model selection
- New `knowledge_operations.py` with orchestration methods
- Enhanced Supabase schema with `arcus_model_patterns` and `arcus_user_preference_vectors` tables
- ToolOrchestra review document with enhancement roadmap

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
