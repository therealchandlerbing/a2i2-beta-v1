# A2I2 Voice Architecture: Progressive Enhancement Strategy

**Document Version**: 1.0.0
**Created**: 2026-01-26
**Purpose**: Define the progressive path from Siri Shortcuts MVP to full "Hey Arcus" voice replacement
**Status**: Strategic Architecture

---

## Executive Summary

This document defines A2I2's voice strategy as a **three-phase progressive enhancement**:

| Phase | Platform | Voice Layer | Wake Word | Timeline |
|-------|----------|-------------|-----------|----------|
| **1. MVP** | iOS (Siri Shortcuts) | Apple Siri | "Hey Siri, ask Arcus" | Weeks 1-2 |
| **2. Native** | iOS/Android App | PersonaPlex | "Hey Arcus" (Picovoice) | Weeks 3-6 |
| **3. Full** | All Platforms | PersonaPlex | "Hey Arcus" everywhere | Weeks 7-12 |

**Key Insight**: Siri Shortcuts is a **validation layer**, not a limitation. It lets us prove the concept with zero native development while PersonaPlex infrastructure is deployed.

---

## Phase 1: Siri Shortcuts MVP (Mobile Voice - Temporary)

### Why This Works

Siri Shortcuts provides **immediate voice access** with zero app development:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SIRI SHORTCUTS MVP FLOW                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   User: "Hey Siri, ask Arcus about the TechCorp proposal"           │
│                              │                                        │
│                              ▼                                        │
│   ┌───────────────────────────────────────────────────────────┐     │
│   │              iOS Shortcut: "Ask Arcus"                     │     │
│   │                                                             │     │
│   │   1. Dictate Text → query                                  │     │
│   │   2. Get Device ID → user identification                   │     │
│   │   3. POST to Arcus Gateway                                 │     │
│   │   4. Parse JSON response                                   │     │
│   │   5. Speak Text → Siri reads response                      │     │
│   │   6. [Optional] Loop for follow-up                         │     │
│   │                                                             │     │
│   └───────────────────────────────────────────────────────────┘     │
│                              │                                        │
│                              ▼                                        │
│   ┌───────────────────────────────────────────────────────────┐     │
│   │              Arcus Gateway (webhook)                        │     │
│   │                                                             │     │
│   │   • Authenticate via API key in header                     │     │
│   │   • Load user context from memory system                   │     │
│   │   • Inject relevant memories (semantic + episodic)         │     │
│   │   • Route to Claude/Gemini based on query type             │     │
│   │   • Store interaction as episodic memory                   │     │
│   │   • Return optimized voice response (<30 words ideal)      │     │
│   │                                                             │     │
│   │   ⚠️  MUST respond within 25 seconds                        │     │
│   │                                                             │     │
│   └───────────────────────────────────────────────────────────┘     │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Technical Constraints (Important)

| Constraint | Limit | Mitigation |
|------------|-------|------------|
| **Webhook timeout** | 25-30 seconds | Optimize inference, use streaming internally |
| **No background wake** | Must invoke shortcut | Train muscle memory: "Hey Siri, ask Arcus" |
| **Voice is Siri's** | Cannot customize | Phase 2 adds PersonaPlex voice |
| **No full-duplex** | Cannot interrupt | Keep responses concise (<30 words) |
| **Apple Watch** | Limited actions | Test thoroughly, may need simplified flow |
| **CarPlay** | Many actions blocked | Voice-only, no visual feedback |
| **State persistence** | None native | Maintain conversation_id server-side |

### Shortcut Implementation

**Core Shortcut: "Ask Arcus"**

```
Actions:
1. Dictate Text
   → Save to variable: query

2. Get Device Name
   → Save to variable: device_id

3. Get Contents of URL
   URL: https://arcus.yourserver.com/api/siri/query
   Method: POST
   Headers:
     Authorization: Bearer [API_KEY]
     Content-Type: application/json
   Body (JSON):
     {
       "query": [query],
       "device_id": [device_id],
       "shortcut": "ask_arcus",
       "conversation_id": [conversation_id or null]
     }
   → Save to variable: response

4. Get Dictionary Value
   Key: response_text
   → Save to variable: spoken_response

5. Get Dictionary Value
   Key: conversation_id
   → Save to variable: conversation_id

6. Speak Text
   Text: [spoken_response]

7. [Optional] Repeat from step 1 for follow-up
```

**Specialized Shortcuts:**

