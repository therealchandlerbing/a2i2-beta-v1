# Google Gemini Integration for Arcus

**Status**: Available Now (Preview - January 2026)
**Models**: Gemini 3 Pro, Gemini 3 Flash, Gemini 2.5 Pro, Gemini 2.5 Flash
**License**: Google AI API Terms of Service

---

## Why Gemini Integration Supercharges A2I2

Gemini brings **state-of-the-art multimodal understanding** to A2I2, enabling deeper knowledge integration through advanced reasoning, native image generation, and massive context windows. Combined with Claude's capabilities, A2I2 becomes a truly multi-model intelligent platform.

| Capability | Claude | Gemini 3 Pro | Combined Power |
|:-----------|:------:|:------------:|:---------------|
| Long-form reasoning | Excellent | Excellent | Choose best for task |
| Multimodal (vision) | Good | **Excellent** | Gemini for complex vision |
| Image generation | No | **Yes** | Gemini generates visuals |
| Context window | 200K | **1M tokens** | Gemini for massive context |
| Real-time grounding | No | **Yes** | Gemini for current info |
| Code execution | No | **Yes** | Gemini runs code safely |
| Structured output | Yes | **Yes** | Both support JSON schemas |

---

## What Makes Gemini 3 Different

### The Most Intelligent Model Family

Gemini 3 is Google's most intelligent model family, built on **state-of-the-art reasoning** capabilities:

