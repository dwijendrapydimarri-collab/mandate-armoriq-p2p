"""
MANDATE — Live ArmorIQ Advanced Enforcement Audit Script
Performs a rigorous, truthful audit of live ArmorIQ cloud enforcement:
1. Plan Capture & Intent Token Issuance (Core)
2. Remote MCP Tool Invocation via Registered Proxy (fetch_invoices -> ALLOW) (Core)
3. Out-of-Plan Proposal Interception (unplanned_tool -> BLOCK) (Core)
4. Subagent Delegation Status Inspection (Problem 2)
5. HOLD / Resume Approval Session Inspection (Problem 1)

Exit Codes:
- 0: Core ArmorIQ Verified (with explicit capability status for delegation/resume)
- 1: Core ArmorIQ Failure (planned action denied or unplanned action allowed)
"""

import os
import sys
import json

try:
    import armoriq_sdk
except ImportError:
    print("[ERROR] armoriq-sdk is not installed.")
    sys.exit(1)

from backend.armoriq.real import RealArmorIQ


def run_advanced_audit():
    api_key = os.environ.get("ARMORIQ_API_KEY")
    if not api_key:
        print("[SKIP] ARMORIQ_API_KEY is not set.")
        sys.exit(0)

    print("=" * 75)
    print("MANDATE — LIVE REAL ARMORIQ SDK ENFORCEMENT & CAPABILITY AUDIT")
    print("=" * 75)
    print(f"SDK Version        : {getattr(armoriq_sdk, '__version__', 'unknown')}")
    print(f"Mode               : ARMORIQ_MODE=real")
    print(f"API Key Status     : CONFIGURED (Length: {len(api_key)}, [REDACTED])")
    print("-" * 75)

    real_adapter = RealArmorIQ(api_key=api_key)

    core_verified = True
    delegation_verified = False
    resume_verified = False

    # -------------------------------------------------------------
    # 1. Capture Plan & Token Minting
    # -------------------------------------------------------------
    print("[1/5] Testing Plan Capture & Intent Token Minting...")
    try:
        plan_res = real_adapter.capture_plan(
            objective="Procure-to-Pay Autonomous Settle Batch 1",
            context={
                "mission_id": "audit_mission_01",
                "approved_payees": ["1122334455", "9988776655"],
                "spend_ceilings": {"per_invoice_paise": 50000000, "mission_paise": 200000000},
                "open_pos": ["PO-1001", "PO-1004"],
            },
        )
        print(f"      Plan Hash Prefix  : {plan_res.plan_hash[:16]}...")

        token_res = real_adapter.get_intent_token(plan_res.plan_hash, plan_res.envelope)
        print(f"      Token Status      : ISSUED ([REDACTED])")
        print(f"      Merkle Root       : {token_res.merkle_root[:16] if token_res.merkle_root else 'None (Token-bound)'}...")
    except Exception as e:
        print(f"      [FAILED] Token issuance error: {e}")
        sys.exit(1)

    # -------------------------------------------------------------
    # 2. Remote MCP Tool Invocation Verification (Planned -> ALLOW)
    # -------------------------------------------------------------
    print("\n[2/5] Testing Remote MCP 'fetch_invoices' Invocation (Planned)...")
    decision_read = real_adapter.invoke(
        agent_id="matcher",
        tool="fetch_invoices",
        params={},
        intent_token=token_res.intent_token,
    )
    print(f"      Verdict           : {decision_read.verdict}")
    print(f"      Reason            : {decision_read.reason}")
    print(f"      Proof Fields      : {list(decision_read.proof.keys())}")

    if decision_read.verdict != "ALLOW":
        print(f"      [ERROR] Expected ALLOW for planned tool, got {decision_read.verdict}")
        core_verified = False
        sys.exit(1)

    # -------------------------------------------------------------
    # 3. Out-of-Plan Tool Invocation (Unplanned -> BLOCK)
    # -------------------------------------------------------------
    print("\n[3/5] Testing Out-of-Plan Tool 'unplanned_malicious_tool' (Should BLOCK)...")
    decision_unplanned = real_adapter.invoke(
        agent_id="disburser",
        tool="unplanned_malicious_tool",
        params={"payload": "malicious_script"},
        intent_token=token_res.intent_token,
    )
    print(f"      Verdict           : {decision_unplanned.verdict}")
    print(f"      Reason            : {decision_unplanned.reason}")
    print(f"      Rule Matched      : {decision_unplanned.rule_matched}")

    if decision_unplanned.verdict != "BLOCK":
        print(f"      [ERROR] Expected BLOCK for unplanned action, got {decision_unplanned.verdict}")
        core_verified = False
        sys.exit(1)

    if "ARMORIQ_UNAVAILABLE" in decision_unplanned.reason:
        print("      [WARN] Block was due to service unavailability, not policy mismatch.")
        core_verified = False
        sys.exit(1)

    # -------------------------------------------------------------
    # 4. Subagent Delegation Audit (Problem 2)
    # -------------------------------------------------------------
    print("\n[4/5] Auditing Subagent Delegation Mechanism (Problem 2)...")
    grant_matcher = real_adapter.delegate(
        mission_id="audit_mission_01",
        parent_agent="controller",
        child_agent="matcher",
        capabilities=["fetch_invoices"],
        ceiling_paise=0,
        payee_scope=[],
        intent_token=token_res.intent_token,
    )
    print(f"      Grant ID          : {grant_matcher.grant_id}")
    print(f"      Grant Signature   : {grant_matcher.signature[:35]}...")

    if "armoriq_delegation" in grant_matcher.signature:
        delegation_verified = True
        print("      Delegation Status : VERIFIED (SDK delegation token returned)")
    else:
        print("      Delegation Status : PARTIAL (SDK delegation endpoint not supported in this session; client-attenuated)")

    # -------------------------------------------------------------
    # 5. HOLD & Resume Approval Audit (Problem 1)
    # -------------------------------------------------------------
    print("\n[5/5] Auditing HOLD & Resume Approval Mechanism (Problem 1)...")
    hold_decision_id = "dec_hold_audit_001"
    original_params = {"invoice_id": "INV-2041", "payee_account": "509900443322", "amount_paise": 4620000}

    resume_res = real_adapter.resume(
        decision_id=hold_decision_id,
        approver="cfo@mandate.internal",
        expected_params=original_params,
        intent_token=token_res.intent_token,
    )
    print(f"      Resume Verdict    : {resume_res.verdict}")
    print(f"      Resume Reason     : {resume_res.reason}")

    if resume_res.verdict == "ALLOW" and resume_res.proof.get("status") == "APPROVED":
        resume_verified = True
        print("      Resume Status     : VERIFIED (ArmorIQ cloud approval confirmed)")
    else:
        print("      Resume Status     : PARTIAL (Cloud approval session unavailable; fail-closed in real mode)")

    # -------------------------------------------------------------
    # Final Summary Matrix
    # -------------------------------------------------------------
    print("\n" + "=" * 75)
    print("MANDATE — FINAL LIVE ARMORIQ CAPABILITY MATRIX")
    print("=" * 75)
    print(f"1. Plan Capture & Intent Token Issuance : {'VERIFIED' if core_verified else 'FAILED'}")
    print(f"2. Remote MCP Tool Invocation (ALLOW)   : {'VERIFIED' if core_verified else 'FAILED'}")
    print(f"3. Out-of-Plan Action Interception (BLOCK): {'VERIFIED' if core_verified else 'FAILED'}")
    print(f"4. Cryptographic Delegation (Problem 2) : {'VERIFIED' if delegation_verified else 'PARTIAL'}")
    print(f"5. Cloud Approval / Resume (Problem 1)  : {'VERIFIED' if resume_verified else 'PARTIAL'}")
    print("-" * 75)
    if core_verified and not (delegation_verified and resume_verified):
        print("FINAL VERDICT: CORE ARMORIQ VERIFIED; DELEGATION/RESUME PARTIAL")
    elif core_verified and delegation_verified and resume_verified:
        print("FINAL VERDICT: FULL REAL ARMORIQ VERIFIED")
    else:
        print("FINAL VERDICT: NOT VERIFIED")
    print("=" * 75)


if __name__ == "__main__":
    run_advanced_audit()
