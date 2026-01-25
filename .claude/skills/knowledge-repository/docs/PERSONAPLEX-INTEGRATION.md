# NVIDIA PersonaPlex Integration for Arcus

**Status**: Available Now (Released January 2026)
**Model**: personaplex-7b-v1
**License**: MIT (code) / NVIDIA Open Model License (weights)

---

## Why PersonaPlex Changes Everything

PersonaPlex solves the fundamental problem we identified: **you can't have natural conversation AND custom personas** - until now.

| Previous Options | Natural Conversation | Custom Voice | Custom Role |
|-----------------|---------------------|--------------|-------------|
| ASR → LLM → TTS | No (robotic pauses) | Yes | Yes |
| Moshi (original) | Yes (full duplex) | No (fixed) | No (fixed) |
| **PersonaPlex** | **Yes** | **Yes** | **Yes** |

---

## What Makes It Different

### Full Duplex = Listens While Speaking

PersonaPlex doesn't wait for you to finish. It:
- **Hears interruptions** and responds immediately (~240ms)
- **Produces backchannels** ("uh-huh", "oh okay", "yeah") while you talk
- **Handles overlapping speech** naturally
- **Responds in ~170ms** during normal turn-taking

This is what makes R2-D2 feel alive - it doesn't just respond, it *reacts*.

### Hybrid Prompting System

```
┌─────────────────────────────────────────────────────────┐
│                   PERSONA CONTROL                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   VOICE PROMPT (Audio Tokens)                          │
│   ├── Timbre                                           │
│   ├── Speaking style                                   │
│   └── Emotional tone                                   │
│                                                         │
│   TEXT PROMPT (Up to 200 tokens)                       │
│   ├── Role definition                                  │
│   ├── Business context                                 │
│   ├── Behavioral constraints                           │
│   └── Knowledge domain                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    PERSONAPLEX ARCHITECTURE                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   INPUT                      PROCESSING                OUTPUT    │
│   ────────                   ──────────                ──────    │
│                                                                  │
│   [User Audio]               ┌──────────────┐                    │
│        │                     │              │                    │
│        ▼                     │   7B Param   │                    │
│   ┌─────────┐               │  Transformer  │    ┌─────────┐    │
│   │  Mimi   │───────────────▶│              │───▶│  Mimi   │    │
│   │ Encoder │               │   (Helium    │    │ Decoder │    │
│   │ ConvNet │               │   backbone)  │    │ ConvNet │    │
│   │   +     │               │              │    │   +     │    │
│   │Transformer              │   Temporal   │    │Transformer   │
│   └─────────┘               │   + Depth    │    └─────────┘    │
│                              │ Transformers │         │         │
│   [Voice Prompt]────────────▶│              │         ▼         │
│                              │              │    [AI Speech]    │
│   [Text Prompt]─────────────▶│              │                   │
│                              └──────────────┘                   │
│                                                                  │
│   DUAL STREAM: Input & Output processed simultaneously          │
│   LATENCY: 170ms (normal) / 240ms (interruption)               │
│   SAMPLE RATE: 24kHz                                            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Available Voices

PersonaPlex comes with 16 pre-trained voice embeddings:

### Natural Voices (More Conversational)
| Voice | Gender | Best For |
|-------|--------|----------|
| NATF0-NATF3 | Female | Professional assistant, coaching |
| NATM0-NATM3 | Male | Professional assistant, advisory |

### Variety Voices (More Expressive Range)
| Voice | Gender | Best For |
|-------|--------|----------|
| VARF0-VARF4 | Female | Customer service, entertainment |
| VARM0-VARM4 | Male | Customer service, entertainment |

---

## Implementation Guide

### Prerequisites

```bash
# System dependencies
# Ubuntu/Debian
sudo apt-get install libopus-dev

# macOS
brew install opus

# Accept license at https://huggingface.co/nvidia/personaplex-7b-v1
export HF_TOKEN=<YOUR_HUGGINGFACE_TOKEN>
```

### Installation

```bash
# Clone repository
git clone https://github.com/NVIDIA/personaplex
cd personaplex

# Install
pip install moshi/.

# For memory-constrained GPUs
pip install accelerate
```

### Running the Server

```bash
# Create SSL directory and start
SSL_DIR=$(mktemp -d)
python -m moshi.server --ssl "$SSL_DIR"

# With CPU offload for smaller GPUs
python -m moshi.server --ssl "$SSL_DIR" --cpu-offload
```

Access at: `https://localhost:8998`

---

## Arcus Persona Configuration

### Recommended Persona Prompt

