#!/usr/bin/env python3
"""
Arcus Gateway Server - Entry Point

Starts the Arcus Multi-Channel Gateway with all configured adapters.
Reads configuration from environment variables and connects to WhatsApp,
Discord, and/or Siri based on available credentials.

Usage:
    # Start with all configured adapters
    python gateway_server.py

    # Or with specific adapters
    ARCUS_ADAPTERS=discord,siri python gateway_server.py

Environment Variables:
    See .env.example for full list. Key variables:

    # Gateway
    ARCUS_GATEWAY_HOST=127.0.0.1
    ARCUS_GATEWAY_WS_PORT=18790
    ARCUS_GATEWAY_HTTP_PORT=8080

    # WhatsApp (requires Baileys bridge running)
    WHATSAPP_BRIDGE_URL=ws://127.0.0.1:18791
    WHATSAPP_ALLOWLIST=+15551234567,+15559876543

    # Discord
    DISCORD_BOT_TOKEN=your-bot-token
    DISCORD_GUILD_IDS=123456789,987654321
    DISCORD_REQUIRE_MENTION=false

    # Siri
    SIRI_API_SECRET=your-api-secret
    SIRI_ALLOWED_DEVICES=iPhone,iPad

    # AI & Memory
    ANTHROPIC_API_KEY=sk-ant-...
    GEMINI_API_KEY=AIzaSy...
    SUPABASE_URL=https://...
    SUPABASE_SERVICE_ROLE_KEY=...
"""

import asyncio
import logging
import os
import signal
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gateway import ArcusGateway, GatewayConfig
from chat_commands import ChatCommandHandler
from channel_adapter import AccessPolicy


# =============================================================================
# LOGGING
# =============================================================================

def setup_logging() -> None:
    """Configure structured logging."""
    level = logging.DEBUG if os.getenv("ARCUS_DEBUG", "").lower() == "true" else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Quiet noisy libraries
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)


# =============================================================================
# ADAPTER FACTORIES
# =============================================================================

def create_whatsapp_adapter():
    """Create WhatsApp adapter if configured."""
    bridge_url = os.getenv("WHATSAPP_BRIDGE_URL")
    if not bridge_url:
        return None

    from adapter_whatsapp import WhatsAppAdapter

    allowlist_str = os.getenv("WHATSAPP_ALLOWLIST", "")
    allowlist = [s.strip() for s in allowlist_str.split(",") if s.strip()]

    policy = AccessPolicy.ALLOWLIST if allowlist else AccessPolicy.OPEN

    return WhatsAppAdapter(
        bridge_url=bridge_url,
        access_policy=policy,
        allowlist=allowlist,
        send_read_receipts=os.getenv("WHATSAPP_READ_RECEIPTS", "true").lower() == "true",
        send_typing_indicator=os.getenv("WHATSAPP_TYPING_INDICATOR", "true").lower() == "true",
    )


def create_discord_adapter():
    """Create Discord adapter if configured."""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not bot_token:
        return None

    from adapter_discord import DiscordAdapter

    guild_ids_str = os.getenv("DISCORD_GUILD_IDS", "")
    guild_ids = [s.strip() for s in guild_ids_str.split(",") if s.strip()]

    policy = AccessPolicy.ALLOWLIST if guild_ids else AccessPolicy.OPEN

    return DiscordAdapter(
        bot_token=bot_token,
        access_policy=policy,
        allowlist_guild_ids=guild_ids,
        require_mention=os.getenv("DISCORD_REQUIRE_MENTION", "false").lower() == "true",
        respond_to_dms=os.getenv("DISCORD_RESPOND_DMS", "true").lower() == "true",
    )


