# A2I2 Voice Integration Setup Guide

Complete guide for setting up voice capabilities in the A2I2 platform.

---

## Table of Contents

1. [Voice Architecture Overview](#voice-architecture-overview)
2. [Quick Setup Decision Tree](#quick-setup-decision-tree)
3. [Option A: Cloud Voice (OpenAI)](#option-a-cloud-voice-openai)
4. [Option B: Local Voice (Whisper + Kokoro)](#option-b-local-voice-whisper--kokoro)
5. [Option C: Premium Voice (ElevenLabs)](#option-c-premium-voice-elevenlabs)
6. [Option D: Wake Word Detection](#option-d-wake-word-detection)
7. [MCP Server Configuration](#mcp-server-configuration)
8. [Testing Voice Integration](#testing-voice-integration)
9. [Performance Tuning](#performance-tuning)
10. [Troubleshooting](#troubleshooting)

---

## Voice Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    A2I2 Voice Pipeline                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Microphone] → [Wake Word] → [STT] → [Claude] → [TTS] → [Speaker]
│                      │           │         │         │          │
│                      ▼           ▼         ▼         ▼          │
│               NanoWakeWord   Whisper   Knowledge   OpenAI       │
│               or Picovoice   or OpenAI  + Memory   or Kokoro    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Target Latencies:
- Wake word detection: <50ms
- Speech-to-text: <500ms
- LLM processing: <1000ms
- Text-to-speech: <200ms
- Total end-to-end: <2000ms (target: <1500ms)
```

### Component Options

| Component | Cloud Option | Local Option | Premium Option |
|-----------|--------------|--------------|----------------|
| **Wake Word** | - | NanoWakeWord | Picovoice |
| **STT** | OpenAI Whisper API | whisper.cpp | Deepgram |
| **TTS** | OpenAI TTS | Kokoro ONNX | ElevenLabs |
| **Full-duplex** | Gemini Live API | - | NVIDIA PersonaPlex |

---

## Quick Setup Decision Tree

```
Do you need voice features?
├── No → Skip this guide
└── Yes → What's your priority?
    ├── Simplicity → Option A: Cloud (OpenAI)
    ├── Cost/Privacy → Option B: Local (Whisper + Kokoro)
    ├── Voice Quality → Option C: Premium (ElevenLabs)
    └── Wake Word → Option D: Add wake word to any option
```

**Recommended for most users**: Option A (Cloud) for fastest setup.

---

## Option A: Cloud Voice (OpenAI)

**Best for**: Quick setup, reliable quality, moderate cost

### Prerequisites
- OpenAI API key with access to Whisper and TTS APIs
- Internet connection required

### Setup Steps

#### Step 1: Get OpenAI API Key
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create new API key
3. Copy the key (starts with `sk-proj-`)

#### Step 2: Configure Environment

Add to `.env.local`:
```bash
# OpenAI Voice Configuration
OPENAI_API_KEY="sk-proj-your-key-here"

# Voice Settings
VOICE_MODE="cloud"
VOICE_STT_SERVICE="openai"
VOICE_TTS_SERVICE="openai"
VOICE_TTS_VOICE="nova"
```

**Available TTS voices:**
| Voice | Description | Best For |
|-------|-------------|----------|
| `alloy` | Neutral, balanced | General use |
| `echo` | Warm, conversational | Friendly interactions |
| `fable` | Expressive, British | Storytelling |
| `onyx` | Deep, authoritative | Professional |
| `nova` | Friendly, upbeat | Default recommended |
| `shimmer` | Clear, gentle | Calm interactions |

#### Step 3: Install MCP Voice Server

```bash
# Install the voicemode MCP server
pip install voicemode

# Or with uv (faster)
uv pip install voicemode
```

#### Step 4: Configure MCP

The configuration is in `.claude/skills/knowledge-repository/config/mcp-voice-config.json`:

```json
{
  "mcpServers": {
    "voicemode": {
      "command": "uvx",
      "args": ["voicemode"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      }
    }
  }
}
```

### Cost Estimate (OpenAI)

| Service | Rate | 10 min/day | 1 hr/day |
|---------|------|------------|----------|
| Whisper STT | $0.006/min | $1.80/mo | $10.80/mo |
| TTS | $0.015/1K chars | ~$4.50/mo | ~$27/mo |
| **Total** | | **~$6.30/mo** | **~$38/mo** |

---

## Option B: Local Voice (Whisper + Kokoro)

**Best for**: Privacy-conscious, offline use, zero ongoing cost

### Prerequisites
- Python 3.10+
- ~2GB disk space for models
- CPU with AVX2 support (or GPU for faster inference)

### Setup Steps

#### Step 1: Install Whisper.cpp

```bash
# Clone whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# Build
make

# Download model (base.en is good balance of speed/quality)
bash ./models/download-ggml-model.sh base.en

# Test
./main -m models/ggml-base.en.bin -f samples/jfk.wav
```

**Model Options:**
| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| `tiny.en` | 75MB | Fastest | Good |
| `base.en` | 142MB | Fast | Better |
| `small.en` | 466MB | Medium | Great |
| `medium.en` | 1.5GB | Slow | Excellent |

#### Step 2: Install Kokoro TTS

```bash
# Install kokoro-onnx
pip install kokoro-onnx

# Or build from source for better performance
git clone https://github.com/thewh1teagle/kokoro-onnx.git
cd kokoro-onnx
pip install -e .
```

#### Step 3: Install Python Bindings

```bash
pip install whisper-cpp-python kokoro-onnx pyaudio
```

#### Step 4: Configure Environment

Add to `.env.local`:
```bash
# Local Voice Configuration
VOICE_MODE="local"
VOICE_STT_SERVICE="whisper"
VOICE_TTS_SERVICE="kokoro"
WHISPER_MODEL="base.en"
WHISPER_MODEL_PATH="/path/to/whisper.cpp/models/ggml-base.en.bin"
```

#### Step 5: Configure MCP

```json
{
  "mcpServers": {
    "voicemode-local": {
      "command": "python",
      "args": ["-m", "voicemode_local"],
      "env": {
        "WHISPER_MODEL_PATH": "${WHISPER_MODEL_PATH}",
        "VOICE_MODE": "local"
      }
    }
  }
}
```

### Performance Tips (Local)

1. **Use GPU acceleration** (if available):
   ```bash
   # For CUDA
   pip install whisper-cpp-python[cuda]

   # For Metal (Mac)
   CMAKE_ARGS="-DWHISPER_COREML=1" pip install whisper-cpp-python
   ```

2. **Optimize model loading**:
   - Keep model in memory between requests
   - Use memory-mapped files for large models

3. **Reduce latency**:
   - Use `tiny.en` model for fastest response
   - Enable VAD (Voice Activity Detection) to reduce processing

---

## Option C: Premium Voice (ElevenLabs)

**Best for**: Highest quality voice synthesis, custom voices

### Prerequisites
- ElevenLabs account and API key
- OpenAI API key (for STT, or use Deepgram)

### Setup Steps

#### Step 1: Get ElevenLabs API Key
1. Go to [elevenlabs.io](https://elevenlabs.io)
2. Sign up and go to Profile → API Key
3. Copy your API key

#### Step 2: Configure Environment

Add to `.env.local`:
```bash
# ElevenLabs Configuration
ELEVENLABS_API_KEY="your-key-here"

# Combined setup: OpenAI STT + ElevenLabs TTS
OPENAI_API_KEY="sk-proj-..."
VOICE_MODE="cloud"
VOICE_STT_SERVICE="openai"
VOICE_TTS_SERVICE="elevenlabs"

# ElevenLabs voice ID (optional, defaults to Rachel)
ELEVENLABS_VOICE_ID="21m00Tcm4TlvDq8ikWAM"
```

**Popular ElevenLabs Voices:**
| Voice | ID | Description |
|-------|-----|-------------|
| Rachel | `21m00Tcm4TlvDq8ikWAM` | Calm, professional |
| Domi | `AZnzlk1XvdvUeBnXmlld` | Strong, confident |
| Bella | `EXAVITQu4vr4xnSDxMaL` | Soft, friendly |
| Antoni | `ErXwobaYiN019PkySvjV` | Well-rounded male |
| Josh | `TxGEqnHWrfWFTfGW9XjX` | Deep, narrative |

#### Step 3: Install MCP Server

```bash
# Install ElevenLabs MCP
npm install -g @anthropic/mcp-elevenlabs

# Or use npx
npx @anthropic/mcp-elevenlabs
```

#### Step 4: Configure MCP

```json
{
  "mcpServers": {
    "elevenlabs": {
      "command": "npx",
      "args": ["@anthropic/mcp-elevenlabs"],
      "env": {
        "ELEVENLABS_API_KEY": "${ELEVENLABS_API_KEY}"
      }
    }
  }
}
```

### Cost Estimate (ElevenLabs)

| Plan | Characters/mo | Cost | Best For |
|------|---------------|------|----------|
| Free | 10,000 | $0 | Testing |
| Starter | 30,000 | $5/mo | Light use |
| Creator | 100,000 | $22/mo | Regular use |
| Pro | 500,000 | $99/mo | Heavy use |

---

## Option D: Wake Word Detection

Enable hands-free activation with "Hey Arcus" or custom wake words.

### Option D1: NanoWakeWord (Recommended - Open Source)

**Best for**: Free, customizable, Apache 2.0 license

```bash
# Install
pip install nanowakeword>=2.0.0

# Download pre-trained model
python -c "import nanowakeword; nanowakeword.download_model('hey_arcus')"
```

Configure in `.env.local`:
```bash
WAKE_WORD_ENGINE="nanowakeword"
WAKE_WORD_MODEL="hey_arcus"
WAKE_WORD_SENSITIVITY="0.5"
```

See `.claude/skills/knowledge-repository/docs/NANOWAKEWORD-INTEGRATION.md` for full details.

### Option D2: Picovoice Porcupine (Commercial)

**Best for**: Production reliability, custom wake words

```bash
# Install
pip install pvporcupine

# Get access key from https://console.picovoice.co/
```

Configure in `.env.local`:
```bash
PICOVOICE_ACCESS_KEY="your-access-key"
WAKE_WORD_ENGINE="picovoice"
WAKE_WORD_KEYWORD="hey arcus"  # Or custom trained
```

**Note**: Custom wake word training costs ~$100 one-time.

---

## MCP Server Configuration

The complete MCP configuration file is at `.claude/skills/knowledge-repository/config/mcp-voice-config.json`:

```json
{
  "mcpServers": {
    "voicemode": {
      "command": "uvx",
      "args": ["voicemode"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      },
      "description": "Cloud-based voice (OpenAI Whisper + TTS)"
    },
    "voicemode-local": {
      "command": "python",
      "args": ["-m", "voicemode_local"],
      "env": {
        "WHISPER_MODEL_PATH": "${WHISPER_MODEL_PATH}",
        "KOKORO_MODEL_PATH": "${KOKORO_MODEL_PATH}"
      },
      "description": "Local voice (Whisper.cpp + Kokoro)"
    },
    "elevenlabs": {
      "command": "npx",
      "args": ["@anthropic/mcp-elevenlabs"],
      "env": {
        "ELEVENLABS_API_KEY": "${ELEVENLABS_API_KEY}"
      },
      "description": "Premium TTS (ElevenLabs)"
    }
  },
  "defaultServer": "voicemode",
  "settings": {
    "sampleRate": 16000,
    "channels": 1,
    "chunkSize": 1024,
    "silenceThreshold": 0.01,
    "silenceDuration": 1.5
  }
}
```

---

## Testing Voice Integration

### Basic Tests

```bash
# Test STT (Speech-to-Text)
curl -X POST https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F file=@test_audio.wav \
  -F model=whisper-1

# Test TTS (Text-to-Speech)
curl -X POST https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "Hello, I am Arcus.", "voice": "nova"}' \
  --output test_output.mp3
```

### Integration Test

```python
# test_voice.py
import asyncio
from voicemode import VoiceSession

async def test_voice():
    session = VoiceSession()

    # Test STT
    text = await session.transcribe("test_audio.wav")
    print(f"Transcribed: {text}")

    # Test TTS
    audio = await session.synthesize("Hello from Arcus!")
    print(f"Generated {len(audio)} bytes of audio")

asyncio.run(test_voice())
```

### Latency Benchmark

```python
# benchmark_voice.py
import time
import statistics

def benchmark_stt(audio_file, iterations=10):
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        # Run STT
        transcribe(audio_file)
        times.append((time.perf_counter() - start) * 1000)

    print(f"STT Latency: {statistics.mean(times):.0f}ms avg, {statistics.stdev(times):.0f}ms std")

def benchmark_tts(text, iterations=10):
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        # Run TTS
        synthesize(text)
        times.append((time.perf_counter() - start) * 1000)

    print(f"TTS Latency: {statistics.mean(times):.0f}ms avg, {statistics.stdev(times):.0f}ms std")
```

---

## Performance Tuning

### Latency Optimization

| Technique | Impact | Implementation |
|-----------|--------|----------------|
| **Streaming STT** | -200ms | Use real-time transcription API |
| **Streaming TTS** | -300ms | Stream audio as it generates |
| **Model preloading** | -500ms | Keep models in memory |
| **Edge deployment** | -100ms | Deploy closer to users |
| **VAD** | -500ms | Only process speech segments |

### Quality vs Speed Tradeoffs

| Setting | Faster | Better Quality |
|---------|--------|----------------|
| Whisper model | tiny.en | medium.en |
| TTS model | tts-1 | tts-1-hd |
| Sample rate | 16kHz | 24kHz |
| Audio format | opus | wav |

### Resource Usage

| Component | CPU | Memory | GPU |
|-----------|-----|--------|-----|
| Whisper tiny | 1 core | 200MB | Optional |
| Whisper base | 2 cores | 500MB | Recommended |
| Whisper medium | 4 cores | 2GB | Required |
| Kokoro | 1 core | 500MB | Optional |
| NanoWakeWord | 0.1 core | 50MB | No |

---

## Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| "No audio input" | Microphone not detected | Check `pyaudio` installation, permissions |
| "API rate limit" | Too many requests | Implement request queuing, upgrade plan |
| "High latency" | Network or model size | Use local models or edge deployment |
| "Poor transcription" | Background noise | Enable noise suppression, use better mic |
| "Robotic TTS" | Low quality model | Upgrade to `tts-1-hd` or ElevenLabs |
| "Wake word false positives" | Sensitivity too high | Lower `WAKE_WORD_SENSITIVITY` |

### Debugging

```bash
# Check audio devices
python -c "import pyaudio; p = pyaudio.PyAudio(); [print(p.get_device_info_by_index(i)) for i in range(p.get_device_count())]"

# Test microphone
python -c "import sounddevice; print(sounddevice.query_devices())"

# Verify API connectivity
curl -I https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"

# Check MCP server logs
tail -f ~/.claude/logs/mcp-voice.log
```

### Audio Quality Checklist

- [ ] Microphone sample rate matches config (16kHz recommended)
- [ ] Background noise is minimized
- [ ] Audio input is mono (not stereo)
- [ ] No audio clipping (levels below 0dB)
- [ ] Consistent volume levels

---

## Quick Reference

### Environment Variables Summary

```bash
# Cloud (OpenAI)
OPENAI_API_KEY="sk-proj-..."
VOICE_MODE="cloud"
VOICE_STT_SERVICE="openai"
VOICE_TTS_SERVICE="openai"
VOICE_TTS_VOICE="nova"

# Local
VOICE_MODE="local"
VOICE_STT_SERVICE="whisper"
VOICE_TTS_SERVICE="kokoro"
WHISPER_MODEL="base.en"

# Premium (ElevenLabs)
ELEVENLABS_API_KEY="..."
VOICE_TTS_SERVICE="elevenlabs"
ELEVENLABS_VOICE_ID="21m00Tcm4TlvDq8ikWAM"

# Wake Word
WAKE_WORD_ENGINE="nanowakeword"
WAKE_WORD_MODEL="hey_arcus"
WAKE_WORD_SENSITIVITY="0.5"
```

### File Locations

| Purpose | Path |
|---------|------|
| MCP Config | `.claude/skills/knowledge-repository/config/mcp-voice-config.json` |
| Voice Architecture | `.claude/skills/knowledge-repository/docs/VOICE-ARCHITECTURE.md` |
| NanoWakeWord Guide | `.claude/skills/knowledge-repository/docs/NANOWAKEWORD-INTEGRATION.md` |
| PersonaPlex Guide | `.claude/skills/knowledge-repository/docs/PERSONAPLEX-INTEGRATION.md` |

---

**Last Updated**: 2026-01-27
