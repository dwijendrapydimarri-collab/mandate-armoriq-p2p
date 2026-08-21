# ArmorIQ Hackathon — Product Discovery & Strategy
**Automate India / HackBriven · Track: ArmorIQ · Prepared 19 Aug 2026**

---

## READ THIS FIRST — two honesty disclosures

**1. I had no internet access while writing this.** Egress was blocked in this session, so I could not verify a single external fact. Everything I say about open-source projects, ArmorIQ, Notion's API, or licences comes from my own knowledge, which is reliable only up to **May 2025**. Every external dependency in this document is tagged `[VERIFY]`. Treat those tags as a literal to-do list — assign one person two hours to check them before you commit to the architecture. I have deliberately chosen a design whose critical path depends on almost nothing I could not verify.

**2. Your original idea is not the best one.** You asked me to be brutal. The DevOps Incident Response Agent ranked **9th out of 10**. It is the single most over-used demo in the entire agent-security space, its dangerous actions require judges to understand Kubernetes, and it needs flaky local infrastructure that will betray you at a venue. Full reasoning in Sections 2 and 3. Drop it.

---

## EXECUTIVE VERDICT

Build **MANDATE** — an autonomous accounts-payable back office that processes a week of vendor invoices end to end with no human babysitting, and **cryptographically cannot pay anyone the CFO did not authorise.**

It wins because of one structural property no other candidate has: **money is the only stake that needs zero explanation.** Every judge on that panel — ArmorIQ engineer, Notion jury, HackBriven mentor, the VC in the corner — already understands invoice fraud. You will never spend a second of your 180 explaining why the dangerous action is dangerous. That saves you the scarcest resource in the room: judge attention.

And the attack writes itself. The most common real-world attack on accounts payable is **Business Email Compromise**: a supplier document arrives saying "our bank details have changed, please remit to this new account." It is a multi-billion-dollar annual loss category. It is also, precisely, an **indirect prompt injection** — attacker-controlled text inside data the agent is legitimately required to read. You do not have to invent a contrived attack. You reproduce the most expensive fraud in corporate finance and show ArmorIQ stopping it.

Critically, no content filter can stop it, because the malicious instruction is indistinguishable from a legitimate remittance update. The only defence is the one ArmorIQ sells: **the set of accounts this mission may ever pay is fixed, signed, and frozen before the agent reads any attacker-controllable text.** That single sentence makes ArmorIQ load-bearing rather than decorative, and it is the intellectual core of your submission.

---

## SECTION 0 — THE NEXT 60 HOURS (the deadline you actually have)

You framed this as a build question. It is not yet. Re-read your own submission form:

> Round 2 · Ends **Aug 21, 2026, 11:59 PM** · Project Name, Idea Name, Project Description, **Presentation File (PDF), max 10 MB**, GitHub URL.

Round 2 is judged on *"innovation, feasibility, problem understanding, and presentation."* **Nobody runs your code this round.** The finale is a separate, later, ~8-hour live build. So your next 60 hours produce a **PDF and three paragraphs of text** — not a system.

This changes everything about how you should spend today:

| Priority | Action | Owner | Deadline |
|---|---|---|---|
| **P0** | Email/DM ArmorIQ **today** asking for SDK access, docs, and sandbox credentials. Mention you are a shortlisted Round-2 team building on their enforcement layer. | Team lead | 19 Aug, EOD |
| **P0** | Confirm the finale rules: **may you bring pre-existing code into the 8 hours?** The answer changes your entire prep strategy. Ask the organisers in writing. | Team lead | 20 Aug |
| **P0** | Write the Round-2 PDF (structure in Appendix A) | Whole team | 21 Aug, 6 PM |
| **P1** | Stand up a public GitHub repo with README, architecture diagram, typed schemas, and the ArmorIQ adapter interface. Judges click that link. An empty repo reads as vapourware; a repo with a crisp spec reads as a team that will ship. | Builder | 21 Aug |
| **P2** | Only after the above: start coding the sandbox ledger. | Builder | post-submission |

The ArmorIQ SDK request is the highest-leverage action available to you and it costs one email. You currently have **zero** access to the thing your entire submission is built on. If they never respond, you will be demoing against an adapter you wrote, and you need to know that weeks in advance, not at hour 6 of the finale.

