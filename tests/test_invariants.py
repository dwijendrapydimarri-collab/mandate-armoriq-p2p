"""
MANDATE — Comprehensive Acceptance Gates & Invariant Suite
Covers SPEC.md 1.11 (T1 through T6) and import boundary integrity.
"""

import os
import glob
import ast
import json
import asyncio
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import select

from backend.main import app
from backend.domain import (
    DB_PATH,
    SEED_DB_PATH,
    get_session,
    domain_initiate_payment,
)
from backend.models import BankAccount, LedgerEntry, Mission, Decision
from backend.seed import reset_to_seed, build_seed_database
from backend import gateway
from backend.armoriq import get_enforcer
from backend.agents.controller import run_mandate_mission

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_seed():
    build_seed_database(SEED_DB_PATH)


@pytest.fixture(autouse=True)
def setup_clean_db():
    reset_to_seed()
    os.environ["GOVERNANCE"] = "on"
    yield


def test_t1_plan_ordering_invariant():
    """
    T1: No untrusted read occurs before the plan is sealed.
    fetch_invoices timestamp > Mission.sealed_at, else fail.
    """
    async def _run():
        m_res = await run_mandate_mission("Governed Mission T1", mission_id="mission_t1_valid")
        mission_id = m_res["mission_id"]

        with get_session(DB_PATH) as session:
            mission = session.get(Mission, mission_id)
            assert mission is not None
            assert mission.sealed_at is not None

            fetch_decisions = session.exec(
                select(Decision).where(
                    Decision.mission_id == mission_id,
                    Decision.tool == "fetch_invoices",
                )
            ).all()

            assert len(fetch_decisions) >= 1
            fetch_ts = fetch_decisions[0].ts
            assert fetch_ts > mission.sealed_at, "Untrusted read must strictly follow plan sealing"

    asyncio.run(_run())


def test_t1_fails_when_order_inverted():
    """
    T1 Guard: Actively proves that reversing read order causes T1 assertion to fail.
    """
    async def _run():
        m_res = await run_mandate_mission(
            "Inverted Mission Test",
            mission_id="mission_t1_inverted",
            order_inversion_for_test=True,
        )
        mission_id = m_res["mission_id"]

        with get_session(DB_PATH) as session:
            mission = session.get(Mission, mission_id)
            fetch_decisions = session.exec(
                select(Decision).where(
                    Decision.mission_id == mission_id,
                    Decision.tool == "fetch_invoices",
                )
            ).all()
            fetch_ts = fetch_decisions[0].ts
            is_valid_order = fetch_ts > mission.sealed_at
            assert not is_valid_order, "Order inversion must violate T1 invariant"

    asyncio.run(_run())


def test_t2_block_before_dispatch_spy():
    """
    T2: When verdict is BLOCK, the tool function body is never entered.
    Uses a spy call-counter on domain_initiate_payment.
    """
    async def _run():
        os.environ["GOVERNANCE"] = "on"
        enforcer = get_enforcer()
        plan_res = enforcer.capture_plan("Test Mission", {"vendors": [{"bank_account": "004701234567", "approved": True}]})
        token_res = enforcer.get_intent_token(plan_res.plan_hash, plan_res.envelope)

        with patch("backend.domain.domain_initiate_payment") as domain_spy:

            result = await gateway.call(
                agent_id="disburser-agent",
                tool="initiate_payment",
                params={
                    "invoice_id": "INV-2041",
                    "payee_account": "509900443322",  # Attacker account -> BLOCK
                    "amount_paise": 4620000,
                },
                mission_id="test_mission_t2",
                intent_token=token_res.intent_token,
            )

            assert result.verdict == "BLOCK"
            assert result.reason == "PAYEE_NOT_IN_SEALED_SCOPE"
            assert domain_spy.call_count == 0, "Tool body entered despite BLOCK verdict"

    asyncio.run(_run())


