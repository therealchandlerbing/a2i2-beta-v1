# Clawdbot Technical Reference for A2I2 Implementation

**Version:** 1.0.0
**Last Updated:** 2026-01-26
**Source:** https://docs.clawd.bot/
**Purpose:** Complete technical reference for implementing A2I2 agent with Clawdbot infrastructure

---

## Table of Contents

1. [Gateway Configuration Reference](#gateway-configuration-reference)
2. [Channel Configuration Details](#channel-configuration-details)
3. [Agent Configuration Reference](#agent-configuration-reference)
4. [Session & Memory Management](#session--memory-management)
5. [Tools & Sandbox Configuration](#tools--sandbox-configuration)
6. [Model Provider Configuration](#model-provider-configuration)
7. [Webhooks & Automation](#webhooks--automation)
8. [Message Handling Configuration](#message-handling-configuration)
9. [CLI Commands Reference](#cli-commands-reference)
10. [A2I2 Implementation Checklist](#a2i2-implementation-checklist)

---

## Gateway Configuration Reference

### File Location
```
~/.clawdbot/clawdbot.json
```
Format: JSON5 (comments + trailing commas allowed)

### Complete Gateway Configuration

```json5
{
  // Gateway server settings
  gateway: {
    mode: "local",                    // "local" | "remote"
    port: 18789,                      // WebSocket + HTTP multiplex port
    bind: "loopback",                 // "loopback" | "lan" | "tailnet"

    // Authentication
    auth: {
      mode: "token",                  // "token" | "password"
      token: "your-shared-token",
      password: "your-password",      // Or use CLAWDBOT_GATEWAY_PASSWORD env
      allowTailscale: true            // Allow Tailscale Serve identity
    },

    // Control UI settings
    controlUi: {
      enabled: true,
      basePath: "/",                  // URL prefix: "/ui", "/clawdbot", etc.
      allowInsecureAuth: false,
      dangerouslyDisableDeviceAuth: false
    },

    // Tailscale integration
    tailscale: {
      mode: "off",                    // "off" | "serve" | "funnel"
      resetOnExit: false
    },

    // Hot reload settings
    reload: {
      mode: "hybrid",                 // "hybrid" | "hot" | "restart" | "off"
      debounceMs: 300
    },

    // Remote client defaults (for CLI)
    remote: {
      url: "ws://gateway.tailnet:18789",
      transport: "ssh",               // "ssh" | "direct"
      token: "remote-token",
      password: "remote-password"
    },

    // Trusted reverse proxies
    trustedProxies: ["10.0.0.1", "192.168.1.1"],

    // HTTP endpoints
    http: {
      endpoints: {
        chatCompletions: { enabled: false }  // OpenAI-compatible endpoint
      }
    }
  },

  // Logging configuration
  logging: {
    level: "info",                    // "debug" | "info" | "warn" | "error"
    file: "/tmp/clawdbot/clawdbot.log",
    consoleLevel: "info",
    consoleStyle: "pretty",           // "pretty" | "compact" | "json"
    redactSensitive: "tools",         // "off" | "tools"
    redactPatterns: [
      "\\bTOKEN\\b\\s*[=:]\\s*([\"']?)([^\\s\"']+)\\1"
    ]
  },

  // Environment variables
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: {
      GROQ_API_KEY: "gsk-..."
    },
    shellEnv: {
      enabled: true,
      timeoutMs: 15000
    }
  },

  // UI appearance
  ui: {
    seamColor: "#FF4500",             // Hex color for UI chrome
    assistant: {
      name: "Clawdbot",
      avatar: "CB"                    // Emoji, text, URL, or data URI
    }
  }
}
```

### Default Ports

| Service | Port | Description |
|---------|------|-------------|
| Gateway (WS + HTTP) | 18789 | Main control plane |
| Browser CDP | 18792 | Chrome DevTools Protocol |
| Canvas Host | 18793 | HTML/CSS/JS serving |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `CLAWDBOT_CONFIG_PATH` | Custom config file path |
| `CLAWDBOT_STATE_DIR` | State directory (~/.clawdbot) |
| `CLAWDBOT_GATEWAY_PORT` | Override gateway port |
| `CLAWDBOT_GATEWAY_TOKEN` | Gateway auth token |
| `CLAWDBOT_GATEWAY_PASSWORD` | Gateway auth password |
| `CLAWDBOT_AGENT_DIR` | Agent directory override |
| `CLAWDBOT_OAUTH_DIR` | OAuth credentials directory |
| `CLAWDBOT_LOAD_SHELL_ENV` | Enable shell env loading |
| `CLAWDBOT_SKIP_GMAIL_WATCHER` | Disable Gmail auto-watcher |
| `CLAWDBOT_SKIP_CANVAS_HOST` | Disable canvas host |

---

## Channel Configuration Details

### WhatsApp Configuration

**Transport:** WhatsApp Web via Baileys

```json5
{
  channels: {
    whatsapp: {
      // DM access control
      dmPolicy: "pairing",            // "pairing" | "allowlist" | "open" | "disabled"
      allowFrom: ["+15555550123"],    // E.164 phone numbers
      selfChatMode: true,             // Enable for personal number usage

      // Read receipts
      sendReadReceipts: true,         // Blue ticks on message read

      // Message formatting
      textChunkLimit: 4000,           // Max chars per message
      chunkMode: "length",            // "length" | "newline"
      mediaMaxMb: 50,                 // Inbound media cap

      // Config writes permission
      configWrites: true,             // Allow /config set|unset

      // Multi-account support
      accounts: {
        default: {},
        personal: {
          sendReadReceipts: false,    // Per-account override
          mediaMaxMb: 100
        },
        biz: {
          // authDir: "~/.clawdbot/credentials/whatsapp/biz"
        }
      },

      // Group settings
      groupPolicy: "allowlist",       // "open" | "disabled" | "allowlist"
      groupAllowFrom: ["+15551234567"],
      groups: {
        "*": { requireMention: true },
        "120363403215116621@g.us": {
          requireMention: false,
          allowFrom: ["@admin"]
        }
      },

      // History context
      historyLimit: 50,               // Group messages to include as context
      dmHistoryLimit: 30,             // DM history limit in user turns
      dms: {
        "+15551234567": { historyLimit: 50 }  // Per-user override
      },

      // Acknowledgment reactions
      ackReaction: {
        emoji: "👀",
        direct: true,
        group: "mentions"             // "always" | "mentions" | "never"
      },

      // Tool actions
      actions: {
        reactions: true
      },

      // Message prefix (inbound)
      messagePrefix: "",              // Or "[clawdbot]"

      // Block streaming
      blockStreaming: false,
      blockStreamingCoalesce: {
        idleMs: 1000,
        minChars: 800,
        maxChars: 4000
      }
    }
  }
}
```

**Credentials Storage:**
```
~/.clawdbot/credentials/whatsapp/<accountId>/creds.json
~/.clawdbot/credentials/whatsapp/<accountId>/creds.json.bak
```

**CLI Commands:**
```bash
clawdbot channels login                    # QR code login
clawdbot channels login --account personal # Multi-account
clawdbot channels logout
clawdbot channels logout --account personal
clawdbot channels status
clawdbot channels status --probe
```

### Telegram Configuration

**Transport:** Bot API via grammY

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "123456:ABC...",      // Or TELEGRAM_BOT_TOKEN env
      // tokenFile: "/path/to/token", // Alternative: file-based token

      // DM access control
      dmPolicy: "pairing",            // "pairing" | "allowlist" | "open" | "disabled"
      allowFrom: ["tg:123456789", "@username"],

      // Group settings
      groupPolicy: "allowlist",
      groupAllowFrom: ["tg:123456789"],
      groups: {
        "*": { requireMention: true },
        "-1001234567890": {
          allowFrom: ["@admin"],
          systemPrompt: "Keep answers brief.",
          topics: {
            "99": {
              requireMention: false,
              skills: ["search"],
              systemPrompt: "Stay on topic."
            }
          }
        }
      },

      // Custom bot menu commands
      customCommands: [
        { command: "backup", description: "Git backup" },
        { command: "generate", description: "Create an image" }
      ],

      // History and context
      historyLimit: 50,
      dmHistoryLimit: 30,

      // Reply threading
      replyToMode: "first",           // "off" | "first" | "all"
      linkPreview: true,

      // Draft streaming (experimental)
      streamMode: "partial",          // "off" | "partial" | "block"
      draftChunk: {
        minChars: 200,
        maxChars: 800,
        breakPreference: "paragraph"  // "paragraph" | "newline" | "sentence"
      },

      // Tool actions
      actions: {
        reactions: true,
        sendMessage: true
      },

      // Reaction notifications
      reactionNotifications: "own",   // "off" | "own" | "all"

      // Media limits
      mediaMaxMb: 5,

      // Retry policy
      retry: {
        attempts: 3,
        minDelayMs: 400,
        maxDelayMs: 30000,
        jitter: 0.1
      },

      // Webhook mode (alternative to polling)
      webhookUrl: "https://example.com/telegram-webhook",
      webhookSecret: "secret",
      webhookPath: "/telegram-webhook",

      // Proxy support
      proxy: "socks5://localhost:9050",

      // Config writes permission
      configWrites: true,

      // Multi-account
      accounts: {
        default: {
          name: "Primary bot",
          botToken: "123456:ABC..."
        },
        alerts: {
          name: "Alerts bot",
          botToken: "987654:XYZ..."
        }
      }
    }
  }
}
```

### Discord Configuration

**Transport:** Official Discord Bot Gateway

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "YOUR_BOT_TOKEN",        // Or DISCORD_BOT_TOKEN env

      // Media handling
      mediaMaxMb: 8,
      allowBots: false,               // Allow bot-authored messages

      // DM settings
      dm: {
        enabled: true,
        policy: "pairing",            // "pairing" | "allowlist" | "open" | "disabled"
        allowFrom: ["1234567890", "username"],
        groupEnabled: false,          // Group DMs
        groupChannels: ["clawd-dm"]   // Group DM allowlist
      },

      // Group/guild policy
      groupPolicy: "allowlist",       // "open" | "disabled" | "allowlist"

      // Guild-specific settings
      guilds: {
        "*": { requireMention: true },
        "123456789012345678": {
          slug: "friends-of-clawd",
          requireMention: false,
          reactionNotifications: "own",  // "off" | "own" | "all" | "allowlist"
          users: ["987654321098765432"],
          channels: {
            general: { allow: true },
            help: {
              allow: true,
              enabled: true,
              requireMention: true,
              users: ["987654321098765432"],
              skills: ["docs"],
              systemPrompt: "Short answers only."
            }
          }
        }
      },

      // Tool actions
      actions: {
        reactions: true,
        stickers: true,
        emojiUploads: true,
        stickerUploads: true,
        polls: true,
        permissions: true,
        messages: true,
        threads: true,
        pins: true,
        search: true,
        memberInfo: true,
        roleInfo: true,
        channelInfo: true,
        channels: true,
        voiceStatus: true,
        events: true,
        roles: false,                 // Disabled by default
        moderation: false             // Disabled by default
      },

      // Reply threading
      replyToMode: "off",             // "off" | "first" | "all"

      // History and context
      historyLimit: 20,
      dmHistoryLimit: 30,

      // Message formatting
      textChunkLimit: 2000,
      chunkMode: "length",            // "length" | "newline"
      maxLinesPerMessage: 17,

      // Native commands
      commands: {
        native: "auto"                // true | false | "auto"
      },

      // Retry policy
      retry: {
        attempts: 3,
        minDelayMs: 500,
        maxDelayMs: 30000,
        jitter: 0.1
      },

      // Config writes permission
      configWrites: true
    }
  }
}
```

**Required Discord Developer Portal Settings:**
1. Enable **Message Content Intent** (required)
2. Enable **Server Members Intent** (recommended)
3. Bot Permissions: View Channels, Send Messages, Read Message History, Embed Links, Attach Files, Add Reactions

### Slack Configuration

**Transport:** Socket Mode

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: "xoxb-...",           // Or SLACK_BOT_TOKEN env
      appToken: "xapp-...",           // Or SLACK_APP_TOKEN env

      // DM settings
      dm: {
        enabled: true,
        policy: "pairing",
        allowFrom: ["U123", "U456"],
        groupEnabled: false,
        groupChannels: ["G123"]
      },

      // Channel settings
      groupPolicy: "allowlist",
      channels: {
        C123: { allow: true, requireMention: true, allowBots: false },
        "#general": {
          allow: true,
          requireMention: true,
          allowBots: false,
          users: ["U123"],
          skills: ["docs"],
          systemPrompt: "Short answers only."
        }
      },

      // History and context
      historyLimit: 50,
      dmHistoryLimit: 30,

      // Bot messages
      allowBots: false,

      // Reaction notifications
      reactionNotifications: "own",   // "off" | "own" | "all" | "allowlist"
      reactionAllowlist: ["U123"],

      // Reply threading
      replyToMode: "off",

      // Thread behavior
      thread: {
        historyScope: "thread",       // "thread" | "channel"
        inheritParent: false
      },

      // Tool actions
      actions: {
        reactions: true,
        messages: true,
        pins: true,
        memberInfo: true,
        emojiList: true
      },

      // Slash command
      slashCommand: {
        enabled: true,
        name: "clawd",
        sessionPrefix: "slack:slash",
        ephemeral: true
      },

      // Message formatting
      textChunkLimit: 4000,
      chunkMode: "length",
      mediaMaxMb: 20,

      // Config writes permission
      configWrites: true
    }
  }
}
```

### Signal Configuration

**Transport:** signal-cli

```json5
{
  channels: {
    signal: {
      // Reaction notifications
      reactionNotifications: "own",   // "off" | "own" | "all" | "allowlist"
      reactionAllowlist: ["+15551234567", "uuid:123e4567-..."],

      // History context
      historyLimit: 50,

      // DM settings
      dmPolicy: "pairing",
      allowFrom: ["+15551234567"],

      // Group settings
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"]
    }
  }
}
```

### iMessage Configuration

**Transport:** imsg CLI (macOS only)

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "imsg",                // Path to imsg CLI
      dbPath: "~/Library/Messages/chat.db",
      remoteHost: "user@gateway-host", // For SSH wrapper SCP

      // DM settings
      dmPolicy: "pairing",
      allowFrom: ["+15555550123", "user@example.com", "chat_id:123"],

      // History context
      historyLimit: 50,

      // Media handling
      includeAttachments: false,
      mediaMaxMb: 16,

      // Service settings
      service: "auto",                // "auto" | "iMessage" | "SMS"
      region: "US",

      // Group settings
      groupPolicy: "allowlist",
      groupAllowFrom: ["chat_id:123"],
      groups: {
        "*": { requireMention: true }
      }
    }
  }
}
```

### Google Chat Configuration

**Transport:** Chat API webhook

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      // serviceAccount: {...},       // Inline JSON alternative
      audienceType: "app-url",        // "app-url" | "project-number"
      audience: "https://gateway.example.com/googlechat",
      webhookPath: "/googlechat",
      botUser: "users/1234567890",

      // DM settings
      dm: {
        enabled: true,
        policy: "pairing",
        allowFrom: ["users/1234567890"]
      },

      // Group settings
      groupPolicy: "allowlist",
      groups: {
        "spaces/AAAA": { allow: true, requireMention: true }
      },

      // Tool actions
      actions: { reactions: true },

      // Typing indicator
      typingIndicator: "message",     // "never" | "message"

      // Media limits
      mediaMaxMb: 20
    }
  }
}
```

### Microsoft Teams Configuration

```json5
{
  channels: {
    msteams: {
      // Group settings
      groupPolicy: "allowlist",
      groupAllowFrom: ["user@org.com"],

      // DM settings
      dmPolicy: "pairing",
      allowFrom: ["user@org.com"]
    }
  }
}
```

### Mattermost Configuration

**Note:** Requires plugin: `clawdbot plugins install @clawdbot/mattermost`

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",           // Or MATTERMOST_BOT_TOKEN env
      baseUrl: "https://chat.example.com", // Or MATTERMOST_URL env

      // DM settings
      dmPolicy: "pairing",
      allowFrom: ["username"],

      // Chat mode
      chatmode: "oncall",             // "oncall" | "onmessage" | "onchar"
      oncharPrefixes: [">", "!"],

      // Group settings
      groupPolicy: "allowlist",
      groupAllowFrom: ["username"],

      // Message formatting
      textChunkLimit: 4000,
      chunkMode: "length"
    }
  }
}
```

### Channel Defaults

```json5
{
  channels: {
    defaults: {
      groupPolicy: "allowlist"        // Default for all channels
    }
  }
}
```

---

## Agent Configuration Reference

### Complete Agent Configuration

```json5
{
  agents: {
    // Default settings for all agents
    defaults: {
      workspace: "~/clawd",
      repoRoot: "~/Projects/clawdbot",
      skipBootstrap: false,
      bootstrapMaxChars: 20000,
      userTimezone: "America/Chicago",
      timeFormat: "auto",             // "auto" | "12" | "24"

      // Model configuration
      model: {
        primary: "anthropic/claude-opus-4-5",
        fallbacks: ["minimax/MiniMax-M2.1"]
      },

      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
        fallbacks: ["openrouter/google/gemini-2.0-flash-vision:free"]
      },

      // Model catalog with aliases and params
      models: {
        "anthropic/claude-opus-4-5": { alias: "Opus" },
        "anthropic/claude-sonnet-4-5": {
          alias: "Sonnet",
          params: { temperature: 0.6 }
        },
        "openai/gpt-5.2": {
          alias: "gpt",
          params: { maxTokens: 8192 }
        },
        "zai/glm-4.7": {
          alias: "GLM",
          params: {
            thinking: { type: "enabled", clear_thinking: false }
          }
        }
      },

      // Thinking/reasoning defaults
      thinkingDefault: "low",         // "off" | "low" | "medium" | "high"
      verboseDefault: "off",
      elevatedDefault: "on",

      // Timeouts and limits
      timeoutSeconds: 600,
      mediaMaxMb: 5,
      maxConcurrent: 3,
      contextTokens: 200000,

      // Heartbeat configuration
      heartbeat: {
        every: "30m",                 // Duration: ms, s, m, h
        target: "last",               // "last" | "whatsapp" | "telegram" | "discord" | "none"
        to: "+15555550123",           // Optional recipient override
        session: "main",
        model: "openai/gpt-5.2-mini", // Optional model override
        includeReasoning: false,
        prompt: "Read HEARTBEAT.md. Reply HEARTBEAT_OK if nothing needs attention.",
        ackMaxChars: 300
      },

      // Sub-agent defaults
      subagents: {
        model: "minimax/MiniMax-M2.1",
        maxConcurrent: 1,
        archiveAfterMinutes: 60
      },

      // Execution settings
      exec: {
        backgroundMs: 10000,
        timeoutSec: 1800,
        cleanupMs: 1800000
      },

      // Context pruning
      contextPruning: {
        mode: "adaptive",             // "off" | "adaptive" | "aggressive"
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
        minPrunableToolChars: 50000,
        softTrim: { maxChars: 4000, headChars: 1500, tailChars: 1500 },
        hardClear: {
          enabled: true,
          placeholder: "[Old tool result content cleared]"
        },
        tools: { deny: ["browser", "canvas"] }
      },

      // Compaction (memory flush)
      compaction: {
        mode: "safeguard",            // "default" | "safeguard"
        reserveTokensFloor: 24000,
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY."
        }
      },

      // Block streaming
      blockStreamingDefault: "off",   // "on" | "off"
      blockStreamingBreak: "text_end", // "text_end" | "message_end"
      blockStreamingChunk: {
        minChars: 800,
        maxChars: 1200,
        breakPreference: "paragraph"
      },
      blockStreamingCoalesce: {
        idleMs: 1000,
        minChars: 800
      },

      // Human-like delay
      humanDelay: {
        mode: "off",                  // "off" | "natural" | "custom"
        minMs: 800,
        maxMs: 2500
      },

      // Typing indicators
      typingMode: "instant",          // "never" | "instant" | "thinking" | "message"
      typingIntervalSeconds: 6,

      // CLI backends (fallback)
      cliBackends: {
        "claude-cli": {
          command: "/opt/homebrew/bin/claude"
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          modelArg: "--model",
          sessionArg: "--session",
          sessionMode: "existing",
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat"
        }
      },

      // Sandbox configuration
      sandbox: {
        mode: "non-main",             // "off" | "non-main" | "all"
        scope: "agent",               // "session" | "agent" | "shared"
        workspaceAccess: "none",      // "none" | "ro" | "rw"
        workspaceRoot: "~/.clawdbot/sandboxes",

        docker: {
          image: "clawdbot-sandbox:bookworm-slim",
          containerPrefix: "clawdbot-sbx-",
          workdir: "/workspace",
          readOnlyRoot: true,
          tmpfs: ["/tmp", "/var/tmp", "/run"],
          network: "none",
          user: "1000:1000",
          capDrop: ["ALL"],
          env: { LANG: "C.UTF-8" },
          setupCommand: "apt-get update && apt-get install -y git curl jq",
          pidsLimit: 256,
          memory: "1g",
          memorySwap: "2g",
          cpus: 1,
          ulimits: {
            nofile: { soft: 1024, hard: 2048 },
            nproc: 256
          },
          seccompProfile: "/path/to/seccomp.json",
          apparmorProfile: "clawdbot-sandbox",
          dns: ["1.1.1.1", "8.8.8.8"],
          extraHosts: ["internal.service:10.0.0.5"],
          binds: ["/var/run/docker.sock:/var/run/docker.sock"]
        },

        browser: {
          enabled: false,
          image: "clawdbot-sandbox-browser:bookworm-slim",
          containerPrefix: "clawdbot-sbx-browser-",
          cdpPort: 9222,
          vncPort: 5900,
          noVncPort: 6080,
          headless: false,
          enableNoVnc: true,
          allowHostControl: false,
          autoStart: true,
          autoStartTimeoutMs: 12000
        },

        prune: {
          idleHours: 24,
          maxAgeDays: 7
        }
      }
    },

    // Multi-agent list
    list: [
      {
        id: "main",
        default: true,
        name: "Main Agent",
        workspace: "~/clawd",
        agentDir: "~/.clawdbot/agents/main/agent",

        // Identity
        identity: {
          name: "Samantha",
          theme: "helpful sloth",
          emoji: "🦥",
          avatar: "avatars/samantha.png"
        },

        // Per-agent model override
        model: "anthropic/claude-opus-4-5",
        // Or object form:
        // model: {
        //   primary: "anthropic/claude-opus-4-5",
        //   fallbacks: []
        // },

        // Group chat settings
        groupChat: {
          mentionPatterns: ["@samantha", "samantha"]
        },

        // Per-agent sandbox override
        sandbox: { mode: "off" },

        // Per-agent tool restrictions
        tools: {
          profile: "coding",
          allow: ["memory_search"],
          deny: []
        },

        // Per-agent heartbeat
        heartbeat: {
          every: "1h",
          target: "whatsapp"
        }
      },
      {
        id: "work",
        workspace: "~/clawd-work",
        identity: { name: "WorkBot", emoji: "💼" },
        model: "anthropic/claude-sonnet-4-5",
        groupChat: { mentionPatterns: ["@workbot"] },
        sandbox: { mode: "all", workspaceAccess: "ro" },
        tools: {
          allow: ["read", "sessions_list", "sessions_history"],
          deny: ["write", "edit", "exec", "browser"]
        }
      }
    ]
  },

  // Agent routing bindings
  bindings: [
    { agentId: "main", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
    { agentId: "work", match: { channel: "slack" } },
    { agentId: "main", match: { channel: "telegram", peer: { kind: "dm", id: "123456789" } } },
    { agentId: "work", match: { channel: "discord", guildId: "123456789012345678" } }
  ]
}
```

### Workspace Bootstrap Files

Auto-created in agent workspace:

| File | Purpose | Max Chars |
|------|---------|-----------|
| `AGENTS.md` | Agent instructions and capabilities | 20000 |
| `SOUL.md` | Agent personality definition | 20000 |
| `TOOLS.md` | Available tools documentation | 20000 |
| `IDENTITY.md` | Identity and role definition | 20000 |
| `USER.md` | User preferences and context | 20000 |
| `BOOTSTRAP.md` | Bootstrap instructions | 20000 |
| `MEMORY.md` | Semantic memory index | 20000 |
| `memory/*.md` | Additional memory files | 20000 |
| `HEARTBEAT.md` | Heartbeat instructions | 20000 |

---

## Session & Memory Management

### Session Configuration

```json5
{
  session: {
    scope: "per-sender",
    dmScope: "main",                  // "main" | "per-peer" | "per-channel-peer"
    mainKey: "main",

    // Identity linking across channels
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"]
    },

    // Reset policy
    reset: {
      mode: "daily",                  // "daily" | "idle"
      atHour: 4,                      // Local hour (0-23) for daily reset
      idleMinutes: 60                 // Sliding idle window
    },

    // Per-session-type overrides
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      dm: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 }
    },

    // Heartbeat idle override
    heartbeatIdleMinutes: 120,

    // Reset triggers
    resetTriggers: ["/new", "/reset"],

    // Session store location
    store: "~/.clawdbot/agents/{agentId}/sessions/sessions.json",

    // Agent-to-agent settings
    agentToAgent: {
      maxPingPongTurns: 5             // Max reply-back turns (0-5)
    },

    // Send policy
    sendPolicy: {
      rules: [
        { action: "deny", match: { channel: "discord", chatType: "group" } },
        { action: "deny", match: { keyPrefix: "cron:" } }
      ],
      default: "allow"
    },

    // Typing mode
    typingMode: "instant",
    typingIntervalSeconds: 6
  }
}
```

### Session Keys

| Session Type | Key Format |
|--------------|------------|
| Main/DM | `agent:<agentId>:main` |
| WhatsApp DM | `agent:<agentId>:whatsapp:dm:<phone>` |
| WhatsApp Group | `agent:<agentId>:whatsapp:group:<jid>` |
| Telegram DM | `agent:<agentId>:telegram:dm:<chatId>` |
| Discord DM | `agent:<agentId>:discord:dm:<userId>` |
| Discord Guild | `agent:<agentId>:discord:channel:<channelId>` |
| Slack DM | `agent:<agentId>:slack:dm:<userId>` |
| Slack Channel | `agent:<agentId>:slack:channel:<channelId>` |

---

## Tools & Sandbox Configuration

### Tool Configuration

```json5
{
  tools: {
    // Base profile
    profile: "coding",                // "minimal" | "coding" | "messaging" | "full"

    // Allow/deny lists
    allow: ["group:fs", "group:runtime", "memory_search"],
    deny: ["browser", "canvas"],

    // Per-provider restrictions
    byProvider: {
      "google-antigravity": { profile: "minimal" },
      "openai/gpt-5.2": { allow: ["group:fs", "sessions_list"] }
    },

    // Elevated (host) exec access
    elevated: {
      enabled: true,
      allowFrom: {
        whatsapp: ["+15555550123"],
        telegram: ["tg:123456789", "@username"],
        discord: ["steipete", "1234567890123"],
        signal: ["+15555550123"],
        imessage: ["+15555550123"],
        webchat: ["session123"]
      }
    },

    // Agent-to-agent messaging
    agentToAgent: {
      enabled: false,
      allow: ["home", "work"]
    },

    // Exec settings
    exec: {
      backgroundMs: 10000,
      timeoutSec: 1800,
      cleanupMs: 1800000,
      notifyOnExit: true,
      applyPatch: {
        enabled: false,
        allowModels: ["gpt-5.2"]
      }
    },

    // Web tools
    web: {
      search: {
        enabled: true,
        apiKey: "BRAVE_API_KEY",      // Or use env var
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15
      },
      fetch: {
        enabled: true,
        maxChars: 50000,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
        userAgent: "ClawdbotBot/1.0",
        readability: true,
        firecrawl: {
          enabled: true,
          apiKey: "FIRECRAWL_API_KEY",
          baseUrl: "https://api.firecrawl.dev",
          onlyMainContent: true,
          maxAgeMs: 86400000,
          timeoutSeconds: 30
        }
      }
    },

    // Media understanding
    media: {
      concurrency: 2,
      models: [],                     // Shared models (capability-tagged)

      image: {
        enabled: true,
        prompt: "Describe this image.",
        maxChars: 500,
        maxBytes: 10485760,           // 10MB
        timeoutSeconds: 60,
        attachments: {
          mode: "first",              // "first" | "all"
          maxAttachments: 1
        },
        scope: {
          default: "allow",
          rules: []
        },
        models: [
          { provider: "openai", model: "gpt-4o-mini" },
          { provider: "anthropic" }
        ]
      },

      audio: {
        enabled: true,
        maxBytes: 20971520,           // 20MB
        timeoutSeconds: 60,
        language: "en",
        scope: {
          default: "deny",
          rules: [{ action: "allow", match: { chatType: "direct" } }]
        },
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          { provider: "groq", model: "whisper-large-v3-turbo" },
          {
            type: "cli",
            command: "whisper",
            args: ["--model", "base", "{{MediaPath}}"]
          }
        ]
      },

      video: {
        enabled: true,
        maxChars: 500,
        maxBytes: 52428800,           // 50MB
        timeoutSeconds: 120,
        models: [
          { provider: "google", model: "gemini-3-flash-preview" }
        ]
      }
    },

    // Sandbox tool policy
    sandbox: {
      tools: {
        allow: [
          "exec", "process", "read", "write", "edit", "apply_patch",
          "sessions_list", "sessions_history", "sessions_send",
          "sessions_spawn", "session_status"
        ],
        deny: ["browser", "canvas", "nodes", "cron", "discord", "gateway"]
      }
    },

    // Sub-agent tool policy
    subagents: {
      tools: {
        allow: ["*"],
        deny: ["gateway"]
      }
    }
  }
}
```

### Tool Groups

| Group | Tools |
|-------|-------|
| `group:runtime` | exec, bash, process |
| `group:fs` | read, write, edit, apply_patch |
| `group:sessions` | sessions_list, sessions_history, sessions_send, sessions_spawn, session_status |
| `group:memory` | memory_search, memory_get |
| `group:web` | web_search, web_fetch |
| `group:ui` | browser, canvas |
| `group:automation` | cron, gateway |
| `group:messaging` | message |
| `group:nodes` | nodes |
| `group:clawdbot` | All built-in Clawdbot tools |

### Tool Profiles

| Profile | Included Tools |
|---------|----------------|
| `minimal` | session_status only |
| `coding` | group:fs, group:runtime, group:sessions, group:memory, image |
| `messaging` | group:messaging, sessions_list, sessions_history, sessions_send, session_status |
| `full` | No restrictions |

---

## Model Provider Configuration

### Built-in Providers

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-5",
        fallbacks: ["openrouter/meta-llama/llama-3.3-70b-instruct:free"]
      },

      models: {
        // Anthropic
        "anthropic/claude-opus-4-5": { alias: "opus" },
        "anthropic/claude-sonnet-4-5": { alias: "sonnet" },

        // OpenAI
        "openai/gpt-5.2": { alias: "gpt" },
        "openai/gpt-5-mini": { alias: "gpt-mini" },

        // Google
        "google/gemini-3-pro-preview": { alias: "gemini" },
        "google/gemini-3-flash-preview": { alias: "gemini-flash" },

        // OpenRouter
        "openrouter/deepseek/deepseek-r1:free": {},
        "openrouter/meta-llama/llama-3.3-70b-instruct:free": {},

        // Z.AI
        "zai/glm-4.7": {
          alias: "GLM",
          params: { thinking: { type: "enabled" } }
        },

        // MiniMax
        "minimax/MiniMax-M2.1": { alias: "minimax" },

        // OpenCode Zen
        "opencode/claude-opus-4-5": {}
      }
    }
  }
}
```

### Custom Provider Configuration

```json5
{
  models: {
    mode: "merge",                    // "merge" | "replace"
    providers: {
      // LiteLLM / OpenAI-compatible
      "custom-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "${LITELLM_KEY}",
        api: "openai-completions",    // "openai-completions" | "openai-responses" | "anthropic-messages" | "google-generative-ai"
        models: [
          {
            id: "llama-3.1-8b",
            name: "Llama 3.1 8B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 32000
          }
        ]
      },

      // Anthropic-compatible (MiniMax)
      "minimax": {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.1",
            name: "MiniMax M2.1",
            reasoning: false,
            input: ["text"],
            cost: { input: 15, output: 60, cacheRead: 2, cacheWrite: 10 },
            contextWindow: 200000,
            maxTokens: 8192
          }
        ]
      },

      // Moonshot (Kimi)
      "moonshot": {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "kimi-k2-0905-preview",
            name: "Kimi K2",
            contextWindow: 256000,
            maxTokens: 8192
          }
        ]
      },

      // Cerebras
      "cerebras": {
        baseUrl: "https://api.cerebras.ai/v1",
        apiKey: "${CEREBRAS_API_KEY}",
        api: "openai-completions",
        models: [
          { id: "zai-glm-4.7", name: "GLM 4.7 (Cerebras)" },
          { id: "zai-glm-4.6", name: "GLM 4.6 (Cerebras)" }
        ]
      }
    }
  }
}
```

### Auth Profiles

```json5
{
  auth: {
    profiles: {
      "anthropic:me@example.com": {
        provider: "anthropic",
        mode: "oauth",
        email: "me@example.com"
      },
      "anthropic:work": {
        provider: "anthropic",
        mode: "api_key"
      }
    },
    order: {
      anthropic: ["anthropic:me@example.com", "anthropic:work"]
    }
  }
}
```

### Environment Variables for Providers

| Variable | Provider |
|----------|----------|
| `ANTHROPIC_API_KEY` | Anthropic |
| `OPENAI_API_KEY` | OpenAI |
| `GOOGLE_API_KEY` / `GEMINI_API_KEY` | Google |
| `OPENROUTER_API_KEY` | OpenRouter |
| `ZAI_API_KEY` / `Z_AI_API_KEY` | Z.AI |
| `MINIMAX_API_KEY` | MiniMax |
| `OPENCODE_API_KEY` | OpenCode Zen |
| `GROQ_API_KEY` | Groq |
| `BRAVE_API_KEY` | Brave Search |
| `FIRECRAWL_API_KEY` | Firecrawl |
| `ELEVENLABS_API_KEY` / `XI_API_KEY` | ElevenLabs |

---

## Webhooks & Automation

### Hooks Configuration

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
    maxBodyBytes: 262144,             // 256 KB

    presets: ["gmail"],
    transformsDir: "~/.clawdbot/hooks",

    mappings: [
      {
        match: { path: "gmail" },     // Or { source: "gmail" }
        action: "agent",
        wakeMode: "now",              // "now" | "next-heartbeat"
        name: "Gmail",
        sessionKey: "hook:gmail:{{messages[0].id}}",
        messageTemplate: "From: {{messages[0].from}}\nSubject: {{messages[0].subject}}\n{{messages[0].snippet}}",
        deliver: true,
        channel: "last",              // "last" | "whatsapp" | "telegram" | etc.
        to: "+15555550123",           // Optional recipient
        model: "openai/gpt-5.2-mini",
        thinking: "off",
        timeoutSeconds: 60
      },
      {
        match: { path: "custom" },
        action: "agent",
        transform: "custom-transform.js"
      }
    ],

    // Gmail helper config
    gmail: {
      account: "clawdbot@gmail.com",
      topic: "projects/<project-id>/topics/gog-gmail-watch",
      subscription: "gog-gmail-watch-push",
      pushToken: "shared-push-token",
      hookUrl: "http://127.0.0.1:18789/hooks/gmail",
      includeBody: true,
      maxBytes: 20000,
      renewEveryMinutes: 720,
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      thinking: "off",
      serve: { bind: "127.0.0.1", port: 8788, path: "/" },
      tailscale: { mode: "funnel", path: "/gmail-pubsub" }
    }
  }
}
```