| Shortcut Name | Trigger | Purpose |
|---------------|---------|---------|
| "Ask Arcus" | "Hey Siri, ask Arcus..." | General queries |
| "Arcus Remember" | "Hey Siri, Arcus remember..." | Explicit /learn |
| "Arcus Recall" | "Hey Siri, Arcus recall..." | Explicit /recall |
| "Morning Briefing" | "Hey Siri, Arcus briefing" | Proactive summary |
| "Quick Note" | "Hey Siri, Arcus note..." | Fast capture |

### Gateway API for Siri

```typescript
// POST /api/siri/query
interface SiriQueryRequest {
  query: string;              // Transcribed speech
  device_id: string;          // For user identification
  shortcut: string;           // Which shortcut triggered
  conversation_id?: string;   // For continuity (null = new)
}

interface SiriQueryResponse {
  response_text: string;      // Optimized for speech (<30 words)
  conversation_id: string;    // For follow-up queries
  display_text?: string;      // Richer text if shown on screen
  action_taken?: string;      // "Saved to memory", "Created task", etc.
  follow_up_prompt?: string;  // Suggest next question
}
```

### Response Optimization for Voice

Since Siri speaks the response, optimize for **brevity**:

```python
# Voice response guidelines
VOICE_OPTIMAL_LENGTH = 15-30  # words
VOICE_MAX_LENGTH = 60         # absolute maximum

def optimize_for_voice(response: str) -> str:
    """
    Transform written response to spoken form.
    """
    # Remove markdown formatting
    response = strip_markdown(response)

    # Expand abbreviations
    response = expand_abbreviations(response)  # "API" → "A P I"

    # Add natural pauses
    response = add_speech_pauses(response)     # Commas for breath

    # Truncate if needed
    if word_count(response) > VOICE_MAX_LENGTH:
        response = summarize_to_length(response, VOICE_OPTIMAL_LENGTH)
        response += " Want me to elaborate?"

    return response
```

### What We Validate in Phase 1

| Hypothesis | How We Test |
|------------|-------------|
| Users want voice access to Arcus | Track shortcut usage frequency |
| Memory context improves responses | Compare with/without context injection |
| 25s timeout is sufficient | Monitor timeout rates, optimize slow queries |
| Apple Watch is viable | Test on device, measure success rate |
| CarPlay works for hands-free | Test in vehicle, document limitations |
| Users want follow-up conversations | Track conversation continuation rate |

---

## Phase 2: Native Mobile App with PersonaPlex

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                 NATIVE APP + PERSONAPLEX FLOW                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   User: "Hey Arcus" (detected locally)                               │
│                              │                                        │
│        ┌─────────────────────┼─────────────────────┐                 │
│        ▼                     │                     │                 │
│   ┌─────────────┐           │            ┌─────────────┐            │
│   │  Picovoice  │           │            │  PersonaPlex │            │
│   │  Porcupine  │           │            │  Cloud GPU   │            │
│   │  (on-device)│           │            │  (16GB VRAM) │            │
│   │             │           │            │              │            │
│   │  Wake word  │──────────►│◄───────────│  Full-duplex │            │
│   │  detection  │   audio   │   stream   │  voice AI    │            │
│   │  <5% CPU    │           │            │  170ms turn  │            │
│   │  $100 train │           │            │  $75-300/mo  │            │
│   └─────────────┘           │            └─────────────┘            │
│                              │                     │                 │
│                              ▼                     ▼                 │
│                    ┌─────────────────────────────────────┐          │
│                    │          Arcus Gateway               │          │
│                    │                                      │          │
│                    │  • Memory context injection          │          │
│                    │  • Model routing (Claude/Gemini)     │          │
│                    │  • VNKG optimization for speech      │          │
│                    │  • Episodic memory capture           │          │
│                    │  • Trust ledger updates              │          │
│                    └─────────────────────────────────────┘          │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Why PersonaPlex Changes Everything

