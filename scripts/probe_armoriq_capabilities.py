"""
MANDATE — Direct Probe of ArmorIQ Cloud Delegation & Approval Routes
Tests whether the current ArmorIQ API key and workspace support:
1. POST /iap/trust/delegate (client.delegate)
2. POST /delegation/request (client.create_delegation_request)
3. GET /delegation/{id}/status (client.get_delegation_status)
4. POST /delegation/mark-executed (client.mark_delegation_executed)
"""

import os
import sys

try:
    import armoriq_sdk
    from armoriq_sdk import ArmorIQClient, DelegationRequestParams
except ImportError:
    print("[ERROR] armoriq-sdk is not installed.")
    sys.exit(1)

from backend.armoriq.real import RealArmorIQ


def probe_cloud_capabilities():
    api_key = os.environ.get("ARMORIQ_API_KEY")
    if not api_key:
        print("[SKIP] ARMORIQ_API_KEY is not set.")
        sys.exit(0)

    print("=" * 75)
    print("MANDATE — PROBING CLOUD DELEGATION & APPROVAL CAPABILITIES")
    print("=" * 75)
    print(f"SDK Version    : {getattr(armoriq_sdk, '__version__', 'unknown')}")
    print(f"Backend Endpoint: {os.environ.get('BACKEND_ENDPOINT', 'https://api.armoriq.ai')}")
    print(f"API Key Status : CONFIGURED (Length: {len(api_key)}, [REDACTED])")
    print("-" * 75)

    real_adapter = RealArmorIQ(api_key=api_key)

    # 1. Capture Plan and Mint Token
    print("[1/4] Minting IntentToken for delegation tests...")
    plan_res = real_adapter.capture_plan(
        objective="Probe Delegation and Approval Capability",
        context={
            "mission_id": "probe_mission_01",
            "approved_payees": ["1122334455"],
            "spend_ceilings": {"per_invoice_paise": 50000000},
            "open_pos": ["PO-PROBE-01"],
        },
    )
    token_res = real_adapter.get_intent_token(plan_res.plan_hash, plan_res.envelope)
    print(f"      Token ID Prefix: {token_res.intent_token[:12]}... (Redacted)")
    sdk_token = real_adapter._tokens.get(token_res.intent_token)

    # 2. Probe client.delegate (/iap/trust/delegate)
    print("\n[2/4] Probing client.delegate (/iap/trust/delegate)...")
    try:
        del_res = real_adapter.client.delegate(
            intent_token=sdk_token,
            delegate_public_key="matcher_agent_ed25519_key",
            validity_seconds=3600,
            allowed_actions=["fetch_invoices"],
            target_agent="matcher",
        )
        print(f"      [SUCCESS] client.delegate returned: delegation_id={getattr(del_res, 'delegation_id', None)}")
    except Exception as e:
        print(f"      [NOTE] client.delegate result: {type(e).__name__} -> {e}")

    # 3. Probe client.create_delegation_request (/delegation/request)
    print("\n[3/4] Probing client.create_delegation_request (/delegation/request)...")
    delegation_id = None
    try:
        req_params = DelegationRequestParams(
            tool="initiate_payment",
            action="initiate_payment",
            arguments={"invoice_id": "INV-2041", "payee_account": "509900443322", "amount": 46200.0},
            amount=46200.0,
            requester_email="cfo@mandate.internal",
            requester_role="agent_user",
            requester_limit=0,
            domain="mandate-mcp",
            plan_id=getattr(sdk_token, "plan_id", None),
            intent_reference=getattr(sdk_token, "token_id", None),
            merkle_root=token_res.merkle_root,
            reason="Synthetic hold test: Vendor payee changed to 509900443322",
        )
        req_res = real_adapter.client.create_delegation_request(req_params)
        delegation_id = req_res.delegation_id
        print(f"      [SUCCESS] Created delegation request: delegation_id={delegation_id}")
    except Exception as e:
        print(f"      [NOTE] create_delegation_request result: {type(e).__name__} -> {e}")

    # 4. Probe get_delegation_status and mark_delegation_executed if request was created
    print("\n[4/4] Probing delegation status / lifecycle...")
    if delegation_id:
        try:
            status = real_adapter.client.get_delegation_status(delegation_id)
            print(f"      [SUCCESS] get_delegation_status returned: '{status}'")
            if status == "approved":
                real_adapter.client.mark_delegation_executed("cfo@mandate.internal", delegation_id)
                print("      [SUCCESS] mark_delegation_executed executed successfully.")
        except Exception as e:
            print(f"      [NOTE] get_delegation_status error: {type(e).__name__} -> {e}")
    else:
        print("      [SKIP] Status check skipped because delegation request was not created.")

    print("\n" + "=" * 75)
    print("PROBE COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    probe_cloud_capabilities()