**Webhook Endpoints:**
- `POST /hooks/wake` - Wake agent: `{ text, mode?: "now"|"next-heartbeat" }`
- `POST /hooks/agent` - Send to agent: `{ message, name?, sessionKey?, wakeMode?, deliver?, channel?, to?, model?, thinking?, timeoutSeconds? }`
- `POST /hooks/<name>` - Custom mapped hooks

**Authentication:**
- `Authorization: Bearer <token>`
- `x-clawdbot-token: <token>`
- `?token=<token>`

### Cron Configuration

```json5
{
  cron: {
    enabled: true,
    maxConcurrentRuns: 2
  }
}
```

---

## Message Handling Configuration

### Message Settings

```json5
{
  messages: {
    // Response prefix
    responsePrefix: "🦞",             // Or "auto" for identity.name
    // Template variables: {model}, {modelFull}, {provider}, {thinkingLevel}, {identity.name}

    // Ack reactions
    ackReaction: "👀",
    ackReactionScope: "group-mentions", // "group-mentions" | "group-all" | "direct" | "all"
    removeAckAfterReply: false,

    // Message queue
    queue: {
      mode: "collect",                // "steer" | "followup" | "collect" | "steer-backlog" | "interrupt"
      debounceMs: 1000,
      cap: 20,
      drop: "summarize",              // "old" | "new" | "summarize"
      byChannel: {
        whatsapp: "collect",
        telegram: "collect",
        discord: "collect"
      }
    },

    // Inbound debouncing
    inbound: {
      debounceMs: 2000,
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
        discord: 1500
      }
    },

    // Group chat history
    groupChat: {
      historyLimit: 50
    },

    // Text-to-speech
    tts: {
      auto: "always",                 // "off" | "always" | "inbound" | "tagged"
      mode: "final",                  // "final" | "all"
      provider: "elevenlabs",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: { enabled: true },
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.clawdbot/settings/tts.json",

      elevenlabs: {
        apiKey: "elevenlabs_api_key",
        baseUrl: "https://api.elevenlabs.io",
        voiceId: "voice_id",
        modelId: "eleven_multilingual_v2",
        seed: 42,
        applyTextNormalization: "auto",
        languageCode: "en",
        voiceSettings: {
          stability: 0.5,
          similarityBoost: 0.75,
          style: 0.0,
          useSpeakerBoost: true,
          speed: 1.0
        }
      },

      openai: {
        apiKey: "openai_api_key",
        model: "gpt-4o-mini-tts",
        voice: "alloy"
      }
    }
  },

  // Talk mode defaults (macOS/iOS/Android)
  talk: {
    voiceId: "elevenlabs_voice_id",
    voiceAliases: {
      Clawd: "EXAVITQu4vr4xnSDxMaL",
      Roger: "CwhRBWXzGAHq8TQ4Fs17"
    },
    modelId: "eleven_v3",
    outputFormat: "mp3_44100_128",
    apiKey: "elevenlabs_api_key",
    interruptOnSpeech: true
  }
}
```

