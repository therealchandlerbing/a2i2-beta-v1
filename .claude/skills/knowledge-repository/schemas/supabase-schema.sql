-- ============================================================================
-- ARCUS KNOWLEDGE REPOSITORY - SUPABASE SCHEMA
-- ============================================================================
-- Version: 1.0.0
-- Author: Arcus Innovation Studios
-- Created: 2026-01-24
--
-- This schema creates the persistent storage layer for the Arcus Knowledge
-- Repository. It implements the five memory types:
--   1. Episodic Memory (What Happened)
--   2. Semantic Memory (What We Know)
--   3. Procedural Memory (How We Work)
--   4. Knowledge Graph (How Things Connect)
--   5. Working Memory (tracked via session_state)
--
-- Prerequisites:
--   - Supabase project with pgvector extension enabled
--   - Supabase Pro plan recommended for higher limits
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================================
-- EPISODIC MEMORY
-- Stores what happened: conversations, decisions, meetings, outcomes
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_episodic_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Event classification
    event_type TEXT NOT NULL CHECK (event_type IN (
        'conversation',    -- Chat/voice interaction
        'decision',        -- A decision that was made
        'meeting',         -- Scheduled meeting or call
        'milestone',       -- Project milestone reached
        'error',           -- Something went wrong (learning opportunity)
        'success',         -- Something went well (pattern to repeat)
        'feedback',        -- User feedback received
        'correction'       -- User corrected Claude
    )),

    -- Core content
    summary TEXT NOT NULL,
    detailed_content JSONB DEFAULT '{}',

    -- Context
    participants TEXT[] DEFAULT '{}',
    related_entities JSONB DEFAULT '[]',  -- [{type, id, name}]
    related_projects TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',

    -- Outcomes and learnings
    outcome TEXT,
    outcome_type TEXT CHECK (outcome_type IN ('positive', 'negative', 'neutral', 'pending')),
    learnings TEXT[] DEFAULT '{}',

    -- Quality metrics
    confidence FLOAT DEFAULT 0.8 CHECK (confidence >= 0 AND confidence <= 1),
    importance TEXT DEFAULT 'normal' CHECK (importance IN ('low', 'normal', 'high', 'critical')),

    -- Source tracking
    source JSONB NOT NULL DEFAULT '{}',  -- {type, session_id, interaction_id, document_ref}

    -- Timestamps
    event_timestamp TIMESTAMPTZ DEFAULT NOW(),  -- When the event occurred
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Vector embedding for semantic search
    embedding VECTOR(1536),

    -- Additional metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for episodic memory
CREATE INDEX IF NOT EXISTS idx_episodic_event_type ON arcus_episodic_memory(event_type);
CREATE INDEX IF NOT EXISTS idx_episodic_timestamp ON arcus_episodic_memory(event_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_episodic_participants ON arcus_episodic_memory USING GIN(participants);
CREATE INDEX IF NOT EXISTS idx_episodic_projects ON arcus_episodic_memory USING GIN(related_projects);
CREATE INDEX IF NOT EXISTS idx_episodic_tags ON arcus_episodic_memory USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_episodic_importance ON arcus_episodic_memory(importance) WHERE importance IN ('high', 'critical');
CREATE INDEX IF NOT EXISTS idx_episodic_outcome ON arcus_episodic_memory(outcome_type);

COMMENT ON TABLE arcus_episodic_memory IS 'Episodic memory: stores events, conversations, decisions, and outcomes';

-- ============================================================================
-- SEMANTIC MEMORY
-- Stores what we know: facts, patterns, frameworks, domain knowledge
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_semantic_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Knowledge classification
    category TEXT NOT NULL CHECK (category IN (
        'fact',           -- Verified factual information
        'pattern',        -- Observed recurring pattern
        'framework',      -- Mental model or decision framework
        'definition',     -- Term or concept definition
        'best_practice',  -- Recommended approach
        'insight',        -- Synthesized learning
        'preference'      -- User or organizational preference
    )),

    -- Core content
    statement TEXT NOT NULL,
    explanation TEXT,

    -- Evidence and confidence
    evidence TEXT[] DEFAULT '{}',
    evidence_count INT DEFAULT 0,
    confidence FLOAT DEFAULT 0.8 CHECK (confidence >= 0 AND confidence <= 1),

    -- Domain and categorization
    domain TEXT,  -- e.g., 'clients', 'operations', 'finance', 'technology'
    subdomain TEXT,
    related_concepts TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',

    -- Validity
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_until TIMESTAMPTZ,  -- NULL means still valid
    superseded_by UUID REFERENCES arcus_semantic_memory(id),

    -- Source tracking
    source JSONB NOT NULL DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed TIMESTAMPTZ DEFAULT NOW(),
    access_count INT DEFAULT 0,

    -- Vector embedding
    embedding VECTOR(1536),

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for semantic memory
CREATE INDEX IF NOT EXISTS idx_semantic_category ON arcus_semantic_memory(category);
CREATE INDEX IF NOT EXISTS idx_semantic_domain ON arcus_semantic_memory(domain);
CREATE INDEX IF NOT EXISTS idx_semantic_subdomain ON arcus_semantic_memory(domain, subdomain);
CREATE INDEX IF NOT EXISTS idx_semantic_valid ON arcus_semantic_memory(valid_from, valid_until);
CREATE INDEX IF NOT EXISTS idx_semantic_concepts ON arcus_semantic_memory USING GIN(related_concepts);
CREATE INDEX IF NOT EXISTS idx_semantic_tags ON arcus_semantic_memory USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_semantic_confidence ON arcus_semantic_memory(confidence DESC);

COMMENT ON TABLE arcus_semantic_memory IS 'Semantic memory: stores facts, patterns, frameworks, and domain knowledge';

-- ============================================================================
-- PROCEDURAL MEMORY
-- Stores how we work: workflows, preferences, standards, templates
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_procedural_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Procedure classification
    procedure_type TEXT NOT NULL CHECK (procedure_type IN (
        'workflow',        -- Multi-step process
        'preference',      -- User preference
        'standard',        -- Organizational standard
        'template',        -- Reusable template
        'decision_tree',   -- Decision logic
        'shortcut',        -- Quick action pattern
        'automation'       -- Automated trigger
    )),

    -- Core content
    name TEXT NOT NULL,
    description TEXT,

    -- For workflows: steps
    steps JSONB DEFAULT '[]',  -- [{order, action, skill?, conditions?, on_success?, on_failure?}]

    -- For preferences: the preference
    preference_value JSONB,  -- Flexible structure for different preference types
    preference_strength TEXT CHECK (preference_strength IN ('strong', 'moderate', 'weak')),

    -- Trigger conditions
    trigger_conditions TEXT[] DEFAULT '{}',
    trigger_keywords TEXT[] DEFAULT '{}',
    trigger_entities TEXT[] DEFAULT '{}',

    -- Success tracking
    success_criteria TEXT[] DEFAULT '{}',
    usage_count INT DEFAULT 0,
    success_count INT DEFAULT 0,
    failure_count INT DEFAULT 0,
    success_rate FLOAT GENERATED ALWAYS AS (
        CASE WHEN usage_count > 0 THEN success_count::FLOAT / usage_count ELSE 0 END
    ) STORED,

    -- Applicability
    applies_to TEXT[] DEFAULT '{}',  -- ['all', 'chandler', 'eduardo', 'client_work', etc.]
    scope TEXT DEFAULT 'global' CHECK (scope IN ('global', 'project', 'person', 'context')),

    -- Quality
    confidence FLOAT DEFAULT 0.8 CHECK (confidence >= 0 AND confidence <= 1),

    -- Source
    source JSONB NOT NULL DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_used TIMESTAMPTZ,

    -- Vector embedding
    embedding VECTOR(1536),

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for procedural memory
CREATE INDEX IF NOT EXISTS idx_procedural_type ON arcus_procedural_memory(procedure_type);
CREATE INDEX IF NOT EXISTS idx_procedural_name ON arcus_procedural_memory(name);
CREATE INDEX IF NOT EXISTS idx_procedural_last_used ON arcus_procedural_memory(last_used DESC);
CREATE INDEX IF NOT EXISTS idx_procedural_success ON arcus_procedural_memory(success_rate DESC) WHERE usage_count > 5;
CREATE INDEX IF NOT EXISTS idx_procedural_triggers ON arcus_procedural_memory USING GIN(trigger_keywords);
CREATE INDEX IF NOT EXISTS idx_procedural_applies ON arcus_procedural_memory USING GIN(applies_to);
CREATE INDEX IF NOT EXISTS idx_procedural_scope ON arcus_procedural_memory(scope);

COMMENT ON TABLE arcus_procedural_memory IS 'Procedural memory: stores workflows, preferences, standards, and patterns';

-- ============================================================================
-- KNOWLEDGE GRAPH - ENTITIES
-- Stores the nodes in our knowledge graph
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Entity identification
    entity_type TEXT NOT NULL CHECK (entity_type IN (
        'person',
        'organization',
        'project',
        'concept',
        'document',
        'decision',
        'meeting',
        'skill',
        'tool',
        'location'
    )),
    external_id TEXT,  -- ID from external system (Asana, Gmail, etc.)

    -- Core attributes
    name TEXT NOT NULL,
    aliases TEXT[] DEFAULT '{}',
    description TEXT,

    -- Type-specific attributes
    attributes JSONB DEFAULT '{}',

    -- For people
    -- attributes: {title, organization, email, communication_style, timezone}

    -- For organizations
    -- attributes: {type, industry, size, relationship_status, primary_contact}

    -- For projects
    -- attributes: {status, client, start_date, end_date, outcomes}

    -- Observation tracking
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    mention_count INT DEFAULT 1,

    -- Quality
    confidence FLOAT DEFAULT 0.8 CHECK (confidence >= 0 AND confidence <= 1),
    verified BOOLEAN DEFAULT FALSE,

    -- Source
    source JSONB NOT NULL DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Vector embedding (for name + description)
    embedding VECTOR(1536),

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Uniqueness constraint
    UNIQUE(entity_type, external_id),
    UNIQUE(entity_type, name) WHERE external_id IS NULL
);