```
+--------------------------------------------------------------------------------+
|                         GEMINI 3 ARCHITECTURE                                   |
+--------------------------------------------------------------------------------+
|                                                                                 |
|   INPUTS                           PROCESSING                      OUTPUTS      |
|   ------                           ----------                      -------      |
|                                                                                 |
|   [Text]          --+                                                           |
|                     |           +----------------------+                        |
|   [Images]        --+           |                      |                        |
|                     |           |   MULTIMODAL         |         [Text]         |
|   [Video]         --+---------->|   TRANSFORMER        |-------> [Images]       |
|                     |           |                      |         [Structured]   |
|   [Audio]         --+           |   - Dynamic Thinking |                        |
|                     |           |   - Grounded Search  |                        |
|   [PDF]           --+           |   - Code Execution   |                        |
|                                 |   - Function Calling |                        |
|                                 +----------------------+                        |
|                                                                                 |
|   TOKEN CAPACITY: 1M input / 64K output                                        |
|   THINKING: Dynamic reasoning with configurable depth                          |
|   KNOWLEDGE: Cutoff January 2025 + real-time grounding                         |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Dynamic Thinking

Gemini 3 introduces **thinking levels** that control reasoning depth:

| Level | Description | Best For |
|:------|:------------|:---------|
| `low` | Minimize latency | Simple tasks, chat, high-throughput |
| `medium` | Balanced (Flash only) | Most general tasks |
| `high` | Maximum reasoning | Complex analysis, coding, STEM |
| `minimal` | Near-zero thinking (Flash only) | Ultra-fast responses |

---

## Gemini Model Family Overview

### Gemini 3 Series (Latest)

| Model | Code | Input/Output | Strengths | Pricing |
|:------|:-----|:-------------|:----------|:--------|
| **Gemini 3 Pro** | `gemini-3-pro-preview` | 1M/64K | Most intelligent, agentic tasks, vibe-coding | $2-4/$12-18 per 1M |
| **Gemini 3 Flash** | `gemini-3-flash-preview` | 1M/64K | Pro-level intelligence at Flash speed | $0.50/$3 per 1M |
| **Gemini 3 Pro Image** | `gemini-3-pro-image-preview` | 65K/32K | Highest quality image generation | $2 text/$0.134 image |

### Gemini 2.5 Series (Production Ready)

| Model | Code | Input/Output | Strengths | Pricing |
|:------|:-----|:-------------|:----------|:--------|
| **Gemini 2.5 Pro** | `gemini-2.5-pro` | 1M/64K | Advanced thinking, complex reasoning | Per API pricing |
| **Gemini 2.5 Flash** | `gemini-2.5-flash` | 1M/64K | Best price-performance, large-scale processing | Per API pricing |
| **Gemini 2.5 Flash-Lite** | `gemini-2.5-flash-lite` | 1M/64K | Ultra-fast, cost-efficient | Per API pricing |
| **Gemini 2.5 Flash Image** | `gemini-2.5-flash-image` | 65K/32K | Image generation with Flash | Per API pricing |
| **Gemini 2.5 Flash Live** | `gemini-2.5-flash-native-audio-preview-12-2025` | 131K/8K | Real-time audio, Live API | Per API pricing |
| **Gemini 2.5 Flash TTS** | `gemini-2.5-flash-preview-tts` | 8K/16K | Text-to-speech generation | Per API pricing |

### Capability Matrix

| Capability | 3 Pro | 3 Flash | 3 Pro Image | 2.5 Pro | 2.5 Flash |
|:-----------|:-----:|:-------:|:-----------:|:-------:|:---------:|
| Thinking | Yes | Yes | Yes | Yes | Yes |
| Function Calling | Yes | Yes | No | Yes | Yes |
| Code Execution | Yes | Yes | No | Yes | Yes |
| Search Grounding | Yes | Yes | Yes | Yes | Yes |
| Image Generation | No | No | **Yes** | No | No |
| URL Context | Yes | Yes | No | Yes | Yes |
| Caching | Yes | Yes | No | Yes | Yes |
| Batch API | Yes | Yes | Yes | Yes | Yes |
| Live API | No | No | No | No | No* |
| File Search | Yes | Yes | No | Yes | Yes |

*Live API available via `gemini-2.5-flash-native-audio-preview`

---

## A2I2 + Gemini Architecture

### Multi-Model Intelligence Layer

```
+--------------------------------------------------------------------------------+
|                    A2I2 MULTI-MODEL ARCHITECTURE                                |
+--------------------------------------------------------------------------------+
|                                                                                 |
|   USER INTERFACE                                                                |
|   ==============                                                                |
|                                                                                 |
|   +----------+    +----------+    +----------+    +----------+                 |
|   |  Voice   |    |   Chat   |    |   API    |    | Webhooks |                 |
|   | (Persona |    |  (Web)   |    |  (REST)  |    | (Events) |                 |
|   |   Plex)  |    |          |    |          |    |          |                 |
|   +----+-----+    +----+-----+    +----+-----+    +----+-----+                 |
|        |              |              |              |                           |
|        +------+-------+------+-------+------+------+                           |
|               |                                                                 |
|               v                                                                 |
|   +--------------------------------------------------------------------------------+
|   |                      MODEL ROUTER & ORCHESTRATOR                            |
|   |                                                                             |
|   |   +------------------+    +------------------+    +------------------+      |
|   |   |    CLAUDE        |    |     GEMINI       |    |   PERSONAPLEX    |      |
|   |   |                  |    |                  |    |                  |      |
|   |   | - Extended       |    | - Multimodal     |    | - Real-time      |      |
|   |   |   thinking       |    |   analysis       |    |   voice          |      |
|   |   | - Tool use       |    | - Image gen      |    | - Full duplex    |      |
|   |   | - Nuanced        |    | - Grounded       |    | - 170ms latency  |      |
|   |   |   conversation   |    |   search         |    |                  |      |
|   |   | - Complex        |    | - 1M context     |    |                  |      |
|   |   |   reasoning      |    | - Code exec      |    |                  |      |
|   |   +--------+---------+    +--------+---------+    +--------+---------+      |
|   |            |                       |                       |                |
|   |            +----------+------------+------------+----------+                |
|   |                       |                                                     |
|   +--------------------------------------------------------------------------------+
|                           |                                                     |
|                           v                                                     |
|   +--------------------------------------------------------------------------------+
|   |                        KNOWLEDGE REPOSITORY                                 |
|   |                                                                             |
|   |   +------------+  +------------+  +------------+  +------------+           |
|   |   |  Episodic  |  |  Semantic  |  | Procedural |  | Relational |           |
|   |   |   Memory   |  |   Memory   |  |   Memory   |  |   Graph    |           |
|   |   +------------+  +------------+  +------------+  +------------+           |
|   |                                                                             |
|   +--------------------------------------------------------------------------------+
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Model Selection Logic

A2I2 intelligently routes requests to the optimal model:

```python
# arcus_model_router.py
"""
Model routing logic for A2I2 multi-model architecture.
"""
from typing import Literal

ModelType = Literal["claude", "gemini-3-pro", "gemini-3-flash", "gemini-2.5-pro",
                    "gemini-2.5-flash", "gemini-3-pro-image"]

def select_model(task: dict) -> ModelType:
    """
    Select the optimal model based on task characteristics.

    Args:
        task: Dictionary with task metadata
            - type: "reasoning", "vision", "image_gen", "grounding", "audio"
            - complexity: "low", "medium", "high"
            - context_size: estimated token count
            - latency_requirement: "fast", "normal", "slow_ok"
            - needs_current_info: bool

    Returns:
        Recommended model identifier
    """
    task_type = task.get("type", "reasoning")
    complexity = task.get("complexity", "medium")
    context_size = task.get("context_size", 0)
    latency = task.get("latency_requirement", "normal")
    needs_grounding = task.get("needs_current_info", False)

    # Image generation -> Gemini 3 Pro Image
    if task_type == "image_gen":
        return "gemini-3-pro-image"

    # Real-time grounded search -> Gemini with Search
    if needs_grounding:
        if latency == "fast":
            return "gemini-3-flash"
        return "gemini-3-pro"

    # Large context (>200K tokens) -> Gemini
    if context_size > 200_000:
        if complexity == "high":
            return "gemini-3-pro"
        return "gemini-2.5-flash"

    # Complex multimodal analysis -> Gemini 3 Pro
    if task_type == "vision" and complexity == "high":
        return "gemini-3-pro"

    # High-complexity reasoning -> Claude or Gemini 3 Pro
    if complexity == "high":
        # Claude for nuanced conversation, Gemini for technical/STEM
        if task.get("domain") in ["conversation", "writing", "analysis"]:
            return "claude"
        return "gemini-3-pro"

    # Fast, simple tasks -> Gemini Flash
    if latency == "fast" or complexity == "low":
        return "gemini-2.5-flash"

    # Default: Claude for general conversation
    return "claude"
```

---

## Implementation Guide

### Prerequisites

```bash
# Install Google GenAI SDK
pip install google-genai

# Set API key
export GEMINI_API_KEY="your-api-key"
```

### Basic Integration

#### Python

```python
from google import genai
from google.genai import types

# Initialize client
client = genai.Client()

# Simple text generation
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Analyze the quarterly sales data and identify trends.",
)

print(response.text)
```

#### JavaScript/TypeScript

```typescript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

async function analyze() {
  const response = await ai.models.generateContent({
    model: "gemini-3-pro-preview",
    contents: "Analyze the quarterly sales data and identify trends.",
  });

  console.log(response.text);
}

analyze();
```

### Advanced: Thinking Levels

```python
from google import genai
from google.genai import types

client = genai.Client()

# High thinking for complex analysis
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Analyze this multi-threaded code for race conditions: [code]",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="high")
    ),
)

# Low thinking for simple responses
quick_response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="What's the weather like?",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="low")
    ),
)
```

### Advanced: Search Grounding

```python
from google import genai
from google.genai import types

client = genai.Client()

# Get real-time information with Google Search grounding
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="What are the latest developments in AI regulation in 2026?",
    config=types.GenerateContentConfig(
        tools=[{"google_search": {}}],
    ),
)

print(response.text)
# Response includes grounding metadata with sources
```

### Advanced: Image Generation

```python
from google import genai
from google.genai import types

client = genai.Client()

# Generate high-quality images
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="Generate an infographic showing A2I2's memory architecture",
    config=types.GenerateContentConfig(
        tools=[{"google_search": {}}],  # Ground in real data
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="4K"
        )
    )
)

# Save generated images
for part in response.parts:
    if part.inline_data:
        image = part.as_image()
        image.save('architecture_infographic.png')
```

### Advanced: Multimodal Analysis

```python
from google import genai
from google.genai import types
import base64

client = genai.Client()

# Analyze documents, images, or video
with open("quarterly_report.pdf", "rb") as f:
    pdf_data = base64.b64encode(f.read()).decode()

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[
        types.Content(
            parts=[
                types.Part(text="Analyze this quarterly report and extract key insights."),
                types.Part(
                    inline_data=types.Blob(
                        mime_type="application/pdf",
                        data=base64.b64decode(pdf_data),
                    )
                )
            ]
        )
    ],
)

print(response.text)
```

---

## Integration with A2I2 Knowledge Repository

### Gemini-Powered Knowledge Capture

