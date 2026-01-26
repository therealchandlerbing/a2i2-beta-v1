---
# Arcus Knowledge Repository - Session Memory
# This file is read by Claude at session start and updated with learnings
# Version: 1.0.0
# Last Updated: 2026-01-26T00:00:00Z
# Session Count: 2
---

# User Preferences

## Communication Style
- Response style: Concise, technical, actionable
- Emoji usage: Never unless explicitly requested
- Formality: Professional but direct
- When uncertain: Ask clarifying questions rather than assume

## Technical Preferences
- Primary language: TypeScript
- Secondary language: Python
- Code style: Clean, well-structured, minimal comments (self-documenting)
- Documentation: Only when explicitly requested
- Testing: Prefer comprehensive tests for critical modules

## Workflow Preferences
- Planning: Architecture/design first, then implementation
- Commits: Descriptive messages, atomic changes
- Autonomy: Currently building trust - confirm before major actions

---

# Organization Context

## Organization
- Name: Arcus Innovation Studios
- Focus: AI innovation, technology consulting, impact-driven work
- Team: Chandler, Eduardo, Felipe (and others)

## Active Projects
1. **Knowledge Repository Setup** (Priority: HIGH)
   - Building persistent memory system for Claude
   - Vision: R2-D2/Enterprise computer level AI companion
   - Current phase: Platform Design & Interaction Architecture
   - Next: Deploy Supabase, build first interface

2. **Platform Interaction Design** (Priority: HIGH)
   - "Hey Arcus" voice activation system
   - Multi-platform access (web, mobile, wearable, embedded)
   - Collective intelligence for team use
   - See: PLATFORM-DESIGN.md

3. **AI Agent Planning Dashboard** (Priority: MEDIUM)
   - 12-step wizard for agent development planning
   - Enterprise features with role-based access
   - Completed initial version

## Technology Stack
- Frontend: Next.js 14, React 18, TypeScript
- Database: Supabase (PostgreSQL + pgvector)
- Skills: 33 Claude skills in .claude/skills/
- Agents: 18 specialized agents in .claude/agents/

---

# Recent Learnings