-- Indexes for entities
CREATE INDEX IF NOT EXISTS idx_entities_type ON arcus_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_name ON arcus_entities(name);
CREATE INDEX IF NOT EXISTS idx_entities_external ON arcus_entities(external_id) WHERE external_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_entities_aliases ON arcus_entities USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_entities_last_seen ON arcus_entities(last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_entities_mentions ON arcus_entities(mention_count DESC);

COMMENT ON TABLE arcus_entities IS 'Knowledge graph nodes: people, organizations, projects, concepts, etc.';

-- ============================================================================
-- KNOWLEDGE GRAPH - RELATIONSHIPS
-- Stores the edges in our knowledge graph
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Source entity
    source_entity_id UUID NOT NULL REFERENCES arcus_entities(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,
    source_name TEXT NOT NULL,

    -- Relationship
    relationship TEXT NOT NULL CHECK (relationship IN (
        -- Professional relationships
        'works_at', 'worked_at', 'manages', 'reports_to', 'collaborates_with',
        'hired', 'fired', 'promoted', 'mentors', 'mentored_by',

        -- Business relationships
        'partner_of', 'client_of', 'vendor_of', 'competitor_of',
        'invested_in', 'acquired', 'merged_with',

        -- Project relationships
        'owns', 'leads', 'contributes_to', 'created', 'modified',
        'approved', 'rejected', 'reviewed',

        -- Knowledge relationships
        'related_to', 'part_of', 'contains', 'depends_on', 'blocks',
        'derived_from', 'supersedes', 'conflicts_with',

        -- Social relationships
        'knows', 'introduced', 'referred', 'trusts', 'distrusts',

        -- Event relationships
        'participated_in', 'organized', 'attended', 'spoke_at',
        'decided_on', 'influenced', 'caused', 'prevented'
    )),
    relationship_category TEXT GENERATED ALWAYS AS (
        CASE
            WHEN relationship IN ('works_at', 'worked_at', 'manages', 'reports_to', 'collaborates_with', 'hired', 'fired', 'promoted', 'mentors', 'mentored_by') THEN 'professional'
            WHEN relationship IN ('partner_of', 'client_of', 'vendor_of', 'competitor_of', 'invested_in', 'acquired', 'merged_with') THEN 'business'
            WHEN relationship IN ('owns', 'leads', 'contributes_to', 'created', 'modified', 'approved', 'rejected', 'reviewed') THEN 'project'
            WHEN relationship IN ('related_to', 'part_of', 'contains', 'depends_on', 'blocks', 'derived_from', 'supersedes', 'conflicts_with') THEN 'knowledge'
            WHEN relationship IN ('knows', 'introduced', 'referred', 'trusts', 'distrusts') THEN 'social'
            WHEN relationship IN ('participated_in', 'organized', 'attended', 'spoke_at', 'decided_on', 'influenced', 'caused', 'prevented') THEN 'event'
            ELSE 'other'
        END
    ) STORED,

    -- Target entity
    target_entity_id UUID NOT NULL REFERENCES arcus_entities(id) ON DELETE CASCADE,
    target_type TEXT NOT NULL,
    target_name TEXT NOT NULL,

    -- Relationship properties
    properties JSONB DEFAULT '{}',
    -- Common properties:
    -- {start_date, end_date, strength, notes, context}

    -- Directionality
    bidirectional BOOLEAN DEFAULT FALSE,

    -- Quality
    confidence FLOAT DEFAULT 0.8 CHECK (confidence >= 0 AND confidence <= 1),
    evidence_count INT DEFAULT 1,

    -- Observation tracking
    first_observed TIMESTAMPTZ DEFAULT NOW(),
    last_observed TIMESTAMPTZ DEFAULT NOW(),
    observation_count INT DEFAULT 1,

    -- Source
    source JSONB NOT NULL DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Prevent duplicate relationships
    UNIQUE(source_entity_id, relationship, target_entity_id)
);

-- Indexes for relationships
CREATE INDEX IF NOT EXISTS idx_rel_source ON arcus_relationships(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_rel_target ON arcus_relationships(target_entity_id);
CREATE INDEX IF NOT EXISTS idx_rel_relationship ON arcus_relationships(relationship);
CREATE INDEX IF NOT EXISTS idx_rel_category ON arcus_relationships(relationship_category);
CREATE INDEX IF NOT EXISTS idx_rel_source_type ON arcus_relationships(source_type, source_entity_id);
CREATE INDEX IF NOT EXISTS idx_rel_target_type ON arcus_relationships(target_type, target_entity_id);
CREATE INDEX IF NOT EXISTS idx_rel_last_observed ON arcus_relationships(last_observed DESC);
CREATE INDEX IF NOT EXISTS idx_rel_confidence ON arcus_relationships(confidence DESC);

COMMENT ON TABLE arcus_relationships IS 'Knowledge graph edges: relationships between entities';

-- ============================================================================
-- SESSION STATE
-- Tracks active sessions and working memory
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_session_state (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Session identification
    session_id TEXT UNIQUE NOT NULL,
    user_id TEXT,  -- If multi-user support needed

    -- Preferences loaded for this session
    user_preferences JSONB DEFAULT '{}',

    -- Active context
    active_projects JSONB DEFAULT '[]',
    active_entities JSONB DEFAULT '[]',
    recent_topics TEXT[] DEFAULT '{}',

    -- Learnings captured this session (to sync later)
    pending_learnings JSONB DEFAULT '[]',

    -- Actions taken this session
    actions_log JSONB DEFAULT '[]',

    -- Working memory state
    working_memory JSONB DEFAULT '{}',

    -- Session metrics
    interaction_count INT DEFAULT 0,
    tool_use_count INT DEFAULT 0,
    learning_capture_count INT DEFAULT 0,

    -- Timestamps
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,

    -- Status
    sync_status TEXT DEFAULT 'active' CHECK (sync_status IN (
        'active',     -- Session in progress
        'syncing',    -- Syncing learnings to persistent storage
        'synced',     -- All learnings synced
        'archived'    -- Session archived
    )),

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for session state
CREATE INDEX IF NOT EXISTS idx_session_active ON arcus_session_state(session_id) WHERE sync_status = 'active';
CREATE INDEX IF NOT EXISTS idx_session_user ON arcus_session_state(user_id);
CREATE INDEX IF NOT EXISTS idx_session_started ON arcus_session_state(started_at DESC);

COMMENT ON TABLE arcus_session_state IS 'Session state and working memory tracking';

-- ============================================================================
-- AUTONOMY AUDIT LOG
-- Tracks all autonomous actions for governance and learning
-- Enhanced with ToolOrchestra-inspired efficiency tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_autonomy_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Action details
    action_type TEXT NOT NULL,
    action_category TEXT NOT NULL CHECK (action_category IN (
        'read', 'write', 'execute', 'communicate', 'schedule', 'financial', 'system'
    )),
    action_description TEXT NOT NULL,

    -- Decision context
    autonomy_level INT NOT NULL CHECK (autonomy_level >= 0 AND autonomy_level <= 4),
    decision_reasoning TEXT,
    context_summary TEXT,

    -- Confidence and boundaries
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    boundary_check JSONB NOT NULL,  -- {passed: bool, boundaries_checked: [...], violations: [...]}

    -- Outcome
    outcome TEXT CHECK (outcome IN (
        'success',      -- Action completed successfully
        'failure',      -- Action failed
        'pending',      -- Action in progress
        'cancelled',    -- Action cancelled before execution
        'overridden',   -- Human overrode the action
        'escalated'     -- Escalated to human
    )),
    outcome_details TEXT,

    -- =========================================================================
    -- EFFICIENCY TRACKING (ToolOrchestra-inspired)
    -- Enables cost/latency optimization and model selection analysis
    -- =========================================================================
    tokens_input INTEGER DEFAULT 0,          -- Input tokens consumed
    tokens_output INTEGER DEFAULT 0,         -- Output tokens generated
    tokens_thinking INTEGER DEFAULT 0,       -- Thinking/reasoning tokens (for Gemini)
    estimated_cost_usd DECIMAL(10, 6),       -- Estimated cost in USD
    latency_ms INTEGER,                      -- Total latency in milliseconds

    -- Model/tool tracking
    model_used TEXT,                         -- Primary model used (e.g., 'gemini-3-flash')
    tools_invoked JSONB DEFAULT '[]',        -- Array of tools used: [{name, latency_ms, cost, success}]
    thinking_level TEXT,                     -- Thinking level used (minimal/low/medium/high)

    -- Efficiency scoring
    efficiency_score DECIMAL(4, 3),          -- Computed: outcome_success / (normalized_cost + normalized_latency)

    -- Human involvement
    human_approval_required BOOLEAN DEFAULT FALSE,
    human_approved BOOLEAN,
    human_override BOOLEAN DEFAULT FALSE,
    override_reason TEXT,
    approver_id TEXT,

    -- Session context
    session_id TEXT,

    -- Timestamps
    proposed_at TIMESTAMPTZ DEFAULT NOW(),
    executed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Additional indexes for efficiency analysis
CREATE INDEX IF NOT EXISTS idx_audit_model ON arcus_autonomy_audit(model_used);
CREATE INDEX IF NOT EXISTS idx_audit_cost ON arcus_autonomy_audit(estimated_cost_usd DESC);
CREATE INDEX IF NOT EXISTS idx_audit_latency ON arcus_autonomy_audit(latency_ms DESC);
CREATE INDEX IF NOT EXISTS idx_audit_efficiency ON arcus_autonomy_audit(efficiency_score DESC) WHERE efficiency_score IS NOT NULL;

-- Indexes for audit
CREATE INDEX IF NOT EXISTS idx_audit_action ON arcus_autonomy_audit(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_category ON arcus_autonomy_audit(action_category);
CREATE INDEX IF NOT EXISTS idx_audit_level ON arcus_autonomy_audit(autonomy_level);
CREATE INDEX IF NOT EXISTS idx_audit_outcome ON arcus_autonomy_audit(outcome);
CREATE INDEX IF NOT EXISTS idx_audit_override ON arcus_autonomy_audit(human_override) WHERE human_override = TRUE;
CREATE INDEX IF NOT EXISTS idx_audit_executed ON arcus_autonomy_audit(executed_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_session ON arcus_autonomy_audit(session_id);

COMMENT ON TABLE arcus_autonomy_audit IS 'Audit log for all autonomous actions';

-- ============================================================================
-- MODEL/TOOL PATTERNS
-- Tracks which models/tools work best for which task contexts
-- Inspired by ToolOrchestra's outcome-based learning
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_model_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Pattern identification
    task_context TEXT NOT NULL,              -- e.g., "code_review", "document_analysis", "voice_response"
    task_complexity TEXT DEFAULT 'medium' CHECK (task_complexity IN ('low', 'medium', 'high')),

    -- Model/tool sequence that worked
    model_used TEXT NOT NULL,                -- Primary model (e.g., 'gemini-3-flash', 'claude-sonnet')
    tools_sequence JSONB DEFAULT '[]',       -- Ordered tools: [{name, params_hash, success}]

    -- Outcome tracking
    outcome TEXT NOT NULL CHECK (outcome IN ('success', 'partial', 'failure')),
    accuracy_score FLOAT CHECK (accuracy_score >= 0 AND accuracy_score <= 1),

    -- Efficiency metrics
    total_cost_usd DECIMAL(10, 6),
    total_latency_ms INTEGER,
    tokens_used INTEGER,

    -- User context
    user_preference_context TEXT,            -- e.g., "cost_sensitive", "latency_sensitive", "accuracy_first"

    -- Learning metrics
    usage_count INTEGER DEFAULT 1,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    success_rate FLOAT GENERATED ALWAYS AS (
        CASE WHEN usage_count > 0 THEN success_count::FLOAT / usage_count ELSE 0 END
    ) STORED,

    -- Confidence and quality
    confidence FLOAT DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),

    -- Source
    source JSONB NOT NULL DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_used TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Embedding for similarity search
    embedding VECTOR(1536),

    -- UNIQUE constraint for UPSERT operations (prevents race conditions)
    UNIQUE(task_context, model_used)
);

-- RPC function for atomic counter updates (prevents race conditions)
CREATE OR REPLACE FUNCTION increment_model_pattern_counters(
    p_task_context TEXT,
    p_model_used TEXT,
    p_is_success BOOLEAN,
    p_is_failure BOOLEAN,
    p_cost DECIMAL(10, 6) DEFAULT NULL,
    p_latency INTEGER DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE arcus_model_patterns
    SET
        usage_count = usage_count + 1,
        success_count = success_count + CASE WHEN p_is_success THEN 1 ELSE 0 END,
        failure_count = failure_count + CASE WHEN p_is_failure THEN 1 ELSE 0 END,
        total_cost_usd = COALESCE(p_cost, total_cost_usd),
        total_latency_ms = COALESCE(p_latency, total_latency_ms),
        last_used = NOW(),
        updated_at = NOW()
    WHERE task_context = p_task_context AND model_used = p_model_used;
END;
$$ LANGUAGE plpgsql;

-- Indexes for model patterns
CREATE INDEX IF NOT EXISTS idx_pattern_context ON arcus_model_patterns(task_context);
CREATE INDEX IF NOT EXISTS idx_pattern_model ON arcus_model_patterns(model_used);
CREATE INDEX IF NOT EXISTS idx_pattern_outcome ON arcus_model_patterns(outcome);
CREATE INDEX IF NOT EXISTS idx_pattern_success_rate ON arcus_model_patterns(success_rate DESC) WHERE usage_count >= 3;
CREATE INDEX IF NOT EXISTS idx_pattern_complexity ON arcus_model_patterns(task_complexity);
CREATE INDEX IF NOT EXISTS idx_pattern_last_used ON arcus_model_patterns(last_used DESC);

COMMENT ON TABLE arcus_model_patterns IS 'Model/tool usage patterns - tracks what works for which tasks';

-- ============================================================================
-- USER PREFERENCE VECTORS
-- Numerical preferences that modify model/skill routing
-- Inspired by ToolOrchestra's preference-aware optimization
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_user_preference_vectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- User/context identification
    user_id TEXT DEFAULT 'default',
    context_name TEXT NOT NULL,              -- e.g., "default", "confidential_data", "time_critical"

    -- Objective weights (should sum to 1.0 for normalized scoring)
    accuracy_weight FLOAT DEFAULT 0.5 CHECK (accuracy_weight >= 0 AND accuracy_weight <= 1),
    cost_weight FLOAT DEFAULT 0.3 CHECK (cost_weight >= 0 AND cost_weight <= 1),
    latency_weight FLOAT DEFAULT 0.2 CHECK (latency_weight >= 0 AND latency_weight <= 1),
    -- Note: Sum constraint enforced at application level for flexibility
    CONSTRAINT weights_sum_check CHECK (accuracy_weight + cost_weight + latency_weight BETWEEN 0.99 AND 1.01),

    -- Model preferences (0.0 = avoid, 1.0 = strongly prefer)
    model_preferences JSONB DEFAULT '{
        "claude-opus": 0.5,
        "claude-sonnet": 0.7,
        "claude-haiku": 0.6,
        "gemini-3-pro": 0.6,
        "gemini-3-flash": 0.7,
        "gemini-2.5-flash": 0.8,
        "personaplex": 0.9
    }',

    -- Tool preferences
    tool_preferences JSONB DEFAULT '{
        "web_search": 0.5,
        "local_search": 0.7,
        "code_execution": 0.6,
        "deep_research": 0.4
    }',

    -- Skill preferences
    skill_preferences JSONB DEFAULT '{
        "knowledge_repository": 0.8,
        "research": 0.6,
        "code_analysis": 0.7
    }',

    -- Context-specific overrides
    overrides JSONB DEFAULT '{}',            -- {condition: {field: value}}

    -- Learning from feedback
    feedback_count INTEGER DEFAULT 0,
    last_feedback TIMESTAMPTZ,

    -- Active/archived
    is_active BOOLEAN DEFAULT TRUE,

    -- Source
    source JSONB NOT NULL DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Ensure one active preference vector per user per context
    UNIQUE(user_id, context_name) WHERE is_active = TRUE
);

