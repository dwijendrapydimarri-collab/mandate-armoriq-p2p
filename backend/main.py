"""
MANDATE — FastAPI Backend Application
Handles REST endpoints, state inspection, database reset, human-in-the-loop approvals,
mission execution triggers, and real-time SSE streaming.
"""

import os
import json
import asyncio
from typing import Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlmodel import select

from pydantic import BaseModel, Field as PydanticField
from typing import Optional, List, Dict, Any

from backend import gateway
from backend.armoriq import get_enforcer
from backend.domain import (
    get_session,
    DB_PATH,
    get_scenario_db_path,
    init_scenario_db,
    domain_write_ap_record,
)

from backend.models import (
    BankAccount,
    Vendor,
    PurchaseOrder,
    Invoice,
    Payment,
    LedgerEntry,
    Mission,
    Delegation,
    Decision,
    APRecord,
    ScenarioMetadata,
)
from backend.seed import reset_to_seed
from backend.agents.controller import run_mandate_mission

app = FastAPI(title="MANDATE Mission Control & Judge Sandbox", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


ALLOWED_PROBE_TOOLS = {
    "initiate_payment",
    "fetch_invoices",
    "get_vendor_master",
    "list_open_purchase_orders",
    "write_ap_record",
}


# =====================================================================
# REQUEST / RESPONSE SCHEMAS FOR JUDGE MODE
# =====================================================================

class NewScenarioRequest(BaseModel):
    scenario_id: Optional[str] = None
    objective: Optional[str] = "Judge Sandbox Procurement Mission"
    opening_balance_paise: Optional[int] = 425000000


class VendorInput(BaseModel):
    id: str
    name: str
    bank_account: str
    ifsc: str = "ICIC0000047"
    approved: bool = True


class PurchaseOrderInput(BaseModel):
    id: str
    vendor_id: str
    amount_paise: int
    description: Optional[str] = ""


class CFOSetupRequest(BaseModel):
    scenario_id: str
    vendors: List[VendorInput] = []
    purchase_orders: List[PurchaseOrderInput] = []
    per_invoice_ceiling_paise: int = 5000000
    mission_ceiling_paise: int = 30000000


class SealScenarioRequest(BaseModel):
    scenario_id: str
    objective: Optional[str] = None


class InvoiceInput(BaseModel):
    id: str
    vendor_id: str
    po_id: str
    stated_amount_paise: int
    raw_text: Optional[str] = ""


class InvoiceIntakeRequest(BaseModel):
    scenario_id: str
    invoices: List[InvoiceInput]


class ProbeRequest(BaseModel):
    scenario_id: str
    agent_id: str = "disburser-agent"
    tool: str = "initiate_payment"
    params: Dict[str, Any]


class RunScenarioRequest(BaseModel):
    scenario_id: str
    auto_approve_held: bool = True


# =====================================================================
# CANONICAL / BASELINE ENDPOINTS
# =====================================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "app": "mandate",
        "version": "1.0.0",
        "governance_mode": os.environ.get("GOVERNANCE", "on"),
        "armoriq_mode": os.environ.get("ARMORIQ_MODE", "local"),
    }



