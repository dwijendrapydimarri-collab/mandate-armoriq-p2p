"""
MANDATE — ArmorIQ Module Init
Selects between LocalEnforcer and RealArmorIQ based on ARMORIQ_MODE env var.
"""

import os
from backend.armoriq.local import LocalEnforcer
from backend.armoriq.real import RealArmorIQ

ARMORIQ_MODE = os.environ.get("ARMORIQ_MODE", "local")

if ARMORIQ_MODE == "real":
    enforcer = RealArmorIQ()
else:
    enforcer = LocalEnforcer()


def get_enforcer():
    return enforcer