-- Indexes for preference vectors
CREATE INDEX IF NOT EXISTS idx_pref_user ON arcus_user_preference_vectors(user_id);
CREATE INDEX IF NOT EXISTS idx_pref_context ON arcus_user_preference_vectors(context_name);
CREATE INDEX IF NOT EXISTS idx_pref_active ON arcus_user_preference_vectors(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE arcus_user_preference_vectors IS 'User preference vectors for model/tool routing optimization';

-- Default preference vector
INSERT INTO arcus_user_preference_vectors (
    user_id, context_name, accuracy_weight, cost_weight, latency_weight,
    source
) VALUES (
    'default', 'default', 0.5, 0.3, 0.2,
    '{"type": "system", "note": "Initial default preferences"}'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- VECTOR SIMILARITY INDEXES (for semantic search)
-- Note: Requires pgvector extension
-- ============================================================================

-- These use IVFFlat for approximate nearest neighbor search
-- Adjust 'lists' parameter based on expected data size:
-- - lists = 100 for ~10k rows
-- - lists = 1000 for ~1M rows

CREATE INDEX IF NOT EXISTS idx_episodic_embedding ON arcus_episodic_memory
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_semantic_embedding ON arcus_semantic_memory
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_procedural_embedding ON arcus_procedural_memory
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_entities_embedding ON arcus_entities
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update modified timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update triggers to all tables
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN SELECT unnest(ARRAY[
        'arcus_episodic_memory',
        'arcus_semantic_memory',
        'arcus_procedural_memory',
        'arcus_entities',
        'arcus_relationships',
        'arcus_session_state'
    ])
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS update_%s_modtime ON %s;
            CREATE TRIGGER update_%s_modtime
            BEFORE UPDATE ON %s
            FOR EACH ROW EXECUTE FUNCTION update_modified_column();
        ', t, t, t, t);
    END LOOP;
END;
$$;

-- Function to increment entity mention count
CREATE OR REPLACE FUNCTION increment_entity_mention()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE arcus_entities
    SET mention_count = mention_count + 1,
        last_seen = NOW()
    WHERE id = ANY(
        SELECT (elem->>'id')::UUID
        FROM jsonb_array_elements(NEW.related_entities) elem
        WHERE elem->>'id' IS NOT NULL
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update entity mentions when episodic memory is added
CREATE TRIGGER update_entity_mentions
AFTER INSERT ON arcus_episodic_memory
FOR EACH ROW EXECUTE FUNCTION increment_entity_mention();

-- Function to increment relationship observation count
CREATE OR REPLACE FUNCTION increment_relationship_observation()
RETURNS TRIGGER AS $$
BEGIN
    NEW.observation_count = OLD.observation_count + 1;
    NEW.last_observed = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROW LEVEL SECURITY (for multi-user support if needed)
-- ============================================================================

-- Enable RLS on all tables (but don't enforce yet - enable when multi-user)
ALTER TABLE arcus_episodic_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_semantic_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_procedural_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_session_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_autonomy_audit ENABLE ROW LEVEL SECURITY;

-- Default policies (allow all for now, restrict later if needed)
CREATE POLICY "Allow all for now" ON arcus_episodic_memory FOR ALL USING (true);
CREATE POLICY "Allow all for now" ON arcus_semantic_memory FOR ALL USING (true);
CREATE POLICY "Allow all for now" ON arcus_procedural_memory FOR ALL USING (true);
CREATE POLICY "Allow all for now" ON arcus_entities FOR ALL USING (true);
CREATE POLICY "Allow all for now" ON arcus_relationships FOR ALL USING (true);
CREATE POLICY "Allow all for now" ON arcus_session_state FOR ALL USING (true);
CREATE POLICY "Allow all for now" ON arcus_autonomy_audit FOR ALL USING (true);

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- View: Recent important events
CREATE OR REPLACE VIEW recent_important_events AS
SELECT
    id,
    event_type,
    summary,
    participants,
    outcome,
    learnings,
    importance,
    confidence,
    event_timestamp
FROM arcus_episodic_memory
WHERE importance IN ('high', 'critical')
    AND event_timestamp > NOW() - INTERVAL '30 days'
ORDER BY event_timestamp DESC
LIMIT 100;

-- View: Active knowledge (not superseded)
CREATE OR REPLACE VIEW active_knowledge AS
SELECT *
FROM arcus_semantic_memory
WHERE (valid_until IS NULL OR valid_until > NOW())
    AND superseded_by IS NULL
ORDER BY confidence DESC, updated_at DESC;

-- View: Top workflows by success
CREATE OR REPLACE VIEW top_workflows AS
SELECT
    id,
    name,
    description,
    steps,
    usage_count,
    success_rate,
    last_used
FROM arcus_procedural_memory
WHERE procedure_type = 'workflow'
    AND usage_count >= 3
ORDER BY success_rate DESC, usage_count DESC
LIMIT 50;

-- View: Entity relationship summary
CREATE OR REPLACE VIEW entity_relationships AS
SELECT
    e.id AS entity_id,
    e.entity_type,
    e.name,
    COUNT(DISTINCT r1.id) + COUNT(DISTINCT r2.id) AS relationship_count,
    ARRAY_AGG(DISTINCT r1.relationship) || ARRAY_AGG(DISTINCT r2.relationship) AS relationship_types,
    MAX(GREATEST(r1.last_observed, r2.last_observed)) AS last_relationship_observed
FROM arcus_entities e
LEFT JOIN arcus_relationships r1 ON e.id = r1.source_entity_id
LEFT JOIN arcus_relationships r2 ON e.id = r2.target_entity_id
GROUP BY e.id, e.entity_type, e.name
ORDER BY relationship_count DESC;

-- ============================================================================
-- INITIAL DATA (Optional seed data)
-- ============================================================================

-- Insert initial preferences (customize for your team)
INSERT INTO arcus_procedural_memory (
    procedure_type, name, description, preference_value, preference_strength,
    applies_to, scope, confidence, source
) VALUES
(
    'preference', 'response_style',
    'Preferred response style for Claude',
    '{"style": "concise", "technical_level": "high", "emoji_usage": "never", "code_style": "typescript_preferred"}',
    'strong',
    ARRAY['all'],
    'global',
    0.95,
    '{"type": "user_explicit", "note": "Initial setup"}'
),
(
    'preference', 'documentation_style',
    'How to format documentation and comments',
    '{"inline_comments": "only_when_complex", "readme_creation": "only_when_requested", "docstrings": "for_public_functions"}',
    'moderate',
    ARRAY['all'],
    'global',
    0.90,
    '{"type": "user_explicit", "note": "Initial setup"}'
)
ON CONFLICT DO NOTHING;

-- Insert organization entity
INSERT INTO arcus_entities (
    entity_type, name, description, attributes, confidence, verified, source
) VALUES (
    'organization',
    'Arcus Innovation Studios',
    'The organization operating this knowledge repository',
    '{"type": "company", "industry": "technology_consulting", "focus": "ai_innovation"}',
    1.0,
    TRUE,
    '{"type": "system", "note": "Initial setup"}'
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PHASE 2: SKILL REGISTRY
-- Tracks registered skills and their capabilities
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Skill identification
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    version TEXT DEFAULT '1.0.0',

    -- Classification
    category TEXT NOT NULL CHECK (category IN (
        'knowledge',       -- Knowledge operations
        'research',        -- Research and information gathering
        'code',           -- Code analysis and generation
        'communication',  -- Drafting and formatting
        'integration',    -- External service integration
        'analysis',       -- Data and document analysis
        'voice'           -- Voice-optimized operations
    )),
    status TEXT DEFAULT 'active' CHECK (status IN (
        'active',
        'deprecated',
        'experimental',
        'disabled'
    )),

    -- Capabilities (array of capability names or full objects)
    capabilities JSONB DEFAULT '[]',
    -- Example: [{"name": "recall", "description": "...", "estimated_latency_ms": 1000}]

    -- Context requirements
    required_context TEXT[] DEFAULT '{}',     -- Must have these context types
    optional_context TEXT[] DEFAULT '{}',     -- Nice to have

    -- Model preferences
    preferred_models TEXT[] DEFAULT '{}',     -- e.g., ['claude-sonnet', 'gemini-3-flash']
    excluded_models TEXT[] DEFAULT '{}',      -- Models to never use
    min_context_window INTEGER DEFAULT 8000,  -- Minimum context window required

    -- Execution characteristics
    avg_latency_ms INTEGER DEFAULT 1000,
    avg_cost_usd DECIMAL(10, 6) DEFAULT 0.001,
    max_retries INTEGER DEFAULT 2,
    timeout_ms INTEGER DEFAULT 30000,

    -- Dependencies
    depends_on TEXT[] DEFAULT '{}',           -- Other skills this depends on
    conflicts_with TEXT[] DEFAULT '{}',       -- Skills that can't run together

    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    success_rate FLOAT GENERATED ALWAYS AS (
        CASE WHEN usage_count > 0 THEN success_count::FLOAT / usage_count ELSE 0 END
    ) STORED,
    last_used TIMESTAMPTZ,

    -- Tags and metadata
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',

    -- Source
    source JSONB NOT NULL DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for skills
CREATE INDEX IF NOT EXISTS idx_skills_name ON arcus_skills(name);
CREATE INDEX IF NOT EXISTS idx_skills_category ON arcus_skills(category);
CREATE INDEX IF NOT EXISTS idx_skills_status ON arcus_skills(status);
CREATE INDEX IF NOT EXISTS idx_skills_tags ON arcus_skills USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_skills_capabilities ON arcus_skills USING GIN(capabilities);

COMMENT ON TABLE arcus_skills IS 'Phase 2: Registered skills and their capabilities';

-- ============================================================================
-- PHASE 2: SKILL EXECUTIONS
-- Tracks individual skill executions for learning and analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_skill_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id TEXT UNIQUE NOT NULL,

    -- Skill reference
    skill_id UUID REFERENCES arcus_skills(id) ON DELETE SET NULL,
    skill_name TEXT NOT NULL,
    capability TEXT NOT NULL,

    -- Execution status
    status TEXT NOT NULL CHECK (status IN (
        'pending',
        'running',
        'completed',
        'failed',
        'cancelled',
        'timeout'
    )),

    -- Input/Output
    inputs JSONB DEFAULT '{}',
    output JSONB,
    error TEXT,

    -- Performance metrics
    latency_ms INTEGER DEFAULT 0,
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    tokens_thinking INTEGER DEFAULT 0,
    tokens_total INTEGER GENERATED ALWAYS AS (tokens_input + tokens_output + tokens_thinking) STORED,
    cost_usd DECIMAL(10, 6) DEFAULT 0,

    -- Model info
    model_used TEXT,
    thinking_level TEXT,
    fallback_used BOOLEAN DEFAULT FALSE,

    -- Context info
    context_tokens INTEGER DEFAULT 0,
    context_sources TEXT[] DEFAULT '{}',

    -- User/session tracking
    user_id TEXT DEFAULT 'default',
    session_id TEXT,
    orchestration_id TEXT,              -- Link to orchestration run

    -- Timestamps
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for skill executions
CREATE INDEX IF NOT EXISTS idx_skill_exec_skill ON arcus_skill_executions(skill_name);
CREATE INDEX IF NOT EXISTS idx_skill_exec_status ON arcus_skill_executions(status);
CREATE INDEX IF NOT EXISTS idx_skill_exec_user ON arcus_skill_executions(user_id);
CREATE INDEX IF NOT EXISTS idx_skill_exec_session ON arcus_skill_executions(session_id);
CREATE INDEX IF NOT EXISTS idx_skill_exec_orchestration ON arcus_skill_executions(orchestration_id);
CREATE INDEX IF NOT EXISTS idx_skill_exec_model ON arcus_skill_executions(model_used);
CREATE INDEX IF NOT EXISTS idx_skill_exec_created ON arcus_skill_executions(created_at DESC);

COMMENT ON TABLE arcus_skill_executions IS 'Phase 2: Individual skill execution tracking';

-- ============================================================================
-- PHASE 2: ORCHESTRATION RUNS
-- Tracks multi-skill orchestration executions
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_orchestration_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id TEXT UNIQUE NOT NULL,

    -- Task description
    task_description TEXT NOT NULL,
    task_context TEXT,
    capabilities_requested TEXT[] DEFAULT '{}',

    -- Status
    status TEXT NOT NULL CHECK (status IN (
        'planning',
        'running',
        'completed',
        'failed',
        'cancelled'
    )),

    -- Plan details
    plan_steps JSONB DEFAULT '[]',            -- Array of planned steps
    skills_used TEXT[] DEFAULT '{}',          -- Skills that were executed

    -- Aggregated metrics
    total_latency_ms INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10, 6) DEFAULT 0,
    skills_executed INTEGER DEFAULT 0,
    skills_succeeded INTEGER DEFAULT 0,
    skills_failed INTEGER DEFAULT 0,

    -- Context assembly info
    context_budget_total INTEGER,
    context_budget_used INTEGER,
    context_allocation JSONB,                 -- Budget allocation by memory type
    context_coverage JSONB,                   -- Coverage achieved by type

    -- Model routing
    primary_model TEXT,
    primary_model_confidence FLOAT,
    fallback_model TEXT,

    -- Final output
    final_output JSONB,

    -- User/session tracking
    user_id TEXT DEFAULT 'default',
    session_id TEXT,

    -- Timestamps
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for orchestration runs
CREATE INDEX IF NOT EXISTS idx_orch_status ON arcus_orchestration_runs(status);
CREATE INDEX IF NOT EXISTS idx_orch_user ON arcus_orchestration_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_orch_session ON arcus_orchestration_runs(session_id);
CREATE INDEX IF NOT EXISTS idx_orch_started ON arcus_orchestration_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_orch_context ON arcus_orchestration_runs(task_context);
CREATE INDEX IF NOT EXISTS idx_orch_skills ON arcus_orchestration_runs USING GIN(skills_used);

COMMENT ON TABLE arcus_orchestration_runs IS 'Phase 2: Multi-skill orchestration tracking';

-- ============================================================================
-- PHASE 2: CONTEXT BUDGET LOGS
-- Tracks context budget allocations for analysis and optimization
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_context_budget_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Reference to orchestration
    orchestration_id TEXT REFERENCES arcus_orchestration_runs(plan_id) ON DELETE CASCADE,
    execution_id TEXT,

    -- Model context limits
    model_id TEXT NOT NULL,
    model_context_limit INTEGER NOT NULL,

    -- Budget breakdown
    total_available INTEGER NOT NULL,
    reserved_for_prompt INTEGER DEFAULT 0,
    reserved_for_response INTEGER DEFAULT 0,
    reserved_for_overhead INTEGER DEFAULT 0,
    available_for_context INTEGER NOT NULL,

    -- Allocation by memory type
    allocation_episodic INTEGER DEFAULT 0,
    allocation_semantic INTEGER DEFAULT 0,
    allocation_procedural INTEGER DEFAULT 0,
    allocation_graph INTEGER DEFAULT 0,

    -- Actual usage
    used_episodic INTEGER DEFAULT 0,
    used_semantic INTEGER DEFAULT 0,
    used_procedural INTEGER DEFAULT 0,
    used_graph INTEGER DEFAULT 0,
    total_used INTEGER DEFAULT 0,

    -- Items selected
    items_episodic INTEGER DEFAULT 0,
    items_semantic INTEGER DEFAULT 0,
    items_procedural INTEGER DEFAULT 0,
    items_graph INTEGER DEFAULT 0,
    items_dropped INTEGER DEFAULT 0,

    -- Efficiency metrics
    utilization_rate FLOAT GENERATED ALWAYS AS (
        CASE WHEN available_for_context > 0 THEN total_used::FLOAT / available_for_context ELSE 0 END
    ) STORED,

    -- Strategy used
    ranking_strategy TEXT,
    packing_strategy TEXT,

    -- Query used for relevance ranking
    query_text TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for context budget logs
CREATE INDEX IF NOT EXISTS idx_budget_orch ON arcus_context_budget_logs(orchestration_id);
CREATE INDEX IF NOT EXISTS idx_budget_model ON arcus_context_budget_logs(model_id);
CREATE INDEX IF NOT EXISTS idx_budget_created ON arcus_context_budget_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_budget_utilization ON arcus_context_budget_logs(utilization_rate DESC);

COMMENT ON TABLE arcus_context_budget_logs IS 'Phase 2: Context budget allocation tracking';

-- ============================================================================
-- PHASE 2: RPC FUNCTIONS
-- ============================================================================

-- Function to update skill usage counters atomically
CREATE OR REPLACE FUNCTION increment_skill_counters(
    p_skill_name TEXT,
    p_is_success BOOLEAN,
    p_is_failure BOOLEAN
)
RETURNS VOID AS $$
BEGIN
    UPDATE arcus_skills
    SET
        usage_count = usage_count + 1,
        success_count = success_count + CASE WHEN p_is_success THEN 1 ELSE 0 END,
        failure_count = failure_count + CASE WHEN p_is_failure THEN 1 ELSE 0 END,
        last_used = NOW(),
        updated_at = NOW()
    WHERE name = p_skill_name;
END;
$$ LANGUAGE plpgsql;

-- Function to get best skill for a capability based on success rate
CREATE OR REPLACE FUNCTION get_best_skill_for_capability(
    p_capability TEXT,
    p_min_usage INTEGER DEFAULT 3
)
RETURNS TABLE(
    skill_name TEXT,
    skill_category TEXT,
    success_rate FLOAT,
    avg_latency_ms INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.name,
        s.category,
        s.success_rate,
        s.avg_latency_ms
    FROM arcus_skills s
    WHERE s.status = 'active'
      AND s.usage_count >= p_min_usage
      AND s.capabilities @> jsonb_build_array(jsonb_build_object('name', p_capability))
    ORDER BY s.success_rate DESC, s.avg_latency_ms ASC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PHASE 2: VIEWS
-- ============================================================================

-- View: Skill performance summary
CREATE OR REPLACE VIEW skill_performance_summary AS
SELECT
    name,
    category,
    status,
    usage_count,
    success_rate,
    avg_latency_ms,
    avg_cost_usd,
    last_used,
    ARRAY_LENGTH(capabilities::jsonb[], 1) AS capability_count
FROM arcus_skills
WHERE status = 'active'
ORDER BY usage_count DESC, success_rate DESC;

-- View: Recent orchestration runs
CREATE OR REPLACE VIEW recent_orchestration_runs AS
SELECT
    plan_id,
    task_description,
    task_context,
    status,
    skills_executed,
    skills_succeeded,
    total_latency_ms,
    total_cost_usd,
    primary_model,
    started_at,
    completed_at
FROM arcus_orchestration_runs
WHERE started_at > NOW() - INTERVAL '7 days'
ORDER BY started_at DESC
LIMIT 100;

-- View: Context budget efficiency
CREATE OR REPLACE VIEW context_budget_efficiency AS
SELECT
    model_id,
    COUNT(*) AS allocation_count,
    AVG(utilization_rate) AS avg_utilization,
    AVG(total_used) AS avg_tokens_used,
    SUM(items_dropped) AS total_items_dropped,
    AVG(items_episodic + items_semantic + items_procedural + items_graph) AS avg_items_selected
FROM arcus_context_budget_logs
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY model_id
ORDER BY avg_utilization DESC;

-- ============================================================================
-- PHASE 2: SEED DATA
-- ============================================================================

-- Insert built-in skills
INSERT INTO arcus_skills (
    name, description, category, status, capabilities,
    preferred_models, avg_latency_ms, avg_cost_usd, tags, source
) VALUES
(
    'knowledge_repository',
    'LEARN-RECALL-RELATE-REFLECT operations on persistent memory',
    'knowledge',
    'active',
    '[
        {"name": "learn", "description": "Store new knowledge", "estimated_latency_ms": 500},
        {"name": "recall", "description": "Retrieve relevant knowledge", "estimated_latency_ms": 1000},
        {"name": "relate", "description": "Create entity relationships", "estimated_latency_ms": 500},
        {"name": "reflect", "description": "Synthesize insights from learnings", "estimated_latency_ms": 3000}
    ]'::jsonb,
    ARRAY['claude-sonnet', 'gemini-3-flash'],
    1000,
    0.001,
    ARRAY['memory', 'knowledge', 'persistence'],
    '{"type": "system", "note": "Built-in skill"}'
),
(
    'research',
    'Research and information gathering',
    'research',
    'active',
    '[
        {"name": "search", "description": "Search for information", "estimated_latency_ms": 2000},
        {"name": "summarize", "description": "Summarize findings", "estimated_latency_ms": 1500},
        {"name": "synthesize", "description": "Synthesize multiple sources", "estimated_latency_ms": 3000}
    ]'::jsonb,
    ARRAY['gemini-3-pro', 'deep-research'],
    2000,
    0.005,
    ARRAY['research', 'search', 'analysis'],
    '{"type": "system", "note": "Built-in skill"}'
),
(
    'code_analysis',
    'Code review and analysis',
    'code',
    'active',
    '[
        {"name": "review", "description": "Review code for issues", "estimated_latency_ms": 3000},
        {"name": "explain", "description": "Explain code functionality", "estimated_latency_ms": 2000},
        {"name": "suggest", "description": "Suggest improvements", "estimated_latency_ms": 2500},
        {"name": "security_scan", "description": "Scan for security issues", "estimated_latency_ms": 4000}
    ]'::jsonb,
    ARRAY['claude-opus', 'claude-sonnet'],
    3000,
    0.01,
    ARRAY['code', 'review', 'analysis', 'security'],
    '{"type": "system", "note": "Built-in skill"}'
)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- PHASE 3: REWARD SIGNALS
-- Tracks reward signals for skill optimization
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_reward_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_id TEXT UNIQUE NOT NULL,

    -- Reference
    trajectory_id TEXT NOT NULL,
    user_id TEXT DEFAULT 'default',
    context TEXT,

    -- Reward values
    total_reward DECIMAL(6, 4) NOT NULL,
    accuracy_component DECIMAL(6, 4) DEFAULT 0,
    cost_component DECIMAL(6, 4) DEFAULT 0,
    latency_component DECIMAL(6, 4) DEFAULT 0,
    preference_bonus DECIMAL(6, 4) DEFAULT 0,
    efficiency_bonus DECIMAL(6, 4) DEFAULT 0,
    correction_penalty DECIMAL(6, 4) DEFAULT 0,

    -- Raw metrics
    raw_accuracy DECIMAL(6, 4),
    raw_cost_usd DECIMAL(10, 6),
    raw_latency_ms INTEGER,
    raw_tokens INTEGER,

    -- Skills and models used
    skills_used TEXT[] DEFAULT '{}',
    models_used TEXT[] DEFAULT '{}',

    -- Outcome info
    outcome_type TEXT CHECK (outcome_type IN ('success', 'partial', 'failure', 'timeout', 'cancelled')),
    required_correction BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for reward signals
CREATE INDEX IF NOT EXISTS idx_reward_trajectory ON arcus_reward_signals(trajectory_id);
CREATE INDEX IF NOT EXISTS idx_reward_user ON arcus_reward_signals(user_id);
CREATE INDEX IF NOT EXISTS idx_reward_context ON arcus_reward_signals(context);
CREATE INDEX IF NOT EXISTS idx_reward_value ON arcus_reward_signals(total_reward DESC);
CREATE INDEX IF NOT EXISTS idx_reward_created ON arcus_reward_signals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reward_skills ON arcus_reward_signals USING GIN(skills_used);
CREATE INDEX IF NOT EXISTS idx_reward_models ON arcus_reward_signals USING GIN(models_used);

COMMENT ON TABLE arcus_reward_signals IS 'Phase 3: Reward signals for skill optimization';

-- ============================================================================
-- PHASE 3: TRUST METRICS
-- Tracks trust metrics by category for autonomy progression
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_trust_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN (
        'read', 'write', 'execute', 'communicate', 'schedule', 'financial', 'system'
    )),

    -- Counts
    total_actions INTEGER DEFAULT 0,
    successful_actions INTEGER DEFAULT 0,
    corrected_actions INTEGER DEFAULT 0,
    failed_actions INTEGER DEFAULT 0,
    overridden_actions INTEGER DEFAULT 0,
    boundary_violations INTEGER DEFAULT 0,

    -- Computed rates
    success_rate FLOAT GENERATED ALWAYS AS (
        CASE WHEN total_actions > 0 THEN successful_actions::FLOAT / total_actions ELSE 0 END
    ) STORED,
    correction_rate FLOAT GENERATED ALWAYS AS (
        CASE WHEN successful_actions > 0 THEN corrected_actions::FLOAT / successful_actions ELSE 0 END
    ) STORED,

    -- Trust score for this category
    trust_score FLOAT DEFAULT 0.5 CHECK (trust_score >= 0 AND trust_score <= 1),

    -- Timestamps
    first_action_at TIMESTAMPTZ,
    last_action_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique per user+category
    UNIQUE(user_id, category)
);

