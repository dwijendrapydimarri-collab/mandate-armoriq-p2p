"""
MANDATE — ArmorIQ Module Init (SPEC.md §1.8)
Selects between LocalEnforcer (local contract adapter) and RealArmorIQ (official SDK)
based on ARMORIQ_MODE environment variable. Fails closed if ARMORIQ_MODE=real
and credentials are missing.
"""

import os
import logging
from backend.armoriq.local import LocalEnforcer
from backend.armoriq.real import RealArmorIQ

logger = logging.getLogger(__name__)

ARMORIQ_MODE = os.environ.get("ARMORIQ_MODE", "local").lower()

if ARMORIQ_MODE == "real":
    api_key = os.environ.get("ARMORIQ_API_KEY")
    if not api_key:
        raise ValueError(
            "ARMORIQ_MODE=real requested, but ARMORIQ_API_KEY is missing. "
            "Set ARMORIQ_API_KEY to a valid key or run in ARMORIQ_MODE=local."
        )
    logger.info("Initializing genuine ArmorIQ SDK enforcer (ARMORIQ_MODE=real)")
    enforcer = RealArmorIQ(api_key=api_key)
else:
    logger.info("Initializing deterministic LocalEnforcer (ARMORIQ_MODE=local)")
    enforcer = LocalEnforcer()


def get_enforcer():
    return enforcer