**On track selection:** your form shows a single-select for the problem statement, and P1 (*"Autonomous, until it shouldn't be"*) is chosen. Keep it. Mandate leads with P1 and delivers P2 as an unrequested bonus. In the PDF, say so explicitly: *"We selected Problem 1. Our architecture also fully satisfies Problem 2 — cryptographic delegation across independent sub-agents — because spend authority cannot be modelled honestly without it."* Judges remember teams that over-deliver on scope. They do not reward teams that ticked two boxes badly.

**On the Notion lane:** the hackathon's stated rule is *"output with no destination doesn't count"* and Notion runs its own jury with its own prize pool. Mandate's AP register lives in a **real Notion database**, and every authorisation decision is written back to a Notion audit database. This is not prize-farming — it is the correct design. A Notion database is mutable, structured, projector-legible state, which is exactly what you need to *prove* that a blocked action changed nothing. Same build, two juries. Check whether cross-lane eligibility is permitted `[VERIFY]`; if it is not, the design still stands on its own merits.

---

## SECTION 1 — TOP 10 PRODUCT CONCEPTS

Format per candidate: concept · domain · autonomous workflow · agents · tools · dangerous action · P1 · P2 · reusable OSS · build complexity · demo complexity · novelty.

---

### C1 · SentinelOps — *your original idea*
**Concept:** An agent triages production alerts and remediates them autonomously, stopping at anything that risks data loss.
**Domain:** Cloud infrastructure / DevOps.
**Workflow:** Ingest alert → read logs and metrics → form hypothesis → apply remediation (restart, scale, roll back) → write postmortem.
**Agents:** Orchestrator, Diagnostician (read-only), Remediator (write).
**Tools:** log search, metrics query, container restart, deploy rollback, incident write-up.
**Dangerous action:** Drop a production database, delete a namespace, scale a critical service to zero.
**P1:** Restarts and rollbacks proceed unattended; a schema-destructive migration is held.
**P2:** Diagnostician holds read-only delegation; it attempts a restart and is blocked.
**OSS:** Docker Compose stack, Prometheus/Grafana, a Kubernetes-in-Docker cluster or a mocked control plane, Gitea.
**Build:** High — you must build believable infrastructure *before* you build the product.
**Demo:** High risk. Container orchestration on a venue laptop, under time pressure, on someone else's projector.
**Novelty:** Low. This is the canonical agent-security demo; expect other teams to bring it.

---

### C2 · MANDATE — autonomous accounts payable ★
**Concept:** An autonomous back office that processes vendor invoices to payment, and cryptographically cannot pay any account outside the authority its CFO granted.
**Domain:** Finance / business operations.
**Workflow:** Read the week's invoices from Notion → extract line items → three-way match against purchase orders and the vendor master → classify discrepancies → initiate payment for clean invoices → write outcomes to the Notion AP register.
**Agents:** Controller (parent/orchestrator), Extractor (read-only), Matcher (read PO + vendor master), Disburser (sole holder of payment capability, capped).
**Tools:** `notion_query_invoices`, `get_purchase_order`, `lookup_vendor_account`, `initiate_payment`, `notion_write_ap_record`.
**Dangerous action:** Remit real funds to an account not on the vendor master, or above the delegated per-invoice ceiling.
**P1:** Seven invoices clear with no human input. One legitimately exceeds the ceiling → **HOLD** → CFO approves → resumes. One fraudulent → **BLOCK**.
**P2:** Extractor, Matcher and Disburser have separate keypairs and disjoint capability sets. Extractor attempts payment → blocked at the delegation layer, not by policy luck.
**OSS:** Notion API + Notion MCP server, MCP Python SDK, React Flow, injection phrasings from AgentDojo's banking suite, Ed25519 via PyNaCl. Mock bank is ~150 lines of ours.
**Build:** Low–medium. CRUD, SQLite, FastAPI, one React page. The most vibe-codable candidate on this list.
**Demo:** Low risk. Everything except Notion runs locally and deterministically. Two balance figures tell the whole story.
**Novelty:** Medium on the task (AP automation is a real market), high on the mechanism (pre-committed payment authority bound to a signed intent).

---