---

## CLI Commands Reference

### Gateway Commands

```bash
# Start gateway
clawdbot gateway
clawdbot gateway --port 18789 --verbose
clawdbot gateway --force

# Gateway management
clawdbot gateway status
clawdbot gateway status --deep
clawdbot gateway restart
clawdbot gateway stop

# Logs
clawdbot logs
clawdbot logs --follow
```

### Channel Commands

```bash
# Status
clawdbot channels status
clawdbot channels status --probe

# WhatsApp
clawdbot channels login
clawdbot channels login --account personal
clawdbot channels logout
clawdbot channels logout --account personal

# Pairing
clawdbot pairing list whatsapp
clawdbot pairing approve whatsapp <code>
clawdbot pairing list telegram
clawdbot pairing approve telegram <code>
```

### Configuration Commands

```bash
# Configure
clawdbot configure
clawdbot configure --section web

# Onboarding
clawdbot onboard
clawdbot onboard:web
clawdbot onboard --auth-choice anthropic

# Doctor
clawdbot doctor
clawdbot doctor --fix
clawdbot doctor --yes
```

### Message Commands

```bash
# Send messages
clawdbot send "Hello"
clawdbot message send --media <path-or-url> --message <caption>
clawdbot message send --media <mp4> --gif-playback
```

