# Antigravity Prompt — Review and Correct the Amended Implementation Plan

Copy and paste the following prompt into Antigravity. This is a **review-only phase**. Do not begin P1 and do not implement the winning-prototype features yet.

```text
You are reviewing the amended MANDATE implementation plan before implementation begins.

Read these files fully before responding:
1. SPEC.md — authoritative product contract
2. ANTIGRAVITY-BUILD-PROMPT.md — original staged P0–P10 build plan
3. DECISION-MEMO.md — strategic rationale and known risks
4. ANTIGRAVITY-JUDGE-MODE-PATCH.md — Judge Mode requirements
5. ANTIGRAVITY-WINNING-PROTOTYPE-UPGRADE.md — later winning-prototype direction

The attached/amended plan claims to incorporate SPEC.md sections 1.14 and 1.15. Your job now is to audit, reconcile, and correct the plan. This is not permission to write application code.

## Important doubts you must resolve

### Doubt 1 — False test status
The amended plan marks T1–T6 as “Verified,” but the project folder does not yet contain the executable backend, MCP server, frontend, or test output. Treating these tests as verified is inaccurate.

Correct this:
- Change every unexecuted test status from “Verified” to “Specified,” “Pending implementation,” or “Not yet run.”
- A test may be marked “Verified” only after it has actually been executed and the verbatim output is recorded.
- Do not claim a real ArmorIQ invocation has been verified unless a real SDK call and response are available.

### Doubt 2 — Hidden implementation-plan file
The previous plan was created in Antigravity’s hidden workspace location. The final plan must be saved inside the repository/project folder as:

implementation_plan.md

The repository copy is the version the human team reviews and commits.

### Doubt 3 — Plan scope versus product scope
The product must be Mandate, not AutoMart, ProcureProof, or a generic authorization platform. Confirm that every phase uses:
- Controller, Matcher, and Disburser agents
- the five Mandate MCP tools
- SQLite and integer paise
- the trusted-data → sealed plan → untrusted invoice order
- gateway.py as the sole agent-to-tool path

### Doubt 4 — Judge usability
The product must not be only a fixed scripted scenario. A judge must be able to use the browser to:
- create a new isolated sandbox scenario
- create approved vendors, payee accounts, purchase orders, and ceilings before sealing
- seal the mission
- enter arbitrary invoice amount and free-text advisory after sealing
- run the autonomous workflow
- test custom proposals through Security Probe
- inspect the decision and unchanged ledger
- reset or load the canonical demo

Confirm that these requirements are mapped to implementation phases and J1–J7/J8–J10 tests.

### Doubt 5 — Trust boundary
Confirm that the plan does not allow invoice text to mutate the trusted vendor master, payee account, purchase order, or ceilings. After Mission Seal, trusted authority must be immutable for that mission. Any trusted-data change requires a new mission and a new intent token.

### Doubt 6 — ArmorIQ honesty
Confirm the following:
- `ARMORIQ_MODE=real` uses the actual ArmorIQ SDK only after credentials and signatures are verified.
- `ARMORIQ_MODE=local` is clearly labeled as a local contract-faithful adapter.
- A locally generated hash, UUID, or Ed25519 receipt is never presented as an ArmorIQ cryptographic proof.
- If ArmorIQ delegate() supplies grants or signatures, any duplicate local grant/crypto implementation is removed from the real path.
- The plan identifies the remote-proxy latency and connectivity risk, if applicable.

### Doubt 7 — Submission timing
The required submission contains seven slides, a repository/deployed link, a PPT under 10 MB, and a video under 100 MB. Confirm that the plan separates:
- Round 2 submission preparation and PDF creation
- later 8-hour finale implementation

Do not defer the PDF until after implementation.

## Required corrections to the implementation plan

Amend the phase plan so that it includes these gates:

### Planning gates
- P0: read SPEC.md, reconcile all plan documents, and save repository-local implementation_plan.md.
- P0: list exact files per phase, acceptance tests per phase, risks, and rollback points.
- P0: mark all test statuses honestly.

### Core gates
- T1: no untrusted invoice read before plan sealing.
- T2: BLOCK never enters the tool function body.
- T3: blocked payment leaves the protected balance byte-identical.
- T4: same tool and agent; ₹8,724 allowed and ₹87,240 blocked.
- T5: Matcher payment attempt blocked with CAPABILITY_NOT_DELEGATED.
- T6: governed and ungoverned canonical runs reproduce exact expected balances.

### Judge gates
- J1: browser-created vendor, PO, ceilings, and sealed mission.
- J2: post-seal trusted immutability.
- J3: arbitrary invoice text accepted as UNTRUSTED after seal.
- J4: legitimate custom invoice completes correctly.
- J5: custom bad payee/amount/agent proposal blocks before the tool and leaves ledger unchanged.
- J6: Reset Demo, Load Canonical Demo, and New Judge Scenario work from a cold browser.
- J7: custom scenario and canonical replay pass against a production-like build.
- J8: changing custom vendor, PO, amount, and advisory text does not require source-code changes.
- J9: no secret appears in frontend bundle or browser network requests.
- J10: a clean checkout starts using documented commands.

### Winning-prototype gates
Include these as planned—not verified—until actually demonstrated:
- W1: Authority Envelope reflects the actual sealed mission data.
- W2: Trust Boundary Map identifies trusted facts, untrusted claims, and the conflicting rule.
- W3: Counterfactual Ledger Proof shows projected loss while real state remains unchanged.
- W4: Security Probe uses the exact gateway.py → ArmorIQ adapter → MCP path.
- W5: custom judge scenarios generate the same proof surfaces without code changes.
- W6: blocked action visually stops at the ArmorIQ boundary and forensics shows AUTHORIZED BY: NOBODY.

## Required response format

Return only a plan-review report, not application code. The report must contain:

1. **Reconciled source-of-truth statement.** State that SPEC.md is authoritative and where implementation_plan.md is saved.
2. **Corrected P0–P10 phase table.** For each phase list objective, exact files, acceptance tests, dependencies, and risks.
3. **Status correction table.** Show which tests are specified, pending, or actually verified. Do not claim unexecuted tests are verified.
4. **Architecture consistency check.** Confirm agents, five tools, SQLite, gateway, ArmorIQ adapter, and the security ordering.
5. **Judge Mode check.** Confirm custom scenario, arbitrary invoice text, Security Probe, reset controls, and browser tests.
6. **Submission check.** Confirm seven-slide PPT, repository/deployed link, video under 100 MB, and PDF under 10 MB are planned separately from the finale build.
7. **Unresolved risks.** Include SDK access, proxy latency, approval/resume semantics, deployment, and any remaining ambiguity.
8. **Exact next step.** State what P1 will implement and its acceptance gate.

Then STOP. Do not begin P1, do not create backend files, do not create frontend files, and do not add winning-prototype features yet. Wait for human approval of the corrected plan.
```

## Human approval rule

Approve the next phase only if the response contains the corrected repository-local `implementation_plan.md` plan, honest test statuses, all judge gates, the seven-slide submission path, and an explicit stop before P1. After this review is approved, proceed to the separate winning-prototype directive.