@app.get("/api/state")
def get_state(scenario_id: Optional[str] = Query(None)):
    target_db = get_scenario_db_path(scenario_id)
    if not os.path.exists(target_db):
        raise HTTPException(status_code=404, detail="Scenario database not found")

    with get_session(target_db) as session:
        accounts = session.exec(select(BankAccount)).all()
        vendors = session.exec(select(Vendor)).all()
        pos = session.exec(select(PurchaseOrder)).all()
        invoices = session.exec(select(Invoice)).all()
        payments = session.exec(select(Payment)).all()
        ledger = session.exec(select(LedgerEntry)).all()
        missions = session.exec(select(Mission)).all()
        delegations = session.exec(select(Delegation)).all()
        decisions = session.exec(select(Decision)).all()
        ap_records = session.exec(select(APRecord)).all()
        meta = session.exec(select(ScenarioMetadata)).first()

        return {
            "scenario_id": scenario_id or "canonical",
            "metadata": meta.model_dump() if meta else None,
            "accounts": [a.model_dump() for a in accounts],
            "vendors": [v.model_dump() for v in vendors],
            "purchase_orders": [p.model_dump() for p in pos],
            "invoices": [i.model_dump() for i in invoices],
            "payments": [p.model_dump() for p in payments],
            "ledger": [l.model_dump() for l in ledger],
            "missions": [m.model_dump() for m in missions],
            "delegations": [d.model_dump() for d in delegations],
            "decisions": [d.model_dump() for d in decisions],
            "ap_records": [r.model_dump() for r in ap_records],
        }


@app.post("/api/reset")
def reset_state():
    reset_to_seed()
    return {"status": "reset_success"}


@app.post("/api/run")
async def trigger_run(
    governance: str = Query("on", enum=["on", "off"]),
    auto_approve: bool = Query(True),
):
    os.environ["GOVERNANCE"] = governance.lower()
    res = await run_mandate_mission(
        objective="Clear this week's vendor invoices",
        auto_approve_held=auto_approve,
    )
    return res


@app.post("/api/approve/{decision_id}")
async def approve_decision(decision_id: str, scenario_id: Optional[str] = Query(None)):
    """
    CFO Approves a HELD decision.
    Resumes payment strictly through gateway.resume_held() without minting a fresh unrestricted token.
    """
    target_db = get_scenario_db_path(scenario_id)
    try:
        tool_res = await gateway.resume_held(decision_id, approver="cfo", db_path=target_db)
        return {"status": "approved", "payment": tool_res.data, "verdict": tool_res.verdict, "reason": tool_res.reason}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/reject/{decision_id}")
def reject_decision(decision_id: str, scenario_id: Optional[str] = Query(None)):
    """
    CFO Rejects a HELD decision.
    Leaves bank balance untouched and logs rejection in AP record.
    """
    target_db = get_scenario_db_path(scenario_id)
    with get_session(target_db) as session:
        decision = session.get(Decision, decision_id)
        if not decision:
            raise HTTPException(status_code=404, detail="Decision not found")

        params = json.loads(decision.params)
        invoice_id = params.get("invoice_id")

        decision.verdict = "BLOCK"
        decision.reason = "REJECTED_BY_CFO_HUMAN_IN_THE_LOOP"
        session.add(decision)
        session.commit()

        domain_write_ap_record(
            invoice_id=invoice_id,
            outcome="REJECTED",
            note="Rejected by CFO during approval gate.",
            db_path=target_db,
        )

        return {"status": "rejected", "decision_id": decision_id}


# =====================================================================
# JUDGE MODE ENDPOINTS (SPEC.md 1.14)
# =====================================================================

@app.post("/api/scenario/new")
def create_new_scenario(req: NewScenarioRequest):
    """
    Creates a fresh, isolated SQLite sandbox workspace for a Judge Mode scenario.
    Zero connection to real rails, zero mutation of canonical seed data.
    """
    if req.opening_balance_paise is not None and req.opening_balance_paise <= 0:
        raise HTTPException(status_code=400, detail="Opening balance must be a positive integer in paise.")

    scen_id = req.scenario_id or f"scen_{uuid.uuid4().hex[:8]}"
    opening_bal = req.opening_balance_paise if req.opening_balance_paise is not None else 425000000
    objective = req.objective or "Judge Sandbox Procurement Mission"

    init_scenario_db(
        scenario_id=scen_id,
        objective=objective,
        opening_balance_paise=opening_bal,
    )

    return {
        "scenario_id": scen_id,
        "status": "CFO_SETUP",
        "objective": objective,
        "opening_balance_paise": opening_bal,
    }