### C3 · AtlasTrim — autonomous cloud cost optimiser
**Concept:** An agent hunts idle cloud resources and reclaims them, without ever touching anything production-tagged.
**Domain:** Cloud infrastructure.
**Workflow:** Inventory resources → compute waste → rightsize or delete → report savings.
**Agents:** Orchestrator, Auditor (read-only), Reclaimer (delete/resize).
**Tools:** list resources, read utilisation, resize instance, delete volume, delete snapshot.
**Dangerous action:** Delete the only snapshot of a production database.
**P1:** Reclaims eleven idle dev volumes; halts on a prod-tagged snapshot.
**P2:** Auditor attempts a delete outside its grant.
**OSS:** LocalStack (a genuinely good fit), Terraform state, Infracost.
**Build:** Medium — LocalStack is helpful but adds a moving part and its own failure modes.
**Demo:** Medium. "We saved $4,200/mo" is decent; deleting a fake EBS volume is far less visceral than money leaving a bank account.
**Novelty:** Low.

---

### C4 · Recourse — autonomous refunds and credits
**Concept:** An agent resolves customer complaints end to end, including issuing refunds, within a per-ticket authority.
**Domain:** Digital commerce / support.
**Workflow:** Read ticket → pull order history → decide remedy → issue refund or credit → reply to customer → close ticket.
**Agents:** Triage, Investigator (read-only), Remediator (refund capability, capped).
**Tools:** ticket read, order lookup, issue refund, send reply, close ticket.
**Dangerous action:** Refund far above the order value, or refund to a payment instrument the customer did not use.
**P1:** Clears eight tickets; holds a ₹40,000 goodwill credit.
**P2:** Investigator tries to refund.
**OSS:** Notion or a Dockerised helpdesk, Stripe test mode, MCP SDK.
**Build:** Low. Genuinely easy.
**Demo:** Low risk, good visuals.
**Novelty:** Low — "AI support agent" is the most crowded demo category in existence, and judges are fatigued by it.

---

### C5 · Erasure — autonomous right-to-be-forgotten
**Concept:** An agent executes GDPR/DPDP data-subject requests across systems, with deletion authority scoped to exactly one verified subject.
**Domain:** Compliance / privacy.
**Workflow:** Receive request → verify identity → discover all records for that subject → produce an export → execute erasure → issue a compliance certificate.
**Agents:** Intake, Discovery (read-only), Eraser (delete capability, single-subject scope).
**Tools:** identity verify, cross-system search, generate export, delete records, write certificate.
**Dangerous action:** Delete another subject's records, or export a whole table instead of one subject's rows.
**P1:** Completes three requests; halts when a deletion would cascade beyond the subject.
**P2:** Discovery agent attempts deletion.
**OSS:** Postgres, Faker, OpenDataRights-style schemas.
**Build:** Medium.
**Demo:** Medium. Row-count diffs are provable and honest but need a sentence of setup, and "GDPR" costs you fifteen seconds of explanation you cannot spare.
**Novelty:** High — I have not seen this done as an agent-security demo. A genuinely interesting runner-up in a longer format.

---

### C6 · Patchwork — autonomous vulnerability remediation
**Concept:** An agent takes CVE advisories to merged patches, with merge authority restricted to non-production branches.
**Domain:** Software development / supply chain.
**Workflow:** Ingest advisory → locate affected dependency → bump version → run tests → open PR → merge to staging.
**Agents:** Orchestrator, Analyst (read-only), Patcher (branch write), Merger (merge to staging only).
**Tools:** advisory fetch, repo search, edit file, run tests, open PR, merge branch.
**Dangerous action:** Force-push to `main`, merge unreviewed code to production, or introduce a typo-squatted package.
**P1:** Three CVEs patched and merged to staging; a `main` merge is held.
**P2:** Analyst attempts a merge.
**OSS:** Gitea in Docker, OSV database, Dependabot-style advisory feeds, Semgrep.
**Build:** Medium-high — git state management is fiddly and hard to reset between demo runs.
**Demo:** Medium. Engineers will love it; the Notion jury and the business judges will partially tune out.
**Novelty:** Medium. Strong real-world value; the poisoned-advisory attack is excellent.

---

