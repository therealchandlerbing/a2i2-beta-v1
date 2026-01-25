/**
 * Arcus Knowledge Repository - Type Definitions
 * Version: 1.0.0
 *
 * Comprehensive TypeScript types for the knowledge repository system.
 * These types define the structure for all memory types and operations.
 */

// ============================================================================
// BASE TYPES
// ============================================================================

export type UUID = string;

export type KnowledgeType = 'episodic' | 'semantic' | 'procedural' | 'graph';

export type ConfidenceLevel = number; // 0.0 - 1.0

export interface KnowledgeSource {
  type: 'user_explicit' | 'user_implicit' | 'extraction' | 'inference' | 'integration' | 'system';
  session_id?: string;
  interaction_id?: string;
  document_ref?: string;
  note?: string;
}

export interface BaseKnowledgeEntity {
  id: UUID;
  confidence: ConfidenceLevel;
  source: KnowledgeSource;
  created_at: string; // ISO timestamp
  updated_at: string; // ISO timestamp
  metadata: Record<string, unknown>;
  embedding?: number[]; // Vector embedding (1536 dimensions for OpenAI)
}

// ============================================================================
// EPISODIC MEMORY (What Happened)
// ============================================================================

export type EpisodicEventType =
  | 'conversation'
  | 'decision'
  | 'meeting'
  | 'milestone'
  | 'error'
  | 'success'
  | 'feedback'
  | 'correction';

export type OutcomeType = 'positive' | 'negative' | 'neutral' | 'pending';

export type ImportanceLevel = 'low' | 'normal' | 'high' | 'critical';

export interface EntityReference {
  type: EntityType;
  id: UUID;
  name: string;
}

export interface EpisodicMemory extends BaseKnowledgeEntity {
  type: 'episodic';
  event_type: EpisodicEventType;
  summary: string;
  detailed_content?: Record<string, unknown>;
  participants: string[];
  related_entities: EntityReference[];
  related_projects: string[];
  tags: string[];
  outcome?: string;
  outcome_type?: OutcomeType;
  learnings: string[];
  importance: ImportanceLevel;
  event_timestamp: string; // ISO timestamp
}

export interface EpisodicMemoryInput {
  event_type: EpisodicEventType;
  summary: string;
  detailed_content?: Record<string, unknown>;
  participants?: string[];
  related_entities?: EntityReference[];
  related_projects?: string[];
  tags?: string[];
  outcome?: string;
  outcome_type?: OutcomeType;
  learnings?: string[];
  importance?: ImportanceLevel;
  event_timestamp?: string;
  confidence?: ConfidenceLevel;
  source?: KnowledgeSource;
  metadata?: Record<string, unknown>;
}

// ============================================================================
// SEMANTIC MEMORY (What We Know)
// ============================================================================

export type SemanticCategory =
  | 'fact'
  | 'pattern'
  | 'framework'
  | 'definition'
  | 'best_practice'
  | 'insight'
  | 'preference';

export interface SemanticMemory extends BaseKnowledgeEntity {
  type: 'semantic';
  category: SemanticCategory;
  statement: string;
  explanation?: string;
  evidence: string[];
  evidence_count: number;
  domain?: string;
  subdomain?: string;
  related_concepts: string[];
  tags: string[];
  valid_from: string; // ISO timestamp
  valid_until?: string; // ISO timestamp, null if still valid
  superseded_by?: UUID;
  last_accessed: string; // ISO timestamp
  access_count: number;
}

export interface SemanticMemoryInput {
  category: SemanticCategory;
  statement: string;
  explanation?: string;
  evidence?: string[];
  domain?: string;
  subdomain?: string;
  related_concepts?: string[];
  tags?: string[];
  valid_until?: string;
  confidence?: ConfidenceLevel;
  source?: KnowledgeSource;
  metadata?: Record<string, unknown>;
}

// ============================================================================
// PROCEDURAL MEMORY (How We Work)
// ============================================================================

export type ProcedureType =
  | 'workflow'
  | 'preference'
  | 'standard'
  | 'template'
  | 'decision_tree'
  | 'shortcut'
  | 'automation';

export type PreferenceStrength = 'strong' | 'moderate' | 'weak';

export type ProcedureScope = 'global' | 'project' | 'person' | 'context';

export interface WorkflowStep {
  order: number;
  action: string;
  skill?: string;
  conditions?: string[];
  on_success?: string;
  on_failure?: string;
}

export interface ProceduralMemory extends BaseKnowledgeEntity {
  type: 'procedural';
  procedure_type: ProcedureType;
  name: string;
  description?: string;
  steps?: WorkflowStep[];
  preference_value?: Record<string, unknown>;
  preference_strength?: PreferenceStrength;
  trigger_conditions: string[];
  trigger_keywords: string[];
  trigger_entities: string[];
  success_criteria: string[];
  applies_to: string[];
  scope: ProcedureScope;
  usage_count: number;
  success_count: number;
  failure_count: number;
  success_rate: number;
  last_used?: string; // ISO timestamp
}