## Session Learnings (Last 7 Days)
1. **2026-01-26**: Voice architecture strategic design
   - Created VOICE-ARCHITECTURE.md with progressive enhancement strategy
   - **Phase 1 (MVP)**: Siri Shortcuts as validation layer (Weeks 1-2)
     - "Hey Siri, ask Arcus..." via webhook endpoint
     - 25-30 second timeout limit - optimize responses
     - Works on iPhone, Apple Watch, CarPlay (with limitations)
     - Zero app development, immediate deployment
   - **Phase 2 (Native)**: React Native + PersonaPlex (Weeks 3-6)
     - Custom "Hey Arcus" wake word via Picovoice Porcupine ($100)
     - PersonaPlex full-duplex voice (170ms latency)
     - Custom voice identity (not Siri's voice)
     - Full memory integration
   - **Phase 3 (Full)**: All platforms unified (Weeks 7-12)
     - Web app voice via WebRTC + PersonaPlex
     - Apple Watch companion app
     - CarPlay optimization
     - Cross-device conversation continuity
   - **Strategic insight**: Siri Shortcuts is VALIDATION, not compromise
   - Cost estimate: Phase 1 ~$95/mo, Phase 2 ~$270-500/mo, Phase 3 ~$370-700/mo

2. **2026-01-26**: Clawdbot integration analysis
   - Reviewed clawdbot (41k+ stars) for patterns to enhance A2I2
   - Key insight: Clawdbot = accessibility (12+ channels), A2I2 = intelligence (memory)
   - Gateway pattern: Single WebSocket control plane for all channels
   - **PREFERENCE**: Team does NOT use Slack - they hate it
   - **PREFERENCE**: Primary communication is WhatsApp (team + partners)
   - **PREFERENCE**: Discord preferred for async/community collaboration
   - Priority integrations: WhatsApp, Siri Shortcuts, Discord (NO Slack)
   - Siri Shortcuts idea: "Hey Siri, ask Arcus..." via webhook - low effort, high impact
   - Chat commands: /recall, /learn, /context for memory operations
   - Session coordination: Enable cross-user knowledge sharing
   - Created CLAWDBOT-INTEGRATION.md with full roadmap
   - Complementary systems - combine for "everywhere + remembers + learns"

2. **2026-01-26**: Platform interaction design review
   - User wants "Hey Arcus" wake word like Alexa/Siri
   - Multiple access points needed: web, mobile, wearable, embedded
   - Collective intelligence for team (Chandler, Eduardo, Felipe)
   - Integration priority: connect to existing workflows
   - Created PLATFORM-DESIGN.md with full interaction architecture
   - Key decision: voice-first or web-first for MVP?
   - Wake word tech: Picovoice Porcupine recommended ($100 training)

2. **2026-01-25**: ToolOrchestra review - orchestration paradigm insights
   - Small orchestrators (8B) can coordinate larger tools efficiently
   - Multi-objective rewards: accuracy + efficiency + user preferences
   - A2I2 could add Skill Orchestration Layer for routing
   - Tool patterns should become procedural memory
   - User preference vectors enable runtime control

3. **2026-01-24**: User wants modular, future-proof architecture
   - Design for capabilities that don't exist yet
   - Build knowledge foundation now for future AI capabilities
   - Vision: AI companion like R2-D2 or Enterprise computer

4. **2026-01-24**: User prefers architecture-first approach
   - Complete design documents before implementation
   - Think through full system before building pieces

5. **2026-01-24**: Real-time voice agent is a future goal
   - Memory-enabled voice interface
   - Autonomous decision-making (with training)
   - Current focus is building knowledge foundation

## Patterns Observed
- User thinks in terms of long-term vision, not just immediate tasks
- User values comprehensive planning and documentation
- User wants Claude to be proactive and thoughtful
- User wants A2I2 to be accessible everywhere (ambient computing vision)
- User thinks about team adoption, not just personal use
- User wants to understand how things connect before building

---

# Active Context

## Current Session Focus
- Building Arcus Knowledge Repository
- Creating architecture documentation
- Setting up foundation for persistent memory

## Recently Discussed Entities
- Arcus Innovation Studios (organization)
- AI Agent Planning Dashboard (project)
- Knowledge Repository (project)
- R2-D2 / Enterprise Computer (vision references)

## Open Questions
- Wake word decision: "Hey Arcus" or alternative?
- Voice-first or web-first for MVP?
- Start with single-user or multi-user from day one?
- Which external tool to integrate first? (Slack, Calendar, Notion?)
- Dedicated hardware (Raspberry Pi) or phone-only for voice?
- Starting autonomy level: Level 0 or Level 1?
- How to balance comprehensive capture vs. privacy?
- Specific autonomy boundaries for Phase 2?

---

# Pending Actions

## To Complete
- [x] Finish knowledge repository skill setup
- [x] Create README and QUICK-START for skill
- [x] Update hooks.json with knowledge capture triggers
- [ ] Deploy Supabase schema
- [ ] Test basic LEARN/RECALL operations
- [ ] Create example implementation code

## To Remember
- Push to branch: `claude/knowledge-repository-setup-UYJXD`
- Organization name: Arcus Innovation Studios (not 360 Social Impact Studios)
- Vision: Building toward R2-D2/Enterprise computer level AI companion

---

# Memory Operations Log

## Recent Captures
| Timestamp | Type | Summary | Confidence |
|-----------|------|---------|------------|
| 2026-01-26 | semantic | Platform interaction design: voice + multi-modal access | 0.95 |
| 2026-01-26 | preference | "Hey Arcus" wake word activation desired | 0.95 |
| 2026-01-26 | preference | Team/collective intelligence is priority | 0.90 |
| 2026-01-26 | procedural | PLATFORM-DESIGN.md created for interaction architecture | 1.00 |
| 2026-01-25 | semantic | ToolOrchestra orchestration paradigm | 0.95 |
| 2026-01-25 | semantic | Multi-objective rewards for efficiency | 0.90 |
| 2026-01-25 | procedural | Skill orchestration layer pattern | 0.85 |
| 2026-01-24 | preference | Modular architecture preference | 0.95 |
| 2026-01-24 | preference | Architecture-first approach | 0.95 |
| 2026-01-24 | semantic | Vision: R2-D2 level AI companion | 0.90 |
| 2026-01-24 | semantic | Organization: Arcus Innovation Studios | 1.00 |

## Sync Status
- Last sync to Supabase: Not yet initialized
- Pending captures: 4
- Next sync: After Supabase schema deployment

---

# Autonomy Status

## Current Level: 0 (Assisted)
- Claude advises, user executes
- Building baseline understanding
- Capturing preferences and patterns

## Trust Metrics (Initializing)
- Successful actions: 0
- Corrections received: 0
- Patterns identified: 3
- Session count: 1

## Boundary Reminders
- Always confirm before: git push, file deletion, external communication
- Can do autonomously: read files, search, generate content drafts
- Never without asking: financial actions, sensitive data operations

---

# Notes

## Session Notes
- First session of knowledge repository setup
- User has clear vision for long-term AI companion
- Focus on building durable, future-proof foundation
- Voice integration is desired but not immediate priority

## Technical Notes
- Supabase schema created at `schemas/supabase-schema.sql` (not yet deployed)
- Full skill documentation: SKILL.md, README.md, QUICK-START.md, INDEX.md
- Architecture docs: ARCHITECTURE.md (1300+ lines), VISION.md
- TypeScript types: src/types.ts (comprehensive type definitions)
- Config files: hooks-config.json, memory-template.md
- hooks.json updated with session knowledge context loading

---

*This file is automatically managed by the Arcus Knowledge Repository skill.*
*Manual edits are preserved but may be overwritten during sync.*
