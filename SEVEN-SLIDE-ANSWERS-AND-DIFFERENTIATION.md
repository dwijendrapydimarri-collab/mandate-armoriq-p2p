# Mandate — Submission-Ready Slide Answers and Competitive Differentiation

## The honest competitive verdict

**Mandate is not revolutionary because accounts-payable automation exists.** It becomes highly distinctive for the ArmorIQ track when it is presented as an **Authority Envelope for autonomous money movement**: a CFO creates trusted payment authority, ArmorIQ seals it before the agent reads untrusted invoices, and judges can live-test whether any agent can escape that authority.

Do not try to become “revolutionary” by adding blockchain, a chatbot, a vector database, more agents, or a fake fraud-detection score. Those additions would make the project look generic and reduce implementation reliability.

The differentiation to build is:

> **Mandate turns the CFO’s approved vendor and PO data into a live, sealed Authority Envelope—then lets a judge attack it in real time and prove that the payment tool cannot be reached outside that envelope.**

This changes the story from “an invoice bot with guardrails” into a **live authorization proving ground for autonomous finance**.

| Positioning level | Assessment | What judges will think |
|---|---|---|
| Invoice-processing agent only | Common | “Another finance automation demo.” |
| Agent plus alert for suspicious invoice | Better, but common | “A fraud detector.” |
| Agent plus generic approvals | Useful, but expected | “Humans still do the security work.” |
| **Mandate: sealed Authority Envelope + pre-tool ArmorIQ verification + Judge Challenge Mode** | **Distinctive for this track** | “This agent can work independently, but I can prove exactly where its authority ends.” |

### Competitive target

Assuming approximately 5,000 participating teams, no idea is guaranteed to win. **Mandate has finalist-level potential only if all three conditions are true:**

1. The ArmorIQ boundary is real or plainly and honestly labeled as a local-adapter development mode.
2. The live demo shows one useful payment workflow complete automatically, one realistic bank-detail fraud blocked before the ledger changes, and one delegated-agent violation blocked.
3. A judge can create or probe a fresh sandbox scenario without editing code.

With only a scripted demo and local mock, rate the competitive strength **7/10**. With a verified ArmorIQ path, a visible before/after ledger, and Judge Challenge Mode, rate it **9/10 for the ArmorIQ track**. The gap is execution proof, not more features.

---

# Exact seven-slide answers

## Cover

**Project title:** Mandate  
**Theme:** ArmorIQ — Autonomous, until it shouldn’t be  
**One-line pitch:** Autonomous procure-to-pay with a sealed Authority Envelope.  
**Team:** `STELLAR STACK` · `team-E657F05D7F45`  
**College:** `AMRITA VISHWA VIDYAPEETHAM, NAGERCOIL`


---

## Slide 2 — AI payment automation has a trust gap

### What is the problem?

Supplier invoices often include routine-looking remittance instructions. A fraudulent bank-account-change advisory can cause an autonomous accounts-payable agent to send a legitimate payment to an attacker. The danger is not merely that an agent reads untrusted text; it is that the text can influence a real payment tool.

### Who is affected?

| Affected group | Impact |
|---|---|
| Finance and AP teams | Must choose between slow manual checking and risky automation |
| CFOs and procurement managers | Carry financial and supplier-payment accountability |
| Security and compliance teams | Need evidence of who authorized an automated payment |
| Legitimate suppliers | Experience payment delays and disputes when bank details are uncertain |

### What current solutions exist?

| Current solution | What it does |
|---|---|
| ERP approval workflows | Route invoices to human approvers |
| Approved-vendor masters and PO matching | Store trusted supplier and purchase-order data |
| IAM / RBAC | Limit who or what can use a payment capability |
| LLM guardrails and prompt filters | Try to prevent models from following malicious content |
| Audit logs | Record activity after it occurs |

### What are the gaps and limitations?

- Manual approvals reduce the value of autonomy by forcing humans into routine, low-risk work.
- Broad IAM permissions can say that an agent may “make payments,” but often do not bind a specific **payee, amount, mission, and delegation chain** to each runtime action.
- Prompt filters and guardrails can be bypassed by plausible business language; a real remittance update may look almost identical to a fraudulent one.
- Conventional audit logs explain a loss after it happens; they do not stop the payment tool before funds move.

### Slide-ready core line

> **Today’s systems either slow agents down with blanket approvals or give them authority that is too broad. Neither proves whether this exact payment was authorized.**

---

## Slide 3 — Mandate seals authority before invoices arrive

### Your idea in simple terms

Mandate is an autonomous procure-to-pay workspace. It clears valid supplier invoices, but it creates a sealed **Authority Envelope** from trusted vendor and purchase-order data before the AI agents see untrusted invoice text.

### How does it solve the problem?

