"""
Arcus Skill Orchestrator - Intelligent Skill Coordination

This module provides the Skill Orchestration Layer for A2I2:
1. Skill registration and capability tracking
2. Skill selection based on task requirements
3. Multi-skill execution coordination
4. Context assembly and knowledge injection
5. Outcome tracking and learning

Implements the "Skill Orchestration Layer" enhancement from Phase 2.

Usage:
    from skill_orchestrator import SkillOrchestrator, SkillDefinition

    orchestrator = SkillOrchestrator()

    # Register a skill
    orchestrator.register_skill(SkillDefinition(
        name="knowledge_repository",
        capabilities=["learn", "recall", "relate", "reflect"],
        required_context=["user_preferences"],
        preferred_models=["claude-sonnet", "gemini-3-flash"]
    ))

    # Execute a task
    result = await orchestrator.execute(
        task="Find all information about TechCorp",
        context="research",
        user_id="default"
    )
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum

# Import dependencies with fallback for standalone testing
try:
    from knowledge_operations import (
        KnowledgeRepository,
        PatternOutcome,
        TaskComplexity,
        ToolInvocation,
        MemoryType,
    )
except ImportError:
    # Provide stubs for standalone testing
    KnowledgeRepository = None
    PatternOutcome = None
    TaskComplexity = None
    ToolInvocation = None
    MemoryType = None

try:
    from model_router import ModelRouter, RoutingDecision, TaskComplexity as RouterComplexity
except ImportError:
    ModelRouter = None
    RoutingDecision = None
    RouterComplexity = None

try:
    from context_budget import (
        ContextBudgetManager,
        BudgetAllocation,
        PackedContext,
        ContextPayload,
        RankingStrategy,
        PackingStrategy,
    )
except ImportError:
    ContextBudgetManager = None
    BudgetAllocation = None
    PackedContext = None
    ContextPayload = None
    RankingStrategy = None
    PackingStrategy = None


# =============================================================================
# ENUMS
# =============================================================================

class SkillStatus(Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    DISABLED = "disabled"


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class SkillCategory(Enum):
    KNOWLEDGE = "knowledge"        # Knowledge operations (learn, recall, etc.)
    RESEARCH = "research"          # Research and information gathering
    CODE = "code"                  # Code analysis and generation
    COMMUNICATION = "communication"  # Drafting and formatting
    INTEGRATION = "integration"    # External service integration
    ANALYSIS = "analysis"          # Data and document analysis
    VOICE = "voice"                # Voice-optimized operations


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class SkillCapability:
    """A specific capability of a skill."""
    name: str
    description: str
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    estimated_latency_ms: int = 1000
    estimated_cost_usd: float = 0.001
    requires_context: List[str] = field(default_factory=list)


@dataclass
class SkillDefinition:
    """Definition of a skill that can be orchestrated."""
    name: str
    description: str = ""
    category: SkillCategory = SkillCategory.KNOWLEDGE
    version: str = "1.0.0"
    status: SkillStatus = SkillStatus.ACTIVE

    # Capabilities this skill provides
    capabilities: List[Union[str, SkillCapability]] = field(default_factory=list)

    # Context requirements
    required_context: List[str] = field(default_factory=list)  # Must have
    optional_context: List[str] = field(default_factory=list)  # Nice to have

    # Model preferences
    preferred_models: List[str] = field(default_factory=list)
    excluded_models: List[str] = field(default_factory=list)
    min_context_window: int = 8000

    # Execution characteristics
    avg_latency_ms: int = 1000
    avg_cost_usd: float = 0.001
    max_retries: int = 2
    timeout_ms: int = 30000

    # Dependencies on other skills
    depends_on: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)

    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillExecutionRequest:
    """Request to execute a skill."""
    skill_name: str
    capability: str
    inputs: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    user_id: str = "default"
    session_id: Optional[str] = None
    priority: int = 5  # 1=highest, 10=lowest
    timeout_ms: Optional[int] = None


@dataclass
class SkillExecutionResult:
    """Result of skill execution."""
    execution_id: str
    skill_name: str
    capability: str
    status: ExecutionStatus
    inputs: Optional[Dict[str, Any]] = None  # Input parameters used
    output: Optional[Any] = None
    error: Optional[str] = None

    # Execution metrics
    latency_ms: int = 0
    tokens_used: int = 0
    cost_usd: float = 0.0

    # Model info
    model_used: Optional[str] = None
    thinking_level: Optional[str] = None

    # Context info
    context_tokens: int = 0
    context_sources: List[str] = field(default_factory=list)

    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "skill_name": self.skill_name,
            "capability": self.capability,
            "status": self.status.value,
            "inputs": self.inputs,
            "output": self.output,
            "error": self.error,
            "latency_ms": self.latency_ms,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "model_used": self.model_used,
            "thinking_level": self.thinking_level,
            "context_tokens": self.context_tokens,
            "context_sources": self.context_sources,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }


@dataclass
class OrchestrationPlan:
    """Plan for executing multiple skills."""
    plan_id: str
    task_description: str
    steps: List[Dict[str, Any]]
    estimated_total_latency_ms: int = 0
    estimated_total_cost_usd: float = 0.0
    context_allocation: Optional[BudgetAllocation] = None
    model_decision: Optional[RoutingDecision] = None


@dataclass
class OrchestrationResult:
    """Result of an orchestration execution."""
    plan_id: str
    status: ExecutionStatus
    skill_results: List[SkillExecutionResult]
    final_output: Optional[Any] = None

    # Aggregated metrics
    total_latency_ms: int = 0
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0

    # Context info
    context_assembled: Optional[ContextPayload] = None

    # Learning
    patterns_learned: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "status": self.status.value,
            "skill_results": [r.to_dict() for r in self.skill_results],
            "final_output": self.final_output,
            "total_latency_ms": self.total_latency_ms,
            "total_tokens_used": self.total_tokens_used,
            "total_cost_usd": self.total_cost_usd,
            "patterns_learned": self.patterns_learned
        }


# =============================================================================
# SKILL REGISTRY
# =============================================================================

class SkillRegistry:
    """
    Registry of available skills.

    Manages skill definitions, capabilities, and discovery.
    """

    def __init__(self):
        self._skills: Dict[str, SkillDefinition] = {}
        self._capability_index: Dict[str, List[str]] = {}  # capability -> [skill_names]
        self._category_index: Dict[SkillCategory, List[str]] = {}

    def register(self, skill: SkillDefinition) -> None:
        """Register a skill."""
        self._skills[skill.name] = skill

        # Index by capabilities
        for cap in skill.capabilities:
            cap_name = cap if isinstance(cap, str) else cap.name
            if cap_name not in self._capability_index:
                self._capability_index[cap_name] = []
            if skill.name not in self._capability_index[cap_name]:
                self._capability_index[cap_name].append(skill.name)

        # Index by category
        if skill.category not in self._category_index:
            self._category_index[skill.category] = []
        if skill.name not in self._category_index[skill.category]:
            self._category_index[skill.category].append(skill.name)

    def unregister(self, skill_name: str) -> bool:
        """Unregister a skill."""
        if skill_name not in self._skills:
            return False

        skill = self._skills[skill_name]

        # Remove from capability index
        for cap in skill.capabilities:
            cap_name = cap if isinstance(cap, str) else cap.name
            if cap_name in self._capability_index:
                self._capability_index[cap_name] = [
                    s for s in self._capability_index[cap_name] if s != skill_name
                ]

        # Remove from category index
        if skill.category in self._category_index:
            self._category_index[skill.category] = [
                s for s in self._category_index[skill.category] if s != skill_name
            ]

        del self._skills[skill_name]
        return True

    def get(self, name: str) -> Optional[SkillDefinition]:
        """Get a skill by name."""
        return self._skills.get(name)

    def find_by_capability(self, capability: str) -> List[SkillDefinition]:
        """Find skills that provide a capability."""
        skill_names = self._capability_index.get(capability, [])
        return [self._skills[name] for name in skill_names if name in self._skills]

    def find_by_category(self, category: SkillCategory) -> List[SkillDefinition]:
        """Find skills in a category."""
        skill_names = self._category_index.get(category, [])
        return [self._skills[name] for name in skill_names if name in self._skills]

    def list_all(self, include_inactive: bool = False) -> List[SkillDefinition]:
        """List all registered skills."""
        if include_inactive:
            return list(self._skills.values())
        return [s for s in self._skills.values() if s.status == SkillStatus.ACTIVE]

    def list_capabilities(self) -> List[str]:
        """List all available capabilities."""
        return list(self._capability_index.keys())


# =============================================================================
# SKILL EXECUTOR
# =============================================================================

class SkillExecutor:
    """
    Executes individual skills.

    Handles:
    - Skill invocation
    - Timeout management
    - Error handling
    - Metric collection
    """

    def __init__(
        self,
        repository: Optional["KnowledgeRepository"] = None,
        router: Optional["ModelRouter"] = None
    ):
        # Handle case where dependencies are not available
        if KnowledgeRepository is not None:
            self.repository = repository or KnowledgeRepository()
        else:
            self.repository = repository

        if ModelRouter is not None and self.repository is not None:
            self.router = router or ModelRouter(repository=self.repository)
        else:
            self.router = router

        self._handlers: Dict[str, Callable] = {}

    def register_handler(self, skill_name: str, handler: Callable) -> None:
        """Register a handler function for a skill."""
        self._handlers[skill_name] = handler

    async def execute(
        self,
        request: SkillExecutionRequest,
        skill: SkillDefinition,
        context_payload: Optional[ContextPayload] = None
    ) -> SkillExecutionResult:
        """
        Execute a skill.

        Args:
            request: Execution request
            skill: Skill definition
            context_payload: Optional assembled context

        Returns:
            Execution result
        """
        execution_id = str(uuid.uuid4())[:8]
        started_at = datetime.utcnow()

        result = SkillExecutionResult(
            execution_id=execution_id,
            skill_name=request.skill_name,
            capability=request.capability,
            status=ExecutionStatus.RUNNING,
            inputs=request.inputs,
            started_at=started_at.isoformat()
        )

        try:
            # Get model routing decision
            routing_decision = self.router.route(
                task=str(request.inputs.get("query", request.capability)),
                context=request.skill_name,
                complexity=self._estimate_complexity(request, skill),
                user_id=request.user_id,
                exclude_models=skill.excluded_models or None
            )

            result.model_used = routing_decision.model_id
            result.thinking_level = routing_decision.thinking_level

            # Set context info
            if context_payload:
                result.context_tokens = context_payload.total_tokens
                result.context_sources = list(context_payload.sections.keys())

            # Execute via handler or built-in
            timeout = request.timeout_ms or skill.timeout_ms
            output = await self._execute_with_timeout(
                request=request,
                skill=skill,
                context=context_payload,
                timeout_ms=timeout
            )

            result.output = output
            result.status = ExecutionStatus.COMPLETED

        except asyncio.TimeoutError:
            result.status = ExecutionStatus.TIMEOUT
            result.error = f"Skill execution timed out after {skill.timeout_ms}ms"

        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)

        finally:
            completed_at = datetime.utcnow()
            result.completed_at = completed_at.isoformat()
            result.latency_ms = int((completed_at - started_at).total_seconds() * 1000)

        # Record outcome for learning
        self._record_outcome(result, skill)

        return result

    async def _execute_with_timeout(
        self,
        request: SkillExecutionRequest,
        skill: SkillDefinition,
        context: Optional[ContextPayload],
        timeout_ms: int
    ) -> Any:
        """Execute with timeout handling."""
        # Check for registered handler
        if request.skill_name in self._handlers:
            handler = self._handlers[request.skill_name]
            task = asyncio.create_task(
                self._call_handler(handler, request, context)
            )
        else:
            # Use built-in handlers
            task = asyncio.create_task(
                self._builtin_execute(request, skill, context)
            )

        try:
            return await asyncio.wait_for(task, timeout=timeout_ms / 1000)
        except asyncio.TimeoutError:
            task.cancel()
            raise

    async def _call_handler(
        self,
        handler: Callable,
        request: SkillExecutionRequest,
        context: Optional[ContextPayload]
    ) -> Any:
        """Call a registered handler."""
        if asyncio.iscoroutinefunction(handler):
            return await handler(request, context)
        return handler(request, context)

    async def _builtin_execute(
        self,
        request: SkillExecutionRequest,
        skill: SkillDefinition,
        context: Optional[ContextPayload]
    ) -> Any:
        """Execute using built-in skill implementations."""
        # Knowledge repository operations
        if request.skill_name == "knowledge_repository":
            return await self._execute_knowledge_op(request)

        # Research operations
        if request.skill_name == "research":
            return await self._execute_research(request, context)

        # Default: return a placeholder
        return {
            "message": f"Skill '{request.skill_name}' executed with capability '{request.capability}'",
            "inputs": request.inputs
        }

    async def _execute_knowledge_op(self, request: SkillExecutionRequest) -> Any:
        """Execute knowledge repository operations."""
        capability = request.capability
        inputs = request.inputs

        if capability == "recall":
            return self.repository.recall(
                query=inputs.get("query", ""),
                memory_types=[MemoryType(mt) for mt in inputs.get("memory_types", ["semantic", "procedural"])],
                limit=inputs.get("limit", 10),
                min_confidence=inputs.get("min_confidence", 0.5)
            )

        elif capability == "learn":
            memory_type = MemoryType(inputs.get("memory_type", "semantic"))
            if memory_type == MemoryType.SEMANTIC:
                return self.repository.learn_fact(
                    statement=inputs.get("content", ""),
                    domain=inputs.get("domain"),
                    confidence=inputs.get("confidence", 0.8)
                )
            elif memory_type == MemoryType.PROCEDURAL:
                return self.repository.learn_preference(
                    preference=inputs.get("content", ""),
                    confidence=inputs.get("confidence", 0.9)
                )

        elif capability == "relate":
            return self.repository.relate(
                source_name=inputs.get("source_name", ""),
                relationship=inputs.get("relationship", "related_to"),
                target_name=inputs.get("target_name", ""),
                properties=inputs.get("properties")
            )

        elif capability == "reflect":
            return self.repository.reflect(
                days=inputs.get("days", 30),
                focus_areas=inputs.get("focus_areas")
            )

        return {"error": f"Unknown capability: {capability}"}

    async def _execute_research(
        self,
        request: SkillExecutionRequest,
        context: Optional[ContextPayload]
    ) -> Any:
        """Execute research operations."""
        # Placeholder for research implementation
        return {
            "message": "Research capability",
            "query": request.inputs.get("query"),
            "context_used": context is not None
        }

    def _estimate_complexity(
        self,
        request: SkillExecutionRequest,
        skill: SkillDefinition
    ) -> RouterComplexity:
        """Estimate task complexity for routing."""
        # Simple heuristic based on inputs
        input_size = len(str(request.inputs))

        if input_size > 10000:
            return RouterComplexity.HIGH
        elif input_size > 1000:
            return RouterComplexity.MEDIUM
        return RouterComplexity.LOW

    def _record_outcome(
        self,
        result: SkillExecutionResult,
        skill: SkillDefinition
    ) -> None:
        """Record outcome for learning."""
        if result.status == ExecutionStatus.COMPLETED:
            outcome = PatternOutcome.SUCCESS
        elif result.status == ExecutionStatus.FAILED:
            outcome = PatternOutcome.FAILURE
        else:
            outcome = PatternOutcome.PARTIAL

        self.repository.learn_model_pattern(
            task_context=f"skill:{skill.name}:{result.capability}",
            model_used=result.model_used or "unknown",
            outcome=outcome,
            total_cost_usd=result.cost_usd,
            total_latency_ms=result.latency_ms,
            tokens_used=result.tokens_used
        )


# =============================================================================
# SKILL ORCHESTRATOR
# =============================================================================

class SkillOrchestrator:
    """
    Main orchestrator for coordinating skills.

    Responsibilities:
    1. Task analysis and skill selection
    2. Context assembly from knowledge
    3. Multi-skill execution coordination
    4. Result aggregation and learning
    """

    def __init__(
        self,
        repository: Optional["KnowledgeRepository"] = None,
        router: Optional["ModelRouter"] = None,
        budget_manager: Optional["ContextBudgetManager"] = None
    ):
        """
        Initialize the skill orchestrator.

        Args:
            repository: Knowledge repository for context
            router: Model router for selection
            budget_manager: Context budget manager
        """
        # Handle case where dependencies are not available
        if KnowledgeRepository is not None:
            self.repository = repository or KnowledgeRepository()
        else:
            self.repository = repository

        if ModelRouter is not None and self.repository is not None:
            self.router = router or ModelRouter(repository=self.repository)
        else:
            self.router = router

        if ContextBudgetManager is not None:
            self.budget_manager = budget_manager or ContextBudgetManager()
        else:
            self.budget_manager = budget_manager

        self.registry = SkillRegistry()
        self.executor = SkillExecutor(repository=self.repository, router=self.router)

        # Register built-in skills
        self._register_builtin_skills()

    def _register_builtin_skills(self) -> None:
        """Register built-in skill definitions."""
        # Knowledge Repository skill
        self.registry.register(SkillDefinition(
            name="knowledge_repository",
            description="LEARN-RECALL-RELATE-REFLECT operations on persistent memory",
            category=SkillCategory.KNOWLEDGE,
            capabilities=[
                SkillCapability(
                    name="learn",
                    description="Store new knowledge",
                    input_schema={"type": "object", "properties": {"content": {"type": "string"}}},
                    estimated_latency_ms=500
                ),
                SkillCapability(
                    name="recall",
                    description="Retrieve relevant knowledge",
                    input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
                    estimated_latency_ms=1000
                ),
                SkillCapability(
                    name="relate",
                    description="Create entity relationships",
                    estimated_latency_ms=500
                ),
                SkillCapability(
                    name="reflect",
                    description="Synthesize insights from learnings",
                    estimated_latency_ms=3000
                )
            ],
            preferred_models=["claude-sonnet", "gemini-3-flash"],
            tags=["memory", "knowledge", "persistence"]
        ))

        # Research skill
        self.registry.register(SkillDefinition(
            name="research",
            description="Research and information gathering",
            category=SkillCategory.RESEARCH,
            capabilities=["search", "summarize", "synthesize"],
            preferred_models=["gemini-3-pro", "deep-research"],
            tags=["research", "search", "analysis"]
        ))

        # Code Analysis skill
        self.registry.register(SkillDefinition(
            name="code_analysis",
            description="Code review and analysis",
            category=SkillCategory.CODE,
            capabilities=["review", "explain", "suggest", "security_scan"],
            preferred_models=["claude-opus", "claude-sonnet"],
            min_context_window=100000,
            tags=["code", "review", "analysis"]
        ))

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def register_skill(self, skill: SkillDefinition) -> None:
        """Register a skill."""
        self.registry.register(skill)

    def register_handler(self, skill_name: str, handler: Callable) -> None:
        """Register a handler for a skill."""
        self.executor.register_handler(skill_name, handler)

    def get_skill(self, name: str) -> Optional[SkillDefinition]:
        """Get a skill definition."""
        return self.registry.get(name)

    def list_skills(self) -> List[SkillDefinition]:
        """List all active skills."""
        return self.registry.list_all()

    def list_capabilities(self) -> List[str]:
        """List all available capabilities."""
        return self.registry.list_capabilities()

    def find_skills_for_capability(self, capability: str) -> List[SkillDefinition]:
        """Find skills that can provide a capability."""
        return self.registry.find_by_capability(capability)

    # =========================================================================
    # ORCHESTRATION
    # =========================================================================

    def plan(
        self,
        task: str,
        capabilities_needed: Optional[List[str]] = None,
        user_id: str = "default",
        max_skills: int = 5
    ) -> OrchestrationPlan:
        """
        Create an orchestration plan for a task.

        Args:
            task: Task description
            capabilities_needed: Specific capabilities required
            user_id: User ID for preferences
            max_skills: Maximum number of skills to use

        Returns:
            Orchestration plan
        """
        plan_id = str(uuid.uuid4())[:8]
        steps = []
        total_latency = 0
        total_cost = 0.0

        # Determine capabilities needed
        if not capabilities_needed:
            capabilities_needed = self._infer_capabilities(task)

        # Select skills for capabilities
        selected_skills = []
        for cap in capabilities_needed[:max_skills]:
            skills = self.registry.find_by_capability(cap)
            if skills:
                # Select best skill (first active one)
                skill = next((s for s in skills if s.status == SkillStatus.ACTIVE), None)
                if skill and skill not in selected_skills:
                    selected_skills.append(skill)
                    steps.append({
                        "skill": skill.name,
                        "capability": cap,
                        "order": len(steps),
                        "parallel": False
                    })
                    total_latency += skill.avg_latency_ms
                    total_cost += skill.avg_cost_usd

        # Get context allocation
        context_allocation = self.budget_manager.allocate_budget(
            base_prompt_tokens=1000,
            task_context=self._infer_task_context(task)
        )

        # Get model decision
        model_decision = self.router.route(
            task=task,
            context=self._infer_task_context(task),
            user_id=user_id
        )

        return OrchestrationPlan(
            plan_id=plan_id,
            task_description=task,
            steps=steps,
            estimated_total_latency_ms=total_latency,
            estimated_total_cost_usd=total_cost,
            context_allocation=context_allocation,
            model_decision=model_decision
        )

    async def execute(
        self,
        task: str,
        context: Optional[str] = None,
        capabilities_needed: Optional[List[str]] = None,
        user_id: str = "default",
        session_id: Optional[str] = None,
        include_context: bool = True
    ) -> OrchestrationResult:
        """
        Execute an orchestrated task.

        Args:
            task: Task description
            context: Optional task context
            capabilities_needed: Required capabilities
            user_id: User ID
            session_id: Session ID for tracking
            include_context: Whether to assemble and inject context

        Returns:
            Orchestration result
        """
        # Create plan
        plan = self.plan(
            task=task,
            capabilities_needed=capabilities_needed,
            user_id=user_id
        )

        # Assemble context if requested
        context_payload = None
        if include_context:
            context_payload = await self._assemble_context(
                task=task,
                allocation=plan.context_allocation,
                user_id=user_id
            )

        # Execute steps
        results = []
        for step in plan.steps:
            skill = self.registry.get(step["skill"])
            if not skill:
                continue

            request = SkillExecutionRequest(
                skill_name=step["skill"],
                capability=step["capability"],
                inputs={"query": task, "task": task},
                user_id=user_id,
                session_id=session_id
            )

            result = await self.executor.execute(
                request=request,
                skill=skill,
                context_payload=context_payload
            )
            results.append(result)

        # Aggregate results
        total_latency = sum(r.latency_ms for r in results)
        total_tokens = sum(r.tokens_used for r in results)
        total_cost = sum(r.cost_usd for r in results)

        # Determine overall status
        if all(r.status == ExecutionStatus.COMPLETED for r in results):
            status = ExecutionStatus.COMPLETED
        elif any(r.status == ExecutionStatus.FAILED for r in results):
            status = ExecutionStatus.FAILED
        else:
            status = ExecutionStatus.COMPLETED

        # Combine outputs
        final_output = self._aggregate_outputs(results)

        return OrchestrationResult(
            plan_id=plan.plan_id,
            status=status,
            skill_results=results,
            final_output=final_output,
            total_latency_ms=total_latency,
            total_tokens_used=total_tokens,
            total_cost_usd=total_cost,
            context_assembled=context_payload,
            patterns_learned=len(results)
        )

    async def execute_single(
        self,
        skill_name: str,
        capability: str,
        inputs: Dict[str, Any],
        user_id: str = "default"
    ) -> SkillExecutionResult:
        """
        Execute a single skill directly.

        Args:
            skill_name: Name of skill to execute
            capability: Capability to invoke
            inputs: Input parameters
            user_id: User ID

        Returns:
            Execution result
        """
        skill = self.registry.get(skill_name)
        if not skill:
            return SkillExecutionResult(
                execution_id="error",
                skill_name=skill_name,
                capability=capability,
                status=ExecutionStatus.FAILED,
                error=f"Skill '{skill_name}' not found"
            )

        request = SkillExecutionRequest(
            skill_name=skill_name,
            capability=capability,
            inputs=inputs,
            user_id=user_id
        )

        return await self.executor.execute(request, skill)

    # =========================================================================
    # CONTEXT ASSEMBLY
    # =========================================================================

    async def _assemble_context(
        self,
        task: str,
        allocation: BudgetAllocation,
        user_id: str
    ) -> ContextPayload:
        """Assemble context from knowledge repository."""
        # Recall relevant knowledge
        episodic = []
        semantic = []
        procedural = []
        graph = []

        # Get recent events
        episodic = self.repository.recall_recent_events(days=7)

        # Get relevant knowledge
        recalled = self.repository.recall(
            query=task,
            memory_types=[MemoryType.SEMANTIC, MemoryType.PROCEDURAL],
            limit=20
        )
        semantic = recalled.get("semantic", [])
        procedural = recalled.get("procedural", [])

        # Get preferences
        preferences = self.repository.recall_preferences()
        procedural.extend(preferences)

        # Pack knowledge
        packed = self.budget_manager.pack_knowledge(
            allocation=allocation,
            episodic_items=episodic,
            semantic_items=semantic,
            procedural_items=procedural,
            graph_items=graph,
            query=task,
            ranking_strategy=RankingStrategy.BALANCED
        )

        # Assemble context
        return self.budget_manager.assemble_context(packed)

    # =========================================================================
    # INFERENCE HELPERS
    # =========================================================================

    def _infer_capabilities(self, task: str) -> List[str]:
        """Infer capabilities needed from task description."""
        task_lower = task.lower()
        capabilities = []

        # Knowledge operations
        if any(word in task_lower for word in ["remember", "learn", "save", "store"]):
            capabilities.append("learn")
        if any(word in task_lower for word in ["find", "search", "recall", "remember", "what", "who"]):
            capabilities.append("recall")
        if any(word in task_lower for word in ["relate", "connect", "link", "relationship"]):
            capabilities.append("relate")
        if any(word in task_lower for word in ["reflect", "analyze", "pattern", "insight"]):
            capabilities.append("reflect")

        # Research
        if any(word in task_lower for word in ["research", "investigate", "explore"]):
            capabilities.append("search")
            capabilities.append("summarize")

        # Code
        if any(word in task_lower for word in ["code", "review", "bug", "fix", "implement"]):
            capabilities.append("review")

        # Default to recall if no specific capability detected
        if not capabilities:
            capabilities = ["recall"]

        return capabilities

    def _infer_task_context(self, task: str) -> str:
        """Infer task context from description."""
        task_lower = task.lower()

        if any(word in task_lower for word in ["code", "review", "bug", "function"]):
            return "code_review"
        if any(word in task_lower for word in ["document", "analyze", "report"]):
            return "document_analysis"
        if any(word in task_lower for word in ["research", "find", "search"]):
            return "research"
        if any(word in task_lower for word in ["voice", "speak", "say"]):
            return "voice_response"

        return "conversation"

    def _aggregate_outputs(self, results: List[SkillExecutionResult]) -> Any:
        """Aggregate outputs from multiple skill executions."""
        if not results:
            return None

        if len(results) == 1:
            return results[0].output

        # Combine outputs
        combined = {
            "skills_executed": len(results),
            "outputs": {}
        }

        for result in results:
            key = f"{result.skill_name}:{result.capability}"
            combined["outputs"][key] = result.output

        return combined


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_orchestrator() -> SkillOrchestrator:
    """Create a default skill orchestrator."""
    return SkillOrchestrator()


async def quick_execute(
    task: str,
    capabilities: Optional[List[str]] = None
) -> OrchestrationResult:
    """Quick execution of a task."""
    orchestrator = create_orchestrator()
    return await orchestrator.execute(task=task, capabilities_needed=capabilities)


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    import sys

    async def main():
        print("Arcus Skill Orchestrator - Test Run")
        print("=" * 50)

        orchestrator = SkillOrchestrator()

        # List registered skills
        print("\n1. Registered Skills:")
        for skill in orchestrator.list_skills():
            caps = [c if isinstance(c, str) else c.name for c in skill.capabilities]
            print(f"   - {skill.name}: {caps}")

        # List capabilities
        print("\n2. Available Capabilities:")
        for cap in orchestrator.list_capabilities():
            skills = orchestrator.find_skills_for_capability(cap)
            skill_names = [s.name for s in skills]
            print(f"   - {cap}: {skill_names}")

        # Create a plan
        print("\n3. Planning Test:")
        plan = orchestrator.plan(
            task="Find all information about user preferences",
            user_id="default"
        )
        print(f"   Plan ID: {plan.plan_id}")
        print(f"   Steps: {len(plan.steps)}")
        print(f"   Est. Latency: {plan.estimated_total_latency_ms}ms")
        for step in plan.steps:
            print(f"     - {step['skill']}.{step['capability']}")

        # Execute
        print("\n4. Execution Test:")
        result = await orchestrator.execute(
            task="Recall user preferences",
            user_id="default"
        )
        print(f"   Status: {result.status.value}")
        print(f"   Skills executed: {len(result.skill_results)}")
        print(f"   Total latency: {result.total_latency_ms}ms")

        for skill_result in result.skill_results:
            print(f"   - {skill_result.skill_name}: {skill_result.status.value}")

        print("\nTest complete!")

    asyncio.run(main())