export interface ProceduralMemoryInput {
  procedure_type: ProcedureType;
  name: string;
  description?: string;
  steps?: WorkflowStep[];
  preference_value?: Record<string, unknown>;
  preference_strength?: PreferenceStrength;
  trigger_conditions?: string[];
  trigger_keywords?: string[];
  trigger_entities?: string[];
  success_criteria?: string[];
  applies_to?: string[];
  scope?: ProcedureScope;
  confidence?: ConfidenceLevel;
  source?: KnowledgeSource;
  metadata?: Record<string, unknown>;
}

// ============================================================================
// KNOWLEDGE GRAPH (How Things Connect)
// ============================================================================

export type EntityType =
  | 'person'
  | 'organization'
  | 'project'
  | 'concept'
  | 'document'
  | 'decision'
  | 'meeting'
  | 'skill'
  | 'tool'
  | 'location';

export interface GraphEntity extends BaseKnowledgeEntity {
  type: 'entity';
  entity_type: EntityType;
  external_id?: string;
  name: string;
  aliases: string[];
  description?: string;
  attributes: Record<string, unknown>;
  first_seen: string; // ISO timestamp
  last_seen: string; // ISO timestamp
  mention_count: number;
  verified: boolean;
}

export interface GraphEntityInput {
  entity_type: EntityType;
  external_id?: string;
  name: string;
  aliases?: string[];
  description?: string;
  attributes?: Record<string, unknown>;
  verified?: boolean;
  confidence?: ConfidenceLevel;
  source?: KnowledgeSource;
  metadata?: Record<string, unknown>;
}

export type RelationshipType =
  // Professional
  | 'works_at' | 'worked_at' | 'manages' | 'reports_to' | 'collaborates_with'
  | 'hired' | 'fired' | 'promoted' | 'mentors' | 'mentored_by'
  // Business
  | 'partner_of' | 'client_of' | 'vendor_of' | 'competitor_of'
  | 'invested_in' | 'acquired' | 'merged_with'
  // Project
  | 'owns' | 'leads' | 'contributes_to' | 'created' | 'modified'
  | 'approved' | 'rejected' | 'reviewed'
  // Knowledge
  | 'related_to' | 'part_of' | 'contains' | 'depends_on' | 'blocks'
  | 'derived_from' | 'supersedes' | 'conflicts_with'
  // Social
  | 'knows' | 'introduced' | 'referred' | 'trusts' | 'distrusts'
  // Event
  | 'participated_in' | 'organized' | 'attended' | 'spoke_at'
  | 'decided_on' | 'influenced' | 'caused' | 'prevented';

export type RelationshipCategory =
  | 'professional'
  | 'business'
  | 'project'
  | 'knowledge'
  | 'social'
  | 'event'
  | 'other';

export interface GraphRelationship extends BaseKnowledgeEntity {
  type: 'relationship';
  source_entity_id: UUID;
  source_type: EntityType;
  source_name: string;
  relationship: RelationshipType;
  relationship_category: RelationshipCategory;
  target_entity_id: UUID;
  target_type: EntityType;
  target_name: string;
  properties: Record<string, unknown>;
  bidirectional: boolean;
  evidence_count: number;
  first_observed: string; // ISO timestamp
  last_observed: string; // ISO timestamp
  observation_count: number;
}

export interface GraphRelationshipInput {
  source: EntityReference | UUID;
  relationship: RelationshipType;
  target: EntityReference | UUID;
  properties?: Record<string, unknown>;
  bidirectional?: boolean;
  confidence?: ConfidenceLevel;
  source_info?: KnowledgeSource;
  metadata?: Record<string, unknown>;
}

// ============================================================================
// SESSION STATE
// ============================================================================

export type SyncStatus = 'active' | 'syncing' | 'synced' | 'archived';

export interface SessionState {
  id: UUID;
  session_id: string;
  user_id?: string;
  user_preferences: Record<string, unknown>;
  active_projects: EntityReference[];
  active_entities: EntityReference[];
  recent_topics: string[];
  pending_learnings: PendingLearning[];
  actions_log: ActionLogEntry[];
  working_memory: Record<string, unknown>;
  interaction_count: number;
  tool_use_count: number;
  learning_capture_count: number;
  started_at: string; // ISO timestamp
  last_activity: string; // ISO timestamp
  ended_at?: string; // ISO timestamp
  sync_status: SyncStatus;
  metadata: Record<string, unknown>;
}

export interface PendingLearning {
  type: KnowledgeType;
  content: unknown;
  captured_at: string;
  source: KnowledgeSource;
}

export interface ActionLogEntry {
  timestamp: string;
  action: string;
  tool?: string;
  outcome?: 'success' | 'failure';
  details?: Record<string, unknown>;
}

// ============================================================================
// AUTONOMY
// ============================================================================

