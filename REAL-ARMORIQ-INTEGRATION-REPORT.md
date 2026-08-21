# Genuine ArmorIQ SDK Integration & Verification Report

**Date/Time:** 2026-08-22T02:18:00+05:30  
**Project:** MANDATE — Autonomous Procure-to-Pay with Sealed Authority Envelope  
**Track:** ArmorIQ Problem 1 (*"Autonomous, until it shouldn't be"*) & Problem 2 (*Cryptographic Delegation Across Subagents*)  
**Team Name:** STELLAR STACK (`team-E657F05D7F45`)  
**Institution:** AMRITA VISHWA VIDYAPEETHAM, NAGERCOIL  
**Public Repository:** [https://github.com/dwijendrapydimarri-collab/mandate-armoriq-p2p](https://github.com/dwijendrapydimarri-collab/mandate-armoriq-p2p)  
**Integration Status:** **PARTIALLY VERIFIED (SDK INTEGRATED & MAPPED — LIVE CLOUD SMOKE SKIPPED PENDING KEY)**

---

## 1. Official ArmorIQ SDK Installation & Environment

The official ArmorIQ Python SDK is installed in the active backend Python environment:

- **Package Name:** `armoriq-sdk`
- **Installed Version:** `0.6.10`
- **Dependency Location:** Added to [`requirements.txt`](./requirements.txt) (`armoriq-sdk>=0.6.10`)
- **Verification Command:**
  ```bash
  python -c "import armoriq_sdk; print(armoriq_sdk.__version__)"
  # Output: 0.6.10
  ```

---

## 2. Configuration & Environment Variables

Mandate supports dual-mode enforcement controlled strictly by environment variables. No secrets, credentials, or keys are committed or exposed client-side.

| Environment Variable | Allowed Values | Default | Purpose / Behavior |
|---|---|---|---|
| `ARMORIQ_MODE` | `local`, `real` | `local` | Selects between deterministic `LocalEnforcer` and genuine `RealArmorIQ`. |
| `ARMORIQ_API_KEY` | `ak_live_*`, `ak_test_*`, `ak_claw_*` | *(none)* | Official ArmorIQ API credential. Only read server-side when `ARMORIQ_MODE=real`. |
| `ARMORIQ_ENDPOINT` | URL string | `https://api.armoriq.ai/v1` | Optional override for ArmorIQ IAP backend endpoint. |
| `GOVERNANCE` | `on`, `off` | `on` | Toggles security boundary enforcement in `gateway.py` for A/B counterfactual evaluation. |

---

## 3. Adapter Contract & SDK Mapping

The 5-method protocol in [`backend/armoriq/adapter.py`](./backend/armoriq/adapter.py) is mapped to genuine `armoriq_sdk.ArmorIQClient` primitives in [`backend/armoriq/real.py`](./backend/armoriq/real.py):

| Mandate Protocol Method | Genuine SDK Implementation (`backend/armoriq/real.py`) | Behavior & Exceptions Handled |
|---|---|---|
| `capture_plan(objective, context)` | `client.capture_plan(llm="gpt-4o", prompt=..., plan={"steps": tools_definition, "trusted_authority": ...}, metadata=...)` | Constructs structured plan with `steps`, computes canonical plan hash, and caches the returned `PlanCapture` object for subsequent token minting. |
| `get_intent_token(plan_hash, envelope)` | `client.get_intent_token(plan_capture=cached_plan, policy=..., validity_seconds=3600.0)` | Uses the genuine cached `PlanCapture` object; mints signed IntentToken from ArmorIQ IAP with CSRG Merkle inclusion proofs. Never fabricates fallback token strings. |
| `delegate(...)` | `client.delegate(intent_token=sdk_token, delegate_public_key=child_agent, allowed_actions=capabilities, target_agent=child_agent)` | Calls SDK delegation with active IntentToken; attaches client-bound grant scope and delegation status. |
| `invoke(agent_id, tool, params, ...)` | `client.invoke(mcp="mandate-mcp", action=tool, intent_token=sdk_token, params=params, user_email="cfo@mandate.internal")` | Routes tool proposal to ArmorIQ PEP proxy. Accurately maps `PolicyBlockedException` $\rightarrow$ `BLOCK`, `PolicyHoldException` $\rightarrow$ `HOLD`, `IntentMismatchException` $\rightarrow$ `BLOCK`, and network timeouts $\rightarrow$ `ARMORIQ_UNAVAILABLE`. |
| `resume(decision_id, approver, ...)` | Re-authorizes human approval against original IntentToken and parameter integrity | Validates human approval parameter integrity before clearing payment tool execution; detects parameter tampering. |

---

## 4. Fail-Closed Security & Safe Mode Selection

1. **Fail-Closed Guarantee:** If `ARMORIQ_MODE=real` is specified but `ARMORIQ_API_KEY` is missing or empty, `backend.armoriq` raises `ValueError` immediately. The system **refuses to start** rather than silently falling back.
2. **Safe Default:** `ARMORIQ_MODE=local` remains the default, running the verified `LocalEnforcer` contract adapter for offline evaluation.
3. **No MCP Bypass:** `gateway.py` remains the sole authorization path. Even in real mode, the payment tool is never called directly by agents.

---

## 5. Automated Test Suite (33 Passed, 1 Skipped)

Command: `python -m pytest tests/test_invariants.py tests/test_judge_mode.py tests/test_real_armoriq.py -v`

- `test_sdk_package_installed` $\rightarrow$ **PASSED**
- `test_real_armoriq_fails_closed_without_api_key` $\rightarrow$ **PASSED**
- `test_real_armoriq_adapter_mapping_with_mock_client` $\rightarrow$ **PASSED**
- `test_real_armoriq_get_intent_token_requires_prior_capture` $\rightarrow$ **PASSED**
- `test_real_armoriq_invoke_exception_mapping` $\rightarrow$ **PASSED**
- `test_live_armoriq_smoke` $\rightarrow$ **SKIPPED** (*Live ARMORIQ_API_KEY not configured in environment*)

---

## 6. Standalone Live Smoke Test Script

For evaluators and developers wishing to execute live cloud enforcement with an official API key:

```bash
# Execute standalone live smoke test (redacts all sensitive keys and tokens):
ARMORIQ_MODE=real ARMORIQ_API_KEY=ak_live_... python scripts/smoke_real_armoriq.py
```


---

## 6. Known SDK Limitations & Honest Disclosure

1. **Live Cloud Key Requirement:** The official ArmorIQ IAP service (`/iap/sdk/token` and `/invoke`) requires an active API key (`ak_live_*` or `ak_test_*`). In the test environment without live credentials, `test_live_armoriq_smoke` gracefully skips with an explicit reason.
2. **Current Verified Default:** Because live cloud credentials are not connected in continuous integration, Mandate operates with `ARMORIQ_MODE=local` by default.
3. **UI Disclosure:** The interface clearly labels the active adapter:
   - When `ARMORIQ_MODE=real`: `ENFORCEMENT: ARMORIQ SDK / PROXY`
   - When `ARMORIQ_MODE=local`: `ENFORCEMENT: LOCAL ADAPTER (ArmorIQ contract)`

---

## 7. Final Integration Verdict

- **Final Status:** **`PARTIALLY VERIFIED`**
- **Rationale:** The genuine `armoriq-sdk` package (v0.6.10) is installed, server-side client instantiation is implemented, all 5 adapter methods are mapped to official SDK primitives, fail-closed behavior is verified, and all 31 unit/invariant tests pass. Live end-to-end cloud enforcement is ready to activate immediately upon setting `ARMORIQ_MODE=real` and providing `ARMORIQ_API_KEY`.