@app.post("/api/scenario/cfo-setup")
def cfo_setup(req: CFOSetupRequest):
    """
    Phase 1 (Pre-Seal): Judge acting as CFO creates trusted vendors, approved payees,
    open POs, per-invoice ceiling, and mission ceiling.
    Strict Rule: Rejects with 400 if mission is already sealed.
    """
    if req.per_invoice_ceiling_paise <= 0 or req.mission_ceiling_paise <= 0:
        raise HTTPException(status_code=400, detail="Ceilings must be positive integers in paise.")

    vendor_ids = [v.id.strip() for v in req.vendors if v.id]
    if len(vendor_ids) != len(set(vendor_ids)):
        raise HTTPException(status_code=400, detail="Duplicate vendor ID detected in setup.")

    for v in req.vendors:
        if not v.id.strip() or not v.bank_account.strip():
            raise HTTPException(status_code=400, detail="Vendor ID and bank account must not be empty.")

    po_ids = [p.id.strip() for p in req.purchase_orders if p.id]
    if len(po_ids) != len(set(po_ids)):
        raise HTTPException(status_code=400, detail="Duplicate purchase order ID detected in setup.")

    for p in req.purchase_orders:
        if p.amount_paise <= 0:
            raise HTTPException(status_code=400, detail=f"Purchase order '{p.id}' amount must be positive.")
        if p.vendor_id not in vendor_ids:
            raise HTTPException(status_code=400, detail=f"Purchase order '{p.id}' references unknown vendor '{p.vendor_id}'.")

    target_db = get_scenario_db_path(req.scenario_id)
    if not os.path.exists(target_db):
        raise HTTPException(status_code=404, detail=f"Scenario '{req.scenario_id}' not found.")

    with get_session(target_db) as session:
        meta = session.get(ScenarioMetadata, req.scenario_id)
        if not meta:
            raise HTTPException(status_code=404, detail="Scenario metadata missing.")

        if meta.status != "CFO_SETUP":
            raise HTTPException(
                status_code=400,
                detail="Cannot modify trusted setup after mission seal. Create a new mission.",
            )

        # Clear existing unsealed setup if updating
        existing_vendors = session.exec(select(Vendor)).all()
        for v in existing_vendors:
            session.delete(v)

        existing_pos = session.exec(select(PurchaseOrder)).all()
        for p in existing_pos:
            session.delete(p)

        # Add trusted vendors
        for v_in in req.vendors:
            session.add(Vendor(
                id=v_in.id,
                name=v_in.name,
                bank_account=v_in.bank_account,
                ifsc=v_in.ifsc,
                approved=v_in.approved,
            ))

        # Add trusted purchase orders
        for po_in in req.purchase_orders:
            session.add(PurchaseOrder(
                id=po_in.id,
                vendor_id=po_in.vendor_id,
                amount_paise=po_in.amount_paise,
                status="OPEN",
                description=po_in.description or "",
            ))

        # Update ceilings
        meta.per_invoice_ceiling_paise = req.per_invoice_ceiling_paise
        meta.mission_ceiling_paise = req.mission_ceiling_paise
        session.add(meta)
        session.commit()

        return {
            "scenario_id": req.scenario_id,
            "status": "CFO_SETUP",
            "vendors_count": len(req.vendors),
            "purchase_orders_count": len(req.purchase_orders),
            "ceilings": {
                "per_invoice_ceiling_paise": req.per_invoice_ceiling_paise,
                "mission_ceiling_paise": req.mission_ceiling_paise,
            },
        }


