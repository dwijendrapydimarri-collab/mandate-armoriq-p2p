# MANDATE — Master Implementation Plan & Product Contract

**Product:** MANDATE — Autonomous Procure-to-Pay with Cryptographically Bounded Spend Authority  
**Authoritative Contract:** `SPEC.md` (Sections 1.1–1.15)  
**Track:** ArmorIQ Problem 1 (*"Autonomous, until it shouldn't be"*) & Problem 2 (*Cryptographic Delegation Across Subagents*)  
**Physical File Location:** `C:\Users\DWIJENDRA\new hacakathon\hackathon 1\implementation_plan.md` (Repository Root)  
**Status:** Corrected & Reconciled — Awaiting Final Human Sign-off Before P1

---

## 1. Reconciled Source of Truth & Core Invariants

`SPEC.md` is the single, absolute source of truth. All historical reports (*AutoMart*, *ProcureProof*) are reference material only. All data schemas, fixtures, exact monetary amounts in integer paise, invariants, and acceptance gates are governed strictly by `SPEC.md`.

### Core Architectural & Security Invariants:
1. **Ordering Invariant (SPEC §1.2 & §5.3):** Spend authority is sealed strictly over *trusted records* (`get_vendor_master`, `list_open_purchase_orders`) before reading any *untrusted input* (`fetch_invoices` / invoice `raw_text`).
2. **Five-Method ArmorIQ Adapter Seam (SPEC §1.8):** `backend/armoriq/adapter.py` defines a Protocol with exactly five methods: `capture_plan`, `get_intent_token`, `delegate`, `invoke`, and `resume`. `resume()` re-authorizes previously HELD transactions with parameter tamper detection (`HELD_DECISION_PARAM_TAMPER_DETECTED`) before tool dispatch.
3. **Sole Gateway Invariant (SPEC §1.4):** `backend/gateway.py` is the single path from agents or approval actions to tools (`gateway.call` and `gateway.resume_held`). Agent modules are strictly forbidden from importing MCP client transports directly (enforced via AST unit test).
4. **MCP Transport Standard (SPEC §1.6 Option B):** Implements the **official MCP Python SDK** (`mcp.server.fastmcp.FastMCP`) protocol layer in-process for deterministic Windows local execution reliability, strictly exposing 5 typed MCP tools.
5. **Integer Currency Integrity:** All bank balances, purchase orders, stated invoice amounts, and disbursements are stored and calculated strictly in **integer paise** (`*_paise`).
6. **Two-Phase Judge Contract (SPEC §1.14):**
   - *Phase 1 (CFO Setup — Pre-Seal):* Trusted vendors, payee accounts, POs, per-invoice ceiling, and mission ceiling.
   - *Phase 2 (Mission Seal):* Captures plan & mints intent token. Post-seal trusted data is **strictly immutable**.
   - *Phase 3 (Invoice Intake — Post-Seal):* Ingests arbitrary invoice text labeled `UNTRUSTED`. Invoices cannot mutate master data.
   - *Phase 4 (Security Probe):* Direct typed test proposal through `gateway.py` labeled `TEST PROPOSAL — NOT AN LLM DECISION`.
7. **ArmorIQ Honesty & Crypto Boundary (DECISION-MEMO §5.1 & §5.2):**
   - `backend/armoriq/crypto.py` is strictly a local-development fallback.
   - In `ARMORIQ_MODE=real`, the real ArmorIQ SDK methods are authoritative; any duplicate local crypto is removed from the real path.
   - Local Ed25519 signatures, UUIDs, or hashes are **never** presented or labeled as ArmorIQ cryptographic proofs.
   - The UI permanently displays `ENFORCEMENT: LOCAL ADAPTER (ArmorIQ contract)` whenever running in local fallback mode.
8. **Winning Prototype Surfaces (SPEC §1.15):** Real Authority Envelope, Trust Boundary Map, Counterfactual Ledger Proof (`COUNTERFACTUAL — NOT EXECUTED`), and Authority Cliff Replay (`AUTHORIZED BY: NOBODY`).

---

## 2. Corrected P0–P10 Phase Table

