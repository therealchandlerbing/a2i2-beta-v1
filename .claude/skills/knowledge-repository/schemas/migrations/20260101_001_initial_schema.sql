-- Migration: 20260101_001_initial_schema
-- Description: Base A2I2 schema (v1.0.0) - reference only, applied via supabase-schema.sql
-- Author: A2I2 Team
-- Date: 2026-01-01
-- Note: This migration documents the initial schema version. New installations
--       should run supabase-schema.sql directly. This file is for tracking purposes.

-- ============================================
-- INITIAL SCHEMA TABLES (v1.0.0)
-- ============================================

-- Core Memory Tables:
--   - arcus_episodic_memory: Events and interactions
--   - arcus_semantic_memory: Facts and knowledge
--   - arcus_procedural_memory: Workflows and preferences
--   - arcus_session_state: Working memory

-- Knowledge Graph:
--   - arcus_entities: Graph nodes (people, orgs, projects)
--   - arcus_relationships: Graph edges (connections)

-- Autonomy & Trust:
--   - arcus_autonomy_state: Current trust level
--   - arcus_autonomy_audit: Action audit trail
--   - arcus_trust_delegations: Delegated permissions

-- Skills & Learning:
--   - arcus_skills: Available skills
--   - arcus_skill_executions: Execution history
--   - arcus_digital_twin_profiles: User modeling

-- User Preferences:
--   - arcus_user_preferences: Key-value preferences
--   - arcus_user_preference_vectors: Category-based preferences

-- Voice (Phase 3+):
--   - arcus_voice_sessions: Voice session tracking
--   - arcus_wake_word_events: Wake word detections

-- System:
--   - arcus_schema_migrations: Migration tracking

-- ============================================
-- Record migration
-- ============================================

-- Only run this if migrating from an existing installation
-- New installations get this via supabase-schema.sql
INSERT INTO arcus_schema_migrations (version, description, applied_by)
VALUES ('20260101_001', 'initial_schema', current_user)
ON CONFLICT (version) DO NOTHING;