@app.post("/api/scenario/seal")
def seal_scenario(req: SealScenarioRequest):
    """
    Mission Seal: Freezes trusted records, computes plan hash, mints ArmorIQ intent token,
    issues cryptographic delegations, and renders the immutable Authority Envelope.
    """
    target_db = get_scenario_db_path(req.scenario_id)
    if not os.path.exists(target_db):
        raise HTTPException(status_code=404, detail=f"Scenario '{req.scenario_id}' not found.")

    with get_session(target_db) as session:
        meta = session.get(ScenarioMetadata, req.scenario_id)
        if not meta:
            raise HTTPException(status_code=404, detail="Scenario metadata missing.")

        if meta.status == "SEALED" or meta.status == "READY_FOR_EXECUTION":
            raise HTTPException(status_code=400, detail="Mission is already sealed and immutable.")

        vendors = session.exec(select(Vendor)).all()
        pos = session.exec(select(PurchaseOrder)).all()

        approved_vendors = [v for v in vendors if v.approved and v.bank_account and v.bank_account.strip()]
        if not approved_vendors:
            raise HTTPException(status_code=400, detail="Must configure at least one approved vendor with a valid bank account before sealing.")

        allowed_payees = [v.bank_account for v in approved_vendors]
        per_inv_ceiling = meta.per_invoice_ceiling_paise
        mission_ceiling = meta.mission_ceiling_paise

        envelope = {
            "allowed_payees": allowed_payees,
            "per_invoice_ceiling_paise": per_inv_ceiling,
            "mission_ceiling_paise": mission_ceiling,
            "open_pos_count": len(pos),
        }

        objective = req.objective or meta.objective
        enforcer = get_enforcer()

        # Capture Plan & Mint Intent Token
        plan_result = enforcer.capture_plan(
            objective,
            {
                "vendors": [v.model_dump() for v in vendors],
                "open_pos": [p.model_dump() for p in pos],
                "ceilings": {"per_invoice_ceiling_paise": per_inv_ceiling, "mission_ceiling_paise": mission_ceiling},
            }
        )
        token_result = enforcer.get_intent_token(plan_result.plan_hash, envelope)

        # Issue Delegations
        matcher_grant = enforcer.delegate(
            mission_id=req.scenario_id,
            parent_agent="controller-agent",
            child_agent="matcher-agent",
            capabilities=["fetch_invoices"],
            ceiling_paise=0,
            payee_scope=[],
            intent_token=token_result.intent_token,
        )
        disburser_grant = enforcer.delegate(
            mission_id=req.scenario_id,
            parent_agent="controller-agent",
            child_agent="disburser-agent",
            capabilities=["initiate_payment"],
            ceiling_paise=per_inv_ceiling,
            payee_scope=allowed_payees,
            intent_token=token_result.intent_token,
        )

        # Persist Mission & Delegations in Scenario DB
        mission_record = Mission(
            id=req.scenario_id,
            objective=objective,
            intent_token=token_result.intent_token,
            plan_hash=token_result.plan_hash,
            merkle_root=token_result.merkle_root,
            status="SEALED",
            sealed_at=token_result.sealed_at,
        )
        session.add(mission_record)

        session.add(Delegation(
            id=matcher_grant.grant_id,
            mission_id=req.scenario_id,
            parent_agent="controller-agent",
            child_agent="matcher-agent",
            capabilities=json.dumps(matcher_grant.capabilities),
            ceiling_paise=matcher_grant.ceiling_paise,
            payee_scope=json.dumps(matcher_grant.payee_scope),
            signature=matcher_grant.signature,
        ))
        session.add(Delegation(
            id=disburser_grant.grant_id,
            mission_id=req.scenario_id,
            parent_agent="controller-agent",
            child_agent="disburser-agent",
            capabilities=json.dumps(disburser_grant.capabilities),
            ceiling_paise=disburser_grant.ceiling_paise,
            payee_scope=json.dumps(disburser_grant.payee_scope),
            signature=disburser_grant.signature,
        ))

        # Update Scenario Metadata
        meta.status = "SEALED"
        meta.plan_hash = token_result.plan_hash
        meta.intent_token = token_result.intent_token
        meta.sealed_at = token_result.sealed_at
        session.add(meta)
        session.commit()

        armoriq_mode = os.environ.get("ARMORIQ_MODE", "local")
        return {
            "scenario_id": req.scenario_id,
            "status": "SEALED",
            "objective": objective,
            "plan_hash": token_result.plan_hash,
            "intent_token": token_result.intent_token,
            "merkle_root": token_result.merkle_root,
            "sealed_at": token_result.sealed_at,
            "envelope": envelope,
            "proof": {
                "enforcement_mode": armoriq_mode,
                "proof_type": "LOCAL_DETERMINISTIC_HASH" if armoriq_mode == "local" else "ARMORIQ_CLOUD_PROOF",
                "disclaimer": "LOCAL ADAPTER SIMULATION — NOT AN ARMORIQ CLOUD RECEIPT" if armoriq_mode == "local" else "VERIFIED BY ARMORIQ SDK",
                "plan_hash": token_result.plan_hash,
                "sealed_at": token_result.sealed_at,
            },
        }


