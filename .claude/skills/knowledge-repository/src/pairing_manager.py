"""
Arcus Pairing Manager - Device Pairing System

Manages pairing codes for secure device authorization. Users must enter a
6-digit code to pair their device with A2I2, similar to Bluetooth pairing.

Usage:
    from pairing_manager import PairingManager

    manager = PairingManager()

    # Generate a code for a user
    code = manager.generate_code(user_id="user123", channel="whatsapp")
    print(f"Your pairing code: {code}")

    # User enters code to pair
    result = manager.pair_device(
        code="123456",
        device_id="+15551234567",
        channel="whatsapp"
    )
"""

import logging
import random
import string
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

logger = logging.getLogger("arcus.pairing")


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class PairingCode:
    """A temporary pairing code."""
    code: str
    user_id: str
    channel: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=15))
    used: bool = False

    @property
    def is_expired(self) -> bool:
        """Check if the code has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if the code is still valid."""
        return not self.used and not self.is_expired


@dataclass
class PairedDevice:
    """A paired device record."""
    device_id: str
    user_id: str
    channel: str
    paired_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    nickname: Optional[str] = None
    metadata: Dict[str, any] = field(default_factory=dict)


@dataclass
class PairingResult:
    """Result of a pairing attempt."""
    success: bool
    device_id: Optional[str] = None
    user_id: Optional[str] = None
    error: Optional[str] = None
    paired_device: Optional[PairedDevice] = None


# =============================================================================
# PAIRING MANAGER
# =============================================================================

