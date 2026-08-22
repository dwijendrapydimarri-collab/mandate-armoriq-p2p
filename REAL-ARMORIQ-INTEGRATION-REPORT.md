# Genuine ArmorIQ SDK Integration & Live Verification Report

**Date/Time:** 2026-08-22T14:00:00+05:30  
**Project:** MANDATE — Autonomous Procure-to-Pay with Sealed Authority Envelope  
**Track:** ArmorIQ Problem 1 (*"Autonomous, until it shouldn't be"*) & Problem 2 (*Cryptographic Delegation Across Subagents*)  
**Team Name:** STELLAR STACK (`team-E657F05D7F45`)  
**Institution:** AMRITA VISHWA VIDYAPEETHAM, NAGERCOIL  
**Public Repository:** [https://github.com/dwijendrapydimarri-collab/mandate-armoriq-p2p](https://github.com/dwijendrapydimarri-collab/mandate-armoriq-p2p)  
**Registered Remote MCP:** `https://compare-phrase-siren.ngrok-free.dev` (`mandate-mcp`)  

---

## 1. Truthful Public Capability Matrix

> **Official Capability Disclosure:**  
> *"Core ArmorIQ plan capture, intent-token issuance, remote MCP ALLOW, and out-of-plan BLOCK are live verified. Delegated grant enforcement and HOLD/resume remain partially verified pending SDK capability confirmation."*

| Feature Area | Primitive / Method | Live Cloud Status | Exact Verification Evidence |
|---|---|---|---|
| **Core Intent Sealing** | `client.capture_plan()` | **`VERIFIED`** | Plan captured with `steps` schema; canonical SHA-256 hash computed and cached. |
| **Core Token Issuance** | `client.get_intent_token()` | **`VERIFIED`** | Real `IntentToken` minted from `/iap/sdk/token` with CSRG Merkle root and step proofs. |
| **Remote MCP Dispatch** | `client.invoke('fetch_invoices')` | **`VERIFIED`** | Forwarded to registered HTTPS `mandate-mcp` endpoint via ArmorIQ PEP proxy; returned genuine **`ALLOW`**. |
| **Out-of-Plan Interception** | `client.invoke('unplanned_tool')` | **`VERIFIED`** | Intercepted before MCP dispatch; returned genuine **`BLOCK`** (`INTENT_MISMATCH`). |
| **Subagent Delegation (P2)** | `client.delegate()` | **`PARTIALLY VERIFIED`** | Client gateway enforces local capability attenuation; cloud delegation session logged as `ARMORIQ_DELEGATION_UNSUPPORTED` when backend subtree route is inactive. |
| **HOLD / Resume (P1)** | `client.get_delegation_status()` | **`PARTIALLY VERIFIED`** | Fails closed with `ARMORIQ_RESUME_UNSUPPORTED` when cloud approval session is not active; parameter tamper detection verified. |

---

## 2. Genuine SDK Methods Used (`armoriq-sdk==0.6.10`)

The adapter in [`backend/armoriq/real.py`](./backend/armoriq/real.py) maps strictly to installed SDK methods without fabricating tokens or proof signatures:

```python
# 1. Plan Capture
plan_capture = client.capture_plan(
    llm="gpt-4o",
    prompt=f"Execute Procure-to-Pay Mission: {objective}",
    plan={"steps": tools_definition, "trusted_authority": ...},
    metadata={"mission_id": mission_id, "cfo_sealed": True},
)

# 2. Intent Token Minting
sdk_token = client.get_intent_token(
    plan_capture=plan_capture,
    policy=policy,
    validity_seconds=3600.0,
)

# 3. Tool Invocation via PEP Proxy
res = client.invoke(
    mcp="mandate-mcp",
    action=tool,
    intent_token=sdk_token,
    params=params,
    user_email="cfo@mandate.internal",
)

# 4. Delegation Check
res = client.delegate(
    intent_token=sdk_token,
    delegate_public_key=child_agent,
    validity_seconds=3600,
    allowed_actions=capabilities,
    target_agent=child_agent,
)

# 5. Hold / Delegation Status Check
status = client.get_delegation_status(decision_id)
```

---

## 3. Redacted Live Smoke Test Evidence

Command: `python .\scripts\smoke_real_armoriq.py`

```text
======================================================================
MANDATE — GENUINE ARMORIQ SDK LIVE SMOKE TEST
======================================================================
SDK Version       : 0.6.10
Mode              : ARMORIQ_MODE=real
IAP Endpoint      : https://iap.armoriq.ai
Proxy Endpoint    : https://proxy.armoriq.ai
Backend Endpoint  : https://api.armoriq.ai
API Key Status    : CONFIGURED (Length: 42, [REDACTED])
----------------------------------------------------------------------
[1/4] Capturing plan via ArmorIQClient...
      Plan Hash Prefix : 0fc2177ef7bad156...
      Sealed At        : 2026-08-22T08:20:14.218542+00:00
[2/4] Minting IntentToken via ArmorIQ IAP...
      Token Status     : ISSUED ([REDACTED])
      Merkle Root      : 4f8a9e2d1c0b3a7e...
[3/4] Testing planned action authorization ('fetch_invoices')...
      Verdict          : ALLOW
      Proof Fields     : ['enforcer', 'status', 'execution_time']
[4/4] Testing unplanned / unauthorized action ('unplanned_malicious_tool')...
      Verdict          : BLOCK
      Reason           : INTENT_MISMATCH: Action 'unplanned_malicious_tool' not found in the original plan.
      Rule Matched     : UNPLANNED_ACTION_BLOCKED
======================================================================
RESULT: LIVE REAL ARMORIQ SDK SMOKE TEST COMPLETED SUCCESSFULLY!
======================================================================
```

---

## 4. Redacted Advanced Audit Output

Command: `python .\scripts\audit_live_armoriq_advanced.py`

```text
===========================================================================
MANDATE — LIVE REAL ARMORIQ SDK ENFORCEMENT & CAPABILITY AUDIT
===========================================================================
SDK Version        : 0.6.10
Mode               : ARMORIQ_MODE=real
API Key Status     : CONFIGURED (Length: 42, [REDACTED])
---------------------------------------------------------------------------
[1/5] Testing Plan Capture & Intent Token Minting...
      Plan Hash Prefix  : b7a1e843f098c21a...
      Token Status      : ISSUED ([REDACTED])
      Merkle Root       : e5c3a91b427d08f4...

[2/5] Testing Remote MCP 'fetch_invoices' Invocation (Planned)...
      Verdict           : ALLOW
      Reason            : ArmorIQ SDK verified action against sealed authority plan
      Proof Fields      : ['enforcer', 'status', 'execution_time']

[3/5] Testing Out-of-Plan Tool 'unplanned_malicious_tool' (Should BLOCK)...
      Verdict           : BLOCK
      Reason            : INTENT_MISMATCH: Action 'unplanned_malicious_tool' not found in plan
      Rule Matched      : UNPLANNED_ACTION_BLOCKED

[4/5] Auditing Subagent Delegation Mechanism (Problem 2)...
      Grant ID          : grant_4c281a9f02e1
      Grant Signature   : ARMORIQ_DELEGATION_UNSUPPORTED...
      Delegation Status : PARTIAL (SDK delegation endpoint not supported in this session; client-attenuated)

[5/5] Auditing HOLD & Resume Approval Mechanism (Problem 1)...
      Resume Verdict    : BLOCK
      Resume Reason     : ARMORIQ_RESUME_UNSUPPORTED: No active ArmorIQ cloud approval session found for decision 'dec_hold_audit_001'
      Resume Status     : PARTIAL (Cloud approval session unavailable; fail-closed in real mode)

===========================================================================
MANDATE — FINAL LIVE ARMORIQ CAPABILITY MATRIX
===========================================================================
1. Plan Capture & Intent Token Issuance : VERIFIED
2. Remote MCP Tool Invocation (ALLOW)   : VERIFIED
3. Out-of-Plan Action Interception (BLOCK): VERIFIED
4. Cryptographic Delegation (Problem 2) : PARTIAL
5. Cloud Approval / Resume (Problem 1)  : PARTIAL
---------------------------------------------------------------------------
FINAL VERDICT: CORE ARMORIQ VERIFIED; DELEGATION/RESUME PARTIAL
===========================================================================
```

---

## 5. Automated Test Suite Results (33 Passed, 1 Skipped)

Command: `python -m pytest tests/test_invariants.py tests/test_judge_mode.py tests/test_real_armoriq.py -v`

- `tests/test_invariants.py` $\rightarrow$ **17 passed**
- `tests/test_judge_mode.py` $\rightarrow$ **11 passed**
- `tests/test_real_armoriq.py` $\rightarrow$ **5 passed, 1 skipped** (*`test_live_armoriq_smoke` skipped in CI without live API key*)
- **Total:** **33 passed, 1 skipped in 10.66s**
