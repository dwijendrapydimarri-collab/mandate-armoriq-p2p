"""
MANDATE — Tool Gateway (THE ONLY PATH FROM AGENT TO TOOL)
SPEC.md 1.8: No agent module may import or invoke the MCP client directly.
Every single tool invocation passes through gateway.call or gateway.resume_held.
"""

import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel

from backend.armoriq import get_enforcer
from backend.mcp_server.client import default_mcp_client
from backend.domain import get_session, DB_PATH
from backend.models import Decision, APRecord


class ToolResult(BaseModel):
    status: str  # SUCCESS | BLOCKED | HELD | ERROR
    verdict: str  # ALLOW | HOLD | BLOCK | BYPASS
    tool: str
    data: Optional[Any] = None
    reason: Optional[str] = None
    decision_id: Optional[str] = None
    proof: Dict[str, Any] = {}


async def call(
    agent_id: str,
    tool: str,
    params: Dict[str, Any],
    mission_id: str = "mission_default",
    intent_token: Optional[str] = None,
    db_path: str = DB_PATH,
) -> ToolResult:
    """
    The sole entrypoint for agent tool calls.
    Enforces governance, persists decisions, and dispatches to MCP strictly on ALLOW.
    No global mission leakage: mission_id and intent_token are explicitly scoped.
    """
    governance_mode = os.environ.get("GOVERNANCE", "on").lower()
    enforcer = get_enforcer()

    now_iso = datetime.now(timezone.utc).isoformat()
    unique_suffix = uuid.uuid4().hex[:8]
    decision_id = f"dec_{agent_id}_{tool}_{unique_suffix}"

    # -------------------------------------------------------------
    # PATH 1: GOVERNANCE OFF (UNGONVERNED BASELINE)
    # -------------------------------------------------------------
    if governance_mode == "off":
        print(f"[GATEWAY] [GOVERNANCE=OFF BYPASS] Agent '{agent_id}' invoking '{tool}' directly.")
        bypass_decision = Decision(
            id=decision_id,
            mission_id=mission_id,
            agent_id=agent_id,
            tool=tool,
            params=json.dumps(params),
            verdict="BYPASS",
            reason="GOVERNANCE_DISABLED_BASELINE_MODE",
            proof=json.dumps({"governance": "off", "bypassed": True}),
            ts=now_iso,
        )
        with get_session(db_path) as session:
            session.add(bypass_decision)
            session.commit()

        # Dispatch tool call directly
        mcp_data = await default_mcp_client.call_tool(tool, {**params, "db_path": db_path})
        return ToolResult(
            status="SUCCESS",
            verdict="ALLOW",
            tool=tool,
            data=mcp_data,
            reason="Governance disabled",
            decision_id=decision_id,
            proof={"governance": "off"},
        )

    # -------------------------------------------------------------
    # PATH 2: GOVERNANCE ON (ARMORIQ ENFORCEMENT)
    # -------------------------------------------------------------
    grant = enforcer.get_grant(agent_id, mission_id=mission_id)
    decision = enforcer.invoke(
        agent_id=agent_id,
        tool=tool,
        params=params,
        grant=grant,
        intent_token=intent_token,
    )

    db_decision = Decision(
        id=decision_id,
        mission_id=mission_id,
        agent_id=agent_id,
        tool=tool,
        params=json.dumps(params),
        verdict=decision.verdict,
        reason=decision.reason,
        proof=json.dumps(decision.proof),
        ts=now_iso,
    )
    with get_session(db_path) as session:
        session.add(db_decision)
        session.commit()

    if decision.verdict == "ALLOW":
        print(f"[GATEWAY] [ALLOW] Dispatching Agent '{agent_id}' -> Tool '{tool}' to MCP...")
        # Dispatch to MCP Tool strictly on ALLOW
        mcp_data = await default_mcp_client.call_tool(tool, {**params, "decision_id": decision_id, "db_path": db_path})
        return ToolResult(
            status="SUCCESS",
            verdict="ALLOW",
            tool=tool,
            data=mcp_data,
            reason=decision.reason,
            decision_id=decision_id,
            proof=decision.proof,
        )


    elif decision.verdict == "HOLD":
        print(f"[GATEWAY] [HELD] Agent '{agent_id}' -> Tool '{tool}' HELD for human approval. Reason: {decision.reason}")
        if hasattr(enforcer, "register_held"):
            enforcer.register_held(decision_id, params, intent_token)
        return ToolResult(
            status="HELD",
            verdict="HOLD",
            tool=tool,
            data=None,
            reason=decision.reason,
            decision_id=decision_id,
            proof=decision.proof,
        )


    else:  # BLOCK
        print(f"[GATEWAY] [BLOCKED] Agent '{agent_id}' -> Tool '{tool}' BLOCKED. Reason: {decision.reason}")
        return ToolResult(
            status="BLOCKED",
            verdict="BLOCK",
            tool=tool,
            data=None,
            reason=decision.reason,
            decision_id=decision_id,
            proof=decision.proof,
        )


