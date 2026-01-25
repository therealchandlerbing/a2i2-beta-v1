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

export interface ToolInvocation {
  name: string;
  latency_ms?: number;
  cost?: number;
  success: boolean;
  params_hash?: string;
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

  // Efficiency tracking (ToolOrchestra-inspired)
  tokens_input?: number;
  tokens_output?: number;
  tokens_thinking?: number;
  estimated_cost_usd?: number;
  latency_ms?: number;
  model_used?: string;
  tools_invoked?: ToolInvocation[];
  thinking_level?: 'minimal' | 'low' | 'medium' | 'high';
  efficiency_score?: number;

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

// ============================================================================
// MODEL/TOOL PATTERNS (ToolOrchestra-inspired)
// ============================================================================

export type TaskComplexity = 'low' | 'medium' | 'high';

export type PatternOutcome = 'success' | 'partial' | 'failure';

export interface ModelPattern {
  id: UUID;
  task_context: string;
  task_complexity: TaskComplexity;
  model_used: string;
  tools_sequence: ToolInvocation[];
  outcome: PatternOutcome;
  accuracy_score?: number;
  total_cost_usd?: number;
  total_latency_ms?: number;
  tokens_used?: number;
  user_preference_context?: string;
  usage_count: number;
  success_count: number;
  failure_count: number;
  success_rate: number;
  confidence: ConfidenceLevel;
  source: KnowledgeSource;
  created_at: string;
  updated_at: string;
  last_used: string;
  metadata: Record<string, unknown>;
  embedding?: number[];
}

export interface ModelPatternInput {
  task_context: string;
  task_complexity?: TaskComplexity;
  model_used: string;
  tools_sequence?: ToolInvocation[];
  outcome: PatternOutcome;
  accuracy_score?: number;
  total_cost_usd?: number;
  total_latency_ms?: number;
  tokens_used?: number;
  user_preference_context?: string;
  confidence?: ConfidenceLevel;
  source?: KnowledgeSource;
  metadata?: Record<string, unknown>;
}

// ============================================================================
// USER PREFERENCE VECTORS (ToolOrchestra-inspired)
// ============================================================================

export interface ModelPreferences {
  'claude-opus'?: number;
  'claude-sonnet'?: number;
  'claude-haiku'?: number;
  'gemini-3-pro'?: number;
  'gemini-3-flash'?: number;
  'gemini-2.5-pro'?: number;
  'gemini-2.5-flash'?: number;
  'personaplex'?: number;
  [key: string]: number | undefined;
}

export interface ToolPreferences {
  web_search?: number;
  local_search?: number;
  code_execution?: number;
  deep_research?: number;
  [key: string]: number | undefined;
}

export interface SkillPreferences {
  knowledge_repository?: number;
  research?: number;
  code_analysis?: number;
  [key: string]: number | undefined;
}

export interface UserPreferenceVector {
  id: UUID;
  user_id: string;
  context_name: string;

  // Objective weights (should sum to 1.0)
  accuracy_weight: number;
  cost_weight: number;
  latency_weight: number;

  // Preferences (0.0 = avoid, 1.0 = strongly prefer)
  model_preferences: ModelPreferences;
  tool_preferences: ToolPreferences;
  skill_preferences: SkillPreferences;

  // Context-specific overrides
  overrides: Record<string, Record<string, number>>;

  // Learning from feedback
  feedback_count: number;
  last_feedback?: string;

