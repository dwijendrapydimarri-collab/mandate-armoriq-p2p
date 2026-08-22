# ANTIGRAVITY — Automated Browser Recording Directive

**Goal:** Execute a flawless, cinematic, end-to-end browser walkthrough of Mandate on `http://127.0.0.1:8008`, producing a high-resolution, zero-secret recording that covers every item in the Feature Coverage Matrix.

---

## 1. Recording Preconditions

1. **Target URL:** `http://127.0.0.1:8008` (Served by `python run.py --host 127.0.0.1 --port 8008`).
2. **Browser Viewport:** $1920 \times 1080$ (16:9 widescreen).
3. **Secret Hygiene:** Developer tools closed, network panels closed, 0 credentials visible.
4. **Recording Tool:** Browser Subagent with recording name `mandate_cinematic_walkthrough`.

---

## 2. Interactive Step Sequence

```
Step 1: Initial Landing & Threat Orientation (0:00 - 0:40)
Step 2: CFO Setup & Mission Sealing (0:40 - 1:20)
Step 3: Multi-Agent Graph & Capability Attenuation (1:20 - 1:55)
Step 4: Invoice Intake & Decision Stream Replay (1:55 - 2:55)
Step 5: Judge Challenge Mode & Live Security Probe (2:55 - 3:35)
Step 6: Live Submission Tracker & Verification Modal (3:35 - 4:00)
```

---

### Step 1: Landing Page & Top State Overview
1. Navigate to `http://127.0.0.1:8008/`.
2. Scroll smoothly through the header bar:
   - Verify App Title: `MANDATE`
   - Verify Problem Badge: `ArmorIQ Problem 1 & 2`
   - Verify Treasury Balance: `₹40,00,000.00`
3. Pause for 3 seconds over the Authority Envelope overview.

### Step 2: CFO Setup & Authority Sealing
1. Click the **"CFO Setup"** button in the header or Mission Bar.
2. The CFO Setup Modal opens:
   - View approved vendor list (`Apex Supplies Pvt Ltd`, `CloudTech Solutions`).
   - View registered payee bank accounts and open PO ceilings (`PO-1001: ₹24,000.00`, `PO-1004: ₹8,724.00`).
   - Observe maximum spend ceiling per invoice: `₹50,000.00`.
3. Click the emerald **"Seal Mission Authority"** button.
4. Modal smoothly dismisses. Observe the **Sealed Authority Envelope** glowing green with:
   - Mission ID: `mission_...`
   - Canonical Plan Hash: `b7a1e8...`
   - Intent Token Status: `ISSUED`
   - Merkle Root: `e5c3a9...`

### Step 3: Agent Graph & Capability Attenuation Inspection
1. Scroll to the **Multi-Agent Topology (React Flow)** section.
2. Click on the **`mandate-controller`** node:
   - Show scoped roles: `delegate_task`, `orchestrate`.
3. Click on the **`mandate-matcher`** node:
   - Show scoped capabilities: `fetch_invoices`, `verify_match`.
   - Observe Spend Ceiling: `₹0.00` (Read-only guarantee).
4. Click on the **`mandate-disburser`** node:
   - Show scoped capabilities: `initiate_payment`.
   - Observe Whitelist constraint: `[1122334455, 9988776655]`.

### Step 4: Run Automated Settlement & Inspect Defenses
1. Click **"Run Automated Settlement"** (or **"Simulate Batch"**).
2. Watch the Decision Stream animate:
   - `INV-2040` $\rightarrow$ **`ALLOW`** (Green badge, ₹24,000.00 disbursed).
   - `INV-2041` $\rightarrow$ **`BLOCK`** (Red badge, `PAYEE_NOT_IN_SEALED_SCOPE`).
   - `INV-2042` $\rightarrow$ **`BLOCK`** (Red badge, `LOCAL_CAPABILITY_ATTENUATION: Capability Not Possessed`).
   - `INV-2044` $\rightarrow$ **`ADJUSTED`** (Disbursed PO limit ₹8,724.00, blocked ₹78,516.00 overpay).
3. Click on the `INV-2041` blocked decision row:
   - The **Trust Boundary Map** opens.
   - Contrast Left Column (`Trusted Authority: ACC 1122334455`) vs Right Column (`Untrusted Invoice Claim: ACC 509900443322`).
4. Click **"View Authority Cliff Replay"**:
   - Trace execution pipeline halting at `gateway.py` with banner `AUTHORIZED BY: NOBODY`.
5. Point to Counterfactual Proof summary:
   - **Governed Balance:** `₹39,91,726.00`
   - **Ungoverned Baseline:** `₹38,57,560.00`
   - **Prevented Fraud Loss:** `₹1,34,166.00`

### Step 5: Judge Challenge Mode Live Proving Ground
1. Scroll down to the **Judge Challenge Mode** console.
2. Click **"Create Isolated Sandbox"**:
   - Enter Vendor: `Judge Security Systems`
   - Enter Account: `776655443322`
   - Enter PO Limit: `₹45,000.00`
3. Click **"Seal Custom Authority"**.
4. Click **"Custom Invoice Intake"**:
   - Ingest invoice with adversarial account `999988881111`.
5. Click **"Execute Security Probe"**:
   - Watch real-time dispatch through `gateway.py`.
   - Result: **`BLOCKED (PAYEE_NOT_IN_SEALED_SCOPE)`**.
6. Click **"Open Forensics Drawer"**:
   - Review typed audit verdict, rule matched, and zero-secret proof envelope.

### Step 6: Live Submission Tracker & Verification Modal
1. Click **"Submission Tracker"** in the top navigation bar.
2. Verify all verification indicators:
   - `33 Automated Invariant & Security Tests` $\rightarrow$ **Passing (Green)**
   - `Single-Command Production Server` $\rightarrow$ **Healthy (Green)**
   - `Zero-Secret Credential Scan` $\rightarrow$ **Verified (Green)**
   - `Truthful ArmorIQ Matrix` $\rightarrow$ **Displayed with exact boundary wording**
3. Close modal and conclude on the clean, governed Treasury dashboard.

---

## 3. Subagent Invocation Specification

When using `browser_subagent`:
- **RecordingName:** `mandate_cinematic_walkthrough`
- **TaskName:** `Record Mandate Cinematic Security Mission`
- **TaskSummary:** `Execute guided end-to-end browser walkthrough across CFO Setup, Sealing, Live Settlement Defenses, Trust Boundary Map, Judge Challenge Mode, and Submission Tracker.`
