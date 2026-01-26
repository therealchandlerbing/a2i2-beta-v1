# A2I2 Platform Design: Interaction & Access Architecture

**Version**: 1.0.0
**Author**: Claude + Chandler
**Date**: 2026-01-26
**Status**: Design Review

---

## Executive Summary

This document addresses a critical question: **How do users interact with A2I2?**

The platform has sophisticated memory, intelligence, and voice capabilities. But none of that matters if people can't naturally engage with it. This document proposes a multi-modal, multi-platform access architecture that makes A2I2 feel like a natural extension of how your team already works.

**Core Principle**: A2I2 should be everywhere you need it, invisible when you don't, and always contextually aware.

---

## The Interaction Problem

### Current State
- Robust backend: memory system, model routing, skill orchestration, voice pipeline
- No frontend: no way for users to actually engage with the system
- No persistent daemon: nothing listening for "Hey Arcus"

### What You Need
1. **Voice-First Interface** - "Hey Arcus" activation like Alexa/Siri
2. **Multi-Platform Access** - Web, mobile, wearable, embedded
3. **Cross-Platform Learning** - Knowledge flows from all touchpoints
4. **Collective Intelligence** - Team shares a unified organizational brain

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER TOUCHPOINTS                                   │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────┤
│   Voice     │    Web      │   Mobile    │  Wearable   │     Embedded        │
│  Devices    │    App      │    App      │   (Watch)   │   (Slack, etc.)     │
│             │             │             │             │                     │
│ "Hey Arcus" │  Dashboard  │  On-the-go  │  Quick      │  Where you          │
│  always-on  │  deep work  │  capture    │  queries    │  already work       │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴──────────┬──────────┘
       │             │             │             │                 │
       └─────────────┴─────────────┴─────────────┴─────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │      UNIFIED API LAYER       │
                    │                              │
                    │  • Authentication (Supabase) │
                    │  • Rate limiting             │
                    │  • Context assembly          │
                    │  • User identification       │
                    │  • Team/org routing          │
                    └──────────────┬───────────────┘
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       │                           │                           │
┌──────▼──────┐             ┌──────▼──────┐             ┌──────▼──────┐
│   VOICE     │             │   SKILL     │             │   MODEL     │
│ ORCHESTRATOR│◄───────────►│ORCHESTRATOR │◄───────────►│   ROUTER    │
│             │             │             │             │             │
│ PersonaPlex │             │ 33 Skills   │             │ Claude      │
│ Gemini Live │             │ Routing     │             │ Gemini      │
│ Wake Word   │             │ Composition │             │ PersonaPlex │
└──────┬──────┘             └──────┬──────┘             └─────────────┘
       │                           │
       └───────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │    KNOWLEDGE LAYER      │
        │                         │
        │  Episodic │ Semantic    │
        │  Procedural │ Graph     │
        │  Working Memory         │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   SUPABASE + VECTOR     │
        │                         │
        │  PostgreSQL + pgvector  │
        │  Real-time subscriptions│
        │  Row-level security     │
        └─────────────────────────┘
```

---

## Interaction Modalities

### 1. Voice Interface: "Hey Arcus"

**The Vision**: A dedicated voice device (or app) that's always listening for "Hey Arcus", just like asking a colleague a question.

**Technical Options**:

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **Raspberry Pi + Microphone** | Cheap, customizable, runs 24/7 | DIY, limited processing | Home office, personal |
| **ESP32 with Wake Word** | Ultra-cheap ($5), low power | Very limited, needs edge ML | Multiple rooms, ambient |
| **Alexa Custom Skill** | Existing hardware, good mics | Amazon lock-in, latency, privacy | Quick MVP |
| **Mobile App (Background)** | Phone you already have | Battery, permissions | On-the-go |
| **Smart Display (Custom)** | Visual + voice, tablet form | More expensive | Conference rooms |

**Recommended MVP Path**:
1. **Phase 1**: Custom mobile app with wake word detection (iOS/Android)
   - Use Picovoice Porcupine for "Hey Arcus" wake word ($100 wake word training)
   - Stream to PersonaPlex for processing
   - Works anywhere you have your phone

2. **Phase 2**: Raspberry Pi dedicated device
   - 24/7 always-on in office/home
   - Better mics, no battery concerns
   - Can run local wake word detection

3. **Phase 3**: Smart display with visual feedback
   - Shows context, confirmations, data
   - Video call integration potential

**Wake Word Architecture**:
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Microphone    │────►│  Wake Word      │────►│  PersonaPlex    │
│   (always on)   │     │  Detection      │     │  Voice Engine   │
│                 │     │  (local/edge)   │     │  (cloud GPU)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       ▼
        │                 "Hey Arcus"            ┌─────────────────┐
        │                  detected              │  A2I2 Backend   │
        │                       │                │  (orchestrator) │
        │                       ▼                └─────────────────┘
        │              ┌─────────────────┐              │
        └─────────────►│  Audio Stream   │◄─────────────┘
                       │  (post wake)    │
                       └─────────────────┘
```

