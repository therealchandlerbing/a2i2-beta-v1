# Practical Implementation Guide: Arcus Voice Companion

**Status**: Ready to Build
**Target**: Q1 2026 MVP
**Organization**: Arcus Innovation Studios

---

## What We Can Build TODAY

This document focuses exclusively on tools and integrations that exist, work, and can be deployed immediately. No vaporware.

---

## Architecture: Four Tiers of Capability

### Tier 1: Immediate (This Week)
Tools we can configure and use within days.

### Tier 2: Near-Term (2-4 Weeks)
Requires development but uses proven, documented tools.

### Tier 3: Advanced (1-2 Months)
Full voice agent with memory, autonomy, and multi-modal capabilities.

### Tier 4: Full Duplex - The R2-D2 Experience (Available Now!)
**NVIDIA PersonaPlex** - True simultaneous listen/speak with custom personas.
See [PERSONAPLEX-INTEGRATION.md](PERSONAPLEX-INTEGRATION.md) for complete guide.

---

## Tier 1: Immediate Voice Integration

### Option A: VoiceMode MCP Server (Recommended Start)

**What it is**: An MCP server that adds voice input/output to Claude Code
**GitHub**: https://github.com/mbailey/voicemode
**Effort**: 30 minutes to configure

#### Installation

```bash
# Method 1: Claude Code Plugin
claude plugin install voicemode@mbailey

# Method 2: UV Package Manager
uvx voice-mode-install

# Method 3: From source
git clone https://github.com/mbailey/voicemode
cd voicemode
pip install -e .
```

#### Configuration for .mcp.json

Add to your existing `.mcp.json`:

```json
{
  "mcpServers": {
    "voicemode": {
      "command": "uvx",
      "args": ["voice-mcp"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "VOICE_MODE": "cloud"
      }
    }
  }
}
```

#### What You Get
- Talk to Claude Code with your voice
- Claude responds with synthesized speech
- Automatic silence detection
- Works offline with Whisper.cpp + Kokoro TTS

