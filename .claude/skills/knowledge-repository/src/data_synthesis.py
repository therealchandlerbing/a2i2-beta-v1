"""
Arcus Data Synthesis - Synthetic Training Data Generation

This module generates synthetic training and evaluation data for:
1. Skill sequence optimization
2. Model routing validation
3. Context budgeting tuning
4. Reward signal calibration

Inspired by ToolScale's approach to synthetic data generation.

Implements the "Synthetic Data Generation" enhancement from Phase 3.

Usage:
    from data_synthesis import DataSynthesizer, DomainDefinition

    synthesizer = DataSynthesizer()

    # Define a domain
    domain = DomainDefinition(
        name="client_management",
        skills=["recall", "relate", "research"],
        entities=["TechCorp", "Acme Inc", "GlobalTech"]
    )

    # Generate synthetic tasks
    tasks = synthesizer.generate_tasks(domain, count=100)

    # Generate evaluation dataset
    dataset = synthesizer.create_evaluation_dataset(domains=[domain])
"""

import random
import uuid
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum


# =============================================================================
# CONSTANTS
# =============================================================================

# Task complexity levels
COMPLEXITY_LEVELS = ["simple", "moderate", "complex", "expert"]

# Default entity pools
DEFAULT_PEOPLE = [
    "Sarah Chen", "James Miller", "Emily Rodriguez", "Michael Kim",
    "Jessica Taylor", "David Lee", "Amanda Wilson", "Christopher Brown"
]

DEFAULT_ORGANIZATIONS = [
    "TechCorp", "Acme Industries", "GlobalTech Solutions", "Nexus Consulting",
    "Pinnacle Systems", "Velocity Partners", "Horizon Labs", "Summit Group"
]

DEFAULT_PROJECTS = [
    "Q1 Strategy Review", "Product Launch", "System Migration",
    "Client Onboarding", "Annual Report", "Partnership Proposal",
    "Budget Planning", "Security Audit"
]

DEFAULT_TOPICS = [
    "quarterly performance", "project timeline", "budget allocation",
    "team resources", "client feedback", "technical requirements",
    "market analysis", "competitor research"
]


# =============================================================================
# ENUMS
# =============================================================================

class TaskType(Enum):
    RECALL = "recall"           # Simple knowledge retrieval
    ANALYZE = "analyze"         # Analysis and synthesis
    RELATE = "relate"           # Relationship discovery
    RESEARCH = "research"       # Deep research
    SUMMARIZE = "summarize"     # Summarization
    PREDICT = "predict"         # Prediction/recommendation
    COORDINATE = "coordinate"   # Multi-entity coordination


class DatasetType(Enum):
    TRAINING = "training"
    VALIDATION = "validation"
    EVALUATION = "evaluation"
    BENCHMARK = "benchmark"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DomainDefinition:
    """Definition of a domain for task generation."""
    name: str
    description: str = ""
    skills: List[str] = field(default_factory=lambda: ["recall", "relate", "reflect"])
    task_types: List[TaskType] = field(default_factory=lambda: [TaskType.RECALL, TaskType.ANALYZE])
    entities: List[str] = field(default_factory=list)
    entity_types: Dict[str, List[str]] = field(default_factory=dict)
    topics: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    complexity_distribution: Dict[str, float] = field(default_factory=lambda: {
        "simple": 0.3, "moderate": 0.4, "complex": 0.2, "expert": 0.1
    })


@dataclass
class SkillCall:
    """A single skill call in a golden sequence."""
    skill: str
    capability: str
    params: Dict[str, Any] = field(default_factory=dict)
    expected_output_type: str = "any"
    required: bool = True