-- Indexes for trust metrics
CREATE INDEX IF NOT EXISTS idx_trust_user ON arcus_trust_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_trust_category ON arcus_trust_metrics(category);
CREATE INDEX IF NOT EXISTS idx_trust_score ON arcus_trust_metrics(trust_score DESC);

COMMENT ON TABLE arcus_trust_metrics IS 'Phase 3: Trust metrics by category';

-- ============================================================================
-- PHASE 3: AUTONOMY STATE
-- Tracks overall autonomy state per user
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_autonomy_state (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT UNIQUE NOT NULL,

    -- Current state
    overall_trust FLOAT DEFAULT 0.5 CHECK (overall_trust >= 0 AND overall_trust <= 1),
    current_level INTEGER DEFAULT 0 CHECK (current_level >= 0 AND current_level <= 4),
    -- 0: Assisted, 1: Supervised, 2: Autonomous, 3: Trusted, 4: Partner

    -- Level change tracking
    pending_level_upgrade INTEGER,
    level_history JSONB DEFAULT '[]',
    last_level_change TIMESTAMPTZ,

    -- Aggregate stats
    total_actions INTEGER DEFAULT 0,
    days_at_current_level INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for autonomy state
CREATE INDEX IF NOT EXISTS idx_autonomy_user ON arcus_autonomy_state(user_id);
CREATE INDEX IF NOT EXISTS idx_autonomy_level ON arcus_autonomy_state(current_level);
CREATE INDEX IF NOT EXISTS idx_autonomy_trust ON arcus_autonomy_state(overall_trust DESC);

COMMENT ON TABLE arcus_autonomy_state IS 'Phase 3: Autonomy state per user';

-- ============================================================================
-- PHASE 3: SYNTHETIC DATASETS
-- Stores generated evaluation datasets
-- ============================================================================

CREATE TABLE IF NOT EXISTS arcus_synthetic_datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,

    -- Classification
    dataset_type TEXT NOT NULL CHECK (dataset_type IN (
        'training', 'validation', 'evaluation', 'benchmark'
    )),
    domains TEXT[] DEFAULT '{}',

    -- Contents
    example_count INTEGER DEFAULT 0,
    examples JSONB DEFAULT '[]',

    -- Quality metrics
    avg_difficulty FLOAT,
    difficulty_distribution JSONB,
    task_type_distribution JSONB,

    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for synthetic datasets
CREATE INDEX IF NOT EXISTS idx_dataset_type ON arcus_synthetic_datasets(dataset_type);
CREATE INDEX IF NOT EXISTS idx_dataset_domains ON arcus_synthetic_datasets USING GIN(domains);
CREATE INDEX IF NOT EXISTS idx_dataset_created ON arcus_synthetic_datasets(created_at DESC);

COMMENT ON TABLE arcus_synthetic_datasets IS 'Phase 3: Synthetic evaluation datasets';

-- ============================================================================
-- PHASE 3: RPC FUNCTIONS
-- ============================================================================

-- Function to update trust metrics atomically
CREATE OR REPLACE FUNCTION update_trust_metrics(
    p_user_id TEXT,
    p_category TEXT,
    p_success BOOLEAN,
    p_corrected BOOLEAN,
    p_failed BOOLEAN,
    p_overridden BOOLEAN,
    p_boundary_violation BOOLEAN,
    p_trust_delta FLOAT
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO arcus_trust_metrics (
        user_id, category, total_actions, successful_actions, corrected_actions,
        failed_actions, overridden_actions, boundary_violations, trust_score,
        first_action_at, last_action_at
    ) VALUES (
        p_user_id, p_category, 1,
        CASE WHEN p_success THEN 1 ELSE 0 END,
        CASE WHEN p_corrected THEN 1 ELSE 0 END,
        CASE WHEN p_failed THEN 1 ELSE 0 END,
        CASE WHEN p_overridden THEN 1 ELSE 0 END,
        CASE WHEN p_boundary_violation THEN 1 ELSE 0 END,
        0.5 + p_trust_delta,
        NOW(), NOW()
    )
    ON CONFLICT (user_id, category) DO UPDATE SET
        total_actions = arcus_trust_metrics.total_actions + 1,
        successful_actions = arcus_trust_metrics.successful_actions + CASE WHEN p_success THEN 1 ELSE 0 END,
        corrected_actions = arcus_trust_metrics.corrected_actions + CASE WHEN p_corrected THEN 1 ELSE 0 END,
        failed_actions = arcus_trust_metrics.failed_actions + CASE WHEN p_failed THEN 1 ELSE 0 END,
        overridden_actions = arcus_trust_metrics.overridden_actions + CASE WHEN p_overridden THEN 1 ELSE 0 END,
        boundary_violations = arcus_trust_metrics.boundary_violations + CASE WHEN p_boundary_violation THEN 1 ELSE 0 END,
        trust_score = GREATEST(0, LEAST(1, arcus_trust_metrics.trust_score + p_trust_delta)),
        last_action_at = NOW(),
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to update autonomy state
CREATE OR REPLACE FUNCTION update_autonomy_state(
    p_user_id TEXT,
    p_overall_trust FLOAT,
    p_level_change INTEGER DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO arcus_autonomy_state (user_id, overall_trust, current_level, total_actions)
    VALUES (p_user_id, p_overall_trust, 0, 1)
    ON CONFLICT (user_id) DO UPDATE SET
        overall_trust = p_overall_trust,
        current_level = COALESCE(p_level_change, arcus_autonomy_state.current_level),
        total_actions = arcus_autonomy_state.total_actions + 1,
        last_level_change = CASE WHEN p_level_change IS NOT NULL THEN NOW() ELSE arcus_autonomy_state.last_level_change END,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to compute reward statistics
CREATE OR REPLACE FUNCTION get_reward_statistics(
    p_user_id TEXT DEFAULT NULL,
    p_context TEXT DEFAULT NULL,
    p_days INTEGER DEFAULT 30
)
RETURNS TABLE(
    avg_reward FLOAT,
    min_reward FLOAT,
    max_reward FLOAT,
    total_signals INTEGER,
    avg_accuracy FLOAT,
    avg_cost_usd FLOAT,
    top_skills TEXT[],
    top_models TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        AVG(rs.total_reward)::FLOAT AS avg_reward,
        MIN(rs.total_reward)::FLOAT AS min_reward,
        MAX(rs.total_reward)::FLOAT AS max_reward,
        COUNT(*)::INTEGER AS total_signals,
        AVG(rs.raw_accuracy)::FLOAT AS avg_accuracy,
        AVG(rs.raw_cost_usd)::FLOAT AS avg_cost_usd,
        ARRAY(
            SELECT unnest(rs2.skills_used)
            FROM arcus_reward_signals rs2
            WHERE (p_user_id IS NULL OR rs2.user_id = p_user_id)
              AND (p_context IS NULL OR rs2.context = p_context)
              AND rs2.created_at > NOW() - (p_days || ' days')::INTERVAL
            GROUP BY unnest
            ORDER BY COUNT(*) DESC
            LIMIT 5
        ) AS top_skills,
        ARRAY(
            SELECT unnest(rs3.models_used)
            FROM arcus_reward_signals rs3
            WHERE (p_user_id IS NULL OR rs3.user_id = p_user_id)
              AND (p_context IS NULL OR rs3.context = p_context)
              AND rs3.created_at > NOW() - (p_days || ' days')::INTERVAL
            GROUP BY unnest
            ORDER BY COUNT(*) DESC
            LIMIT 5
        ) AS top_models
    FROM arcus_reward_signals rs
    WHERE (p_user_id IS NULL OR rs.user_id = p_user_id)
      AND (p_context IS NULL OR rs.context = p_context)
      AND rs.created_at > NOW() - (p_days || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PHASE 3: VIEWS
-- ============================================================================

-- View: Trust summary by user
CREATE OR REPLACE VIEW trust_summary AS
SELECT
    ats.user_id,
    ats.overall_trust,
    ats.current_level,
    CASE ats.current_level
        WHEN 0 THEN 'Assisted'
        WHEN 1 THEN 'Supervised'
        WHEN 2 THEN 'Autonomous'
        WHEN 3 THEN 'Trusted'
        WHEN 4 THEN 'Partner'
    END AS level_name,
    ats.total_actions,
    ats.days_at_current_level,
    (
        SELECT json_agg(json_build_object(
            'category', tm.category,
            'trust_score', tm.trust_score,
            'success_rate', tm.success_rate,
            'total_actions', tm.total_actions
        ))
        FROM arcus_trust_metrics tm
        WHERE tm.user_id = ats.user_id
    ) AS category_metrics
FROM arcus_autonomy_state ats
ORDER BY ats.overall_trust DESC;

-- View: Reward trends
CREATE OR REPLACE VIEW reward_trends AS
SELECT
    DATE_TRUNC('day', created_at) AS day,
    COUNT(*) AS signal_count,
    AVG(total_reward) AS avg_reward,
    AVG(raw_accuracy) AS avg_accuracy,
    AVG(raw_cost_usd) AS avg_cost,
    AVG(raw_latency_ms) AS avg_latency
FROM arcus_reward_signals
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY day DESC;

-- View: Skill reward performance
CREATE OR REPLACE VIEW skill_reward_performance AS
SELECT
    unnest(skills_used) AS skill,
    COUNT(*) AS usage_count,
    AVG(total_reward) AS avg_reward,
    AVG(raw_accuracy) AS avg_accuracy,
    AVG(raw_cost_usd) AS avg_cost
FROM arcus_reward_signals
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY unnest(skills_used)
ORDER BY avg_reward DESC;

-- ============================================================================
-- PHASE 3: SEED DATA
-- ============================================================================

-- Insert default autonomy state
INSERT INTO arcus_autonomy_state (user_id, overall_trust, current_level)
VALUES ('default', 0.5, 0)
ON CONFLICT (user_id) DO NOTHING;

-- ============================================================================
-- PHASE 4: VOICE ORCHESTRATION
-- ============================================================================

-- Voice-Native Knowledge Graph entries
CREATE TABLE IF NOT EXISTS arcus_vnkg_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Content
    content TEXT NOT NULL,
    spoken_form TEXT NOT NULL,
    phonetic_hints TEXT[] DEFAULT '{}',
    brevity_score FLOAT DEFAULT 0.5 CHECK (brevity_score >= 0 AND brevity_score <= 1),

    -- Indexing
    keywords TEXT[] DEFAULT '{}',
    entity_refs TEXT[] DEFAULT '{}',
    topic_tags TEXT[] DEFAULT '{}',

    -- Usage metrics
    voice_retrieval_count INTEGER DEFAULT 0,
    avg_retrieval_latency_ms FLOAT DEFAULT 0,
    user_satisfaction_score FLOAT DEFAULT 0,

    -- Validity
    ttl_seconds INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed TIMESTAMPTZ DEFAULT NOW(),

    -- Vector embedding for fast retrieval
    embedding VECTOR(1536),

    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_vnkg_keywords ON arcus_vnkg_entries USING GIN(keywords);
CREATE INDEX IF NOT EXISTS idx_vnkg_entities ON arcus_vnkg_entries USING GIN(entity_refs);
CREATE INDEX IF NOT EXISTS idx_vnkg_topics ON arcus_vnkg_entries USING GIN(topic_tags);
CREATE INDEX IF NOT EXISTS idx_vnkg_brevity ON arcus_vnkg_entries(brevity_score DESC);
CREATE INDEX IF NOT EXISTS idx_vnkg_retrieval_count ON arcus_vnkg_entries(voice_retrieval_count DESC);

-- Voice query log
CREATE TABLE IF NOT EXISTS arcus_voice_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_text TEXT NOT NULL,
    user_id TEXT NOT NULL,
    session_id TEXT,

    -- Query metadata
    audio_duration_ms INTEGER,
    speech_confidence FLOAT DEFAULT 1.0,
    detected_language TEXT DEFAULT 'en',

    -- Intent classification
    detected_intent TEXT CHECK (detected_intent IN (
        'quick_answer', 'recall', 'command', 'clarification', 'conversation', 'complex_query'
    )),
    intent_confidence FLOAT,

    -- Response metrics
    first_chunk_latency_ms INTEGER,
    total_latency_ms INTEGER,
    provider_used TEXT,
    response_mode TEXT CHECK (response_mode IN (
        'immediate', 'streaming', 'progressive', 'interruptible'
    )),

    -- Quality metrics
    skills_used TEXT[] DEFAULT '{}',
    context_tokens_used INTEGER DEFAULT 0,
    overall_confidence FLOAT,

    -- Interruption
    was_interrupted BOOLEAN DEFAULT FALSE,
    interrupt_point INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_voice_queries_user ON arcus_voice_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_voice_queries_intent ON arcus_voice_queries(detected_intent);
CREATE INDEX IF NOT EXISTS idx_voice_queries_latency ON arcus_voice_queries(first_chunk_latency_ms);
CREATE INDEX IF NOT EXISTS idx_voice_queries_time ON arcus_voice_queries(created_at DESC);

-- Proactive preparations cache
CREATE TABLE IF NOT EXISTS arcus_proactive_preparations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,

    -- Trigger configuration
    trigger_patterns TEXT[] NOT NULL,
    required_entities TEXT[] DEFAULT '{}',
    required_topic TEXT,

    -- Prepared response
    prepared_response TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.5,

    -- Tracking
    used_count INTEGER DEFAULT 0,

    -- Validity
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,

    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_proactive_user ON arcus_proactive_preparations(user_id);
CREATE INDEX IF NOT EXISTS idx_proactive_expires ON arcus_proactive_preparations(expires_at);
CREATE INDEX IF NOT EXISTS idx_proactive_patterns ON arcus_proactive_preparations USING GIN(trigger_patterns);

-- ============================================================================
-- PHASE 4: DIGITAL TWIN MODELING
-- ============================================================================

-- Cognitive profiles
CREATE TABLE IF NOT EXISTS arcus_cognitive_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT UNIQUE NOT NULL,

    -- Cognitive styles (JSON map: style -> weight)
    cognitive_styles JSONB DEFAULT '{}',

    -- Primary preferences
    communication_style TEXT DEFAULT 'direct' CHECK (communication_style IN (
        'direct', 'detailed', 'visual', 'narrative', 'structured'
    )),
    time_orientation TEXT DEFAULT 'present_focused' CHECK (time_orientation IN (
        'past_focused', 'present_focused', 'future_focused'
    )),
    risk_tolerance TEXT DEFAULT 'risk_neutral' CHECK (risk_tolerance IN (
        'risk_averse', 'risk_neutral', 'risk_seeking'
    )),
    information_processing TEXT DEFAULT 'sequential' CHECK (information_processing IN (
        'sequential', 'holistic', 'comparative', 'iterative'
    )),

    -- Profile quality
    profile_confidence FLOAT DEFAULT 0.5 CHECK (profile_confidence >= 0 AND profile_confidence <= 1),
    observations_count INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_cognitive_user ON arcus_cognitive_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_cognitive_confidence ON arcus_cognitive_profiles(profile_confidence DESC);

-- Decision patterns
CREATE TABLE IF NOT EXISTS arcus_decision_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    pattern_type TEXT NOT NULL,

    -- Pattern details
    context_tags TEXT[] DEFAULT '{}',
    decision_factors TEXT[] DEFAULT '{}',
    typical_questions TEXT[] DEFAULT '{}',
    information_needs TEXT[] DEFAULT '{}',
    decision_timeline TEXT DEFAULT 'moderate',

    -- Outcomes
    successful_outcomes INTEGER DEFAULT 0,
    unsuccessful_outcomes INTEGER DEFAULT 0,

    -- Quality
    confidence FLOAT DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    times_observed INTEGER DEFAULT 1,
    last_observed TIMESTAMPTZ DEFAULT NOW(),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_decision_user ON arcus_decision_patterns(user_id);
CREATE INDEX IF NOT EXISTS idx_decision_type ON arcus_decision_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_decision_tags ON arcus_decision_patterns USING GIN(context_tags);

-- Interaction signals
CREATE TABLE IF NOT EXISTS arcus_interaction_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Signal classification
    signal_type TEXT NOT NULL CHECK (signal_type IN (
        'question', 'correction', 'approval', 'rejection', 'feedback'
    )),

    -- Context
    topic TEXT,
    entities_involved TEXT[] DEFAULT '{}',
    task_type TEXT,

    -- Signal content
    content TEXT NOT NULL,
    sentiment TEXT DEFAULT 'neutral' CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    urgency TEXT DEFAULT 'medium' CHECK (urgency IN ('low', 'medium', 'high')),

    -- Response tracking
    response_given TEXT,
    response_accepted BOOLEAN,
    correction_made TEXT,

    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_signals_user ON arcus_interaction_signals(user_id);
CREATE INDEX IF NOT EXISTS idx_signals_type ON arcus_interaction_signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_signals_time ON arcus_interaction_signals(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_signals_entities ON arcus_interaction_signals USING GIN(entities_involved);

-- Anticipated needs
CREATE TABLE IF NOT EXISTS arcus_anticipated_needs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,

    -- Need specification
    need_type TEXT NOT NULL,
    description TEXT NOT NULL,
    context_triggers TEXT[] DEFAULT '{}',
    time_triggers TEXT[] DEFAULT '{}',

    -- Prepared content
    prepared_content TEXT,
    preparation_confidence FLOAT DEFAULT 0,

    -- Tracking
    times_anticipated INTEGER DEFAULT 0,
    times_fulfilled INTEGER DEFAULT 0,
    accuracy_rate FLOAT DEFAULT 0,

    -- Validity
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_until TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_anticipated_user ON arcus_anticipated_needs(user_id);
CREATE INDEX IF NOT EXISTS idx_anticipated_valid ON arcus_anticipated_needs(valid_until);
CREATE INDEX IF NOT EXISTS idx_anticipated_triggers ON arcus_anticipated_needs USING GIN(context_triggers);

-- ============================================================================
-- PHASE 4: VECTOR EMBEDDINGS
-- ============================================================================

-- Embedding cache
CREATE TABLE IF NOT EXISTS arcus_embedding_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    text_hash TEXT UNIQUE NOT NULL,  -- Hash of text + model

    -- Embedding data
    embedding VECTOR(1536),  -- Standard dimension, can vary
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,

    -- Source info
    text_length INTEGER,
    tokens_used INTEGER,

    -- Performance
    latency_ms INTEGER,
    cost_usd FLOAT DEFAULT 0,

    -- Validity
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ DEFAULT NOW(),

    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_embedding_hash ON arcus_embedding_cache(text_hash);
CREATE INDEX IF NOT EXISTS idx_embedding_model ON arcus_embedding_cache(model);
CREATE INDEX IF NOT EXISTS idx_embedding_expires ON arcus_embedding_cache(expires_at);

-- Search index metadata (for tracking indexed items)
CREATE TABLE IF NOT EXISTS arcus_search_index (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id TEXT UNIQUE NOT NULL,  -- ID of source item
    source_type TEXT NOT NULL,        -- episodic, semantic, procedural, graph

    -- Index status
    indexed_at TIMESTAMPTZ DEFAULT NOW(),
    embedding_id UUID REFERENCES arcus_embedding_cache(id),

    -- Content summary
    content_preview TEXT,
    keywords TEXT[] DEFAULT '{}',

    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_search_source ON arcus_search_index(source_id);
CREATE INDEX IF NOT EXISTS idx_search_type ON arcus_search_index(source_type);
CREATE INDEX IF NOT EXISTS idx_search_keywords ON arcus_search_index USING GIN(keywords);

-- ============================================================================
-- PHASE 4: RPC FUNCTIONS
-- ============================================================================

-- Function: Record voice query and get latency stats
CREATE OR REPLACE FUNCTION record_voice_query(
    p_query_text TEXT,
    p_user_id TEXT,
    p_detected_intent TEXT,
    p_first_chunk_latency_ms INTEGER,
    p_total_latency_ms INTEGER,
    p_provider_used TEXT,
    p_skills_used TEXT[],
    p_was_interrupted BOOLEAN DEFAULT FALSE
)
RETURNS TABLE (
    query_id UUID,
    avg_latency_24h FLOAT,
    under_250ms_rate FLOAT
) AS $$
DECLARE
    v_query_id UUID;
BEGIN
    -- Insert the query
    INSERT INTO arcus_voice_queries (
        query_text, user_id, detected_intent,
        first_chunk_latency_ms, total_latency_ms,
        provider_used, skills_used, was_interrupted
    )
    VALUES (
        p_query_text, p_user_id, p_detected_intent,
        p_first_chunk_latency_ms, p_total_latency_ms,
        p_provider_used, p_skills_used, p_was_interrupted
    )
    RETURNING id INTO v_query_id;

    -- Return stats
    RETURN QUERY
    SELECT
        v_query_id,
        AVG(vq.first_chunk_latency_ms)::FLOAT,
        (COUNT(*) FILTER (WHERE vq.first_chunk_latency_ms < 250))::FLOAT / NULLIF(COUNT(*), 0)
    FROM arcus_voice_queries vq
    WHERE vq.user_id = p_user_id
      AND vq.created_at > NOW() - INTERVAL '24 hours';
END;
$$ LANGUAGE plpgsql;

-- Function: Update cognitive profile from interaction
CREATE OR REPLACE FUNCTION update_cognitive_profile(
    p_user_id TEXT,
    p_cognitive_styles JSONB,
    p_communication_style TEXT DEFAULT NULL,
    p_time_orientation TEXT DEFAULT NULL
)
RETURNS arcus_cognitive_profiles AS $$
DECLARE
    v_profile arcus_cognitive_profiles;
    v_current_styles JSONB;
    v_key TEXT;
    v_new_val FLOAT;
    v_old_val FLOAT;
    v_alpha FLOAT := 0.1;  -- Learning rate
BEGIN
    -- Get or create profile
    INSERT INTO arcus_cognitive_profiles (user_id)
    VALUES (p_user_id)
    ON CONFLICT (user_id) DO NOTHING;

    -- Get current profile
    SELECT * INTO v_profile
    FROM arcus_cognitive_profiles
    WHERE user_id = p_user_id;

    -- Update cognitive styles with exponential moving average
    v_current_styles := COALESCE(v_profile.cognitive_styles, '{}');

    FOR v_key, v_new_val IN SELECT key, value::FLOAT FROM jsonb_each_text(p_cognitive_styles) LOOP
        v_old_val := COALESCE((v_current_styles->>v_key)::FLOAT, 0.5);
        v_current_styles := jsonb_set(
            v_current_styles,
            ARRAY[v_key],
            to_jsonb(v_old_val * (1 - v_alpha) + v_new_val * v_alpha)
        );
    END LOOP;

    -- Update profile
    UPDATE arcus_cognitive_profiles
    SET
        cognitive_styles = v_current_styles,
        communication_style = COALESCE(p_communication_style, communication_style),
        time_orientation = COALESCE(p_time_orientation, time_orientation),
        observations_count = observations_count + 1,
        profile_confidence = LEAST(0.95, (observations_count + 1)::FLOAT / (observations_count + 11)),
        updated_at = NOW()
    WHERE user_id = p_user_id
    RETURNING * INTO v_profile;

    RETURN v_profile;
END;
$$ LANGUAGE plpgsql;

-- Function: Get personalized context for a user
CREATE OR REPLACE FUNCTION get_personalized_context(
    p_user_id TEXT,
    p_task_type TEXT DEFAULT NULL
)
RETURNS TABLE (
    profile JSONB,
    recent_patterns JSONB,
    anticipated_needs JSONB,
    recommendations TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        -- Profile
        jsonb_build_object(
            'cognitive_styles', cp.cognitive_styles,
            'communication_style', cp.communication_style,
            'time_orientation', cp.time_orientation,
            'risk_tolerance', cp.risk_tolerance,
            'information_processing', cp.information_processing,
            'confidence', cp.profile_confidence
        ),
        -- Recent patterns
        COALESCE((
            SELECT jsonb_agg(jsonb_build_object(
                'type', dp.pattern_type,
                'factors', dp.decision_factors,
                'questions', dp.typical_questions,
                'info_needs', dp.information_needs,
                'confidence', dp.confidence
            ))
            FROM arcus_decision_patterns dp
            WHERE dp.user_id = p_user_id
              AND (p_task_type IS NULL OR p_task_type = ANY(dp.context_tags))
            ORDER BY dp.confidence DESC
            LIMIT 3
        ), '[]'::JSONB),
        -- Anticipated needs
        COALESCE((
            SELECT jsonb_agg(jsonb_build_object(
                'type', an.need_type,
                'description', an.description,
                'confidence', an.preparation_confidence
            ))
            FROM arcus_anticipated_needs an
            WHERE an.user_id = p_user_id
              AND (an.valid_until IS NULL OR an.valid_until > NOW())
            ORDER BY an.accuracy_rate DESC
            LIMIT 5
        ), '[]'::JSONB),
        -- Recommendations based on profile
        ARRAY(
            SELECT CASE
                WHEN cp.communication_style = 'direct' THEN 'Use bullet points'
                WHEN cp.communication_style = 'detailed' THEN 'Provide comprehensive explanations'
                WHEN cp.communication_style = 'structured' THEN 'Format as numbered lists'
                ELSE 'Adapt to context'
            END
        )
    FROM arcus_cognitive_profiles cp
    WHERE cp.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Semantic search with vector similarity
CREATE OR REPLACE FUNCTION semantic_search(
    p_query_embedding VECTOR(1536),
    p_memory_types TEXT[] DEFAULT NULL,
    p_top_k INTEGER DEFAULT 10,
    p_min_score FLOAT DEFAULT 0.0
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    memory_type TEXT,
    similarity_score FLOAT,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    WITH all_memories AS (
        -- Episodic memories
        SELECT
            em.id,
            em.summary AS content,
            'episodic' AS memory_type,
            1 - (em.embedding <=> p_query_embedding) AS similarity,
            em.metadata
        FROM arcus_episodic_memory em
        WHERE em.embedding IS NOT NULL
          AND (p_memory_types IS NULL OR 'episodic' = ANY(p_memory_types))

        UNION ALL

        -- Semantic memories
        SELECT
            sm.id,
            sm.statement AS content,
            'semantic' AS memory_type,
            1 - (sm.embedding <=> p_query_embedding) AS similarity,
            sm.metadata
        FROM arcus_semantic_memory sm
        WHERE sm.embedding IS NOT NULL
          AND (p_memory_types IS NULL OR 'semantic' = ANY(p_memory_types))

        UNION ALL

        -- Procedural memories
        SELECT
            pm.id,
            pm.name || ': ' || COALESCE(pm.description, '') AS content,
            'procedural' AS memory_type,
            1 - (pm.embedding <=> p_query_embedding) AS similarity,
            pm.metadata
        FROM arcus_procedural_memory pm
        WHERE pm.embedding IS NOT NULL
          AND (p_memory_types IS NULL OR 'procedural' = ANY(p_memory_types))

        UNION ALL

        -- VNKG entries
        SELECT
            ve.id,
            ve.spoken_form AS content,
            'vnkg' AS memory_type,
            1 - (ve.embedding <=> p_query_embedding) AS similarity,
            ve.metadata
        FROM arcus_vnkg_entries ve
        WHERE ve.embedding IS NOT NULL
          AND (p_memory_types IS NULL OR 'vnkg' = ANY(p_memory_types))
    )
    SELECT
        am.id,
        am.content,
        am.memory_type,
        am.similarity AS similarity_score,
        am.metadata
    FROM all_memories am
    WHERE am.similarity >= p_min_score
    ORDER BY am.similarity DESC
    LIMIT p_top_k;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PHASE 4: VIEWS
-- ============================================================================

-- View: Voice latency statistics
CREATE OR REPLACE VIEW voice_latency_stats AS
SELECT
    user_id,
    DATE_TRUNC('hour', created_at) AS hour,
    COUNT(*) AS query_count,
    AVG(first_chunk_latency_ms) AS avg_first_chunk_ms,
    AVG(total_latency_ms) AS avg_total_ms,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY first_chunk_latency_ms) AS p50_latency,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY first_chunk_latency_ms) AS p95_latency,
    COUNT(*) FILTER (WHERE first_chunk_latency_ms < 250)::FLOAT / NULLIF(COUNT(*), 0) AS under_250ms_rate
FROM arcus_voice_queries
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY user_id, DATE_TRUNC('hour', created_at)
ORDER BY hour DESC;

-- View: Digital twin summary
CREATE OR REPLACE VIEW digital_twin_summary AS
SELECT
    cp.user_id,
    cp.cognitive_styles,
    cp.communication_style,
    cp.time_orientation,
    cp.risk_tolerance,
    cp.profile_confidence,
    cp.observations_count,
    (SELECT COUNT(*) FROM arcus_decision_patterns dp WHERE dp.user_id = cp.user_id) AS decision_patterns_count,
    (SELECT COUNT(*) FROM arcus_interaction_signals is2 WHERE is2.user_id = cp.user_id) AS interaction_signals_count,
    (SELECT COUNT(*) FROM arcus_anticipated_needs an WHERE an.user_id = cp.user_id AND (an.valid_until IS NULL OR an.valid_until > NOW())) AS active_anticipated_needs,
    cp.updated_at
FROM arcus_cognitive_profiles cp
ORDER BY cp.updated_at DESC;

-- View: VNKG performance
CREATE OR REPLACE VIEW vnkg_performance AS
SELECT
    COUNT(*) AS total_entries,
    AVG(brevity_score) AS avg_brevity_score,
    SUM(voice_retrieval_count) AS total_retrievals,
    AVG(avg_retrieval_latency_ms) AS avg_latency,
    AVG(user_satisfaction_score) AS avg_satisfaction,
    COUNT(DISTINCT unnest(keywords)) AS unique_keywords,
    COUNT(DISTINCT unnest(entity_refs)) AS unique_entities
FROM arcus_vnkg_entries
WHERE created_at > NOW() - INTERVAL '30 days';

-- ============================================================================
-- PHASE 4: SEED DATA
-- ============================================================================

-- Insert default cognitive profile
INSERT INTO arcus_cognitive_profiles (user_id, cognitive_styles, communication_style)
VALUES ('default', '{"analytical": 0.5, "intuitive": 0.5}', 'direct')
ON CONFLICT (user_id) DO NOTHING;

-- ============================================================================
-- COMPLETION
-- ============================================================================

-- Grant necessary permissions (adjust role names as needed)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

COMMENT ON SCHEMA public IS 'Arcus Knowledge Repository v1.4.0 - Phase 4 Schema (Voice Orchestration + Digital Twin + Embeddings) - Updated 2026-01-25';
