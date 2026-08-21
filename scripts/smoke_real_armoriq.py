"""
MANDATE — Live Real ArmorIQ SDK Smoke Test Script
Executes live end-to-end cloud enforcement against ArmorIQ IAP / PEP proxy
when ARMORIQ_API_KEY is supplied. Redacts sensitive keys and credentials.
"""

import os
import sys
from urllib.parse import urlparse

try:
    import armoriq_sdk
except ImportError:
    print("[ERROR] armoriq-sdk package is not installed.")
    sys.exit(1)

from backend.armoriq.real import RealArmorIQ


def run_smoke_test():
    api_key = os.environ.get("ARMORIQ_API_KEY")
    if not api_key:
        print("[SKIP] ARMORIQ_API_KEY is not set. To run live cloud smoke test, set ARMORIQ_API_KEY.")
        sys.exit(0)

    endpoint = os.environ.get("ARMORIQ_ENDPOINT", "https://api.armoriq.ai/v1")
    parsed_url = urlparse(endpoint)
    endpoint_host = parsed_url.netloc or parsed_url.path

    print("=" * 70)
    print("MANDATE — GENUINE ARMORIQ SDK LIVE SMOKE TEST")
    print("=" * 70)
    print(f"SDK Version       : {getattr(armoriq_sdk, '__version__', 'unknown')}")
    print(f"Mode              : ARMORIQ_MODE=real")
    print(f"Endpoint Host     : {endpoint_host}")
    print(f"API Key Redacted  : {api_key[:6]}...{api_key[-4:] if len(api_key) > 10 else ''}")
    print("-" * 70)

    try:
        real_adapter = RealArmorIQ(api_key=api_key, endpoint=endpoint)

        # Step 1: Capture Plan
        print("[1/4] Capturing plan via ArmorIQClient...")
        plan_res = real_adapter.capture_plan(
            objective="Smoke Test P2P Authority Sealing",
            context={
                "mission_id": "smoke_mission_001",
                "approved_payees": ["1122334455", "9988776655"],
                "spend_ceilings": {"per_invoice_paise": 50000000},
                "open_pos": ["PO-SMOKE-01"],
            },
        )
        print(f"      Plan Hash Prefix : {plan_res.plan_hash[:16]}...")
        print(f"      Sealed At        : {plan_res.sealed_at}")

        # Step 2: Mint Intent Token
        print("[2/4] Minting IntentToken via ArmorIQ IAP...")
        token_res = real_adapter.get_intent_token(
            plan_hash=plan_res.plan_hash,
            envelope=plan_res.envelope,
        )
        print(f"      Token ID Prefix  : {token_res.intent_token[:12]}... (Redacted)")
        print(f"      Merkle Root      : {token_res.merkle_root[:16]}...")

        # Step 3: Planned Action Invocation (Harmless read-only or authorized action)
        print("[3/4] Testing planned action authorization ('fetch_invoices')...")
        decision_allowed = real_adapter.invoke(
            agent_id="matcher",
            tool="fetch_invoices",
            params={},
            intent_token=token_res.intent_token,
        )
        print(f"      Verdict          : {decision_allowed.verdict}")
        print(f"      Proof Fields     : {list(decision_allowed.proof.keys())}")

        # Step 4: Unplanned Action Invocation (Should be blocked by ArmorIQ)
        print("[4/4] Testing unplanned / unauthorized action ('unplanned_malicious_tool')...")
        decision_blocked = real_adapter.invoke(
            agent_id="disburser",
            tool="unplanned_malicious_tool",
            params={"untrusted": "injection"},
            intent_token=token_res.intent_token,
        )
        print(f"      Verdict          : {decision_blocked.verdict}")
        print(f"      Reason           : {decision_blocked.reason}")
        print(f"      Rule Matched     : {decision_blocked.rule_matched}")

        print("=" * 70)
        print("RESULT: LIVE REAL ARMORIQ SDK SMOKE TEST COMPLETED SUCCESSFULLY!")
        print("=" * 70)

    except Exception as e:
        print(f"[FAILED] Live smoke test encountered error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_smoke_test()
