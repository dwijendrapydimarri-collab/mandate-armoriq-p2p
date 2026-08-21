# MANDATE — Autonomous Procure-to-Pay with Sealed Authority Envelope

**Team Name:** STELLAR STACK  
**Team ID:** team-E657F05D7F45  
**College / Institution:** AMRITA VISHWA VIDYAPEETHAM, NAGERCOIL  
**Track:** ArmorIQ — Problem 1 (*"Autonomous, until it shouldn't be"*) + Problem 2 (*Cryptographic Delegation Across Subagents*)  

> **"Authority is fixed at plan time over trusted data before reading any untrusted input."**


---

## 1. Quickstart & Launch Instructions

### Option A: Single-Command Production Server (Serves Backend & Built UI)
```bash
# 1. Start unified server on http://127.0.0.1:8008
python run.py --host 0.0.0.0 --port 8008

# Or on Windows:
start.bat

# Or on Linux/macOS:
./start.sh
```
*The FastAPI backend serves the complete, built Vite production frontend (`frontend/dist`) and API endpoints directly on port 8008.*

### Option B: Local Development Mode
```bash
# Terminal 1 — Backend (from repository root)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8008 --reload

# Terminal 2 — Frontend Dev Server (must run inside frontend/ directory)
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```
*Note: Vite dev server proxies `/api` requests to `http://127.0.0.1:8008`.*

### Building Frontend Production Bundle
```bash
# IMPORTANT: Run inside frontend/ directory
cd frontend
npm run build
```

---

## 2. Automated Test Suite (28 Tests Passing)

Execute the full regression, security invariant, and Judge Mode test suite:
```bash
# From repository root
python -m pytest tests/test_invariants.py tests/test_judge_mode.py -v
```

### Verified Acceptance Gates:
- **T1–T6 (Core Security Invariants):** Plan ordering, pre-dispatch block spy, integer paise balance integrity, semantic parameter scope, capability attenuation, governance A/B comparison.
- **P8 (Human-in-the-Loop Re-Auth):** Strict HOLD approval re-authorization via `enforcer.resume()` with parameter tamper protection.
- **P10 (Replay Determinism):** 10 consecutive cold-reset runs with byte-identical ledger closing balances.
- **J1–J5 & Hardening (Judge Mode):** Two-phase contract, trusted immutability, untrusted intake, legitimate execution, Security Probe dispatch, sandbox database isolation, malformed payload validation, and tool whitelisting.

---

## 3. Judge Mode Contract & Interactive UI Proving Ground

Mandate features a zero-CLI interactive proving ground for judges and evaluators:

1. **Phase 1 (CFO Setup — Trusted, Pre-Seal):**
   - Define approved vendor master, payee bank accounts, open purchase orders, per-invoice spend ceiling, and mission cumulative ceiling.
   - Click `Seal Authority Envelope` $\rightarrow$ hashes trusted facts, mints immutable Intent Token, and permanently locks trusted records.
2. **Phase 2 (Invoice Intake — Untrusted, Post-Seal):**
   - Ingest supplier invoices with arbitrary advisory text.
   - One-click adversarial attack presets (*Attack A: Bank Shift*, *Attack B: Port Demurrage*, *Attack C: 10x Amount Spike*).
   - Clear architectural guarantee: invoice text cannot edit trusted authority.
3. **Security Probe Console (`POST /api/scenario/probe`):**
   - Propose typed tool calls directly through `gateway.py` $\rightarrow$ `ArmorIQ`.
   - Realtime execution verdict with `CounterfactualProof` card displaying **`PREVENTED LOSS: ₹46,200.00`** and **`COUNTERFACTUAL — NOT EXECUTED`**.
4. **Visual Forensics & Verification Surfaces:**
   - **Authority Envelope:** Renders sealed cryptographic container with approved payees, ceilings, and delegation grants.
   - **Trust Boundary Map:** Side-by-side comparison of **TRUSTED AUTHORITY FACTS** vs **UNTRUSTED INVOICE CLAIMS** with highlighted conflicts (`requested_payee ≠ approved_payee`).
   - **Authority Cliff Replay:** Visualizes the 5-step dispatch pipeline; blocked attacks stop dead at the cliff with header **`AUTHORIZED BY: NOBODY`**.

---

## 4. Key Submission Artifacts

- **Presentation PDF:** [`MANDATE-ROUND2-PRESENTATION.pdf`](./MANDATE-ROUND2-PRESENTATION.pdf) (Official 7-slide PDF, 11.37 KB, compliant with < 10 MB limit).
- **Slide Script & Differentiation:** [`SEVEN-SLIDE-ANSWERS-AND-DIFFERENTIATION.md`](./SEVEN-SLIDE-ANSWERS-AND-DIFFERENTIATION.md).
- **Demo Walkthrough & Video:** [`walkthrough.md`](./walkthrough.md) (Browser session demo recording, 5.10 MB, compliant with < 100 MB limit).
- **Implementation Status:** [`IMPLEMENTATION-STATUS.md`](./IMPLEMENTATION-STATUS.md).

---

## 5. Security Model & Honest Disclosures

- **Zero Secret Leakage:** Zero API keys, private signing keys, or tokens exist in client-side code or browser bundles. All signing and token validations occur strictly server-side in Python.
- **ArmorIQ Seam Contract:** 5-method protocol in `backend/armoriq/adapter.py` (`capture_plan`, `get_intent_token`, `delegate`, `invoke`, `resume`).
- **Honest Adapter Disclosure:** When running locally without live cloud proxy credentials, the application explicitly discloses `ENFORCEMENT: LOCAL ADAPTER (ArmorIQ contract)` and labels proof objects as deterministic simulation receipts.

---

## 6. Feature Freeze Declaration

Following the successful completion and verification of Step 5 (Deployment, Final Replay, and Submission Hardening), the Mandate product is **FEATURE FROZEN**. All 28 automated tests pass, all UI surfaces are verified in browser, and all submission artifacts are in place.
