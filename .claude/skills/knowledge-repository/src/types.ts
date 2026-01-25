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
