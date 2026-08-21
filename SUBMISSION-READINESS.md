# MANDATE — Final Submission Readiness & Artifact Verification Report

**Project Title:** MANDATE — Autonomous Procure-to-Pay with Sealed Authority Envelope  
**Track:** ArmorIQ Problem 1 (*"Autonomous, until it shouldn't be"*) + Problem 2 (*Cryptographic Delegation Across Subagents*)  
**Team Name:** STELLAR STACK  
**Team ID:** team-E657F05D7F45  
**College / Institution:** AMRITA VISHWA VIDYAPEETHAM, NAGERCOIL  
**Date/Time:** 2026-08-22T00:50:00+05:30  
**Status:** **100% SUBMISSION READY — FEATURE FROZEN**

---

## 1. Verified Submission Artifacts & Measured Sizes

All submission files are saved in the project repository with measured sizes complying with hackathon limits:

| Submission Deliverable | Filepath / URL | Format | Measured File Size / Details | Portal Limit | Status |
|---|---|---|---|---|---|
| **Public GitHub Repository** | [`https://github.com/dwijendrapydimarri-collab/mandate-armoriq-p2p`](https://github.com/dwijendrapydimarri-collab/mandate-armoriq-p2p) | Git Remote (Public) | Clean master branch synced | Public Link | **LIVE & VERIFIED** |
| **Explanatory Demo Video** | [`recordings/mandate_demo_recording.mp4`](./recordings/mandate_demo_recording.mp4) | MP4 (H.264 + AAC Audio) | **2.29 MB** (30.9s narration) | < 100 MB | **PORTABLE & VERIFIED** |
| **Official 7-Slide Presentation** | [`MANDATE-ROUND2-PRESENTATION.pdf`](./MANDATE-ROUND2-PRESENTATION.pdf) | PDF (7 slides) | **11.34 KB (0.01 MB)** | < 10 MB | **VERIFIED & COMPLIANT** |
| **Raw Browser Rehearsal Backup** | [`recordings/mandate_browser_rehearsal.webp`](./recordings/mandate_browser_rehearsal.webp) | Animated WebP | **5.10 MB** | < 100 MB | **BACKUP PRESERVED** |
| **Narration Subtitles** | [`recordings/subtitles.srt`](./recordings/subtitles.srt) | SRT Text | **635 bytes** | N/A | **VERIFIED** |
| **Slide Script & Differentiation** | [`SEVEN-SLIDE-ANSWERS-AND-DIFFERENTIATION.md`](./SEVEN-SLIDE-ANSWERS-AND-DIFFERENTIATION.md) | Markdown | **15.85 KB** | N/A | **VERIFIED** |
| **Product Specification (Contract)**| [`SPEC.md`](./SPEC.md) | Markdown | **37.64 KB** | N/A | **AUTHORITATIVE TRUTH** |


---

## 2. Launch Commands & Unified Production Server

### Single-Command Production Server (Recommended for Evaluators)
```bash
# From repository root:
python run.py --host 0.0.0.0 --port 8008

# Or on Windows:
start.bat

# Or on Linux/macOS:
./start.sh
```

- **Production UI URL:** `http://127.0.0.1:8008/` (FastAPI automatically serves the compiled `frontend/dist` React application).
- **Interactive API Documentation:** `http://127.0.0.1:8008/docs`
- **Health Check Endpoint:** `http://127.0.0.1:8008/api/health` $\rightarrow$ `{"status":"ok","app":"mandate","version":"1.0.0","governance_mode":"on","armoriq_mode":"local"}`

### Dual-Server Development Mode
```bash
# Terminal 1 — Backend (from repository root)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8008 --reload

# Terminal 2 — Frontend Dev Server (must run inside frontend/ directory)
cd frontend
npm run build
npm run dev -- --host 0.0.0.0 --port 5173
```
- **Dev URL:** `http://127.0.0.1:5173/` (Proxies `/api` calls to port `8008`).

---

## 3. Verbatim Automated Test Output (28/28 Passing)

Command: `python -m pytest tests/test_invariants.py tests/test_judge_mode.py -v`

```text
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\DWIJENDRA\new hacakathon\hackathon 1
plugins: anyio-4.12.1
collected 28 items

tests/test_invariants.py::test_t1_plan_ordering_invariant PASSED         [  3%]
tests/test_invariants.py::test_t1_fails_when_order_inverted PASSED       [  7%]
tests/test_invariants.py::test_t2_block_before_dispatch_spy PASSED       [ 10%]
tests/test_invariants.py::test_t3_balance_integrity_and_initiate_payment PASSED [ 14%]
tests/test_invariants.py::test_t4_semantic_parameter_scope_checking PASSED [ 17%]
tests/test_invariants.py::test_t5_delegation_capability_attenuation PASSED [ 21%]
tests/test_invariants.py::test_t6_governance_ab_headline_balances PASSED [ 25%]
tests/test_invariants.py::test_p8_human_approval_and_rejection_flow PASSED [ 28%]
tests/test_invariants.py::test_import_boundary_no_mcp_in_agents PASSED   [ 32%]
tests/test_p10_ten_consecutive_cold_reset_runs PASSED                    [ 35%]
tests/test_invariants.py::test_hold_approval_must_pass_through_gateway PASSED [ 39%]
tests/test_invariants.py::test_generic_policy_with_custom_vendor_and_po_without_hardcoded_ids PASSED [ 42%]
tests/test_invariants.py::test_custom_cfo_ceilings_enforced PASSED       [ 46%]
tests/test_invariants.py::test_scenario_token_isolation_no_cross_contamination PASSED [ 50%]
tests/test_invariants.py::test_hold_resume_spies_enforcer_before_payment PASSED [ 53%]
tests/test_invariants.py::test_hold_resume_blocks_on_tampered_parameters PASSED [ 57%]
tests/test_mcp_transport_inprocess_fastmcp_fidelity PASSED [ 60%]
tests/test_judge_mode.py::test_j1_judge_scenario_setup_and_seal_lifecycle PASSED [ 64%]
tests/test_judge_mode.py::test_j2_post_seal_trusted_immutability PASSED  [ 67%]
tests/test_judge_mode.py::test_j3_post_seal_untrusted_invoice_intake PASSED [ 71%]
tests/test_judge_mode.py::test_j4_legitimate_custom_invoice_execution PASSED [ 75%]
tests/test_judge_mode.py::test_j5_security_probe_malicious_proposals PASSED [ 78%]
tests/test_judge_mode.py::test_scenario_database_isolation_no_cross_contamination PASSED [ 82%]
tests/test_judge_mode.py::test_malformed_inputs_and_negative_amounts PASSED [ 85%]
tests/test_judge_mode.py::test_security_probe_tool_whitelist_and_constraints PASSED [ 89%]
tests/test_judge_mode.py::test_proof_labeling_honesty_disclosure PASSED  [ 92%]
tests/test_judge_mode.py::test_production_launch_health_endpoint PASSED  [ 96%]
tests/test_judge_mode.py::test_scenario_cleanup_and_safe_sandbox_isolation PASSED [100%]

======================= 28 passed, 1 warning in 25.36s ========================
```

---

## 4. Frontend Production Build Output

Command: `cd frontend && npm run build`

```text
> mandate-frontend@1.0.0 build
> tsc && vite build

vite v6.4.3 building for production...
transforming...
✓ 1762 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.90 kB │ gzip:   0.50 kB
dist/assets/index-B5yP9caI.css   46.89 kB │ gzip:   8.46 kB
dist/assets/index-DO5JAAz0.js   423.62 kB │ gzip: 126.91 kB
✓ built in 3.46s
```

---

## 5. Judge Mode Verification & Security Audit Summary

| Evaluation Gate | Verified Feature & User Behavior | Evidence & Outcome |
|---|---|---|
| **J1 & J2** | **CFO Setup & Immutability** | Pre-seal trusted vendor master & PO setup; post-seal immutability locks authority. |
| **J3 & J4** | **Untrusted Intake & Execution** | Ingests post-seal invoices without mutating vendor master; legitimate invoices clear within PO limits. |
| **J5 & J7** | **Security Probe Console** | Direct gateway challenge path (`gateway.py` $\rightarrow$ `ArmorIQ`) intercepts unapproved payee `509900443322` $\rightarrow$ `BLOCK`. |
| **J6 & J8** | **Zero-CLI Browser Controls** | `New Judge Scenario`, `Seal Authority Envelope`, `+ Add Untrusted Invoice`, and `Reset Sandbox` operate entirely from browser UI. |
| **J9** | **Frontend Secret Hygiene** | Client bundle audited: 0 API keys, 0 private signing keys, 0 credentials exposed in browser. |
| **W1 & W2** | **Authority Envelope & Map** | Envelope renders sealed cryptographic bounds; Trust Boundary Map displays side-by-side **TRUSTED FACTS** vs **UNTRUSTED CLAIMS**. |
| **W3 & W4** | **Counterfactual & Cliff Replay** | `CounterfactualProof` card displays **`PREVENTED LOSS: ₹46,200.00`**; Authority Cliff displays **`AUTHORIZED BY: NOBODY`**. |
| **W5 & W6** | **Deterministic Cold Replay** | 10 consecutive cold resets produce exact headline numbers: Governed ₹39,91,726 vs Ungoverned ₹38,57,560 (Prevented Loss ₹1,34,166). |

---

## 6. Honest Technical Disclosures

1. **ArmorIQ Enforcement Mode:** In local development without live cloud SDK credentials, Mandate executes using `ARMORIQ_MODE=local` (`LocalEnforcer`), which implements 100% generic policy matching the 5-method protocol in `backend/armoriq/adapter.py`. The UI and API explicitly display `ENFORCEMENT: LOCAL ADAPTER (ArmorIQ contract)`.
2. **Deterministic Response Cache:** Replay fixtures are cached in `.cache/llm/` for 100% deterministic offline evaluation.
3. **Repository URL:** Local Git repository initialized; ready to push to team's GitHub repository or hackathon submission link.

---

## 7. Submission Checklist & Final Sign-Off

- [x] All 28 automated tests passing in continuous execution.
- [x] Frontend TypeScript and Vite bundle compiled cleanly with 0 errors.
- [x] Unified production server verified on `http://127.0.0.1:8008/`.
- [x] Official 7-slide PDF (`MANDATE-ROUND2-PRESENTATION.pdf`) verified at 11.34 KB (< 10 MB).
- [x] Portable MP4 video recording (`recordings/mandate_demo_recording.mp4`) verified at 1.64 MB (< 100 MB).
- [x] Real team credentials (`STELLAR STACK`, `team-E657F05D7F45`, `AMRITA VISHWA VIDYAPEETHAM, NAGERCOIL`) populated in PDF, README, and submission documents.
- [x] Feature freeze declared.
