# Antigravity Prompt — Step 4 Judge Mode UI & Winning Visual Experience

Step 3 is approved. The current backend/API suite has 28 passing tests. Begin Step 4 only: build the browser UI against the real Judge Mode endpoints. Do not replace API calls with hardcoded mock data.

## Required UI surfaces

Build these components and integrate them into the existing Mission Control application:

1. `ScenarioBar.tsx`
   - `Load Canonical Demo`
   - `New Judge Scenario`
   - `Reset Sandbox`
   - visible current scenario ID and status

2. `CFOSetupModal.tsx`
   - vendor name and ID
   - approved payee account and IFSC
   - PO ID, vendor, amount in rupees, and description
   - per-invoice ceiling and mission ceiling
   - validation errors in plain language
   - submit only before seal

3. `InvoiceIntakeModal.tsx`
   - invoice ID, vendor, PO, amount, and arbitrary free-text advisory
   - prominent `UNTRUSTED INPUT` label
   - available only after Mission Seal
   - clear statement that invoice text cannot edit trusted authority

4. `JudgeChallengeConsole.tsx`
   - agent selector
   - tool selector restricted to the server-approved tools
   - typed parameter editor
   - four starter presets: Valid Payment, Unapproved Payee, Excess Amount, Matcher Direct Spend
   - prominent label: `TEST PROPOSAL — NOT AN LLM DECISION`
   - display verdict, reason, decision ID, proof, and counterfactual when returned

5. `AuthorityEnvelope.tsx`
   - sealed/unsealed state
   - named user
   - approved payees
   - PO references
   - per-invoice and mission ceilings
   - delegated agent capabilities
   - plan hash and intent-token state
   - real ArmorIQ proof fields only when actually returned
   - local-mode disclosure remains visible

6. `TrustBoundaryMap.tsx`
   - side-by-side trusted facts and untrusted claims
   - origin label for every field
   - exact conflict, for example `requested_payee ≠ approved_payee`
   - do not describe this as “the AI detected prompt injection”; explain the authority conflict

7. `CounterfactualProof.tsx`
   - projected debit, destination, and prevented loss for blocked/held actions
   - exact label: `COUNTERFACTUAL — NOT EXECUTED`
   - never mutate the actual ledger

8. `AuthorityCliffReplay.tsx`
   - action path from agent → gateway → ArmorIQ → MCP tool
   - ALLOW crosses the boundary and changes sandbox state
   - BLOCK stops at the boundary
   - blocked forensics header: `AUTHORIZED BY: NOBODY`

## Non-negotiable UI behavior

- All custom scenario buttons call the real backend endpoints.
- No UI state may display ALLOW, BLOCK, or HOLD unless the backend returned that verdict.
- The frontend must never contain ArmorIQ, LLM, or private signing keys.
- Normal Judge Mode must not expose governance-off mode.
- The canonical comparison must be visibly labeled as a sandbox comparison.
- Trusted setup becomes read-only after seal; changing it starts a new scenario.
- A blocked probe must show unchanged ledger state.
- The UI must work at 1280×720 and remain usable at a smaller laptop viewport.
- Rupee amounts must be integer-paise accurate and formatted consistently.
- Handle backend errors, loading states, and network timeouts without silently showing stale verdicts.

## Required browser verification before Step 4 completion

Create browser tests or a documented manual browser run for:

1. New Judge Scenario → CFO Setup → Mission Seal.
2. Confirm the Authority Envelope is populated from the actual API response.
3. Add arbitrary untrusted invoice text after seal.
4. Run a legitimate custom invoice and observe the actual result.
5. Run an unapproved-payee probe and observe the action stop before the tool.
6. View Trust Boundary Map and Counterfactual Proof.
7. Open forensics and confirm `AUTHORIZED BY: NOBODY` for the blocked action.
8. Reset Sandbox, Load Canonical Demo, and create a second new scenario.
9. Confirm the first scenario’s ledger and authority do not leak into the second.
10. Inspect the browser network and production bundle for secrets.

Do not mark J6–J10 or W1–W6 verified until these tests have actually run and the output/screenshots are recorded. Preserve all 28 backend tests.

## Required completion report

Return:

- exact files created and modified
- endpoint-to-component mapping
- browser test command or manual test procedure
- screenshots or recording of a custom judge scenario
- complete backend and frontend test output
- any remaining limitation, especially `ARMORIQ_MODE=local`

Then stop for human review before Step 5 deployment, final replay, and submission hardening.