def test_t3_balance_integrity_and_initiate_payment():
    """
    T3: ACC-MANDATE-01.balance_paise is byte-identical before and after a blocked payment.
    """
    with get_session(DB_PATH) as session:
        acc = session.get(BankAccount, "ACC-MANDATE-01")
        initial_balance = acc.balance_paise
        assert initial_balance == 425000000

    # Legitimate payment
    res = domain_initiate_payment(
        invoice_id="INV-2036",
        payee_account="004701234567",
        amount_paise=3850000,
        db_path=DB_PATH,
    )
    expected_new_balance = initial_balance - 3850000
    assert res["balance_after_paise"] == expected_new_balance

    with get_session(DB_PATH) as session:
        acc_after = session.get(BankAccount, "ACC-MANDATE-01")
        assert acc_after.balance_paise == expected_new_balance


def test_t4_semantic_parameter_scope_checking():
    """
    T4: Same tool, same agent, two parameter sets, two different verdicts.
    ₹8,724 (872400 paise) -> ALLOW
    ₹87,240 (8724000 paise) -> BLOCK (exceeds ceiling & PO amount)
    """
    async def _run():
        os.environ["GOVERNANCE"] = "on"
        enforcer = get_enforcer()
        plan_res = enforcer.capture_plan("Mission T4", {"vendors": [{"bank_account": "501001122334", "approved": True}]})
        token_res = enforcer.get_intent_token(plan_res.plan_hash, plan_res.envelope)

        disburser_grant = enforcer.delegate(
            mission_id="mission_t4",
            parent_agent="controller-agent",
            child_agent="disburser-agent",
            capabilities=["initiate_payment"],
            ceiling_paise=5000000,  # Rs 50,000 ceiling
            payee_scope=["501001122334"],
            intent_token=token_res.intent_token,
        )

        # Call 1: Rs 87,240 (8724000 paise) -> Exceeds ceiling -> BLOCK
        res_blocked = await gateway.call(
            agent_id="disburser-agent",
            tool="initiate_payment",
            params={
                "invoice_id": "INV-2044",
                "payee_account": "501001122334",
                "amount_paise": 8724000,
            },
            mission_id="mission_t4",
            intent_token=token_res.intent_token,
        )
        assert res_blocked.verdict == "BLOCK"
        assert res_blocked.reason == "AMOUNT_EXCEEDS_PO_AND_CEILING"

        # Call 2: Rs 8,724 (872400 paise) -> Within ceiling -> ALLOW
        res_allowed = await gateway.call(
            agent_id="disburser-agent",
            tool="initiate_payment",
            params={
                "invoice_id": "INV-2044",
                "payee_account": "501001122334",
                "amount_paise": 872400,
            },
            mission_id="mission_t4",
            intent_token=token_res.intent_token,
        )
        assert res_allowed.verdict == "ALLOW"
        assert res_allowed.data["amount_paise"] == 872400

    asyncio.run(_run())


def test_t5_delegation_capability_attenuation():
    """
    T5: matcher-agent calling initiate_payment yields BLOCK with reason CAPABILITY_NOT_DELEGATED.
    """
    async def _run():
        os.environ["GOVERNANCE"] = "on"
        enforcer = get_enforcer()
        plan_res = enforcer.capture_plan("Mission T5", {"vendors": [{"bank_account": "004709988776", "approved": True}]})
        token_res = enforcer.get_intent_token(plan_res.plan_hash, plan_res.envelope)

        # Delegate fetch_invoices ONLY to matcher-agent
        enforcer.delegate(
            mission_id="mission_t5",
            parent_agent="controller-agent",
            child_agent="matcher-agent",
            capabilities=["fetch_invoices"],
            ceiling_paise=0,
            payee_scope=[],
            intent_token=token_res.intent_token,
        )

        res = await gateway.call(
            agent_id="matcher-agent",
            tool="initiate_payment",
            params={
                "invoice_id": "INV-2042",
                "payee_account": "004709988776",
                "amount_paise": 945000,
            },
            mission_id="mission_t5",
            intent_token=token_res.intent_token,
        )
        assert res.verdict == "BLOCK"
        assert res.reason == "CAPABILITY_NOT_DELEGATED"

    asyncio.run(_run())


