# Round 2 Submission Draft — Mandate

## Required form fields

| Field | Submission-ready content | Status |
|---|---|---|
| Project Name | **Mandate** | Ready |
| Idea Name | **Autonomous procure-to-pay with cryptographically bounded spend authority** | Ready |
| Theme | **ArmorIQ — Autonomous, until it shouldn’t be** | Ready; state that Problem 2 is also demonstrated |
| GitHub/deployed link | **TODO:** Add repository URL and preferably a deployed judge-ready link | Pending executable project |
| Project PPT | Seven-slide deck exported below 10 MB | Pending deck production |
| Project video | 2–3 minute walkthrough of mission, ArmorIQ boundary, and judge mode, below 100 MB | Pending executable project |

## Project description

Finance teams lose money when a supplier document arrives claiming its bank account has changed and a legitimate payment run sends funds to an attacker. Giving the same workflow to an AI agent increases the exposure because the malicious instruction is embedded in data the agent is required to read.

Mandate is an autonomous procure-to-pay back office. Three agents with separate identities read open purchase orders, three-way match incoming vendor invoices, write accounts-payable outcomes, and disburse sandbox payments—clearing routine invoices without constant human approval.

Mandate derives payment authority from trusted records only—the approved vendor master and open purchase orders—and seals that authority into an ArmorIQ intent token before any agent reads an invoice. Authority is fixed before the agent reads anything an attacker can write. Every payment crosses ArmorIQ before reaching an MCP payment tool, so an injected payee account, a delegated-capability violation, or an out-of-scope amount is stopped before sandbox funds move. Judges can also create their own trusted setup and untrusted invoice scenario to test the same boundary.

---

# Seven-slide PPT structure

## Cover

**Mandate**  
**Autonomous procure-to-pay with cryptographically bounded spend authority**  
**Theme:** ArmorIQ — Autonomous, until it shouldn’t be  
**Team:** [Team Name] · [Team ID]  
**College:** [College Name]

## Slide 2 — BEC turns invoice automation into a payment risk

**Problem + existing gap**

Finance teams process supplier invoices at scale. A believable remittance advisory can redirect a legitimate payment to an attacker, and autonomous agents magnify the risk because they are designed to act on the documents they read.

| Audience affected | Existing approach | Gap |
|---|---|---|
| Finance and AP teams | Manual review, static approval limits, broad automation credentials | Humans become a bottleneck, while agents may still receive excessive authority |
| Procurement managers | Approved-vendor and PO controls | Those controls are not automatically bound to every agent tool call |
| Security and compliance teams | Logs after the fact | Logs cannot stop an unauthorized payment before it executes |

**Core gap:** Existing workflows do not cryptographically bind an agent’s runtime action, payee, amount, and delegation chain to pre-approved authority.

## Slide 3 — Mandate seals authority before untrusted invoices arrive

**Proposed solution**

Mandate is an autonomous procure-to-pay workspace that clears valid invoices while preventing payments outside the CFO’s sealed authority.

```text
Trusted vendor master + open POs
        ↓
ArmorIQ plan + intent token sealed
        ↓
Untrusted invoice advisory enters
        ↓
Agents match, propose, and invoke payment
        ↓
ArmorIQ allows, holds, or blocks before funds move
```

**Why it is better:** The agent remains autonomous for routine work, but authority is fixed before it sees attacker-controlled content. The protection is runtime enforcement, not a prompt instruction or a post-event log.

## Slide 4 — One security boundary governs every tool call

**Architecture + tech stack**

```text
CFO Setup → Mission Seal → Invoice Intake → Agent workflow
                                      ↓
                        Gateway → ArmorIQ → MCP payment tool → SQLite ledger/AP register
                                      ↓
                       ALLOW / HOLD / BLOCK + provenance timeline
```

| Layer | Technology | Role |
|---|---|---|
| Frontend | React, TypeScript, Tailwind, React Flow | Mission Control, CFO Setup, Invoice Intake, Security Probe, audit view |
| Backend | Python, FastAPI, SQLModel | Mission state, orchestration, APIs, SSE events |
| Authorization | ArmorIQ SDK through a typed adapter | Capture plan, mint intent token, delegate, verify invocation |
| Tool layer | Official MCP Python SDK | Five typed tools, including real sandbox payment mutation |
| Data | SQLite | Isolated judge scenarios, trusted records, invoices, ledger, AP register |
| Verification | pytest + browser tests | T1–T6 plus judge-mode gates J1–J7 |

## Slide 5 — Autonomous work, scoped delegation, and judge-created tests

**Key features**

