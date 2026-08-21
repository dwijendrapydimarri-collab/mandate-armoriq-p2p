# Antigravity Prompt — Final Contract Fix Before Step 2

Step 1 security behavior is accepted provisionally: the 17 invariant tests pass, including HOLD-resume authorization and parameter tamper detection. Before starting Step 2, make this contract correction.

## Required correction

`SPEC.md §1.8` still says that `armoriq/adapter.py` defines a Protocol with **exactly four methods**:

```text
capture_plan, get_intent_token, invoke, delegate
```

The implementation now correctly adds `resume()` for HOLD approval. The specification and implementation plan must be reconciled.

Update `SPEC.md`, `implementation_plan.md`, `README.md`, and `IMPLEMENTATION-STATUS.md` so that:

1. The adapter contract contains five methods:
   `capture_plan`, `get_intent_token`, `invoke`, `delegate`, and `resume`.
2. `resume()` is described as a separate human-approval/resume operation that preserves the original decision, intent token, mission, agent, grant, and parameters.
3. The real SDK adapter uses the real SDK resume/approval primitive if available; if unavailable, the local fallback remains clearly disclosed.
4. T1–T6 remain verified only because their actual tests passed; J1–J10 and W1–W6 remain specified/pending.
5. Option B in-process FastMCP is documented consistently as the current local prototype transport; do not call it stdio.
6. The P8 phase and architecture diagrams reference the five-method adapter contract.

Do not modify application behavior in this step unless required to make the contract accurate. Do not implement Judge Mode yet.

Return:
- Exact files changed
- The corrected adapter contract excerpt
- Confirmation that 17 invariant tests still pass
- Confirmation that J1–J10 and W1–W6 remain pending

Then stop. After this correction, Step 2 (Judge Mode Backend and Scenario Isolation) may be approved.
