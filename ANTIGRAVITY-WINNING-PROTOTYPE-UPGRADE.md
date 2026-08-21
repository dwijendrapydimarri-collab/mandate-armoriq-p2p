# Antigravity Directive — Build the Winning Mandate Prototype

**Use this after Antigravity has amended its plan for Judge Mode and before it begins P1.**  
**Primary contract:** `SPEC.md`, especially sections 1.14 and 1.15.  
**Goal:** Build a live, judge-challengeable **Authority Envelope** for autonomous payments—not a generic invoice dashboard and not a scripted demo.

```text
Read SPEC.md fully, including sections 1.14 and 1.15, before changing the implementation plan or writing code.

You are not building a standard accounts-payable app. You are building MANDATE: a live, judge-testable Authority Envelope for autonomous payments.

The product’s memorable moment must answer one question visually:
“Can this exact autonomous payment cross the authority boundary—and what would happen if it did?”

Do not add agents, external services, custom cryptography, fraud-scoring models, blockchain, vector databases, a payment provider, or a second policy engine. The winning experience must be assembled from the existing mission, delegation, gateway, ArmorIQ decision, MCP tool, ledger, and provenance data.

Add the following features to the implementation plan before starting P1. Show the amended phase plan, changed file list, acceptance gates W1–W6, and then stop for approval.

1. Authority Envelope
   - In CFO Setup, collect trusted vendor, payee, PO, per-invoice ceiling, and mission ceiling.
   - On Mission Seal, capture the plan and token, then render a sealed Authority Envelope.
   - Render the actual trusted scope: named CFO, approved payees, PO references, ceilings, agent capability scopes, token state, and real ArmorIQ proof fields if available.
   - After sealing, trusted scope is immutable for that mission.

2. Trust Boundary Map
   - For every proposed payment, show trusted facts separately from untrusted invoice-origin facts.
   - Example: requested_payee = HDFC 509900443322 is UNTRUSTED; approved_payee = ICIC 004709988776 is TRUSTED.
   - Show the exact conflict rule and decision. Do not claim an LLM “detected prompt injection.” The story is that authority refused the untrusted request.

3. Counterfactual Ledger Proof
   - For a BLOCK or HOLD, calculate the projected debit, credit, payee, and loss if the action had executed.
   - Label it exactly: COUNTERFACTUAL — NOT EXECUTED.
   - It must use attempted parameters, but must never dispatch a payment tool or create a ledger entry.
   - T2 and T3 remain mandatory proof that real state did not change.

4. Judge Challenge Console
   - Build browser-only Judge Mode with four starter tests: valid payment, unapproved payee, excessive amount, and matcher attempts payment.
   - Let a judge select agent, tool, and typed parameters.
   - Every challenge must call the exact same gateway method as agent proposals: gateway.py → configured ArmorIQ adapter → MCP tool only on ALLOW.
   - The console is a TEST PROPOSAL — NOT AN LLM DECISION. This is intentional: it lets judges challenge the enforcement boundary directly.
   - No SQL, shell, arbitrary code execution, real banking, or governance-off switch in Judge Mode.

5. Authority Cliff Replay
   - In Mission Control, animate a proposed action from the agent to the ArmorIQ boundary.
   - An allowed action proceeds to the tool and updates state.
   - A blocked action stops at the boundary. The view then reveals:
     untrusted claim → attempted parameter → sealed rule → ArmorIQ verdict → counterfactual prevented loss.
   - The blocked forensics header must say AUTHORIZED BY: NOBODY.

6. Canonical Mission Compare
   - Preserve the governed/un governed seeded comparison only as a presentation-mode Counterfactual Ledger Proof.
   - It is never exposed as a normal customer/judge feature.

Suggested phase placement:
- P1: scenario model, payment-domain projection helper, data origin/classification fields.
- P5: Authority Envelope sealing and immutable trusted setup.
- P6/P7: Trust Boundary Map source data, Counterfactual Ledger Proof for attacks, and the challenge-path test cases.
- P9: Mission Control visuals, Authority Cliff Replay, Challenge Console, custom scenario flow.
- P10: W1–W6 browser/replay tests and video-ready rehearsal.

You must preserve every existing T1–T6 and J1–J10 invariant. The new features are successful only if they are generated from real mission and decision data rather than hardcoded visual states.

Before declaring P9 complete, run a browser test and show evidence of this exact flow:
1. Create a CFO trusted setup.
2. Seal the Authority Envelope.
3. Enter a plausible remittance advisory after seal.
4. Run the agent and show the block before tool dispatch.
5. Show Counterfactual Ledger Proof with no real ledger change.
6. Run a Judge Challenge probe using a different payee or amount.
7. Open forensics and show AUTHORIZED BY: NOBODY.

Do not report success without the exact test commands, passing output, screenshots or recording, and a clear indication of ARMORIQ_MODE=real or ARMORIQ_MODE=local.
```

## The intended product identity

> **Mandate is an Authority Envelope for autonomous payments: finance teams define trusted authority once, agents work within it, and anyone can challenge the boundary before money moves.**

## What not to accept from Antigravity

| Weak implementation | Why it fails |
|---|---|
| A static “allowed payees” card | It does not prove the card comes from the sealed mission or governs a tool call |
| A red block toast | It does not show why the request conflicted with trusted authority or prove state remained unchanged |
| A fake UI sandbox form | It does not prove the judge’s input traverses the same gateway and authorization path |
| A locally computed “crypto hash” labeled as ArmorIQ proof | It misrepresents the sponsor technology |
| A fraud risk score | It turns the product into another detector instead of an authority enforcement system |
| A governance-off button in normal Judge Mode | It makes the product appear unsafe and undermines the security story |
