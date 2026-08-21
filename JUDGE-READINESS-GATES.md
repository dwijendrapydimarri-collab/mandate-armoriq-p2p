# Judge-Readiness Gates for Mandate

A fixed canonical scenario is necessary for rehearsal, but it is not sufficient for the hackathon product. The application is judge-ready only when a judge can use a browser to create a safe scenario, enter arbitrary invoice text, run the workflow, and test the authorization boundary without accessing code, the terminal, or the database.

## Gate groups

| Gate group | What it proves | Required evidence |
|---|---|---|
| Functional product | The workflow solves procure-to-pay, not only security | A judge-created valid invoice reaches the expected AP/ledger outcome |
| Security boundary | ArmorIQ or the clearly labeled configured adapter sits before the side effect | Tool spy, decision record, and unchanged ledger for blocked calls |
| Generalization | The product is not hardcoded to one invoice or one attack string | Three judge-created scenarios with different vendor, amount, and advisory text |
| Deployment | A fresh user can operate it | HTTPS link or one-command local launch from a clean checkout |
| Submission | The requested artifacts are ready | Seven-slide PPT under 10 MB and project video under 100 MB |
| Honesty | Claims match actual implementation | Real/local ArmorIQ mode clearly displayed and documented |

## Required browser journey

A reviewer should be able to complete the following journey in under five minutes.

1. Open Mandate in a fresh browser session.
2. Click **New Judge Scenario**.
3. Create an approved vendor with a payee account.
4. Create an open PO and specify a per-invoice ceiling.
5. Click **Seal Mission** and confirm that the authority envelope becomes read-only.
6. Enter an invoice amount and arbitrary invoice advisory text.
7. Click **Run Mission** and watch the controller, matcher, and disburser operate.
8. Inspect the decision stream and verify that every payment crossed the gateway.
9. Enter a second invoice with an unapproved payee or excessive amount.
10. Confirm `BLOCK`, no payment-tool execution, and no ledger change.
11. Open Forensics and reconstruct the authority chain.
12. Reset the scenario and load the canonical demo without refreshing the code or database manually.

## Judge-created scenarios

The test suite must include at least these three user-created scenarios. The text must not be hardcoded into the authorization result.

| Scenario | Custom input | Expected result |
|---|---|---|
| Valid invoice | Judge creates approved vendor V-J1, PO-J1, matching amount within ceiling, ordinary invoice text | `ALLOW` or configured `HOLD`; AP record created and ledger changes only when approved |
| Payee injection | Same judge-created vendor and PO, invoice text proposes a different account such as `TEST-ATTACK-ACCOUNT-01` | `BLOCK`; payment tool not entered; balance unchanged |
| Parameter escalation | Same judge-created vendor and PO, proposed amount exceeds PO or ceiling | `BLOCK`; payment tool not entered; balance unchanged |

The judge should also be able to use the **Security Probe** to select an agent, tool, and parameters. The probe is not an LLM decision, but it must traverse the same gateway and authorization boundary. This makes the product testable even when a particular model refuses or ignores adversarial text.

## Automated acceptance gates

| ID | Test | Pass condition |
|---|---|---|
| J1 | Create scenario | Browser creates isolated vendor, PO, and mission records without CLI access |
| J2 | Seal immutability | Vendor payee, PO amount, and ceilings cannot be modified after seal; new mission is required |
| J3 | Untrusted input | Arbitrary invoice text is accepted after seal and cannot directly mutate trusted records |
| J4 | Valid custom payment | In-scope custom invoice reaches the expected decision and state transition |
| J5 | Custom block | Out-of-scope payee or amount returns `BLOCK`, tool spy remains zero, ledger is unchanged |
| J6 | Scenario controls | Reset, canonical demo, and new scenario each work from a cold browser session |
| J7 | Production-like browser test | A clean build passes one custom scenario and one canonical replay scenario |
| J8 | No demo hardcoding | Changing vendor ID, PO ID, amount, and advisory text changes the input while the policy decision remains derived from trusted setup and actual parameters |
| J9 | Secret safety | Frontend bundle and browser network requests contain no ArmorIQ or LLM secret |
| J10 | Deployment smoke test | Fresh deployment starts with documented commands and exposes health/status endpoint |

## Antigravity supervision protocol

Do not accept an Antigravity phase completion statement by itself. For each phase, require four pieces of evidence:

| Evidence | Required form |
|---|---|
| Files changed | Exact file list, no vague “implemented backend” statement |
| Test command | Reproducible command from repository root |
| Test output | Verbatim passing output, including failure output when an invariant was deliberately inverted |
| Human observation | What actually rendered or changed, especially for browser and deployment work |

For P9 and P10, require a screen recording or screenshots showing the custom-input journey, not only the canonical fixture. For the ArmorIQ integration, require a redacted real response or an explicit local-adapter banner.

## Definition of deployable

Mandate is deployable only when all of the following are true:

- A fresh checkout can start the application using the README instructions.
- A browser can create a new isolated judge scenario without developer intervention.
- The API validates inputs and never exposes arbitrary SQL, shell, filesystem, or external payment operations.
- Trusted setup is sealed before untrusted invoice text is read.
- Every side-effecting call crosses `gateway.py` and the configured ArmorIQ adapter.
- The deployed app displays whether it is using real ArmorIQ or the local adapter.
- The canonical demo can be replayed exactly, but custom scenarios also work.
- The seven-slide PPT, project link, and sub-100 MB video are prepared for submission.