export type AutonomyLevel = 0 | 1 | 2 | 3 | 4;
// 0: Assisted - Human does, Claude advises
// 1: Supervised - Claude proposes, human confirms
// 2: Autonomous - Claude acts, human reviews after
// 3: Trusted - Claude acts, exceptions only
// 4: Partner - Full collaboration, peer-level

export type ActionCategory =
  | 'read'
  | 'write'
  | 'execute'
  | 'communicate'
  | 'schedule'
  | 'financial'
  | 'system';

export type ActionOutcome =
  | 'success'
  | 'failure'
  | 'pending'
  | 'cancelled'
  | 'overridden'
  | 'escalated';

export interface BoundaryCheck {
  passed: boolean;
  boundaries_checked: string[];
  violations: string[];
}

export interface AutonomyAuditEntry {
  id: UUID;
  action_type: string;
  action_category: ActionCategory;
  action_description: string;
  autonomy_level: AutonomyLevel;
  decision_reasoning?: string;
  context_summary?: string;
  confidence: ConfidenceLevel;
  boundary_check: BoundaryCheck;
  outcome?: ActionOutcome;
  outcome_details?: string;
  human_approval_required: boolean;
  human_approved?: boolean;
  human_override: boolean;
  override_reason?: string;
  approver_id?: string;
  session_id?: string;
  proposed_at: string; // ISO timestamp
  executed_at?: string; // ISO timestamp
  completed_at?: string; // ISO timestamp
  metadata: Record<string, unknown>;
}

// ============================================================================
// OPERATIONS
// ============================================================================

export interface LearnOperation {
  type: 'episodic' | 'semantic' | 'procedural';
  content: EpisodicMemoryInput | SemanticMemoryInput | ProceduralMemoryInput;
}

export interface RelateOperation {
  source: EntityReference | GraphEntityInput;
  relationship: RelationshipType;
  target: EntityReference | GraphEntityInput;
  properties?: Record<string, unknown>;
}

export interface RecallQuery {
  query: string;
  memory_types?: KnowledgeType[];
  limit?: number;
  min_confidence?: ConfidenceLevel;
  time_range?: {
    start?: string;
    end?: string;
  };
  filters?: Record<string, unknown>;
}

export interface RecallResult<T> {
  items: T[];
  total_count: number;
  query_time_ms: number;
  memory_type: KnowledgeType;
}

export interface ReflectRequest {
  time_period: {
    start: string;
    end: string;
  };
  focus_areas?: string[];
  min_evidence_count?: number;
}

export interface ReflectInsight {
  pattern: string;
  evidence_count: number;
  confidence: ConfidenceLevel;
  recommendation?: string;
  supporting_memories: UUID[];
}

export interface ReflectResult {
  period: {
    start: string;
    end: string;
  };
  insights: ReflectInsight[];
  new_semantic_entries: SemanticMemory[];
  new_procedural_entries: ProceduralMemory[];
}

// ============================================================================
// CLAUDE.memory.md STRUCTURE
// ============================================================================

export interface MemoryFileStructure {
  // Header
  version: string;
  last_updated: string;
  session_count: number;

  // Sections
  user_preferences: {
    communication_style: Record<string, string>;
    technical_preferences: Record<string, string>;
    workflow_preferences: Record<string, string>;
  };

  organization_context: {
    organization: {
      name: string;
      focus: string;
      team: string[];
    };
    active_projects: Array<{
      name: string;
      priority: 'LOW' | 'MEDIUM' | 'HIGH';
      description: string;
      current_phase: string;
    }>;
    technology_stack: Record<string, string>;
  };

  recent_learnings: {
    session_learnings: Array<{
      date: string;
      learning: string;
      confidence: ConfidenceLevel;
    }>;
    patterns_observed: string[];
  };

  active_context: {
    current_session_focus: string;
    recently_discussed_entities: EntityReference[];
    open_questions: string[];
  };

  pending_actions: {
    to_complete: string[];
    to_remember: string[];
  };

  memory_operations_log: {
    recent_captures: Array<{
      timestamp: string;
      type: KnowledgeType;
      summary: string;
      confidence: ConfidenceLevel;
    }>;
    sync_status: {
      last_sync: string | null;
      pending_captures: number;
      next_sync: string;
    };
  };

  autonomy_status: {
    current_level: AutonomyLevel;
    trust_metrics: {
      successful_actions: number;
      corrections_received: number;
      patterns_identified: number;
      session_count: number;
    };
    boundary_reminders: {
      always_confirm: string[];
      can_do_autonomously: string[];
      never_without_asking: string[];
    };
  };

  notes: {
    session_notes: string[];
    technical_notes: string[];
  };
}

// ============================================================================
// API RESPONSES
// ============================================================================

export interface KnowledgeApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  metadata: {
    timestamp: string;
    duration_ms: number;
    session_id?: string;
  };
}

export interface BulkOperationResult {
  total: number;
  successful: number;
  failed: number;
  errors: Array<{
    index: number;
    error: string;
  }>;
}