#### Limitations
- Push-to-talk (not full duplex)
- No persistent memory (yet - we'll add this)
- No autonomous actions during conversation

---

### Option B: ElevenLabs MCP Server

**What it is**: Official ElevenLabs MCP integration for high-quality voice
**Source**: https://elevenlabs.io/blog/introducing-elevenlabs-mcp
**Effort**: 1 hour to configure

#### Configuration

```json
{
  "mcpServers": {
    "elevenlabs": {
      "command": "npx",
      "args": ["-y", "@elevenlabs/mcp-server"],
      "env": {
        "ELEVENLABS_API_KEY": "${ELEVENLABS_API_KEY}"
      }
    }
  }
}
```

#### What You Get
- Professional-grade voice synthesis (29+ voices)
- Voice cloning capability
- Outbound calling integration
- Sound effect generation

---

## Tier 2: Voice + Memory Integration

### Connecting VoiceMode to Knowledge Repository

The key insight: **Voice is just another input/output channel**. The real power comes from connecting it to persistent memory.

#### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARCUS VOICE COMPANION                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐  │
│   │  VoiceMode   │────▶│   Claude     │────▶│  Knowledge   │  │
│   │  MCP Server  │◀────│   (Sonnet)   │◀────│  Repository  │  │
│   └──────────────┘     └──────────────┘     └──────────────┘  │
│         │                     │                    │           │
│         │                     │                    │           │
│   ┌─────▼─────┐         ┌────▼────┐         ┌─────▼─────┐    │
│   │ Whisper   │         │  Hooks  │         │ Supabase  │    │
│   │ + Kokoro  │         │ System  │         │ + pgvector│    │
│   └───────────┘         └─────────┘         └───────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Implementation: Voice-Triggered Memory Storage

Create a hook that captures voice conversations:

```json
// .claude/hooks/hooks.json addition
{
  "hooks": [
    {
      "event": "PostToolUse",
      "matcher": {
        "tool_name": "voicemode_*"
      },
      "command": "python3 .claude/skills/knowledge-repository/src/capture_voice_memory.py",
      "run_async": true
    }
  ]
}
```

#### Voice Memory Capture Script

```python
# .claude/skills/knowledge-repository/src/capture_voice_memory.py
"""
Captures voice conversation context and stores in knowledge repository.
"""
import json
import sys
from datetime import datetime
from knowledge_operations import KnowledgeRepository

def capture_voice_interaction(tool_result: dict):
    """Store voice interaction as episodic memory."""
    repo = KnowledgeRepository()

    # Extract conversation context
    user_speech = tool_result.get("user_transcript", "")
    claude_response = tool_result.get("assistant_response", "")

    if not user_speech:
        return

    # Store as episodic memory
    memory = {
        "type": "voice_conversation",
        "user_input": user_speech,
        "assistant_response": claude_response,
        "timestamp": datetime.now().isoformat(),
        "modality": "voice",
        "context": {
            "session_type": "voice",
            "duration_seconds": tool_result.get("duration", 0)
        }
    }

    repo.learn("episodic", memory)

    # Extract and store any entities mentioned
    # (Could integrate with NER here)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        tool_result = json.loads(sys.argv[1])
        capture_voice_interaction(tool_result)
```

---

## Tier 3: Full Voice Agent with Pipecat

### Why Pipecat?

| Feature | VoiceMode MCP | Pipecat |
|---------|---------------|---------|
| Setup complexity | Low | Medium |
| Latency | Good | Excellent |
| Full duplex | No | Yes |
| Custom pipelines | Limited | Unlimited |
| Self-hostable | Partial | Full |
| Claude support | Yes | Yes (via Anthropic plugin) |
| Memory integration | Manual | Built-in (mem0) |

### Pipecat Architecture for Arcus

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ARCUS VOICE AGENT (Pipecat)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     PIPELINE FLOW                            │   │
│  │                                                              │   │
│  │  [Microphone] ──▶ [VAD] ──▶ [Deepgram STT] ──▶ [Claude] ──┐ │   │
│  │                                                             │ │   │
│  │  [Speaker] ◀── [Cartesia TTS] ◀── [Response Filter] ◀──────┘ │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   MEMORY LAYER (mem0)                        │   │
│  │                                                              │   │
│  │  • Conversation history                                      │   │
│  │  • User preferences                                          │   │
│  │  • Entity extraction                                         │   │
│  │  • Context preservation                                      │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              ARCUS KNOWLEDGE REPOSITORY                      │   │
│  │                                                              │   │
│  │  Supabase + pgvector ◀──────────────────────────────────────│   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Pipecat + Claude Implementation

```python
# arcus_voice_agent.py
"""
Full Pipecat voice agent with Arcus knowledge integration.
"""
import asyncio
from pipecat.frames.frames import TextFrame, EndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.services.anthropic import AnthropicLLMService
from pipecat.services.deepgram import DeepgramSTTService, DeepgramTTSService
from pipecat.transports.services.daily import DailyTransport
from pipecat.processors.aggregators.llm_response import LLMResponseAggregator

# Import our knowledge repository
from knowledge_operations import KnowledgeRepository

class ArcusMemoryProcessor:
    """Integrates Arcus knowledge repository with Pipecat."""

    def __init__(self):
        self.repo = KnowledgeRepository()
        self.conversation_buffer = []

    async def process_frame(self, frame):
        """Store conversation turns in knowledge repository."""
        if isinstance(frame, TextFrame):
            self.conversation_buffer.append({
                "role": "user" if frame.is_user else "assistant",
                "content": frame.text,
                "timestamp": frame.timestamp
            })

            # Store every exchange
            if len(self.conversation_buffer) >= 2:
                await self._store_exchange()

    async def _store_exchange(self):
        """Store conversation exchange as episodic memory."""
        exchange = self.conversation_buffer[-2:]
        self.repo.learn("episodic", {
            "type": "voice_conversation",
            "exchange": exchange,
            "modality": "voice"
        })

async def create_arcus_agent():
    """Create the Arcus voice agent pipeline."""

    # Initialize services
    transport = DailyTransport(
        room_url="YOUR_DAILY_ROOM_URL",
        token="YOUR_DAILY_TOKEN",
        bot_name="Arcus"
    )

    stt = DeepgramSTTService(api_key="YOUR_DEEPGRAM_KEY")

    llm = AnthropicLLMService(
        api_key="YOUR_ANTHROPIC_KEY",
        model="claude-sonnet-4-20250514",
        system_prompt="""You are Arcus, an AI companion for Arcus Innovation Studios.

        Your personality:
        - Loyal and committed to the team's success
        - Proactive in offering relevant information
        - Concise but thorough
        - You remember past conversations and learn preferences

        You have access to the team's knowledge repository with:
        - Project history and decisions
        - Client information
        - Workflow preferences
        - Past meeting notes

        Use this context to provide personalized, relevant responses."""
    )

    tts = DeepgramTTSService(
        api_key="YOUR_DEEPGRAM_KEY",
        voice="aura-asteria-en"  # Professional, clear voice
    )

    memory = ArcusMemoryProcessor()

    # Build pipeline
    pipeline = Pipeline([
        transport.input(),
        stt,
        memory,
        llm,
        tts,
        transport.output()
    ])

    return PipelineTask(pipeline)

if __name__ == "__main__":
    asyncio.run(create_arcus_agent())
```

### Required Dependencies

```bash
# Install Pipecat with Anthropic and Deepgram support
pip install "pipecat-ai[anthropic,deepgram,daily]"

# Or with all services
pip install "pipecat-ai[all]"
```

---

## Tier 3 Alternative: LiveKit Agents

### Why Consider LiveKit?

- Powers ChatGPT's Advanced Voice Mode
- Native MCP support
- Built-in turn detection
- Easier phone integration (SIP)

### LiveKit + Claude Implementation

```python
# arcus_livekit_agent.py
"""
LiveKit voice agent with Arcus knowledge integration.
"""
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import anthropic, deepgram, silero

async def entrypoint(ctx: JobContext):
    """LiveKit agent entrypoint."""

    # Connect to room
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Initialize assistant
    assistant = VoiceAssistant(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        llm=anthropic.LLM(model="claude-sonnet-4-20250514"),
        tts=deepgram.TTS(),
        fnc_ctx=ArcusFunctionContext()  # Custom tools
    )

    # Start assistant
    assistant.start(ctx.room)

    # Handle conversation with memory
    @assistant.on("user_speech_committed")
    async def on_user_speech(text: str):
        # Store in Arcus knowledge repository
        from knowledge_operations import KnowledgeRepository
        repo = KnowledgeRepository()
        repo.learn("episodic", {
            "type": "voice_input",
            "content": text,
            "modality": "voice"
        })

class ArcusFunctionContext:
    """Custom tools the voice agent can call."""

    @llm.ai_callable()
    async def recall_context(self, query: str) -> str:
        """Search Arcus knowledge repository for relevant context."""
        from knowledge_operations import KnowledgeRepository
        repo = KnowledgeRepository()
        results = repo.recall(query)
        return str(results)

    @llm.ai_callable()
    async def get_project_status(self, project_name: str) -> str:
        """Get current status of a project."""
        # Integration with Asana, etc.
        pass

    @llm.ai_callable()
    async def schedule_reminder(self, message: str, time: str) -> str:
        """Schedule a reminder for the team."""
        pass

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

---

## Practical Comparison: Which Path to Choose?

### Decision Matrix

| Criterion | VoiceMode MCP | Pipecat | LiveKit |
|-----------|--------------|---------|---------|
| **Setup time** | 30 min | 2-4 hours | 2-4 hours |
| **Cost** | $0 (local) or ~$0.01/min | ~$0.02-0.05/min | ~$0.02-0.05/min |
| **Latency** | 500-800ms | 200-400ms | 200-400ms |
| **Full duplex** | No | Yes | Yes |
| **Phone integration** | No | Yes (Daily) | Yes (SIP) |
| **Memory integration** | Manual | Built-in (mem0) | Manual |
| **MCP native** | Yes | No | Yes |
| **Self-host** | Partial | Full | Full |
| **Best for** | Quick start | Custom pipelines | Production scale |

### Recommended Path for Arcus

**Phase 1 (This Week)**: VoiceMode MCP
- Get voice working immediately
- Add memory hooks manually
- Validate use cases

**Phase 2 (Weeks 2-4)**: Pipecat Migration
- Build custom pipeline
- Integrate mem0 for memory
- Add full duplex support

**Phase 3 (Month 2+)**: Production Hardening
- Consider LiveKit for scale
- Add phone/SIP integration
- Deploy dedicated infrastructure

---

## Service Cost Comparison

### Speech-to-Text Options

| Service | Cost per Hour | Latency | Quality |
|---------|--------------|---------|---------|
| Whisper.cpp (local) | $0 | 300-500ms | Good |
| Deepgram Nova-2 | $0.36 | 100-200ms | Excellent |
| AssemblyAI | $0.37 | 200-300ms | Excellent |
| OpenAI Whisper API | $0.36 | 300-500ms | Good |

### Text-to-Speech Options

| Service | Cost per 1M chars | Latency | Quality |
|---------|------------------|---------|---------|
| Kokoro (local) | $0 | 200-400ms | Good |
| Deepgram Aura | $15 | 100-200ms | Good |
| ElevenLabs | $30-330 | 200-300ms | Excellent |
| Cartesia Sonic | $15 | 50-100ms | Excellent |
| OpenAI TTS | $15-30 | 200-300ms | Good |

### LLM Options

| Service | Cost per 1M tokens | Latency | Quality |
|---------|-------------------|---------|---------|
| Claude Sonnet 4 | $3 in / $15 out | 200-500ms | Excellent |
| Claude Haiku | $0.25 in / $1.25 out | 100-200ms | Good |
| GPT-4o mini | $0.15 in / $0.60 out | 100-200ms | Good |
| Llama 3.3 70B (local) | $0 | Variable | Good |

### Recommended Stack for Arcus (Cost-Optimized)

**Development/Testing**:
- STT: Whisper.cpp (free, local)
- LLM: Claude Haiku (fast, cheap)
- TTS: Kokoro (free, local)
- **Total: ~$0.001/minute**

**Production**:
- STT: Deepgram Nova-2 ($0.006/min)
- LLM: Claude Sonnet 4 (~$0.02/min avg)
- TTS: Cartesia Sonic ($0.005/min)
- **Total: ~$0.03/minute = $1.80/hour**

---

## What Makes This Different From Everyone Else

### 1. Persistent Memory Across All Modalities

Most voice agents are stateless. Ours remembers:
- Every conversation (voice, text, code)
- Learned preferences
- Project context
- Team dynamics

### 2. Knowledge Graph Integration

Not just conversation history - actual semantic understanding:
- Entity relationships (people, projects, decisions)
- Temporal connections (what happened when)
- Causal chains (why decisions were made)

### 3. Autonomy Progression

The system learns what it can do autonomously:
- Level 0: Always asks
- Level 1: Suggests, you confirm
- Level 2: Does routine tasks, reports after
- Level 3: Handles domains independently
- Level 4: Full partnership

### 4. Multi-Agent Coordination

Voice agent is just the interface. Behind it:
- Research agents for deep dives
- Financial agents for analysis
- Design agents for reviews
- All sharing the same knowledge base

### 5. Context That Compounds

Every interaction makes the system smarter:
- Today: "Remind me about the Johnson meeting"
- Month 1: "You usually prepare financial summaries before Johnson meetings"
- Month 6: "I've prepared the Johnson deck based on Q3 results and the pricing discussion from September"

---

## Immediate Next Steps

### Today
1. [ ] Add VoiceMode MCP to `.mcp.json`
2. [ ] Test basic voice conversation
3. [ ] Verify Supabase connection for memory storage

### This Week
1. [ ] Deploy Supabase schema
2. [ ] Test voice → memory capture hook
3. [ ] Create initial voice agent personality prompt

### Next Week
1. [ ] Evaluate Pipecat vs LiveKit for Tier 3
2. [ ] Set up development environment for chosen framework
3. [ ] Build first custom pipeline with memory integration

---

## Appendix: Service Links and Documentation

### Voice Frameworks
- **Pipecat**: https://github.com/pipecat-ai/pipecat
- **LiveKit Agents**: https://github.com/livekit/agents
- **VoiceMode MCP**: https://github.com/mbailey/voicemode
- **NVIDIA Voice Agent Examples**: https://github.com/NVIDIA/voice-agent-examples

### Speech Services
- **Deepgram**: https://developers.deepgram.com/
- **ElevenLabs**: https://elevenlabs.io/docs
- **Cartesia**: https://docs.cartesia.ai/
- **AssemblyAI**: https://www.assemblyai.com/docs

### Local/Self-Hosted Options
- **Whisper.cpp**: https://github.com/ggerganov/whisper.cpp
- **Kokoro TTS**: https://github.com/remsky/Kokoro-FastAPI
- **Piper TTS**: https://github.com/rhasspy/piper

### Memory/Context
- **mem0**: https://github.com/mem0ai/mem0
- **LangChain Memory**: https://python.langchain.com/docs/modules/memory/

---

*Document created: January 2026*
*Last updated: January 24, 2026*
*Status: Ready for implementation*