@app.post("/api/scenario/invoice-intake")
def invoice_intake(req: InvoiceIntakeRequest):
    """
    Phase 2 (Post-Seal): Ingests untrusted invoices with arbitrary advisory text.
    Strict Rule: Invoices are recorded with source='JUDGE_INTAKE' and CANNOT mutate trusted records.
    """
    inv_ids = [inv.id.strip() for inv in req.invoices if inv.id]
    if len(inv_ids) != len(set(inv_ids)):
        raise HTTPException(status_code=400, detail="Duplicate invoice ID detected in intake.")

    for inv in req.invoices:
        if not inv.id.strip() or not inv.vendor_id.strip() or not inv.po_id.strip():
            raise HTTPException(status_code=400, detail="Invoice ID, vendor ID, and PO ID must not be empty.")
        if inv.stated_amount_paise <= 0:
            raise HTTPException(status_code=400, detail=f"Invoice '{inv.id}' stated amount must be positive.")

    target_db = get_scenario_db_path(req.scenario_id)
    if not os.path.exists(target_db):
        raise HTTPException(status_code=404, detail=f"Scenario '{req.scenario_id}' not found.")

    with get_session(target_db) as session:
        meta = session.get(ScenarioMetadata, req.scenario_id)
        if not meta:
            raise HTTPException(status_code=404, detail="Scenario metadata missing.")

        if meta.status not in ["SEALED", "READY_FOR_EXECUTION"]:
            raise HTTPException(
                status_code=400,
                detail="Invoices can only be ingested AFTER mission has been sealed (Phase 2).",
            )

        # Ingest untrusted invoices
        for inv_in in req.invoices:
            session.add(Invoice(
                id=inv_in.id,
                vendor_id=inv_in.vendor_id,
                po_id=inv_in.po_id,
                stated_amount_paise=inv_in.stated_amount_paise,
                raw_text=inv_in.raw_text or "",
                source="JUDGE_INTAKE",
            ))

        meta.status = "READY_FOR_EXECUTION"
        session.add(meta)
        session.commit()

        return {
            "scenario_id": req.scenario_id,
            "status": "READY_FOR_EXECUTION",
            "invoices_added": len(req.invoices),
            "invoices": [inv.model_dump() for inv in req.invoices],
        }