| Capability | Siri Shortcuts | PersonaPlex |
|------------|----------------|-------------|
| **Wake word** | "Hey Siri" (Apple's) | "Hey Arcus" (custom) |
| **Voice** | Siri's voice | 16 customizable voices |
| **Latency** | ~1-2 seconds | 170ms turn-taking |
| **Full-duplex** | No (turn-based) | Yes (can interrupt) |
| **Backchannels** | No | "Uh-huh", "I see", "Yeah" |
| **Emotion** | None | Detected and responded to |
| **Background** | Limited | Always-on wake word |
| **Custom persona** | None | Full personality control |

### Mobile App Architecture (React Native + Expo)

```
src/
├── app/                          # Expo Router screens
│   ├── (tabs)/
│   │   ├── voice.tsx             # Main voice interface
│   │   ├── memory.tsx            # Knowledge browser
│   │   └── settings.tsx          # Preferences
│   └── _layout.tsx
├── services/
│   ├── wakeword.ts               # Picovoice Porcupine integration
│   ├── personaplex.ts            # WebSocket to PersonaPlex server
│   ├── arcus-gateway.ts          # REST API to gateway
│   └── memory-sync.ts            # Supabase realtime sync
├── hooks/
│   ├── useVoice.ts               # Voice state management
│   ├── useMemory.ts              # Local memory cache
│   └── useAuth.ts                # Supabase auth
└── components/
    ├── VoiceOrb.tsx              # Visual feedback (listening/speaking)
    ├── TranscriptView.tsx        # Live transcription display
    └── MemoryCard.tsx            # Memory entry display
```

### Wake Word Integration (Picovoice Porcupine)

```typescript
// services/wakeword.ts
import { Porcupine, BuiltInKeywords } from '@picovoice/porcupine-react-native';

const CUSTOM_KEYWORD_PATH = 'assets/hey_arcus.ppn';  // Trained model ($100)

class WakeWordService {
  private porcupine: Porcupine | null = null;

  async initialize() {
    this.porcupine = await Porcupine.create(
      PICOVOICE_ACCESS_KEY,
      [CUSTOM_KEYWORD_PATH],  // "Hey Arcus"
      [0.5]  // Sensitivity (0.0-1.0)
    );
  }

  async startListening(onWakeWord: () => void) {
    // Runs on device, <5% CPU, no network needed
    // When "Hey Arcus" detected, calls onWakeWord
    // Then streams audio to PersonaPlex
  }
}
```

### PersonaPlex Connection

```typescript
// services/personaplex.ts
import { ArcusContextBridge } from './context-bridge';

class PersonaPlexService {
  private ws: WebSocket | null = null;
  private contextBridge: ArcusContextBridge;

  async connect(userId: string) {
    // Connect to PersonaPlex server
    this.ws = new WebSocket('wss://personaplex.arcus.server:8998');

    // Load context from memory system
    const context = await this.contextBridge.getContextForUser(userId);

    // Send persona configuration
    this.ws.send(JSON.stringify({
      type: 'configure',
      persona: {
        voice_embedding: 'NATF2',  // Professional female voice
        text_prompt: context.personaPrompt,  // Up to 200 tokens
        temperature: 0.7
      }
    }));
  }

  streamAudio(audioBuffer: ArrayBuffer) {
    // Stream post-wake-word audio to PersonaPlex
    // PersonaPlex handles STT + LLM + TTS in full-duplex
  }
}
```

### Context Injection for Voice

```typescript
// services/context-bridge.ts
interface VoiceContext {
  personaPrompt: string;      // 200 tokens max
  relevantMemories: string[]; // Top 3 semantic/episodic
  userPreferences: {
    communicationStyle: string;
    verbosityLevel: number;
    timezone: string;
  };
}

class ArcusContextBridge {
  async getContextForUser(userId: string): Promise<VoiceContext> {
    // Fetch from Supabase in parallel
    const [semantic, episodic, preferences] = await Promise.all([
      this.getRelevantSemanticMemories(userId, 3),
      this.getRecentEpisodicContext(userId, 2),
      this.getUserPreferences(userId)
    ]);

    // Build persona prompt (200 tokens max)
    const personaPrompt = `
You are Arcus, ${preferences.name}'s AI companion.
Communication style: ${preferences.communicationStyle}.
Current context: ${semantic.map(m => m.summary).join('. ')}.
Recent: ${episodic.map(e => e.summary).join('. ')}.
Keep responses under 30 words for voice.
    `.trim();

    return { personaPrompt, relevantMemories: semantic, userPreferences: preferences };
  }
}
```

### What Phase 2 Enables

| Feature | Description |
|---------|-------------|
| **True "Hey Arcus"** | Custom wake word, your brand |
| **Natural conversation** | Interrupt, get backchannels, feels human |
| **Custom voice** | Arcus has its own voice identity |
| **Always-on** | Background wake word detection |
| **Faster** | 170ms vs ~2 seconds |
| **Emotional awareness** | Detect and respond to user emotion |
| **Full memory integration** | Real-time context injection |

---

## Phase 3: Full Platform Voice (Web + Mobile + Wearable)

### Web Application with PersonaPlex

The web app uses PersonaPlex **directly** (not through Siri):

```
┌─────────────────────────────────────────────────────────────────────┐
│                  WEB APP VOICE ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   Browser (Next.js)                                                  │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                                                               │   │
│   │   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │   │
│   │   │   Voice     │    │   Chat      │    │   Memory    │    │   │
│   │   │   Mode      │    │   Mode      │    │   Browser   │    │   │
│   │   │   (WebRTC)  │    │   (Text)    │    │   (Graph)   │    │   │
│   │   └──────┬──────┘    └─────────────┘    └─────────────┘    │   │
│   │          │                                                    │   │
│   │          ▼                                                    │   │
│   │   ┌─────────────────────────────────────────────────────┐   │   │
│   │   │            WebRTC Audio Stream                       │   │   │
│   │   │   • Microphone → PersonaPlex (full-duplex)          │   │   │
│   │   │   • PersonaPlex → Speaker                            │   │   │
│   │   │   • Visual: VoiceOrb shows state                     │   │   │
│   │   └─────────────────────────────────────────────────────┘   │   │
│   │                                                               │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                        │
│                              ▼                                        │
│   PersonaPlex Server (Cloud GPU) ◄──────► Arcus Gateway              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Web Voice Implementation

```typescript
// components/VoiceMode.tsx
import { usePersonaPlex } from '@/hooks/usePersonaPlex';

export function VoiceMode() {
  const {
    isListening,
    isSpeaking,
    transcript,
    startListening,
    stopListening
  } = usePersonaPlex();

  return (
    <div className="voice-container">
      <VoiceOrb
        state={isListening ? 'listening' : isSpeaking ? 'speaking' : 'idle'}
      />
      <TranscriptView
        text={transcript}
        isLive={isListening}
      />
      <button onClick={isListening ? stopListening : startListening}>
        {isListening ? 'Stop' : 'Start Voice'}
      </button>
    </div>
  );
}
```

### Cross-Platform Voice Sync

All platforms share the same memory and context:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    UNIFIED VOICE ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐            │
│   │   Web   │   │  Mobile │   │  Watch  │   │ CarPlay │            │
│   │  App    │   │   App   │   │  App    │   │         │            │
│   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘            │
│        │             │             │             │                   │
│        └─────────────┴──────┬──────┴─────────────┘                   │
│                             │                                         │
│                             ▼                                         │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                   PersonaPlex Server                          │   │
│   │                                                               │   │
│   │   • Full-duplex voice for all platforms                      │   │
│   │   • Same voice identity (NATF2/NATM1)                        │   │
│   │   • Consistent persona across devices                        │   │
│   │                                                               │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                             │                                         │
│                             ▼                                         │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    Arcus Gateway                              │   │
│   │                                                               │   │
│   │   • Memory context injection                                 │   │
│   │   • Model routing                                            │   │
│   │   • Episodic capture                                         │   │
│   │   • Trust ledger                                             │   │
│   │                                                               │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                             │                                         │
│                             ▼                                         │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    Supabase                                   │   │
│   │                                                               │   │
│   │   • arcus_episodic_memory                                    │   │
│   │   • arcus_semantic_memory                                    │   │
│   │   • arcus_procedural_memory                                  │   │
│   │   • arcus_knowledge_graph                                    │   │
│   │                                                               │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Wearable Integration

**Apple Watch**:
- Companion app with VoiceOrb complication
- "Hey Arcus" via Picovoice (if sufficient resources)
- Or: Simplified Siri Shortcut fallback

**AirPods**:
- Triggered via iPhone app background audio
- Seamless handoff from phone

**CarPlay**:
- Voice-only interface
- Simplified responses (extra brevity)
- No visual distraction

---

## Implementation Roadmap

### Phase 1: Siri Shortcuts MVP (Weeks 1-2)

| Week | Tasks |
|------|-------|
| 1 | Deploy Arcus Gateway with /api/siri/query endpoint |
| 1 | Create "Ask Arcus" shortcut template |
| 1 | Implement voice response optimization (<30 words) |
| 1 | Add conversation_id for continuity |
| 2 | Create specialized shortcuts (Remember, Recall, Briefing) |
| 2 | Test on Apple Watch and CarPlay |
| 2 | Document limitations and success rates |
| 2 | Collect usage metrics for Phase 2 planning |

**Deliverables**:
- Working Siri Shortcuts (shareable .shortcut files)
- Gateway endpoint with memory injection
- Usage analytics dashboard

### Phase 2: Native Mobile App (Weeks 3-6)

| Week | Tasks |
|------|-------|
| 3 | Train "Hey Arcus" wake word (Picovoice, $100) |
| 3 | Set up PersonaPlex on cloud GPU (AWS g5.xlarge or Lambda Labs) |
| 3 | Create React Native app scaffold with Expo |
| 4 | Integrate Picovoice Porcupine for wake word |
| 4 | Connect to PersonaPlex via WebSocket |
| 4 | Implement context bridge for memory injection |
| 5 | Build VoiceOrb UI component (listening/speaking states) |
| 5 | Add transcript view and conversation history |
| 5 | Implement episodic memory capture for voice |
| 6 | TestFlight beta for iOS |
| 6 | Android build and internal testing |
| 6 | Performance optimization (battery, latency) |

**Deliverables**:
- iOS app with "Hey Arcus" wake word
- Android app (same codebase)
- PersonaPlex server deployed
- Full memory integration

### Phase 3: Full Platform (Weeks 7-12)

| Week | Tasks |
|------|-------|
| 7-8 | Web app voice mode with WebRTC |
| 7-8 | Apple Watch companion app |
| 9-10 | CarPlay optimization |
| 9-10 | Cross-device conversation continuity |
| 11-12 | Proactive voice features (briefings, reminders) |
| 11-12 | Advanced persona customization |

**Deliverables**:
- Unified voice across all platforms
- Same Arcus voice everywhere
- Seamless context handoff

---

## Cost Analysis

### Phase 1: Siri Shortcuts MVP
| Item | Cost |
|------|------|
| Supabase (Pro) | $25/month |
| Gateway hosting (Vercel/Railway) | $20/month |
| Claude API | ~$50/month (usage-based) |
| **Total** | **~$95/month** |

### Phase 2: Native + PersonaPlex
| Item | Cost |
|------|------|
| Phase 1 costs | $95/month |
| Picovoice wake word training | $100 (one-time) |
| PersonaPlex GPU (Lambda Labs A10) | ~$75/month (low usage) to $300/month (heavy) |
| Apple Developer | $99/year |
| **Total** | **~$270-500/month** |

### Phase 3: Full Platform
| Item | Cost |
|------|------|
| Phase 2 costs | $270-500/month |
| Additional GPU capacity | +$100-200/month |
| **Total** | **~$370-700/month** |

---

## Success Metrics

### Phase 1 (Validation)
- Shortcut invocation rate (daily/weekly active)
- Query completion rate (vs. timeout)
- Conversation continuation rate
- Apple Watch success rate
- User satisfaction (qualitative feedback)

### Phase 2 (Adoption)
- Daily active voice users
- Wake word detection accuracy
- Response latency (p50, p95)
- Memory injection relevance score
- Session length (turns per conversation)

### Phase 3 (Retention)
- Cross-device usage patterns
- Voice vs. text preference ratio
- Proactive feature engagement
- Trust level progression (autonomy)
- Net Promoter Score

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Siri timeout (25s) | High | Optimize queries, cache common contexts |
| Wake word false positives | Medium | Tune sensitivity, add confirmation for actions |
| PersonaPlex latency spikes | Medium | Geographic GPU placement, fallback to text |
| Apple Watch battery drain | Medium | Minimal background processing, Siri fallback |
| CarPlay restrictions | Low | Accept limitations, voice-only design |
| User confusion (Siri vs Arcus) | Medium | Clear branding, distinct voice in Phase 2 |

---

## The Vision: Replacing Siri

The end state is **"Hey Arcus" as the primary voice interface**:

| Dimension | Siri | Arcus (Phase 3) |
|-----------|------|-----------------|
| **Memory** | None cross-session | Full organizational memory |
| **Context** | Device-only | Cross-device, cross-team |
| **Voice** | Apple's voice | Custom Arcus voice |
| **Personality** | Generic assistant | Personalized companion |
| **Actions** | Apple ecosystem only | Integrated with your workflows |
| **Learning** | None | Improves with every interaction |
| **Autonomy** | Command-response only | Progressive autonomous action |
| **Team** | Single user | Collective intelligence |

**The journey**:
1. Start with Siri as transport layer (Phase 1)
2. Add custom wake word and voice (Phase 2)
3. Build superior experience that makes Siri unnecessary (Phase 3)

---

## Conclusion

Siri Shortcuts is **not a compromise** - it's a **smart validation strategy**. It lets us:

1. **Prove demand** before building native apps
2. **Test memory integration** in voice context
3. **Learn user patterns** for Phase 2 optimization
4. **Ship in days** instead of months

The progressive path ensures we're always shipping value while building toward the full vision of "Hey Arcus" as the organizational AI companion that truly replaces Siri.

---

*"The best way to predict the future is to ship it incrementally."*

---

**Document History**
| Date | Version | Changes |
|------|---------|---------|
| 2026-01-26 | 1.0.0 | Initial strategic architecture |
