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
-- COMPLETION
-- ============================================================================

-- Grant necessary permissions (adjust role names as needed)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

COMMENT ON SCHEMA public IS 'Arcus Knowledge Repository v1.0.0 - Schema created 2026-01-24';
