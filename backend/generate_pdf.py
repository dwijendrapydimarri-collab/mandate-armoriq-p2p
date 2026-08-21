"""
MANDATE — Round 2 Presentation PDF Generator
Generates the crisp 10-slide submission deck for Round 2 using fpdf2.
"""

import os
from fpdf import FPDF


class PresentationPDF(FPDF):
    def header(self):
        self.set_fill_color(7, 11, 20)  # Dark slate
        self.rect(0, 0, 297, 210, 'F')  # A4 landscape 297x210 mm
        
        # Subtle header bar
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 116, 139)
        self.set_xy(15, 10)
        self.cell(0, 5, "MANDATE  |  Autonomous Procure-to-Pay  |  ArmorIQ Hackathon Track", 0, 0, 'L')
        self.set_xy(0, 10)
        self.cell(282, 5, f"Slide {self.page_no()}", 0, 0, 'R')

    def draw_slide_title(self, title: str, subtitle: str = ""):
        self.set_xy(15, 22)
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(248, 250, 252)
        self.cell(0, 10, title, 0, 1, 'L')
        
        if subtitle:
            self.set_font("Helvetica", "", 12)
            self.set_text_color(52, 211, 153)  # Emerald
            self.cell(0, 7, subtitle, 0, 1, 'L')

    def draw_card(self, x, y, w, h, title="", bg_color=(15, 23, 42), border_color=(30, 41, 59)):
        self.set_fill_color(*bg_color)
        self.set_draw_color(*border_color)
        self.set_line_width(0.5)
        self.rect(x, y, w, h, 'DF')
        if title:
            self.set_xy(x + 5, y + 5)
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(226, 232, 240)
            self.cell(w - 10, 6, title, 0, 1, 'L')