### Model Commands

```bash
clawdbot models auth setup-token --provider anthropic
```

### RPC Commands

```bash
# Gateway RPC calls
clawdbot gateway call config.get --params '{}'
clawdbot gateway call config.apply --params '{...}'
clawdbot gateway call config.patch --params '{...}'
```

### Profiles

```bash
# Development profile
clawdbot --dev gateway       # Uses ~/.clawdbot-dev, port 19001+

# Custom profile
clawdbot --profile work gateway  # Uses ~/.clawdbot-work
```

---

## A2I2 Implementation Checklist

### Phase 1: Foundation

- [ ] Install Clawdbot: `curl -fsSL https://clawd.bot/install.sh | bash`
- [ ] Run onboarding: `clawdbot onboard`
- [ ] Configure Anthropic API key
- [ ] Set workspace to A2I2 directory
- [ ] Create `AGENTS.md` with A2I2 memory operations
- [ ] Create `SOUL.md` with A2I2 personality
- [ ] Create `MEMORY.md` for semantic memory index
- [ ] Test basic functionality: `clawdbot send "Test"`

### Phase 2: Channel Setup

- [ ] Configure WhatsApp channel
  - [ ] Set `dmPolicy: "allowlist"`
  - [ ] Add allowed phone numbers
  - [ ] Test QR code login