| Phase | Objective | Exact Files to Create / Modify | Acceptance Tests | Dependencies | Key Risks & Mitigations |
|---|---|---|---|---|---|
| **P0** | Master Plan Reconciliation & SDK Spike | `implementation_plan.md` (repo root), `backend/armoriq/adapter.py` | Plan audit sign-off | `SPEC.md`, `DECISION-MEMO.md` | **Risk:** SDK private/unavailable. <br>**Mitigation:** Spike SDK; fallback to honest `ARMORIQ_MODE=local` adapter with persistent UI disclosure. |
| **P1** | Sandbox DB & Scenario Isolation | `backend/models.py`, `backend/seed.py`, `backend/domain.py`, `backend/main.py` | **T3** (byte-integrity), Scenario isolation | P0 | **Risk:** Float rounding in currency. <br>**Mitigation:** Strict integer paise columns in SQLModel. |
| **P2** | Official MCP SDK Tool Layer (5 Tools) | `backend/mcp_server/server.py`, `backend/mcp_server/client.py`, `scripts/verify_mcp.py` | 5 tools registered via FastMCP in-process protocol layer; trusted vs untrusted reads | P1 | **Risk:** Tool transport leaks to agents. <br>**Mitigation:** Thin client consumed only by `gateway.py`. |
| **P3** | Ungoverned Baseline (The Target) | `backend/llm.py` (disk cache), `backend/agents/baseline_agent.py` | Baseline compromise: Closing balance = ₹38,57,560 (`385756000` paise) | P2 | **Risk:** LLM non-determinism. <br>**Mitigation:** Disk cache in `.cache/llm/` + `DEMO_MODE=replay`. |
| **P4** | ArmorIQ Seam & Sole Tool Gateway | `backend/gateway.py`, `backend/armoriq/local.py`, `backend/armoriq/real.py`, `backend/armoriq/crypto.py` | **T2** (Spy counter = 0 on BLOCK), AST import check | P3 | **Risk:** Agents bypass gateway. <br>**Mitigation:** AST unit test verifies 0 MCP imports in `backend/agents/`. |
| **P5** | Plan Sealing, CFO Setup & Immutability | `backend/agents/controller.py`, `backend/main.py` (`/api/scenario/*`) | **T1** (Order invariant), **J1**, **J2**, **J3**, **W1** | P4 | **Risk:** Reversing setup order breaks security. <br>**Mitigation:** T1 asserts `fetch_ts > sealed_at`; J2 asserts 400 on post-seal mutate. |
| **P6** | Attack A, Governance Engine & Probe API | `backend/gateway.py`, `backend/domain.py`, `backend/main.py` (`/api/scenario/probe`) | **T6** (Headline balances ₹39,91,726 vs ₹38,57,560), **J5**, **W2**, **W3** | P5 | **Risk:** Model refuses malicious prompt. <br>**Mitigation:** Security Probe verifies gateway boundary independently of LLM. |
| **P7** | Multi-Agent Delegation & Attenuation | `backend/agents/matcher.py`, `backend/agents/disburser.py` | **T4** (Semantic scope), **T5** (Capability attenuation), **W4** | P6 | **Risk:** Delegation scope escalation. <br>**Mitigation:** Matcher has ceiling 0; Disburser has ₹50,000 ceiling. |
| **P8** | Human-in-the-Loop Gate (HOLD & Resume) | `backend/gateway.py` (`resume_held`), `backend/armoriq/local.py` (`resume`) | **T6** (₹1,45,000 HOLD → Re-auth → Dispatched via MCP) | P7 | **Risk:** Resuming mints fresh unconstrained token or bypasses auth. <br>**Mitigation:** `resume()` validates original token, role, and tamper checks parameters before tool entry. |
| **P9** | Mission Control & Judge UI | `frontend/src/*` (Vite, React 18, Tailwind, React Flow, Modals, Console) | **J4**, **J6**, **W5**, **W6**, Visual browser audit | P8 | **Risk:** Complex UI delays delivery. <br>**Mitigation:** 5 cohesive zones + modular modals for CFO Setup, Intake, and Probe. |
| **P10** | Replay Determinism & Verification Suite | `tests/test_invariants.py`, `tests/test_judge_mode.py`, `DEMO.md`, `README.md` | **J7**, **J8**, **J9**, **J10**, 10 consecutive cold-start replays, build verification | P9 | **Risk:** Submission rush. <br>**Mitigation:** Automated 10-run cold replay test + production-like launch verification and smoke tests. |

---

## 3. Status Correction & Verification Register

All tests are cataloged below with their true current status. T1–T6 are verified with 17 passing invariant tests; J1–J10 and W1–W6 remain specified and pending.