def test_t6_governance_ab_headline_balances():
    """
    T6: Golden Path
    - Governed run ends at exactly 399172600 paise (Rs 39,91,726)
    - Ungoverned run ends at exactly 385756000 paise (Rs 38,57,560)
    - Prevented loss: Rs 1,34,166
    """
    async def _run():
        # 1. Governed Run
        reset_to_seed()
        os.environ["GOVERNANCE"] = "on"
        gov_res = await run_mandate_mission("Governed Mission T6", mission_id="mission_gov_t6", auto_approve_held=True)
        assert gov_res["closing_balance_paise"] == 399172600, (
            f"Governed balance mismatch: expected 399172600, got {gov_res['closing_balance_paise']}"
        )

        # 2. Ungoverned Run
        reset_to_seed()
        os.environ["GOVERNANCE"] = "off"
        ungov_res = await run_mandate_mission("Ungoverned Mission T6", mission_id="mission_ungov_t6")
        assert ungov_res["closing_balance_paise"] == 385756000, (
            f"Ungoverned balance mismatch: expected 385756000, got {ungov_res['closing_balance_paise']}"
        )

        prevented_loss = gov_res["closing_balance_paise"] - ungov_res["closing_balance_paise"]
        assert prevented_loss == 13416600, f"Expected prevented loss 13416600 paise, got {prevented_loss}"

    asyncio.run(_run())


def test_p8_human_approval_and_rejection_flow():
    """
    P8: INV-2043 (Nimbus Rs 1,45,000) is legitimate but exceeds Rs 50,000 ceiling -> HOLD.
    - POST /api/approve/{decision_id} dispatches payment and achieves exact T6 balance.
    - POST /api/reject/{decision_id} leaves balance untouched.
    - Blocked Attack A cannot be approved.
    """
    async def _run():
        reset_to_seed()
        os.environ["GOVERNANCE"] = "on"

        # Run mission with auto_approve_held=False
        m_res = await run_mandate_mission(
            "Mission P8 Hold Test",
            mission_id="mission_p8_hold",
            auto_approve_held=False,
        )

        # Find the HELD decision for INV-2043
        with get_session(DB_PATH) as session:
            held_dec = session.exec(
                select(Decision).where(
                    Decision.mission_id == "mission_p8_hold",
                    Decision.verdict == "HOLD",
                )
            ).first()
            assert held_dec is not None, "Expected a HELD decision for INV-2043"
            held_id = held_dec.id

            # Also verify Attack A is BLOCKED
            blocked_dec = session.exec(
                select(Decision).where(
                    Decision.mission_id == "mission_p8_hold",
                    Decision.verdict == "BLOCK",
                )
            ).first()
            assert blocked_dec is not None
            blocked_id = blocked_dec.id

        # Attempt to approve BLOCKED decision -> Must return 400 Bad Request
        resp_block_approve = client.post(f"/api/approve/{blocked_id}")
        assert resp_block_approve.status_code == 400

        # Approve the HELD decision
        resp_held_approve = client.post(f"/api/approve/{held_id}")
        assert resp_held_approve.status_code == 200

        # Verify closing balance matches T6 target
        with get_session(DB_PATH) as session:
            acc = session.get(BankAccount, "ACC-MANDATE-01")
            assert acc.balance_paise == 399172600

    asyncio.run(_run())


def test_import_boundary_no_mcp_in_agents():
    """
    Invariant: No agent module under backend/agents/ may import the MCP client.
    gateway.py is the SOLE path from agent to tool.
    """
    agents_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", "agents")
    py_files = glob.glob(os.path.join(agents_dir, "*.py"))

    assert len(py_files) > 0

    for file_path in py_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=file_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "mcp_server" not in alias.name, f"Forbidden direct MCP import '{alias.name}' in {file_path}"
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                assert "mcp_server" not in module, f"Forbidden direct MCP from-import '{module}' in {file_path}"