### C7 · Procura — autonomous procurement
**Concept:** An agent monitors inventory and issues purchase orders, but only to approved suppliers within a delegated value band.
**Domain:** Supply chain.
**Workflow:** Detect stockouts → check contracts → select supplier → issue PO → update the procurement register.
**Agents:** Planner, Sourcing (read-only), Buyer (PO issuance, capped).
**Tools:** inventory read, contract lookup, supplier lookup, issue PO, register write.
**Dangerous action:** Issue a PO to an unapproved supplier, or above the delegated value.
**P1:** Six POs issued unattended; a ₹12L order is held.
**P2:** Sourcing agent attempts issuance.
**OSS:** Notion, Odoo (heavy), Faker.
**Build:** Low-medium.
**Demo:** Low risk, good story.
**Novelty:** Medium. **This is Mandate's closest rival** and loses narrowly — see Section 3.

---

### C8 · Signatory — autonomous contract execution
**Concept:** An agent reviews inbound contracts, redlines them against playbook, and signs those within its delegated signature authority.
**Domain:** Legal / enterprise operations.
**Workflow:** Ingest contract → clause-by-clause review → redline → route → **sign**.
**Agents:** Reviewer (read-only), Redliner, Signer (signature capability, value- and clause-scoped).
**Tools:** clause extract, playbook lookup, generate redline, request approval, apply signature.
**Dangerous action:** Sign a contract with uncapped liability, or above the delegated contract value.
**P1:** Signs three NDAs; holds an MSA with an unlimited-indemnity clause.
**P2:** Reviewer attempts to sign.
**OSS:** CUAD contract dataset, docx tooling, a mock e-signature service.
**Build:** Medium-high — contract text is heavy and redlining well is genuinely hard.
**Demo:** **High risk in 180 seconds.** Judges must read legal prose on a projector. That is death.
**Novelty:** High, and conceptually the most elegant fit for *"Who authorized that?"* — signature authority literally *is* delegated authority. Wrong format, right idea. Remember it for a longer competition.

---

### C9 · Payrun — autonomous payroll operations
**Concept:** An agent runs monthly payroll, resolves discrepancies, and disburses salaries within per-employee authority.
**Domain:** Business operations / HR finance.
**Workflow:** Pull timesheets → compute gross → apply deductions → reconcile → disburse → post to the payroll register.
**Agents:** Orchestrator, Reconciler (read-only), Disburser (capped).
**Tools:** timesheet read, salary lookup, compute payroll, disburse, register write.
**Dangerous action:** Change a bank account on an employee record, pay a ghost employee, **or raise its own operator's salary.**
**P1:** Forty-one salaries paid; one anomalous record held.
**P2:** Reconciler attempts a disbursement.
**OSS:** Notion, Faker, mock bank.
**Build:** Low. Very close to Mandate architecturally.
**Demo:** Low risk. *"The agent gave itself a raise"* is the single funniest and most memorable beat available in this whole list.
**Novelty:** Medium-high. Strong third place; see Section 3 for why it loses.

---

### C10 · Lifeline — autonomous emergency resource dispatch
**Concept:** An agent allocates ambulances and relief supplies during an incident, within a delegated geographic and budget scope.
**Domain:** Emergency response / government.
**Workflow:** Ingest incident reports → assess severity → allocate units → dispatch → log.
**Agents:** Incident Commander, Assessor (read-only), Dispatcher (allocation authority).
**Tools:** incident feed, resource inventory, route calculation, dispatch unit, procurement.
**Dangerous action:** Divert the last critical-care unit out of a zone, or exceed emergency budget.
**P1:** Nine dispatches unattended; one critical diversion held.
**P2:** Assessor attempts dispatch.
**OSS:** Leaflet/Mapbox, OpenStreetMap, SUMO traffic sim.
**Build:** High — map state and simulation are a lot of custom work.
**Demo:** Highest *visual* ceiling on the list — vehicles moving on a live map is beautiful.
**Novelty:** High. But: it cannot be claimed as realistically deployable by a student team, and there is a narrative problem — an audience does not *enjoy* watching a security layer block an ambulance. The emotional valence of your climax is wrong.

**Also considered and cut:** DBT/scholarship disbursement (strong India relevance, but beneficiary data is hard to make credible), autonomous treasury/trading (judges distrust trading bots), marketing ad-spend agent (weaker delegation story), clinical prior-authorisation (uncomfortable to demo; regulatory realism unfakeable), and a research agent that spends API budget (no real destination — fails the hackathon's own rule).