```text
You are Arcus, the AI companion for Arcus Innovation Studios.

Your core traits:
- Loyal and committed to the team's success
- Proactive in offering relevant information before asked
- Concise but thorough - respect people's time
- Remember past conversations and learn preferences
- Honest, even when the truth is uncomfortable

Your capabilities:
- Access to team knowledge repository (projects, clients, decisions)
- Can recall past conversations and learned preferences
- Understands company workflows and processes

Communication style:
- Warm but professional
- Use natural backchannels ("got it", "I see", "absolutely")
- Don't over-explain unless asked
- Ask clarifying questions when intent is unclear
```

### Voice Selection for Arcus

**Recommended**: `NATF2` or `NATM1`
- Natural conversational tone
- Professional but warm
- Good backchannel production

---

## Integration with Knowledge Repository

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 ARCUS + PERSONAPLEX INTEGRATION                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌────────────────┐                    ┌──────────────────┐   │
│   │  PersonaPlex   │                    │   Knowledge      │   │
│   │    Server      │◀──── Context ─────│   Repository     │   │
│   │  (localhost:   │                    │   (Supabase)     │   │
│   │    8998)       │                    │                  │   │
│   └───────┬────────┘                    └────────┬─────────┘   │
│           │                                      │              │
│           │  Full Duplex                         │ Vector       │
│           │  Audio Stream                        │ Search       │
│           │                                      │              │
│   ┌───────▼────────┐                    ┌────────▼─────────┐   │
│   │    Context     │                    │    Memory        │   │
│   │    Injector    │◀───────────────────│    Retrieval     │   │
│   │   (Pre-prompt) │                    │    (RAG)         │   │
│   └────────────────┘                    └──────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Context Injection Approach

Since PersonaPlex uses text prompts (up to 200 tokens), we inject relevant context:

```python
# arcus_personaplex_bridge.py
"""
Bridge between Arcus Knowledge Repository and PersonaPlex.
"""
from knowledge_operations import KnowledgeRepository

class ArcusPersonaPlexBridge:
    """Injects Arcus context into PersonaPlex prompts."""

    def __init__(self):
        self.repo = KnowledgeRepository()
        self.base_persona = """You are Arcus, the AI companion for Arcus Innovation Studios.
You are loyal, proactive, concise, and remember past conversations."""

    def build_context_prompt(self, conversation_topic: str = None) -> str:
        """
        Build a context-aware prompt for PersonaPlex.
        Must stay under 200 tokens.
        """
        prompt_parts = [self.base_persona]

        # Get recent context
        if conversation_topic:
            relevant = self.repo.recall(
                query=conversation_topic,
                memory_types=["semantic", "episodic"],
                limit=3
            )

            if relevant.get("semantic"):
                # Add key facts
                facts = [m["summary"] for m in relevant["semantic"][:2]]
                prompt_parts.append(f"Relevant context: {'; '.join(facts)}")

        # Get user preferences
        prefs = self.repo.recall(
            query="user preferences communication style",
            memory_types=["procedural"],
            limit=1
        )
        if prefs.get("procedural"):
            style = prefs["procedural"][0].get("summary", "")
            if style:
                prompt_parts.append(f"Style note: {style}")

        return " ".join(prompt_parts)[:800]  # ~200 tokens

    def get_voice_embedding(self) -> str:
        """Get configured voice for Arcus."""
        # Could be stored in preferences
        return "NATF2.pt"  # Default: professional female voice
```

### Conversation Memory Capture

```python
# arcus_personaplex_memory.py
"""
Captures PersonaPlex conversations to knowledge repository.
"""
import json
from datetime import datetime
from knowledge_operations import KnowledgeRepository

class PersonaPlexMemoryCapture:
    """Captures voice conversations to Arcus knowledge repo."""

    def __init__(self):
        self.repo = KnowledgeRepository()
        self.current_session = []

    def on_turn_complete(self, user_audio_path: str, user_text: str,
                         ai_audio_path: str, ai_text: str):
        """Called after each conversational turn."""

        turn = {
            "timestamp": datetime.now().isoformat(),
            "user": {"text": user_text, "audio": user_audio_path},
            "assistant": {"text": ai_text, "audio": ai_audio_path}
        }
        self.current_session.append(turn)

        # Store episodic memory
        self.repo.learn("episodic", {
            "type": "voice_conversation",
            "user_input": user_text,
            "assistant_response": ai_text,
            "modality": "voice_full_duplex",
            "timestamp": turn["timestamp"],
            "context": {
                "session_type": "personaplex",
                "had_interruption": False,  # Could detect from timing
                "had_backchannels": True
            }
        })

    def on_session_end(self):
        """Called when conversation session ends."""
        if not self.current_session:
            return

        # Create session summary
        all_text = " ".join([
            t["user"]["text"] + " " + t["assistant"]["text"]
            for t in self.current_session
        ])

        # Extract key topics (simplified - could use LLM)
        self.repo.learn("semantic", {
            "type": "conversation_summary",
            "session_turns": len(self.current_session),
            "modality": "voice_full_duplex",
            "summary": f"Voice session with {len(self.current_session)} turns",
            "full_transcript": all_text[:2000]  # Truncate for storage
        })

        self.current_session = []
```

