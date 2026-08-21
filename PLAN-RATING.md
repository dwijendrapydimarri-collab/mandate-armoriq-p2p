# ArmorIQ Hackathon Plan Rating

**Reviewed:** 20 August 2026  
**Folder reviewed:** `hackathon 1`  
**Recommendation:** Proceed with **Mandate**, using the staged build prompt as the implementation source of truth.

## Executive rating

| Dimension | Rating | Assessment |
|---|---:|---|
| Product choice | **9.5/10** | Mandate is a real procure-to-pay workflow, not a generic security framework. The BEC attack makes ArmorIQ naturally necessary. |
| ArmorIQ Problem 1 fit | **9.5/10** | The plan demonstrates autonomous invoice processing, pre-tool enforcement, HOLD/BLOCK behavior, human approval, and resume. |
| ArmorIQ Problem 2 fit | **9.5/10** | The three-agent hierarchy, scoped delegation, separate identities, and provenance chain directly answer “Who authorized this?” |
| Attack realism | **9.8/10** | The supplier bank-account-change attack is credible to a finance professional and stronger than a contrived “VIP refund” attack. |
| Security architecture | **9.5/10** | The trusted-data → sealed plan → untrusted invoice ordering is the most important architectural insight in the folder. |
| Demo clarity | **9.5/10** | A bank balance that does not move is more immediately convincing than a purchase order that remains in draft. |
| Deterministic reliability | **9.7/10** | SQLite snapshots, integer paise, sequential agents, replay mode, exact fixtures, and ten-run verification are excellent choices. |
| Vibe-coding feasibility | **8.7/10** | The staged gates are strong, but real ArmorIQ integration, proxy latency, and SDK uncertainty remain material risks. |
| Submission readiness | **7.8/10** | The discovery and build plans are strong, but the folder does not yet show a finalized PDF submission, executable repo, or verified real-SDK run. |
| **Overall plan quality** | **9.2/10** | Strategically excellent and technically disciplined; not yet execution-ready until the SDK spike and submission package are completed. |

## What I found in the folder

The folder contains four primary planning artifacts plus an adjudication memo. The older `ARMORIQ_DISCOVERY_REPORT.md` recommends **AutoMart**, but its attack scenarios are weaker and its architecture is more infrastructure-heavy. The shorter `ARMORIQ-PRODUCT-DISCOVERY.md` recommends **Mandate** but is incomplete. The `armoriq_hackathon_discovery_report.md` recommends **ProcureProof** and contains the strongest external ArmorIQ documentation research. The `ANTIGRAVITY-BUILD-PROMPT.md` then evolves that direction into the more convincing **Mandate** procure-to-pay implementation. `DECISION-MEMO.md` correctly merges ProcureProof’s trusted authority source with Mandate’s visible bank-ledger side effect.

The folder is therefore strategically coherent, but it contains multiple winners and multiple reports. That is manageable for internal work, but dangerous if an agent or teammate reads the wrong file as the source of truth.

## Strongest parts of the plan

### 1. The product is a real job, not a security demo

Mandate clears vendor invoices, performs three-way matching, writes AP records, and moves money in a controlled sandbox. ArmorIQ is necessary because the workflow contains a consequential side effect. This directly satisfies the brief’s requirement that security should be naturally necessary because of the task.

### 2. The attack is credible

The supplier remittance advisory is the plan’s best decision. It is plausible business data, not an obviously malicious instruction. The attacker-controlled bank account is absent from the trusted vendor master, so the system can show that the authority envelope was fixed before the invoice was read.

### 3. The plan-ordering invariant is excellent

The sequence below is the core of the entire project:

```text
Read trusted vendor master and open POs
→ capture_plan() + get_intent_token()
→ read untrusted invoices
→ invoke() every payment
```

This prevents the injected payee account from becoming part of the authorization plan. The acceptance test `T1` turns this insight into a regression-proof engineering invariant.

### 4. The side effect is undeniable

The controlled bank balance provides a simple before/after proof. In governed mode, the balance remains at the expected protected value. In the sandbox comparison with governance disabled, the fraudulent payments reduce the balance. This is much easier for a judge to understand than an abstract “blocked” message.

### 5. The implementation discipline is unusually strong

The build prompt has a clear gateway boundary, exact fixtures, integer paise arithmetic, sequential agents, a local database, acceptance gates, replay mode, reset behavior, and a cut list. The rule that no agent may import the MCP client directly is especially important.

## Highest-priority risks

### Risk 1 — Real ArmorIQ access is still unverified

This is the largest risk. The plan currently designs against documented method names while the team has zero SDK access. Before building the UI, verify the actual `capture_plan`, `get_intent_token`, `invoke`, and `delegate` signatures; the decision enum; HOLD and approval-resume behavior; delegation grant shape; and available proof fields.

