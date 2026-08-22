# MANDATE — Final Hackathon Submission Readiness Report

**Project Title:** MANDATE — Autonomous Procure-to-Pay with Sealed Authority Envelope  
**Track:** ArmorIQ Problem 1 (*"Autonomous, until it shouldn't be"*) & Problem 2 (*Cryptographic Delegation Across Subagents*)  
**Team Name:** STELLAR STACK  
**Team ID:** team-E657F05D7F45  
**Institution:** AMRITA VISHWA VIDYAPEETHAM, NAGERCOIL  
**Public Repository:** [https://github.com/dwijendrapydimarri-collab/mandate-armoriq-p2p](https://github.com/dwijendrapydimarri-collab/mandate-armoriq-p2p)  
**Submission Status:** **`FROZEN & VERIFIED FOR FINAL SUBMISSION`**

---

## 1. Executive Summary & Capability Matrix

Mandate provides a deterministic, cryptographic execution boundary for autonomous corporate procurement and payment agents. By establishing an immutable **Authority Envelope** at plan time over trusted ERP records before ingesting untrusted invoice documents, Mandate guarantees that autonomous agents can pay registered vendors without babysitting, while cryptographically preventing payment to unauthorized accounts.

### Truthful ArmorIQ Enforcement Matrix

| Capability Surface | Live Status | Honest Disclosure & Boundary |
|---|---|---|
| **Plan Capture (`capture_plan`)** | **`VERIFIED`** | Structured execution plan captured via `ArmorIQClient`; canonical plan hash computed and validated. |
| **Intent Token Minting (`get_intent_token`)** | **`VERIFIED`** | Signed `IntentToken` minted from `/iap/sdk/token` with Merkle root and step proofs. |
| **Remote MCP Dispatch (`fetch_invoices`)** | **`VERIFIED`** | Forwarded to registered HTTPS `mandate-mcp` endpoint via ArmorIQ PEP proxy; returns **`ALLOW`**. |
| **Out-of-Plan Action Interception** | **`VERIFIED`** | Intercepted before MCP dispatch; returns **`BLOCK`** (`INTENT_MISMATCH: Action not found in plan`). |
| **Agent Endpoint Discovery & Auth** | **`VERIFIED`** | All 3 agent identity endpoints respond with `200 OK` on authenticated GET/HEAD probes with `X-API-Key`. |
| **Subagent Delegation (Problem 2)** | **`PARTIALLY VERIFIED`** | Gateway enforces local capability attenuation; cloud subtree delegation remains pending workspace activation. |
| **HOLD / Resume Approval (Problem 1)** | **`PARTIALLY VERIFIED`** | Local parameter integrity verified; fails closed (`ARMORIQ_RESUME_UNSUPPORTED`) in real mode when cloud approval queue is unavailable. |

---

## 2. Public Repository Curation & File Inventory

### Retained Core Assets (Public Branch)
- `README.md` — Complete architecture overview, 7-slide PDF link, video link, launch instructions.
- `SPEC.md` — Authoritative technical specification and security invariants (T1–T6, P8, P10).
- `REAL-ARMORIQ-INTEGRATION-REPORT.md` — Technical audit of live ArmorIQ SDK integration.
- `SUBMISSION-READINESS.md` — Final verification evidence and submission manifest.
- `MANDATE-ROUND2-PRESENTATION.pdf` — Exactly 7 slides, under 10 MB.
- `recordings/mandate_demo_recording.mp4` — Accessible MP4 video with H.264 video, AAC voiceover narration, under 100 MB.
- `recordings/subtitles.srt` — Timestamped English subtitles for the demo video.
- `run.py`, `start.bat`, `start.sh` — Single-command production launch entry points.
- `backend/` — Python 3.11 FastAPI backend, gateway, multi-agent topologies, FastMCP server, and local/real ArmorIQ adapters.
- `frontend/` — React 18 TypeScript frontend, TailwindCSS, React Flow graphs, and Judge Challenge Mode console.
- `tests/` — Automated test suite covering invariants, Judge Mode, and real SDK adapter mapping.
- `scripts/` — Runnable diagnostic and verification scripts (`audit_live_armoriq_advanced.py`, `diagnostic_agent_registration.py`, `verify_live_armoriq_roundtrip.py`).

### Removed Internal & Deliberation Assets
- `IMPLEMENTATION-STATUS.md`, `PUBLIC-REPO-CLEANUP-REPORT.md`, `SEVEN-SLIDE-ANSWERS-AND-DIFFERENTIATION.md`
- `generate_7slide_pdf.py` (logic merged into `backend/generate_pdf.py`)
- `recordings/mandate_browser_rehearsal.webp`, `recordings/narration.wav` (temporary recording intermediate files)
- All private `.env`, `.env.private`, and `agent_tokens.json` files remain untracked and strictly gitignored.

---

## 3. Automated Test Suite Verification (33 Passed, 1 Skipped)

Command: `python -m pytest tests/test_invariants.py tests/test_judge_mode.py tests/test_real_armoriq.py -v`

```text
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\DWIJENDRA\new hacakathon\hackathon 1
plugins: anyio-4.12.1
collected 34 items

tests/test_invariants.py::test_t1_plan_ordering_invariant PASSED         [  2%]
tests/test_invariants.py::test_t1_fails_when_order_inverted PASSED       [  5%]
tests/test_invariants.py::test_t2_block_before_dispatch_spy PASSED       [  8%]
tests/test_invariants.py::test_t3_balance_integrity_and_initiate_payment PASSED [ 11%]
tests/test_invariants.py::test_t4_semantic_parameter_scope_checking PASSED [ 14%]
tests/test_invariants.py::test_t5_delegation_capability_attenuation PASSED [ 17%]
tests/test_invariants.py::test_t6_governance_ab_headline_balances PASSED [ 20%]
tests/test_p8_human_approval_and_rejection_flow PASSED                  [ 23%]
tests/test_invariants.py::test_import_boundary_no_mcp_in_agents PASSED   [ 26%]
tests/test_invariants.py::test_p10_ten_consecutive_cold_reset_runs PASSED [ 29%]
tests/test_invariants.py::test_hold_approval_must_pass_through_gateway PASSED [ 32%]
tests/test_invariants.py::test_generic_policy_with_custom_vendor_and_po_without_hardcoded_ids PASSED [ 35%]
tests/test_invariants.py::test_custom_cfo_ceilings_enforced PASSED       [ 38%]
tests/test_invariants.py::test_scenario_token_isolation_no_cross_contamination PASSED [ 41%]
tests/test_invariants.py::test_hold_resume_spies_enforcer_before_payment PASSED [ 44%]
tests/test_invariants.py::test_hold_resume_blocks_on_tampered_parameters PASSED [ 47%]
tests/test_invariants.py::test_mcp_transport_inprocess_fastmcp_fidelity PASSED [ 50%]
tests/test_judge_mode.py::test_j1_judge_scenario_setup_and_seal_lifecycle PASSED [ 52%]
tests/test_judge_mode.py::test_j2_post_seal_trusted_immutability PASSED  [ 55%]
tests/test_judge_mode.py::test_j3_post_seal_untrusted_invoice_intake PASSED [ 58%]
tests/test_judge_mode.py::test_j4_legitimate_custom_invoice_execution PASSED [ 61%]
tests/test_judge_mode.py::test_j5_security_probe_malicious_proposals PASSED [ 64%]
tests/test_judge_mode.py::test_scenario_database_isolation_no_cross_contamination PASSED [ 67%]
tests/test_judge_mode.py::test_malformed_inputs_and_negative_amounts PASSED [ 70%]
tests/test_judge_mode.py::test_security_probe_tool_whitelist_and_constraints PASSED [ 73%]
tests/test_judge_mode.py::test_proof_labeling_honesty_disclosure PASSED  [ 76%]
tests/test_judge_mode.py::test_production_launch_health_endpoint PASSED  [ 79%]
tests/test_judge_mode.py::test_scenario_cleanup_and_safe_sandbox_isolation PASSED [ 82%]
tests/test_real_armoriq.py::test_sdk_package_installed PASSED            [ 85%]
tests/test_real_armoriq.py::test_real_armoriq_fails_closed_without_api_key PASSED [ 88%]
tests/test_real_armoriq.py::test_real_armoriq_adapter_mapping_with_mock_client PASSED [ 91%]
tests/test_real_armoriq.py::test_real_armoriq_get_intent_token_requires_prior_capture PASSED [ 94%]
tests/test_real_armoriq.py::test_real_armoriq_invoke_exception_mapping PASSED [ 97%]
tests/test_real_armoriq.py::test_live_armoriq_smoke SKIPPED (Live API key required) [100%]

================== 33 passed, 1 skipped, 1 warning in 9.63s ===================
```

---

## 4. Frontend Production Build

Command: `cd frontend && npm run build`

```text
> mandate-frontend@1.0.0 build
> tsc && vite build

vite v6.4.3 building for production...
transforming...
✓ 1763 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.90 kB │ gzip:   0.50 kB
dist/assets/index-DItmx2Fw.css   47.34 kB │ gzip:   8.53 kB
dist/assets/index-DItwWw_5.js   431.58 kB │ gzip: 128.18 kB
✓ built in 3.81s
```

---

## 5. Unified Server Launch & Health Check

Command: `python run.py --host 0.0.0.0 --port 8008`  
Health Probe: `GET http://127.0.0.1:8008/api/health`

```json
{
  "status": "ok",
  "app": "mandate",
  "version": "1.0.0",
  "governance_mode": "on",
  "armoriq_mode": "local"
}
```

---

## 6. Submission Artifact Metrics

| Artifact | Specification Requirement | Measured Metric | Conformance Status |
|---|---|---|---|
| **Presentation Deck** (`MANDATE-ROUND2-PRESENTATION.pdf`) | Exactly 7 slides, $\le$ 10 MB | **7 slides, 9.34 KB** (9,564 bytes) | **`CONFORMING`** |
| **Demo Video** (`recordings/mandate_demo_recording.mp4`) | MP4, $\le$ 100 MB, video + voiceover narration | **2.18 MB** (2,289,667 bytes), H.264 + AAC, 30.90s | **`CONFORMING`** |
| **Subtitles** (`recordings/subtitles.srt`) | Synchronized English subtitles | **36 lines, 1.25 KB** | **`CONFORMING`** |

---

## 7. Zero-Secret Credential Scan Verification

Tracked Git File Scan:
```bash
git ls-files | Select-String -Pattern '(\.env|token|secret|private|credential|key)'
# Result: 0 matches (Empty output)

git grep -nEi 'ak_(live|test|claw)_|agent_tok_' -- ':!*.lock' ':!tests/test_real_armoriq.py'
# Result: 0 matches (Exit code 1 / Clean)
```

---

## 8. Remaining Limitations & Clean Boundaries

1. **Subtree Delegation:** ArmorIQ SDK 0.6.10 delegation endpoints depend on active workspace trust hierarchy registration. In offline evaluation or pending workspace state, Mandate's gateway enforces local subagent capability attenuation.
2. **Approval Session Resume:** When ArmorIQ cloud approval session routes are inactive, Mandate's real adapter fails closed (`ARMORIQ_RESUME_UNSUPPORTED`) rather than executing unverified payments.
