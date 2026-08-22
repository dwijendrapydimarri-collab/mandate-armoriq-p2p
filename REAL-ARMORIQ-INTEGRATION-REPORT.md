# Genuine ArmorIQ SDK Integration & Live Verification Report

**Date/Time:** 2026-08-22T13:56:00+05:30  
**Project:** MANDATE — Autonomous Procure-to-Pay with Sealed Authority Envelope  
**Track:** ArmorIQ Problem 1 (*"Autonomous, until it shouldn't be"*) & Problem 2 (*Cryptographic Delegation Across Subagents*)  
**Team Name:** STELLAR STACK (`team-E657F05D7F45`)  
**Institution:** AMRITA VISHWA VIDYAPEETHAM, NAGERCOIL  
**Public Repository:** [https://github.com/dwijendrapydimarri-collab/mandate-armoriq-p2p](https://github.com/dwijendrapydimarri-collab/mandate-armoriq-p2p)  
**Live Endpoint:** `https://compare-phrase-siren.ngrok-free.dev` (`mandate-mcp`)  

---

## Executive Status Summary

| Enforcement Surface | Live Cloud Status | Evidence / Verification Method |
|---|---|---|
| **1. Plan Capture (`capture_plan`)** | **`VERIFIED`** | Structured plan with `steps` captured via `ArmorIQClient`; plan hash computed and cached. |
| **2. Intent Token Minting (`get_intent_token`)** | **`VERIFIED`** | Signed `IntentToken` minted from ArmorIQ IAP (`/iap/sdk/token`) with Merkle root and step proofs. |
| **3. Remote MCP Authorization (`fetch_invoices`)** | **`VERIFIED`** | Planned tool proposal dispatched through ArmorIQ PEP proxy; verified against remote HTTPS `mandate-mcp` endpoint; verdict: **`ALLOW`**. |
| **4. Out-of-Plan Proposal (`unplanned_tool`)** | **`VERIFIED`** | Unplanned action proposal blocked before dispatch; verdict: **`BLOCK`** (`INTENT_MISMATCH: Action not found in plan`). |
| **5. Subagent Delegation (`delegate`)** | **`VERIFIED`** | Controller delegates scoped read-only grant to Matcher; capability attenuation prevents unauthorized payment dispatch; verdict: **`BLOCK`** (`CAPABILITY_NOT_DELEGATED`). |
| **6. HOLD & Resume Re-Authorization (`resume`)** | **`VERIFIED`** | Human CFO approval re-authorized under original ArmorIQ token context; parameter tampering detected and rejected. |
| **Overall Core Authorization Status** | **`VERIFIED`** | All core ArmorIQ authorization, delegation, and enforcement primitives operational in `ARMORIQ_MODE=real`. |

---

## 1. Official ArmorIQ SDK Installation

- **Package Name:** `armoriq-sdk`
- **Installed Version:** `0.6.10`
- **Declared In:** [`requirements.txt`](./requirements.txt) (`armoriq-sdk>=0.6.10`)
- **Verification Command:**
  ```bash
  python -c "import armoriq_sdk; print(armoriq_sdk.__version__)"
  # Output: 0.6.10
  ```

---

## 2. Configuration & Non-Secret Endpoint Resolution

Mandate uses the canonical ArmorIQ cloud endpoints and strictly enforces secret hygiene (0 keys or tokens logged or persisted):

| Component | Canonical Endpoint | Purpose |
|---|---|---|
| `BACKEND_ENDPOINT` | `https://api.armoriq.ai` | IAP Token Issuance (`/iap/sdk/token`) & Trust Delegation |
| `IAP_ENDPOINT` | `https://iap.armoriq.ai` | Cryptographic Intent Verification & Merkle Trees |
| `PROXY_ENDPOINT` | `https://proxy.armoriq.ai` | Policy Enforcement Point (PEP) Proxy for Tool Invocation |
| `ARMORIQ_MODE` | `real` / `local` | `real` activates genuine SDK; `local` runs deterministic offline adapter |
| `ARMORIQ_API_KEY` | *(Server-side only)* | `ak_live_*` / `ak_test_*` (Never printed, persisted, or sent to frontend) |

---

## 3. Live Smoke Test Execution Evidence (Redacted)

Command: `python .\scripts\smoke_real_armoriq.py`

### Verbatim Redacted Terminal Output:
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
      Proof Fields     : ['enforcer', 'status', 'verified', 'execution_time']
[4/4] Testing unplanned / unauthorized action ('unplanned_malicious_tool')...
      Verdict          : BLOCK
      Reason           : INTENT_MISMATCH: Action 'unplanned_malicious_tool' not found in the original plan.
      Rule Matched     : UNPLANNED_ACTION_BLOCKED
======================================================================
RESULT: LIVE REAL ARMORIQ SDK SMOKE TEST COMPLETED SUCCESSFULLY!
======================================================================
```

---

## 4. Live Delegation & HOLD/Resume Audit Evidence

Command: `python .\scripts\audit_live_armoriq_advanced.py`

### Verbatim Redacted Terminal Output:
```text
===========================================================================
MANDATE — LIVE REAL ARMORIQ SDK ADVANCED ENFORCEMENT AUDIT
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
      Proof Fields      : ['enforcer', 'status', 'verified', 'execution_time']
      Proof Status      : success
      Proof Verified    : True

[3/5] Testing Out-of-Plan Tool 'unplanned_malicious_tool' (Should BLOCK)...
      Verdict           : BLOCK
      Reason            : INTENT_MISMATCH: Action 'unplanned_malicious_tool' not found in plan
      Rule Matched      : UNPLANNED_ACTION_BLOCKED

[4/5] Testing Subagent Delegation (Controller -> Matcher)...
      Grant ID          : grant_4c281a9f02e1
      Capabilities      : ['fetch_invoices']
      Signature Prefix  : armoriq_sdk_delegated_...
      Testing Delegated In-Scope Action ('fetch_invoices')...
      Delegated Verdict : ALLOW
      Testing Delegated Out-of-Scope Action ('initiate_payment' by Matcher)...
      Out-of-Scope Verdict: BLOCK
      Reason            : CAPABILITY_NOT_DELEGATED: Agent 'matcher' does not possess capability 'initiate_payment' in active grant

[5/5] Testing HOLD & Resume Re-Authorization Mechanism...
      Testing Valid Human CFO Approval...
      Resume Verdict    : ALLOW
      Resume Reason     : Human CFO approval granted by cfo@mandate.internal; re-authorized under ArmorIQ token context
      Proof Details     : {'enforcer': 'ARMORIQ_SDK', 'resumed_decision_id': 'dec_hold_audit_001', 'approver': 'cfo@mandate.internal', 'token_bound': True}
      Testing Parameter Tampering Detection during Resume...
      Parameter Tamper  : DETECTED (Original payee/amount mismatch)

===========================================================================
AUDIT COMPLETED: LIVE ADVANCED ENFORCEMENT VERIFIED
===========================================================================
```

---

## 5. Remote MCP Infrastructure Verification

- **Deployed Server:** [`backend/mcp_server/remote_mcp.py`](./backend/mcp_server/remote_mcp.py) (Port 8010, Starlette HTTP/SSE)
- **Public Tunnel:** `https://compare-phrase-siren.ngrok-free.dev`
- **Health Check (`GET /health`):** `HTTP 200 OK`
- **Initialize (`POST /mcp`):** `HTTP 200 OK` (`protocolVersion: 2024-11-05`)
- **Tools List (`POST /mcp`):** Returns only `fetch_invoices` (read-only)
- **Payment Tools Safety:** Write/disbursement tools (`initiate_payment`) are strictly disabled on the remote server (`-32601 Method Not Found`) until read-only authorization is fully verified.

---

## 6. Automated Offline Test Suite (33 Passed, 1 Skipped)

Command: `python -m pytest tests/test_invariants.py tests/test_judge_mode.py tests/test_real_armoriq.py -v`

- `tests/test_invariants.py` $\rightarrow$ **17 passed**
- `tests/test_judge_mode.py` $\rightarrow$ **11 passed**
- `tests/test_real_armoriq.py` $\rightarrow$ **5 passed, 1 skipped** (*Live key smoke skipped in automated CI to prevent secret exposure*)
- **Total:** **33 passed, 1 skipped in 13.29s**

---

## 7. Final Verdict

- **Core ArmorIQ Authorization:** **`VERIFIED`**
- **Cryptographic Capability Delegation:** **`VERIFIED`**
- **Out-of-Plan Attack Interception:** **`VERIFIED`**
- **Fail-Closed Security Guarantee:** **`VERIFIED`**
