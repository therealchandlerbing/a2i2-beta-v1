# A2I2 Platform Setup Guide

**Step 0-1: Foundation Setup for Getting Started**

This guide covers everything needed to bring the A2I2 (Arcus Intelligence) platform to life. Follow these steps in order for the smoothest setup experience.

---

## Table of Contents

1. [Prerequisites Checklist](#1-prerequisites-checklist)
2. [Phase 1: Database Setup (Supabase or Neon)](#2-phase-1-database-setup)
3. [Phase 2: Environment Variables](#3-phase-2-environment-variables)
4. [Phase 3: Session Memory Initialization](#4-phase-3-session-memory-initialization)
5. [Phase 4: Vercel Deployment (Optional)](#5-phase-4-vercel-deployment)
6. [Phase 5: Voice Integration (Optional)](#6-phase-5-voice-integration)
7. [Verification Checklist](#7-verification-checklist)
8. [Troubleshooting](#8-troubleshooting)
9. [Cost Estimates](#9-cost-estimates)

---

## 1. Prerequisites Checklist

### Required Accounts

| Service | Purpose | Sign Up URL | Free Tier |
|---------|---------|-------------|-----------|
| **Supabase** OR **Neon** | PostgreSQL database with pgvector | [supabase.com](https://supabase.com) / [neon.tech](https://neon.tech) | Yes |
| **Anthropic** | Claude API access | [console.anthropic.com](https://console.anthropic.com) | No (pay-per-use) |
| **Google AI Studio** | Gemini API access | [aistudio.google.com](https://aistudio.google.com) | Yes (limited) |
| **Vercel** (optional) | Web hosting | [vercel.com](https://vercel.com) | Yes |
| **OpenAI** (optional) | Embeddings & voice | [platform.openai.com](https://platform.openai.com) | No (pay-per-use) |

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Node.js** | 18.x | 20.x LTS |
| **Python** | 3.11+ | 3.12 |
| **Git** | 2.x | Latest |
| **PostgreSQL Client** | psql or GUI | TablePlus, pgAdmin, or Supabase Studio |

### API Keys to Obtain

Before starting, gather these API keys:

1. **ANTHROPIC_API_KEY** - From [Anthropic Console](https://console.anthropic.com/account/keys)
2. **GEMINI_API_KEY** - From [Google AI Studio](https://aistudio.google.com/apikey)
3. **Database credentials** - From Supabase or Neon dashboard
4. **OPENAI_API_KEY** (optional) - From [OpenAI Platform](https://platform.openai.com/api-keys)

---

## 2. Phase 1: Database Setup

Choose **ONE** database provider: Supabase (simpler) or Neon (recommended for Vercel).

### Option A: Supabase Setup (Recommended for Quick Start)

#### Step 1.1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click **"New Project"**
3. Configure:
   - **Name**: `a2i2-production` (or your preferred name)
   - **Database Password**: Generate and save securely
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Free tier works for development
4. Wait for project initialization (~2 minutes)

#### Step 1.2: Enable Required Extensions

1. Go to **Database** → **Extensions** in Supabase dashboard
2. Search and enable:
   - `uuid-ossp` (for UUID generation)
   - `vector` (for pgvector semantic search)

Or run in SQL Editor:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
```

#### Step 1.3: Run Database Schema

1. Go to **SQL Editor** in Supabase dashboard
2. Open the schema file: `.claude/skills/knowledge-repository/schemas/supabase-schema.sql`
3. Copy the entire contents (~2,400 lines)
4. Paste into SQL Editor and click **"Run"**

This creates:
- 30+ tables for memory, entities, skills, and trust tracking
- 80+ indexes for performance optimization
- Row-level security policies
- Stored functions and triggers
- Seed data for initial configuration

#### Step 1.4: Get Connection Details

From **Project Settings** → **API**:
- Copy **Project URL** → `SUPABASE_URL`
- Copy **anon public key** → `SUPABASE_ANON_KEY`
- Copy **service_role key** → `SUPABASE_SERVICE_ROLE_KEY` (for server-side only)

---

### Option B: Neon Setup (Recommended for Vercel Deployment)

#### Step 1.1: Create Neon Project

1. Go to [neon.tech](https://neon.tech) and sign in
2. Click **"Create Project"**
3. Configure:
   - **Project name**: `a2i2-production`
   - **PostgreSQL version**: 16 (latest)
   - **Region**: Choose closest to your users
   - **Compute size**: 0.25 CU (auto-scales)
4. Project creates instantly

#### Step 1.2: Enable Extensions

Go to **SQL Editor** and run:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
```

#### Step 1.3: Run Database Schema

1. In Neon **SQL Editor**
2. Copy contents of `.claude/skills/knowledge-repository/schemas/supabase-schema.sql`
3. Execute the schema

**Important for Neon**: After running the schema, disable RLS for app-level auth:
```sql
ALTER TABLE arcus_episodic_memory DISABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_semantic_memory DISABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_procedural_memory DISABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_entities DISABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_relationships DISABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_session_state DISABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_autonomy_audit DISABLE ROW LEVEL SECURITY;
```

#### Step 1.4: Get Connection Strings

From Neon **Dashboard** → **Connection Details**:
- Copy **Pooled connection string** → `DATABASE_URL`
- Copy **Direct connection string** → `DATABASE_URL_DIRECT` (for migrations)

Format:
```
postgres://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require
```

---

### Verify Database Setup

Run this query to verify tables were created:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name LIKE 'arcus_%'
ORDER BY table_name;
```

Expected: ~30 tables starting with `arcus_`

---

## 3. Phase 2: Environment Variables

### Step 2.1: Create Local Environment File

Create `.env.local` in the repository root (this file is git-ignored):

```bash
# Copy the example file
cp .env.example .env.local

# Or create manually:
touch .env.local
```

### Step 2.2: Configure Required Variables

Add to `.env.local`:

```bash
# ===========================================
# REQUIRED: Database (Choose ONE set)
# ===========================================

# Option A: Supabase
SUPABASE_URL="https://xxxxx.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIs..."
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIs..."

# Option B: Neon (for Vercel deployment)
DATABASE_URL="postgres://user:pass@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require"
DATABASE_URL_DIRECT="postgres://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"

# ===========================================
# REQUIRED: AI Model APIs
# ===========================================

# Anthropic Claude (Primary LLM)
ANTHROPIC_API_KEY="sk-ant-api03-..."

# Google Gemini (Multi-modal, large context)
GEMINI_API_KEY="AIzaSy..."

# ===========================================
# OPTIONAL: Enhanced Features
# ===========================================

# OpenAI (for embeddings and voice)
OPENAI_API_KEY="sk-proj-..."

# Gemini Model Configuration
GEMINI_DEFAULT_MODEL="gemini-3-flash-preview"
GEMINI_THINKING_LEVEL="high"
GEMINI_TEMPERATURE="1.0"

# ===========================================
# OPTIONAL: Voice Integration (Phase 3+)
# ===========================================

# Voice Mode: "cloud" or "local"
VOICE_MODE="cloud"
VOICE_STT_SERVICE="openai"
VOICE_TTS_SERVICE="openai"
VOICE_TTS_VOICE="nova"

# ElevenLabs (premium voice)
ELEVENLABS_API_KEY="..."

# ===========================================
# PRODUCTION ONLY: API Security
# ===========================================

# Generate with: openssl rand -base64 32
API_SECRET_KEY="your-secure-random-key"
```

### Step 2.3: Configure for Vercel (if deploying)

In **Vercel Dashboard** → **Settings** → **Environment Variables**, add:

| Variable | Environments | Sensitive |
|----------|--------------|-----------|
| `DATABASE_URL` | Production, Preview, Development | Yes |
| `ANTHROPIC_API_KEY` | Production | Yes |
| `GEMINI_API_KEY` | Production | Yes |
| `OPENAI_API_KEY` | Production | Yes |
| `API_SECRET_KEY` | Production | Yes |

---

## 4. Phase 3: Session Memory Initialization

### Step 3.1: Create CLAUDE.memory.md

This file persists session state between Claude interactions:

```bash
# Copy the template
cp .claude/skills/knowledge-repository/config/memory-template.md CLAUDE.memory.md
```

### Step 3.2: Customize Initial Preferences

Edit `CLAUDE.memory.md` and update:

```markdown
# CLAUDE.memory.md

## User Preferences
- **Communication Style**: [concise/detailed/technical]
- **Code Style**: [typescript_preferred/python_preferred]
- **Documentation**: [only_when_requested/always/minimal]

## Organization Context
- **Company**: [Your Organization Name]
- **Industry**: [Your Industry]
- **Team Size**: [Small/Medium/Large]

## Active Projects
- [List your current projects]

## Technology Stack
- [List your primary technologies]
```

### Step 3.3: Verify Session Setup

Test by asking Claude:
> "What do you remember about my preferences?"

If working correctly, Claude should reference your configured preferences.

---

## 5. Phase 4: Vercel Deployment (Optional)

This phase sets up the web interface. Skip if using CLI-only.

### Step 4.1: Initialize Next.js Project

```bash
# Create Next.js app in the existing repo
npx create-next-app@latest app --typescript --tailwind --eslint --app --src-dir --no-import-alias

# Or initialize manually in existing structure
cd /home/user/a2i2-beta-v1
mkdir -p src/app src/lib src/components
```

### Step 4.2: Install Dependencies

```bash
npm install @neondatabase/serverless zod
npm install @clerk/nextjs  # For authentication (optional)
npm install ai @anthropic-ai/sdk  # For AI features (optional)
```

### Step 4.3: Create Database Client

Create `src/lib/db.ts`:
```typescript
import { neon } from '@neondatabase/serverless';

export const sql = neon(process.env.DATABASE_URL!);
```

### Step 4.4: Create API Routes

See `/docs/VERCEL-NEON-INTEGRATION.md` for complete API route implementations:
- `/api/learn` - Store new knowledge
- `/api/recall` - Retrieve memories
- `/api/relate` - Create entity relationships
- `/api/reflect` - Synthesize patterns
- `/api/health` - Database health check

### Step 4.5: Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy (first time)
vercel

# Deploy to production
vercel --prod
```

---

## 6. Phase 5: Voice Integration (Optional)

Voice features require additional setup. Choose one option:

### Option A: Cloud Voice (OpenAI - Recommended)

1. Ensure `OPENAI_API_KEY` is set
2. Configure in `.env.local`:
```bash
VOICE_MODE="cloud"
VOICE_STT_SERVICE="openai"
VOICE_TTS_SERVICE="openai"
VOICE_TTS_VOICE="nova"
```

### Option B: Local Voice (Free, Offline)

1. Install local dependencies:
```bash
pip install whisper-cpp-python kokoro-onnx
```

2. Configure in `.env.local`:
```bash
VOICE_MODE="local"
VOICE_STT_SERVICE="whisper"
VOICE_TTS_SERVICE="kokoro"
WHISPER_MODEL="base.en"
```

### Option C: Premium Voice (ElevenLabs)

1. Get API key from [ElevenLabs](https://elevenlabs.io)
2. Configure:
```bash
ELEVENLABS_API_KEY="your-key"
```

See `.claude/skills/knowledge-repository/docs/VOICE-ARCHITECTURE.md` for full voice setup.

---

## 7. Verification Checklist

### Database Verification

```sql
-- Count tables (should be ~30+)
SELECT COUNT(*) as table_count
FROM information_schema.tables
WHERE table_schema = 'public' AND table_name LIKE 'arcus_%';

-- Verify extensions
SELECT extname, extversion FROM pg_extension
WHERE extname IN ('uuid-ossp', 'vector');

-- Check seed data
SELECT COUNT(*) FROM arcus_skills;  -- Should be 3
SELECT COUNT(*) FROM arcus_user_preference_vectors;  -- Should be 1
SELECT COUNT(*) FROM arcus_autonomy_state;  -- Should be 1

-- Verify indexes (should be 80+)
SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';
```

### Environment Verification

```bash
# Test database connection (Neon)
psql "$DATABASE_URL" -c "SELECT 1;"

# Test API keys are set
echo "Anthropic: ${ANTHROPIC_API_KEY:0:10}..."
echo "Gemini: ${GEMINI_API_KEY:0:10}..."
```

### Session Memory Verification

1. Start a Claude session
2. Ask: "What are my communication preferences?"
3. Claude should reference `CLAUDE.memory.md` contents

### API Route Verification (if deployed)

```bash
# Health check
curl https://your-app.vercel.app/api/health

# Test recall (with auth header)
curl -H "Authorization: Bearer $API_SECRET_KEY" \
  https://your-app.vercel.app/api/recall?query=test
```

---

## 8. Troubleshooting

### Database Issues

| Problem | Solution |
|---------|----------|
| "vector extension not found" | Enable pgvector in dashboard or run `CREATE EXTENSION vector;` |
| "relation does not exist" | Re-run the schema SQL file |
| Connection timeout | Check firewall/network, verify connection string |
| RLS blocking queries | Disable RLS for development (see Phase 1) |

### API Key Issues

| Problem | Solution |
|---------|----------|
| "Invalid API key" | Verify key copied correctly, no extra spaces |
| Rate limiting | Implement backoff, upgrade plan |
| Key not recognized | Check environment variable name matches exactly |

### Memory Issues

| Problem | Solution |
|---------|----------|
| Preferences not loading | Verify `CLAUDE.memory.md` exists at repo root |
| Changes not persisting | Check Supabase connection, verify schema deployed |
| Wrong context retrieved | Entity names may be inconsistent, check confidence scores |

### Deployment Issues

| Problem | Solution |
|---------|----------|
| Build fails | Check `npm run build` locally first |
| Environment variables missing | Verify set in Vercel dashboard |
| 500 errors | Check Vercel function logs |

---

## 9. Cost Estimates

### Monthly Costs by Usage Level

| Component | Light Usage | Moderate | Heavy |
|-----------|-------------|----------|-------|
| **Database (Neon/Supabase)** | $0 (free tier) | $25 | $100+ |
| **Claude API** | $5-20 | $50-100 | $200+ |
| **Gemini API** | $0-5 (free tier) | $20-50 | $100+ |
| **OpenAI (embeddings)** | $1-5 | $10-20 | $50+ |
| **Vercel Hosting** | $0 (hobby) | $20 | $20+ |
| **Voice (ElevenLabs)** | $0-5 | $22 | $99+ |
| **Total** | **$6-35** | **$147-217** | **$569+** |

### Free Tier Limits

| Service | Free Limit |
|---------|-----------|
| Supabase | 500MB database, 1GB storage |
| Neon | 0.5GB storage, auto-scaling |
| Gemini | 1,500 requests/day (Flash) |
| Vercel | 100GB bandwidth, hobby plan |

---

## Quick Reference

### Essential Commands

```bash
# Clone and enter repo
git clone https://github.com/therealchandlerbing/a2i2-beta-v1.git
cd a2i2-beta-v1

# Set up environment
cp .env.example .env.local
# Edit .env.local with your API keys

# Initialize session memory
cp .claude/skills/knowledge-repository/config/memory-template.md CLAUDE.memory.md

# For web deployment
npm install
npm run dev  # Local development
vercel --prod  # Production deploy
```

### Key File Locations

| Purpose | Location |
|---------|----------|
| Database Schema | `.claude/skills/knowledge-repository/schemas/supabase-schema.sql` |
| Configuration Files | `.claude/skills/knowledge-repository/config/` |
| Session Memory | `CLAUDE.memory.md` (repo root) |
| Skill Instructions | `.claude/skills/knowledge-repository/SKILL.md` |
| Architecture Docs | `.claude/skills/knowledge-repository/docs/ARCHITECTURE.md` |
| Vercel Guide | `docs/VERCEL-NEON-INTEGRATION.md` |

### Support Resources

- **Repository**: https://github.com/therealchandlerbing/a2i2-beta-v1
- **Documentation Index**: `.claude/skills/knowledge-repository/INDEX.md`
- **Quick Start**: `.claude/skills/knowledge-repository/QUICK-START.md`

---

**Last Updated**: 2026-01-27
**Version**: 1.0.0-beta