| Feature | Innovation / value |
|---|---|
| **Trusted-before-untrusted plan sealing** | Prevents invoice text from widening payment authority |
| **Three independent agents** | Controller delegates read-only matching and narrowly scoped disbursement authority |
| **Pre-tool ArmorIQ enforcement** | `ALLOW`, `HOLD`, and `BLOCK` occur before the MCP payment tool reaches the ledger |
| **Semantic scope verification** | Same tool and agent: ₹8,724 can be allowed while ₹87,240 is blocked |
| **Judge Mode** | Judges create a new sandbox mission, enter their own invoice/advisory, and test the identical boundary |

Judge Mode keeps trusted CFO setup separate from post-seal untrusted invoice input. A Security Probe allows a judge to test an agent, tool, and parameter combination through the same gateway without relying on an LLM to obey a specific attack note.

## Slide 6 — Safer automation with an auditable, deployable path

**Impact + feasibility**

| Dimension | Mandate’s outcome |
|---|---|
| Beneficiaries | Finance, procurement, compliance, and security teams operating invoice-payment workflows |
| Real-world impact | Reduces the opportunity for bank-detail fraud, unauthorized payees, delegated-authority abuse, and out-of-scope payment amounts |
| Scalability | Tenant/scenario isolation and typed MCP tools can extend from a local demo to controlled enterprise integrations |
| Feasibility | Single FastAPI backend, SQLite sandbox, one MCP server, three agents, and five tools minimize infrastructure risk |
| Cost / deployment | Local one-command launch for judging; optional HTTPS deployment after real SDK credentials are verified |

**Proof:** The canonical governed run ends at ₹39,91,726; an identical sandbox run with governance disabled ends at ₹38,57,560. The visible difference is ₹1,34,166 in prevented loss.

## Slide 7 — Authority ends where ArmorIQ says it ends

**Demo + conclusion**

**Live or recorded demo sequence:**

1. A CFO creates an approved vendor, PO, and payment ceiling, then seals the mission.
2. An invoice contains a believable bank-account-change advisory.
3. The agent proposes a payment to the unapproved payee.
4. ArmorIQ blocks the call before the MCP payment tool executes; the ledger remains unchanged.
5. The forensics panel answers: **“Who authorized this?” → Nobody.**
6. A judge creates another scenario or uses the Security Probe to test a different payee, amount, or delegated agent.

> **Why Mandate should be selected:** It turns agent authorization from an abstract security claim into a usable, testable enterprise workflow where judges can watch autonomy work—and then prove that authority cannot silently expand.

**Links:**  
GitHub: `[ADD FINAL REPOSITORY URL]`  
Deployed Judge Mode: `[ADD FINAL HTTPS URL]`  
Demo video: `[ADD FINAL VIDEO LINK OR UPLOAD]`

---

# Video requirements and storyboard

The uploaded video must stay below 100 MB. Aim for **2–3 minutes**, 720p or 1080p with compressed MP4/H.264, clear voiceover, and a visible local-adapter disclosure if the real ArmorIQ integration is not yet verified.

| Time | Scene | What it proves |
|---:|---|---|
| 0–15s | State the BEC problem and Mandate’s one-line pitch | Understandable business purpose |
| 15–35s | Show CFO Setup: approved vendor, payee, PO, ceilings | Trusted authority exists before the attack |
| 35–45s | Click Mission Seal and display authority envelope | Intent and scope are fixed |
| 45–65s | Enter or open invoice with remittance-change advisory | Untrusted input arrives after sealing |
| 65–90s | Show agent proposal and ArmorIQ `BLOCK` before tool dispatch | Problem 1 enforcement |
| 90–110s | Show unchanged ledger and provenance chain | Side-effect proof and “Who authorized this?” |
| 110–135s | Show Matcher blocked from payment and ₹87,240 blocked vs ₹8,724 allowed | Delegation and parameter enforcement |
| 135–165s | Create a new Judge Mode scenario or run a Security Probe | Generalized judge-usable product, not a scripted demo |
| 165–180s | Closing message, repository/deployment link, team name | Final selection case |

## Submission verification checklist

| Item | Must be true before submission |
|---|---|
| PPT | Exactly seven slides using the required structure; export is below 10 MB |
| Project link | Repository is public or judges have access; README includes setup and reset instructions |
| Deployed link | Prefer an HTTPS Judge Mode link; if unavailable, provide a reliable one-command local launch and demo video |
| Video | Below 100 MB; visibly demonstrates how ArmorIQ is used, not only the UI |
| ArmorIQ disclosure | Real mode is demonstrated if available; local adapter is plainly labeled if real SDK access remains unavailable |
| Judge usability | User can create a new safe scenario and test inputs without code, terminal, or database access |
| Test evidence | T1–T6 and J1–J7 are passing and recorded in the repository |
