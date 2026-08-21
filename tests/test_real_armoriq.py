"""
MANDATE — Genuine ArmorIQ SDK Integration Tests (Local vs Real Mode)
Tests fail-closed behavior, safe mode selection, and real SDK verification when credentials exist.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from backend.armoriq.adapter import PlanResult, IntentTokenResult, DelegationGrant, InvokeDecision
from backend.armoriq.local import LocalEnforcer
from backend.armoriq.real import RealArmorIQ, ARMORIQ_SDK_AVAILABLE


def test_sdk_package_installed():
    """Verify that armoriq-sdk package is installed and importable."""
    assert ARMORIQ_SDK_AVAILABLE, "armoriq-sdk must be installed in the environment"
    import armoriq_sdk
    version = getattr(armoriq_sdk, "__version__", None) or getattr(armoriq_sdk, "VERSION", "unknown")
    assert version != "unknown", "armoriq-sdk must expose a valid version"


def test_real_armoriq_fails_closed_without_api_key():
    """Verify that ARMORIQ_MODE=real fails closed if ARMORIQ_API_KEY is missing."""
    with patch.dict(os.environ, {"ARMORIQ_MODE": "real", "ARMORIQ_API_KEY": ""}, clear=False):
        with pytest.raises(ValueError, match="ARMORIQ_API_KEY"):
            RealArmorIQ(api_key="")


def test_real_armoriq_adapter_mapping_with_mock_client():
    """Verify the 5-method protocol mapping against the ArmorIQClient."""
    real_adapter = RealArmorIQ(api_key="ak_test_mock_for_unit_test")
    assert real_adapter.client is not None

    # 1. Test capture_plan
    plan_res = real_adapter.capture_plan(
        objective="Settle vendor invoices under PO limit",
        context={
            "mission_id": "mission_test_01",
            "approved_payees": ["1122334455"],
            "spend_ceilings": {"per_invoice_paise": 50000000},
            "open_pos": ["PO-2026-001"],
        },
    )
    assert isinstance(plan_res, PlanResult)
    assert plan_res.plan_hash is not None
    assert len(plan_res.plan_hash) > 0

    # 2. Test get_intent_token with mocked client response
    mock_token = MagicMock()
    mock_token.token_id = "token_test_123"
    mock_token.jwt_token = "jwt_token_sample"
    mock_token.plan_hash = plan_res.plan_hash
    mock_token.merkle_root = "merkle_root_test"
    mock_token.raw_token = {"jwt_token": "jwt_token_sample", "merkle_root": "merkle_root_test"}
    
    with patch.object(real_adapter.client, "get_intent_token", return_value=mock_token):
        token_res = real_adapter.get_intent_token(
            plan_hash=plan_res.plan_hash,
            envelope=plan_res.envelope,
        )
        assert isinstance(token_res, IntentTokenResult)
        assert token_res.intent_token == "jwt_token_sample"
        assert token_res.plan_hash == plan_res.plan_hash

    # 3. Test delegation grant
    grant = real_adapter.delegate(
        mission_id="mission_test_01",
        parent_agent="controller",
        child_agent="disburser",
        capabilities=["initiate_payment"],
        ceiling_paise=50000000,
        payee_scope=["1122334455"],
        intent_token=token_res.intent_token,
    )
    assert isinstance(grant, DelegationGrant)
    assert grant.child_agent == "disburser"
    assert "initiate_payment" in grant.capabilities

    # 4. Test capability enforcement on invoke
    blocked_invoke = real_adapter.invoke(
        agent_id="matcher",
        tool="initiate_payment",
        params={"paise": 1000},
        grant=DelegationGrant(
            grant_id="grant_matcher",
            mission_id="mission_test_01",
            parent_agent="controller",
            child_agent="matcher",
            capabilities=["fetch_invoices"],
            ceiling_paise=0,
            payee_scope=[],
        ),
        intent_token=token_res.intent_token,
    )
    assert isinstance(blocked_invoke, InvokeDecision)
    assert blocked_invoke.verdict == "BLOCK"
    assert "CAPABILITY_NOT_DELEGATED" in blocked_invoke.reason

    # 5. Test resume
    resumed = real_adapter.resume(
        decision_id="dec_test_01",
        approver="cfo@mandate.internal",
        expected_params={"paise": 14500000},
        intent_token=token_res.intent_token,
    )
    assert isinstance(resumed, InvokeDecision)
    assert resumed.verdict == "ALLOW"


@pytest.mark.skipif(
    not os.environ.get("ARMORIQ_API_KEY") or os.environ.get("ARMORIQ_API_KEY", "").startswith("ak_test_mock"),
    reason="Live ARMORIQ_API_KEY not configured in environment",
)
def test_live_armoriq_smoke():
    """Live smoke test executed strictly when genuine ArmorIQ credentials are present."""
    api_key = os.environ["ARMORIQ_API_KEY"]
    real_adapter = RealArmorIQ(api_key=api_key)

    plan_res = real_adapter.capture_plan(
        objective="Smoke Test Live P2P Authority Sealing",
        context={
            "mission_id": "smoke_mission_01",
            "approved_payees": ["1122334455"],
            "spend_ceilings": {"per_invoice_paise": 50000000},
            "open_pos": ["PO-SMOKE-001"],
        },
    )
    assert plan_res.plan_hash

    token_res = real_adapter.get_intent_token(
        plan_hash=plan_res.plan_hash,
        envelope=plan_res.envelope,
    )
    assert token_res.intent_token
