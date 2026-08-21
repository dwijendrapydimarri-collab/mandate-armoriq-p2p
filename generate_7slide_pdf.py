"""
MANDATE — Official 7-Slide Presentation PDF Generator
Generates a clean 7-slide PDF document compliant with Round 2 Hackathon requirements (< 10 MB).
"""

import os


def generate_pdf(output_path: str):
    slides = [
        # Slide 1: Cover
        {
            "title": "MANDATE",
            "subtitle": "Autonomous Procure-to-Pay with a Sealed Authority Envelope",
            "bullets": [
                "Track: ArmorIQ -- Problem 1 ('Autonomous, until it shouldn't be') & Problem 2 (Delegation)",
                "Team: STELLAR STACK  |  Team ID: team-E657F05D7F45",
                "Institution: AMRITA VISHWA VIDYAPEETHAM, NAGERCOIL",
                "Core Principle: Fix Authority at Plan Time Over Trusted Data Before Ingesting Untrusted Invoices",
            ],
        },
        # Slide 2: Problem
        {
            "title": "Slide 2 -- AI Payment Automation Has a Critical Trust Gap",
            "subtitle": "Prompt injection in supplier invoices allows models to be hijacked into unauthorized payments",
            "bullets": [
                "The Danger: Invoice free-text advisories contain plausible bank change requests ('Remit to new HDFC A/C...').",
                "The Flaw: LLMs read untrusted text and directly execute disbursement tools without proving authority.",
                "Limitations of Existing Tools: Prompt filters can be bypassed; RBAC is too broad; audit logs only record after the theft.",
                "The Requirement: A deterministic security boundary that stops unauthorized payments before the tool runs.",
            ],
        },
        # Slide 3: Solution
        {
            "title": "Slide 3 -- Mandate: Pre-Mission Authority Sealing",
            "subtitle": "Transforming CFO vendor & PO data into an immutable, cryptographic Authority Envelope",
            "bullets": [
                "Phase 1 (Trusted Setup): CFO defines approved vendors, payee bank accounts, open POs, and spend ceilings.",
                "Plan Sealing: ArmorIQ captures the plan, hashes trusted facts, and mints an immutable Intent Token.",
                "Phase 2 (Untrusted Intake): Invoices and advisories are ingested only after seal and cannot mutate authority.",
                "Pre-Tool Verification: Sole gateway.py validates every MCP tool call against the sealed envelope.",
            ],
        },
        # Slide 4: Architecture & Delegation
        {
            "title": "Slide 4 -- Cryptographic Delegation Across Subagents",
            "subtitle": "Capability attenuation across Controller, Matcher, and Disburser agents",
            "bullets": [
                "Controller Agent: Owns the root mission, creates delegation grants, and coordinates workflow.",
                "Matcher Agent: Granted strictly read-only capability ('fetch_invoices'); direct spend is cryptographically blocked.",
                "Disburser Agent: Granted 'initiate_payment' scoped strictly to approved payee accounts and PO amounts.",
                "FastMCP Protocol: Native FastMCP tool server executes financial mutations only upon gateway ALLOW verdict.",
            ],
        },
        # Slide 5: Live Defense Evidence
        {
            "title": "Slide 5 -- Deterministic Defense Against Live Attacks",
            "subtitle": "Proven headline balances: Governed Rs 39,91,726 vs Ungoverned Rs 38,57,560",
            "bullets": [
                "Attack A (Bank Shift): Untrusted payee 509900443322 blocked instantly -> Prevented loss: Rs 46,200.00.",
                "Attack B (Capability Bypass): Matcher direct payment blocked with CAPABILITY_NOT_DELEGATED.",
                "Attack C (10x Amount Spike): Over-PO payment blocked with AMOUNT_EXCEEDS_PO_AND_CEILING.",
                "Legitimate Over-Ceiling: Rs 1,45,000 payment paused for human CFO review and resumed via ArmorIQ re-auth.",
            ],
        },
        # Slide 6: Judge Challenge Mode
        {
            "title": "Slide 6 -- Judge Challenge Mode: Live Proving Ground",
            "subtitle": "Deployable, zero-CLI interactive proving ground for hackathon evaluators",
            "bullets": [
                "Sandbox Isolation: Evaluators create independent procurement missions with custom vendors, POs, and ceilings.",
                "Real Gateway Path: Custom Security Probes dispatch typed proposals directly through gateway.py -> ArmorIQ.",
                "Visual Forensics: Trust Boundary Map highlights exact authority conflicts; Counterfactual Proof displays prevented losses.",
                "Authority Cliff Replay: Visualizes execution halting at the boundary with header 'AUTHORIZED BY: NOBODY'.",
            ],
        },
        # Slide 7: Impact & Honest Disclosure
        {
            "title": "Slide 7 -- Economic Impact & Submission Disclosure",
            "subtitle": "Team STELLAR STACK -- AMRITA VISHWA VIDYAPEETHAM, NAGERCOIL",
            "bullets": [
                "Financial Protection: Zero balance drift under adversarial attack; Rs 1,34,166.00 in total fraud loss prevented.",
                "Zero Secret Leakage: Private signing keys and credentials remain strictly server-side inside Python backend.",
                "Transparent Architecture: LocalEnforcer simulation implements 100% generic policy matching the ArmorIQ contract.",
                "Verified Test Suite: 28/28 automated invariant & Judge Mode tests passing in continuous integration.",
            ],
        },
    ]


    # Generate minimal conforming PDF 1.4
    objects = []
    # 1: Catalog, 2: Pages, 3..: Page objects, Content streams, Fonts

    font_obj_idx = 3
    page_count = len(slides)

    # We will build page objects and stream objects
    page_obj_indices = []
    content_obj_indices = []

    current_idx = 4
    for _ in range(page_count):
        page_obj_indices.append(current_idx)
        content_obj_indices.append(current_idx + 1)
        current_idx += 2

    pdf_output = bytearray()
    offsets = {}

    def write_obj(idx, content_bytes):
        offsets[idx] = len(pdf_output)
        pdf_output.extend(f"{idx} 0 obj\n".encode("latin1"))
        pdf_output.extend(content_bytes)
        pdf_output.extend(b"\nendobj\n")

    # Header
    pdf_output.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    # Obj 1: Catalog
    write_obj(1, b"<< /Type /Catalog /Pages 2 0 R >>")

    # Obj 2: Pages
    kids_refs = " ".join(f"{idx} 0 R" for idx in page_obj_indices)
    write_obj(2, f"<< /Type /Pages /Kids [{kids_refs}] /Count {page_count} >>".encode("latin1"))

    # Obj 3: Font
    write_obj(3, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    # Generate Page & Content Objects
    for i, slide in enumerate(slides):
        p_idx = page_obj_indices[i]
        c_idx = content_obj_indices[i]

        title = (
            slide["title"]
            .replace("\u2014", "--")
            .replace("\u2019", "'")
            .replace("\u2018", "'")
            .replace("\u20b9", "Rs ")
            .replace("(", "[")
            .replace(")", "]")
        )
        subtitle = (
            slide["subtitle"]
            .replace("\u2014", "--")
            .replace("\u2019", "'")
            .replace("\u2018", "'")
            .replace("\u20b9", "Rs ")
            .replace("(", "[")
            .replace(")", "]")
        )

        # Content stream (792 x 612 Landscape US Letter)
        # Background: dark slate #0f172a
        stream_lines = [
            "q",
            "0.06 0.09 0.16 rg",  # dark slate bg
            "0 0 792 612 re f",  # fill rect
            "0.12 0.16 0.24 rg",  # card container bg
            "36 36 720 540 re f",
            "0.2 0.27 0.38 RG",  # border
            "1.5 w",
            "36 36 720 540 re S",
            # Header accent line (emerald #10b981)
            "0.06 0.72 0.51 RG",
            "3 w",
            "56 525 m 736 525 l S",
            # Text elements
            "BT",
            "/F1 20 Tf",
            "0.94 0.96 0.98 rg",  # White title
            "56 540 Td",
            f"({title}) Tj",
            "ET",
            "BT",
            "/F1 12 Tf",
            "0.58 0.64 0.72 rg",  # Slate subtitle
            "56 502 Td",
            f"({subtitle}) Tj",
            "ET",
        ]

        # Bullets
        y_pos = 450
        for b in slide["bullets"]:
            clean_bullet = (
                b.replace("\u2014", "--")
                .replace("\u2019", "'")
                .replace("\u2018", "'")
                .replace("\u20b9", "Rs ")
                .replace("(", "[")
                .replace(")", "]")
            )
            stream_lines.extend(
                [
                    "BT",
                    "/F1 11 Tf",
                    "0.06 0.72 0.51 rg",  # emerald bullet dot
                    f"60 {y_pos} Td",
                    "(>) Tj",
                    "ET",
                    "BT",
                    "/F1 11 Tf",
                    "0.85 0.88 0.92 rg",  # text
                    f"76 {y_pos} Td",
                    f"({clean_bullet}) Tj",
                    "ET",
                ]
            )
            y_pos -= 42


        # Slide Number Footer
        stream_lines.extend(
            [
                "BT",
                "/F1 9 Tf",
                "0.4 0.45 0.55 rg",
                f"680 50 Td",
                f"(Slide {i+1} of 7) Tj",
                "ET",
                "BT",
                "/F1 9 Tf",
                "0.4 0.45 0.55 rg",
                "56 50 Td",
                "(MANDATE -- ArmorIQ Authority Envelope for Autonomous P2P) Tj",
                "ET",
                "Q",
            ]
        )

        stream_data = "\n".join(stream_lines).encode("latin1")
        stream_len = len(stream_data)


        # Write Page Object
        page_dict = f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 792 612] /Contents {c_idx} 0 R /Resources << /Font << /F1 3 0 R >> >> >>"
        write_obj(p_idx, page_dict.encode("latin1"))

        # Write Content Object
        content_dict = f"<< /Length {stream_len} >>\nstream\n".encode("latin1") + stream_data + b"\nendstream"
        write_obj(c_idx, content_dict)

    # Xref Table
    xref_offset = len(pdf_output)
    total_objs = current_idx
    pdf_output.extend(f"xref\n0 {total_objs}\n0000000000 65535 f \n".encode("latin1"))
    for idx in range(1, total_objs):
        offset_val = offsets.get(idx, 0)
        pdf_output.extend(f"{offset_val:010d} 00000 n \n".encode("latin1"))

    # Trailer
    pdf_output.extend(
        f"trailer\n<< /Size {total_objs} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin1")
    )

    with open(output_path, "wb") as f:
        f.write(pdf_output)

    print(f"Generated {output_path} ({len(pdf_output)} bytes)")


if __name__ == "__main__":
    generate_pdf("MANDATE-ROUND2-PRESENTATION.pdf")
