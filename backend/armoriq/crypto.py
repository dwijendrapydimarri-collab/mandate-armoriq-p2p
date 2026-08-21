"""
MANDATE — Cryptographic Utilities for Local Adapter
Generates Ed25519 keypairs and signs canonical JSON grants.
"""

import json
from typing import Tuple, Dict, Any
from cryptography.hazmat.primitives.asymmetric import ed25519


def generate_agent_keypair() -> Tuple[str, str]:
    """Generates an Ed25519 private/public keypair in hex format."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    priv_hex = private_key.private_bytes_raw().hex()
    pub_hex = public_key.public_bytes_raw().hex()
    return priv_hex, pub_hex


def sign_payload(private_key_hex: str, payload: Dict[str, Any]) -> str:
    """Signs a canonical JSON payload using an Ed25519 private key."""
    canonical_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(private_key_hex))
    signature = private_key.sign(canonical_bytes)
    return signature.hex()


def verify_signature(public_key_hex: str, payload: Dict[str, Any], signature_hex: str) -> bool:
    """Verifies an Ed25519 signature over canonical JSON."""
    canonical_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
    try:
        public_key.verify(bytes.fromhex(signature_hex), canonical_bytes)
        return True
    except Exception:
        return False