```python
# arcus_gemini_knowledge.py
"""
Use Gemini's capabilities to enhance A2I2 knowledge operations.
"""
from google import genai
from google.genai import types
from knowledge_operations import KnowledgeRepository

class GeminiKnowledgeEnhancer:
    """Enhance A2I2 knowledge operations with Gemini capabilities."""

    def __init__(self):
        self.client = genai.Client()
        self.repo = KnowledgeRepository()

    def analyze_document_to_memory(self, file_path: str) -> dict:
        """
        Analyze a document and extract knowledge to memory.
        Uses Gemini's 1M context window for large documents.
        """
        with open(file_path, "rb") as f:
            content = f.read()

        # Use Gemini to analyze the document
        response = self.client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=[
                types.Content(
                    parts=[
                        types.Part(text="""Analyze this document and extract:
1. Key facts and information (for semantic memory)
2. Important events and decisions (for episodic memory)
3. Workflows or processes described (for procedural memory)
4. People, organizations, and their relationships (for knowledge graph)

Format as JSON with keys: facts, events, processes, entities"""),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type="application/pdf",
                                data=content,
                            )
                        )
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_level="high")
            ),
        )

        # Parse and store to knowledge repository
        import json
        extracted = json.loads(response.text)

        # Store facts
        for fact in extracted.get("facts", []):
            self.repo.learn("semantic", {
                "type": "document_fact",
                "content": fact,
                "source": file_path,
                "extraction_model": "gemini-3-pro"
            })

        # Store events
        for event in extracted.get("events", []):
            self.repo.learn("episodic", {
                "type": "document_event",
                "content": event,
                "source": file_path
            })

        # Store processes
        for process in extracted.get("processes", []):
            self.repo.learn("procedural", {
                "type": "document_workflow",
                "content": process,
                "source": file_path
            })

        # Create entity relationships
        for entity in extracted.get("entities", []):
            self.repo.relate(
                source_entity=entity.get("name"),
                relationship=entity.get("relationship", "mentioned_in"),
                target_entity=file_path
            )

        return extracted

    def grounded_knowledge_query(self, query: str) -> dict:
        """
        Query knowledge with real-time grounding for current information.
        Combines repository knowledge with live search.
        """
        # First, get relevant context from repository
        repo_context = self.repo.recall(
            query=query,
            memory_types=["semantic", "episodic"],
            limit=5
        )

        # Build context string
        context_parts = []
        for memory_type, memories in repo_context.items():
            for mem in memories:
                context_parts.append(f"[{memory_type}] {mem.get('summary', mem.get('content', ''))}")

        context_str = "\n".join(context_parts) if context_parts else "No relevant internal knowledge found."

        # Query Gemini with grounding
        response = self.client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=f"""Based on this internal knowledge:
{context_str}

And using current information from search, answer: {query}

Clearly distinguish between internal knowledge and new information from search.""",
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                thinking_config=types.ThinkingConfig(thinking_level="high")
            ),
        )

        return {
            "answer": response.text,
            "internal_context": repo_context,
            "grounded": True
        }

    def generate_knowledge_visualization(self, topic: str) -> bytes:
        """
        Generate visual representations of knowledge using Gemini image generation.
        """
        # Get knowledge context
        context = self.repo.recall(
            query=topic,
            memory_types=["semantic", "relational"],
            limit=10
        )

        # Build description for image generation
        entities = [e.get("name", "") for e in context.get("relational", [])]
        facts = [f.get("summary", "") for f in context.get("semantic", [])]

        prompt = f"""Create a professional infographic visualizing:
Topic: {topic}
Key entities: {', '.join(entities[:5])}
Key facts: {'; '.join(facts[:3])}

Style: Modern, clean, business-appropriate with clear hierarchy and connections."""

        response = self.client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                    image_size="2K"
                )
            )
        )

        for part in response.parts:
            if part.inline_data:
                return part.inline_data.data

        return None
```

### Structured Output with Knowledge Schema

```python
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional

# Define knowledge extraction schema
class ExtractedEntity(BaseModel):
    name: str = Field(description="Entity name")
    type: str = Field(description="Entity type: person, organization, project, etc.")
    attributes: dict = Field(description="Key attributes")

class ExtractedRelationship(BaseModel):
    source: str = Field(description="Source entity name")
    relationship: str = Field(description="Relationship type")
    target: str = Field(description="Target entity name")
    confidence: float = Field(description="Confidence score 0-1")

class KnowledgeExtraction(BaseModel):
    entities: List[ExtractedEntity]
    relationships: List[ExtractedRelationship]
    summary: str
    key_facts: List[str]

# Use structured output
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Extract knowledge from this meeting transcript: [transcript]",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema=KnowledgeExtraction.model_json_schema(),
        thinking_config=types.ThinkingConfig(thinking_level="high")
    ),
)

# Parse structured response
extraction = KnowledgeExtraction.model_validate_json(response.text)
print(f"Found {len(extraction.entities)} entities")
print(f"Found {len(extraction.relationships)} relationships")
```

---

## Use Cases for A2I2 + Gemini

### 1. Large Document Analysis

**Scenario**: Analyze a 500-page annual report for board preparation.

```python
# Gemini's 1M context window handles entire documents
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[
        types.Part(text="Extract all financial metrics, risks, and strategic initiatives."),
        types.Part(inline_data=types.Blob(mime_type="application/pdf", data=report_data))
    ],
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="high")
    )
)

# Store extracted knowledge
for insight in parse_insights(response.text):
    repo.learn("semantic", insight)
```