- [ ] Configure Telegram channel (optional)
  - [ ] Create bot via BotFather
  - [ ] Set bot token
  - [ ] Configure groups
- [ ] Configure Discord channel (optional)
  - [ ] Create Discord application
  - [ ] Enable required intents
  - [ ] Configure guilds and channels

### Phase 3: Memory Integration

- [ ] Configure session persistence
  - [ ] Set `dmScope: "per-peer"` for cross-channel identity
  - [ ] Configure `identityLinks` for user mapping
  - [ ] Set appropriate reset policy
- [ ] Configure memory flush
  - [ ] Enable `compaction.memoryFlush`
  - [ ] Set prompt for A2I2 LEARN operation
  - [ ] Configure `softThresholdTokens`
- [ ] Configure heartbeat for REFLECT operation
  - [ ] Set `heartbeat.every`
  - [ ] Configure `HEARTBEAT.md` with reflection prompt

### Phase 4: Agent Configuration

- [ ] Configure multi-agent if needed
  - [ ] Define agent list with identities
  - [ ] Set up bindings for routing
  - [ ] Configure per-agent tools
- [ ] Configure tools
  - [ ] Enable `memory_search` tool
  - [ ] Set appropriate tool profile
  - [ ] Configure sandbox for untrusted sessions
- [ ] Configure model settings
  - [ ] Set primary model (Claude Opus recommended)
  - [ ] Configure fallbacks
  - [ ] Set thinking level