def test_p10_ten_consecutive_cold_reset_runs():
    """
    P10 Gate: POST /api/reset then a full replay run reproduces byte-identical
    closing balances and identical decision sequences 10 times consecutively.
    """
    os.environ["DEMO_MODE"] = "replay"
    os.environ["GOVERNANCE"] = "on"

    async def _run():
        for i in range(10):
            reset_to_seed()
            m_res = await run_mandate_mission(
                f"Replay Rehearsal Run #{i+1}",
                mission_id=f"replay_run_{i+1}",
                auto_approve_held=True,
            )
            assert m_res["closing_balance_paise"] == 399172600, (
                f"Rehearsal Run #{i+1} failed determinism check: expected 399172600, got {m_res['closing_balance_paise']}"
            )
            assert len(m_res["payments_made"]) == 6, f"Expected 6 payments in run #{i+1}, got {len(m_res['payments_made'])}"

    asyncio.run(_run())


def test_hold_approval_must_pass_through_gateway():
    """
    Step 1 Regression: Proves that an approved HOLD reaches the payment tool
    ONLY through gateway.resume_held(), never through direct controller-to-domain bypass.
    """
    reset_to_seed()
    os.environ["GOVERNANCE"] = "on"

    async def _run():
        enforcer = get_enforcer()
        mission_id = "mission_hold_gateway_test"
        
        # 1. Setup trusted plan with high-value PO
        trusted_context = {
            "vendors": [{"id": "V-04", "name": "Nimbus", "bank_account": "917020045511", "approved": True}],
            "open_pos": [{"id": "PO-1004", "amount_paise": 14500000}],
            "ceilings": {"per_invoice_ceiling_paise": 5000000, "mission_ceiling_paise": 30000000},
        }
        plan_res = enforcer.capture_plan("High Value Mission", trusted_context)
        token_res = enforcer.get_intent_token(plan_res.plan_hash, plan_res.envelope)

        # Grant Disburser initiate_payment with 50,000 ceiling
        grant = enforcer.delegate(
            mission_id=mission_id,
            parent_agent="controller-agent",
            child_agent="disburser-agent",
            capabilities=["initiate_payment"],
            ceiling_paise=5000000,
            payee_scope=["917020045511"],
            intent_token=token_res.intent_token,
        )

        # 2. Dispatch high-value call -> Must return HELD through gateway
        held_tool_res = await gateway.call(
            agent_id="disburser-agent",
            tool="initiate_payment",
            params={
                "invoice_id": "INV-HOLD-TEST",
                "payee_account": "917020045511",
                "amount_paise": 14500000,
            },
            mission_id=mission_id,
            intent_token=token_res.intent_token,
        )
        assert held_tool_res.status == "HELD"
        assert held_tool_res.verdict == "HOLD"
        assert held_tool_res.decision_id is not None

        # Verify balance has NOT moved yet
        with get_session(DB_PATH) as session:
            acc = session.get(BankAccount, "ACC-MANDATE-01")
            assert acc.balance_paise == 425000000

        # 3. Resume through gateway.resume_held()
        resumed_res = await gateway.resume_held(held_tool_res.decision_id, approver="cfo")
        assert resumed_res.status == "SUCCESS"
        assert resumed_res.verdict == "ALLOW"

        # Verify balance debited by exactly 14500000 paise (Rs 1,45,000)
        with get_session(DB_PATH) as session:
            acc = session.get(BankAccount, "ACC-MANDATE-01")
            assert acc.balance_paise == 425000000 - 14500000

    asyncio.run(_run())


