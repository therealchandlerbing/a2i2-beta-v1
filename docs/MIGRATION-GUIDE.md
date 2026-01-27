# A2I2 Migration & Upgrade Guide

This guide covers upgrading between A2I2 versions and migrating data between environments.

---

## Table of Contents

1. [Version History](#version-history)
2. [Upgrading Between Versions](#upgrading-between-versions)
3. [Database Migrations](#database-migrations)
4. [Environment Migration](#environment-migration)
5. [Breaking Changes](#breaking-changes)
6. [Rollback Procedures](#rollback-procedures)

---

## Version History

| Version | Release Date | Key Changes |
|---------|--------------|-------------|
| **1.4.0** | 2026-01-25 | Voice architecture, NanoWakeWord integration |
| **1.3.0** | 2026-01-20 | Gemini 3 integration, Deep Research agent |
| **1.2.0** | 2026-01-15 | Digital twin modeling, reward signals |
| **1.1.0** | 2026-01-10 | Skill orchestration, context budgeting |
| **1.0.0** | 2026-01-05 | Initial release: Core memory operations |

---

## Upgrading Between Versions

### General Upgrade Process

1. **Backup your data**
   ```bash
   # Export current database
   pg_dump "$DATABASE_URL" > backup_$(date +%Y%m%d).sql

   # Backup session memory
   cp CLAUDE.memory.md CLAUDE.memory.md.backup
   ```

2. **Pull latest changes**
   ```bash
   git fetch origin main
   git checkout main
   git pull origin main
   ```

3. **Run database migrations** (if any)
   ```bash
   # Check for new migration files
   ls -la .claude/skills/knowledge-repository/schemas/migrations/

   # Run migrations in order
   psql "$DATABASE_URL" < migrations/001_xxx.sql
   ```

4. **Update dependencies**
   ```bash
   # Node.js dependencies
   npm install

   # Python dependencies
   pip install -r requirements.txt
   ```

5. **Verify upgrade**
   ```bash
   # Run health check
   curl https://your-app.vercel.app/api/health
   ```

---

### Version-Specific Upgrades

#### 1.3.x → 1.4.x (Voice Architecture)

**New tables added:**
```sql
-- Run if upgrading from 1.3.x
CREATE TABLE IF NOT EXISTS arcus_voice_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL DEFAULT 'default',
    query_text TEXT NOT NULL,
    session_id TEXT,
    audio_duration_ms INTEGER,
    speech_confidence FLOAT DEFAULT 1.0,
    first_chunk_latency_ms INTEGER,
    total_latency_ms INTEGER,
    provider_used TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS arcus_proactive_preparations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL DEFAULT 'default',
    trigger_context TEXT NOT NULL,
    prepared_response TEXT NOT NULL,
    confidence DECIMAL(3,2) DEFAULT 0.5,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);
```

**New environment variables:**
```bash
# Add to .env.local
VOICE_MODE="cloud"
VOICE_STT_SERVICE="openai"
VOICE_TTS_SERVICE="openai"
```

**Configuration changes:**
- New file: `config/mcp-voice-config.json`
- Updated: `config/hooks-config.json` (voice triggers added)

---

#### 1.2.x → 1.3.x (Gemini Integration)

**New tables added:**
```sql
-- Run if upgrading from 1.2.x
CREATE TABLE IF NOT EXISTS arcus_model_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_context TEXT NOT NULL,
    model_used TEXT NOT NULL,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_latency_ms DECIMAL(10,2),
    avg_cost DECIMAL(10,6),
    last_used TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(task_context, model_used)
);
```

**New environment variables:**
```bash
# Add to .env.local
GEMINI_API_KEY="your-key"
GEMINI_DEFAULT_MODEL="gemini-3-flash-preview"
GEMINI_THINKING_LEVEL="high"
```

**Configuration changes:**
- New file: `config/gemini-config.json`

---

#### 1.1.x → 1.2.x (Digital Twin)

**New tables added:**
```sql
-- Run if upgrading from 1.1.x
CREATE TABLE IF NOT EXISTS arcus_cognitive_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT UNIQUE NOT NULL DEFAULT 'default',
    cognitive_styles JSONB DEFAULT '{}',
    decision_weights JSONB DEFAULT '{}',
    communication_style TEXT DEFAULT 'direct',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS arcus_decision_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL DEFAULT 'default',
    decision_type TEXT NOT NULL,
    factors JSONB NOT NULL,
    outcome TEXT,
    confidence DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS arcus_reward_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_id UUID,
    signal_type TEXT NOT NULL,
    signal_value DECIMAL(5,4) NOT NULL,
    context JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

#### 1.0.x → 1.1.x (Skill Orchestration)

**New tables added:**
```sql
-- Run if upgrading from 1.0.x
CREATE TABLE IF NOT EXISTS arcus_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    capabilities TEXT[] DEFAULT '{}',
    version TEXT DEFAULT '1.0.0',
    enabled BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS arcus_skill_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_id UUID REFERENCES arcus_skills(id),
    input_summary TEXT,
    output_summary TEXT,
    success BOOLEAN,
    latency_ms INTEGER,
    tokens_used INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS arcus_orchestration_runs (
    plan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    goal TEXT NOT NULL,
    skills_planned TEXT[] DEFAULT '{}',
    skills_executed TEXT[] DEFAULT '{}',
    status TEXT DEFAULT 'pending',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS arcus_context_budget_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    orchestration_id UUID REFERENCES arcus_orchestration_runs(plan_id),
    model TEXT NOT NULL,
    allocated_tokens INTEGER,
    used_tokens INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Database Migrations

### UUID Generation Note

The A2I2 schema uses `uuid_generate_v4()` from the `uuid-ossp` extension. This extension is enabled automatically in the base schema:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

**Alternative for PostgreSQL 13+:** You can also use `gen_random_uuid()` which is built into PostgreSQL core and doesn't require the extension. Both produce cryptographically random UUIDs and are functionally equivalent.

### Creating a Migration

When making schema changes:

1. Create migration file:
   ```bash
   # From repo root
   touch .claude/skills/knowledge-repository/schemas/migrations/$(date +%Y%m%d)_description.sql
   ```

2. Write migration with rollback:
   ```sql
   -- Migration: 20260127_add_voice_tables.sql
   -- Up
   BEGIN;

   CREATE TABLE IF NOT EXISTS arcus_voice_queries (...);

   COMMIT;

   -- Down (save separately for rollback)
   -- DROP TABLE IF EXISTS arcus_voice_queries;
   ```

3. Test migration:
   ```bash
   # Test on dev database first (from repo root)
   psql "$DEV_DATABASE_URL" < .claude/skills/knowledge-repository/schemas/migrations/20260127_add_voice_tables.sql
   ```

### Running Migrations

```bash
# Migration files are located at: .claude/skills/knowledge-repository/schemas/migrations/

# List pending migrations (from repo root)
ls .claude/skills/knowledge-repository/schemas/migrations/*.sql | sort

# Run specific migration
psql "$DATABASE_URL" < .claude/skills/knowledge-repository/schemas/migrations/20260127_add_voice_tables.sql

# Run all migrations in order
for f in .claude/skills/knowledge-repository/schemas/migrations/*.sql; do
    echo "Running $f..."
    psql "$DATABASE_URL" < "$f"
done
```

---

## Environment Migration

### Supabase → Neon Migration

1. **Export from Supabase**
   ```bash
   # Get connection string from Supabase dashboard
   pg_dump "postgres://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres" \
     --no-owner --no-acl > supabase_export.sql
   ```

2. **Prepare for Neon**
   ```bash
   # Remove Supabase-specific extensions/roles if any
   sed -i '/GRANT.*supabase/d' supabase_export.sql
   sed -i '/CREATE ROLE.*supabase/d' supabase_export.sql
   ```

3. **Import to Neon**
   ```bash
   # Enable extensions first
   psql "$NEON_DATABASE_URL" -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
   psql "$NEON_DATABASE_URL" -c "CREATE EXTENSION IF NOT EXISTS \"vector\";"

   # Import data
   psql "$NEON_DATABASE_URL" < supabase_export.sql
   ```

4. **Update environment variables**
   ```bash
   # Replace in .env.local
   # OLD:
   SUPABASE_URL="..."
   SUPABASE_ANON_KEY="..."

   # NEW:
   DATABASE_URL="postgres://..."
   DATABASE_URL_DIRECT="postgres://..."
   ```

5. **Disable RLS for Neon**
   ```sql
   ALTER TABLE arcus_episodic_memory DISABLE ROW LEVEL SECURITY;
   ALTER TABLE arcus_semantic_memory DISABLE ROW LEVEL SECURITY;
   ALTER TABLE arcus_procedural_memory DISABLE ROW LEVEL SECURITY;
   ALTER TABLE arcus_entities DISABLE ROW LEVEL SECURITY;
   ALTER TABLE arcus_relationships DISABLE ROW LEVEL SECURITY;
   ALTER TABLE arcus_session_state DISABLE ROW LEVEL SECURITY;
   ALTER TABLE arcus_autonomy_audit DISABLE ROW LEVEL SECURITY;
   ```

### Development → Production Migration

1. **Export development data**
   ```bash
   pg_dump "$DEV_DATABASE_URL" \
     --data-only \
     --exclude-table=arcus_session_state \
     > dev_data.sql
   ```

2. **Review and sanitize**
   - Remove test data
   - Check for sensitive information
   - Verify confidence scores

3. **Import to production**
   ```bash
   # Ensure schema exists
   psql "$PROD_DATABASE_URL" < schemas/supabase-schema.sql

   # Import data
   psql "$PROD_DATABASE_URL" < dev_data.sql
   ```

---

## Breaking Changes

### v1.4.0 Breaking Changes
- None (additive only)

### v1.3.0 Breaking Changes
- `model_router.py` API changed: `select_model()` now requires `task_context` parameter
- Gemini config required for multi-model routing

### v1.2.0 Breaking Changes
- `arcus_procedural_memory.workflow_steps` changed from TEXT to JSONB
- Migration required:
  ```sql
  ALTER TABLE arcus_procedural_memory
  ALTER COLUMN workflow_steps TYPE JSONB USING workflow_steps::JSONB;
  ```

### v1.1.0 Breaking Changes
- None (additive only)

### v1.0.0
- Initial release

---

## Rollback Procedures

### Quick Rollback

```bash
# 1. Stop the application
vercel rm your-app --yes

# 2. Restore database
psql "$DATABASE_URL" < backup_YYYYMMDD.sql

# 3. Restore code
git checkout v1.x.x  # Previous version tag

# 4. Restore session memory
cp CLAUDE.memory.md.backup CLAUDE.memory.md

# 5. Redeploy
vercel --prod
```

### Partial Rollback (Schema Only)

```bash
# Drop new tables only
psql "$DATABASE_URL" << 'EOF'
DROP TABLE IF EXISTS arcus_voice_queries CASCADE;
DROP TABLE IF EXISTS arcus_proactive_preparations CASCADE;
-- Add other new tables as needed
EOF
```

### Data Rollback

```bash
# Restore specific tables
pg_restore -d "$DATABASE_URL" \
  --data-only \
  --table=arcus_episodic_memory \
  backup_YYYYMMDD.dump
```

---

## Pre-Upgrade Checklist

- [ ] Database backed up (`pg_dump`)
- [ ] `CLAUDE.memory.md` backed up
- [ ] Current version noted
- [ ] Changelog reviewed for breaking changes
- [ ] Test environment upgraded first
- [ ] Rollback plan documented
- [ ] Team notified of maintenance window

## Post-Upgrade Checklist

- [ ] Health check passes
- [ ] Database tables verified
- [ ] API routes responding
- [ ] Session memory loads correctly
- [ ] Smoke test completed
- [ ] Monitoring alerts checked
- [ ] Backup verified

---

**Last Updated**: 2026-01-27