### 2. Real-Time Competitive Intelligence

**Scenario**: Get current information about a competitor before a sales call.

```python
# Use search grounding for current info
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="What are the latest news and developments about CompetitorX in 2026?",
    config=types.GenerateContentConfig(
        tools=[{"google_search": {}}, {"url_context": {}}],
    )
)

# Combine with internal knowledge
internal = repo.recall(query="CompetitorX", memory_types=["semantic", "episodic"])
briefing = f"{response.text}\n\nInternal Notes:\n{format_memories(internal)}"
```

### 3. Visual Knowledge Generation

**Scenario**: Create infographics for presentations automatically.

```python
# Generate architecture diagram
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="""Create a professional diagram showing:
    - A2I2 memory architecture with 5 memory types
    - Data flow between components
    - Integration with external systems
    Style: Modern tech diagram, blue and white color scheme""",
    config=types.GenerateContentConfig(
        image_config=types.ImageConfig(aspect_ratio="16:9", image_size="4K")
    )
)

# Save for presentation
for part in response.parts:
    if part.inline_data:
        part.as_image().save("architecture_diagram.png")
```

### 4. Meeting Video Analysis

**Scenario**: Analyze recorded meetings and extract knowledge.

```python
# Gemini can process video directly
with open("meeting_recording.mp4", "rb") as f:
    video_data = f.read()

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[
        types.Part(text="""Analyze this meeting and extract:
1. Key decisions made
2. Action items and owners
3. Important discussions and context
4. Relationships between participants"""),
        types.Part(inline_data=types.Blob(mime_type="video/mp4", data=video_data))
    ],
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="high")
    )
)

# Store to episodic memory
repo.learn("episodic", {
    "type": "meeting_analysis",
    "content": response.text,
    "source": "meeting_recording.mp4"
})
```

### 5. Code Analysis and Documentation

**Scenario**: Analyze codebase for technical documentation.

```python
# Gemini's code execution can verify understanding
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=f"""Analyze this codebase and:
1. Document the architecture
2. Identify patterns and best practices
3. Find potential issues or improvements
4. Generate API documentation

Code:
{codebase_content}""",
    config=types.GenerateContentConfig(
        tools=[{"code_execution": {}}],
        thinking_config=types.ThinkingConfig(thinking_level="high")
    )
)
```

---

## Performance Comparison

### Model Selection Guide

| Task | Best Model | Why |
|:-----|:-----------|:----|
| Complex reasoning | Claude or Gemini 3 Pro | Both excel, choose by preference |
| Large document analysis | Gemini 3 Pro | 1M context window |
| Image generation | Gemini 3 Pro Image | Only option with generation |
| Real-time information | Gemini 3 Flash | Search grounding + speed |
| Video/audio analysis | Gemini 3 Pro | Native multimodal |
| High-volume processing | Gemini 2.5 Flash | Best price-performance |
| Natural conversation | Claude | More nuanced, empathetic |
| Code analysis | Gemini 3 Pro | Code execution capability |
| Quick responses | Gemini 3 Flash (minimal) | Lowest latency |

### Latency Benchmarks

| Model | Simple Query | Complex Analysis | With Search |
|:------|:-------------|:-----------------|:------------|
| Claude | ~1-2s | ~5-15s | N/A |
| Gemini 3 Pro (high) | ~2-3s | ~10-30s | ~3-5s |
| Gemini 3 Flash (low) | ~0.5-1s | ~2-5s | ~1-2s |
| Gemini 3 Flash (minimal) | ~0.3-0.5s | ~1-2s | ~0.5-1s |

### Cost Comparison (per 1M tokens)

| Model | Input | Output | Notes |
|:------|:------|:-------|:------|
| Claude Sonnet | $3 | $15 | Standard pricing |
| Gemini 3 Pro | $2-4 | $12-18 | Varies by context length |
| Gemini 3 Flash | $0.50 | $3 | Best value for speed |
| Gemini 2.5 Flash | ~$0.10 | ~$0.30 | Ultra-low cost |

---

## Configuration

### Environment Variables

```bash
# Required
export GEMINI_API_KEY="your-api-key"

# Optional: Default model
export GEMINI_DEFAULT_MODEL="gemini-3-flash-preview"

# Optional: Thinking level
export GEMINI_THINKING_LEVEL="high"  # low, medium, high, minimal
```

### Configuration File

See `config/gemini-config.json` for full configuration options.

---

## Thought Signatures (Important)

Gemini 3 uses **Thought Signatures** to maintain reasoning context across API calls. When using function calling or multi-turn conversations:

1. **Function Calling**: Signatures are strictly validated. Always return them.
2. **Chat/Text**: Not strictly validated but recommended for quality.
3. **Image Generation**: Strictly validated for editing workflows.

The official SDKs handle this automatically. If using REST directly, preserve and return `thoughtSignature` fields.

---

## Best Practices

### 1. Model Selection

```python
# Use Flash for simple, high-volume tasks
quick_response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Summarize this paragraph: ...",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="low")
    )
)

# Use Pro for complex analysis
deep_analysis = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Analyze the strategic implications of...",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="high")
    )
)
```

### 2. Keep Temperature at Default

Gemini 3 is optimized for `temperature=1.0`. Changing it may cause looping or degraded performance.

### 3. Use Structured Outputs

```python
# Always use JSON schema for predictable output
config=types.GenerateContentConfig(
    response_mime_type="application/json",
    response_json_schema=YourSchema.model_json_schema(),
)
```

### 4. Leverage Caching for Repeated Context

```python
# Use context caching for large, repeated prompts
# Reduces cost and latency for subsequent calls
```

### 5. Combine Models Strategically

```python
# Use Claude for initial conversation understanding
# Use Gemini for document analysis and grounding
# Use Gemini Image for visualization
# Let A2I2 route automatically based on task
```

---

## Live API (Real-Time Audio/Video)

The Gemini Live API enables **real-time, bidirectional audio and video streaming** for conversational AI applications.

### Live API Architecture

```
+--------------------------------------------------------------------------------+
|                         GEMINI LIVE API ARCHITECTURE                            |
+--------------------------------------------------------------------------------+
|                                                                                 |
|   CLIENT                    WEBSOCKET                      GEMINI LIVE          |
|   ------                    ---------                      -----------          |
|                                                                                 |
|   [Microphone] ──────┐                                                         |
|                      │     ┌──────────────────────┐                            |
|   [Camera]    ──────▶│────▶│  Bi-directional      │────▶ [Gemini Model]        |
|                      │     │  WebSocket Stream    │                            |
|   [Screen]   ───────┘     │                      │                            |
|                            │  - Audio chunks      │◀──── [Audio Response]      |
|   [Speaker]  ◀────────────│  - Video frames      │                            |
|                            │  - Text/JSON         │                            |
|                            └──────────────────────┘                            |
|                                                                                 |
|   FEATURES:                                                                    |
|   - Voice Activity Detection (VAD) for natural turn-taking                     |
|   - Interruption handling (barge-in support)                                   |
|   - Session management with context preservation                               |
|   - Proactive audio for AI-initiated responses                                 |
|   - Affective dialog for emotional awareness                                   |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Live API Models

| Model | Use Case | Features |
|:------|:---------|:---------|
| `gemini-2.5-flash-native-audio-preview` | Real-time voice | Audio generation, VAD, interruption |
| `gemini-2.5-pro-preview-tts` | High-quality TTS | Premium voice quality |
| `gemini-2.5-flash-preview-tts` | Fast TTS | Quick audio synthesis |

### Live API Session Management

```python
from google import genai
from google.genai import types

client = genai.Client()

# Create a Live API session
async with client.aio.live.connect(
    model="gemini-2.5-flash-native-audio-preview",
    config=types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore"  # Available: Aoede, Charon, Fenrir, Kore, Puck, etc.
                )
            )
        ),
        # Enable Voice Activity Detection
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(
                disabled=False,
                start_of_speech_sensitivity="MEDIUM",  # LOW, MEDIUM, HIGH
                end_of_speech_sensitivity="MEDIUM",
                prefix_padding_ms=300,
                silence_duration_ms=1000
            )
        ),
        # Enable proactive audio (AI-initiated speech)
        proactive_audio=types.ProactiveAudio(enabled=True),
        # Enable affective dialog (emotional awareness)
        enable_affective_dialog=True,
    ),
) as session:
    # Send audio data
    await session.send_realtime_input(audio=audio_chunk)

    # Receive responses
    async for response in session.receive():
        if response.audio:
            play_audio(response.audio)
        if response.text:
            print(response.text)