@dataclass
class SyntheticTask:
    """A synthetic task with ground truth."""
    task_id: str
    domain: str
    task_type: TaskType
    complexity: str
    description: str
    golden_skill_sequence: List[SkillCall]
    expected_output_contains: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "domain": self.domain,
            "task_type": self.task_type.value,
            "complexity": self.complexity,
            "description": self.description,
            "golden_skill_sequence": [
                {
                    "skill": sc.skill,
                    "capability": sc.capability,
                    "params": sc.params,
                    "expected_output_type": sc.expected_output_type,
                    "required": sc.required
                }
                for sc in self.golden_skill_sequence
            ],
            "expected_output_contains": self.expected_output_contains,
            "constraints": self.constraints,
            "metadata": self.metadata
        }


@dataclass
class EvaluationExample:
    """An example in an evaluation dataset."""
    example_id: str
    task: SyntheticTask
    context: Dict[str, Any]
    expected_reward_range: Tuple[float, float]  # (min, max)
    difficulty_score: float  # 0-1
    tags: List[str] = field(default_factory=list)


@dataclass
class EvaluationDataset:
    """A complete evaluation dataset."""
    dataset_id: str
    name: str
    dataset_type: DatasetType
    domains: List[str]
    examples: List[EvaluationExample]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "name": self.name,
            "dataset_type": self.dataset_type.value,
            "domains": self.domains,
            "example_count": len(self.examples),
            "examples": [
                {
                    "example_id": ex.example_id,
                    "task": ex.task.to_dict(),
                    "context": ex.context,
                    "expected_reward_range": ex.expected_reward_range,
                    "difficulty_score": ex.difficulty_score,
                    "tags": ex.tags
                }
                for ex in self.examples
            ],
            "created_at": self.created_at,
            "metadata": self.metadata
        }

    def save(self, filepath: str) -> None:
        """Save dataset to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


# =============================================================================
# TASK TEMPLATES
# =============================================================================

TASK_TEMPLATES = {
    TaskType.RECALL: [
        "What do you know about {entity}?",
        "Find all information about {entity} from the last {time_period}",
        "What are the recent interactions with {entity}?",
        "Recall our preferences for working with {entity}",
        "What decisions have been made regarding {topic}?",
    ],
    TaskType.ANALYZE: [
        "Analyze the relationship between {entity1} and {entity2}",
        "What patterns do you see in our {topic} over the past {time_period}?",
        "Summarize the key insights about {entity}'s {topic}",
        "Compare our approach to {topic} across different {entity_type}s",
        "What are the trends in {topic} that we should be aware of?",
    ],
    TaskType.RELATE: [
        "How is {entity1} connected to {entity2}?",
        "Who are the key stakeholders for {project}?",
        "What projects is {person} involved in?",
        "Map the relationships between all {entity_type}s in {domain}",
        "Find the connection path from {entity1} to {entity2}",
    ],
    TaskType.RESEARCH: [
        "Research {topic} and provide a comprehensive summary",
        "Find the latest information about {entity}'s {topic}",
        "What are the industry best practices for {topic}?",
        "Investigate {entity}'s approach to {topic}",
        "Compile a report on {topic} with recommendations",
    ],
    TaskType.SUMMARIZE: [
        "Summarize all interactions with {entity} this {time_period}",
        "Create a brief on {project} progress",
        "Synthesize our learnings about {topic}",
        "Provide an executive summary of {entity}'s status",
        "Consolidate feedback from {entity_type}s about {topic}",
    ],
    TaskType.PREDICT: [
        "What should we prioritize in our work with {entity}?",
        "Recommend next steps for {project}",
        "Based on past patterns, what approach should we take for {topic}?",
        "Suggest improvements for our {topic} process",
        "What risks should we consider for {project}?",
    ],
    TaskType.COORDINATE: [
        "Prepare a briefing for the meeting with {entity}",
        "What context should I have before talking to {person} about {topic}?",
        "Draft an agenda for the {project} review",
        "Compile everything needed for the {entity} presentation",
        "Gather all relevant information for the {topic} discussion",
    ],
}

# Skill sequences for each task type
SKILL_SEQUENCES = {
    TaskType.RECALL: [
        [SkillCall("knowledge_repository", "recall", {"memory_types": ["semantic", "episodic"]})],
        [
            SkillCall("knowledge_repository", "recall", {"memory_types": ["episodic"]}),
            SkillCall("knowledge_repository", "recall", {"memory_types": ["procedural"]})
        ],
    ],
    TaskType.ANALYZE: [
        [
            SkillCall("knowledge_repository", "recall", {}),
            SkillCall("knowledge_repository", "reflect", {"focus_areas": []})
        ],
        [
            SkillCall("knowledge_repository", "recall", {"memory_types": ["episodic", "semantic"]}),
            SkillCall("research", "synthesize", {})
        ],
    ],
    TaskType.RELATE: [
        [SkillCall("knowledge_repository", "relate", {})],
        [
            SkillCall("knowledge_repository", "recall", {"memory_types": ["graph"]}),
            SkillCall("knowledge_repository", "relate", {})
        ],
    ],
    TaskType.RESEARCH: [
        [
            SkillCall("knowledge_repository", "recall", {}),
            SkillCall("research", "search", {}),
            SkillCall("research", "summarize", {})
        ],
        [
            SkillCall("research", "search", {}),
            SkillCall("research", "synthesize", {}),
            SkillCall("knowledge_repository", "learn", {})
        ],
    ],
    TaskType.SUMMARIZE: [
        [
            SkillCall("knowledge_repository", "recall", {}),
            SkillCall("research", "summarize", {})
        ],
    ],
    TaskType.PREDICT: [
        [
            SkillCall("knowledge_repository", "recall", {}),
            SkillCall("knowledge_repository", "reflect", {}),
        ],
    ],
    TaskType.COORDINATE: [
        [
            SkillCall("knowledge_repository", "recall", {"memory_types": ["episodic", "procedural"]}),
            SkillCall("knowledge_repository", "relate", {}),
            SkillCall("research", "summarize", {})
        ],
    ],
}


# =============================================================================
# DATA SYNTHESIZER
# =============================================================================

class DataSynthesizer:
    """
    Generates synthetic tasks and evaluation datasets.

    Features:
    1. Domain-aware task generation
    2. Complexity-controlled generation
    3. Golden skill sequence attachment
    4. Quality filtering
    5. Evaluation dataset creation
    """

    def __init__(
        self,
        seed: Optional[int] = None,
        default_domains: Optional[List[DomainDefinition]] = None
    ):
        """
        Initialize the data synthesizer.

        Args:
            seed: Random seed for reproducibility
            default_domains: Default domain definitions
        """
        if seed is not None:
            random.seed(seed)

        self.domains = {d.name: d for d in (default_domains or [])}
        self._init_default_domains()

    def _init_default_domains(self) -> None:
        """Initialize default domain definitions."""
        if "client_management" not in self.domains:
            self.domains["client_management"] = DomainDefinition(
                name="client_management",
                description="Managing client relationships and interactions",
                skills=["recall", "relate", "reflect", "research"],
                task_types=[TaskType.RECALL, TaskType.ANALYZE, TaskType.RELATE, TaskType.COORDINATE],
                entity_types={
                    "organization": DEFAULT_ORGANIZATIONS,
                    "person": DEFAULT_PEOPLE,
                    "project": DEFAULT_PROJECTS
                },
                topics=["relationship status", "recent meetings", "project progress", "feedback"]
            )

        if "research" not in self.domains:
            self.domains["research"] = DomainDefinition(
                name="research",
                description="Research and information gathering",
                skills=["research", "recall", "summarize"],
                task_types=[TaskType.RESEARCH, TaskType.SUMMARIZE, TaskType.ANALYZE],
                topics=DEFAULT_TOPICS,
                entity_types={
                    "organization": DEFAULT_ORGANIZATIONS,
                    "topic": DEFAULT_TOPICS
                }
            )

        if "knowledge_management" not in self.domains:
            self.domains["knowledge_management"] = DomainDefinition(
                name="knowledge_management",
                description="Managing organizational knowledge",
                skills=["recall", "learn", "reflect", "relate"],
                task_types=[TaskType.RECALL, TaskType.ANALYZE, TaskType.RELATE],
                topics=["best practices", "lessons learned", "decision history", "patterns"],
                entity_types={
                    "concept": ["workflows", "standards", "preferences", "frameworks"],
                    "person": DEFAULT_PEOPLE
                }
            )

    def add_domain(self, domain: DomainDefinition) -> None:
        """Add a domain definition."""
        self.domains[domain.name] = domain

    def generate_task(
        self,
        domain: Optional[DomainDefinition] = None,
        task_type: Optional[TaskType] = None,
        complexity: Optional[str] = None
    ) -> SyntheticTask:
        """
        Generate a single synthetic task.

        Args:
            domain: Domain definition (uses random if None)
            task_type: Task type (uses random if None)
            complexity: Complexity level (uses distribution if None)

        Returns:
            Generated synthetic task
        """
        # Select domain
        if domain is None:
            domain = random.choice(list(self.domains.values()))

        # Select task type
        if task_type is None:
            task_type = random.choice(domain.task_types)

        # Select complexity
        if complexity is None:
            complexity = self._sample_complexity(domain.complexity_distribution)

        # Generate task description
        description = self._generate_description(domain, task_type)

        # Generate golden skill sequence
        skill_sequence = self._generate_skill_sequence(domain, task_type, complexity)

        # Generate expected outputs
        expected_outputs = self._generate_expected_outputs(domain, task_type, description)

        # Generate constraints based on complexity
        constraints = self._generate_constraints(complexity)

        return SyntheticTask(
            task_id=str(uuid.uuid4())[:8],
            domain=domain.name,
            task_type=task_type,
            complexity=complexity,
            description=description,
            golden_skill_sequence=skill_sequence,
            expected_output_contains=expected_outputs,
            constraints=constraints,
            metadata={
                "generated_at": datetime.utcnow().isoformat(),
                "generator_version": "1.0.0"
            }
        )

    def generate_tasks(
        self,
        domain: Optional[DomainDefinition] = None,
        count: int = 100,
        task_types: Optional[List[TaskType]] = None
    ) -> List[SyntheticTask]:
        """
        Generate multiple synthetic tasks.

        Args:
            domain: Domain to generate for (all domains if None)
            count: Number of tasks to generate
            task_types: Task types to include (all if None)

        Returns:
            List of generated tasks
        """
        tasks = []

        for _ in range(count):
            selected_domain = domain
            if selected_domain is None:
                selected_domain = random.choice(list(self.domains.values()))

            selected_type = None
            if task_types:
                valid_types = [t for t in task_types if t in selected_domain.task_types]
                if valid_types:
                    selected_type = random.choice(valid_types)

            task = self.generate_task(
                domain=selected_domain,
                task_type=selected_type
            )
            tasks.append(task)

        return tasks

    def create_evaluation_dataset(
        self,
        name: str = "eval_dataset",
        domains: Optional[List[DomainDefinition]] = None,
        examples_per_domain: int = 50,
        dataset_type: DatasetType = DatasetType.EVALUATION
    ) -> EvaluationDataset:
        """
        Create a complete evaluation dataset.

        Args:
            name: Dataset name
            domains: Domains to include
            examples_per_domain: Examples per domain
            dataset_type: Type of dataset

        Returns:
            Evaluation dataset
        """
        domains = domains or list(self.domains.values())
        examples = []

        for domain in domains:
            tasks = self.generate_tasks(domain=domain, count=examples_per_domain)

            for task in tasks:
                # Generate context
                context = self._generate_context(domain, task)

                # Calculate difficulty
                difficulty = self._calculate_difficulty(task)

                # Estimate expected reward range
                reward_range = self._estimate_reward_range(task)

                # Generate tags
                tags = self._generate_tags(task)

                example = EvaluationExample(
                    example_id=f"ex-{task.task_id}",
                    task=task,
                    context=context,
                    expected_reward_range=reward_range,
                    difficulty_score=difficulty,
                    tags=tags
                )
                examples.append(example)

        return EvaluationDataset(
            dataset_id=str(uuid.uuid4())[:8],
            name=name,
            dataset_type=dataset_type,
            domains=[d.name for d in domains],
            examples=examples,
            metadata={
                "examples_per_domain": examples_per_domain,
                "total_examples": len(examples)
            }
        )

    def filter_dataset(
        self,
        dataset: EvaluationDataset,
        min_difficulty: float = 0.0,
        max_difficulty: float = 1.0,
        task_types: Optional[List[TaskType]] = None,
        domains: Optional[List[str]] = None
    ) -> EvaluationDataset:
        """
        Filter an evaluation dataset.

        Args:
            dataset: Dataset to filter
            min_difficulty: Minimum difficulty score
            max_difficulty: Maximum difficulty score
            task_types: Task types to include
            domains: Domains to include

        Returns:
            Filtered dataset
        """
        filtered_examples = []

        for example in dataset.examples:
            # Check difficulty
            if not (min_difficulty <= example.difficulty_score <= max_difficulty):
                continue

            # Check task type
            if task_types and example.task.task_type not in task_types:
                continue

            # Check domain
            if domains and example.task.domain not in domains:
                continue

            filtered_examples.append(example)

        return EvaluationDataset(
            dataset_id=f"{dataset.dataset_id}-filtered",
            name=f"{dataset.name} (filtered)",
            dataset_type=dataset.dataset_type,
            domains=domains or dataset.domains,
            examples=filtered_examples,
            metadata={
                **dataset.metadata,
                "filtered": True,
                "original_count": len(dataset.examples),
                "filtered_count": len(filtered_examples)
            }
        )

    # =========================================================================
    # GENERATION HELPERS
    # =========================================================================

    def _sample_complexity(self, distribution: Dict[str, float]) -> str:
        """Sample complexity based on distribution."""
        levels = list(distribution.keys())
        weights = list(distribution.values())
        return random.choices(levels, weights=weights, k=1)[0]

    def _generate_description(self, domain: DomainDefinition, task_type: TaskType) -> str:
        """Generate task description from template."""
        templates = TASK_TEMPLATES.get(task_type, ["Perform task for {entity}"])
        template = random.choice(templates)

        # Fill in template variables
        replacements = {}

        # Entities
        all_entities = []
        for entity_list in domain.entity_types.values():
            all_entities.extend(entity_list)
        if not all_entities:
            all_entities = DEFAULT_ORGANIZATIONS + DEFAULT_PEOPLE

        if "{entity}" in template:
            replacements["entity"] = random.choice(all_entities)
        if "{entity1}" in template:
            replacements["entity1"] = random.choice(all_entities)
        if "{entity2}" in template:
            remaining = [e for e in all_entities if e != replacements.get("entity1")]
            replacements["entity2"] = random.choice(remaining) if remaining else random.choice(all_entities)

        # Entity types
        if "{entity_type}" in template:
            replacements["entity_type"] = random.choice(list(domain.entity_types.keys()) or ["entity"])

        # Topics
        topics = domain.topics or DEFAULT_TOPICS
        if "{topic}" in template:
            replacements["topic"] = random.choice(topics)

        # People and projects
        if "{person}" in template:
            people = domain.entity_types.get("person", DEFAULT_PEOPLE)
            replacements["person"] = random.choice(people)
        if "{project}" in template:
            projects = domain.entity_types.get("project", DEFAULT_PROJECTS)
            replacements["project"] = random.choice(projects)

        # Time periods
        if "{time_period}" in template:
            replacements["time_period"] = random.choice(["week", "month", "quarter", "year"])

        # Domain
        if "{domain}" in template:
            replacements["domain"] = domain.name

        # Apply replacements
        description = template
        for key, value in replacements.items():
            description = description.replace("{" + key + "}", value)

        return description

    def _generate_skill_sequence(
        self,
        domain: DomainDefinition,
        task_type: TaskType,
        complexity: str
    ) -> List[SkillCall]:
        """Generate golden skill sequence."""
        # Get base sequences for task type
        base_sequences = SKILL_SEQUENCES.get(task_type, [
            [SkillCall("knowledge_repository", "recall", {})]
        ])

        sequence = list(random.choice(base_sequences))

        # Add complexity-based modifications
        if complexity in ["complex", "expert"]:
            # Add additional skill calls for complex tasks
            if task_type in [TaskType.ANALYZE, TaskType.RESEARCH]:
                sequence.append(SkillCall("knowledge_repository", "reflect", {}))
            if task_type in [TaskType.COORDINATE, TaskType.SUMMARIZE]:
                sequence.append(SkillCall("research", "synthesize", {}))

        if complexity == "expert":
            # Expert tasks might need learning/storage
            sequence.append(SkillCall("knowledge_repository", "learn", {}, required=False))

        return sequence

    def _generate_expected_outputs(
        self,
        domain: DomainDefinition,
        task_type: TaskType,
        description: str
    ) -> List[str]:
        """Generate expected output indicators."""
        outputs = []

        # Task-type specific outputs
        if task_type == TaskType.RECALL:
            outputs.extend(["found", "retrieved", "information about"])
        elif task_type == TaskType.ANALYZE:
            outputs.extend(["analysis", "pattern", "insight", "trend"])
        elif task_type == TaskType.RELATE:
            outputs.extend(["relationship", "connected", "associated"])
        elif task_type == TaskType.RESEARCH:
            outputs.extend(["research", "findings", "sources", "data"])
        elif task_type == TaskType.SUMMARIZE:
            outputs.extend(["summary", "key points", "overview"])
        elif task_type == TaskType.PREDICT:
            outputs.extend(["recommendation", "suggest", "priority"])
        elif task_type == TaskType.COORDINATE:
            outputs.extend(["prepared", "compiled", "agenda", "context"])

        return outputs

    def _generate_constraints(self, complexity: str) -> Dict[str, Any]:
        """Generate task constraints based on complexity."""
        constraints = {}

        if complexity == "simple":
            constraints["max_skills"] = 2
            constraints["max_latency_ms"] = 5000
        elif complexity == "moderate":
            constraints["max_skills"] = 3
            constraints["max_latency_ms"] = 10000
        elif complexity == "complex":
            constraints["max_skills"] = 5
            constraints["max_latency_ms"] = 20000
            constraints["requires_synthesis"] = True
        elif complexity == "expert":
            constraints["max_skills"] = 8
            constraints["max_latency_ms"] = 30000
            constraints["requires_synthesis"] = True
            constraints["requires_learning"] = True

        return constraints

    def _generate_context(self, domain: DomainDefinition, task: SyntheticTask) -> Dict[str, Any]:
        """Generate context for an evaluation example."""
        return {
            "domain": domain.name,
            "available_skills": domain.skills,
            "available_entities": sum(len(e) for e in domain.entity_types.values()),
            "time_context": datetime.utcnow().isoformat(),
            "user_context": "default"
        }

    def _calculate_difficulty(self, task: SyntheticTask) -> float:
        """Calculate difficulty score for a task."""
        difficulty = 0.0

        # Complexity contribution
        complexity_scores = {"simple": 0.1, "moderate": 0.3, "complex": 0.6, "expert": 0.9}
        difficulty += complexity_scores.get(task.complexity, 0.3) * 0.4

        # Skill sequence length contribution
        seq_length = len(task.golden_skill_sequence)
        difficulty += min(1.0, seq_length / 5) * 0.3

        # Task type contribution
        type_scores = {
            TaskType.RECALL: 0.1,
            TaskType.SUMMARIZE: 0.2,
            TaskType.RELATE: 0.3,
            TaskType.ANALYZE: 0.5,
            TaskType.RESEARCH: 0.6,
            TaskType.PREDICT: 0.7,
            TaskType.COORDINATE: 0.8
        }
        difficulty += type_scores.get(task.task_type, 0.3) * 0.3

        return min(1.0, difficulty)

    def _estimate_reward_range(self, task: SyntheticTask) -> Tuple[float, float]:
        """Estimate expected reward range for a task."""
        base_min = 0.4
        base_max = 0.9

        # Adjust for complexity
        if task.complexity == "simple":
            return (base_min + 0.2, base_max + 0.1)
        elif task.complexity == "moderate":
            return (base_min + 0.1, base_max)
        elif task.complexity == "complex":
            return (base_min, base_max - 0.1)
        else:  # expert
            return (base_min - 0.1, base_max - 0.2)

    def _generate_tags(self, task: SyntheticTask) -> List[str]:
        """Generate tags for a task."""
        tags = [
            task.domain,
            task.task_type.value,
            task.complexity,
            f"skills:{len(task.golden_skill_sequence)}"
        ]
        return tags


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_synthesizer(seed: Optional[int] = None) -> DataSynthesizer:
    """Create a default data synthesizer."""
    return DataSynthesizer(seed=seed)


def generate_quick_dataset(
    count: int = 100,
    domains: Optional[List[str]] = None
) -> EvaluationDataset:
    """
    Generate a quick evaluation dataset.

    Args:
        count: Total number of examples
        domains: Domain names to include

    Returns:
        Evaluation dataset
    """
    synthesizer = DataSynthesizer()

    if domains:
        selected_domains = [synthesizer.domains[d] for d in domains if d in synthesizer.domains]
    else:
        selected_domains = list(synthesizer.domains.values())

    examples_per_domain = max(1, count // len(selected_domains))

    return synthesizer.create_evaluation_dataset(
        name="quick_dataset",
        domains=selected_domains,
        examples_per_domain=examples_per_domain
    )


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Arcus Data Synthesis - Test Run")
    print("=" * 50)

    synthesizer = DataSynthesizer(seed=42)

    # Test single task generation
    print("\n1. Single Task Generation:")
    task = synthesizer.generate_task()
    print(f"   Task ID: {task.task_id}")
    print(f"   Domain: {task.domain}")
    print(f"   Type: {task.task_type.value}")
    print(f"   Complexity: {task.complexity}")
    print(f"   Description: {task.description}")
    print(f"   Skill Sequence: {[s.skill + '.' + s.capability for s in task.golden_skill_sequence]}")

    # Test batch generation
    print("\n2. Batch Task Generation:")
    tasks = synthesizer.generate_tasks(count=10)
    print(f"   Generated {len(tasks)} tasks")
    complexity_dist = {}
    for t in tasks:
        complexity_dist[t.complexity] = complexity_dist.get(t.complexity, 0) + 1
    print(f"   Complexity distribution: {complexity_dist}")

    # Test evaluation dataset creation
    print("\n3. Evaluation Dataset Creation:")
    dataset = synthesizer.create_evaluation_dataset(
        name="test_dataset",
        examples_per_domain=20
    )
    print(f"   Dataset ID: {dataset.dataset_id}")
    print(f"   Domains: {dataset.domains}")
    print(f"   Total examples: {len(dataset.examples)}")

    # Test filtering
    print("\n4. Dataset Filtering:")
    filtered = synthesizer.filter_dataset(
        dataset,
        min_difficulty=0.3,
        max_difficulty=0.7
    )
    print(f"   Filtered examples: {len(filtered.examples)} (from {len(dataset.examples)})")

    # Show example difficulty distribution
    print("\n5. Difficulty Distribution:")
    difficulties = [ex.difficulty_score for ex in dataset.examples]
    print(f"   Min: {min(difficulties):.2f}")
    print(f"   Max: {max(difficulties):.2f}")
    print(f"   Avg: {sum(difficulties)/len(difficulties):.2f}")

    print("\nTest complete!")
