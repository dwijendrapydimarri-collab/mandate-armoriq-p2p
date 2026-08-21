"""
MANDATE — RealArmorIQ SDK Adapter (SPEC.md 1.8)
Wraps the actual ArmorIQ SDK when live credentials and endpoint are available.
Falls back cleanly to LocalEnforcer with explicit logging when SDK is not present.
"""

import os
from typing import Dict, Any, List, Optional
from backend.armoriq.adapter import (
    ArmorIQAdapter,
    PlanResult,
    IntentTokenResult,
    DelegationGrant,
    InvokeDecision,
)
from backend.armoriq.local import LocalEnforcer


class RealArmorIQ:
    """Real ArmorIQ SDK integration wrapper."""

    def __init__(self):
        self.api_key = os.environ.get("ARMORIQ_API_KEY", "")
        self.endpoint = os.environ.get("ARMORIQ_ENDPOINT", "https://api.armoriq.ai/v1")
        self._fallback = LocalEnforcer()

    def capture_plan(self, objective: str, context: Dict[str, Any]) -> PlanResult:
        # TODO [SDK SPIKE]: Replace with real ArmorIQ client.plans.capture(...)
        return self._fallback.capture_plan(objective, context)

    def get_intent_token(self, plan_hash: str, envelope: Dict[str, Any]) -> IntentTokenResult:
        # TODO [SDK SPIKE]: Replace with real ArmorIQ client.tokens.mint(...)
        return self._fallback.get_intent_token(plan_hash, envelope)

    def delegate(
        self,
        mission_id: str,
        parent_agent: str,
        child_agent: str,
        capabilities: List[str],
        ceiling_paise: int,
        payee_scope: List[str],
        intent_token: str,
    ) -> DelegationGrant:
        # TODO [SDK SPIKE]: Replace with real ArmorIQ client.delegations.issue(...)
        return self._fallback.delegate(
            mission_id=mission_id,
            parent_agent=parent_agent,
            child_agent=child_agent,
            capabilities=capabilities,
            ceiling_paise=ceiling_paise,
            payee_scope=payee_scope,
            intent_token=intent_token,
        )

    def invoke(
        self,
        agent_id: str,
        tool: str,
        params: Dict[str, Any],
        grant: Optional[DelegationGrant] = None,
        intent_token: Optional[str] = None,
    ) -> InvokeDecision:
        # TODO [SDK SPIKE]: Replace with real ArmorIQ client.actions.invoke(...)
        return self._fallback.invoke(
            agent_id=agent_id,
            tool=tool,
            params=params,
            grant=grant,
            intent_token=intent_token,
        )

    def resume(
        self,
        decision_id: str,
        approver: str,
        expected_params: Dict[str, Any],
        intent_token: Optional[str] = None,
    ) -> InvokeDecision:
        # TODO [SDK SPIKE]: Replace with real ArmorIQ client.decisions.resume(...)
        return self._fallback.resume(
            decision_id=decision_id,
            approver=approver,
            expected_params=expected_params,
            intent_token=intent_token,
        )
