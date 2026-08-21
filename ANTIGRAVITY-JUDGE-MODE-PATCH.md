# Antigravity Directive — Judge-Ready Product Patch

**When to use:** Paste this into Antigravity **before approving P1**. If P1 has already started, paste it before proceeding to P2 and require the implementation plan to be amended before more code is written.

```text
Read SPEC.md again, including the newly appended section 1.14, “Judge Mode and deployable custom-input contract,” before writing or changing code.

The project has a new non-negotiable requirement: MANDATE is not only a fixed canonical demo. A judge must be able to use the deployed application in a browser, create a safe sandbox procurement mission, supply their own inputs, and observe the same authority boundary. The canonical seeded scenario remains the deterministic rehearsal and regression fixture.

Do not weaken the security model to make custom input possible. Implement two explicit phases:

1. CFO Setup — trusted, pre-seal data only. The judge creates approved vendor records, approved payee accounts, open purchase orders, per-invoice ceiling, and mission ceiling.
2. Invoice Intake — untrusted, post-seal data only. After Mission Seal, the judge adds invoice vendor, PO, amount, and arbitrary advisory text.

The required rule is unchanged:
trusted setup → capture_plan + get_intent_token → untrusted invoice text → invoke every payment.

After Mission Seal, the trusted vendor master, approved payees, open PO amounts, and ceilings must be immutable for that mission. The UI must require a new mission if the judge wants to change them. Invoice text must never directly mutate trusted records.

Add the following requirements to the implementation plan and mark their implementation phases:

A. New Judge Scenario: a browser-only flow that creates an isolated sandbox mission. No real bank or vendor integration, no arbitrary SQL, no shell commands, and no external payee URLs.

B. CFO Setup form: create vendor, payee, PO, per-invoice ceiling, and mission ceiling before sealing.

C. Mission Seal: captures the plan and displays the frozen authority envelope. No changes to the trusted setup after sealing.

D. Invoice Intake form: adds arbitrary free text after sealing and labels it UNTRUSTED.

E. Security Probe panel: lets a judge submit a typed test proposal using an agent identity, selected tool, and parameters. Label it “TEST PROPOSAL — NOT AN LLM DECISION.” It must traverse the same gateway.py → ArmorIQ → MCP path as every agent action. It is required because a judge must be able to test the boundary even if an LLM does not follow a particular malicious note.

F. Scenario controls: Reset Demo, Load Canonical Demo, and New Judge Scenario. The governance-off comparison remains presentation-only and must not be a normal judge-mode control.

G. Browser acceptance tests J1–J7 from SPEC.md section 1.14. Add them to the test plan. They supplement T1–T6 and are required before declaring the product judge-ready.

H. Deployment readiness: production build succeeds; README provides one-command local run and reset instructions; no secret is exposed to the frontend; local mode has the persistent local-adapter disclosure.

Amend the P1–P10 plan before implementation. Suggested placement:
- P1: mission and scenario data model; scenario isolation and reset primitives.
- P5: trusted setup, mission seal, and immutable post-seal state.
- P6/P7: custom-input probes must prove the existing attack and delegation invariants on a judge-created scenario.
- P9: CFO Setup, Invoice Intake, Security Probe, scenario controls, and browser test coverage.
- P10: cold-start deployed-build and J1–J7 verification.

Do not begin UI polish or claim that the project is complete until you have shown the amended phase plan, listed the exact new or modified files, and listed the J1–J7 acceptance gates.
```

## What a correct Antigravity response must contain

| Required item | Why it matters |
|---|---|
| Acknowledgement that `SPEC.md §1.14` is binding | Ensures it did not build only a scripted demo |
| New Judge Scenario model or isolation scheme | Prevents state contamination between judge tests |
| Clear pre-seal versus post-seal workflow | Preserves the plan-ordering invariant |
| Immutable trusted setup after Mission Seal | Prevents a judge or invoice from silently widening authority |
| Security Probe through the exact gateway path | Proves the boundary independently of LLM behavior |
| J1–J7 browser test plan | Converts “judge can use it” into verifiable acceptance criteria |
| Deployment and secret-handling plan | Makes the repository/deployed-link submission real |

Reject any plan that merely adds a text input on the demo screen. A generic form without data classification, mission sealing, immutability, scenario isolation, and browser tests does not satisfy this requirement.