  is_active: boolean;
  source: KnowledgeSource;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
}

export interface UserPreferenceVectorInput {
  user_id?: string;
  context_name: string;
  accuracy_weight?: number;
  cost_weight?: number;
  latency_weight?: number;
  model_preferences?: ModelPreferences;
  tool_preferences?: ToolPreferences;
  skill_preferences?: SkillPreferences;
  overrides?: Record<string, Record<string, number>>;
  source?: KnowledgeSource;
  metadata?: Record<string, unknown>;
}

// ============================================================================
// ORCHESTRATION TYPES
// ============================================================================

export interface OrchestrationDecision {
  selected_model: string;
  thinking_level: 'minimal' | 'low' | 'medium' | 'high' | null;
  reasoning: string;
  estimated_cost: number;
  estimated_latency_ms: number;
  confidence: ConfidenceLevel;
  matched_pattern?: UUID;
  fallback_model?: string;
}

export interface OrchestrationRequest {
  task_description: string;
  task_context?: string;
  complexity_hint?: TaskComplexity;
  user_preference_context?: string;
  max_cost_usd?: number;
  max_latency_ms?: number;
  require_tools?: string[];
  exclude_tools?: string[];
}

export interface EfficiencyReport {
  period: {
    start: string;
    end: string;
  };
  total_requests: number;
  total_cost_usd: number;
  total_tokens: number;
  avg_latency_ms: number;
  model_breakdown: Record<string, {
    count: number;
    cost: number;
    success_rate: number;
    avg_latency_ms: number;
  }>;
  recommendations: string[];
}

// ============================================================================
// PHASE 2: CONTEXT BUDGETING TYPES
// ============================================================================

export type RankingStrategy = 'recency' | 'confidence' | 'relevance' | 'balanced' | 'importance';

export type PackingStrategy = 'greedy' | 'diverse' | 'dense';

export interface TokenEstimate {
  content_tokens: number;
  metadata_tokens: number;
  total_tokens: number;
  char_count: number;
  confidence: ConfidenceLevel;
}

export interface BudgetAllocation {
  total_available: number;
  reserved_for_prompt: number;
  reserved_for_response: number;
  reserved_for_overhead: number;
  available_for_context: number;
  allocation_by_type: Record<string, number>;
  priority_weights: Record<string, number>;
}

export interface RankedItem {
  item: Record<string, unknown>;
  memory_type: KnowledgeType;
  token_estimate: number;
  rank_score: number;
  recency_score: number;
  confidence_score: number;
  relevance_score: number;
  importance_score: number;
  selected: boolean;
}

export interface PackedContext {
  items_by_type: Record<string, Record<string, unknown>[]>;
  tokens_by_type: Record<string, number>;
  total_tokens: number;
  total_items: number;
  dropped_items: number;
  coverage_by_type: Record<string, number>;
  packing_strategy: PackingStrategy;
  ranking_strategy: RankingStrategy;
}

export interface ContextPayload {
  formatted_context: string;
  total_tokens: number;
  sections: Record<string, string>;
  metadata: {
    total_items: number;
    dropped_items: number;
    coverage_by_type: Record<string, number>;
    packing_strategy: PackingStrategy;
    ranking_strategy: RankingStrategy;
  };
}

export interface ContextBudgetLog {
  id: UUID;
  orchestration_id?: string;
  execution_id?: string;
  model_id: string;
  model_context_limit: number;
  total_available: number;
  reserved_for_prompt: number;
  reserved_for_response: number;
  reserved_for_overhead: number;
  available_for_context: number;
  allocation_episodic: number;
  allocation_semantic: number;
  allocation_procedural: number;
  allocation_graph: number;
  used_episodic: number;
  used_semantic: number;
  used_procedural: number;
  used_graph: number;
  total_used: number;
  items_episodic: number;
  items_semantic: number;
  items_procedural: number;
  items_graph: number;
  items_dropped: number;
  utilization_rate: number;
  ranking_strategy?: RankingStrategy;
  packing_strategy?: PackingStrategy;
  query_text?: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

// ============================================================================
// PHASE 2: SKILL ORCHESTRATION TYPES
// ============================================================================

export type SkillStatus = 'active' | 'deprecated' | 'experimental' | 'disabled';

export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled' | 'timeout';

export type SkillCategory =
  | 'knowledge'
  | 'research'
  | 'code'
  | 'communication'
  | 'integration'
  | 'analysis'
  | 'voice';

export interface SkillCapability {
  name: string;
  description: string;
  input_schema?: Record<string, unknown>;
  output_schema?: Record<string, unknown>;
  estimated_latency_ms: number;
  estimated_cost_usd: number;
  requires_context: string[];
}

export interface SkillDefinition {
  id: UUID;
  name: string;
  description: string;
  category: SkillCategory;
  version: string;
  status: SkillStatus;
  capabilities: SkillCapability[];
  required_context: string[];
  optional_context: string[];
  preferred_models: string[];
  excluded_models: string[];
  min_context_window: number;
  avg_latency_ms: number;
  avg_cost_usd: number;
  max_retries: number;
  timeout_ms: number;
  depends_on: string[];
  conflicts_with: string[];
  usage_count: number;
  success_count: number;
  failure_count: number;
  success_rate: number;
  last_used?: string;
  tags: string[];
  metadata: Record<string, unknown>;
  source: KnowledgeSource;
  created_at: string;
  updated_at: string;
}

export interface SkillDefinitionInput {
  name: string;
  description?: string;
  category?: SkillCategory;
  version?: string;
  status?: SkillStatus;
  capabilities?: Array<string | SkillCapability>;
  required_context?: string[];
  optional_context?: string[];
  preferred_models?: string[];
  excluded_models?: string[];
  min_context_window?: number;
  avg_latency_ms?: number;
  avg_cost_usd?: number;
  max_retries?: number;
  timeout_ms?: number;
  depends_on?: string[];
  conflicts_with?: string[];
  tags?: string[];
  metadata?: Record<string, unknown>;
  source?: KnowledgeSource;
}

export interface SkillExecutionRequest {
  skill_name: string;
  capability: string;
  inputs: Record<string, unknown>;
  context?: Record<string, unknown>;
  user_id: string;
  session_id?: string;
  priority: number;
  timeout_ms?: number;
}

export interface SkillExecutionResult {
  id: UUID;
  execution_id: string;
  skill_id?: UUID;
  skill_name: string;
  capability: string;
  status: ExecutionStatus;
  inputs: Record<string, unknown>;
  output?: unknown;
  error?: string;
  latency_ms: number;
  tokens_input: number;
  tokens_output: number;
  tokens_thinking: number;
  tokens_total: number;
  cost_usd: number;
  model_used?: string;
  thinking_level?: 'minimal' | 'low' | 'medium' | 'high';
  fallback_used: boolean;
  context_tokens: number;
  context_sources: string[];
  user_id: string;
  session_id?: string;
  orchestration_id?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface OrchestrationPlanStep {
  skill: string;
  capability: string;
  order: number;
  parallel: boolean;
  depends_on?: string[];
  estimated_latency_ms?: number;
  estimated_cost_usd?: number;
}

export interface OrchestrationPlan {
  plan_id: string;
  task_description: string;
  steps: OrchestrationPlanStep[];
  estimated_total_latency_ms: number;
  estimated_total_cost_usd: number;
  context_allocation?: BudgetAllocation;
  model_decision?: OrchestrationDecision;
}

export type OrchestrationRunStatus = 'planning' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface OrchestrationRun {
  id: UUID;
  plan_id: string;
  task_description: string;
  task_context?: string;
  capabilities_requested: string[];
  status: OrchestrationRunStatus;
  plan_steps: OrchestrationPlanStep[];
  skills_used: string[];
  total_latency_ms: number;
  total_tokens_used: number;
  total_cost_usd: number;
  skills_executed: number;
  skills_succeeded: number;
  skills_failed: number;
  context_budget_total?: number;
  context_budget_used?: number;
  context_allocation?: Record<string, number>;
  context_coverage?: Record<string, number>;
  primary_model?: string;
  primary_model_confidence?: ConfidenceLevel;
  fallback_model?: string;
  final_output?: unknown;
  user_id: string;
  session_id?: string;
  started_at: string;
  completed_at?: string;
  metadata: Record<string, unknown>;
}

export interface OrchestrationResult {
  plan_id: string;
  status: ExecutionStatus;
  skill_results: SkillExecutionResult[];
  final_output?: unknown;
  total_latency_ms: number;
  total_tokens_used: number;
  total_cost_usd: number;
  context_assembled?: ContextPayload;
  patterns_learned: number;
}

// ============================================================================
// PHASE 2: MODEL ROUTING TYPES (Enhanced)
// ============================================================================

export interface ModelConfig {
  id: string;
  name: string;
  provider: 'anthropic' | 'google' | 'nvidia' | string;
  cost_per_1k_input: number;
  cost_per_1k_output: number;
  avg_latency_ms: number;
  max_context: number;
  capabilities: string[];
  thinking_levels: string[];
  best_for: string[];
}

export interface RoutingDecision {
  model_id: string;
  model_config: ModelConfig;
  thinking_level: 'minimal' | 'low' | 'medium' | 'high' | null;
  estimated_cost: number;
  estimated_latency_ms: number;
  confidence: ConfidenceLevel;
  reasoning: string;
  matched_pattern_id?: UUID;
  fallback_model?: string;
}

export interface RoutingRequest {
  task: string;
  context?: string;
  complexity?: TaskComplexity;
  preference_context?: string;
  user_id?: string;
  required_capabilities?: string[];
  max_cost_usd?: number;
  max_latency_ms?: number;
  exclude_models?: string[];
}

// ============================================================================
// PHASE 2: ANALYTICS TYPES
// ============================================================================

export interface SkillPerformanceSummary {
  name: string;
  category: SkillCategory;
  status: SkillStatus;
  usage_count: number;
  success_rate: number;
  avg_latency_ms: number;
  avg_cost_usd: number;
  last_used?: string;
  capability_count: number;
}

export interface ContextBudgetEfficiency {
  model_id: string;
  allocation_count: number;
  avg_utilization: number;
  avg_tokens_used: number;
  total_items_dropped: number;
  avg_items_selected: number;
}

export interface OrchestrationAnalytics {
  period: {
    start: string;
    end: string;
  };
  total_orchestrations: number;
  success_rate: number;
  avg_latency_ms: number;
  total_cost_usd: number;
  skills_breakdown: Record<string, {
    usage_count: number;
    success_rate: number;
    avg_latency_ms: number;
  }>;
  context_efficiency: {
    avg_utilization: number;
    avg_items_selected: number;
    avg_items_dropped: number;
  };
  recommendations: string[];
}

// ============================================================================
// PHASE 3: REWARD SIGNALS TYPES
// ============================================================================

export type RewardType = 'task_completion' | 'efficiency' | 'preference_alignment' | 'correction_penalty';

export interface SkillTrajectory {
  id: UUID;
  skill_name: string;
  capability: string;
  execution_id: string;
  steps: TrajectoryStep[];
  total_cost_usd: number;
  total_latency_ms: number;
  total_tokens: number;
  model_used: string;
  thinking_level?: 'minimal' | 'low' | 'medium' | 'high';
  created_at: string;
}

export interface TrajectoryStep {
  step_id: string;
  action: string;
  tool_used?: string;
  input_tokens: number;
  output_tokens: number;
  latency_ms: number;
  cost_usd: number;
  success: boolean;
  timestamp: string;
}

export interface Outcome {
  success: boolean;
  accuracy_score: number;
  user_satisfaction?: number;
  required_correction: boolean;
  correction_severity?: 'minor' | 'moderate' | 'major';
  task_completed: boolean;
  partial_completion?: number;
  error_type?: string;
  feedback?: string;
}

export interface RewardBreakdown {
  accuracy_component: number;
  cost_component: number;
  latency_component: number;
  preference_bonus: number;
  correction_penalty: number;
  raw_reward: number;
  normalized_reward: number;
  weights_used: {
    accuracy_weight: number;
    cost_weight: number;
    latency_weight: number;
  };
}

export interface RewardSignal {
  id: UUID;
  trajectory_id: UUID;
  skill_name: string;
  capability: string;
  execution_id: string;