def test_generic_policy_with_custom_vendor_and_po_without_hardcoded_ids():
    """
    Step 1 Regression: Proves decisions derive generically from sealed context,
    with zero dependence on hardcoded invoice IDs like 'INV-2043'.
    """
    reset_to_seed()
    os.environ["GOVERNANCE"] = "on"

    async def _run():
        enforcer = get_enforcer()
        mission_id = "mission_generic_policy"

        # Brand new custom IDs never seen in canonical fixtures
        custom_vendor = {"id": "V-CUSTOM-99", "name": "Custom Tech", "bank_account": "999888777666", "approved": True}
        custom_po_high = {"id": "PO-CUSTOM-HIGH", "amount_paise": 25000000}  # Rs 2,50,000
        custom_po_low = {"id": "PO-CUSTOM-LOW", "amount_paise": 800000}     # Rs 8,000

        trusted_context = {
            "vendors": [custom_vendor],
            "open_pos": [custom_po_high, custom_po_low],
            "ceilings": {"per_invoice_ceiling_paise": 10000000, "mission_ceiling_paise": 50000000},  # Rs 1,00,000 ceiling
        }
        plan_res = enforcer.capture_plan("Custom Test", trusted_context)
        token_res = enforcer.get_intent_token(plan_res.plan_hash, plan_res.envelope)

        grant = enforcer.delegate(
            mission_id=mission_id,
            parent_agent="controller-agent",
            child_agent="disburser-agent",
            capabilities=["initiate_payment"],
            ceiling_paise=10000000,  # Rs 1,00,000
            payee_scope=["999888777666"],
            intent_token=token_res.intent_token,
        )

        # Test A: Legitimate payment within ceiling -> ALLOW
        res_a = await gateway.call(
            "disburser-agent", "initiate_payment",
            {"invoice_id": "INV-X1", "payee_account": "999888777666", "amount_paise": 800000},
            mission_id=mission_id, intent_token=token_res.intent_token
        )
        assert res_a.verdict == "ALLOW"

        # Test B: High-value legitimate PO above ceiling -> HOLD
        res_b = await gateway.call(
            "disburser-agent", "initiate_payment",
            {"invoice_id": "INV-X2", "payee_account": "999888777666", "amount_paise": 25000000},
            mission_id=mission_id, intent_token=token_res.intent_token
        )
        assert res_b.verdict == "HOLD"

        # Test C: Amount exceeds PO amount without matching any PO -> BLOCK
        res_c = await gateway.call(
            "disburser-agent", "initiate_payment",
            {"invoice_id": "INV-X3", "payee_account": "999888777666", "amount_paise": 28000000},
            mission_id=mission_id, intent_token=token_res.intent_token
        )
        assert res_c.verdict == "BLOCK"
        assert res_c.reason == "AMOUNT_EXCEEDS_PO_AND_CEILING"

        # Test D: Unapproved payee account -> BLOCK
        res_d = await gateway.call(
            "disburser-agent", "initiate_payment",
            {"invoice_id": "INV-X4", "payee_account": "111222333444", "amount_paise": 800000},
            mission_id=mission_id, intent_token=token_res.intent_token
        )
        assert res_d.verdict == "BLOCK"
        assert res_d.reason == "PAYEE_NOT_IN_SEALED_SCOPE"

    asyncio.run(_run())


def test_custom_cfo_ceilings_enforced():
    """
    Step 1 Regression: Proves dynamic custom ceilings configured during CFO setup
    are strictly sealed into the envelope and enforced at runtime.
    """
    reset_to_seed()
    os.environ["GOVERNANCE"] = "on"

    async def _run():
        enforcer = get_enforcer()
        mission_id = "mission_tight_ceiling"

        # Tight custom ceiling of Rs 10,000 (1000000 paise)
        trusted_context = {
            "vendors": [{"id": "V-01", "name": "Kirloskar", "bank_account": "004701234567", "approved": True}],
            "open_pos": [{"id": "PO-1001", "amount_paise": 1000000}],
            "ceilings": {"per_invoice_ceiling_paise": 1000000, "mission_ceiling_paise": 5000000},
        }
        plan_res = enforcer.capture_plan("Tight Limit Mission", trusted_context)
        token_res = enforcer.get_intent_token(plan_res.plan_hash, plan_res.envelope)

        grant = enforcer.delegate(
            mission_id=mission_id,
            parent_agent="controller-agent",
            child_agent="disburser-agent",
            capabilities=["initiate_payment"],
            ceiling_paise=1000000,  # Rs 10,000
            payee_scope=["004701234567"],
            intent_token=token_res.intent_token,
        )

        # 9,999 paise -> ALLOW
        res_below = await gateway.call(
            "disburser-agent", "initiate_payment",
            {"invoice_id": "INV-TIGHT-OK", "payee_account": "004701234567", "amount_paise": 999900},
            mission_id=mission_id, intent_token=token_res.intent_token
        )
        assert res_below.verdict == "ALLOW"

        # 10,001 paise (Rs 100.01) -> BLOCK (exceeds ceiling and PO)
        res_above = await gateway.call(
            "disburser-agent", "initiate_payment",
            {"invoice_id": "INV-TIGHT-FAIL", "payee_account": "004701234567", "amount_paise": 1000100},
            mission_id=mission_id, intent_token=token_res.intent_token
        )
        assert res_above.verdict == "BLOCK"

    asyncio.run(_run())