**Wake Word Options**:
- **Picovoice Porcupine**: $100 to train custom "Hey Arcus", runs on device, <5% CPU
- **Snowboy**: Open source, self-train, older but works
- **OpenWakeWord**: Open source, Python, good accuracy
- **Mycroft Precise**: Open source, neural network based

---

### 2. Web Application

**Purpose**: Deep work, administration, knowledge exploration

**Key Screens**:

```
┌─────────────────────────────────────────────────────────────────┐
│  ARCUS A2I2                              [👤 Chandler] [⚙️]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐  ┌─────────────────────────────────────────────┐   │
│  │ Home    │  │                                             │   │
│  │ Chat    │  │   [🎤] "How did we handle the TechCorp      │   │
│  │ Memory  │  │        proposal last quarter?"              │   │
│  │ Graph   │  │                                             │   │
│  │ Team    │  │   ─────────────────────────────────────     │   │
│  │ Settings│  │                                             │   │
│  │         │  │   Based on your episodic memory, you        │   │
│  │         │  │   worked on the TechCorp proposal in        │   │
│  │         │  │   October 2025...                           │   │
│  │         │  │                                             │   │
│  │         │  │   [📎 Related: TechCorp Entity]             │   │
│  │         │  │   [📎 Related: Proposals Workflow]          │   │
│  │         │  │                                             │   │
│  └─────────┘  └─────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─ Recent Activity ────────────────────────────────────────┐   │
│  │ • Voice query: "What's Eduardo working on?" (5 min ago) │   │
│  │ • Learned: Meeting notes from Sprint Planning           │   │
│  │ • Insight: You prefer Monday planning sessions          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Core Features**:
- Conversational interface (text + voice input)
- Knowledge graph visualization
- Memory browser (episodic, semantic, procedural)
- Team activity feed
- Settings and privacy controls
- Integration management (connect Slack, Asana, etc.)

**Tech Stack Recommendation**:
- **Next.js 14** (you're already using it)
- **Supabase Auth** (built-in, row-level security)
- **Supabase Realtime** (live updates across devices)
- **React Query** for data fetching
- **D3.js or Cytoscape** for knowledge graph viz

---

### 3. Mobile Application

**Purpose**: Capture and query on-the-go

**Key Use Cases**:
- Voice queries while walking/driving
- Quick capture of ideas or meeting notes
- Notifications and proactive insights
- Widget for quick access

**Recommended Approach**:
- **React Native** (share code with web)
- **Expo** for faster development
- Background wake word detection (battery-conscious)
- Push notifications for proactive insights

**Mobile-Specific Features**:
```
┌─────────────────────┐
│     ARCUS A2I2      │
├─────────────────────┤
│                     │
│   ┌─────────────┐   │
│   │  🎤  Tap or │   │
│   │     say     │   │
│   │ "Hey Arcus" │   │
│   └─────────────┘   │
│                     │
│  Quick Actions:     │
│  [📝 Capture Note]  │
│  [🔍 Search Memory] │
│  [📊 Today's Brief] │
│                     │
│  Recent:            │
│  • Sprint planning  │
│  • TechCorp call    │
│  • Design review    │
│                     │
└─────────────────────┘
```

---

### 4. Wearable Integration

**Purpose**: Ambient, always-available quick queries

**Options**:

| Device | Integration Path | Capabilities |
|--------|------------------|--------------|
| **Apple Watch** | WatchKit app | Voice query, haptic notifications, quick glances |
| **Galaxy Watch** | Wear OS app | Similar to Apple Watch |
| **Oura Ring** | API integration | Health data → knowledge capture (optional) |
| **Ray-Ban Meta** | Voice trigger | "Hey Meta, ask Arcus..." |
| **AirPods** | Siri Shortcut | "Hey Siri, ask Arcus..." |

**MVP Wearable**: Apple Watch complication + voice shortcut
- Tap complication → voice query
- Siri Shortcut: "Ask Arcus [question]"
- Haptic tap for proactive insights

---

### 5. Embedded Integrations

**Purpose**: A2I2 in the tools you already use

**Priority Integrations**:

| Platform | Integration Type | Use Cases |
|----------|-----------------|-----------|
| **Slack** | Bot + Slash commands | `/arcus recall`, @arcus in channels, DM queries |
| **VS Code** | Extension | Code context queries, "How did we implement X?" |
| **Notion** | Sidebar app | Query while writing docs |
| **Linear/Asana** | Bot | Project context, "What's blocked?" |
| **Zoom/Meet** | Companion | Real-time meeting insights |
| **Chrome** | Extension | Capture from any webpage |
| **Obsidian** | Plugin | Bi-directional sync with notes |

**MVP Embedded**: Slack Bot
- Most universal for teams
- Real-time presence
- Channel-aware context
- Easiest to build

---

## Collective Intelligence: Team Architecture

### The Challenge
Individual memories are useful. But A2I2's real power is organizational intelligence - the team's shared brain.

### Memory Scoping Model

```
┌─────────────────────────────────────────────────────────────────┐
│                     ORGANIZATION MEMORY                         │
│     (company-wide knowledge, policies, shared contexts)         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────┐     ┌─────────────────────┐           │
│   │    TEAM MEMORY      │     │    TEAM MEMORY      │           │
│   │   (Engineering)     │     │     (Design)        │           │
│   │                     │     │                     │           │
│   │  ┌───────┐ ┌───────┐│     │  ┌───────┐ ┌───────┐│           │
│   │  │Chandler│ │Eduardo││     │  │ Felipe │ │  ...  ││           │
│   │  │PERSONAL│ │PERSONAL│     │  │PERSONAL│ │       ││           │
│   │  └───────┘ └───────┘│     │  └───────┘ └───────┘│           │
│   └─────────────────────┘     └─────────────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Access Control Matrix

**Legend**: ✅ = Available | ❌ = Not available | ⚙️ = Opt-in (user chooses to share)

| Memory Type | Personal | Team | Org | Default |
|-------------|----------|------|-----|---------|
| Preferences | ✅ | ❌ | ❌ | Personal |
| Work style | ✅ | ⚙️ | ❌ | Personal |
| Episodic (meetings) | ✅ | ✅ If shared meeting | ❌ | Team |
| Semantic (facts) | ⚙️ | ✅ | ✅ | Org |
| Procedural (workflows) | ⚙️ | ✅ | ✅ | Team |
| Relationships | ⚙️ | ✅ | ✅ | Team |

### Team Scenarios

**Scenario 1: New Team Member**
```
Felipe joins Arcus Innovation Studios.

A2I2 can immediately help him:
- "How do we do sprint planning here?"
  → Recalls organizational procedural memory

- "What projects is the team working on?"
  → Recalls team episodic memory

- "What's Chandler's communication style?"
  → Returns nothing (personal, not shared)
```

**Scenario 2: Cross-Team Context**
```
Eduardo (Engineering) needs to know about a Design decision.

"What did Design decide about the dashboard layout?"
 → A2I2 queries Design team's episodic memory
 → Returns: "In the 1/15 design review, the team chose
    the card-based layout because..."
```

**Scenario 3: Institutional Memory**
```
"How did we handle the Series A investor pitch?"
 → Even if original team members left
 → Organizational episodic memory preserves it
```

---

## Cross-Platform Sync Architecture

### Real-Time Context Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Voice     │     │    Web       │     │   Slack      │
│  (Kitchen)   │     │  (Desktop)   │     │  (Thread)    │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │   "Schedule        │                    │
       │    meeting with    │                    │
       │    TechCorp"       │                    │
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────┐
│                    SUPABASE REALTIME                      │
│                                                           │
│  • Working memory updated (all clients notified)         │
│  • Episodic entry created                                 │
│  • Related entities surfaced                              │
└──────────────────────────────────────────────────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Voice:     │     │   Web:       │     │   Slack:     │
│  "Scheduled  │     │  Calendar    │     │  Notifies    │
│   for 3pm"   │     │  updated     │     │  in channel  │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Context Continuity
- Start conversation on phone, continue on desktop
- Voice capture syncs to all platforms instantly
- Working memory follows you across devices
- "Resume where I left off" is automatic

---

## Integration Architecture

### How A2I2 Connects to External Systems

```
                    ┌─────────────────┐
                    │    A2I2 Core    │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐        ┌─────▼─────┐       ┌─────▼────┐
    │ INBOUND │        │ BI-DIRECT │       │ OUTBOUND │
    │ (Learn) │        │  (Sync)   │       │  (Act)   │
    └────┬────┘        └─────┬─────┘       └─────┬────┘
         │                   │                   │
    ┌────┴────┐        ┌─────┴─────┐       ┌─────┴────┐
    │ • Gmail │        │ • Calendar│       │ • Asana  │
    │ • Slack │        │ • Notion  │       │ • Linear │
    │ • Zoom  │        │ • Drive   │       │ • Slack  │
    │ • Meet  │        │ • GitHub  │       │ • Email  │
    └─────────┘        └───────────┘       └──────────┘
```

### Integration Patterns

**1. Inbound (Passive Learning)**
- A2I2 watches email → Extracts key info → Creates episodic memory
- Zoom recordings → Transcribe → Capture commitments
- Slack threads → Identify decisions → Store in semantic memory

**2. Bi-Directional (Active Sync)**
- Calendar: Read events + create/modify on behalf
- Notion: Read context + update pages
- GitHub: Read PRs/issues + comment

**3. Outbound (Autonomous Action)**
- Create Asana tasks based on meeting commitments
- Send Slack reminders based on follow-ups
- Draft emails for review

**Autonomy Levels Apply Here**:
- Level 0-1: Only reads from integrations
- Level 2: Can suggest actions
- Level 3: Can execute with notification
- Level 4: Full autonomous action

---

## Recommended Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Basic web + API working

- [ ] Deploy Supabase schema
- [ ] Create Next.js web shell
- [ ] Implement authentication (Supabase Auth)
- [ ] Build basic chat interface
- [ ] Connect to existing Python backend
- [ ] Simple LEARN/RECALL through web UI

### Phase 2: Voice MVP (Weeks 3-4)
**Goal**: "Hey Arcus" working on mobile

- [ ] Train "Hey Arcus" wake word (Picovoice)
- [ ] Build React Native shell
- [ ] Integrate wake word detection
- [ ] Connect to PersonaPlex endpoint
- [ ] Basic voice → response loop
- [ ] Push notification for async responses

### Phase 3: Team Features (Weeks 5-6)
**Goal**: Collective intelligence basics

- [ ] Multi-user authentication
- [ ] Memory scoping (personal/team/org)
- [ ] Row-level security in Supabase
- [ ] Team dashboard
- [ ] Shared knowledge graph

### Phase 4: Integrations (Weeks 7-8)
**Goal**: A2I2 in your workflow

- [ ] Slack bot (MVP integration)
- [ ] Calendar sync (Google/Outlook)
- [ ] Chrome extension for capture
- [ ] Webhook system for external events

### Phase 5: Dedicated Hardware (Future)
**Goal**: Always-on ambient presence

- [ ] Raspberry Pi + microphone array
- [ ] Local wake word processing
- [ ] LED/display feedback
- [ ] Multi-room deployment

---

## Technology Decisions

### Recommended Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Web Frontend** | Next.js 14 | Already in your stack, SSR, app router |
| **Mobile** | React Native + Expo | Share code with web team |
| **Database** | Supabase | Already designed for, realtime built-in |
| **Auth** | Supabase Auth | Integrated, supports org/team |
| **Voice Processing** | PersonaPlex 7B | <200ms, open source, more versatile than Gemini |
| **Wake Word** | Picovoice Porcupine | Best balance of accuracy/efficiency |
| **Realtime** | Supabase Realtime | Already integrated |
| **API** | Python FastAPI | Matches existing backend code |
| **Hosting** | Vercel (web) + Railway (Python) | Easy, scalable |
| **GPU (Voice)** | RunPod or Lambda Labs | PersonaPlex needs GPU |

### Alternative Considerations

**For simpler MVP** (not recommended for production):
- Skip mobile app initially → Use web PWA
- Skip custom wake word → Use Alexa skill or Siri Shortcut
- Skip PersonaPlex → Use Gemini 2.5 Flash Live (fallback only, less versatile)

**Note on Gemini Live**:
- Gemini 2.5 Flash Live is a fallback option only
- PersonaPlex 7B is preferred: open source, more versatile, full control
- Gemini has higher latency and less customization

---

## Privacy & Security Considerations

### Data Boundaries

| Data Type | Storage | Encryption | Retention |
|-----------|---------|------------|-----------|
| Voice audio | Never stored (streaming only) | N/A | Instant deletion |
| Transcripts | Supabase | At rest + in transit | User-controlled |
| Memories | Supabase | At rest + in transit | Indefinite (user can delete) |
| Preferences | Supabase | At rest + in transit | Indefinite |
| API keys | Vault/env | Vault | Never in DB |

### Team Privacy

- Personal memories are never shared unless explicit
- Users can see what A2I2 knows about them
- "Forget this" command erases specific memories
- Audit log of all knowledge access

---

## Open Questions for Discussion

1. **Wake word**: "Hey Arcus" or something else? ("Arcus", "Hey A2", custom?)

2. **Primary interface**: Voice-first or web-first for MVP?

3. **Team vs Individual**: Start with single-user or multi-user from day one?

4. **Integration priority**: Which external tool is most critical? (Slack, Calendar, Notion?)

5. **Hardware**: Interested in dedicated device (Pi) or phone-only for voice?

6. **Autonomy starting point**: Level 0 (pure assistant) or Level 1 (suggestions)?

---

## Next Steps

1. **Review this document** - align on the architecture
2. **Decide Phase 1 scope** - what's the true MVP?
3. **Deploy Supabase** - unblocks everything
4. **Build web shell** - first real interface
5. **Train wake word** - unlocks voice testing

---

*"The best interface is no interface. The second best is one that feels like talking to a brilliant colleague."*