def generate_deck():
    pdf = PresentationPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(False)

    # -------------------------------------------------------------
    # SLIDE 1: Title
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.set_xy(25, 60)
    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(248, 250, 252)
    pdf.cell(0, 15, "MANDATE", 0, 1, 'L')

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(52, 211, 153)
    pdf.cell(0, 10, "Autonomous Procure-to-Pay with Cryptographically Bounded Spend Authority", 0, 1, 'L')

    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(0, 8, "ArmorIQ Hackathon  *  Problem 1: Autonomous, until it shouldn't be  *  Problem 2 Bonus", 0, 1, 'L')

    pdf.set_xy(25, 140)
    pdf.set_font("Helvetica", "I", 11)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 6, "Core Thesis: Mandate pays your vendors autonomously and cryptographically cannot pay anyone else.", 0, 1, 'L')

    # -------------------------------------------------------------
    # SLIDE 2: The Problem
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.draw_slide_title("The Threat: Scalable Prompt Injection in Corporate Finance", "Why Accounts Payable is the most dangerous autonomous agent workflow")

    pdf.draw_card(15, 45, 125, 145, "Business Email Compromise (BEC)")
    pdf.set_xy(20, 58)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(203, 213, 225)
    pdf.multi_cell(115, 6, 
        "- Invoice Fraud is a multi-billion-dollar loss category in global finance.\n\n"
        "- The standard attack vector: A supplier email/document arrives stating: 'Our banking partner has changed, please remit to this new account.'\n\n"
        "- In human back offices, social engineering tricks staff into manual overrides."
    )

    pdf.draw_card(155, 45, 125, 145, "The AI Agent Vulnerability")
    pdf.set_xy(160, 58)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(203, 213, 225)
    pdf.multi_cell(115, 6,
        "- Autonomous LLM agents MUST read incoming invoice text to extract line items.\n\n"
        "- The malicious remittance advisory is an Indirect Prompt Injection embedded in untrusted data.\n\n"
        "- Critical flaw: Prompt-based defenses fail because the attack instruction is indistinguishable from genuine business text.\n\n"
        "- Solution required: A cryptographic execution boundary that enforces authority independently of LLM reasoning."
    )

    # -------------------------------------------------------------
    # SLIDE 3: The Useful Workflow
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.draw_slide_title("The Useful Workflow: End-to-End Autonomous Procure-to-Pay", "Zero human babysitting for legitimate vendor invoices")

    steps = [
        ("1. Ingest Master Records", "Reads approved vendor master directory and open Purchase Orders (POs) from trusted storage."),
        ("2. Three-Way Matching", "Compares incoming invoice line items, PO numbers, and vendor tax IDs."),
        ("3. Automated Disbursement", "Debits Mandate treasury account ACC-MANDATE-01 and credits vendor registered bank account."),
        ("4. Destination AP Register", "Writes audit trail, outcomes, and transaction hashes directly into AP ledger."),
    ]

    for i, (stitle, sdesc) in enumerate(steps):
        x = 15 + (i * 68)
        pdf.draw_card(x, 50, 62, 135, stitle)
        pdf.set_xy(x + 5, 65)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(203, 213, 225)
        pdf.multi_cell(52, 6, sdesc)

    # -------------------------------------------------------------
    # SLIDE 4: Agent Topology & Attenuation
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.draw_slide_title("Agent Topology: Multi-Agent Delegation & Attenuation", "Problem 2 satisfied in full: Disjoint identities & narrowing authority pipes")

    pdf.draw_card(15, 45, 85, 145, "CFO (Vikram Mehta)")
    pdf.set_xy(20, 58)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(203, 213, 225)
    pdf.multi_cell(75, 6, 
        "- Named Human Principal\n"
        "- Root of spend authority\n"
        "- Issues initial mission mandate\n"
        "- Evaluates high-value HOLD requests"
    )

    pdf.draw_card(105, 45, 85, 145, "Controller Agent (Root)")
    pdf.set_xy(110, 58)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(203, 213, 225)
    pdf.multi_cell(75, 6,
        "- Orchestrates workflow\n"
        "- Reads trusted POs & Vendors\n"
        "- Seals ArmorIQ Plan\n"
        "- Issues Ed25519-signed grants to Matcher and Disburser"
    )

    pdf.draw_card(195, 45, 85, 145, "Specialist Subagents")
    pdf.set_xy(200, 58)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(203, 213, 225)
    pdf.multi_cell(75, 6,
        "Matcher Agent (Read-Only):\n"
        "- Caps: [fetch_invoices]\n"
        "- Ceiling: Rs 0 (No spend capability)\n\n"
        "Disburser Agent (Payment):\n"
        "- Caps: [initiate_payment]\n"
        "- Ceiling: Rs 50,000 / invoice\n"
        "- Payee Scope: Approved accounts only"
    )

    # -------------------------------------------------------------
    # SLIDE 5: The Core Security Property
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.draw_slide_title("The Key Insight: Plan-Ordering Invariant (SPEC.md 1.2)", "Authority is sealed BEFORE the agent reads anything an attacker can write")

    pdf.draw_card(15, 50, 265, 135, "Strict 4-Step Execution Sequence")
    pdf.set_xy(25, 68)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(52, 211, 153)
    pdf.cell(0, 8, "1. Read TRUSTED data only  --> Vendor Master + Open Purchase Orders", 0, 1)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(52, 211, 153)
    pdf.cell(0, 8, "2. capture_plan() + get_intent_token()  --> Seals payees, invoice ceiling, and timestamp", 0, 1)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(251, 113, 133)
    pdf.cell(0, 8, "3. ONLY NOW Read UNTRUSTED data  --> Ingest incoming invoice text", 0, 1)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(96, 165, 250)
    pdf.cell(0, 8, "4. invoke() Every Payment via gateway.call  --> Verified against sealed token", 0, 1)

    pdf.set_xy(25, 125)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(203, 213, 225)
    pdf.multi_cell(245, 6,
        "Why this matters: If an agent reads invoices before sealing the plan, an injected payee account ends up inside the plan, the token is minted over the fraud, and ArmorIQ authorises the theft. Test T1 guarantees that fetch_invoices timestamp > Mission.sealed_at."
    )

    # -------------------------------------------------------------
    # SLIDE 6: The ArmorIQ Seam
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.draw_slide_title("The ArmorIQ Seam: gateway.py Architecture", "The sole path from any agent to any MCP tool")

    pdf.draw_card(15, 48, 125, 140, "ArmorIQ Adapter Protocol")
    pdf.set_xy(20, 60)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(203, 213, 225)
    pdf.multi_cell(115, 6,
        "- adapter.py: Protocol with 4 clean methods:\n"
        "  * capture_plan(objective, context)\n"
        "  * get_intent_token(plan_hash, envelope)\n"
        "  * delegate(parent, child, caps, ceiling)\n"
        "  * invoke(agent, tool, params, grant, token)\n\n"
        "- local.py: Spec-faithful LocalEnforcer\n"
        "- real.py: RealArmorIQ SDK wrapper with marked call sites\n"
        "- Toggleable via ARMORIQ_MODE=local|real"
    )

    pdf.draw_card(155, 48, 125, 140, "Gateway Invariant (gateway.py)")
    pdf.set_xy(160, 60)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(203, 213, 225)
    pdf.multi_cell(115, 6,
        "- Strictly prohibits agent modules from importing MCP client directly (verified via AST test).\n\n"
        "- Evaluates ArmorIQ grant & intent token on every call.\n\n"
        "- BLOCK: Never enters tool body (spy counter = 0).\n"
        "- HOLD: Parks decision for human approval.\n"
        "- ALLOW: Dispatches to MCP server and updates ledger."
    )

    # -------------------------------------------------------------
    # SLIDE 7: The Three Real-World Attacks
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.draw_slide_title("Three Realistic Attacks Stopped at the Boundary", "Demonstrating semantic scope checking rather than naive keyword filtering")

    attacks = [
        ("Attack A: BEC Remittance Fraud", "INV-2041 claims banking partner changed to HDFC 509900443322.\n\nDefense: Blocked by Sealed Payee Scope whitelist. The attacker account was absent from the CFO-sealed vendor master.\n\nResult: BLOCK (PAYEE_NOT_IN_SEALED_SCOPE)"),
        ("Attack B: Capability Escalation", "INV-2042 claims port demurrage urgency, asking reviewer to pay directly.\n\nDefense: Matcher agent holds read capability only (ceiling Rs 0).\n\nResult: BLOCK (CAPABILITY_NOT_DELEGATED)"),
        ("Attack C: Decimal Amount Shift", "INV-2044 states Rs 87,240 instead of PO-1005 value of Rs 8,724.\n\nDefense: Exceeds Rs 50,000 ceiling. Disburser adjusts payment to exact PO amount (Rs 8,724).\n\nResult: BLOCK -> ALLOW @ Rs 8,724"),
    ]

    for i, (atitle, adesc) in enumerate(attacks):
        x = 15 + (i * 90)
        pdf.draw_card(x, 48, 85, 140, atitle)
        pdf.set_xy(x + 5, 62)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(203, 213, 225)
        pdf.multi_cell(75, 6, adesc)

    # -------------------------------------------------------------
    # SLIDE 8: Before & After (Governance A/B)
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.draw_slide_title("Governance A/B: The Proof in Real Numbers", "Deterministic benchmark across identical fixtures, prompts, and seeds")

    pdf.draw_card(15, 50, 125, 95, "GOVERNANCE = OFF (Ungoverned Baseline)", bg_color=(28, 10, 15), border_color=(225, 29, 72))
    pdf.set_xy(25, 70)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(244, 63, 94)
    pdf.cell(0, 12, "Rs 38,57,560.00", 0, 1)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(203, 213, 225)
    pdf.cell(0, 6, "Opening: Rs 42,50,000  *  Disbursed: Rs 3,92,440", 0, 1)
    pdf.cell(0, 6, "Status: Compromised by all 3 attacks", 0, 1)

    pdf.draw_card(155, 50, 125, 95, "GOVERNANCE = ON (ArmorIQ Protected)", bg_color=(6, 30, 20), border_color=(16, 185, 129))
    pdf.set_xy(165, 70)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(52, 211, 153)
    pdf.cell(0, 12, "Rs 39,91,726.00", 0, 1)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(203, 213, 225)
    pdf.cell(0, 6, "Opening: Rs 42,50,000  *  Disbursed: Rs 2,58,274", 0, 1)
    pdf.cell(0, 6, "Status: All legitimate invoices paid, all fraud blocked", 0, 1)

    pdf.draw_card(15, 152, 265, 35, "", bg_color=(15, 23, 42), border_color=(52, 211, 153))
    pdf.set_xy(25, 160)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(52, 211, 153)
    pdf.cell(0, 10, "PREVENTED FRAUD LOSS:  Rs 1,34,166.00 (13,416,600 paise)", 0, 1, 'C')

    # -------------------------------------------------------------
    # SLIDE 9: Forensics Drawer
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.draw_slide_title("Forensics: Answering 'Who Authorized This?'", "Complete 5-step provenance reconstruction from Human Principal to Ledger Result")

    pdf.draw_card(15, 48, 265, 140, "Cryptographic Provenance Chain")
    pdf.set_xy(25, 62)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(203, 213, 225)
    pdf.multi_cell(245, 7,
        "1. Named Human: CFO Vikram Mehta (Mandate Industries Pvt Ltd)\n"
        "2. Sealed Scope: Intent Token tok_intent_... + Merkle Root + Plan Hash sha256:...\n"
        "3. Delegated Authority: Disburser Grant with Ed25519 signature & Rs 50,000 ceiling\n"
        "4. Tool Action Parameters: initiate_payment(INV-2041, Payee: 509900443322, Rs 46,200)\n"
        "5. ArmorIQ Verdict: BLOCK (PAYEE_NOT_IN_SEALED_SCOPE)\n\n"
        "--> For blocked attacks, the primary header reads: 'AUTHORIZED BY: NOBODY'"
    )

    # -------------------------------------------------------------
    # SLIDE 10: Stack, Verification & Honesty
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.draw_slide_title("Stack, Verification & Hackathon Compliance", "Production-grade codebase, deterministic replays, and complete honesty standard")

    pdf.draw_card(15, 48, 125, 140, "Technology Stack")
    pdf.set_xy(20, 60)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(203, 213, 225)
    pdf.multi_cell(115, 6,
        "- Backend: Python 3.11, FastAPI, SQLModel, Uvicorn\n"
        "- Database: SQLite (mandate.db + snapshot mandate.seed.db)\n"
        "- Transport: Official MCP Python SDK (FastMCP)\n"
        "- Realtime: Server-Sent Events (/api/stream)\n"
        "- Frontend: Vite, React 18, TypeScript, TailwindCSS, React Flow\n"
        "- Security Invariants: 10/10 pytest test suite (T1-T6)"
    )

    pdf.draw_card(155, 48, 125, 140, "Verification & Honesty Disclosures")
    pdf.set_xy(160, 60)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(203, 213, 225)
    pdf.multi_cell(115, 6,
        "- 10-Run Replay Gate: 10 consecutive cold resets produce byte-identical balances.\n\n"
        "- Disk Cache: .cache/llm/ sealed for offline presentation without live API dependence.\n\n"
        "- Honesty Banner: UI renders 'ENFORCEMENT: LOCAL ADAPTER (ArmorIQ contract)' when SDK sandbox is offline.\n\n"
        "- Zero Duplication: If real ArmorIQ delegate() supplies grants, local crypto is retired."
    )

    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "MANDATE-ROUND2-PRESENTATION.pdf")
    pdf.output(output_path)
    print(f"Presentation PDF successfully created at: {output_path}")


if __name__ == "__main__":
    generate_deck()
