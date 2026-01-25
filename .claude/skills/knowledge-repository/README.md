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

## Skill Orchestration Layer *(NEW - Phase 2)*

The skill orchestration layer coordinates multiple skills with intelligent context management.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SKILL ORCHESTRATION ARCHITECTURE                         │
│                                                                              │
│   ┌─────────────┐                                                           │
│   │    Task     │                                                           │
│   │  "Research  │                                                           │
│   │  TechCorp"  │                                                           │
│   └──────┬──────┘                                                           │
│          │                                                                   │
│          ▼                                                                   │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │                    SKILL ORCHESTRATOR                            │       │
│   │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │       │
│   │  │ Skill         │  │ Context       │  │ Model         │       │       │
│   │  │ Registry      │  │ Budget        │  │ Router        │       │       │
│   │  │               │  │ Manager       │  │               │       │       │
│   │  └───────────────┘  └───────────────┘  └───────────────┘       │       │
│   └─────────────────────────────────────────────────────────────────┘       │
│          │                      │                     │                      │
│          ▼                      ▼                     ▼                      │
│   ┌─────────────┐        ┌─────────────┐       ┌─────────────┐              │
│   │ Knowledge   │        │ Context     │       │ Gemini 3    │              │
│   │ Repository  │        │ Assembly    │       │ Pro         │              │
│   │ (recall)    │        │ (pack)      │       │             │              │
│   └─────────────┘        └─────────────┘       └─────────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Description |
|-----------|-------------|
| **Skill Registry** | Register and discover skills by capability |
| **Context Budget Manager** | Allocate tokens across memory types |
| **Skill Executor** | Execute skills with timeout and retry handling |
| **Outcome Learning** | Record outcomes to improve future orchestration |

### Quick Example

```python
from skill_orchestrator import SkillOrchestrator

orchestrator = SkillOrchestrator()

# Execute an orchestrated task
result = await orchestrator.execute(
    task="Find all information about TechCorp and their preferences",
    context="research",
    user_id="default"
)

print(f"Status: {result.status.value}")
print(f"Skills executed: {len(result.skill_results)}")
print(f"Total latency: {result.total_latency_ms}ms")
print(f"Context tokens: {result.context_assembled.total_tokens}")
```

---

## Dynamic Context Budgeting *(NEW - Phase 2)*

Intelligent context management that maximizes knowledge injection within model limits.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CONTEXT BUDGET FLOW                                      │
│                                                                              │
│   Model Context: 200,000 tokens                                              │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │                                                                   │       │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────────────────┐  │       │
│   │  │ System  │  │Response │  │Overhead │  │ Available for     │  │       │
│   │  │ Prompt  │  │ Reserve │  │  (15%)  │  │ Context: 161,000  │  │       │
│   │  │ 5,000   │  │ 4,000   │  │ 30,000  │  │                   │  │       │
│   │  └─────────┘  └─────────┘  └─────────┘  └───────────────────┘  │       │
│   │                                                                   │       │
│   └─────────────────────────────────────────────────────────────────┘       │
│                                                                              │
│   Context Allocation:                                                        │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │ Procedural (35%)  │ Semantic (30%)  │ Episodic (25%)  │Graph(10%)│       │
│   │     56,350        │    48,300       │    40,250       │  16,100  │       │
│   └─────────────────────────────────────────────────────────────────┘       │
│                                                                              │
│   Quality Ranking (per item):                                                │
│   ┌────────────┬────────────┬────────────┬────────────┐                     │
│   │  Recency   │ Confidence │ Relevance  │ Importance │ = Rank Score        │
│   │    25%     │    25%     │    25%     │    25%     │                     │
│   └────────────┴────────────┴────────────┴────────────┘                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Ranking Strategies

| Strategy | Description |
|----------|-------------|
| **Recency** | Prefer recent items (exponential decay) |
| **Confidence** | Prefer high-confidence items |
| **Relevance** | Prefer items matching query |
| **Importance** | Prefer critical/high-importance items |
| **Balanced** | Equal weight to all factors |

### Quick Example