| Test ID | Category | Description / Acceptance Condition | Current Status |
|---|---|---|---|
| **T1** | Core Invariant | Plan-ordering: `fetch_invoices` timestamp strictly > `Mission.sealed_at`. Order inversion actively fails. | **VERIFIED (17/17 tests passing)** |
| **T2** | Core Invariant | Block-before-dispatch: Call-counter spy on `initiate_payment` equals exactly 0 on `BLOCK`. | **VERIFIED (17/17 tests passing)** |
| **T3** | Core Invariant | Zero-drift balance integrity: Account balance remains byte-identical after blocked payment. | **VERIFIED (17/17 tests passing)** |
| **T4** | Core Invariant | Semantic parameter scope: Same tool/agent/vendor $\rightarrow$ ₹8,724 yields `ALLOW`, ₹87,240 yields `BLOCK`. | **VERIFIED (17/17 tests passing)** |
| **T5** | Core Invariant | Capability attenuation: Matcher attempting `initiate_payment` yields `BLOCK` (`CAPABILITY_NOT_DELEGATED`). | **VERIFIED (17/17 tests passing)** |
| **T6** | Core Invariant | Canonical headline balances: Governed ₹39,91,726 (`399172600` p) vs Ungoverned ₹38,57,560 (`385756000` p). | **VERIFIED (17/17 tests passing)** |
| **J1** | Judge Gate | Browser CFO Setup creates vendor, PO, ceilings, seals mission, renders envelope without code edits. | **Backend Verified (`test_j1` passed; UI in Step 4)** |
| **J2** | Judge Gate | Post-seal trusted immutability: Modification requests to vendor/PO/ceilings rejected with `400`. | **VERIFIED (`test_j2` passed)** |
| **J3** | Judge Gate | Post-seal invoice intake accepts arbitrary text marked `UNTRUSTED`; cannot mutate master data. | **VERIFIED (`test_j3` passed; UI in Step 4)** |
| **J4** | Judge Gate | Legitimate custom invoice within judge's sealed scope reaches `ALLOW`/`HOLD` and executes correctly. | **VERIFIED (`test_j4` passed; UI in Step 4)** |
| **J5** | Judge Gate | Custom malicious probe (bad payee/excess amount) yields `BLOCK`; tool not entered, ledger unchanged. | **VERIFIED (`test_j5` passed; UI in Step 4)** |
| **J6** | Judge Gate | `Reset Demo`, `Load Canonical Demo`, and `New Judge Scenario` function cleanly from a cold browser. | **Specified (Pending Step 4 Execution)** |
| **J7** | Judge Gate | Automated test suite executes 1 custom judge scenario and 1 canonical replay against production build. | **Specified (Pending Step 3/5 Execution)** |

| **J8** | Judge Gate | Changing custom vendors, POs, amounts, and advisory text requires zero source-code modifications. | **Specified (Pending Step 4/5 Execution)** |
| **J9** | Judge Gate | Security audit: Zero secrets exposed in frontend bundle or browser network payloads. | **Specified (Pending Step 5 Execution)** |
| **J10**| Judge Gate | Clean checkout starts and resets cleanly using documented one-command launch and smoke test. | **Specified (Pending Step 5 Execution)** |
| **W1** | Winning Gate | Authority Envelope visually reflects actual sealed mission parameters and token state. | **Specified (Pending Step 4 Execution)** |
| **W2** | Winning Gate | Trust Boundary Map displays trusted facts vs untrusted claims and highlights the conflicting rule. | **Specified (Pending Step 4 Execution)** |
| **W3** | Winning Gate | Counterfactual Ledger Proof renders projected loss labeled `COUNTERFACTUAL — NOT EXECUTED`. | **Specified (Pending Step 4 Execution)** |
| **W4** | Winning Gate | Security Probe console routes all 4 challenge presets through the real `gateway.py` path. | **Specified (Pending Step 2/4 Execution)** |
| **W5** | Winning Gate | Custom judge scenarios generate identical proof surfaces without code changes. | **Specified (Pending Step 4 Execution)** |
| **W6** | Winning Gate | Blocked action visually stops at ArmorIQ boundary; Forensics drawer shows `AUTHORIZED BY: NOBODY`. | **Specified (Pending Step 4 Execution)** |


---

## 4. Production Launch & Deployment Specification (Phase P10)

Phase P10 includes the full execution and verification of production-grade startup commands:

1. **Backend Service Launch:**
   ```bash
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
   ```
2. **Backend Health Verification:**
   ```bash
   curl -s http://127.0.0.1:8000/api/health
   # Expected response: {"status": "ok", "app": "mandate"}
   ```
3. **Frontend Production Build:**
   ```bash
   cd frontend && npm run build
   ```
4. **Clean Checkout Smoke Test:**
   ```bash
   python -m pytest tests/test_invariants.py tests/test_judge_mode.py -v
   ```

---

## 5. Submission Artifact Status (Pre-Finale)

The submission deliverables are tracked separately from the finale build and are marked with their true status:

* **Seven-Slide Presentation PDF:** **Planned / not yet exported** (Official requirement: exactly 7 slides under 10 MB).
* **Demo Video Backup:** **Planned / not yet recorded** (Official requirement: under 100 MB).
* **GitHub Repository & Clean Documentation:** **Planned** (README with single-command launch instructions).
* **Honest ArmorIQ Disclosure:** Active in UI (`ENFORCEMENT: LOCAL ADAPTER (ArmorIQ contract)`).
