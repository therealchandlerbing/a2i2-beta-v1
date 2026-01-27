# A2I2 Multi-Channel Architecture Design

**Version:** 1.0.0
**Last Updated:** 2026-01-26
**Purpose:** Design patterns and implementation blueprints for A2I2's multi-channel intelligence platform
**Inspired By:** Clawdbot architecture patterns (https://docs.clawd.bot/)

---

## Executive Summary

This document extracts proven architectural patterns from Clawdbot's multi-channel platform and adapts them for A2I2's Enterprise AI Chief of Staff. The goal is to build **A2I2's own native gateway** that connects to WhatsApp, Discord, and Siri while integrating with A2I2's unique memory system (CAP, ATL, five memory types).

**Key Insight:** Clawdbot excels at *accessibility* (reaching users everywhere). A2I2 excels at *intelligence* (persistent memory, organizational learning). This design combines both.

---

## Table of Contents

1. [Core Architecture Patterns](#core-architecture-patterns)
2. [Arcus Gateway Design](#arcus-gateway-design)
3. [Channel Adapter Architecture](#channel-adapter-architecture)
4. [Session & Memory Integration](#session--memory-integration)
5. [WhatsApp Adapter Design](#whatsapp-adapter-design)
6. [Discord Adapter Design](#discord-adapter-design)
7. [Siri/Webhook Integration Design](#siriwebhook-integration-design)
8. [Security & Access Control](#security--access-control)
9. [A2I2 Concept Mapping](#a2i2-concept-mapping)
10. [Implementation Roadmap](#implementation-roadmap)

---

## Core Architecture Patterns

### Pattern 1: Unified Gateway Control Plane

**What Clawdbot Does:**
- Single WebSocket endpoint (`ws://127.0.0.1:18789`) handles all channels
- All sessions, events, and tools flow through one control plane
- Clean separation between gateway logic and channel-specific adapters

**A2I2 Implementation:**

```
┌─────────────────────────────────────────────────────────────────┐
│                      Arcus Gateway                               │
│                  (WebSocket + HTTP Control Plane)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    Gateway Core                           │  │
│   │  • Session Manager     • Memory Context Injector         │  │
│   │  • Event Router        • Autonomy Trust Checker (ATL)    │  │
│   │  • Model Router        • Knowledge Graph Connector       │  │
│   └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│   ┌──────────┐        ┌──────────┐        ┌──────────┐         │
│   │ WhatsApp │        │ Discord  │        │   Siri   │         │
│   │ Adapter  │        │ Adapter  │        │ Webhook  │         │
│   └──────────┘        └──────────┘        └──────────┘         │
│   Baileys lib          discord.js         HTTP POST            │
│   E.164 phones         Guild/Channel      iOS Shortcuts        │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                A2I2 Memory Layer                          │  │
│   │  Episodic │ Semantic │ Procedural │ Working │ Relational │  │
│   │    ↓           ↓          ↓           ↓          ↓       │  │
│   │  Supabase: arcus_* tables + arcus_knowledge_graph        │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Pattern 2: Channel Adapter Abstraction

**What Clawdbot Does:**
- Each channel (WhatsApp, Discord, etc.) implements the same adapter interface
- Adapters handle: incoming messages, outgoing responses, access control, history
- Channel-specific concerns isolated from core logic

**A2I2 Channel Adapter Interface:**

```typescript
// A2I2 Channel Adapter Contract
interface ArcusChannelAdapter {
  // Identity
  readonly name: string;                    // "whatsapp" | "discord" | "siri"
  readonly type: "messaging" | "webhook";

  // Lifecycle
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  isConnected(): boolean;

  // Inbound: Channel → A2I2
  onMessage(handler: (msg: InboundMessage) => Promise<void>): void;
  onReaction?(handler: (reaction: Reaction) => void): void;

  // Outbound: A2I2 → Channel
  send(message: OutboundMessage): Promise<SendResult>;
  sendTypingIndicator?(chatId: string): Promise<void>;

  // Context
  getChatContext(chatId: string): Promise<ChatContext>;
  getUserIdentity(userId: string): Promise<UserIdentity>;

  // Access Control
  checkAccess(userId: string, chatId: string): AccessDecision;
}

// Normalized message format (channel-agnostic)
interface InboundMessage {
  id: string;
  timestamp: Date;
  channel: string;                          // "whatsapp" | "discord" | "siri"
  chatId: string;                           // Normalized chat identifier
  chatType: "dm" | "group";

  sender: {
    id: string;                             // Normalized user identifier
    displayName?: string;
    phone?: string;                         // WhatsApp E.164
    discordId?: string;
    email?: string;
  };

  content: {
    text: string;
    attachments?: Attachment[];
    replyTo?: {
      messageId: string;
      quotedText?: string;
    };
  };

  // A2I2-specific: Memory context to inject
  memoryContext?: {
    recentEpisodes: EpisodicMemory[];
    relevantSemantics: SemanticMemory[];
    userPreferences: ProceduralMemory[];
    entityRelationships: RelationalMemory[];
  };
}
```

### Pattern 3: Access Control Policies

**What Clawdbot Does:**
- `dmPolicy`: "pairing" | "allowlist" | "open" | "disabled"
- Per-channel allowlists (phone numbers, user IDs, usernames)
- Group-specific settings with mention requirements

**A2I2 Access Control Design:**

```typescript
// A2I2 Access Control (integrates with Autonomy Trust Ledger)
interface AccessPolicy {
  // DM policy
  dmPolicy: "pairing" | "allowlist" | "open" | "disabled";
  allowedUsers: UserIdentifier[];           // Cross-channel identifiers

  // Group policy
  groupPolicy: "allowlist" | "open" | "disabled";
  allowedGroups: GroupIdentifier[];
  requireMention: boolean;                  // Only respond when @mentioned

  // A2I2-specific: Trust-based access
  trustRequirements?: {
    minTrustLevel: AutonomyLevel;           // L0-L4
    requirePairedUser: boolean;
  };
}

// Pairing flow (new users must be approved)
interface PairingRequest {
  userId: string;
  channel: string;
  requestedAt: Date;
  code: string;                             // 6-char approval code
  expiresAt: Date;                          // 1 hour TTL
  status: "pending" | "approved" | "denied" | "expired";
}
```

### Pattern 4: Session Scoping & Identity Linking

**What Clawdbot Does:**
- Sessions scoped per sender or collapsed to main session
- `identityLinks` map same person across channels
- Session keys: `agent:<agentId>:<channel>:<chatType>:<identifier>`

**A2I2 Session Design:**

```typescript
// A2I2 Session Management
interface SessionConfig {
  // Scoping
  scope: "per-sender" | "per-channel" | "unified";
  dmScope: "main" | "per-peer" | "per-channel-peer";

  // Identity linking (same person across channels)
  identityLinks: {
    [canonicalUserId: string]: string[];    // ["whatsapp:+1555...", "discord:123..."]
  };

  // Reset policies
  reset: {
    mode: "daily" | "idle" | "manual";
    atHour?: number;                        // For daily reset
    idleMinutes?: number;                   // For idle reset
  };

  // A2I2-specific: Memory persistence
  memoryPersistence: {
    flushOnCompaction: boolean;             // Write to CLAUDE.memory.md
    flushOnIdle: boolean;                   // Write when session goes idle
    memoryFile: string;                     // "memory/YYYY-MM-DD.md"
  };
}

// Session key format for A2I2
type SessionKey =
  | `arcus:main`                            // Unified main session
  | `arcus:${Channel}:dm:${UserId}`         // DM session
  | `arcus:${Channel}:group:${GroupId}`;    // Group session
```

### Pattern 5: Heartbeat & Proactive Operations

**What Clawdbot Does:**
- Configurable heartbeat interval (default 30m)
- Reads HEARTBEAT.md for instructions
- Can trigger proactive notifications

**A2I2 Heartbeat Design (REFLECT Operation):**

```typescript
// A2I2 Heartbeat Configuration
interface HeartbeatConfig {
  // Timing
  interval: string;                         // "30m", "1h", "6h"
  enabled: boolean;

  // Delivery
  target: "last" | "whatsapp" | "discord" | "none";
  recipient?: string;                       // Override recipient

  // A2I2-specific: Triggers REFLECT operation
  reflectPrompt: string;                    // Default: "Run REFLECT operation..."
  suppressIfNoLearnings: boolean;           // Don't notify if nothing new
  minLearningsToReport: number;             // Threshold for notification
}

// Example HEARTBEAT.md for A2I2
const HEARTBEAT_TEMPLATE = `
# A2I2 Heartbeat Instructions

When this heartbeat triggers:

1. **REFLECT** - Synthesize patterns from recent interactions
   - Review episodic memories from last heartbeat
   - Identify recurring themes or preferences
   - Update procedural memory with new patterns

2. **Report** (if significant learnings)
   - Summarize what was learned
   - Note any preference changes
   - Flag items needing user confirmation

3. **Skip** if no significant learnings
   - Reply: HEARTBEAT_OK

## Thresholds
- Report if 3+ new learnings since last heartbeat
- Report if user preferences changed
- Report if new entity relationships discovered
`;
```

---

## Arcus Gateway Design

### Gateway Architecture

```typescript
// Arcus Gateway - Main Entry Point
class ArcusGateway {
  private adapters: Map<string, ArcusChannelAdapter>;
  private sessionManager: SessionManager;
  private memoryLayer: A2I2MemoryLayer;
  private modelRouter: ModelRouter;
  private trustLedger: AutonomyTrustLedger;

  // Configuration
  private config: GatewayConfig;

  constructor(config: GatewayConfig) {
    this.config = config;
    this.adapters = new Map();
    this.sessionManager = new SessionManager(config.session);
    this.memoryLayer = new A2I2MemoryLayer(config.memory);
    this.modelRouter = new ModelRouter(config.models);
    this.trustLedger = new AutonomyTrustLedger(config.trust);
  }

  // Register channel adapters
  registerAdapter(adapter: ArcusChannelAdapter): void {
    this.adapters.set(adapter.name, adapter);
    adapter.onMessage(this.handleInbound.bind(this));
  }

  // Main message flow
  private async handleInbound(msg: InboundMessage): Promise<void> {
    // 1. Access control
    const access = await this.checkAccess(msg);
    if (!access.allowed) {
      return this.handleAccessDenied(msg, access);
    }

    // 2. Get or create session
    const session = await this.sessionManager.getSession(msg);

    // 3. Inject memory context (A2I2-specific)
    const memoryContext = await this.memoryLayer.getContext({
      userId: msg.sender.id,
      chatId: msg.chatId,
      query: msg.content.text,
      entityMentions: this.extractEntities(msg.content.text),
    });

    // 4. Check autonomy level for any actions
    const trustLevel = await this.trustLedger.getUserTrust(msg.sender.id);

    // 5. Route to model with context
    const response = await this.modelRouter.process({
      message: msg,
      session: session,
      memoryContext: memoryContext,
      trustLevel: trustLevel,
    });

    // 6. Execute any LEARN operations from response
    await this.processLearnings(response, msg);

    // 7. Send response back through adapter
    const adapter = this.adapters.get(msg.channel);
    await adapter.send({
      chatId: msg.chatId,
      content: response.text,
      replyTo: msg.id,
    });

    // 8. Log to Autonomy Trust Ledger
    await this.trustLedger.logInteraction({
      userId: msg.sender.id,
      action: "response",
      autonomyLevel: trustLevel,
      successful: true,
    });
  }

  // Extract learnings and persist to memory
  private async processLearnings(
    response: ModelResponse,
    original: InboundMessage
  ): Promise<void> {
    // Check for LEARN directives in response
    if (response.learnings?.length > 0) {
      for (const learning of response.learnings) {
        await this.memoryLayer.learn({
          type: learning.memoryType,         // episodic | semantic | procedural
          content: learning.content,
          source: {
            channel: original.channel,
            messageId: original.id,
            userId: original.sender.id,
          },
          confidence: learning.confidence,
        });
      }
    }
  }
}
```

### Gateway Configuration

```typescript
// A2I2 Gateway Configuration Schema
interface GatewayConfig {
  // Server settings
  server: {
    port: number;                           // Default: 18790 (avoid Clawdbot's 18789)
    host: string;                           // "127.0.0.1" | "0.0.0.0"
    auth: {
      mode: "token" | "none";
      token?: string;
    };
  };

  // Channel adapters to enable
  channels: {
    whatsapp?: WhatsAppConfig;
    discord?: DiscordConfig;
    siri?: SiriWebhookConfig;
  };

  // Session management
  session: SessionConfig;

  // A2I2 Memory integration
  memory: {
    supabase: {
      url: string;
      anonKey: string;
    };
    localCache: {
      enabled: boolean;
      path: string;                         // "~/.arcus/memory"
    };
    contextInjection: {
      maxEpisodicMemories: number;          // Default: 10
      maxSemanticFacts: number;             // Default: 20
      includeRelationships: boolean;        // Include knowledge graph context
    };
  };

  // Model routing
  models: {
    primary: string;                        // "anthropic/claude-opus-4-5"
    fallbacks: string[];
    taskRouting: {
      complexReasoning: string;             // Claude or Gemini Pro
      largeDocuments: string;               // Gemini Pro (1M context)
      imageGeneration: string;              // Gemini Pro Image
      realTimeInfo: string;                 // Gemini Flash + Search
      voiceConversation: string;            // PersonaPlex
    };
  };

  // Trust & autonomy
  trust: {
    defaultLevel: AutonomyLevel;            // L0 for new users
    autoElevate: boolean;                   // Elevate trust over time
    requireApprovalAbove: AutonomyLevel;    // L2 - actions above this need approval
  };

  // Heartbeat (REFLECT operation)
  heartbeat: HeartbeatConfig;
}
```

---

## Channel Adapter Architecture

### Base Adapter Class

```typescript
// Abstract base for all A2I2 channel adapters
abstract class BaseChannelAdapter implements ArcusChannelAdapter {
  abstract readonly name: string;
  abstract readonly type: "messaging" | "webhook";

  protected config: ChannelConfig;
  protected messageHandler?: (msg: InboundMessage) => Promise<void>;
  protected connected: boolean = false;

  constructor(config: ChannelConfig) {
    this.config = config;
  }

  // Common access control logic
  checkAccess(userId: string, chatId: string): AccessDecision {
    const policy = this.config.accessPolicy;

    // Check DM policy
    if (this.isDM(chatId)) {
      switch (policy.dmPolicy) {
        case "disabled":
          return { allowed: false, reason: "DMs disabled" };
        case "allowlist":
          if (!policy.allowedUsers.includes(userId)) {
            return { allowed: false, reason: "Not in allowlist" };
          }
          break;
        case "pairing":
          // Check if user is paired
          if (!this.isPaired(userId)) {
            return { allowed: false, reason: "pairing_required", pairingCode: this.generatePairingCode(userId) };
          }
          break;
        case "open":
          // Allow all
          break;
      }
    }

    // Check group policy
    if (this.isGroup(chatId)) {
      if (policy.groupPolicy === "disabled") {
        return { allowed: false, reason: "Groups disabled" };
      }
      if (policy.groupPolicy === "allowlist" && !policy.allowedGroups.includes(chatId)) {
        return { allowed: false, reason: "Group not in allowlist" };
      }
    }

    return { allowed: true };
  }

  // Normalize user identity across channels
  protected normalizeUserId(rawId: string): string {
    // Format: channel:identifier
    return `${this.name}:${rawId}`;
  }

  // Abstract methods for subclasses
  abstract connect(): Promise<void>;
  abstract disconnect(): Promise<void>;
  abstract send(message: OutboundMessage): Promise<SendResult>;
  abstract getChatContext(chatId: string): Promise<ChatContext>;
  abstract getUserIdentity(userId: string): Promise<UserIdentity>;

  // Optional methods
  sendTypingIndicator?(chatId: string): Promise<void>;
  onReaction?(handler: (reaction: Reaction) => void): void;

  // Registration
  onMessage(handler: (msg: InboundMessage) => Promise<void>): void {
    this.messageHandler = handler;
  }

  isConnected(): boolean {
    return this.connected;
  }

  protected isDM(chatId: string): boolean {
    return !chatId.includes("group") && !chatId.includes("@g.");
  }

  protected isGroup(chatId: string): boolean {
    return !this.isDM(chatId);
  }
}
```

---

## WhatsApp Adapter Design

### WhatsApp Configuration

```typescript
interface WhatsAppConfig {
  enabled: boolean;

  // Access control
  accessPolicy: {
    dmPolicy: "pairing" | "allowlist" | "open" | "disabled";
    allowedUsers: string[];                 // E.164 phone numbers: ["+15555550123"]
    groupPolicy: "allowlist" | "open" | "disabled";
    allowedGroups: string[];                // Group JIDs
    requireMention: boolean;                // In groups, only respond to @mentions
  };

  // Features
  features: {
    sendReadReceipts: boolean;              // Blue ticks
    typingIndicator: boolean;               // "typing..." indicator
    ackReaction: string | null;             // Emoji to react with on receipt (e.g., "👀")
    voiceTranscription: boolean;            // Transcribe voice messages
  };

  // Message handling
  messages: {
    maxLength: number;                      // Chunk long messages (default: 4000)
    historyLimit: number;                   // Messages to include as context
  };

  // Multi-account (future)
  accounts?: {
    [accountId: string]: {
      phone: string;
      authPath: string;
    };
  };
}
```

### WhatsApp Adapter Implementation

```typescript
// A2I2 WhatsApp Adapter using Baileys
import makeWASocket, {
  DisconnectReason,
  useMultiFileAuthState,
  WAMessage
} from "@whiskeysockets/baileys";

class WhatsAppAdapter extends BaseChannelAdapter {
  readonly name = "whatsapp";
  readonly type = "messaging" as const;

  private socket: ReturnType<typeof makeWASocket> | null = null;
  private authState: any;
  private reconnectAttempts: number = 0;

  constructor(config: WhatsAppConfig) {
    super(config);
  }

  async connect(): Promise<void> {
    // Load auth state
    const { state, saveCreds } = await useMultiFileAuthState(
      "~/.arcus/credentials/whatsapp"
    );
    this.authState = state;

    // Create socket
    this.socket = makeWASocket({
      auth: state,
      printQRInTerminal: true,              // For initial pairing
    });

    // Handle connection events
    this.socket.ev.on("connection.update", (update) => {
      const { connection, lastDisconnect } = update;
      if (connection === "close") {
        const shouldReconnect =
          (lastDisconnect?.error as any)?.output?.statusCode !== DisconnectReason.loggedOut;
        if (shouldReconnect) {
          // Exponential backoff to avoid tight reconnection loops
          const backoffMs = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
          this.reconnectAttempts++;
          console.log(`Reconnecting in ${backoffMs}ms (attempt ${this.reconnectAttempts})`);
          setTimeout(() => this.connect(), backoffMs);
        }
      } else if (connection === "open") {
        this.connected = true;
        this.reconnectAttempts = 0;         // Reset backoff on successful connection
        console.log("WhatsApp connected");
      }
    });

    // Save credentials on update
    this.socket.ev.on("creds.update", saveCreds);

    // Handle incoming messages
    this.socket.ev.on("messages.upsert", async ({ messages }) => {
      for (const msg of messages) {
        if (!msg.key.fromMe) {              // Ignore our own messages
          await this.handleIncomingMessage(msg);
        }
      }
    });
  }

  private async handleIncomingMessage(waMsg: WAMessage): Promise<void> {
    if (!this.messageHandler) return;

    const chatId = waMsg.key.remoteJid!;
    const senderId = this.extractSenderId(waMsg);

    // Check access
    const access = this.checkAccess(senderId, chatId);
    if (!access.allowed) {
      if (access.reason === "pairing_required") {
        // Send pairing code
        await this.sendPairingResponse(chatId, access.pairingCode!);
      }
      return;
    }

    // Acknowledge receipt (optional)
    if (this.config.features.ackReaction) {
      await this.socket?.sendMessage(chatId, {
        react: { text: this.config.features.ackReaction, key: waMsg.key }
      });
    }

    // Send typing indicator
    if (this.config.features.typingIndicator) {
      await this.sendTypingIndicator(chatId);
    }

    // Normalize and forward to gateway
    const normalized = await this.normalizeMessage(waMsg);
    await this.messageHandler(normalized);

    // Mark as read
    if (this.config.features.sendReadReceipts) {
      await this.socket?.readMessages([waMsg.key]);
    }
  }

  private async normalizeMessage(waMsg: WAMessage): Promise<InboundMessage> {
    const chatId = waMsg.key.remoteJid!;
    const isGroup = chatId.endsWith("@g.us");

    // Extract text (handle different message types)
    let text = "";
    let attachments: Attachment[] = [];

    if (waMsg.message?.conversation) {
      text = waMsg.message.conversation;
    } else if (waMsg.message?.extendedTextMessage) {
      text = waMsg.message.extendedTextMessage.text || "";
    } else if (waMsg.message?.audioMessage) {
      // Voice message - transcribe if enabled
      if (this.config.features.voiceTranscription) {
        text = await this.transcribeAudio(waMsg);
      }
      attachments.push({ type: "audio", placeholder: "<voice message>" });
    } else if (waMsg.message?.imageMessage) {
      attachments.push({
        type: "image",
        caption: waMsg.message.imageMessage.caption
      });
    }

    // Handle quoted replies
    let replyTo: InboundMessage["content"]["replyTo"] | undefined;
    const quoted = waMsg.message?.extendedTextMessage?.contextInfo?.quotedMessage;
    if (quoted) {
      replyTo = {
        messageId: waMsg.message?.extendedTextMessage?.contextInfo?.stanzaId || "",
        quotedText: quoted.conversation || quoted.extendedTextMessage?.text,
      };
    }

    return {
      id: waMsg.key.id!,
      timestamp: new Date(waMsg.messageTimestamp as number * 1000),
      channel: "whatsapp",
      chatId: chatId,
      chatType: isGroup ? "group" : "dm",
      sender: {
        id: this.normalizeUserId(this.extractSenderId(waMsg)),
        phone: this.extractSenderId(waMsg),
        displayName: waMsg.pushName || undefined,
      },
      content: {
        text: text,
        attachments: attachments.length > 0 ? attachments : undefined,
        replyTo: replyTo,
      },
    };
  }

  async send(message: OutboundMessage): Promise<SendResult> {
    if (!this.socket) {
      return { success: false, error: "Not connected" };
    }

    try {
      // Chunk long messages
      const chunks = this.chunkMessage(message.content, this.config.messages.maxLength);

      for (const chunk of chunks) {
        await this.socket.sendMessage(message.chatId, { text: chunk });
      }

      return { success: true, messageId: Date.now().toString() };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async sendTypingIndicator(chatId: string): Promise<void> {
    await this.socket?.sendPresenceUpdate("composing", chatId);
  }

  async disconnect(): Promise<void> {
    this.socket?.end(undefined);
    this.connected = false;
  }

  // Helper methods
  private extractSenderId(msg: WAMessage): string {
    if (msg.key.remoteJid?.endsWith("@g.us")) {
      return msg.key.participant || msg.key.remoteJid;
    }
    return msg.key.remoteJid!.replace("@s.whatsapp.net", "");
  }

  private chunkMessage(text: string, maxLength: number): string[] {
    if (text.length <= maxLength) return [text];

    const chunks: string[] = [];
    let remaining = text;

    while (remaining.length > 0) {
      if (remaining.length <= maxLength) {
        chunks.push(remaining);
        break;
      }

      // Find good break point (newline or space)
      let breakPoint = remaining.lastIndexOf("\n", maxLength);
      if (breakPoint === -1) breakPoint = remaining.lastIndexOf(" ", maxLength);
      if (breakPoint === -1) breakPoint = maxLength;

      chunks.push(remaining.slice(0, breakPoint));
      remaining = remaining.slice(breakPoint).trim();
    }

    return chunks;
  }

  async getChatContext(chatId: string): Promise<ChatContext> {
    // Get group metadata if applicable
    if (chatId.endsWith("@g.us") && this.socket) {
      const metadata = await this.socket.groupMetadata(chatId);
      return {
        chatId,
        chatType: "group",
        name: metadata.subject,
        participants: metadata.participants.map(p => p.id),
      };
    }

    return {
      chatId,
      chatType: "dm",
    };
  }

  async getUserIdentity(userId: string): Promise<UserIdentity> {
    return {
      id: this.normalizeUserId(userId),
      channel: "whatsapp",
      phone: userId,
    };
  }
}
```

---

## Discord Adapter Design

### Discord Configuration

```typescript
interface DiscordConfig {
  enabled: boolean;
  token: string;                            // Bot token

  // Access control
  accessPolicy: {
    dmPolicy: "pairing" | "allowlist" | "open" | "disabled";
    allowedUsers: string[];                 // Discord user IDs or usernames
    guildPolicy: "allowlist" | "open" | "disabled";
    allowedGuilds: {
      [guildId: string]: {
        requireMention: boolean;
        allowedChannels?: string[];         // Channel IDs or names
        allowedUsers?: string[];            // Guild-specific allowlist
      };
    };
  };

  // Features
  features: {
    typingIndicator: boolean;
    ackReaction: string | null;             // Emoji to react with
    useEmbeds: boolean;                     // Rich embeds for responses
    useThreads: boolean;                    // Reply in threads
  };

  // Message handling
  messages: {
    maxLength: number;                      // Default: 2000 (Discord limit)
    historyLimit: number;
  };

  // Slash commands (A2I2 memory operations)
  commands: {
    enabled: boolean;
    register: {
      recall: boolean;                      // /recall <query>
      learn: boolean;                       // /learn <statement>
      status: boolean;                      // /status
      preferences: boolean;                 // /preferences
    };
  };
}
```

### Discord Adapter Implementation

```typescript
import {
  Client,
  GatewayIntentBits,
  Message,
  Events,
  REST,
  Routes,
  SlashCommandBuilder
} from "discord.js";

class DiscordAdapter extends BaseChannelAdapter {
  readonly name = "discord";
  readonly type = "messaging" as const;

  private client: Client | null = null;

  constructor(config: DiscordConfig) {
    super(config);
  }

  async connect(): Promise<void> {
    this.client = new Client({
      intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.DirectMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMessageReactions,
      ],
    });

    // Register slash commands
    if (this.config.commands.enabled) {
      await this.registerSlashCommands();
    }

    // Handle messages
    this.client.on(Events.MessageCreate, async (msg) => {
      if (msg.author.bot) return;           // Ignore bots
      await this.handleMessage(msg);
    });

    // Handle slash commands
    this.client.on(Events.InteractionCreate, async (interaction) => {
      if (!interaction.isChatInputCommand()) return;
      await this.handleSlashCommand(interaction);
    });

    // Connect
    await this.client.login(this.config.token);
    this.connected = true;
    console.log("Discord connected");
  }

  private async registerSlashCommands(): Promise<void> {
    const commands = [];

    if (this.config.commands.register.recall) {
      commands.push(
        new SlashCommandBuilder()
          .setName("recall")
          .setDescription("Search A2I2 knowledge graph")
          .addStringOption(option =>
            option.setName("query")
              .setDescription("What to search for")
              .setRequired(true)
          )
      );
    }

    if (this.config.commands.register.learn) {
      commands.push(
        new SlashCommandBuilder()
          .setName("learn")
          .setDescription("Teach A2I2 something new")
          .addStringOption(option =>
            option.setName("fact")
              .setDescription("The fact to remember")
              .setRequired(true)
          )
      );
    }

    if (this.config.commands.register.status) {
      commands.push(
        new SlashCommandBuilder()
          .setName("status")
          .setDescription("Check A2I2 memory and trust status")
      );
    }

    if (this.config.commands.register.preferences) {
      commands.push(
        new SlashCommandBuilder()
          .setName("preferences")
          .setDescription("View learned preferences")
      );
    }

    // Register commands
    const rest = new REST({ version: "10" }).setToken(this.config.token);
    await rest.put(
      Routes.applicationCommands(this.client!.user!.id),
      { body: commands.map(c => c.toJSON()) }
    );
  }

  private async handleMessage(msg: Message): Promise<void> {
    if (!this.messageHandler) return;

    const chatId = msg.channel.id;
    const isGuild = msg.guild !== null;
    const guildId = msg.guild?.id;

    // Check access
    const access = this.checkDiscordAccess(msg);
    if (!access.allowed) {
      if (access.reason === "pairing_required") {
        await msg.reply(`Pairing required. Code: \`${access.pairingCode}\``);
      }
      return;
    }

    // Check mention requirement for guilds
    if (isGuild && this.requiresMention(guildId!)) {
      const mentioned = msg.mentions.users.has(this.client!.user!.id);
      if (!mentioned) return;
    }

    // Ack reaction
    if (this.config.features.ackReaction) {
      await msg.react(this.config.features.ackReaction);
    }

    // Typing indicator
    if (this.config.features.typingIndicator) {
      await msg.channel.sendTyping();
    }

    // Normalize and forward
    const normalized = this.normalizeMessage(msg);
    await this.messageHandler(normalized);
  }

  private normalizeMessage(msg: Message): InboundMessage {
    const isGuild = msg.guild !== null;

    return {
      id: msg.id,
      timestamp: msg.createdAt,
      channel: "discord",
      chatId: msg.channel.id,
      chatType: isGuild ? "group" : "dm",
      sender: {
        id: this.normalizeUserId(msg.author.id),
        discordId: msg.author.id,
        displayName: msg.author.displayName || msg.author.username,
      },
      content: {
        text: this.stripMentions(msg.content),
        attachments: msg.attachments.map(a => ({
          type: this.getAttachmentType(a.contentType),
          url: a.url,
        })),
        replyTo: msg.reference ? {
          messageId: msg.reference.messageId || "",
        } : undefined,
      },
    };
  }

  async send(message: OutboundMessage): Promise<SendResult> {
    if (!this.client) {
      return { success: false, error: "Not connected" };
    }

    try {
      const channel = await this.client.channels.fetch(message.chatId);
      if (!channel?.isTextBased()) {
        return { success: false, error: "Invalid channel" };
      }

      // Chunk long messages
      const chunks = this.chunkMessage(message.content, this.config.messages.maxLength);

      for (const chunk of chunks) {
        if (this.config.features.useEmbeds) {
          await (channel as any).send({
            embeds: [{
              description: chunk,
              color: 0x7C3AED,               // A2I2 purple
            }],
          });
        } else {
          await (channel as any).send(chunk);
        }
      }

      return { success: true };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async sendTypingIndicator(chatId: string): Promise<void> {
    const channel = await this.client?.channels.fetch(chatId);
    if (channel?.isTextBased()) {
      await (channel as any).sendTyping();
    }
  }

  async disconnect(): Promise<void> {
    await this.client?.destroy();
    this.connected = false;
  }

  // Discord-specific access control
  private checkDiscordAccess(msg: Message): AccessDecision {
    const userId = msg.author.id;
    const isGuild = msg.guild !== null;
    const guildId = msg.guild?.id;

    if (isGuild) {
      // Guild access
      const guildConfig = this.config.accessPolicy.allowedGuilds[guildId!];
      if (this.config.accessPolicy.guildPolicy === "allowlist" && !guildConfig) {
        return { allowed: false, reason: "Guild not in allowlist" };
      }
      if (guildConfig?.allowedUsers && !guildConfig.allowedUsers.includes(userId)) {
        return { allowed: false, reason: "User not allowed in this guild" };
      }
      if (guildConfig?.allowedChannels && !guildConfig.allowedChannels.includes(msg.channel.id)) {
        return { allowed: false, reason: "Channel not allowed" };
      }
    } else {
      // DM access
      return this.checkAccess(userId, msg.channel.id);
    }

    return { allowed: true };
  }

  private requiresMention(guildId: string): boolean {
    return this.config.accessPolicy.allowedGuilds[guildId]?.requireMention ?? true;
  }

  private stripMentions(content: string): string {
    return content.replace(/<@!?\d+>/g, "").trim();
  }

  private getAttachmentType(contentType: string | null): string {
    if (!contentType) return "file";
    if (contentType.startsWith("image/")) return "image";
    if (contentType.startsWith("audio/")) return "audio";
    if (contentType.startsWith("video/")) return "video";
    return "file";
  }

  private chunkMessage(text: string, maxLength: number): string[] {
    if (text.length <= maxLength) return [text];

    const chunks: string[] = [];
    let remaining = text;

    while (remaining.length > 0) {
      if (remaining.length <= maxLength) {
        chunks.push(remaining);
        break;
      }

      let breakPoint = remaining.lastIndexOf("\n", maxLength);
      if (breakPoint === -1) breakPoint = remaining.lastIndexOf(" ", maxLength);
      if (breakPoint === -1) breakPoint = maxLength;

      chunks.push(remaining.slice(0, breakPoint));
      remaining = remaining.slice(breakPoint).trim();
    }

    return chunks;
  }

  async getChatContext(chatId: string): Promise<ChatContext> {
    const channel = await this.client?.channels.fetch(chatId);
    if (channel?.isTextBased() && "guild" in channel && channel.guild) {
      return {
        chatId,
        chatType: "group",
        name: channel.name || undefined,
        guildName: channel.guild.name,
      };
    }
    return { chatId, chatType: "dm" };
  }

  async getUserIdentity(userId: string): Promise<UserIdentity> {
    const user = await this.client?.users.fetch(userId);
    return {
      id: this.normalizeUserId(userId),
      channel: "discord",
      discordId: userId,
      displayName: user?.displayName || user?.username,
    };
  }
}
```

---

## Siri/Webhook Integration Design

### Siri Shortcut Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  Siri Shortcuts Integration                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   User: "Hey Siri, ask Arcus about my meeting tomorrow"         │
│                         │                                        │
│                         ▼                                        │
│   ┌─────────────────────────────────────────┐                   │
│   │         iOS Shortcut: "Ask Arcus"        │                   │
│   │  1. Dictate Text → captured query        │                   │
│   │  2. Get Contents of URL                  │                   │
│   │     POST https://arcus.api/siri          │                   │
│   │     { query, deviceId }                  │                   │
│   │  3. Get Dictionary Value → response      │                   │
│   │  4. Speak Text → spoken response         │                   │
│   └─────────────────────────────────────────┘                   │
│                         │                                        │
│                         ▼                                        │
│   ┌─────────────────────────────────────────┐                   │
│   │         Arcus Gateway /siri              │                   │
│   │  • Authenticate (device ID + token)      │                   │
│   │  • Inject memory context                 │                   │
│   │  • Route to model                        │                   │
│   │  • Return JSON response                  │                   │
│   └─────────────────────────────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Siri Webhook Configuration

```typescript
interface SiriWebhookConfig {
  enabled: boolean;
  path: string;                             // "/siri" or "/hooks/siri"

  // Authentication
  auth: {
    mode: "token" | "device" | "both";
    tokens?: string[];                      // Static API tokens
    allowedDevices?: string[];              // Device IDs (from Shortcuts)
  };

  // Response format
  response: {
    maxLength: number;                      // Siri speaks better with shorter responses
    includeSummary: boolean;                // Include brief summary for speech
    includeFullText: boolean;               // Include full text for display
  };

  // A2I2 Memory commands via Siri
  commands: {
    recall: {
      enabled: boolean;
      trigger: string[];                    // ["ask arcus", "what does arcus know"]
    };
    learn: {
      enabled: boolean;
      trigger: string[];                    // ["arcus remember", "teach arcus"]
    };
    status: {
      enabled: boolean;
      trigger: string[];                    // ["arcus status"]
    };
  };
}
```

### Siri Webhook Adapter Implementation

```typescript
import express, { Request, Response } from "express";

class SiriWebhookAdapter extends BaseChannelAdapter {
  readonly name = "siri";
  readonly type = "webhook" as const;

  private app: express.Application | null = null;

  constructor(config: SiriWebhookConfig) {
    super(config);
  }

  async connect(): Promise<void> {
    // Note: This adapter is mounted on the gateway's HTTP server
    // The gateway calls registerRoutes() after initialization
    this.connected = true;
  }

  // Register routes on gateway's HTTP server
  registerRoutes(app: express.Application): void {
    app.post(this.config.path, this.handleSiriRequest.bind(this));
  }

  private async handleSiriRequest(req: Request, res: Response): Promise<void> {
    try {
      const { query, deviceId, shortcutName } = req.body;

      // Authenticate
      const authResult = this.authenticateRequest(req, deviceId);
      if (!authResult.success) {
        res.status(401).json({ error: authResult.error });
        return;
      }

      // Check for special A2I2 commands
      const command = this.detectCommand(query);

      // Create normalized message
      const message: InboundMessage = {
        id: `siri-${Date.now()}`,
        timestamp: new Date(),
        channel: "siri",
        chatId: deviceId || "siri-default",
        chatType: "dm",
        sender: {
          id: this.normalizeUserId(deviceId || "anonymous"),
          deviceId: deviceId,
        },
        content: {
          text: query,
        },
        // Flag special commands
        metadata: command ? { command: command.type, ...command.params } : undefined,
      };

      // Forward to gateway
      if (this.messageHandler) {
        await this.messageHandler(message);
      }

      // ARCHITECTURE NOTE: Production Async Response Pattern
      // Siri Shortcuts have ~30s timeout. For AI responses that may take longer:
      // 1. Return immediate acknowledgment with request ID
      // 2. Process async, store response in database keyed by request ID
      // 3. Use push notification (APNs) to alert user when ready
      // 4. User taps notification → Shortcut fetches response by ID
      //
      // For MVP (sub-30s responses), synchronous is acceptable:
      const response = await this.processAndWaitForResponse(message);

      // Format for Siri
      const siriResponse = this.formatSiriResponse(response);

      res.json(siriResponse);

    } catch (error) {
      console.error("Siri webhook error:", error);
      res.status(500).json({
        response: "I encountered an error processing your request.",
        error: String(error),
      });
    }
  }

  private authenticateRequest(req: Request, deviceId?: string): { success: boolean; error?: string } {
    const config = this.config.auth;

    // Token auth - SECURITY: Only accept tokens from headers, never query params
    // Query param tokens are logged in server access logs and can leak
    if (config.mode === "token" || config.mode === "both") {
      const authHeader = req.headers.authorization;
      const token = authHeader?.startsWith("Bearer ")
        ? authHeader.slice("Bearer ".length)
        : (req.headers["x-arcus-token"] as string | undefined);

      // Ensure tokens are configured
      if (!config.tokens || config.tokens.length === 0) {
        return { success: false, error: "Token authentication not configured" };
      }

      if (!token || !config.tokens.includes(token)) {
        return { success: false, error: "Invalid or missing token" };
      }
    }

    // Device auth - NOTE: deviceId is a non-secret identifier used as additional
    // filter, not primary authentication. Always require token auth alongside.
    if (config.mode === "device" || config.mode === "both") {
      if (config.allowedDevices && !config.allowedDevices.includes(deviceId || "")) {
        return { success: false, error: "Device not authorized" };
      }
    }

    return { success: true };
  }

  private detectCommand(query: string): { type: string; params: any } | null {
    const lowerQuery = query.toLowerCase();
    const commands = this.config.commands;

    // Recall command
    if (commands.recall.enabled) {
      for (const trigger of commands.recall.trigger) {
        if (lowerQuery.includes(trigger)) {
          return {
            type: "recall",
            params: { query: query.replace(new RegExp(trigger, "i"), "").trim() },
          };
        }
      }
    }

    // Learn command
    if (commands.learn.enabled) {
      for (const trigger of commands.learn.trigger) {
        if (lowerQuery.includes(trigger)) {
          return {
            type: "learn",
            params: { fact: query.replace(new RegExp(trigger, "i"), "").trim() },
          };
        }
      }
    }

    // Status command
    if (commands.status.enabled) {
      for (const trigger of commands.status.trigger) {
        if (lowerQuery.includes(trigger)) {
          return { type: "status", params: {} };
        }
      }
    }

    return null;
  }

  private formatSiriResponse(response: string): SiriWebhookResponse {
    const maxLength = this.config.response.maxLength || 500;

    // Shorten for speech
    let speechText = response;
    if (speechText.length > maxLength) {
      speechText = speechText.slice(0, maxLength - 3) + "...";
    }

    return {
      response: speechText,                 // Siri speaks this
      displayText: this.config.response.includeFullText ? response : undefined,
      success: true,
    };
  }

  // Simplified - real implementation would use event-based response
  private async processAndWaitForResponse(message: InboundMessage): Promise<string> {
    // This would integrate with the gateway's response queue
    return "Response from A2I2 gateway";
  }

  async send(message: OutboundMessage): Promise<SendResult> {
    // Webhook adapter doesn't send - responses are returned inline
    return { success: true };
  }

  async disconnect(): Promise<void> {
    this.connected = false;
  }

  async getChatContext(chatId: string): Promise<ChatContext> {
    return { chatId, chatType: "dm" };
  }

  async getUserIdentity(userId: string): Promise<UserIdentity> {
    return {
      id: this.normalizeUserId(userId),
      channel: "siri",
      deviceId: userId,
    };
  }
}

// Response types
interface SiriWebhookRequest {
  query: string;
  deviceId?: string;
  shortcutName?: string;
  timestamp?: string;
}

interface SiriWebhookResponse {
  response: string;                         // Text for Siri to speak
  displayText?: string;                     // Full text for notification
  success: boolean;
  error?: string;
}
```

### iOS Shortcut Template

```
Shortcut Name: "Ask Arcus"

Actions:
1. Dictate Text
   - Stop Listening: After Pause
   - Language: Default
   → Save to variable "Query"

2. URL
   - https://your-arcus-gateway.example.com/siri

3. Get Contents of URL
   - Method: POST
   - Headers:
     - Authorization: Bearer YOUR_API_TOKEN
     - Content-Type: application/json
   - Request Body: JSON
     {
       "query": [Query variable],
       "deviceId": [Get Device Details → Name],
       "shortcutName": "Ask Arcus"
     }
   → Save to variable "Response"

4. Get Dictionary Value
   - Key: response
   - Dictionary: [Response variable]
   → Save to variable "Answer"

5. Speak Text
   - Text: [Answer variable]
   - Rate: Default
   - Voice: Siri voice

6. Show Notification (Optional)
   - Title: Arcus
   - Body: [Answer variable]
```

---

## Security & Access Control

### Access Control Design

```typescript
// Unified access control across all channels
interface AccessControlConfig {
  // Default policy
  defaultPolicy: {
    dmPolicy: "pairing" | "allowlist" | "open" | "disabled";
    groupPolicy: "allowlist" | "open" | "disabled";
  };

  // Pairing system
  pairing: {
    enabled: boolean;
    codeLength: number;                     // Default: 6
    expiryMinutes: number;                  // Default: 60
    maxPending: number;                     // Max pending requests per channel
  };

  // Master allowlist (cross-channel)
  masterAllowlist: {
    users: string[];                        // Canonical user IDs
    admins: string[];                       // Can approve pairings
  };

  // A2I2 Trust Integration
  trustIntegration: {
    enabled: boolean;
    minTrustForDM: AutonomyLevel;           // L0 by default
    minTrustForGroup: AutonomyLevel;        // L0 by default
    autoElevatePaired: boolean;             // Paired users start at L1
  };
}
```

### Pairing Flow

```typescript
// Pairing request management
// NOTE: Production implementation should persist pending requests to database
// (e.g., Supabase arcus_pairing_requests table) to survive restarts.
// The in-memory Map shown here is for illustration only.
class PairingManager {
  private pendingRequests: Map<string, PairingRequest> = new Map();
  // TODO: Inject database client for persistent storage
  // private db: SupabaseClient;

  async createPairingRequest(
    userId: string,
    channel: string
  ): Promise<string> {
    const code = this.generateCode();
    const request: PairingRequest = {
      userId,
      channel,
      code,
      requestedAt: new Date(),
      expiresAt: new Date(Date.now() + 60 * 60 * 1000), // 1 hour
      status: "pending",
    };

    this.pendingRequests.set(code, request);
    return code;
  }

  async approvePairing(code: string, approvedBy: string): Promise<boolean> {
    const request = this.pendingRequests.get(code);
    if (!request || request.status !== "pending") {
      return false;
    }

    if (request.expiresAt < new Date()) {
      request.status = "expired";
      return false;
    }

    request.status = "approved";

    // Add to allowlist
    await this.addToAllowlist(request.userId, request.channel);

    // Log to ATL
    await this.trustLedger.logPairingApproval({
      userId: request.userId,
      approvedBy,
      channel: request.channel,
    });

    return true;
  }

  private generateCode(): string {
    // Use cryptographically secure random for pairing codes
    const crypto = require("crypto");
    const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // No ambiguous chars
    const randomBytes = crypto.randomBytes(6);
    let code = "";
    for (let i = 0; i < 6; i++) {
      code += chars[randomBytes[i] % chars.length];
    }
    return code;
  }
}
```

---

## A2I2 Concept Mapping

### Memory Integration

| A2I2 Memory Type | Channel Integration |
|------------------|---------------------|
| **Episodic** | Every message logged with channel/sender context |
| **Semantic** | Facts extracted from conversations, stored with source |
| **Procedural** | Workflow preferences learned from user corrections |
| **Working** | Current session context, injected per-message |
| **Relational** | Entity mentions extracted and linked to knowledge graph |

### Memory Context Injection

```typescript
// Inject memory context before each AI response
async function injectMemoryContext(
  message: InboundMessage,
  memoryLayer: A2I2MemoryLayer
): Promise<InboundMessage> {

  // 1. Get recent episodic memories (what happened recently)
  const recentEpisodes = await memoryLayer.queryEpisodic({
    userId: message.sender.id,
    limit: 10,
    since: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // Last 7 days
  });

  // 2. Get relevant semantic facts (based on message content)
  const relevantFacts = await memoryLayer.querySemantic({
    query: message.content.text,
    limit: 20,
  });

  // 3. Get user's procedural preferences
  const userPreferences = await memoryLayer.queryProcedural({
    userId: message.sender.id,
    category: "preferences",
  });

  // 4. Extract entities and get relationships
  const entities = extractEntities(message.content.text);
  const relationships = await memoryLayer.queryKnowledgeGraph({
    entities: entities,
    depth: 2,
  });

  // 5. Inject into message
  message.memoryContext = {
    recentEpisodes,
    relevantSemantics: relevantFacts,
    userPreferences,
    entityRelationships: relationships,
  };

  return message;
}
```

### Autonomy Trust Ledger Integration

```typescript
// Log all channel interactions to ATL
interface ATLChannelLog {
  userId: string;
  channel: string;
  action: "message_received" | "response_sent" | "command_executed" | "learning_captured";
  autonomyLevel: AutonomyLevel;
  details: {
    messageId?: string;
    commandType?: string;
    learningType?: string;
  };
  timestamp: Date;
  successful: boolean;
}

// Trust-based action gating
async function checkTrustForAction(
  userId: string,
  action: string,
  trustLedger: AutonomyTrustLedger
): Promise<{ allowed: boolean; reason?: string }> {

  const userTrust = await trustLedger.getUserTrust(userId);

  // Define required trust levels for actions
  const trustRequirements: Record<string, AutonomyLevel> = {
    "read_memory": "L0",
    "basic_conversation": "L0",
    "learn_fact": "L1",
    "modify_preference": "L1",
    "execute_workflow": "L2",
    "modify_knowledge_graph": "L2",
    "autonomous_action": "L3",
  };

  const required = trustRequirements[action] || "L0";

  if (compareTrustLevels(userTrust.level, required) < 0) {
    return {
      allowed: false,
      reason: `Action requires ${required}, user has ${userTrust.level}`,
    };
  }

  return { allowed: true };
}
```

### Memory Operations via Chat Commands

| Command | A2I2 Operation | Description |
|---------|----------------|-------------|
| `/recall <query>` | RECALL | Search knowledge graph |
| `/learn <fact>` | LEARN | Capture explicit knowledge |
| `/forget <topic>` | (delete) | Request knowledge removal |
| `/preferences` | RECALL | Show learned preferences |
| `/status` | (query) | Show memory stats + trust level |
| `/reflect` | REFLECT | Trigger pattern synthesis |
| `/new` | (reset) | Start fresh session (memory persists) |

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

- [ ] **Gateway Core**
  - [ ] WebSocket + HTTP server setup
  - [ ] Configuration schema and loading
  - [ ] Basic logging and error handling

- [ ] **Memory Layer Connection**
  - [ ] Supabase client setup
  - [ ] Memory query functions (RECALL)
  - [ ] Memory write functions (LEARN)

- [ ] **Siri Webhook (MVP)**
  - [ ] HTTP endpoint for Shortcuts
  - [ ] Basic auth (token)
  - [ ] iOS Shortcut template

### Phase 2: WhatsApp (Weeks 3-4)

- [ ] **WhatsApp Adapter**
  - [ ] Baileys integration
  - [ ] QR code auth flow
  - [ ] Message send/receive
  - [ ] Access control (allowlist)

- [ ] **Memory Integration**
  - [ ] Context injection per message
  - [ ] Episodic logging
  - [ ] User preference tracking

### Phase 3: Discord (Weeks 5-6)

- [ ] **Discord Adapter**
  - [ ] Bot creation + intents
  - [ ] Guild/channel configuration
  - [ ] Slash commands (/recall, /learn)
  - [ ] Reaction-based feedback

- [ ] **Multi-Channel Identity**
  - [ ] Identity linking across channels
  - [ ] Unified session management
  - [ ] Cross-channel memory queries

### Phase 4: Polish & ATL (Weeks 7-8)

- [ ] **Autonomy Trust Ledger**
  - [ ] Action logging
  - [ ] Trust level tracking
  - [ ] Trust-based gating

- [ ] **Heartbeat (REFLECT)**
  - [ ] Scheduled heartbeat
  - [ ] Pattern synthesis
  - [ ] Proactive notifications

- [ ] **Pairing System**
  - [ ] Pairing code generation
  - [ ] Admin approval flow
  - [ ] Trust elevation on pairing

---

## Summary

This document provides the architectural blueprints for A2I2's native multi-channel gateway, inspired by Clawdbot's proven patterns:

1. **Unified Gateway**: Single control plane for all channels
2. **Channel Adapters**: Pluggable adapters for WhatsApp, Discord, Siri
3. **Memory Integration**: A2I2's five memory types injected per-message
4. **Trust Integration**: ATL-based access control and action gating
5. **Identity Linking**: Same person recognized across channels

**Key Differentiator**: While Clawdbot focuses on accessibility, A2I2 adds deep organizational intelligence through persistent memory, knowledge graphs, and autonomy tracking.

---

*"Meet users where they are, remember everything, and grow with every interaction."*