### Phase 5: Testing & Validation

- [ ] Test memory capture (LEARN)
- [ ] Test memory recall (RECALL)
- [ ] Test entity relationships (RELATE)
- [ ] Test periodic reflection (REFLECT)
- [ ] Test cross-channel memory persistence
- [ ] Test session reset behavior
- [ ] Run `clawdbot doctor` for validation

---

## Quick Reference

### Minimal A2I2 Configuration

```json5
{
  agents: {
    defaults: {
      workspace: "~/a2i2",
      model: { primary: "anthropic/claude-opus-4-5" },
      compaction: {
        mode: "safeguard",
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          prompt: "Store important learnings to memory/YYYY-MM-DD.md. Include: user preferences, decisions, new information. Reply NO_REPLY if nothing to store."
        }
      },
      heartbeat: {
        every: "30m",
        prompt: "Read HEARTBEAT.md. Run REFLECT operation if significant learnings accumulated. Reply HEARTBEAT_OK if nothing needs attention."
      }
    }
  },

  session: {
    dmScope: "per-peer",
    reset: { mode: "idle", idleMinutes: 1440 }
  },

  channels: {
    whatsapp: {
      dmPolicy: "allowlist",
      allowFrom: ["+15555550123"]
    }
  },

  tools: {
    profile: "coding",
    allow: ["memory_search", "memory_get"]
  }
}
```

---

*This technical reference was compiled from the official Clawdbot documentation at https://docs.clawd.bot/ for A2I2 implementation planning.*