def create_siri_adapter():
    """Create Siri webhook adapter if configured."""
    api_secret = os.getenv("SIRI_API_SECRET", os.getenv("API_SECRET_KEY", ""))
    if not api_secret:
        # Siri adapter can run without auth in development
        if os.getenv("NODE_ENV") == "production":
            return None

    from adapter_siri import SiriWebhookAdapter

    devices_str = os.getenv("SIRI_ALLOWED_DEVICES", "")
    devices = [s.strip() for s in devices_str.split(",") if s.strip()]

    policy = AccessPolicy.ALLOWLIST if devices else AccessPolicy.OPEN

    return SiriWebhookAdapter(
        api_secret=api_secret,
        host=os.getenv("ARCUS_GATEWAY_HOST", "0.0.0.0"),
        port=int(os.getenv("ARCUS_GATEWAY_HTTP_PORT", "8080")),
        path=os.getenv("SIRI_WEBHOOK_PATH", "/webhook/siri"),
        access_policy=policy,
        allowed_device_ids=devices,
        max_response_length=int(os.getenv("SIRI_MAX_RESPONSE_LENGTH", "500")),
    )


# =============================================================================
# MAIN
# =============================================================================

async def main() -> None:
    """Start the Arcus Gateway with all configured adapters."""
    setup_logging()
    logger = logging.getLogger("arcus.server")

    logger.info("=" * 60)
    logger.info("  Arcus Multi-Channel Gateway")
    logger.info("  Enterprise AI Chief of Staff")
    logger.info("=" * 60)

    # Load config
    config = GatewayConfig.from_env()

    # Create gateway
    gateway = ArcusGateway(config)

    # Set up chat commands
    commands = ChatCommandHandler(
        supabase_url=config.supabase_url,
        supabase_key=config.supabase_key,
    )
    gateway.set_command_handler(commands.handle)

    # Determine which adapters to load
    adapters_filter = os.getenv("ARCUS_ADAPTERS", "").lower()
    enabled = set(adapters_filter.split(",")) if adapters_filter else None

    # Register adapters
    adapter_factories = {
        "whatsapp": create_whatsapp_adapter,
        "discord": create_discord_adapter,
        "siri": create_siri_adapter,
    }

    registered = 0
    for name, factory in adapter_factories.items():
        if enabled and name not in enabled:
            logger.info(f"  Skipping {name} (not in ARCUS_ADAPTERS)")
            continue
        try:
            adapter = factory()
            if adapter:
                gateway.register_adapter(adapter)
                registered += 1
            else:
                logger.info(f"  {name}: not configured (missing env vars)")
        except ImportError as e:
            logger.warning(f"  {name}: dependency missing ({e})")
        except Exception as e:
            logger.error(f"  {name}: setup failed ({e})")

    if registered == 0:
        logger.warning(
            "No adapters configured. Set environment variables for at least one channel.\n"
            "  WhatsApp: WHATSAPP_BRIDGE_URL\n"
            "  Discord:  DISCORD_BOT_TOKEN\n"
            "  Siri:     SIRI_API_SECRET (or run in dev mode)\n\n"
            "Starting in Siri-only dev mode..."
        )
        # Start Siri in dev mode without auth
        from adapter_siri import SiriWebhookAdapter
        siri = SiriWebhookAdapter(
            api_secret="",
            host=os.getenv("ARCUS_GATEWAY_HOST", "0.0.0.0"),
            port=int(os.getenv("ARCUS_GATEWAY_HTTP_PORT", "8080")),
            access_policy=AccessPolicy.OPEN,
        )
        gateway.register_adapter(siri)

    # Start gateway
    await gateway.start()

    # Print status
    status = gateway.status()
    logger.info("\nGateway Status:")
    for adapter_name, info in status["adapters"].items():
        state = "connected" if info["connected"] else "connecting..."
        logger.info(f"  {adapter_name} ({info['channel']}): {state}")
    logger.info(f"\nMemory injection: {'enabled' if config.memory_injection_enabled else 'disabled'}")
    logger.info(f"Auto-learn: {'enabled' if config.auto_learn_enabled else 'disabled'}")
    logger.info(f"Default model: {config.default_model}")
    logger.info(f"\nHTTP endpoint: http://{config.host}:{config.http_port}")
    logger.info(f"WebSocket port: {config.ws_port}")
    logger.info("\nGateway is running. Press Ctrl+C to stop.\n")

    # Wait for shutdown signal
    stop_event = asyncio.Event()

    def _signal_handler():
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _signal_handler)

    await stop_event.wait()

    # Graceful shutdown
    logger.info("\nShutting down...")
    await gateway.stop()
    logger.info("Goodbye.")


if __name__ == "__main__":
    asyncio.run(main())