class PairingManager:
    """
    Manages device pairing with temporary codes.

    Features:
    - Generate 6-digit pairing codes
    - Time-limited codes (default 15 minutes)
    - One-time use codes
    - Device tracking per user
    - Multi-channel support
    """

    def __init__(
        self,
        code_length: int = 6,
        code_expiry_minutes: int = 15,
        max_devices_per_user: int = 5,
    ):
        """
        Initialize the pairing manager.

        Args:
            code_length: Length of pairing codes (default: 6)
            code_expiry_minutes: Minutes until codes expire (default: 15)
            max_devices_per_user: Max devices a user can pair (default: 5)
        """
        self.code_length = code_length
        self.code_expiry_minutes = code_expiry_minutes
        self.max_devices_per_user = max_devices_per_user

        # In-memory storage (production should use database)
        self._codes: Dict[str, PairingCode] = {}  # code -> PairingCode
        self._paired_devices: Dict[str, PairedDevice] = {}  # device_id -> PairedDevice
        self._user_devices: Dict[str, List[str]] = {}  # user_id -> [device_ids]

    def generate_code(
        self,
        user_id: str,
        channel: str,
        custom_code: Optional[str] = None
    ) -> str:
        """
        Generate a new pairing code for a user.

        Args:
            user_id: User ID requesting the code
            channel: Channel type (whatsapp, discord, etc.)
            custom_code: Optional custom code (for testing)

        Returns:
            6-digit pairing code
        """
        # Clean up expired codes first
        self._cleanup_expired_codes()

        # Generate code
        if custom_code:
            code = custom_code
        else:
            code = ''.join(random.choices(string.digits, k=self.code_length))

        # Ensure uniqueness
        attempts = 0
        while code in self._codes and attempts < 10:
            code = ''.join(random.choices(string.digits, k=self.code_length))
            attempts += 1

        if code in self._codes:
            raise ValueError("Unable to generate unique pairing code")

        # Store code
        pairing_code = PairingCode(
            code=code,
            user_id=user_id,
            channel=channel,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=self.code_expiry_minutes)
        )
        self._codes[code] = pairing_code

        logger.info(f"Generated pairing code {code} for user {user_id} on {channel}")
        return code

    def pair_device(
        self,
        code: str,
        device_id: str,
        channel: str,
        nickname: Optional[str] = None,
        metadata: Optional[Dict[str, any]] = None
    ) -> PairingResult:
        """
        Pair a device using a pairing code.

        Args:
            code: The pairing code
            device_id: Device identifier (phone number, discord ID, etc.)
            channel: Channel type
            nickname: Optional device nickname
            metadata: Optional metadata

        Returns:
            PairingResult with success status
        """
        # Check if code exists
        if code not in self._codes:
            return PairingResult(
                success=False,
                error="Invalid pairing code"
            )

        pairing_code = self._codes[code]

        # Validate code
        if not pairing_code.is_valid:
            if pairing_code.used:
                error = "Pairing code already used"
            else:
                error = "Pairing code expired"
            return PairingResult(success=False, error=error)

        # Verify channel matches
        if pairing_code.channel != channel:
            return PairingResult(
                success=False,
                error=f"Code is for {pairing_code.channel}, not {channel}"
            )

        # Check device limit
        user_id = pairing_code.user_id
        user_device_count = len(self._user_devices.get(user_id, []))
        if user_device_count >= self.max_devices_per_user:
            return PairingResult(
                success=False,
                error=f"Maximum {self.max_devices_per_user} devices already paired"
            )

        # Check if device already paired
        if device_id in self._paired_devices:
            existing = self._paired_devices[device_id]
            if existing.user_id == user_id:
                return PairingResult(
                    success=True,
                    device_id=device_id,
                    user_id=user_id,
                    paired_device=existing,
                    error="Device already paired"
                )
            else:
                return PairingResult(
                    success=False,
                    error="Device already paired to different user"
                )

        # Create paired device
        paired_device = PairedDevice(
            device_id=device_id,
            user_id=user_id,
            channel=channel,
            nickname=nickname,
            metadata=metadata or {}
        )

        # Store pairing
        self._paired_devices[device_id] = paired_device
        if user_id not in self._user_devices:
            self._user_devices[user_id] = []
        self._user_devices[user_id].append(device_id)

        # Mark code as used
        pairing_code.used = True

        logger.info(f"Device {device_id} paired to user {user_id} on {channel}")

        return PairingResult(
            success=True,
            device_id=device_id,
            user_id=user_id,
            paired_device=paired_device
        )

    def is_paired(self, device_id: str, channel: Optional[str] = None) -> bool:
        """
        Check if a device is paired.

        Args:
            device_id: Device identifier
            channel: Optional channel filter

        Returns:
            True if device is paired
        """
        if device_id not in self._paired_devices:
            return False

        if channel:
            return self._paired_devices[device_id].channel == channel

        return True

    def get_paired_device(self, device_id: str) -> Optional[PairedDevice]:
        """Get paired device info."""
        return self._paired_devices.get(device_id)

    def get_user_devices(self, user_id: str) -> List[PairedDevice]:
        """Get all devices paired to a user."""
        device_ids = self._user_devices.get(user_id, [])
        return [self._paired_devices[did] for did in device_ids if did in self._paired_devices]

    def unpair_device(self, device_id: str) -> bool:
        """
        Unpair a device.

        Args:
            device_id: Device identifier

        Returns:
            True if device was unpaired
        """
        if device_id not in self._paired_devices:
            return False

        device = self._paired_devices.pop(device_id)
        user_id = device.user_id

        # Remove from user's device list
        if user_id in self._user_devices:
            self._user_devices[user_id] = [
                did for did in self._user_devices[user_id] if did != device_id
            ]

        logger.info(f"Device {device_id} unpaired from user {user_id}")
        return True

    def revoke_code(self, code: str) -> bool:
        """Revoke a pairing code before it's used."""
        if code in self._codes:
            self._codes[code].used = True
            logger.info(f"Pairing code {code} revoked")
            return True
        return False

    def _cleanup_expired_codes(self) -> None:
        """Remove expired codes from storage."""
        expired = [code for code, pc in self._codes.items() if pc.is_expired]
        for code in expired:
            del self._codes[code]
        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired pairing codes")

    def get_stats(self) -> Dict[str, any]:
        """Get pairing statistics."""
        self._cleanup_expired_codes()
        return {
            "active_codes": len([pc for pc in self._codes.values() if pc.is_valid]),
            "total_codes": len(self._codes),
            "paired_devices": len(self._paired_devices),
            "total_users": len(self._user_devices),
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_pairing_manager() -> PairingManager:
    """Get a global pairing manager instance."""
    global _pairing_manager
    if '_pairing_manager' not in globals():
        _pairing_manager = PairingManager()
    return _pairing_manager