```python
from context_budget import ContextBudgetManager

manager = ContextBudgetManager(model_id="claude-sonnet")

# Allocate budget
allocation = manager.allocate_budget(
    base_prompt_tokens=5000,
    expected_response_tokens=4000,
    task_context="code_review"
)

# Pack knowledge within budget
packed = manager.pack_knowledge(
    allocation=allocation,
    semantic_items=facts,
    procedural_items=preferences,
    episodic_items=events,
    query="TypeScript best practices"
)

# Assemble formatted context
context = manager.assemble_context(packed, format_style="markdown")
print(f"Context tokens: {context.total_tokens}")
print(f"Items selected: {packed.total_items}")
print(f"Items dropped: {packed.dropped_items}")
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
├── SKILL.md                    # Claude's operational instructions
├── README.md                   # This file
├── QUICK-START.md              # Fast reference guide
├── INDEX.md                    # Navigation guide
│
├── docs/
│   ├── ARCHITECTURE.md         # Complete technical architecture
│   ├── VISION.md               # Long-term vision document
│   ├── GEMINI-INTEGRATION.md   # Gemini multi-model guide
│   └── TOOLORCHESTRA-REVIEW.md # ToolOrchestra analysis & enhancements
│
├── schemas/
│   └── supabase-schema.sql     # Database schema (Phase 1 + Phase 2 tables)
│
├── src/
│   ├── types.ts                # TypeScript type definitions (incl. Phase 2)
│   ├── knowledge_operations.py # Core Python operations
│   ├── model_router.py         # Intelligent model routing
│   ├── context_budget.py       # Dynamic context budgeting (NEW - Phase 2)
│   └── skill_orchestrator.py   # Skill orchestration layer (NEW - Phase 2)
│
├── config/
│   └── memory-template.md      # Template for CLAUDE.memory.md
│
└── modules/                    # Future: modular extensions
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

### Phase 1: Foundation (Completed)
- Efficiency tracking in autonomy audit
- Tool pattern procedural memory
- Basic preference vectors
- Model Router integration

### Phase 2: Skill Orchestration (Completed)
- **Skill Orchestration Layer** - Intelligent skill coordination
- **Dynamic Context Budgeting** - Token-efficient context assembly
- Skill registry with capabilities
- Multi-skill execution coordination
- Context packing with quality ranking

### Phase 3: Intelligence (Planned)
- Vector embeddings for semantic search
- Digital Twin Modeling (DTM)
- Autonomy Trust Ledger enhancements
- Pattern detection and recommendations

### Phase 4: Voice & Autonomy (Planned)
- Real-time voice interface via PersonaPlex
- Voice-Native Knowledge Graph (VNKG)
- Proactive task execution
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

### v1.2.0 (2026-01-25) - Phase 2: Skill Orchestration
- **Skill Orchestration Layer** - Multi-skill coordination with intelligent planning
- **Dynamic Context Budgeting** - Token-efficient context assembly within model limits
- **Skill Registry** - Register, discover, and execute skills by capability
- **Context Packing** - Quality-based ranking and selection of knowledge items
- **Ranking Strategies** - Recency, confidence, relevance, importance, balanced
- New `context_budget.py` for intelligent context management
- New `skill_orchestrator.py` for skill coordination
- New database tables: `arcus_skills`, `arcus_skill_executions`, `arcus_orchestration_runs`, `arcus_context_budget_logs`
- New RPC functions: `increment_skill_counters()`, `get_best_skill_for_capability()`
- New views: `skill_performance_summary`, `recent_orchestration_runs`, `context_budget_efficiency`
- Extended TypeScript types for Phase 2 components

### v1.1.0 (2026-01-25) - Phase 1: Foundation
- **Model Orchestration** - Intelligent routing inspired by NVIDIA ToolOrchestra
- **User Preference Vectors** - Customizable accuracy/cost/latency weights
- **Model Patterns** - Cross-session learning from outcomes
- **Efficiency Tracking** - Cost, latency, and token tracking per request
- New `model_router.py` for intelligent model selection
- New `knowledge_operations.py` with orchestration methods
- Enhanced Supabase schema with `arcus_model_patterns` and `arcus_user_preference_vectors` tables
- ToolOrchestra review document with enhancement roadmap

### v1.0.0 (2026-01-24) - Initial Release
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