async def resume_held(
    decision_id: str,
    approver: str = "cfo",
    db_path: str = DB_PATH,
) -> ToolResult:
    """
    Resumes a previously HELD transaction following explicit human-in-the-loop approval.
    Guarantees that approved HOLD requests pass exclusively through the MCP client dispatch
    without bypassing gateway controls or minting fresh unconstrained tokens.
    """
    with get_session(db_path) as session:
        decision = session.get(Decision, decision_id)
        if not decision:
            raise ValueError(f"Decision '{decision_id}' not found.")
        if decision.verdict != "HOLD":
            raise ValueError(f"Decision '{decision_id}' has verdict '{decision.verdict}', not 'HOLD'.")

        params = json.loads(decision.params)
        tool = decision.tool
        invoice_id = params.get("invoice_id")
        amount_paise = params.get("amount_paise", 0)
        payee_account = params.get("payee_account", "")

        # Extract proof context
        proof_ctx = {}
        try:
            proof_ctx = json.loads(decision.proof)
        except Exception:
            pass
        intent_token = proof_ctx.get("intent_token")

        # 1. Re-authorize through ArmorIQ enforcer resume method
        enforcer = get_enforcer()
        auth_decision = enforcer.resume(
            decision_id=decision_id,
            approver=approver,
            expected_params=params,
            intent_token=intent_token,
        )

        if auth_decision.verdict != "ALLOW":
            print(f"[GATEWAY] [RESUME REJECTED] ArmorIQ refused to resume {decision_id}. Reason: {auth_decision.reason}")
            decision.verdict = "BLOCK"
            decision.reason = auth_decision.reason
            decision.proof = json.dumps(auth_decision.proof)
            session.add(decision)
            session.commit()
            return ToolResult(
                status="BLOCKED",
                verdict="BLOCK",
                tool=tool,
                data=None,
                reason=auth_decision.reason,
                decision_id=decision_id,
                proof=auth_decision.proof,
            )

        # 2. Dispatch to MCP Tool strictly after ArmorIQ authorization returns ALLOW
        print(f"[GATEWAY] [RESUME ALLOWED] Dispatching human-approved '{tool}' to MCP for invoice {invoice_id}...")
        mcp_data = await default_mcp_client.call_tool(tool, {**params, "decision_id": decision_id, "db_path": db_path})

        # 3. Update Decision row to ALLOW with full proof trail
        decision.verdict = "ALLOW"
        decision.reason = auth_decision.reason
        decision.proof = json.dumps(auth_decision.proof)
        session.add(decision)
        session.commit()

        # 4. Update AP record
        await default_mcp_client.call_tool("write_ap_record", {
            "invoice_id": invoice_id,
            "outcome": "PAID",
            "note": f"Approved by {approver.upper()}. Disbursed {amount_paise} paise to {payee_account}.",
            "db_path": db_path,
        })


        return ToolResult(
            status="SUCCESS",
            verdict="ALLOW",
            tool=tool,
            data=mcp_data,
            reason=auth_decision.reason,
            decision_id=decision_id,
            proof=auth_decision.proof,
        )