```

### Voice Activity Detection (VAD)

VAD automatically detects when users start and stop speaking:

```python
# Configure VAD sensitivity
realtime_input_config=types.RealtimeInputConfig(
    automatic_activity_detection=types.AutomaticActivityDetection(
        disabled=False,
        # Higher sensitivity = faster detection, more false positives
        start_of_speech_sensitivity="HIGH",
        # Higher sensitivity = shorter pauses trigger end
        end_of_speech_sensitivity="LOW",
        # Padding before speech detection (ms)
        prefix_padding_ms=300,
        # Silence duration to end turn (ms)
        silence_duration_ms=1000
    )
)
```

### Audio Transcription

Get text transcripts of audio input/output:

```python
async with client.aio.live.connect(
    model="gemini-2.5-flash-native-audio-preview",
    config=types.LiveConnectConfig(
        response_modalities=["AUDIO", "TEXT"],
        # Enable input transcription
        input_audio_transcription=types.AudioTranscriptionConfig(
            enabled=True
        ),
        # Enable output transcription
        output_audio_transcription=types.AudioTranscriptionConfig(
            enabled=True
        ),
    ),
) as session:
    async for response in session.receive():
        if response.input_transcription:
            print(f"User said: {response.input_transcription}")
        if response.output_transcription:
            print(f"AI said: {response.output_transcription}")
```

### Session Context & History

Maintain context across session turns:

```python
# Sessions automatically maintain conversation history
# You can also inject context at session start:

async with client.aio.live.connect(
    model="gemini-2.5-flash-native-audio-preview",
    config=types.LiveConnectConfig(
        system_instruction=types.Content(
            parts=[types.Part(text="You are a helpful A2I2 assistant.")]
        ),
        context_window_compression=types.ContextWindowCompression(
            trigger_tokens=100000,
            sliding_window=types.SlidingWindow(target_tokens=50000)
        ),
    ),
) as session:
    # Session maintains full conversation history
    pass
```

---

## Deep Research Agent

The **Deep Research Agent** is an autonomous research system that performs multi-step web research, synthesizes findings, and produces comprehensive reports.

### Deep Research Architecture

```
+--------------------------------------------------------------------------------+
|                       DEEP RESEARCH AGENT WORKFLOW                              |
+--------------------------------------------------------------------------------+
|                                                                                 |
|   [User Query] ──▶ [Research Planning] ──▶ [Web Search Loop] ──▶ [Synthesis]   |
|                                                                                 |
|   ┌─────────────────────────────────────────────────────────────────────────┐  |
|   │                        AUTONOMOUS EXECUTION                              │  |
|   │                                                                         │  |
|   │   1. ANALYZE QUERY                                                      │  |
|   │      └── Understand research objectives                                 │  |
|   │                                                                         │  |
|   │   2. PLAN RESEARCH                                                      │  |
|   │      └── Generate search queries and research strategy                  │  |
|   │                                                                         │  |
|   │   3. EXECUTE SEARCHES (Multiple iterations)                             │  |
|   │      └── Web search → Analyze results → Refine queries → Repeat        │  |
|   │                                                                         │  |
|   │   4. SYNTHESIZE FINDINGS                                                │  |
|   │      └── Combine sources, resolve conflicts, cite evidence              │  |
|   │                                                                         │  |
|   │   5. GENERATE REPORT                                                    │  |
|   │      └── Structured document with citations and recommendations         │  |
|   │                                                                         │  |
|   └─────────────────────────────────────────────────────────────────────────┘  |
|                                                                                 |
|   CAPABILITIES:                                                                |
|   - Up to 60 minutes of autonomous research                                    |
|   - Multiple search iterations with query refinement                           |
|   - Source verification and citation                                           |
|   - Background execution with streaming updates                                |
|   - Multimodal input (text, images, files)                                    |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Using Deep Research

```python
from google import genai
from google.genai import types

client = genai.Client()

# Start a deep research task
job = await client.aio.deep_research.research(
    model="deep-research-pro-preview-12-2025",
    contents="Analyze the competitive landscape of enterprise AI assistants in 2026. Include market leaders, emerging players, key differentiators, and pricing strategies.",
    config=types.DeepResearchConfig(
        # Enable streaming updates during research
        thinking_summaries="auto",  # "auto", "on", or "off"
    )
)

# Poll for completion (can take 5-60 minutes)
while not job.done:
    await asyncio.sleep(30)
    job = await client.aio.deep_research.get(job.name)

    # Check thinking summaries for progress
    if job.thinking_summaries:
        for summary in job.thinking_summaries:
            print(f"Progress: {summary}")

# Get the final report
result = job.result
print(result.report)  # Comprehensive research report
print(result.sources)  # Cited sources with URLs
```

### Background Execution

Deep Research runs asynchronously:

```python
# Start research in background
job = await client.aio.deep_research.research(
    model="deep-research-pro-preview-12-2025",
    contents="Research topic...",
)

print(f"Research job started: {job.name}")

# Do other work while research runs...

# Check status later
job = await client.aio.deep_research.get(job.name)
if job.done:
    print("Research complete!")
    print(job.result.report)
```

### Deep Research for A2I2