**Required action:** Make the first engineering task a small SDK spike. Do not spend the first hours polishing React while the authorization call remains hypothetical.

### Risk 2 — The enforcement call may depend on a remote proxy

The official documentation describes invocation verification at a proxy. Conference Wi-Fi, latency, authentication expiry, or service unavailability could affect the live demo.

**Required action:** Measure real invocation latency immediately, ask ArmorIQ whether an offline or self-hosted mode exists, bring a mobile hotspot, pre-warm the session, and record a complete backup run. Keep the local adapter only as a clearly labeled fallback.

### Risk 3 — The folder has conflicting source documents

The older AutoMart report is polished but should not remain equally authoritative. The implementation prompt says Mandate, while the longer discovery report says ProcureProof. A coding agent could follow the wrong product name, domain, or schema.

**Required action:** Create one `SPEC.md` containing the Mandate contract. Add a short `README.md` stating that `ANTIGRAVITY-BUILD-PROMPT.md`, or its extracted `SPEC.md`, is the source of truth. Mark the AutoMart report as superseded or move it to an archive folder.

### Risk 4 — No executable implementation is visible yet

The folder currently contains planning documents, not the backend, MCP server, tests, frontend, or a runnable repository. The plan is excellent, but the actual project has not crossed the first acceptance gate.

**Required action:** Start P1 immediately: models, deterministic seed database, real `initiate_payment`, reset endpoint, and T3. Do not begin the frontend.

### Risk 5 — The local adapter can be misrepresented

The build prompt handles this risk well by requiring a persistent `ENFORCEMENT: LOCAL ADAPTER` banner. Keep this requirement. A locally implemented policy checker is useful for development, but it is not proof that ArmorIQ enforced the action.

**Required action:** In the presentation and demo, distinguish `ARMORIQ_MODE=real` from `ARMORIQ_MODE=local`. Never label a locally generated hash as an ArmorIQ cryptographic proof. If the real SDK does not return a field, do not display a fabricated equivalent.

## What should be changed before coding

| Priority | Change | Why |
|---:|---|---|
| 1 | Lock **Mandate** as the only product name and concept | Prevents AutoMart/ProcureProof/Mandate drift across agents and slides |
| 2 | Extract Part 1 of the build prompt into `SPEC.md` | Gives the coding agent a short, stable contract instead of a large prompt file |
| 3 | Verify the real SDK and proxy behavior | Determines whether the core demo is genuine and how HOLD/resume works |
| 4 | Build and pass P1–P5 before any UI work | Proves the database, MCP layer, gateway, and plan-ordering invariant first |
| 5 | Keep the BEC attack and parameter attack; make Attack B optional | Attacks A and C provide the strongest realism and semantic-scope proof |
| 6 | Prepare the PDF submission before the finale build | The Round 2 deadline is separate from the later 8-hour implementation window |
| 7 | Archive or label superseded reports | Reduces the chance that Antigravity builds AutoMart instead of Mandate |
| 8 | Confirm finale rules about pre-existing code | The decision memo correctly flags this as a potentially decisive eligibility issue |

## Recommended final source-of-truth stack

| File | Status | Use |
|---|---|---|
| `DECISION-MEMO.md` | Strategic decision | Keep as the rationale and risk register |
| `ANTIGRAVITY-BUILD-PROMPT.md` | Implementation blueprint | Use to generate `SPEC.md` and execute P0–P10 |
| `SPEC.md` | **Create next** | Authoritative contract for the coding agent |
| `ARMORIQ_DISCOVERY_REPORT.md` | Superseded | Retain for comparison, but do not use as build instructions |
| `armoriq_hackathon_discovery_report.md` | Research reference | Keep for citations and product-discovery background |
| `ARMORIQ-PRODUCT-DISCOVERY.md` | Superseded/incomplete | Retain only as historical reasoning |
| `README.md` | **Create next** | Explain the source of truth, run commands, modes, and honesty labels |
| `DEMO.md` | Create at P10 | Exact rehearsal sequence, recovery lines, and expected balances |

## Final verdict

**Mandate is the right plan and should be built.** I rate the strategic and technical plan **9.2/10** and the current execution readiness **7.8/10**.

The plan is not weak because of product strategy; it is waiting on execution proof. The next milestone is not more ideation. It is a short, real ArmorIQ SDK spike followed by P1–P5 acceptance gates. If the SDK behaves as documented, the team has a highly credible finalist concept. If the SDK is unavailable or materially different, the team should preserve the same product and demo story but label the local adapter honestly and avoid claiming real ArmorIQ enforcement until it is verified.

> **Go decision:** Build Mandate. Freeze the concept. Verify the SDK. Implement the boundary before the interface. Prepare the PDF in parallel, but do not let slide polish delay T1–T3.
