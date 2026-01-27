# Database Migrations

This directory contains SQL migration files for updating the A2I2 database schema.

## Migration Naming Convention

```
YYYYMMDD_NNN_description.sql
```

- `YYYYMMDD` - Date of creation (e.g., 20260127)
- `NNN` - Sequential number for the day (001, 002, etc.)
- `description` - Brief description using underscores (e.g., `add_voice_sessions`)

## Example Migration Files

```
20260101_001_initial_schema.sql
20260115_001_add_embedding_indexes.sql
20260120_001_add_voice_session_tables.sql
20260120_002_add_wake_word_config.sql
```

## Running Migrations

### Supabase

1. Navigate to **SQL Editor** in Supabase Dashboard
2. Copy and paste migration file contents
3. Click **Run**

Or use the CLI:
```bash
supabase db push --linked
```

### Neon

Using psql (run from repo root):
```bash
psql "$DATABASE_URL_DIRECT" -f .claude/skills/knowledge-repository/schemas/migrations/YYYYMMDD_NNN_description.sql
```

Or from within the migrations directory:
```bash
cd .claude/skills/knowledge-repository/schemas/migrations
psql "$DATABASE_URL_DIRECT" -f YYYYMMDD_NNN_description.sql
```

Or use Neon Dashboard SQL Editor.

## Migration Best Practices

1. **Always test migrations on development first**
2. **Include rollback statements** in comments when possible
3. **Use `IF NOT EXISTS`** for CREATE statements
4. **Use `IF EXISTS`** for DROP statements
5. **Back up data** before running migrations in production
6. **Run during low-traffic periods**

## Tracking Applied Migrations

A2I2 tracks migrations in the `arcus_schema_migrations` table:

```sql
SELECT * FROM arcus_schema_migrations ORDER BY applied_at DESC;
```

## Creating a New Migration

1. Create a new file following the naming convention
2. Add header comment with description and date
3. Include the migration SQL
4. Add rollback instructions in comments
5. Test on development environment
6. Apply to production

### Template

```sql
-- Migration: YYYYMMDD_NNN_description
-- Description: Brief description of what this migration does
-- Author: Your Name
-- Date: YYYY-MM-DD
-- Rollback: Instructions for reverting (if applicable)

-- ============================================
-- UP Migration
-- ============================================

-- Your migration SQL here

-- ============================================
-- Record migration (do not modify)
-- ============================================

INSERT INTO arcus_schema_migrations (version, description, applied_by)
VALUES ('YYYYMMDD_NNN', 'description', current_user);
```