```text
CFO trusted setup: approved vendors + payee accounts + open POs + limits
                              ↓
            ArmorIQ captures the plan and seals the Authority Envelope
                              ↓
                  Agent reads untrusted invoice/advisory text
                              ↓
               Every payment request is verified before the tool runs
                              ↓
                 ALLOW / HOLD / BLOCK + auditable ledger result
```

The agents autonomously match invoices, prepare AP outcomes, and pay valid invoices. When an invoice tries to redirect payment to an unapproved account, exceed the permitted amount, or make the wrong specialist agent pay, ArmorIQ stops the action before the MCP payment tool reaches the sandbox ledger.

### What makes it better than existing solutions?

| Existing approach | Mandate’s difference |
|---|---|
| Manual approval queue | Automates routine, in-scope invoices without asking a human every time |
| Static role-based permission | Checks the specific action, amount, payee, plan, and delegation at runtime |
| Prompt-injection filter | Does not rely on recognizing malicious wording; it enforces authority even when the text seems legitimate |
| Post-event audit log | Stops the side effect first, then records the full provenance chain |

### Slide-ready core line

> **Mandate does not ask whether an invoice sounds safe. It asks whether this exact payment is inside authority sealed before the invoice was read.**

---

## Slide 4 — One Authority Envelope governs every tool call

### System flow: input → process → output

```text
1. CFO Setup (trusted): vendor, payee, PO, per-invoice ceiling, mission ceiling
2. Mission Seal: capture_plan() + get_intent_token()
3. Invoice Intake (untrusted): invoice amount + advisory text
4. Agent workflow: Controller → Matcher → Disburser
5. Gateway: every side effect → ArmorIQ invoke()
6. MCP tool: payment executes only on ALLOW
7. Output: AP record, sandbox ledger, decision timeline, provenance
```

### Main components

| Component | Purpose |
|---|---|
| **Frontend: Mission Control** | CFO Setup, Mission Seal, Invoice Intake, Judge Challenge Mode, live decisions, forensics |
| **Backend: FastAPI** | Mission orchestration, typed APIs, state machine, approval/resume flow |
| **AI agent layer** | Controller plans work; Matcher reads invoices; Disburser proposes narrowly scoped payments |
| **ArmorIQ adapter** | Captures plan, receives intent token, delegates authority, verifies invocation before side effect |
| **MCP server** | Exposes exactly five typed procurement tools |
| **SQLite sandbox** | Stores trusted setup, untrusted invoices, AP register, ledger, decisions, and scenario isolation |
| **Verification suite** | Tests T1–T6 and judge-usage tests J1–J10 |

### Tech stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Tailwind, React Flow |
| Backend | Python, FastAPI, SQLModel, Uvicorn |
| AI | One configured LLM provider with replay cache |
| Authorization | ArmorIQ SDK through a typed adapter; local adapter only when visibly disclosed |
| Tools | Official MCP Python SDK, stdio transport |
| Database | SQLite for deterministic, isolated sandbox state |
| Testing | pytest and browser automation |

### Slide-ready core line

> **The LLM proposes; the application orchestrates; ArmorIQ authorizes; the MCP tool performs the side effect.**

---

## Slide 5 — Autonomy with proof, not blind trust

### Key feature 1 — Authority Envelope

The CFO configures approved payees, purchase orders, and limits. ArmorIQ seals the mission before untrusted invoice text exists in the agent’s context.

### Key feature 2 — Independent, delegated agents

The Controller delegates reading and matching to the Matcher, and limited payment authority to the Disburser. The Matcher cannot pay, even if an invoice tells it to.

### Key feature 3 — Pre-tool semantic enforcement

The same Disburser and the same payment tool can be allowed for ₹8,724 and blocked for ₹87,240. This proves parameter-level authority, not a simple tool allowlist.

### Key feature 4 — Judge Challenge Mode

A judge can create a fresh safe scenario, seal trusted authority, enter an arbitrary invoice advisory, and observe the real configured boundary. The Security Probe lets the judge test an agent, tool, and parameter combination through the same gateway path.

### Key feature 5 — One-glance forensics

Mission Control answers:

```text
Who authorized this?
CFO → Controller → delegated specialist → tool → parameters → ArmorIQ verdict → ledger result
```

For a blocked action, it shows **AUTHORIZED BY: NOBODY** and the exact missing authority.

### Slide-ready core line

> **Mandate makes autonomous finance testable: judges can challenge the agent, and the system proves whether the tool was ever authorized to run.**

---

## Slide 6 — Safer automation, built for real adoption

### Who benefits?

| User | Benefit |
|---|---|
| Accounts-payable teams | Routine invoices are processed faster without abandoning control |
| CFOs and procurement leaders | Payment authority becomes explicit, scoped, and reviewable |
| Security and compliance teams | Every decision has a traceable authority chain and state proof |
| Enterprises adopting agents | A reusable pattern for governing high-consequence tools |