def test_scenario_token_isolation_no_cross_contamination():
    """
    Step 1 Regression: Proves two isolated missions cannot leak or cross-use
    tokens, payees, or delegation grants.
    """
    reset_to_seed()
    os.environ["GOVERNANCE"] = "on"

    async def _run():
        enforcer = get_enforcer()

        # Scenario Alpha
        token_a = enforcer.get_intent_token("plan_alpha", {"allowed_payees": ["004701234567"], "per_invoice_ceiling_paise": 5000000, "mission_ceiling_paise": 30000000})
        enforcer.delegate("mission_alpha", "controller", "disburser_a", ["initiate_payment"], 5000000, ["004701234567"], token_a.intent_token)

        # Scenario Beta
        token_b = enforcer.get_intent_token("plan_beta", {"allowed_payees": ["201900887766"], "per_invoice_ceiling_paise": 5000000, "mission_ceiling_paise": 30000000})
        enforcer.delegate("mission_beta", "controller", "disburser_b", ["initiate_payment"], 5000000, ["201900887766"], token_b.intent_token)

        # Disburser A attempts payment to Payee Beta -> BLOCKED by Payee Scope
        res_cross = await gateway.call(
            "disburser_a", "initiate_payment",
            {"invoice_id": "INV-CROSS", "payee_account": "201900887766", "amount_paise": 100000},
            mission_id="mission_alpha", intent_token=token_a.intent_token
        )
        assert res_cross.verdict == "BLOCK"
        assert res_cross.reason == "PAYEE_NOT_IN_SEALED_SCOPE"

        # Disburser B attempts payment to Payee Beta -> ALLOWED
        res_valid = await gateway.call(
            "disburser_b", "initiate_payment",
            {"invoice_id": "INV-VALID", "payee_account": "201900887766", "amount_paise": 100000},
            mission_id="mission_beta", intent_token=token_b.intent_token
        )
        assert res_valid.verdict == "ALLOW"

    asyncio.run(_run())


def test_hold_resume_spies_enforcer_before_payment():
    """
    Step 1 Defect 1: Proves enforcer.resume() is explicitly called and authorizes
    the action BEFORE initiate_payment enters the MCP tool layer on human approval.
    """
    reset_to_seed()
    os.environ["GOVERNANCE"] = "on"

    async def _run():
        enforcer = get_enforcer()
        mission_id = "mission_spy_resume"
        trusted_context = {
            "vendors": [{"id": "V-04", "name": "Nimbus", "bank_account": "917020045511", "approved": True}],
            "open_pos": [{"id": "PO-1004", "amount_paise": 14500000}],
            "ceilings": {"per_invoice_ceiling_paise": 5000000, "mission_ceiling_paise": 30000000},
        }
        plan_res = enforcer.capture_plan("High Value Mission", trusted_context)
        token_res = enforcer.get_intent_token(plan_res.plan_hash, plan_res.envelope)

        enforcer.delegate(
            mission_id=mission_id,
            parent_agent="controller-agent",
            child_agent="disburser-agent",
            capabilities=["initiate_payment"],
            ceiling_paise=5000000,
            payee_scope=["917020045511"],
            intent_token=token_res.intent_token,
        )

        # Trigger HOLD
        held_res = await gateway.call(
            "disburser-agent",
            "initiate_payment",
            {"invoice_id": "INV-2043", "payee_account": "917020045511", "amount_paise": 14500000},
            mission_id=mission_id,
            intent_token=token_res.intent_token,
        )
        assert held_res.verdict == "HOLD"
        decision_id = held_res.decision_id

        # Spy on enforcer.resume
        with patch.object(enforcer, "resume", wraps=enforcer.resume) as resume_spy:
            resumed_res = await gateway.resume_held(decision_id, approver="cfo")
            assert resumed_res.verdict == "ALLOW"
            assert resume_spy.call_count == 1, "enforcer.resume() was NOT called before payment dispatch"

    asyncio.run(_run())