@app.post("/api/scenario/probe")
async def security_probe(req: ProbeRequest):
    """
    Security Probe (SPEC.md 1.14):
    Allows a judge to send typed test tool proposals through the real gateway.py path.
    Labeled 'TEST PROPOSAL — NOT AN LLM DECISION'.
    Provides Counterfactual Ledger Proof for BLOCK and HOLD verdicts.
    """
    if req.tool not in ALLOWED_PROBE_TOOLS:
        raise HTTPException(
            status_code=400,
            detail=f"Disallowed probe tool '{req.tool}'. Only registered MCP tools are permitted: {sorted(list(ALLOWED_PROBE_TOOLS))}",
        )

    if req.tool == "initiate_payment":
        amount = req.params.get("amount_paise")
        if amount is None or not isinstance(amount, (int, float)) or int(amount) <= 0:
            raise HTTPException(status_code=400, detail="Payment probe amount_paise must be a positive integer.")
        payee = req.params.get("payee_account")
        if not payee or not str(payee).strip():
            raise HTTPException(status_code=400, detail="Payment probe payee_account must not be empty.")

    target_db = get_scenario_db_path(req.scenario_id)
    if not os.path.exists(target_db):
        raise HTTPException(status_code=404, detail=f"Scenario '{req.scenario_id}' not found.")

    with get_session(target_db) as session:
        meta = session.get(ScenarioMetadata, req.scenario_id)
        if not meta:
            raise HTTPException(status_code=404, detail="Scenario metadata missing.")

        if meta.status == "CFO_SETUP":
            raise HTTPException(status_code=400, detail="Cannot run security probe before mission is sealed.")

        intent_token = meta.intent_token

    # Dispatch proposal through the exact sole gateway (always governed)
    tool_res = await gateway.call(
        agent_id=req.agent_id,
        tool=req.tool,
        params=req.params,
        mission_id=req.scenario_id,
        intent_token=intent_token,
        db_path=target_db,
    )

    # Compute counterfactual projection on BLOCK/HOLD
    counterfactual = None
    if tool_res.verdict in ["BLOCK", "HOLD"] and req.tool == "initiate_payment":
        amount_paise = int(req.params.get("amount_paise", 0))
        payee_account = str(req.params.get("payee_account", "UNKNOWN"))
        counterfactual = {
            "projected_delta_paise": -amount_paise,
            "destination_account": payee_account,
            "status": "COUNTERFACTUAL — NOT EXECUTED",
            "prevented_loss_paise": amount_paise,
        }

    return {
        "scenario_id": req.scenario_id,
        "type": "TEST PROPOSAL — NOT AN LLM DECISION",
        "status": tool_res.status,
        "verdict": tool_res.verdict,
        "reason": tool_res.reason,
        "decision_id": tool_res.decision_id,
        "data": tool_res.data,
        "proof": tool_res.proof,
        "counterfactual": counterfactual,
    }


@app.post("/api/scenario/run")

async def run_scenario_mission(req: RunScenarioRequest):
    """
    Executes the full autonomous multi-agent procurement mission against the judge's scenario sandbox.
    """
    target_db = get_scenario_db_path(req.scenario_id)
    if not os.path.exists(target_db):
        raise HTTPException(status_code=404, detail=f"Scenario '{req.scenario_id}' not found.")

    with get_session(target_db) as session:
        meta = session.get(ScenarioMetadata, req.scenario_id)
        if not meta or meta.status == "CFO_SETUP":
            raise HTTPException(status_code=400, detail="Must seal scenario before running mission.")
        objective = meta.objective

    res = await run_mandate_mission(
        objective=objective,
        mission_id=req.scenario_id,
        auto_approve_held=req.auto_approve_held,
        db_path=target_db,
    )
    return res


@app.get("/api/stream")
async def sse_stream(scenario_id: Optional[str] = Query(None)):
    """
    Server-Sent Events stream for live Mission Control updates.
    """
    target_db = get_scenario_db_path(scenario_id)

    async def event_generator():
        last_decision_count = 0
        while True:
            try:
                if os.path.exists(target_db):
                    with get_session(target_db) as session:
                        decisions = session.exec(select(Decision)).all()
                        if len(decisions) != last_decision_count:
                            last_decision_count = len(decisions)
                            state_data = get_state(scenario_id)
                            payload = f"data: {json.dumps(state_data)}\n\n"
                            yield payload
            except Exception:
                pass
            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Mount static frontend production build if available
from fastapi.staticfiles import StaticFiles

DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.exists(DIST_DIR):
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="frontend")