  // Outcome data
  outcome_success: boolean;
  accuracy_score: number;
  task_completed: boolean;
  required_correction: boolean;
  correction_severity?: 'minor' | 'moderate' | 'major';

  // Cost/latency data
  cost_usd: number;
  latency_ms: number;
  tokens_used: number;
  model_used?: string;

  // Reward computation
  accuracy_component: number;
  cost_component: number;
  latency_component: number;
  preference_bonus: number;
  correction_penalty: number;
  raw_reward: number;
  normalized_reward: number;

  // Normalization stats
  cost_mean?: number;
  cost_std?: number;
  latency_mean?: number;
  latency_std?: number;

  // Weights
  accuracy_weight: number;
  cost_weight: number;
  latency_weight: number;

  // Context
  user_id?: string;
  session_id?: string;
  preference_context?: string;

  created_at: string;
  metadata: Record<string, unknown>;
}

export interface RewardStatistics {
  skill_name: string;
  total_signals: number;
  avg_reward: number;
  min_reward: number;
  max_reward: number;
  std_reward: number;
  success_rate: number;
  correction_rate: number;
  avg_cost_usd: number;
  avg_latency_ms: number;
}

// ============================================================================
// PHASE 3: SYNTHETIC DATA GENERATION TYPES
// ============================================================================

export type TaskType = 'recall' | 'learn' | 'relate' | 'reflect' | 'orchestrate' | 'route';

export type ComplexityLevel = 'simple' | 'moderate' | 'complex' | 'expert';

export type DatasetType = 'training' | 'validation' | 'test' | 'evaluation';

export interface DomainDefinition {
  name: string;
  description: string;
  entity_types: string[];
  relationship_types: string[];
  common_tasks: string[];
  vocabulary: string[];
  complexity_factors: string[];
}

export interface TaskTemplate {
  task_type: TaskType;
  description_template: string;
  input_schema: Record<string, unknown>;
  expected_output_schema: Record<string, unknown>;
  complexity_factors: string[];
  golden_sequence?: GoldenSkillStep[];
}

export interface GoldenSkillStep {
  skill: string;
  capability: string;
  order: number;
  expected_inputs: Record<string, unknown>;
  expected_output_type: string;
  alternatives?: string[];
}

export interface SyntheticTask {
  id: UUID;
  task_type: TaskType;
  complexity: ComplexityLevel;
  domain: string;
  description: string;
  inputs: Record<string, unknown>;
  expected_output: Record<string, unknown>;
  golden_skill_sequence: GoldenSkillStep[];
  evaluation_criteria: EvaluationCriteria;
  generated_at: string;
  generator_version: string;
  metadata: Record<string, unknown>;
}

export interface EvaluationCriteria {
  required_skills: string[];
  expected_accuracy: number;
  max_allowed_cost_usd: number;
  max_allowed_latency_ms: number;
  must_include_steps: string[];
  must_not_include_steps: string[];
  output_validation_rules: ValidationRule[];
}

export interface ValidationRule {
  field: string;
  rule_type: 'exists' | 'type' | 'range' | 'pattern' | 'contains' | 'custom';
  expected: unknown;
  error_message: string;
}

export interface EvaluationDataset {
  id: UUID;
  name: string;
  description?: string;
  dataset_type: DatasetType;
  domains: string[];
  tasks: SyntheticTask[];
  task_count: number;
  complexity_distribution: Record<ComplexityLevel, number>;
  task_type_distribution: Record<TaskType, number>;
  created_at: string;
  updated_at: string;
  version: string;
  metadata: Record<string, unknown>;
}

export interface DatasetSummary {
  id: UUID;
  name: string;
  dataset_type: DatasetType;
  task_count: number;
  domains: string[];
  avg_complexity: number;
  created_at: string;
}

export interface GenerationConfig {
  domain: string;
  task_types?: TaskType[];
  complexity_weights?: Record<ComplexityLevel, number>;
  count: number;
  include_golden_sequences: boolean;
  seed?: number;
}

// ============================================================================
// PHASE 3: AUTONOMY TRUST ENGINE TYPES
// ============================================================================

// Trust categories aligned with database schema
export type TrustCategory =
  | 'read'           // Read operations (file reads, knowledge recall)
  | 'write'          // Write operations (file writes, knowledge capture)
  | 'execute'        // Execution operations (code, commands)
  | 'communicate'    // Communication operations (emails, messages)
  | 'schedule'       // Scheduling operations (calendar, reminders)
  | 'financial'      // Financial operations (purchases, approvals)
  | 'system';        // System operations (config, settings)

export type AutonomyLevelName = 'assisted' | 'supervised' | 'autonomous' | 'trusted' | 'partner';

export interface TrustMetrics {
  category: TrustCategory;
  total_actions: number;
  successful_actions: number;
  failed_actions: number;
  corrections_required: number;
  overrides: number;
  success_rate: number;
  correction_rate: number;
  trust_score: number;
  confidence: ConfidenceLevel;
  last_action?: string;
  last_success?: string;
  last_failure?: string;
  streak_current: number;
  streak_best: number;
}

export interface TrustThresholds {
  min_actions: number;
  min_success_rate: number;
  max_correction_rate: number;
  min_streak: number;
  required_categories: TrustCategory[];
  time_at_level_days?: number;
}

export interface AutonomyLevelConfig {
  level: AutonomyLevel;
  name: AutonomyLevelName;
  description: string;
  allowed_categories: TrustCategory[];
  requires_approval: TrustCategory[];
  max_impact: 'low' | 'medium' | 'high' | 'critical';
  upgrade_thresholds: TrustThresholds;
  downgrade_triggers: DowngradeTrigger[];
}

export interface DowngradeTrigger {
  condition: 'failure_rate' | 'correction_rate' | 'consecutive_failures' | 'user_override';
  threshold: number;
  lookback_period?: string;
  target_level: AutonomyLevel;
}

export interface TrustRewardSignal {
  action_type: string;
  category: TrustCategory;
  success: boolean;
  required_correction: boolean;
  correction_severity?: 'minor' | 'moderate' | 'major';
  impact_level: 'low' | 'medium' | 'high' | 'critical';
  trust_delta: number;
  autonomy_before: AutonomyLevel;
  autonomy_after: AutonomyLevel;
  boundaries_checked: string[];
  boundaries_violated: string[];
  timestamp: string;
}

export interface AutonomyState {
  id: UUID;
  user_id: string;
  current_level: AutonomyLevel;
  level_name: AutonomyLevelName;
  trust_by_category: Record<TrustCategory, TrustMetrics>;
  overall_trust_score: number;
  overall_success_rate: number;
  overall_correction_rate: number;
  total_actions: number;
  level_history: LevelTransition[];
  upgrade_progress: UpgradeProgress;
  active_boundaries: Boundary[];
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
}

export interface LevelTransition {
  from_level: AutonomyLevel;
  to_level: AutonomyLevel;
  reason: string;
  trigger: 'upgrade' | 'downgrade' | 'manual' | 'reset';
  timestamp: string;
  approver_id?: string;
}

export interface UpgradeProgress {
  next_level: AutonomyLevel;
  requirements: TrustThresholds;
  current_progress: {
    actions_completed: number;
    success_rate: number;
    correction_rate: number;
    current_streak: number;
    categories_met: TrustCategory[];
    days_at_level: number;
  };
  percent_complete: number;
  blocking_factors: string[];
  estimated_actions_remaining: number;
}

export interface Boundary {
  category: TrustCategory;
  action_pattern: string;
  min_level_required: AutonomyLevel;
  requires_approval: boolean;
  max_impact: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  active: boolean;
}

export interface BoundaryCheckResult {
  allowed: boolean;
  boundaries_checked: string[];
  violations: string[];
  warnings: string[];
  required_approval: boolean;
  approval_reason?: string;
}

export interface TrustAuditEntry {
  id: UUID;
  user_id: string;
  action_type: string;
  category: TrustCategory;
  autonomy_level: AutonomyLevel;
  success: boolean;
  required_correction: boolean;
  correction_type?: 'minor' | 'moderate' | 'major';
  trust_before: number;
  trust_after: number;
  trust_delta: number;
  boundary_check: BoundaryCheckResult;
  context_summary?: string;
  session_id?: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

// ============================================================================
// PHASE 3: DATABASE RECORD TYPES
// ============================================================================

export interface RewardSignalRecord {
  id: UUID;
  trajectory_id: UUID;
  skill_name: string;
  capability: string;
  execution_id: string;
  outcome_success: boolean;
  accuracy_score: number;
  task_completed: boolean;
  required_correction: boolean;
  correction_severity?: string;
  cost_usd: number;
  latency_ms: number;
  tokens_used: number;
  model_used?: string;
  accuracy_component: number;
  cost_component: number;
  latency_component: number;
  preference_bonus: number;
  correction_penalty: number;
  raw_reward: number;
  normalized_reward: number;
  cost_mean?: number;
  cost_std?: number;
  latency_mean?: number;
  latency_std?: number;
  accuracy_weight: number;
  cost_weight: number;
  latency_weight: number;
  user_id?: string;
  session_id?: string;
  preference_context?: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface TrustMetricsRecord {
  id: UUID;
  user_id: string;
  category: TrustCategory;
  total_actions: number;
  successful_actions: number;
  failed_actions: number;
  corrections_required: number;
  overrides: number;
  trust_score: number;
  confidence: number;
  streak_current: number;
  streak_best: number;
  last_action?: string;
  last_success?: string;
  last_failure?: string;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
}

export interface AutonomyStateRecord {
  id: UUID;
  user_id: string;
  current_level: AutonomyLevel;
  overall_trust_score: number;
  overall_success_rate: number;
  overall_correction_rate: number;
  total_actions: number;
  level_history: LevelTransition[];
  active_boundaries: Boundary[];
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
}

export interface SyntheticDatasetRecord {
  id: UUID;
  name: string;
  description?: string;
  dataset_type: DatasetType;
  domains: string[];
  task_count: number;
  complexity_distribution: Record<string, number>;
  task_type_distribution: Record<string, number>;
  tasks_data: SyntheticTask[];
  version: string;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
}

// ============================================================================
// PHASE 3: ANALYTICS AND VIEWS
// ============================================================================

export interface TrustSummary {
  user_id: string;
  current_level: AutonomyLevel;
  level_name: AutonomyLevelName;
  overall_trust_score: number;
  total_actions: number;
  overall_success_rate: number;
  overall_correction_rate: number;
  categories_tracked: number;
  highest_trust_category?: TrustCategory;
  lowest_trust_category?: TrustCategory;
  days_at_current_level: number;
  upgrade_percent_complete: number;
}

export interface RewardTrend {
  skill_name: string;
  period_start: string;
  period_end: string;
  signal_count: number;
  avg_reward: number;
  reward_trend: 'improving' | 'stable' | 'declining';
  success_rate: number;
  correction_rate: number;
  avg_cost_usd: number;
  avg_latency_ms: number;
}

export interface SkillRewardPerformance {
  skill_name: string;
  capability: string;
  total_executions: number;
  avg_reward: number;
  best_reward: number;
  worst_reward: number;
  success_rate: number;
  correction_rate: number;
  avg_cost_usd: number;
  avg_latency_ms: number;
  preferred_model?: string;
  recommendations: string[];
}

// ============================================================================
// PHASE 4: VOICE ORCHESTRATION TYPES
// ============================================================================

export type VoiceProvider = 'personaplex' | 'gemini_live' | 'gemini_tts';

export type ResponseMode = 'immediate' | 'streaming' | 'progressive' | 'interruptible';

export type VoiceIntent =
  | 'quick_answer'
  | 'recall'
  | 'command'
  | 'clarification'
  | 'conversation'
  | 'complex_query';

export interface VoiceConfig {
  max_first_response_ms: number;
  max_complete_response_ms: number;
  streaming_chunk_ms: number;
  primary_provider: VoiceProvider;
  fallback_provider: VoiceProvider;
  default_response_mode: ResponseMode;
  allow_interrupt: boolean;
  interrupt_saves_context: boolean;
  voice_skill_weights: Record<string, number>;
  enable_proactive_prep: boolean;
  prep_cache_ttl_seconds: number;
  anticipation_window_ms: number;
  min_confidence_for_immediate: number;
  min_confidence_for_streaming: number;
}

export interface VoiceQuery {
  id: string;
  text: string;
  user_id: string;
  session_id: string;
  timestamp: string;
  audio_duration_ms?: number;
  speech_confidence: number;
  detected_language: string;
  conversation_history: Array<Record<string, unknown>>;
  active_entities: string[];
  current_topic?: string;
  response_mode?: ResponseMode;
  max_response_length?: number;
}

export interface VoiceResponseChunk {
  chunk_id: string;
  sequence: number;
  text: string;
  is_final: boolean;
  generated_at: string;
  latency_ms?: number;
  confidence: number;
  source_skill?: string;
  can_interrupt_after: boolean;
}

export interface VoiceResponse {
  id: UUID;
  query_id: string;
  chunks: VoiceResponseChunk[];
  first_chunk_latency_ms: number;
  total_latency_ms: number;
  provider_used: VoiceProvider;
  response_mode: ResponseMode;
  intent_detected: VoiceIntent;
  overall_confidence: number;
  skills_used: string[];
  context_tokens_used: number;
  was_interrupted: boolean;
  interrupt_point?: number;
  saved_context?: Record<string, unknown>;
  anticipated_follow_ups: string[];
  prepared_responses: Record<string, string>;
}

export interface VNKGEntry {
  id: UUID;
  content: string;
  spoken_form: string;
  phonetic_hints: string[];
  brevity_score: number;
  keywords: string[];
  entity_refs: string[];
  topic_tags: string[];
  voice_retrieval_count: number;
  avg_retrieval_latency_ms: number;
  user_satisfaction_score: number;
  created_at: string;
  last_accessed: string;
  ttl_seconds?: number;
}

export interface ProactivePreparation {
  id: UUID;
  trigger_patterns: string[];
  prepared_response: string;
  confidence: number;
  required_entities: string[];
  required_topic?: string;
  created_at: string;
  expires_at: string;
  used_count: number;
}

export interface VoiceLatencyStats {
  total_requests: number;
  avg_latency_ms: number;
  min_latency_ms: number;
  max_latency_ms: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  under_250ms_rate: number;
}

// ============================================================================
// PHASE 4: DIGITAL TWIN TYPES
// ============================================================================

export type CognitiveStyle =
  | 'analytical'
  | 'intuitive'
  | 'directive'
  | 'conceptual'
  | 'behavioral';

export type CommunicationStyle =
  | 'direct'
  | 'detailed'
  | 'visual'
  | 'narrative'
  | 'structured';

export type TimeOrientation =
  | 'past_focused'
  | 'present_focused'
  | 'future_focused';

export type RiskTolerance =
  | 'risk_averse'
  | 'risk_neutral'
  | 'risk_seeking';

export type InformationProcessing =
  | 'sequential'
  | 'holistic'
  | 'comparative'
  | 'iterative';

export interface CognitiveProfile {
  id: UUID;
  user_id: string;
  cognitive_styles: Record<CognitiveStyle, number>;
  communication_style: CommunicationStyle;
  time_orientation: TimeOrientation;
  risk_tolerance: RiskTolerance;
  information_processing: InformationProcessing;
  profile_confidence: number;
  observations_count: number;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
}

export interface DecisionPattern {
  id: UUID;
  user_id: string;
  pattern_type: string;
  context_tags: string[];
  decision_factors: string[];
  typical_questions: string[];
  information_needs: string[];
  decision_timeline: string;
  successful_outcomes: number;
  unsuccessful_outcomes: number;
  confidence: number;
  times_observed: number;
  last_observed: string;
}

export interface ReasoningPreference {
  id: UUID;
  user_id: string;
  domain: string;
  preferred_frameworks: string[];
  data_preferences: string[];
  analogies_used: string[];
  biases_detected: string[];
  analysis_depth: 'surface' | 'moderate' | 'deep';
  verification_level: 'trust' | 'verify' | 'deep_verify';
  confidence: number;
  observations: number;
}

export interface AnticipatedNeed {
  id: UUID;
  user_id: string;
  need_type: string;
  description: string;
  context_triggers: string[];
  time_triggers: string[];
  prepared_content?: string;
  preparation_confidence: number;
  times_anticipated: number;
  times_fulfilled: number;
  accuracy_rate: number;
  valid_from: string;
  valid_until?: string;
}

export interface InteractionSignal {
  id: UUID;
  user_id: string;
  timestamp: string;
  signal_type: 'question' | 'correction' | 'approval' | 'rejection' | 'feedback';
  topic: string;
  entities_involved: string[];
  task_type: string;
  content: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  urgency: 'low' | 'medium' | 'high';
  response_given?: string;
  response_accepted?: boolean;
  correction_made?: string;
}

export interface ProactiveSuggestion {
  id: UUID;
  user_id: string;
  suggestion_type: string;
  content: string;
  reasoning: string;
  confidence: number;
  relevance_score: number;
  urgency: string;
  triggered_by: string[];
  context_match_score: number;
  presented: boolean;
  accepted?: boolean;
  feedback?: string;
  presented_at?: string;
}

export interface DigitalTwinSummary {
  user_id: string;
  profile: {
    primary_style?: CognitiveStyle;
    communication_style: CommunicationStyle;
    time_orientation: TimeOrientation;
    risk_tolerance: RiskTolerance;
    information_processing: InformationProcessing;
    confidence: number;
    observations: number;
  };
  patterns: {
    decision_patterns: number;
    reasoning_preferences: number;
  };
  anticipation: {
    anticipated_needs: number;
    interaction_history: number;
  };
  last_updated: string;
}

// ============================================================================
// PHASE 4: EMBEDDING TYPES
// ============================================================================

export type EmbeddingProvider = 'openai' | 'voyage' | 'cohere' | 'local' | 'mock';

export type EmbeddingModel =
  | 'text-embedding-3-small'
  | 'text-embedding-3-large'
  | 'voyage-3'
  | 'voyage-code-3'
  | 'voyage-3-lite'
  | 'embed-english-v3.0'
  | 'embed-multilingual-v3.0'
  | 'all-MiniLM-L6-v2'
  | 'all-mpnet-base-v2';

export interface EmbeddingConfig {
  provider: EmbeddingProvider;
  model: EmbeddingModel;
  dimensions: number;
  batch_size: number;
  max_tokens_per_batch: number;
  cache_enabled: boolean;
  cache_ttl_hours: number;
  normalize_embeddings: boolean;
  truncate_long_texts: boolean;
  max_text_length: number;
  track_costs: boolean;
}

export interface EmbeddingResult {
  id: UUID;
  text_hash: string;
  embedding: number[];
  model: string;
  dimensions: number;
  text_length: number;
  tokens_used: number;
  latency_ms: number;
  cost_usd: number;
  created_at: string;
  expires_at?: string;
}

export interface SearchResult {
  id: string;
  content: string;
  memory_type: string;
  similarity_score: number;
  metadata: Record<string, unknown>;
  highlights: string[];
}

export interface HybridSearchResult {
  id: string;
  content: string;
  memory_type: string;
  vector_score: number;
  keyword_score: number;
  combined_score: number;
  metadata: Record<string, unknown>;
  matched_keywords: string[];
}

export interface EmbeddingStats {
  total_embeddings: number;
  total_tokens: number;
  total_cost_usd: number;
  avg_latency_ms: number;
  cache_hits: number;
  cache_misses: number;
  cache_hit_rate: number;
}

export interface VectorIndexStats {
  total_vectors: number;
  memory_types: Record<string, number>;
  avg_vector_dim: number;
}

export interface SemanticSearchStats {
  vector_index: VectorIndexStats;
  keyword_index: {
    total_documents: number;
    total_terms: number;
  };
  embedding_service: EmbeddingStats;
}

// ============================================================================
// PHASE 4: DATABASE RECORD TYPES
// ============================================================================

export interface VNKGEntryRecord {
  id: UUID;
  content: string;
  spoken_form: string;
  phonetic_hints: string[];
  brevity_score: number;
  keywords: string[];
  entity_refs: string[];
  topic_tags: string[];
  voice_retrieval_count: number;
  avg_retrieval_latency_ms: number;
  user_satisfaction_score: number;
  ttl_seconds?: number;
  created_at: string;
  last_accessed: string;
  embedding?: number[];
  metadata: Record<string, unknown>;
}

export interface VoiceQueryRecord {
  id: UUID;
  query_text: string;
  user_id: string;
  session_id?: string;
  audio_duration_ms?: number;
  speech_confidence: number;
  detected_language: string;
  detected_intent?: VoiceIntent;
  intent_confidence?: number;
  first_chunk_latency_ms?: number;
  total_latency_ms?: number;
  provider_used?: string;
  response_mode?: ResponseMode;
  skills_used: string[];
  context_tokens_used: number;
  overall_confidence?: number;
  was_interrupted: boolean;
  interrupt_point?: number;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface CognitiveProfileRecord {
  id: UUID;
  user_id: string;
  cognitive_styles: Record<string, number>;
  communication_style: CommunicationStyle;
  time_orientation: TimeOrientation;
  risk_tolerance: RiskTolerance;
  information_processing: InformationProcessing;
  profile_confidence: number;
  observations_count: number;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
}

export interface DecisionPatternRecord {
  id: UUID;
  user_id: string;
  pattern_type: string;
  context_tags: string[];
  decision_factors: string[];
  typical_questions: string[];
  information_needs: string[];
  decision_timeline: string;
  successful_outcomes: number;
  unsuccessful_outcomes: number;
  confidence: number;
  times_observed: number;
  last_observed: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface InteractionSignalRecord {
  id: UUID;
  user_id: string;
  timestamp: string;
  signal_type: string;
  topic?: string;
  entities_involved: string[];
  task_type?: string;
  content: string;
  sentiment: string;
  urgency: string;
  response_given?: string;
  response_accepted?: boolean;
  correction_made?: string;
  metadata: Record<string, unknown>;
}

export interface EmbeddingCacheRecord {
  id: UUID;
  text_hash: string;
  embedding: number[];
  model: string;
  dimensions: number;
  text_length?: number;
  tokens_used?: number;
  latency_ms?: number;
  cost_usd: number;
  created_at: string;
  expires_at?: string;
  access_count: number;
  last_accessed: string;
  metadata: Record<string, unknown>;
}

// ============================================================================
// PHASE 4: ANALYTICS AND VIEWS
// ============================================================================

export interface VoiceLatencyStatsView {
  user_id: string;
  hour: string;
  query_count: number;
  avg_first_chunk_ms: number;
  avg_total_ms: number;
  p50_latency: number;
  p95_latency: number;
  under_250ms_rate: number;
}

export interface DigitalTwinSummaryView {
  user_id: string;
  cognitive_styles: Record<string, number>;
  communication_style: CommunicationStyle;
  time_orientation: TimeOrientation;
  risk_tolerance: RiskTolerance;
  profile_confidence: number;
  observations_count: number;
  decision_patterns_count: number;
  interaction_signals_count: number;
  active_anticipated_needs: number;
  updated_at: string;
}

export interface VNKGPerformanceView {
  total_entries: number;
  avg_brevity_score: number;
  total_retrievals: number;
  avg_latency: number;
  avg_satisfaction: number;
  unique_keywords: number;
  unique_entities: number;
}