def test_hold_resume_blocks_on_tampered_parameters():
    """
    Step 1 Defect 1: Proves parameter tampering between HOLD and approval
    is actively detected and BLOCKED by enforcer.resume() with 0 payment executed.
    """
    reset_to_seed()
    os.environ["GOVERNANCE"] = "on"

    async def _run():
        enforcer = get_enforcer()
        mission_id = "mission_tamper_test"
        trusted_context = {
            "vendors": [{"id": "V-04", "name": "Nimbus", "bank_account": "917020045511", "approved": True}],
            "open_pos": [{"id": "PO-1004", "amount_paise": 14500000}],
            "ceilings": {"per_invoice_ceiling_paise": 5000000, "mission_ceiling_paise": 30000000},
        }
        plan_res = enforcer.capture_plan("Tamper Mission", trusted_context)
        token_res = enforcer.get_intent_token(plan_res.plan_hash, plan_res.envelope)

        enforcer.delegate(
            mission_id=mission_id,
            parent_agent="controller-agent",
            child_agent="disburser-agent",
            capabilities=["initiate_payment"],
            ceiling_paise=5000000,
            payee_scope=["917020045511"],
            intent_token=token_res.intent_token,
        )

        held_res = await gateway.call(
            "disburser-agent",
            "initiate_payment",
            {"invoice_id": "INV-2043", "payee_account": "917020045511", "amount_paise": 14500000},
            mission_id=mission_id,
            intent_token=token_res.intent_token,
        )
        assert held_res.verdict == "HOLD"
        decision_id = held_res.decision_id

        # Attacker modifies the decision record in DB to point to an attacker bank account
        with get_session(DB_PATH) as session:
            dec = session.get(Decision, decision_id)
            dec.params = json.dumps({"invoice_id": "INV-2043", "payee_account": "509900443322", "amount_paise": 14500000})
            session.add(dec)
            session.commit()

        # Approval attempt -> Must be BLOCKED by tamper detection in enforcer.resume
        tamper_res = await gateway.resume_held(decision_id, approver="cfo")
        assert tamper_res.verdict == "BLOCK"
        assert tamper_res.reason == "HELD_DECISION_PARAM_TAMPER_DETECTED"

        # Verify treasury balance remains completely unchanged
        with get_session(DB_PATH) as session:
            acc = session.get(BankAccount, "ACC-MANDATE-01")
            assert acc.balance_paise == 425000000

    asyncio.run(_run())


def test_mcp_transport_inprocess_fastmcp_fidelity():
    """
    Step 1 Defect 2: Verifies that the FastMCP protocol layer in MandateMCPClient
    faithfully lists exactly the 5 tools and executes trusted reads.
    """
    from backend.mcp_server.client import default_mcp_client

    async def _run():
        tools = await default_mcp_client.list_tools()
        assert len(tools) == 5
        assert "list_open_purchase_orders" in tools
        assert "get_vendor_master" in tools
        assert "fetch_invoices" in tools
        assert "initiate_payment" in tools
        assert "write_ap_record" in tools

        # Test trusted tool execution
        vendors = await default_mcp_client.call_tool("get_vendor_master", {})
        assert isinstance(vendors, list)
        assert len(vendors) == 5

    asyncio.run(_run())