---

## Deployment Options

### Option 1: Local Server (Development)

```bash
# Requires GPU with ~16GB VRAM (or use --cpu-offload)
python -m moshi.server --ssl "$SSL_DIR" --cpu-offload
```

**Pros**: Full control, no API costs
**Cons**: Requires GPU, self-managed

### Option 2: Cloud GPU Instance

```bash
# Example: AWS g5.xlarge ($1.01/hr) or Lambda Labs A10 ($0.75/hr)
# 24GB VRAM - runs PersonaPlex comfortably

# SSH to instance, then:
git clone https://github.com/NVIDIA/personaplex
cd personaplex && pip install moshi/.
python -m moshi.server --ssl /tmp/ssl --host 0.0.0.0
```

**Pros**: Scale on demand, no local GPU needed
**Cons**: Latency to cloud, ongoing costs

### Option 3: Hybrid with Pipecat

Use PersonaPlex as the speech model within a Pipecat pipeline:

```python
# arcus_pipecat_personaplex.py
"""
Pipecat pipeline using PersonaPlex for full-duplex voice.
"""
from pipecat.pipeline.pipeline import Pipeline
from pipecat.transports.websocket import WebSocketTransport

# Custom PersonaPlex processor
class PersonaPlexProcessor:
    """Wraps PersonaPlex for use in Pipecat pipeline."""

    def __init__(self, server_url="wss://localhost:8998"):
        self.server_url = server_url
        # WebSocket connection to PersonaPlex server

    async def process_audio(self, audio_chunk):
        """Send audio to PersonaPlex, receive response."""
        # Full duplex - can send and receive simultaneously
        pass

# Pipeline that adds memory layer around PersonaPlex
pipeline = Pipeline([
    WebSocketTransport(),           # Client connection
    ArcusContextInjector(),         # Inject knowledge repo context
    PersonaPlexProcessor(),          # Full duplex voice
    ArcusMemoryCapture(),           # Capture to knowledge repo
])
```

---

## Performance Benchmarks

From NVIDIA's evaluations:

| Metric | PersonaPlex | OpenAI Realtime | Moshi |
|--------|-------------|-----------------|-------|
| Turn-taking latency | 170ms | ~200ms | ~160ms |
| Interruption response | 240ms | ~300ms | ~220ms |
| Voice customization | Yes | Limited | No |
| Role customization | Yes | Yes | No |
| Backchannel quality | Excellent | Good | Good |
| Open source | Yes | No | Yes |

---

## Comparison: PersonaPlex vs Other Options

| Feature | PersonaPlex | Pipecat + Claude | OpenAI Realtime |
|---------|-------------|------------------|-----------------|
| Full duplex | Native | Via transport | Native |
| Custom voice | 16 presets | Any TTS | Limited |
| Custom role | 200 token prompt | Unlimited | Unlimited |
| Memory integration | Manual | Via mem0 | Manual |
| Self-hostable | Yes | Yes | No |
| Latency | 170ms | 300-500ms | 200ms |
| Cost | GPU cost only | Per-API-call | $0.06/min |
| Open weights | Yes | N/A | No |

### When to Use PersonaPlex

**Use PersonaPlex when you need:**
- True full-duplex (interruptions, backchannels)
- Sub-200ms latency
- Self-hosted solution
- Fixed persona with consistent voice

**Use Pipecat + Claude when you need:**
- Unlimited context window
- Complex reasoning
- Tool use / function calling
- Variable personas per session

**Ideal: Hybrid Architecture**
- PersonaPlex for real-time voice layer
- Claude for reasoning and tool execution
- Knowledge Repository for persistent memory

---

## Next Steps for Arcus

1. **Deploy PersonaPlex server** on cloud GPU
2. **Create Arcus persona configuration** with optimal voice/prompt
3. **Build context injection bridge** to knowledge repository
4. **Implement memory capture** for voice conversations
5. **Test backchannel and interruption handling** with team

---

## Resources

- **GitHub**: https://github.com/NVIDIA/personaplex
- **Hugging Face**: https://huggingface.co/nvidia/personaplex-7b-v1
- **Research Page**: https://research.nvidia.com/labs/adlr/personaplex/
- **Paper**: https://research.nvidia.com/labs/adlr/files/personaplex/personaplex_preprint.pdf
- **MarkTechPost Analysis**: https://www.marktechpost.com/2026/01/17/nvidia-releases-personaplex-7b-v1-a-real-time-speech-to-speech-model-designed-for-natural-and-full-duplex-conversations/

---

*Document created: January 24, 2026*
*Status: Ready for implementation*