```python
class A2I2DeepResearch:
    """Integrate Deep Research with A2I2 knowledge repository."""

    def __init__(self):
        self.client = genai.Client()
        self.repo = KnowledgeRepository()

    async def research_and_store(self, topic: str) -> dict:
        """Run deep research and store findings in knowledge repository."""

        # Get existing context from repository
        existing = self.repo.recall(
            query=topic,
            memory_types=["semantic"],
            limit=5
        )

        context = "\n".join([m.get("summary", "") for m in existing.get("semantic", [])])

        # Run deep research
        job = await self.client.aio.deep_research.research(
            model="deep-research-pro-preview-12-2025",
            contents=f"""Research: {topic}

Existing knowledge to build upon:
{context}

Focus on new information not in our existing knowledge.""",
        )

        # Wait for completion
        while not job.done:
            await asyncio.sleep(30)
            job = await self.client.aio.deep_research.get(job.name)

        # Store findings in knowledge repository
        self.repo.learn("semantic", {
            "type": "deep_research",
            "topic": topic,
            "report": job.result.report,
            "sources": job.result.sources,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "report": job.result.report,
            "sources": job.result.sources,
            "stored": True
        }
```

### Deep Research Pricing

| Task Type | Estimated Cost | Typical Duration |
|:----------|:---------------|:-----------------|
| Simple research | $2-3 | 5-15 minutes |
| Standard research | $3-5 | 15-30 minutes |
| Complex research | $5-10 | 30-60 minutes |

---

## Gemini 2.5 Thinking Budgets

Gemini 2.5 models use **thinking budgets** (token counts) instead of thinking levels:

### Thinking Budget Configuration

```python
from google import genai
from google.genai import types

client = genai.Client()

# Gemini 2.5 uses thinking_budget (token count)
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Solve this complex math problem step by step...",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=8000  # Number of thinking tokens
        )
    )
)
```

### Budget Guidelines

| Thinking Budget | Use Case | Latency Impact |
|:----------------|:---------|:---------------|
| 0-1000 | Simple tasks, quick responses | Minimal |
| 1000-4000 | Standard reasoning | Low |
| 4000-8000 | Complex analysis | Moderate |
| 8000-16000 | Deep reasoning, multi-step problems | Higher |
| 16000+ | Maximum reasoning depth | Significant |

### Comparing Approaches

| Model Family | Configuration | Method |
|:-------------|:--------------|:-------|
| Gemini 3 | `thinking_level="high"` | Qualitative levels |
| Gemini 2.5 | `thinking_budget=8000` | Token counts |

---

## Thought Summaries

Access model reasoning with thought summaries (especially useful for Deep Research and complex tasks):

### Including Thoughts in Responses

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Analyze this complex legal document...",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="high",
            include_thoughts=True  # Include thought process
        )
    )
)

# Access the thinking process
for part in response.candidates[0].content.parts:
    if part.thought:
        print(f"Thinking: {part.text}")
    else:
        print(f"Response: {part.text}")
```

### Thought Summaries in Streaming

```python
async for chunk in client.models.generate_content_stream(
    model="gemini-3-pro-preview",
    contents="Complex analysis task...",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="high",
            include_thoughts=True
        )
    )
):
    for part in chunk.candidates[0].content.parts:
        if part.thought:
            print(f"[Thinking] {part.text}", end="")
        else:
            print(part.text, end="")
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|:------|:------|:---------|
| 400 Error on function calls | Missing thought signature | Use SDK or preserve signatures |
| Looping responses | Temperature modified | Keep temperature at 1.0 |
| Poor reasoning | Wrong thinking level | Use `high` for complex tasks |
| Context exceeded | Document too large | Use media_resolution settings |
| Slow responses | Thinking level too high | Use `low` or `minimal` for simple tasks |

### API Limits

- Rate limits vary by tier
- Context caching available for large repeated contexts
- Batch API available for high-volume processing

---

## Resources

- **Google AI Studio**: https://aistudio.google.com
- **API Documentation**: https://ai.google.dev/gemini-api/docs
- **Gemini Cookbook**: https://github.com/google-gemini/cookbook
- **Pricing**: https://ai.google.dev/gemini-api/docs/pricing
- **Model Deprecations**: https://ai.google.dev/gemini-api/docs/deprecations

---

## Next Steps for A2I2

1. **Configure Gemini API** with your credentials
2. **Set up model routing** in A2I2 configuration
3. **Test document analysis** with large files
4. **Enable search grounding** for real-time intelligence
5. **Integrate image generation** for visual knowledge

---

*Document created: January 25, 2026*
*Status: Ready for implementation*
