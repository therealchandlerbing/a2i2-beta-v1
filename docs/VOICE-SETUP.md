# A2I2 Voice Integration Setup Guide

Complete guide for setting up voice capabilities in the A2I2 platform.

**Primary Voice System**: NVIDIA PersonaPlex (full-duplex, 170ms latency)
**Fallback**: Google Gemini 2.5 Live API (real-time audio with WebSocket)

---

## Table of Contents

1. [Voice Architecture Overview](#voice-architecture-overview)
2. [Phase 1: PersonaPlex Setup (Primary)](#phase-1-personaplex-setup-primary)
3. [Phase 2: Gemini Live API Fallback](#phase-2-gemini-live-api-fallback)
4. [Phase 3: Wake Word Detection](#phase-3-wake-word-detection)
5. [Integration with Knowledge Repository](#integration-with-knowledge-repository)
6. [Alternative Options (Development/Testing)](#alternative-options-developmenttesting)
7. [Deployment Architecture](#deployment-architecture)
8. [Performance Tuning](#performance-tuning)
9. [Troubleshooting](#troubleshooting)

---

## Voice Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    A2I2 VOICE ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   User: "Hey Arcus"                                                      │
│         │                                                                │
│         ▼                                                                │
│   ┌─────────────┐                                                        │
│   │ NanoWakeWord│  On-device wake word detection (<50ms)                │
│   │ (Primary)   │  Apache 2.0 license, customizable                     │
│   └──────┬──────┘                                                        │
│          │                                                               │
│          ▼                                                               │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                     PERSONAPLEX (Primary)                         │   │
│   │                                                                   │   │
│   │   • Full-duplex: listens while speaking                          │   │
│   │   • 170ms turn-taking latency                                    │   │
│   │   • 240ms interruption response                                  │   │
│   │   • Natural backchannels ("uh-huh", "I see", "yeah")            │   │
│   │   • 16 customizable voice presets                                │   │
│   │   • 200 token text prompt for persona                            │   │
│   │                                                                   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│          │                                                               │
│          │ If PersonaPlex unavailable:                                  │
│          ▼                                                               │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                 GEMINI 2.5 LIVE API (Fallback)                    │   │
│   │                                                                   │   │
│   │   • Real-time audio via WebSocket                                │   │
│   │   • Native function calling                                      │   │
│   │   • Search grounding for current info                            │   │
│   │   • ~200-300ms latency                                           │   │
│   │                                                                   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│          │                                                               │
│          ▼                                                               │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    ARCUS GATEWAY                                  │   │
│   │                                                                   │   │
│   │   • Memory context injection (up to 200 tokens for voice)        │   │
│   │   • Episodic memory capture                                      │   │
│   │   • Trust ledger updates                                         │   │
│   │   • VNKG optimization for speech                                 │   │
│   │                                                                   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why PersonaPlex is Primary

| Feature | PersonaPlex | Traditional ASR→LLM→TTS |
|---------|-------------|-------------------------|
| **Full-duplex** | Yes (native) | No (turn-based) |
| **Interruptions** | 240ms response | Not supported |
| **Backchannels** | Natural ("uh-huh", "yeah") | None |
| **Latency** | 170ms | 1-2 seconds |
| **Custom voice** | 16 presets | Depends on TTS |
| **Custom persona** | 200 token prompt | Unlimited |
| **Self-hosted** | Yes (GPU required) | Yes |
| **Open source** | Yes (MIT + NVIDIA license) | Varies |

---

## Phase 1: PersonaPlex Setup (Primary)

### Prerequisites

- **GPU**: 16GB+ VRAM (NVIDIA A10, A100, or RTX 4090)
- **HuggingFace Token**: For model weights access
- **Cloud GPU** (recommended): AWS g5.xlarge, Lambda Labs A10, or RunPod

### Step 1: Accept License and Get Token

1. Go to [huggingface.co/nvidia/personaplex-7b-v1](https://huggingface.co/nvidia/personaplex-7b-v1)
2. Accept the NVIDIA Open Model License
3. Get your HuggingFace token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### Step 2: Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libopus-dev python3-dev

# macOS
brew install opus
```

### Step 3: Clone and Install PersonaPlex

```bash
# Clone the repository
git clone https://github.com/NVIDIA/personaplex
cd personaplex

# Set HuggingFace token
export HF_TOKEN="your-huggingface-token"

# Install dependencies
pip install moshi/.

# For memory-constrained GPUs (enables CPU offload)
pip install accelerate
```

### Step 4: Start the Server

```bash
# Create SSL directory (required for WebSocket)
SSL_DIR=$(mktemp -d)

# Start PersonaPlex server
python -m moshi.server --ssl "$SSL_DIR"

# For GPUs with <24GB VRAM, use CPU offload
python -m moshi.server --ssl "$SSL_DIR" --cpu-offload
```

Server runs at: `https://localhost:8998`

### Step 5: Configure Arcus Voice Persona

Create the Arcus persona configuration:

```python
# arcus_persona_config.py
ARCUS_PERSONA = {
    "voice_embedding": "NATF2",  # Professional female voice (or NATM1 for male)
    "text_prompt": """You are Arcus, the AI companion for Arcus Innovation Studios.

Your core traits:
- Loyal and committed to the team's success
- Proactive in offering relevant information
- Concise but thorough - respect people's time
- Remember past conversations and learn preferences
- Honest, even when the truth is uncomfortable

Communication style:
- Warm but professional
- Use natural backchannels ("got it", "I see", "absolutely")
- Don't over-explain unless asked
- Keep responses under 30 words for voice""",
    "temperature": 0.7
}
```

**Available Voice Presets:**

| Voice | Gender | Best For |
|-------|--------|----------|
| NATF0-NATF3 | Female | Professional, conversational |
| NATM0-NATM3 | Male | Professional, advisory |
| VARF0-VARF4 | Female | Expressive, customer service |
| VARM0-VARM4 | Male | Expressive, entertainment |

**Recommended for Arcus**: `NATF2` or `NATM1`

### Step 6: Environment Variables

Add to `.env.local`:

```bash
# PersonaPlex Configuration
HF_TOKEN="your-huggingface-token"
PERSONAPLEX_URL="wss://localhost:8998"
PERSONAPLEX_VOICE="NATF2"

# Or for cloud deployment
PERSONAPLEX_URL="wss://personaplex.your-server.com:8998"
```

---

## Phase 2: Gemini Live API Fallback

Gemini 2.5 Live API serves as fallback when PersonaPlex is unavailable.

### Step 1: Get Gemini API Key

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create or copy your API key

### Step 2: Configure Gemini Live

Add to `.env.local`:

```bash
# Gemini Live API (Fallback)
GEMINI_API_KEY="AIzaSy..."
GEMINI_LIVE_MODEL="gemini-2.5-flash-native-audio-preview"
```

### Step 3: Implement Fallback Logic

```python
# voice_orchestrator.py
"""
Voice orchestrator with PersonaPlex primary, Gemini Live fallback.
"""
import asyncio
from typing import Optional

class VoiceOrchestrator:
    def __init__(self):
        self.personaplex_url = os.getenv("PERSONAPLEX_URL")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.active_backend = None

    async def connect(self) -> str:
        """Connect to voice backend, with fallback."""
        # Try PersonaPlex first
        if await self._try_personaplex():
            self.active_backend = "personaplex"
            return "personaplex"

        # Fallback to Gemini Live
        if await self._try_gemini_live():
            self.active_backend = "gemini_live"
            return "gemini_live"

        raise ConnectionError("No voice backend available")

    async def _try_personaplex(self) -> bool:
        """Attempt PersonaPlex connection."""
        try:
            # WebSocket connection with 5s timeout
            ws = await asyncio.wait_for(
                websockets.connect(self.personaplex_url),
                timeout=5.0
            )
            await ws.close()
            return True
        except Exception as e:
            print(f"PersonaPlex unavailable: {e}")
            return False

    async def _try_gemini_live(self) -> bool:
        """Attempt Gemini Live connection."""
        try:
            from google import genai
            client = genai.Client(api_key=self.gemini_key)

            # Verify Live API is available by checking model capabilities
            # In production, consider a lightweight test stream
            model = os.getenv("GEMINI_LIVE_MODEL", "gemini-2.5-flash-native-audio-preview")

            # Basic connectivity check - for production, implement actual
            # audio stream test to verify live audio capability
            return client is not None and self.gemini_key is not None
        except Exception as e:
            print(f"Gemini Live unavailable: {e}")
            return False

    async def stream_audio(self, audio_chunk: bytes):
        """Stream audio to active backend."""
        if self.active_backend == "personaplex":
            await self._stream_to_personaplex(audio_chunk)
        elif self.active_backend == "gemini_live":
            await self._stream_to_gemini(audio_chunk)
```

### Gemini Live Configuration

```python
# gemini_live_config.py
"""Gemini Live API configuration for voice fallback."""
from google import genai
from google.genai import types

GEMINI_LIVE_CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO", "TEXT"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Aoede"  # Or: Charon, Fenrir, Kore, Puck
            )
        )
    ),
    system_instruction="""You are Arcus, AI companion for Arcus Innovation Studios.
Keep responses under 30 words. Be concise, warm, and professional."""
)

async def create_gemini_live_session():
    """Create a Gemini Live audio session."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # Use environment variable for model, default to native audio model
    model = os.getenv("GEMINI_LIVE_MODEL", "gemini-2.5-flash-native-audio-preview")

    async with client.aio.live.connect(
        model=model,
        config=GEMINI_LIVE_CONFIG
    ) as session:
        return session
```

---

## Phase 3: Wake Word Detection

### Primary: NanoWakeWord (Open Source)

**Recommended** - Apache 2.0 license, customizable, no ongoing costs.

```bash
# Install NanoWakeWord
pip install nanowakeword>=2.0.0

# Download pre-trained model (or train custom)
python -c "import nanowakeword; nanowakeword.download_model('hey_arcus')"
```

Configure in `.env.local`:
```bash
WAKE_WORD_ENGINE="nanowakeword"
WAKE_WORD_MODEL="hey_arcus"
WAKE_WORD_SENSITIVITY="0.5"
```

See `.claude/skills/knowledge-repository/docs/NANOWAKEWORD-INTEGRATION.md` for full details.

### Alternative: Picovoice Porcupine (Commercial)

For production reliability with custom wake word training.

```bash
# Install Picovoice
pip install pvporcupine

# Get access key from https://console.picovoice.co/
```

Configure:
```bash
PICOVOICE_ACCESS_KEY="your-access-key"
WAKE_WORD_ENGINE="picovoice"
WAKE_WORD_KEYWORD="hey_arcus"  # Custom trained ($100 one-time)
```

### Wake Word Integration

```python
# wakeword_service.py
"""Wake word detection service."""
import nanowakeword

class WakeWordService:
    def __init__(self):
        self.engine = os.getenv("WAKE_WORD_ENGINE", "nanowakeword")
        self.sensitivity = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.5"))

    async def start_listening(self, on_wake: callable):
        """Start listening for wake word."""
        if self.engine == "nanowakeword":
            detector = nanowakeword.WakeWordDetector(
                model=os.getenv("WAKE_WORD_MODEL", "hey_arcus"),
                sensitivity=self.sensitivity
            )
            await detector.start(callback=on_wake)
        elif self.engine == "picovoice":
            # Picovoice Porcupine integration (placeholder)
            # See: https://picovoice.ai/docs/porcupine/
            # Requires PICOVOICE_ACCESS_KEY environment variable
            raise NotImplementedError("Picovoice integration pending - use nanowakeword")
```

---

## Integration with Knowledge Repository

### Context Injection for Voice

PersonaPlex accepts up to 200 tokens of text prompt. Inject relevant context:

```python
# arcus_personaplex_bridge.py
"""Bridge between Arcus Knowledge Repository and PersonaPlex."""
from knowledge_operations import KnowledgeRepository

class ArcusPersonaPlexBridge:
    """Injects Arcus context into PersonaPlex prompts."""

    def __init__(self):
        self.repo = KnowledgeRepository()
        self.base_persona = """You are Arcus, AI companion for Arcus Innovation Studios.
Loyal, proactive, concise. Remember past conversations."""

    def build_context_prompt(self, conversation_topic: str = None) -> str:
        """
        Build context-aware prompt for PersonaPlex.
        Must stay under 200 tokens (~800 characters).
        """
        prompt_parts = [self.base_persona]

        # Get relevant context if topic provided
        if conversation_topic:
            relevant = self.repo.recall(
                query=conversation_topic,
                memory_types=["semantic", "episodic"],
                limit=3
            )

            if relevant.get("semantic"):
                facts = [m["summary"] for m in relevant["semantic"][:2]]
                prompt_parts.append(f"Context: {'; '.join(facts)}")

        # Get user preferences
        prefs = self.repo.recall(
            query="user preferences communication style",
            memory_types=["procedural"],
            limit=1
        )
        if prefs.get("procedural"):
            style = prefs["procedural"][0].get("summary", "")
            if style:
                prompt_parts.append(f"Style: {style}")

        return " ".join(prompt_parts)[:800]  # ~200 tokens
```

### Memory Capture from Voice

```python
# arcus_personaplex_memory.py
"""Captures PersonaPlex conversations to knowledge repository."""
from datetime import datetime
from knowledge_operations import KnowledgeRepository

class PersonaPlexMemoryCapture:
    """Captures voice conversations to Arcus knowledge repo."""

    def __init__(self):
        self.repo = KnowledgeRepository()
        self.current_session = []

    def on_turn_complete(self, user_text: str, ai_text: str):
        """Called after each conversational turn."""
        turn = {
            "timestamp": datetime.now().isoformat(),
            "user": user_text,
            "assistant": ai_text
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
                "backend": "personaplex"  # or "gemini_live"
            }
        })

    def on_session_end(self):
        """Called when conversation session ends."""
        if not self.current_session:
            return

        # Create session summary
        self.repo.learn("semantic", {
            "type": "conversation_summary",
            "session_turns": len(self.current_session),
            "modality": "voice_full_duplex",
            "summary": f"Voice session with {len(self.current_session)} turns"
        })

        self.current_session = []
```

---

## Alternative Options (Development/Testing)

For development or when GPU is unavailable:

### Option A: Cloud Voice (OpenAI)

```bash
# Simple cloud-based STT + TTS
OPENAI_API_KEY="sk-proj-..."
VOICE_MODE="cloud"
VOICE_STT_SERVICE="openai"
VOICE_TTS_SERVICE="openai"
VOICE_TTS_VOICE="nova"
```

**Cost**: ~$6-38/month depending on usage

### Option B: Local Voice (Whisper + Kokoro)

```bash
# Free, offline, no API costs
pip install whisper-cpp-python kokoro-onnx pyaudio

VOICE_MODE="local"
VOICE_STT_SERVICE="whisper"
VOICE_TTS_SERVICE="kokoro"
WHISPER_MODEL="base.en"
```

### Option C: ElevenLabs (Premium TTS)

```bash
# Highest quality voice synthesis
ELEVENLABS_API_KEY="..."
VOICE_TTS_SERVICE="elevenlabs"
ELEVENLABS_VOICE_ID="21m00Tcm4TlvDq8ikWAM"
```

---

## Deployment Architecture

### Production Setup

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION VOICE ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐               │
│   │   Web   │   │  Mobile │   │  Watch  │   │ CarPlay │               │
│   │  App    │   │   App   │   │  App    │   │         │               │
│   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘               │
│        │             │             │             │                      │
│        └─────────────┴──────┬──────┴─────────────┘                      │
│                             │                                            │
│                             ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │               PERSONAPLEX SERVER (Cloud GPU)                      │  │
│   │                                                                   │  │
│   │   Platform: AWS g5.xlarge ($1.01/hr) or Lambda Labs A10 ($0.75/hr) │
│   │   VRAM: 24GB (runs comfortably without CPU offload)              │  │
│   │   Latency: 170ms turn-taking                                     │  │
│   │                                                                   │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                             │                                            │
│                             │ Fallback if unavailable                   │
│                             ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                    GEMINI LIVE API                                │  │
│   │                                                                   │  │
│   │   Model: gemini-2.5-flash-preview                                │  │
│   │   Latency: ~200-300ms                                            │  │
│   │   Cost: Pay-per-use                                              │  │
│   │                                                                   │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                             │                                            │
│                             ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                    ARCUS GATEWAY (Vercel)                         │  │
│   │                                                                   │  │
│   │   • Memory context injection                                     │  │
│   │   • Episodic capture                                             │  │
│   │   • Trust ledger                                                 │  │
│   │                                                                   │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                             │                                            │
│                             ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                    SUPABASE / NEON                                │  │
│   │                                                                   │  │
│   │   • arcus_episodic_memory                                        │  │
│   │   • arcus_semantic_memory                                        │  │
│   │   • arcus_voice_queries                                          │  │
│   │                                                                   │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Cost Estimates

| Component | Low Usage | Moderate | Heavy |
|-----------|-----------|----------|-------|
| **PersonaPlex GPU** (Lambda Labs A10) | $75/mo | $150/mo | $300/mo |
| **Gemini Live** (fallback) | $5/mo | $20/mo | $50/mo |
| **Wake Word** (NanoWakeWord) | $0 | $0 | $0 |
| **Total Voice** | **$80/mo** | **$170/mo** | **$350/mo** |

---

## Performance Tuning

### Latency Targets

| Component | Target | Critical |
|-----------|--------|----------|
| Wake word detection | <50ms | <100ms |
| PersonaPlex turn-taking | <170ms | <300ms |
| PersonaPlex interruption | <240ms | <400ms |
| Gemini Live (fallback) | <300ms | <500ms |
| Total end-to-end | <500ms | <1000ms |

### Optimization Checklist

- [ ] Deploy PersonaPlex geographically close to users
- [ ] Use GPU with sufficient VRAM (24GB+ avoids CPU offload)
- [ ] Enable WebSocket compression
- [ ] Cache context prompts when possible
- [ ] Monitor latency metrics in `arcus_voice_queries` table

### Performance Benchmarks

From NVIDIA's evaluations:

| Metric | PersonaPlex | OpenAI Realtime | Moshi |
|--------|-------------|-----------------|-------|
| Turn-taking latency | 170ms | ~200ms | ~160ms |
| Interruption response | 240ms | ~300ms | ~220ms |
| Voice customization | Yes | Limited | No |
| Role customization | Yes | Yes | No |
| Open source | Yes | No | Yes |

---

## Troubleshooting

### PersonaPlex Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| "Connection refused" | Server not running | Start with `python -m moshi.server` |
| "CUDA out of memory" | Insufficient VRAM | Add `--cpu-offload` flag |
| "Model not found" | HF token issue | Verify `HF_TOKEN` and license acceptance |
| High latency | Network or GPU | Check GPU utilization, network latency |
| Audio distortion | Sample rate mismatch | Ensure 24kHz audio |

### Gemini Live Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| "API key invalid" | Wrong key | Verify `GEMINI_API_KEY` |
| "Quota exceeded" | Rate limit | Implement backoff, upgrade plan |
| "Model unavailable" | Region/model issue | Check model availability |

### Wake Word Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| False positives | Sensitivity too high | Lower `WAKE_WORD_SENSITIVITY` |
| Missed detections | Sensitivity too low | Raise sensitivity |
| High CPU usage | Model too large | Use lighter model |

---

## Quick Reference

### Environment Variables

```bash
# PersonaPlex (Primary)
HF_TOKEN="your-huggingface-token"
PERSONAPLEX_URL="wss://personaplex.your-server.com:8998"
PERSONAPLEX_VOICE="NATF2"

# Gemini Live (Fallback)
GEMINI_API_KEY="AIzaSy..."
GEMINI_LIVE_MODEL="gemini-2.5-flash-native-audio-preview"

# Wake Word
WAKE_WORD_ENGINE="nanowakeword"
WAKE_WORD_MODEL="hey_arcus"
WAKE_WORD_SENSITIVITY="0.5"
```

### Key Files

| Purpose | Path |
|---------|------|
| PersonaPlex Guide | `.claude/skills/knowledge-repository/docs/PERSONAPLEX-INTEGRATION.md` |
| Voice Architecture | `.claude/skills/knowledge-repository/docs/VOICE-ARCHITECTURE.md` |
| NanoWakeWord Guide | `.claude/skills/knowledge-repository/docs/NANOWAKEWORD-INTEGRATION.md` |
| Gemini Integration | `.claude/skills/knowledge-repository/docs/GEMINI-INTEGRATION.md` |
| MCP Voice Config | `.claude/skills/knowledge-repository/config/mcp-voice-config.json` |

---

## References

- **PersonaPlex**: [github.com/NVIDIA/personaplex](https://github.com/NVIDIA/personaplex)
- **HuggingFace Model**: [huggingface.co/nvidia/personaplex-7b-v1](https://huggingface.co/nvidia/personaplex-7b-v1)
- **Gemini Live API**: [ai.google.dev/gemini-api/docs/live](https://ai.google.dev/gemini-api/docs/live)
- **NanoWakeWord**: [github.com/kahrendt/NanoWakeWord](https://github.com/kahrendt/NanoWakeWord)

---

**Last Updated**: 2026-01-27
