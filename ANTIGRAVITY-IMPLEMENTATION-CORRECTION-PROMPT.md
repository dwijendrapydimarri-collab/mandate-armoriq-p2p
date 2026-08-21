# Antigravity Prompt — Implementation Status Reconciliation Before More Work

The plan-review document is accepted as a planning correction, but the repository state shows that implementation has already started. Do not claim that the project is still before P1. Do not begin a new phase blindly. First reconcile the existing code against `SPEC.md` and correct the security-boundary defects below.

## Evidence already observed

- `backend/` exists and contains substantial runtime code.
- `frontend/` exists and contains a built frontend directory.
- `tests/test_invariants.py` exists.
- The current invariant suite has actually passed: `10 passed` with one deprecation warning.
- `tests/test_judge_mode.py` is not present yet.
- `implementation_plan.md` says the project is awaiting P1, but code already contains behavior from P1 through P8. Update the status honestly.

## Required response before editing

Return an `IMPLEMENTATION-STATUS.md` report saved in the repository root containing:

1. Actual status of each phase based on files and executed tests.
2. Which tests have verbatim passing output and which are only specified.
3. Every deviation from `SPEC.md`.
4. A corrected next-phase plan.
5. The exact files you will modify.

Then stop for approval before making the corrections below.

## Security and architecture corrections

### 1. Fix the HOLD approval bypass

The current controller path can auto-approve a held decision by calling the domain payment function directly. That violates the sole gateway invariant and bypasses ArmorIQ.

Correct behavior:

- A held decision is persisted as pending.
- The controller never calls `domain_initiate_payment` directly for a held action.
- `POST /api/approve/{decision_id}` resumes the original request through the same `gateway.call()` path.
- Preserve the original mission, intent token, delegation, parameters, and decision relationship.
- Do not mint a fresh unrestricted token.
- Add a regression test proving that every payment, including an approved HOLD, passes through the gateway and that direct controller-to-domain payment is impossible.

### 2. Resolve MCP transport fidelity

Inspect `backend/mcp_server/client.py`. The current implementation appears to import the MCP server object in-process and call it directly rather than connecting to the required stdio server process.

Choose one option and document it explicitly:

- Implement the official MCP Python SDK over the required stdio transport, or
- Amend `SPEC.md` only after proving that the in-process official SDK path is an intentional, compatible decision for this hackathon.

Do not silently claim “stdio” while using an in-process singleton. Add a smoke test that proves the selected transport.

### 3. Remove hardcoded canonical-invoice policy logic

Inspect `backend/armoriq/local.py`. Decisions must derive from the sealed mission envelope, trusted vendor master, purchase order, delegation grant, and actual parameters—not from special invoice IDs such as `INV-2043` or hardcoded attack amounts.

Replace rules such as:

```python
if invoice_id == "INV-2043" or amount_paise == 14500000:
```

with generic policy logic:

- Payee must be in the mission’s sealed approved-payee set.
- Amount must be within the applicable PO and mission scope.
- A legitimate over-ceiling payment may return HOLD based on policy and trusted PO facts, not an invoice ID.
- A malicious payee or parameter must remain BLOCK regardless of invoice text.

Add tests using new invoice IDs and new vendor/PO values to prove the policy generalizes.

### 4. Make custom CFO ceilings real

The current local plan logic appears to hardcode a ₹50,000 per-invoice ceiling and ₹3,00,000 mission ceiling. In Judge Mode, the judge-created ceilings must be captured into the sealed Authority Envelope and enforced for that mission.

Add tests proving:

- Custom ₹10,000 ceiling blocks ₹10,001.
- Custom ₹100,000 ceiling allows an otherwise valid ₹50,000 payment or returns configured HOLD.
- A new mission receives new limits without changing the canonical mission.

### 5. Eliminate global mission leakage

Inspect `backend/gateway.py` for global `current_mission_id` and `current_intent_token` state. It is unsafe for isolated judge scenarios and can cause one browser mission to use another mission’s token.

Prefer explicit mission and token context passed through the call chain. If a temporary context object is necessary, scope it per request or mission and add a test proving two scenarios cannot cross-read grants, tokens, vendor records, or ledger rows.

### 6. Implement the missing Judge Mode surface

The repository must contain and test the planned endpoints:

- `POST /api/scenario/new`
- `POST /api/scenario/cfo-setup`
- `POST /api/scenario/seal`
- `POST /api/scenario/invoice-intake`
- `POST /api/scenario/probe`

It must also contain the browser surfaces:

- CFO Setup
- Mission Seal
- Invoice Intake with `UNTRUSTED` label
- Judge Challenge Console with four typed probes
- Trust Boundary Map
- Counterfactual Ledger Proof labeled `COUNTERFACTUAL — NOT EXECUTED`
- Reset Demo, Load Canonical Demo, and New Judge Scenario

Do not report J1–J7 or W1–W6 as verified until `tests/test_judge_mode.py` and browser evidence exist.

## Required verification sequence after approval

1. Run the existing `tests/test_invariants.py`; preserve the current passing output.
2. Add and run the gateway/HOLD-bypass regression tests.
3. Add and run generic custom-policy tests with new IDs and limits.
4. Add and run scenario-isolation tests.
5. Implement Judge Mode endpoints.
6. Implement Judge Mode UI.
7. Add `tests/test_judge_mode.py` and browser tests.
8. Run the canonical replay and the custom-judge scenario from a clean checkout.
9. Record the exact output and screenshots.

## Non-negotiable honesty rule

The current passing invariant suite proves only the tests it actually covers. It does not prove real ArmorIQ enforcement, Judge Mode, deployment readiness, or browser usability. Keep `ARMORIQ_MODE=local` visibly labeled until a real ArmorIQ SDK invocation is captured.

Return the status report first, then stop and wait for human approval before changing code.
