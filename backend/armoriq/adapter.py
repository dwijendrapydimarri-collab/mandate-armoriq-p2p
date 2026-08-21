"""
MANDATE — ArmorIQ Protocol Adapter Interface (SPEC.md 1.8)
Defines the exact four methods required by the ArmorIQ seam:
1. capture_plan
2. get_intent_token
3. delegate
4. invoke
"""

from typing import Protocol, Dict, Any, List, Optional
from pydantic import BaseModel


class PlanResult(BaseModel):
    plan_hash: str
    objective: str
    envelope: Dict[str, Any]
    sealed_at: str


class IntentTokenResult(BaseModel):
    intent_token: str
    plan_hash: str
    merkle_root: str
    sealed_at: str


class DelegationGrant(BaseModel):
    grant_id: str
    mission_id: str
    parent_agent: str
    child_agent: str
    capabilities: List[str]
    ceiling_paise: int
    payee_scope: List[str]
    signature: Optional[str] = None


class InvokeDecision(BaseModel):
    verdict: str  # ALLOW | HOLD | BLOCK
    reason: str
    proof: Dict[str, Any] = {}
    rule_matched: Optional[str] = None


class ArmorIQAdapter(Protocol):
    """Formal protocol for ArmorIQ enforcement."""

    def capture_plan(self, objective: str, context: Dict[str, Any]) -> PlanResult:
        """Canonicalises mission objective and trusted context into a plan."""
        ...

    def get_intent_token(self, plan_hash: str, envelope: Dict[str, Any]) -> IntentTokenResult:
        """Mints an intent token over the sealed authority envelope."""
        ...

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
        """Issues a scoped delegation grant from parent agent to child agent."""
        ...

    def invoke(
        self,
        agent_id: str,
        tool: str,
        params: Dict[str, Any],
        grant: Optional[DelegationGrant] = None,
        intent_token: Optional[str] = None,
    ) -> InvokeDecision:
        """Evaluates whether an agent action is authorised under the active grant and sealed plan."""
        ...

    def resume(
        self,
        decision_id: str,
        approver: str,
        expected_params: Dict[str, Any],
        intent_token: Optional[str] = None,
    ) -> InvokeDecision:
        """Evaluates human approval to resume a previously HELD decision under the original token context."""
        ...