### Real-world impact

Mandate reduces the opportunity for supplier-payee fraud, delegated-agent overreach, and over-limit disbursement. It also reduces approval fatigue by reserving human review for meaningful exceptions instead of routine matches.

### Scalability

The first demo uses a local sandbox ledger and five tools for reliability. The same Authority Envelope model can later govern other enterprise actions, including payroll exceptions, vendor onboarding, expense payouts, procurement orders, cloud changes, or customer-data exports. The first product must remain focused on invoice payment.

### Basic feasibility: cost and deployment

| Dimension | Feasible choice |
|---|---|
| Initial deployment | One FastAPI backend, one React frontend, one MCP server, SQLite sandbox |
| Infrastructure cost | Low for demo and evaluation because no real payment provider or distributed system is required |
| Judge access | HTTPS deployment preferred; one-command local launch documented as fallback |
| Safety | Synthetic money only; no actual bank accounts or live payment rails |
| Reliability | Deterministic seed scenarios, replay mode, reset control, browser acceptance tests |

### Slide-ready proof

```text
Governance ON:  ₹39,91,726 closing balance
Governance OFF: ₹38,57,560 closing balance
Prevented sandbox loss: ₹1,34,166
```

Label governance-off mode as a **sandbox comparison**, never a production feature.

---

## Slide 7 — Let the judge try to break it

### Demo / prototype sequence

1. The judge creates an approved vendor, payee, purchase order, and ceiling in **CFO Setup**.
2. The judge clicks **Seal Mission**; the Authority Envelope becomes immutable.
3. The judge enters an invoice advisory that proposes a different bank account or oversized amount.
4. The Controller, Matcher, and Disburser work autonomously; the payment request reaches ArmorIQ first.
5. ArmorIQ returns `BLOCK`; the payment tool is not entered and the sandbox ledger does not change.
6. The judge opens Forensics to see why: **AUTHORIZED BY: NOBODY**.
7. The judge tests another amount, payee, or delegated agent using Judge Challenge Mode.

### Links

- **GitHub:** `[ADD FINAL REPOSITORY URL]`
- **Deployed Judge Mode:** `[ADD FINAL HTTPS URL]`
- **Demo video:** `[ADD FINAL VIDEO LINK OR UPLOAD]`

### One-line strong conclusion

> **Mandate makes AI agents useful in finance without making them trusted by default: authority is sealed first, verified at every tool call, and provable under live challenge.**

### Why this should be selected

> **Most teams will demonstrate an agent that works. Mandate demonstrates an agent that can be challenged by a judge and still prove, before money moves, that it cannot exceed the authority it was given.**

---

# What makes Mandate feel revolutionary without overbuilding

## Do build: the Authority Envelope and Judge Challenge Mode

The core product differentiation is not a new model. It is a new **operating primitive** for high-consequence agents:

```text
Trusted business facts → sealed Authority Envelope → untrusted world → verified action
```

Give this primitive a clear visual identity. The Mission Seal should show a literal envelope or vault containing:

- Approved payees
- Open PO references
- Per-invoice ceiling
- Total mission ceiling
- Intent-token state
- Real ArmorIQ proof fields when available

Then make the judge experience the breakthrough: they create trusted facts, seal them, attempt to make the agent act outside them, and watch the side effect stop before the ledger changes.

## Do build: Counterfactual Ledger Proof

Retain the governed/un governed canonical comparison, but call the display **Counterfactual Ledger Proof**. It explains the outcome in one screen:

| Same invoice run | Result |
|---|---|
| Without governance in a sandbox | Fraudulent payment changes ledger |
| With ArmorIQ governance | Same request is blocked before tool dispatch |

This should be a canonical-demo feature, not normal judge-mode bypass.

## Do not build

| Temptation | Why it hurts the project |
|---|---|
| Blockchain or custom cryptographic ledger | Duplicates ArmorIQ, adds complexity, and weakens the sponsor story |
| Generic fraud-score model | Shifts the story to detection and raises data-quality questions |
| More than three agents | Adds noise and delegation bugs without increasing judge comprehension |
| Real banking or payment integrations | Adds safety, credentials, and reliability risk with no hackathon advantage |
| A chat-only interface | Makes it look like every other LLM wrapper and hides the security boundary |
| “AI detects prompt injection” claim | Less defensible than mission-bound authorization that works even when text looks legitimate |

## Final recommendation

**Do not pivot the product. Sharpen it.** The winning version is:

> **Mandate: the first judge-testable Authority Envelope for autonomous payments.**

Avoid claiming “first” in the official submission unless independently verified. In the deck, say instead:

> **A live, judge-testable Authority Envelope for autonomous payments.**

That is ambitious, accurate, technically aligned with ArmorIQ, and still buildable within the hackathon constraints.
