# Arcus Knowledge Repository - Quick Start

**Get up and running in 5 minutes.**

---

## What This Does

Gives Claude persistent memory across sessions - it remembers your preferences, learns from interactions, and builds knowledge about your organization over time.

## Setup (One-Time)

### Step 1: Deploy Database Schema

In Supabase SQL Editor:
```sql
-- Copy and run: schemas/supabase-schema.sql
```

This creates the tables for all memory types.

### Step 2: Initialize Memory File

The `CLAUDE.memory.md` file is already created at the repository root. It tracks:
- Your preferences
- Active projects
- Recent learnings
- Session context

### Step 3: Verify

Ask Claude:
```
"What do you remember about my preferences?"
```

It should read from `CLAUDE.memory.md` and respond with your current settings.

---

## Daily Usage

### Claude Automatically...

| Trigger | What Gets Captured |
|---------|-------------------|
| You correct Claude | Preference saved |
| You make a decision | Event logged |
| You share new info | Fact stored |
| Workflow succeeds | Pattern recorded |
| You mention someone | Entity tracked |

### You Can Explicitly...

**Learn something:**
```
"Remember that I prefer TypeScript for new projects"
"Learn that Sarah Chen is our contact at TechCorp"
```

**Recall something:**
```
"What do you know about TechCorp?"
"How did we handle the last proposal?"
```

**Connect things:**
```
"Sarah introduced us to James"
"This project depends on the API integration"
```

---

## Memory Types at a Glance

| Type | What It Stores | Example |
|------|---------------|---------|
| **Episodic** | Events, decisions, outcomes | "We decided to use LangGraph on 2026-01-24" |
| **Semantic** | Facts, patterns, knowledge | "Sarah prefers data-driven proposals" |
| **Procedural** | Workflows, preferences | "Always run tests before committing" |
| **Graph** | Relationships, connections | "Sarah works_at TechCorp" |

---

## Quick Commands

### View Current Memory
```
Read CLAUDE.memory.md
```

### Check What Claude Knows About X
```
"What do you know about [entity name]?"
```

### Update a Preference
```
"Actually, I prefer [X] instead of [Y]"
```

### Record a Decision
```
"We've decided to [decision] because [reason]"
```

---

## Autonomy Levels

| Level | What Claude Can Do |
|-------|-------------------|
| **0 (Current)** | Advise only, you execute |
| **1** | Propose actions, you confirm |
| **2** | Act on pre-approved tasks |
| **3** | Act, exceptions only |
| **4** | Full partner collaboration |

We're starting at Level 0, building trust through successful interactions.

---

## Troubleshooting

**"Claude isn't remembering things"**
- Check `CLAUDE.memory.md` exists at repo root
- Verify Supabase schema is deployed
- Try explicit: "Remember that..."

**"Wrong context in responses"**
- Be explicit about what you mean
- Check entity names are consistent
- Review recent captures in memory file

**"Preferences not working"**
- State preferences explicitly
- Use clear language: "I prefer X" not "maybe X would be nice"
- Corrections are captured more reliably than hints

---

## Files You Care About

| File | Purpose |
|------|---------|
| `CLAUDE.memory.md` | Session state (edit to customize) |
| `SKILL.md` | How Claude uses the system |
| `schemas/supabase-schema.sql` | Database setup |
| `docs/ARCHITECTURE.md` | Deep dive into system design |
| `docs/VISION.md` | Where we're headed (R2-D2 vision) |

---

## Next Steps

1. **Use normally** - Claude captures automatically
2. **Be explicit** - Clear feedback helps learning
3. **Check periodically** - Review what's being captured
4. **Trust builds** - Autonomy expands with successful interactions

---

*Questions? Check `docs/ARCHITECTURE.md` or ask Claude directly.*
