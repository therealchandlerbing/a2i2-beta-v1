<div align="center">

# 🧠 A2I2 — Arcus Intelligence Platform

### *Your AI Chief of Staff*

[![Beta](https://img.shields.io/badge/Status-Beta-00BFB3?style=for-the-badge)](https://github.com/therealchandlerbing/a2i2-beta-v1)
[![Version](https://img.shields.io/badge/Version-1.0.0--beta-0A2540?style=for-the-badge)](https://github.com/therealchandlerbing/a2i2-beta-v1)
[![License](https://img.shields.io/badge/License-MIT-425466?style=for-the-badge)](LICENSE)
[![Claude](https://img.shields.io/badge/Powered%20By-Claude-8B5CF6?style=for-the-badge)](https://anthropic.com)

<br/>

**Building AI companions that remember, learn, and grow with your organization.**

*Transform AI assistants from stateless tools into intelligent partners.*

<br/>

[🚀 Quick Start](#-quick-start) •
[📖 Documentation](#-documentation) •
[🎯 Features](#-core-features) •
[🗺️ Roadmap](#️-roadmap) •
[🤝 Contributing](#-contributing)

<br/>

---

</div>

<br/>

## 🎯 Real-World Use Cases

<details>
<summary><b>👔 Executive Assistant Scenario</b> — Morning briefing and day planning</summary>

<br/>

**The Situation:** You're a CEO starting your day with dozens of emails, three meetings, and a board presentation next week.

**Without A2I2:** You manually sift through emails, try to remember context from past meetings, and scramble to recall who said what and when.

**With A2I2:**

```
You: "Good morning. What do I need to know today?"

A2I2: "Good morning. Three priorities:

1. Sarah Chen (TechCorp CIO) replied overnight. Based on 12 previous
   interactions, her response pattern suggests strong interest—she typically
   responds within 2 hours when engaged. She raised a timeline concern
   similar to what she did in March. I've drafted a response using the
   approach that worked with Eduardo.

2. Your board meeting is in 8 days. You typically start financial review
   10 days out. I've pre-populated the dashboard with current data and
   flagged two line items that may draw questions from James Wong—similar
   to his Q3 questions.

3. The innovation grant deadline I've been tracking: given our 73% success
   rate with NSF vs 31% with private foundations, and current team capacity,
   I recommend we pass. Want me to archive this or draft an application?"
```

**Memory Types Used:**
- **Episodic**: Past interactions with Sarah, previous board meetings
- **Semantic**: Success rates, stakeholder patterns
- **Procedural**: Your typical prep timelines
- **Relational**: Sarah → TechCorp, James Wong → Board

</details>

<details>
<summary><b>🤝 Client Relationship Management</b> — Never forget a conversation</summary>

<br/>

**The Situation:** You're preparing for a call with a client you haven't spoken to in 3 months.

**Without A2I2:** You search through emails, Slack, and meeting notes trying to remember what you discussed and what was promised.

**With A2I2:**

```
You: "I have a call with DataFlow Inc in 30 minutes. Bring me up to speed."

A2I2: "Here's your DataFlow context:

RELATIONSHIP STATUS:
├── Last contact: October 15 (you sent Q4 roadmap)
├── Champion: Maria Santos (VP Engineering) - prefers data-driven discussions
├── Decision maker: CFO Tom Bradley - concerned about ROI timelines
└── Relationship temperature: Warm (responded positively to roadmap)

OPEN ITEMS:
├── You promised a technical deep-dive on AI integration (not scheduled)
├── They requested case studies from manufacturing sector
└── Maria asked about our security certifications

COMMUNICATION PATTERNS:
├── Maria: Responds best to technical specifics, morning person (EST)
├── Tom: Skeptical but persuadable with concrete numbers
└── Company: 45-day average sales cycle, procurement-heavy

RECOMMENDED APPROACH:
Lead with the manufacturing case studies, then transition to
scheduling the technical deep-dive. Have ROI calculator ready
for Tom if he joins."
```

</details>

<details>
<summary><b>📊 Project Handoff</b> — Institutional memory that survives transitions</summary>

<br/>

**The Situation:** A team member is leaving and you need to capture 2 years of context from their projects.

**Without A2I2:** Knowledge walks out the door. New team members start from scratch.

**With A2I2:**

```
You: "Alex is leaving. Capture everything about the Phoenix project before
      their last day."

A2I2: "I'll conduct a knowledge crystallization session with Alex.
      Here's what I'll capture:

EPISODIC (What Happened):
├── Key decisions and their rationale
├── Failed approaches and why they didn't work
├── Stakeholder interactions and outcomes
└── Critical milestones and blockers overcome

PROCEDURAL (How Things Work):
├── Undocumented workflows Alex developed
├── Vendor relationships and contact protocols
├── Code deployment rituals and gotchas
└── Client communication preferences

RELATIONAL (Who Knows What):
├── Alex's network of experts and consultants
├── Internal subject matter experts they relied on
└── External partners and their reliability ratings

I'll schedule three 45-minute sessions and synthesize into:
1. Searchable knowledge base for the team
2. Onboarding guide for Alex's replacement
3. Risk register for implicit dependencies

Shall I send Alex the calendar invites?"
```

</details>

<details>
<summary><b>🎙️ Voice-First Workflow</b> — Natural conversation with memory</summary>

<br/>

**The Situation:** You're driving to a client meeting and need to prepare hands-free.

**Without A2I2:** Dangerous phone checking, unprepared arrival.

**With A2I2 + NVIDIA PersonaPlex:**

```
You: "Hey Arcus, brief me on Quantum Dynamics before I arrive."

A2I2: [Voice response in 170ms]
"Quantum Dynamics—three things to know:

First, their CTO Jennifer Park is in the meeting. She's technical,
appreciates depth over polish. Last time you two connected over the
neural network architecture discussion.

Second, they're evaluating us against CompetitorX. Their concern is
our enterprise support tier—you addressed this with DataFlow by
offering the pilot SLA. That worked.

Third—heads up—their CFO mentioned budget reviews in Q2. If pricing
comes up, you have flexibility on the implementation timeline but
not the license cost. Want me to pull up the approved negotiation
boundaries?"

You: "Yes, and remind me of Jennifer's background."

A2I2: "Jennifer has a PhD from MIT in distributed systems, 8 years
at Google Cloud, joined Quantum 18 months ago. She posts about
real-time data processing on LinkedIn—your conversation about
streaming architectures would resonate. Sending approved pricing
boundaries to your phone now."
```

</details>

<details>
<summary><b>🔄 Learning from Mistakes</b> — Pattern detection that improves outcomes</summary>

<br/>

**The Situation:** Your team notices proposals keep stalling at the same stage.

**Without A2I2:** Anecdotal theories, no systematic improvement.

**With A2I2:**

```
You: "Why do our proposals keep dying at the procurement stage?"

A2I2: "I've analyzed 23 proposals from the past 18 months:

PATTERN DETECTED:
Proposals that stall at procurement (9 of 23, 39%) share these traits:
├── Missing security questionnaire responses: 78% of stalled
├── No procurement contact identified upfront: 67% of stalled
└── Technical evaluation bypassed procurement: 56% of stalled

CONTRAST WITH SUCCESSES:
Proposals that closed (11 of 23) had:
├── Security questionnaire completed before proposal: 91%
├── Procurement contact identified in discovery: 82%
└── Joint technical + procurement presentation: 73%

RECOMMENDED PROCESS CHANGE:
Add 'Procurement Discovery' stage after technical qualification.
Predicted impact: Reduce stall rate from 39% to ~15%.

Want me to update the proposal-builder skill with this checkpoint?"
```

</details>

<br/>

---

<br/>

## 💡 The Vision

<table>
<tr>
<td width="60%">

Imagine walking into the office and saying:

> *"Good morning. What do I need to know today?"*

And your AI companion responds:

> *"Good morning. Three things:*
>
> *First, Sarah Chen from TechCorp replied overnight. Her tone suggests strong interest, but she raised a timeline concern—this matches her pattern from March. I've drafted a response based on how Eduardo successfully handled a similar situation.*
>
> *Second, the board meeting is in 12 days. Based on our last three preps, you typically start financial review 10 days out. I've pre-populated the dashboard and flagged two line items that may draw questions.*
>
> *Third, there's a grant deadline I've been tracking. Given our success rate with NSF vs. private foundations, I recommend we pass. But if you want to pursue it, here's what it would take."*

**This is A2I2.**

</td>
<td width="40%" align="center">

```
    ╭──────────────────╮
    │   🤖 A2I2       │
    │                  │
    │  ┌────────────┐  │
    │  │ REMEMBER   │  │
    │  │ LEARN      │  │
    │  │ THINK      │  │
    │  │ SPEAK      │  │
    │  │ ACT        │  │
    │  └────────────┘  │
    │                  │
    │  Your AI Chief   │
    │    of Staff      │
    ╰──────────────────╯
```

</td>
</tr>
</table>

<br/>

## 🎯 Core Features

<table>
<tr>
<td align="center" width="33%">

### 🧠 **Persistent Memory**

Everything remembered across sessions—conversations, decisions, relationships, and outcomes.

</td>
<td align="center" width="33%">

### 📚 **Continuous Learning**

Learns from every interaction, correction, and outcome to improve over time.

</td>
<td align="center" width="33%">

### 👤 **Digital Twin**

Models *how* you think, not just what you said—anticipating needs before you express them.

</td>
</tr>
<tr>
<td align="center" width="33%">

### 🎙️ **Natural Voice**

Full-duplex voice via NVIDIA PersonaPlex with 170ms latency for natural conversation.

</td>
<td align="center" width="33%">

### 🔐 **Trusted Autonomy**

Acts independently within earned trust boundaries—escalating when uncertain.

</td>
<td align="center" width="33%">

### 📋 **Work Coordination**

Functions as a true Chief of Staff—coordinating, briefing, and executing.

</td>
</tr>
</table>

<br/>

---

<br/>

## 🔄 How A2I2 Compares

| Capability | A2I2 | ChatGPT | Traditional CRM | Task Manager |
|:-----------|:----:|:-------:|:---------------:|:------------:|
| **Remembers conversations** | Across all sessions | Per chat only | Manual notes | No |
| **Learns your preferences** | Automatically | Limited | Manual config | No |
| **Understands relationships** | Knowledge graph | No | Contact list | No |
| **Natural voice interface** | 170ms latency | Voice mode | No | No |
| **Takes actions autonomously** | Within boundaries | No | Workflows | Automation |
| **Integrates with your tools** | Native | Plugins | Native | Native |
| **Builds institutional memory** | Core feature | No | Sort of | No |
| **Explains its reasoning** | Always | Sometimes | No | No |
| **Works offline** | Local-first | No | Varies | Varies |
| **Open source** | Yes | No | Varies | Varies |

### When to Use A2I2

✅ **Use A2I2 when you need:**
- An AI that remembers everything about your organization
- Natural voice interaction with business context
- Autonomous task execution within safe boundaries
- Pattern detection across months of interactions
- Relationship intelligence beyond a CRM

❌ **Don't use A2I2 when you need:**
- Simple chatbot for customer service
- One-off questions without context
- Real-time collaboration (use Slack/Teams)
- Financial transaction processing (never autonomous)

<br/>

---

<br/>

## 🆕 Seven Novel Concepts

A2I2 introduces genuinely novel concepts that differentiate it from existing AI solutions:

| # | Concept | Acronym | Description |
|:-:|:--------|:-------:|:------------|
| 1 | **Cognitive Architecture Protocol** | `CAP` | Open standard for organizational memory—portable, interoperable AI memory |
| 2 | **Digital Twin Modeling** | `DTM` | Model *how* users think, not just what they said—cognitive pattern matching |
| 3 | **Autonomy Trust Ledger** | `ATL` | Auditable trust progression with immutable audit trail—earned autonomy |
| 4 | **Voice-Native Knowledge Graph** | `VNKG` | Knowledge structured for spoken retrieval—optimized for voice-first interfaces |
| 5 | **Institutional Memory Crystallization** | `IMC` | Automated tacit knowledge capture—preserving organizational wisdom |
| 6 | **Chief of Staff Protocol** | `CoSP` | Formal specification for AI work coordination—structured delegation |
| 7 | **Federated Organizational Intelligence** | `FOI` | Privacy-preserving learning across deployments—collective intelligence |

<br/>

---

<br/>

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          A2I2 ARCHITECTURE                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                         🎤 INTERFACE LAYER                               │   │
│   │    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │   │
│   │    │  Voice   │    │   Chat   │    │   API    │    │ Webhooks │        │   │
│   │    │ (Real-   │    │  (Web)   │    │  (REST)  │    │ (Events) │        │   │
│   │    │  time)   │    │          │    │          │    │          │        │   │
│   │    └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘        │   │
│   └─────────┼──────────────┼──────────────┼──────────────┼─────────────────┘   │
│             └──────────────┴──────┬───────┴──────────────┘                     │
│                                   │                                             │
│   ┌───────────────────────────────▼─────────────────────────────────────────┐   │
│   │                      🎯 ORCHESTRATION LAYER                              │   │
│   │    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │   │
│   │    │   Context   │    │  Decision   │    │   Action    │                │   │
│   │    │   Manager   │    │   Engine    │    │  Executor   │                │   │
│   │    └─────────────┘    └─────────────┘    └─────────────┘                │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                   │                                             │
│   ┌───────────────────────────────▼─────────────────────────────────────────┐   │
│   │                        🧠 MEMORY LAYER                                  │   │
│   │    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐          │   │
│   │    │Episodic│  │Semantic│  │Proced- │  │Working │  │ Graph  │          │   │
│   │    │ Memory │  │ Memory │  │ ural   │  │ Memory │  │ Memory │          │   │
│   │    │ (What  │  │ (What  │  │(How We │  │(Current│  │ (How   │          │   │
│   │    │Happened│  │We Know)│  │ Work)  │  │Context)│  │Things  │          │   │
│   │    │   )    │  │        │  │        │  │        │  │Connect)│          │   │
│   │    └────────┘  └────────┘  └────────┘  └────────┘  └────────┘          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                   │                                             │
│   ┌───────────────────────────────▼─────────────────────────────────────────┐   │
│   │                       💾 STORAGE LAYER                                  │   │
│   │    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │   │
│   │    │ Neon/       │    │   Vector    │    │    Git      │                │   │
│   │    │ Supabase    │    │   Store     │    │ (Versioned) │                │   │
│   │    │ (Postgres)  │    │ (pgvector)  │    │             │                │   │
│   │    └─────────────┘    └─────────────┘    └─────────────┘                │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

<br/>

---

<br/>

## 📊 Memory System Deep Dive

A2I2 implements a comprehensive five-layer memory architecture inspired by human cognitive systems:

<table>
<tr>
<th align="center">Memory Type</th>
<th align="center">Purpose</th>
<th align="center">What It Stores</th>
<th align="center">Storage</th>
</tr>
<tr>
<td align="center">

**📅 Episodic**

</td>
<td>What happened</td>
<td>Events, conversations, decisions, outcomes, milestones</td>
<td><code>arcus_episodic_memory</code></td>
</tr>
<tr>
<td align="center">

**📖 Semantic**

</td>
<td>What we know</td>
<td>Facts, patterns, frameworks, definitions, best practices</td>
<td><code>arcus_semantic_memory</code></td>
</tr>
<tr>
<td align="center">

**⚙️ Procedural**

</td>
<td>How we work</td>
<td>Workflows, preferences, standards, templates, decision trees</td>
<td><code>arcus_procedural_memory</code></td>
</tr>
<tr>
<td align="center">

**💭 Working**

</td>
<td>Current context</td>
<td>Active task, conversation, retrieved context, draft outputs</td>
<td>Session memory</td>
</tr>
<tr>
<td align="center">

**🔗 Relational**

</td>
<td>How things connect</td>
<td>Entity relationships, influence networks, connections</td>
<td><code>arcus_entities</code>, <code>arcus_relationships</code></td>
</tr>
</table>

### How Memory Operations Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        MEMORY OPERATIONS LIFECYCLE                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                         🎯 LEARN (Capture)                               │    │
│  │                                                                          │    │
│  │   User says: "Actually, Sarah prefers email over Slack"                 │    │
│  │                              │                                           │    │
│  │                              ▼                                           │    │
│  │   ┌──────────────────────────────────────────────────┐                  │    │
│  │   │  1. Classify: procedural/preference               │                  │    │
│  │   │  2. Extract: entity=Sarah, pref=email>Slack       │                  │    │
│  │   │  3. Score: confidence=0.95 (explicit statement)   │                  │    │
│  │   │  4. Store: arcus_procedural_memory + graph edge   │                  │    │
│  │   │  5. Index: vector embedding for semantic search   │                  │    │
│  │   └──────────────────────────────────────────────────┘                  │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                         🔍 RECALL (Retrieve)                            │    │
│  │                                                                          │    │
│  │   User asks: "How should I reach out to Sarah?"                         │    │
│  │                              │                                           │    │
│  │                              ▼                                           │    │
│  │   ┌───────────────┬───────────────┬───────────────┐                     │    │
│  │   │ Vector Search │ Pattern Match │ Graph Traverse│                     │    │
│  │   │ "Sarah"       │ communication │ Sarah ──► ?   │                     │    │
│  │   │ "reach out"   │ preferences   │ preferences   │                     │    │
│  │   └───────┬───────┴───────┬───────┴───────┬───────┘                     │    │
│  │           └───────────────┼───────────────┘                             │    │
│  │                           ▼                                              │    │
│  │   Response: "Sarah prefers email over Slack (confidence: 95%)"          │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                       🔗 RELATE (Connect)                                │    │
│  │                                                                          │    │
│  │   Discovered: "Sarah joined TechCorp as CIO last month"                 │    │
│  │                              │                                           │    │
│  │                              ▼                                           │    │
│  │   ┌──────────────────────────────────────────────────┐                  │    │
│  │   │                                                   │                  │    │
│  │   │   [Sarah Chen] ─── works_at ───► [TechCorp]      │                  │    │
│  │   │        │                              │           │                  │    │
│  │   │        │                              │           │                  │    │
│  │   │   role: CIO                    industry: Tech    │                  │    │
│  │   │   start: 2026-01              employees: 500+    │                  │    │
│  │   │   confidence: 0.9            relationship: warm  │                  │    │
│  │   │                                                   │                  │    │
│  │   └──────────────────────────────────────────────────┘                  │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                       💡 REFLECT (Synthesize)                           │    │
│  │                                                                          │    │
│  │   Periodic analysis of accumulated memories                              │    │
│  │                              │                                           │    │
│  │                              ▼                                           │    │
│  │   ┌──────────────────────────────────────────────────┐                  │    │
│  │   │  PATTERN DETECTED:                                │                  │    │
│  │   │                                                   │                  │    │
│  │   │  "Proposals with SROI metrics have 40% higher    │                  │    │
│  │   │   acceptance rate (based on 23 proposals,        │                  │    │
│  │   │   18 months of data, confidence: 0.87)"          │                  │    │
│  │   │                                                   │                  │    │
│  │   │  RECOMMENDATION:                                  │                  │    │
│  │   │  Update proposal-builder skill to include        │                  │    │
│  │   │  SROI calculations by default.                   │                  │    │
│  │   └──────────────────────────────────────────────────┘                  │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Auto-Capture Triggers

A2I2 automatically captures knowledge when these events occur:

| Trigger | Memory Type | Example |
|:--------|:------------|:--------|
| User corrects Claude | **Procedural** | "Actually, I prefer TypeScript" → Preference stored |
| Decision is made | **Episodic** | "Let's go with vendor A" → Decision + rationale captured |
| New fact shared | **Semantic** | "TechCorp has 500 employees" → Fact stored with confidence |
| Relationship revealed | **Relational** | "Sarah reports to the CEO" → Graph edge created |
| Successful workflow | **Procedural** | Proposal accepted → Workflow pattern reinforced |
| Error or failure | **Episodic** | What went wrong + context for future avoidance |

### Memory Retrieval Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            CONTEXT INJECTION FLOW                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   SESSION START                                                                  │
│   ═══════════════                                                               │
│                                                                                  │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│   │ CLAUDE.memory.md│    │   Supabase      │    │  Vector Store   │            │
│   │ (preferences)   │    │ (recent 7 days) │    │ (embeddings)    │            │
│   └────────┬────────┘    └────────┬────────┘    └────────┬────────┘            │
│            │                      │                      │                      │
│            └──────────────────────┼──────────────────────┘                      │
│                                   │                                             │
│                                   ▼                                             │
│                        ┌─────────────────────┐                                  │
│                        │   CONTEXT PACKAGE   │                                  │
│                        │  • User preferences │                                  │
│                        │  • Active projects  │                                  │
│                        │  • Recent decisions │                                  │
│                        │  • Relevant entities│                                  │
│                        └─────────────────────┘                                  │
│                                   │                                             │
│                                   ▼                                             │
│                        ┌─────────────────────┐                                  │
│                        │  TOKEN BUDGET CHECK │                                  │
│                        │  Prioritize by:     │                                  │
│                        │  • Recency          │                                  │
│                        │  • Relevance score  │                                  │
│                        │  • Confidence       │                                  │
│                        └─────────────────────┘                                  │
│                                   │                                             │
│                                   ▼                                             │
│                        ┌─────────────────────┐                                  │
│                        │  ENRICHED SESSION   │                                  │
│                        │  Claude knows you   │                                  │
│                        └─────────────────────┘                                  │
│                                                                                  │
│   DURING INTERACTION                                                            │
│   ═══════════════════                                                           │
│                                                                                  │
│   User mentions "Sarah" ──► Real-time graph lookup ──► Inject Sarah context    │
│   Similar situation ──────► Episodic search ──────────► "Last time we..."      │
│   Workflow triggered ─────► Procedural lookup ────────► Apply learned prefs    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

<br/>

---

<br/>

## 🔐 Autonomy Progression

A2I2 uses a **Trust Ladder** model—AI earns autonomy through demonstrated competence:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   LEVEL 4  ████████████████████████████████████████  TRUSTED PARTNER       │
│            • Full peer-level collaboration                                  │
│            • Strategic decision participation                               │
│            • External stakeholder communication                             │
│                                                                              │
│   LEVEL 3  ██████████████████████████████           FULLY AUTONOMOUS       │
│            • Act within boundaries without asking                           │
│            • Proactive task initiation                                      │
│            • Post-action notification                                       │
│                                                                              │
│   LEVEL 2  ████████████████████                     AUTONOMOUS             │
│            • Pre-approved action types                                      │
│            • No confirmation for routine tasks                              │
│            • Human review after action                                      │
│                                                                              │
│   LEVEL 1  ██████████████                           SUPERVISED             │
│            • Claude proposes actions                                        │
│            • Human confirms before execution                                │
│            • Learning from confirmations                                    │
│                                                                              │
│   LEVEL 0  ████████                                 ASSISTED (Start Here)  │
│            • Human requests, Claude advises                                 │
│            • Human executes all actions                                     │
│            • Observing patterns and preferences                             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Autonomy Boundaries by Category

| Action | L0 | L1 | L2 | L3 | L4 | Notes |
|:-------|:--:|:--:|:--:|:--:|:--:|:------|
| Read files | ✅ | ✅ | ✅ | ✅ | ✅ | Always allowed |
| Search/research | ✅ | ✅ | ✅ | ✅ | ✅ | Always allowed |
| Generate content | ✅ | ✅ | ✅ | ✅ | ✅ | Draft requires review at L0 |
| Write files | ❌ | 🔸 | ✅ | ✅ | ✅ | 🔸 = with permission |
| Git commit | ❌ | 🔸 | ✅ | ✅ | ✅ | Branch restrictions apply |
| Send email | ❌ | ❌ | ❌ | 🔸 | ✅ | Templates only at L3 |
| Schedule meetings | ❌ | ❌ | 🔸 | ✅ | ✅ | Internal only at L2 |
| External comms | ❌ | ❌ | ❌ | ❌ | 🔸 | Always human review |
| Financial actions | ❌ | ❌ | ❌ | ❌ | ❌ | **Never autonomous** |

<br/>

---

<br/>

## 🎙️ NVIDIA PersonaPlex Voice Integration

A2I2 leverages **NVIDIA PersonaPlex** (released January 2026) to deliver a voice-first experience that feels like talking to a real assistant—not a robot.

### Why PersonaPlex Changes Everything

Traditional voice assistants use a pipeline approach: Speech-to-Text → LLM → Text-to-Speech. This creates noticeable delays and unnatural pauses. PersonaPlex is **fundamentally different**—it's a unified speech-to-speech model that:

| Traditional Pipeline | PersonaPlex |
|:---------------------|:------------|
| ~500-800ms latency | **170ms latency** |
| Waits for you to finish | **Listens while speaking** |
| Fixed, robotic voice | **16 customizable voices** |
| Can't handle interruptions | **Natural interruption (240ms)** |
| No backchannels | **"uh-huh", "I see", "got it"** |

### Full-Duplex Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    NVIDIA PERSONAPLEX + ARCUS INTEGRATION                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                        FULL-DUPLEX AUDIO STREAM                          │   │
│   │                                                                          │   │
│   │     YOUR VOICE ════════════════════════════════════════► PROCESSING     │   │
│   │         🎤                                                    │          │   │
│   │         │                    SIMULTANEOUS                     │          │   │
│   │         │              (not turn-taking)                     ▼          │   │
│   │     ARCUS VOICE ◄════════════════════════════════════════ RESPONSE      │   │
│   │         🔊                                                               │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                     PERSONAPLEX MODEL ARCHITECTURE                       │   │
│   │                                                                          │   │
│   │   [Your Audio] ──► ┌──────────────┐                                     │   │
│   │                    │    MIMI      │                                     │   │
│   │                    │   Encoder    │──┐                                  │   │
│   │                    │  (ConvNet +  │  │                                  │   │
│   │                    │ Transformer) │  │                                  │   │
│   │                    └──────────────┘  │                                  │   │
│   │                                      │     ┌──────────────────┐         │   │
│   │   [Voice Prompt] ────────────────────┼────►│                  │         │   │
│   │   (Arcus persona)                    │     │   7B PARAMETER   │         │   │
│   │                                      ├────►│   TRANSFORMER    │         │   │
│   │   [Text Prompt] ─────────────────────┘     │                  │         │   │
│   │   (Knowledge context)                      │  • Temporal      │         │   │
│   │                                            │  • Depth         │         │   │
│   │                                            │  • Full-duplex   │         │   │
│   │                                            │    capable       │         │   │
│   │                                            └────────┬─────────┘         │   │
│   │                                                     │                   │   │
│   │                                            ┌────────▼─────────┐         │   │
│   │                                            │      MIMI       │         │   │
│   │                                            │     Decoder     │         │   │
│   │                                            │    (ConvNet +   │         │   │
│   │                                            │   Transformer)  │         │   │
│   │                                            └────────┬─────────┘         │   │
│   │                                                     │                   │   │
│   │                                            [Arcus Voice] ──► 🔊         │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   LATENCY: 170ms (turn-taking) │ 240ms (interruption handling)                  │
│   SAMPLE RATE: 24kHz │ OPEN SOURCE: Yes (MIT license)                           │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Knowledge-Enriched Voice Conversations

Unlike standalone voice assistants, A2I2's voice layer is connected to the full memory system:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     ARCUS + PERSONAPLEX: CONTEXT FLOW                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────┐          ┌─────────────────┐         ┌─────────────────┐  │
│   │   YOU (Voice)   │          │   PERSONAPLEX   │         │ KNOWLEDGE REPO  │  │
│   │                 │          │                 │         │                 │  │
│   │ "Tell me about  │ ──────►  │  Transcribe +   │ ──────► │ Query:          │  │
│   │  the TechCorp   │          │  understand     │         │ • Sarah Chen    │  │
│   │  meeting with   │          │  intent         │         │ • TechCorp      │  │
│   │  Sarah"         │          │                 │         │ • Past meetings │  │
│   │                 │          │                 │         │ • Relationships │  │
│   └─────────────────┘          └────────┬────────┘         └────────┬────────┘  │
│                                         │                           │           │
│                                         │     ┌─────────────────────┘           │
│                                         │     │                                 │
│                                         ▼     ▼                                 │
│                                ┌─────────────────────┐                          │
│                                │   CONTEXT INJECTOR  │                          │
│                                │                     │                          │
│                                │ "Arcus persona +    │                          │
│                                │  Sarah prefers      │                          │
│                                │  concise updates,   │                          │
│                                │  last meeting was   │                          │
│                                │  about Q1 roadmap,  │                          │
│                                │  action items were  │                          │
│                                │  security review"   │                          │
│                                │                     │                          │
│                                └──────────┬──────────┘                          │
│                                           │                                     │
│                                           ▼                                     │
│                                ┌─────────────────────┐                          │
│                                │   VOICE RESPONSE    │                          │
│                                │   (170ms)           │                          │
│                                │                     │                          │
│                                │ "Your last meeting  │                          │
│                                │  with Sarah at      │                          │
│                                │  TechCorp was       │                          │
│                                │  January 15th..."   │                          │
│                                └─────────────────────┘                          │
│                                                                                  │
│   MEMORY CAPTURE: Conversation stored to episodic memory for future reference  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Voice Capabilities in Practice

<table>
<tr>
<td width="50%">

**Natural Conversation Features**

| Feature | Description |
|:--------|:------------|
| **Backchannels** | "uh-huh", "got it", "I see" while you speak |
| **Interruptions** | Cut in mid-sentence, Arcus responds in 240ms |
| **Emotion awareness** | Detects tone shifts, adjusts response |
| **Turn-taking** | Natural conversation rhythm, not ping-pong |
| **Context memory** | References earlier in the conversation |

**Available Voice Personas**

| Category | Voices | Best For |
|:---------|:-------|:---------|
| Natural Female | NATF0-NATF3 | Professional, coaching |
| Natural Male | NATM0-NATM3 | Advisory, executive |
| Expressive Female | VARF0-VARF4 | Customer service |
| Expressive Male | VARM0-VARM4 | Presentations |

</td>
<td width="50%">

**Meeting Integration**

```
┌─────────────────────────────┐
│    MEETING SCENARIOS        │
├─────────────────────────────┤
│                             │
│  📞 JOIN CALLS              │
│  • Zoom, Meet, Teams        │
│  • Listen + transcribe      │
│  • Real-time summaries      │
│                             │
│  📝 CAPTURE                 │
│  • Action items extracted   │
│  • Decisions logged         │
│  • Commitments tracked      │
│                             │
│  🎯 ASSIST                  │
│  • "Arcus, pull up the      │
│     Q3 numbers"             │
│  • In-meeting fact-check    │
│  • Follow-up scheduling     │
│                             │
│  📊 POST-MEETING            │
│  • Auto-generated summary   │
│  • Action items to Asana    │
│  • Follow-up emails drafted │
│                             │
└─────────────────────────────┘
```

</td>
</tr>
</table>

### Performance Comparison

| Metric | A2I2 + PersonaPlex | OpenAI Realtime | Traditional Pipeline |
|:-------|:------------------:|:---------------:|:--------------------:|
| Turn-taking latency | **170ms** | ~200ms | 500-800ms |
| Interruption response | **240ms** | ~300ms | Not supported |
| Voice customization | 16 presets | Limited | Full (separate TTS) |
| Self-hostable | **Yes** | No | Yes |
| Memory integration | **Native** | Manual | Manual |
| Full duplex | **Yes** | Yes | No |
| Open source | **Yes** | No | Varies |
| Cost | GPU only | $0.06/min | Per-API-call |

<br/>

---

<br/>

## 🔧 Tool Orchestration & Workflow Engine

A2I2 doesn't just remember—it **acts**. The platform orchestrates tools, skills, and integrations to automate complex workflows while learning from every execution.

### Orchestration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          TOOL ORCHESTRATION ENGINE                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                            ┌─────────────────────┐                              │
│                            │   USER REQUEST      │                              │
│                            │ "Prepare a proposal │                              │
│                            │  for TechCorp"      │                              │
│                            └──────────┬──────────┘                              │
│                                       │                                         │
│                                       ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                        DECISION ENGINE                                   │   │
│   │                                                                          │   │
│   │  1. CLASSIFY INTENT          2. CHECK AUTONOMY         3. LOAD CONTEXT   │   │
│   │  ┌─────────────────┐        ┌─────────────────┐       ┌─────────────────┐│   │
│   │  │ proposal        │        │ Level: 2        │       │ TechCorp:       ││   │
│   │  │ generation      │        │ Can execute     │       │ • Industry      ││   │
│   │  │ → skill match   │        │ without asking  │       │ • Contacts      ││   │
│   │  └─────────────────┘        └─────────────────┘       │ • History       ││   │
│   │                                                        │ • Preferences   ││   │
│   │                                                        └─────────────────┘│   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                       │                                         │
│                                       ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                        WORKFLOW PLANNER                                  │   │
│   │                                                                          │   │
│   │  Based on procedural memory + past successes, generate execution plan:  │   │
│   │                                                                          │   │
│   │  Step 1: Research        Step 2: Generate       Step 3: Review          │   │
│   │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │   │
│   │  │ intelligence-   │───►│ proposal-       │───►│ quality-        │     │   │
│   │  │ extractor       │    │ builder         │    │ reviewer        │     │   │
│   │  │                 │    │                 │    │                 │     │   │
│   │  │ Pull TechCorp   │    │ Executive       │    │ Brand + tone    │     │   │
│   │  │ context from    │    │ formatting,     │    │ check, fact     │     │   │
│   │  │ knowledge repo  │    │ SROI metrics    │    │ verification    │     │   │
│   │  └─────────────────┘    └─────────────────┘    └─────────────────┘     │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                       │                                         │
│                                       ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                        ACTION EXECUTOR                                   │   │
│   │                                                                          │   │
│   │  Execute each skill, capture results, handle errors:                    │   │
│   │                                                                          │   │
│   │  ┌──────────────────────────────────────────────────────────────────┐   │   │
│   │  │ [✓] intelligence-extractor: TechCorp profile loaded             │   │   │
│   │  │ [✓] proposal-builder: Draft generated with SROI                  │   │   │
│   │  │ [✓] quality-reviewer: Passed (score: 94/100)                     │   │   │
│   │  │ [→] Ready for human review                                        │   │   │
│   │  └──────────────────────────────────────────────────────────────────┘   │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                       │                                         │
│                                       ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                        LEARNING ENGINE                                   │   │
│   │                                                                          │   │
│   │  Capture workflow execution for future optimization:                    │   │
│   │                                                                          │   │
│   │  • Workflow pattern: TechCorp_proposal_v1                               │   │
│   │  • Execution time: 4.2 minutes                                          │   │
│   │  • Success: Pending human approval                                       │   │
│   │  • Context used: 3 episodic, 5 semantic, 1 procedural                   │   │
│   │  • Next time: Pre-load TechCorp preferences automatically               │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Integration Ecosystem

A2I2 connects to your existing tools and learns from the data flowing through them:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          INTEGRATION LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   PRODUCTIVITY                    COMMUNICATION                DEVELOPMENT      │
│   ════════════                    ═════════════                ═══════════      │
│                                                                                  │
│   ┌─────────┐  ┌─────────┐       ┌─────────┐  ┌─────────┐    ┌─────────┐       │
│   │  Asana  │  │ Google  │       │  Gmail  │  │  Slack  │    │ GitHub  │       │
│   │         │  │Calendar │       │         │  │         │    │         │       │
│   └────┬────┘  └────┬────┘       └────┬────┘  └────┬────┘    └────┬────┘       │
│        │            │                  │            │              │            │
│        │  Tasks     │  Events          │  Threads   │  Messages    │  Issues    │
│        │  assigned  │  scheduled       │  analyzed  │  captured    │  tracked   │
│        │            │                  │            │              │            │
│        └────────────┴──────────────────┴────────────┴──────────────┘            │
│                                        │                                        │
│                                        ▼                                        │
│                        ┌───────────────────────────────┐                       │
│                        │      KNOWLEDGE EXTRACTION      │                       │
│                        │                               │                       │
│                        │  Email → Relationship signals │                       │
│                        │  Tasks → Project status       │                       │
│                        │  Calendar → Availability      │                       │
│                        │  Slack → Team dynamics        │                       │
│                        │  GitHub → Technical patterns  │                       │
│                        │                               │                       │
│                        └───────────────────────────────┘                       │
│                                        │                                        │
│                                        ▼                                        │
│                        ┌───────────────────────────────┐                       │
│                        │      ARCUS ACTIONS             │                       │
│                        │                               │                       │
│                        │  • Create Asana tasks         │                       │
│                        │  • Schedule meetings          │                       │
│                        │  • Draft email responses      │                       │
│                        │  • Update Slack channels      │                       │
│                        │  • Create GitHub issues       │                       │
│                        │                               │                       │
│                        └───────────────────────────────┘                       │
│                                                                                  │
│   DATA SOURCES                   STORAGE                     VOICE              │
│   ════════════                   ═══════                     ═════              │
│                                                                                  │
│   ┌─────────┐  ┌─────────┐       ┌─────────┐               ┌─────────┐         │
│   │ Google  │  │ Notion  │       │  Neon/  │               │PersonaPx│         │
│   │  Drive  │  │         │       │Supabase │               │         │         │
│   └────┬────┘  └────┬────┘       └────┬────┘               └────┬────┘         │
│        │            │                  │                         │              │
│        │  Docs      │  Wiki            │  Postgres +             │  Real-time   │
│        │  indexed   │  synced          │  pgvector               │  voice I/O   │
│        │                               │  (on Vercel)            │              │
│        │                                                                        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Workflow Examples

<details>
<summary><b>Morning Briefing Workflow</b></summary>

```yaml
Trigger: Daily at 7:00 AM or "Good morning" voice command
Steps:
  1. Query overnight emails → Extract urgent items
  2. Check calendar → Today's meetings with context
  3. Query Asana → Overdue and due-today tasks
  4. Run episodic recall → Recent decisions needing follow-up
  5. Check knowledge graph → Relationship follow-ups due
  6. Synthesize → 3-item priority briefing

Output: Voice or text briefing with action suggestions
Learning: Track which items user acts on first
```

</details>

<details>
<summary><b>Client Proposal Workflow</b></summary>

```yaml
Trigger: "Create a proposal for [client]"
Steps:
  1. intelligence-extractor → Pull client context from memory
  2. Recall → Similar successful proposals
  3. proposal-builder → Generate with SROI metrics
  4. quality-reviewer → Brand and accuracy check
  5. Create draft → Save to Google Drive
  6. Optional: Create Asana task for review

Output: Executive-ready proposal document
Learning: Track acceptance rate, refine approach
```

</details>

<details>
<summary><b>Meeting Follow-up Workflow</b></summary>

```yaml
Trigger: Meeting ends (calendar event or voice "meeting's over")
Steps:
  1. Capture → Store transcript to episodic memory
  2. Extract → Action items, decisions, commitments
  3. Create tasks → Push to Asana with context
  4. Draft follow-up → Email summary for attendees
  5. Update graph → New relationships or changes
  6. Schedule → Follow-up meeting if needed

Output: Tasks created, email drafted, memory updated
Learning: Track which action items get completed
```

</details>

<br/>

---

<br/>

## 🚀 Getting Started

### Quick Start (5 minutes)

A2I2 works immediately with Claude Code. For basic functionality:

```bash
# Clone the repository
git clone https://github.com/therealchandlerbing/a2i2-beta-v1.git
cd a2i2-beta-v1

# Initialize session memory
cp .claude/skills/knowledge-repository/config/memory-template.md CLAUDE.memory.md
```

**That's it.** Claude will now read `CLAUDE.memory.md` at session start and learn your preferences.

### Talking to A2I2

Use natural language—no special commands needed:

| What You Say | What A2I2 Does |
|:-------------|:---------------|
| "Remember that Sarah prefers email over Slack" | Stores to procedural memory |
| "What do you know about the TechCorp deal?" | Retrieves from semantic + episodic memory |
| "How did we handle the last board presentation?" | Searches episodic memory for precedents |
| "Sarah works at TechCorp as CIO" | Creates relationship in knowledge graph |
| "Create a proposal for DataFlow" | Triggers proposal workflow with context |

### Adding Persistent Storage (15 minutes)

For cross-session memory that survives beyond `CLAUDE.memory.md`:

<details>
<summary><b>Option A: Vercel + Neon (Recommended)</b></summary>

Deploy A2I2 as a web application with serverless PostgreSQL:

1. **Create a Neon Project** at [neon.tech](https://neon.tech)
   ```sql
   -- Enable required extensions
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   CREATE EXTENSION IF NOT EXISTS "vector";
   ```

2. **Run the Schema SQL**
   ```sql
   -- Copy contents of:
   -- .claude/skills/knowledge-repository/schemas/supabase-schema.sql
   -- (100% compatible with Neon)
   ```

3. **Deploy to Vercel**
   ```bash
   # Install Vercel CLI
   npm install -g vercel

   # Deploy
   vercel --prod
   ```

4. **Configure Environment**
   ```bash
   # In Vercel Dashboard → Settings → Environment Variables
   DATABASE_URL="postgres://user:pass@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require"
   ```

**Benefits:**
- Serverless scaling (pay for what you use)
- Database branching for dev/staging/prod
- Web dashboard for memory visualization
- API endpoints for external integrations

See **[VERCEL-NEON-INTEGRATION.md](docs/VERCEL-NEON-INTEGRATION.md)** for complete setup guide.

</details>

<details>
<summary><b>Option B: Supabase (Alternative)</b></summary>

1. **Create a Supabase Project** at [supabase.com](https://supabase.com)

2. **Run the Schema SQL**
   ```sql
   -- Copy contents of:
   -- .claude/skills/knowledge-repository/schemas/supabase-schema.sql
   ```

3. **Configure Connection**
   ```bash
   # Add to your environment
   export SUPABASE_URL="your-project-url"
   export SUPABASE_KEY="your-anon-key"
   ```

4. **Verify Tables Created**
   - `arcus_episodic_memory`
   - `arcus_semantic_memory`
   - `arcus_procedural_memory`
   - `arcus_knowledge_graph`
   - `arcus_entities`

</details>

### Enabling Voice (30 minutes)

For NVIDIA PersonaPlex voice integration:

<details>
<summary><b>PersonaPlex Setup Instructions</b></summary>

**Prerequisites:**
- GPU with ~16GB VRAM (or use CPU offload)
- Python 3.10+
- HuggingFace account (for model access)

**Installation:**
```bash
# Install system dependencies
# Ubuntu/Debian
sudo apt-get install libopus-dev

# macOS
brew install opus

# Accept model license
# Visit: https://huggingface.co/nvidia/personaplex-7b-v1
export HF_TOKEN=<your-huggingface-token>

# Clone and install
git clone https://github.com/NVIDIA/personaplex
cd personaplex
pip install moshi/.

# Optional: For memory-constrained GPUs
pip install accelerate
```

**Running the Server:**
```bash
# Create SSL directory
SSL_DIR=$(mktemp -d)

# Start server (with CPU offload for smaller GPUs)
python -m moshi.server --ssl "$SSL_DIR" --cpu-offload

# Access at: https://localhost:8998
```

**Recommended Voice for Arcus:** `NATF2` (natural female, professional tone)

See [PERSONAPLEX-INTEGRATION.md](.claude/skills/knowledge-repository/docs/PERSONAPLEX-INTEGRATION.md) for complete integration guide.

</details>

<br/>

---

<br/>

<details>
<summary><b>📁 Repository Structure</b></summary>

```
a2i2-beta-v1/
│
├── 📂 .claude/
│   └── 📂 skills/
│       └── 📂 knowledge-repository/          # 🧠 Core A2I2 skill
│           ├── 📄 SKILL.md                   # Operational logic
│           ├── 📄 README.md                  # Skill documentation
│           ├── 📄 QUICK-START.md             # Fast reference
│           ├── 📄 INDEX.md                   # Navigation guide
│           │
│           ├── 📂 docs/                      # Extended documentation
│           │   ├── 📄 VISION.md              # R2-D2 / Enterprise vision
│           │   ├── 📄 ARCHITECTURE.md        # Technical architecture
│           │   ├── 📄 STRATEGIC-REVIEW.md    # Novel concepts & IP
│           │   ├── 📄 PERSONAPLEX-INTEGRATION.md  # Voice integration
│           │   ├── 📄 PRACTICAL-IMPLEMENTATION.md
│           │   └── 📄 COMPANION-ENHANCEMENTS.md
│           │
│           ├── 📂 schemas/
│           │   └── 📄 supabase-schema.sql    # Database schema
│           │
│           ├── 📂 config/
│           │   ├── 📄 memory-template.md     # Session memory template
│           │   ├── 📄 hooks-config.json      # Hooks configuration
│           │   └── 📄 mcp-voice-config.json  # Voice configuration
│           │
│           └── 📂 src/
│               ├── 📄 knowledge_operations.py  # Python implementation
│               └── 📄 types.ts                 # TypeScript types
│
├── 📂 brand-standards/
│   └── 📂 arcus-innovation-studios/          # 🎨 Brand guidelines
│       ├── 📄 README.md
│       ├── 📄 arcus-brand-standards.md       # Complete brand guide
│       ├── 📄 arcus-quick-reference.md       # Quick reference
│       ├── 📄 arcus-integration-guide.md     # Integration patterns
│       └── 📄 arcus-quality-checklist.md     # Quality validation
│
├── 📂 docs/
│   └── 📄 A2I2-REFERENCE.md                  # Platform reference
│
├── 📄 CLAUDE.md                              # AI assistant instructions
├── 📄 CLAUDE.memory.md                       # Session memory file
├── 📄 LICENSE                                # MIT License
└── 📄 README.md                              # This file
```

</details>

<br/>

---

<br/>

## 📖 Documentation

| Document | Description | Audience |
|:---------|:------------|:---------|
| [**SKILL.md**](.claude/skills/knowledge-repository/SKILL.md) | Core operational logic | Developers |
| [**QUICK-START.md**](.claude/skills/knowledge-repository/QUICK-START.md) | Fast reference guide | Everyone |
| [**VERCEL-NEON-INTEGRATION.md**](docs/VERCEL-NEON-INTEGRATION.md) | Vercel + Neon deployment guide | Developers |
| [**VISION.md**](.claude/skills/knowledge-repository/docs/VISION.md) | R2-D2 / Enterprise vision | Stakeholders |
| [**ARCHITECTURE.md**](.claude/skills/knowledge-repository/docs/ARCHITECTURE.md) | Technical architecture | Developers |
| [**STRATEGIC-REVIEW.md**](.claude/skills/knowledge-repository/docs/STRATEGIC-REVIEW.md) | Novel concepts & IP | Leadership |
| [**PERSONAPLEX-INTEGRATION.md**](.claude/skills/knowledge-repository/docs/PERSONAPLEX-INTEGRATION.md) | Voice integration guide | Developers |
| [**Brand Standards**](brand-standards/arcus-innovation-studios/arcus-brand-standards.md) | Complete brand guide | Designers |

<br/>

---

<br/>

## 🗺️ Roadmap

<table>
<tr>
<th align="center" width="25%">Q1 2026</th>
<th align="center" width="25%">Q2 2026</th>
<th align="center" width="25%">Q3-Q4 2026</th>
<th align="center" width="25%">2027+</th>
</tr>
<tr>
<td valign="top">

**Foundation**

- [x] Core memory architecture
- [x] PersonaPlex voice integration
- [x] Autonomy progression model
- [x] Dedicated repository
- [ ] Digital Twin v1.0
- [ ] CAP specification v1.0

</td>
<td valign="top">

**Intelligence**

- [ ] Institutional Memory Crystallization
- [ ] Chief of Staff Protocol v1.0
- [ ] Enterprise multi-tenant
- [ ] Voice-Native Knowledge Graph

</td>
<td valign="top">

**Scale**

- [ ] Federated Organizational Intelligence
- [ ] Public API launch
- [ ] Partner ecosystem
- [ ] Advanced autonomy

</td>
<td valign="top">

**Vision**

- [ ] Full "Enterprise computer" experience
- [ ] Multi-modal understanding
- [ ] Emotional intelligence
- [ ] Cross-organization learning

</td>
</tr>
</table>

### Progress Visualization

```
Foundation    ███████████████████████░░░░░░░░░░░  67%
Intelligence  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0%
Scale         ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0%
Vision        ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0%
```

<br/>

---

<br/>

<details>
<summary><b>💻 Tech Stack Details</b></summary>

| Layer | Technology | Rationale |
|:------|:-----------|:----------|
| **LLM** | Claude (Anthropic) | Extended thinking, tool use |
| **Hosting** | Vercel | Serverless, edge network, instant deploys |
| **Database** | Neon or Supabase (PostgreSQL) | Serverless Postgres, branching, pgvector |
| **Vector Store** | pgvector | Semantic search, native Postgres |
| **Voice** | NVIDIA PersonaPlex | Full-duplex, 170ms latency |
| **Voice STT (alt)** | Deepgram | Low latency, real-time |
| **Voice TTS (alt)** | ElevenLabs | Natural voices, cloning |
| **Framework** | Next.js 14 (App Router) | Dashboard, API routes, React Server Components |
| **Automation** | Zapier + Hooks | Integration layer |

### Deployment Options

| Option | Database | Hosting | Best For |
|:-------|:---------|:--------|:---------|
| **Vercel + Neon** | Neon PostgreSQL | Vercel | Production web apps, serverless |
| **Supabase** | Supabase PostgreSQL | Self-managed | Real-time features, existing Supabase users |
| **CLI Only** | CLAUDE.memory.md | Local | Development, personal use |

### Infrastructure Requirements

**Development (Free Tier)**
- Neon: Free tier (0.5 GB storage, 190 compute hours)
- Vercel: Hobby plan (free)
- Total: $0/month

**Production (Recommended)**
- Neon: Launch plan ($19/month) - 10GB storage, autoscaling
- Vercel: Pro plan ($20/month) - Team features, analytics
- Total: $39/month

**With Voice (Phase 3+)**
- GPU server for PersonaPlex (~$0.75-1.00/hr on Lambda Labs or AWS)
- Or: Cloud GPU instance (AWS g5.xlarge, Lambda Labs A10)
- Estimated: $100-300/month for moderate usage

**Enterprise (Phase 4-5)**
- Neon: Scale plan ($69+/month)
- Vercel: Enterprise or self-hosted
- Background job processing (Vercel Cron or dedicated)
- Monitoring/observability (Datadog, Sentry)
- Estimated: $200-500/month

</details>

<br/>

---

<br/>

## ❓ Frequently Asked Questions

<details>
<summary><b>How is this different from ChatGPT with memory?</b></summary>

ChatGPT's memory is limited to preferences and facts within a single conversation history. A2I2 provides:

1. **Five distinct memory types** (episodic, semantic, procedural, working, relational) vs. a single fact store
2. **Relationship graph** that understands connections between people, organizations, and projects
3. **Pattern detection** that synthesizes insights across hundreds of interactions
4. **Autonomous actions** that execute workflows within defined boundaries
5. **Full ownership** of your data in your own Supabase instance
6. **Voice-native** design with NVIDIA PersonaPlex (170ms latency)

A2I2 is designed for organizational memory, not personal chat history.

</details>

<details>
<summary><b>What data does A2I2 store? Is it secure?</b></summary>

**Data stored:**
- Conversation summaries and extracted learnings
- Preferences and workflow patterns
- Relationship graphs (who knows who)
- Decision history and outcomes

**Security measures:**
- All data stored in your Supabase instance (you own it)
- Row-level security for multi-tenant support
- PII detection and redaction before storage
- Credentials and secrets are never stored
- Audit logging for all knowledge operations

**What's NOT stored:**
- Raw conversation transcripts (summarized instead)
- API keys, passwords, credentials
- Financial transaction details
- Anything you mark as "do not capture"

</details>

<details>
<summary><b>Can A2I2 send emails or make changes without asking?</b></summary>

It depends on your **autonomy level** configuration:

| Level | What A2I2 Can Do |
|:------|:-----------------|
| **0: Assisted** | Only advises, you execute everything |
| **1: Supervised** | Proposes actions, you confirm before execution |
| **2: Autonomous** | Executes pre-approved action types, you review after |
| **3: Trusted** | Acts independently, notifies on exceptions |
| **4: Partner** | Full collaboration with minimal oversight |

**Default:** Level 1 (Supervised). Financial actions are **never** autonomous at any level.

You control the progression and can dial it back at any time.

</details>

<details>
<summary><b>How does voice integration work?</b></summary>

A2I2 uses NVIDIA PersonaPlex for voice, which is fundamentally different from traditional voice assistants:

1. **Full-duplex**: Listens while speaking (no waiting for you to finish)
2. **170ms latency**: Faster than human conversation pauses
3. **Backchannels**: Says "uh-huh", "I see", "got it" naturally
4. **Interruption handling**: Responds in 240ms when you cut in
5. **Context-aware**: Has access to your full knowledge graph during voice

**Requirements:**
- GPU with ~16GB VRAM (or cloud GPU instance)
- ~$0.75-1.00/hour for cloud GPU
- Self-hosted (no per-minute API costs)

</details>

<details>
<summary><b>How much does A2I2 cost to run?</b></summary>

| Component | Cost | Notes |
|:----------|:-----|:------|
| **Supabase** | $25/month | Pro plan for pgvector |
| **Claude API** | Usage-based | Anthropic pricing |
| **Voice (PersonaPlex)** | $0.75-1.00/hr GPU | Only when running |
| **Voice (cloud)** | ~$100-300/month | Moderate usage |

**Total for most users:** $25-100/month without voice, $150-400/month with active voice usage.

Compare to: Enterprise memory platforms ($500+/month), AI assistant subscriptions ($20-200/month), traditional CRM ($50-300/user/month).

</details>

<details>
<summary><b>Can I use A2I2 with my team?</b></summary>

Yes, A2I2 supports multi-user deployments:

1. **Shared organizational memory**: Team-wide knowledge accessible to all
2. **Personal preferences**: Individual settings per user
3. **Row-level security**: Users see appropriate data based on role
4. **Handoff support**: Knowledge transfers when team members change

Enterprise multi-tenant support is on the roadmap for Q2 2026.

</details>

<details>
<summary><b>What integrations are supported?</b></summary>

**Currently supported:**
- Neon or Supabase (database)
- Vercel (hosting/deployment)
- Google Drive (documents)
- Git/GitHub (version control)

**On roadmap:**
- Asana (task management)
- Gmail (communication)
- Slack (messaging)
- Zoom (meetings)
- Calendar (scheduling)
- CRM systems (Salesforce, HubSpot)

A2I2 also supports webhooks and Zapier for custom integrations.

</details>

<details>
<summary><b>Why Vercel + Neon instead of Supabase?</b></summary>

Both are excellent options. Here's why you might choose one over the other:

**Choose Vercel + Neon when:**
- You want serverless scaling (scale to zero)
- You need database branching for dev/staging/prod
- You're building a web frontend for A2I2
- You want native Vercel integration
- You prefer pure PostgreSQL without proprietary features

**Choose Supabase when:**
- You need real-time subscriptions
- You want built-in authentication (auth.uid())
- You prefer a single platform for database + auth + storage
- You're already invested in the Supabase ecosystem

**Migration is easy:** The schema is 100% PostgreSQL-compatible, so you can switch between them with minimal code changes.

</details>

<br/>

---

<br/>

<details>
<summary><b>🤝 Contributing</b></summary>

We welcome contributions! A2I2 is a new kind of project—part AI system, part organizational philosophy.

### Ways to Contribute

| Type | Description |
|:-----|:------------|
| 🐛 **Bug Reports** | Found something broken? Open an issue |
| 💡 **Feature Ideas** | Have ideas for novel concepts? Share them |
| 📝 **Documentation** | Help improve guides and examples |
| 🔧 **Code** | Implement new features or fix bugs |
| 🧪 **Testing** | Help test in different environments |

### Development Setup

```bash
# Clone the repo
git clone https://github.com/therealchandlerbing/a2i2-beta-v1.git
cd a2i2-beta-v1

# Create a branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add -A
git commit -m "Add: your feature description"

# Push and create PR
git push -u origin feature/your-feature-name
```

</details>

<br/>

---

<br/>

## 🏢 About Arcus Innovation Studios

<table>
<tr>
<td width="70%">

**Arcus Innovation Studios** delivers systematic innovation evaluation for organizations addressing the 90% failure rate through data-driven assessment methodology.

- **6,000+** technologies evaluated
- **13 years** of data
- **30-day** decision cycles
- **Board-ready** assessments

We're building the knowledge foundation for tomorrow's AI capabilities.

</td>
<td width="30%" align="center">

```
    ╭─────────────────╮
    │                 │
    │     ARCUS       │
    │   Innovation    │
    │    Studios      │
    │                 │
    │  Seattle        │
    │  São Paulo      │
    │  Cotonou        │
    │                 │
    ╰─────────────────╯
```

</td>
</tr>
</table>

<br/>

---

<br/>

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

<br/>

---

<br/>

<div align="center">

### 🌟 Star this repo if you believe in the future of AI companions!

<br/>

**A2I2** — *Transforming AI from tools into trusted partners*

<br/>

*"The journey of a thousand light years begins with a single knowledge entry."*

<br/>

---

<br/>

Made with 🧠 by [Arcus Innovation Studios](https://github.com/therealchandlerbing)

[![GitHub](https://img.shields.io/badge/GitHub-therealchandlerbing-0A2540?style=flat-square&logo=github)](https://github.com/therealchandlerbing)

</div>
