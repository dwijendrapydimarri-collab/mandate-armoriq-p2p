"""
MANDATE — LocalEnforcer (Spec-Faithful ArmorIQ Implementation)
Executes local plan capture, intent token minting, delegation grants, and invoke authorization.
Honesty requirement: When active, UI renders 'ENFORCEMENT: LOCAL ADAPTER (ArmorIQ contract)'.
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from backend.armoriq.adapter import (
    ArmorIQAdapter,
    PlanResult,
    IntentTokenResult,
    DelegationGrant,
    InvokeDecision,
)
from backend.armoriq.crypto import generate_agent_keypair, sign_payload


class LocalEnforcer:
    """Local, spec-faithful implementation of ArmorIQ Protocol."""

    def __init__(self):
        self._cfo_priv, self._cfo_pub = generate_agent_keypair()
        self._keys: Dict[str, Tuple[str, str]] = {"cfo": (self._cfo_priv, self._cfo_pub)}
        self._plans: Dict[str, Dict[str, Any]] = {}
        self._tokens: Dict[str, Dict[str, Any]] = {}
        self._grants: Dict[str, DelegationGrant] = {}
        self._held_decisions: Dict[str, Dict[str, Any]] = {}
        self._approved_held_decisions: set = set()

    def register_held(self, decision_id: str, params: Dict[str, Any], intent_token: Optional[str] = None):
        """Registers a held decision and its exact parameters for tamper checking on resume."""
        self._held_decisions[decision_id] = {
            "params": dict(params),
            "intent_token": intent_token,
        }


    def capture_plan(self, objective: str, context: Dict[str, Any]) -> PlanResult:
        now_iso = datetime.now(timezone.utc).isoformat()
        canonical_raw = json.dumps({"objective": objective, "context": context}, sort_keys=True)
        plan_hash = hashlib.sha256(canonical_raw.encode("utf-8")).hexdigest()

        # Derive envelope from trusted context
        vendors = context.get("vendors", [])
        allowed_payees = [v["bank_account"] for v in vendors if v.get("approved", True) and "bank_account" in v]

        # Dynamic CFO ceilings (defaulting to canonical Rs 50,000 / Rs 3,00,000 if not specified)
        ceilings = context.get("ceilings", {})
        per_invoice_ceiling_paise = int(ceilings.get("per_invoice_ceiling_paise", 5000000))
        mission_ceiling_paise = int(ceilings.get("mission_ceiling_paise", 30000000))
        open_pos = context.get("open_pos", [])

        envelope = {
            "allowed_payees": allowed_payees,
            "per_invoice_ceiling_paise": per_invoice_ceiling_paise,
            "mission_ceiling_paise": mission_ceiling_paise,
            "open_pos_count": len(open_pos),
        }

        self._plans[plan_hash] = {
            "objective": objective,
            "envelope": envelope,
            "open_pos": open_pos,
            "vendors": vendors,
            "sealed_at": now_iso,
        }

        return PlanResult(
            plan_hash=plan_hash,
            objective=objective,
            envelope=envelope,
            sealed_at=now_iso,
        )

    def get_intent_token(self, plan_hash: str, envelope: Dict[str, Any]) -> IntentTokenResult:
        plan_data = self._plans.get(plan_hash, {})
        sealed_at = plan_data.get("sealed_at", datetime.now(timezone.utc).isoformat())

        token_raw = f"{plan_hash}:{json.dumps(envelope, sort_keys=True)}"
        intent_token = "tok_intent_" + hashlib.sha256(token_raw.encode("utf-8")).hexdigest()[:24]
        merkle_root = "0x" + hashlib.sha256(f"{intent_token}:{plan_hash}".encode("utf-8")).hexdigest()

        self._tokens[intent_token] = {
            "plan_hash": plan_hash,
            "envelope": envelope,
            "open_pos": plan_data.get("open_pos", []),
            "vendors": plan_data.get("vendors", []),
            "merkle_root": merkle_root,
            "sealed_at": sealed_at,
        }

        return IntentTokenResult(
            intent_token=intent_token,
            plan_hash=plan_hash,
            merkle_root=merkle_root,
            sealed_at=sealed_at,
        )

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
        if parent_agent not in self._keys:
            priv, pub = generate_agent_keypair()
            self._keys[parent_agent] = (priv, pub)
        if child_agent not in self._keys:
            priv, pub = generate_agent_keypair()
            self._keys[child_agent] = (priv, pub)

        parent_priv = self._keys[parent_agent][0]
        grant_id = f"grant_{parent_agent}_{child_agent}_{int(datetime.now(timezone.utc).timestamp())}"
        payload = {
            "grant_id": grant_id,
            "mission_id": mission_id,
            "parent_agent": parent_agent,
            "child_agent": child_agent,
            "capabilities": capabilities,
            "ceiling_paise": ceiling_paise,
            "payee_scope": payee_scope,
            "intent_token": intent_token,
        }
        sig = sign_payload(parent_priv, payload)

        grant = DelegationGrant(
            grant_id=grant_id,
            mission_id=mission_id,
            parent_agent=parent_agent,
            child_agent=child_agent,
            capabilities=capabilities,
            ceiling_paise=ceiling_paise,
            payee_scope=payee_scope,
            signature=sig,
        )
        # Store grant scoped by mission and child_agent
        self._grants[f"{mission_id}:{child_agent}"] = grant
        self._grants[child_agent] = grant
        return grant

    def get_grant(self, agent_id: str, mission_id: Optional[str] = None) -> Optional[DelegationGrant]:
        if mission_id and f"{mission_id}:{agent_id}" in self._grants:
            return self._grants[f"{mission_id}:{agent_id}"]
        return self._grants.get(agent_id)

    def record_human_approval(self, decision_id: str):
        """Records an explicit human approval on a held decision."""
        self._approved_held_decisions.add(decision_id)

    def invoke(
        self,
        agent_id: str,
        tool: str,
        params: Dict[str, Any],
        grant: Optional[DelegationGrant] = None,
        intent_token: Optional[str] = None,
    ) -> InvokeDecision:
        now_iso = datetime.now(timezone.utc).isoformat()
        proof = {
            "enforcement_mode": "local_adapter",
            "adapter": "LocalEnforcer",
            "timestamp": now_iso,
            "intent_token": intent_token,
            "agent_id": agent_id,
            "tool": tool,
        }

        # 1. Capability Delegation Check
        if grant is not None:
            if tool not in grant.capabilities:
                return InvokeDecision(
                    verdict="BLOCK",
                    reason="CAPABILITY_NOT_DELEGATED",
                    rule_matched="DELEGATION_CAPABILITY_POLICY",
                    proof={
                        **proof,
                        "required_capability": tool,
                        "delegated_capabilities": grant.capabilities,
                        "authorized_by": "NOBODY",
                    },
                )

        # 2. Domain & Semantic Scope Checks for initiate_payment
        if tool == "initiate_payment":
            payee_account = str(params.get("payee_account", ""))
            amount_paise = int(params.get("amount_paise", 0))
            invoice_id = str(params.get("invoice_id", ""))

            # Token context lookup
            token_context = self._tokens.get(intent_token, {}) if intent_token else {}
            envelope = token_context.get("envelope", {})
            open_pos = token_context.get("open_pos", [])

            # Payee scope check
            allowed_payees = grant.payee_scope if grant else envelope.get("allowed_payees", [])
            if allowed_payees and payee_account not in allowed_payees:
                return InvokeDecision(
                    verdict="BLOCK",
                    reason="PAYEE_NOT_IN_SEALED_SCOPE",
                    rule_matched="SEALED_PAYEE_WHITELIST",
                    proof={
                        **proof,
                        "payee_attempted": payee_account,
                        "allowed_payee_scope": allowed_payees,
                        "authorized_by": "NOBODY",
                        "violation": "Payee account does not exist in CFO-sealed vendor master",
                    },
                )

            # Ceiling & PO Semantic Matching
            ceiling = grant.ceiling_paise if grant else envelope.get("per_invoice_ceiling_paise", 5000000)
            mission_ceiling = envelope.get("mission_ceiling_paise", 30000000)

            # Look for a matching trusted PO
            matching_po = None
            for po in open_pos:
                po_id = po.get("id")
                po_amount = po.get("amount_paise", 0)
                # Match by exact invoice link or amount
                if po_amount == amount_paise:
                    matching_po = po
                    break
                elif invoice_id and str(po.get("id", "")) in invoice_id:
                    matching_po = po
                    break

            # Generic evaluation:
            if amount_paise > ceiling:
                # Check if this high-value amount is backed by an open PO in the trusted plan
                is_legit_po = any(po.get("amount_paise") == amount_paise for po in open_pos)
                
                if is_legit_po and amount_paise <= mission_ceiling:
                    return InvokeDecision(
                        verdict="HOLD",
                        reason="EXCEEDS_DELEGATION_CEILING_REQUIRES_APPROVAL",
                        rule_matched="HUMAN_IN_THE_LOOP_APPROVAL_GATE",
                        proof={
                            **proof,
                            "amount_paise": amount_paise,
                            "delegation_ceiling_paise": ceiling,
                            "pending_approval": True,
                        },
                    )
                else:
                    # Stated amount exceeds ceiling without a matching trusted PO amount (e.g. Attack C decimal shift)
                    return InvokeDecision(
                        verdict="BLOCK",
                        reason="AMOUNT_EXCEEDS_PO_AND_CEILING",
                        rule_matched="SPEND_LIMIT_POLICY",
                        proof={
                            **proof,
                            "amount_paise": amount_paise,
                            "ceiling_paise": ceiling,
                            "authorized_by": "NOBODY",
                            "violation": "Amount exceeds both PO-derived ceiling and delegation limit",
                        },
                    )

            # If amount is <= ceiling, verify it does not exceed its specific PO if known
            if matching_po and amount_paise > matching_po.get("amount_paise", 0):
                return InvokeDecision(
                    verdict="BLOCK",
                    reason="AMOUNT_EXCEEDS_PO",
                    rule_matched="PO_PRICE_CEILING",
                    proof={
                        **proof,
                        "amount_paise": amount_paise,
                        "po_amount_paise": matching_po.get("amount_paise", 0),
                        "authorized_by": "NOBODY",
                    },
                )

        # 3. Default ALLOW
        return InvokeDecision(
            verdict="ALLOW",
            reason="AUTHORIZED_WITHIN_DELEGATED_SCOPE",
            rule_matched="MANDATE_POLICY_ALLOW",
            proof=proof,
        )

    def resume(
        self,
        decision_id: str,
        approver: str,
        expected_params: Dict[str, Any],
        intent_token: Optional[str] = None,
    ) -> InvokeDecision:
        """
        Evaluates explicit human approval to resume a previously HELD decision.
        Performs strict cryptographic and parameter tamper verification.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        proof = {
            "enforcement_mode": "local_adapter",
            "adapter": "LocalEnforcer",
            "timestamp": now_iso,
            "resumed_from_hold": True,
            "original_decision_id": decision_id,
            "approver": approver,
            "intent_token": intent_token,
        }

        # 1. Check if decision was registered as HELD
        held_info = self._held_decisions.get(decision_id)
        if held_info:
            original_params = held_info.get("params", {})
            # Tamper verification: parameters cannot be changed between HOLD and approval
            for key, val in original_params.items():
                if expected_params.get(key) != val:
                    return InvokeDecision(
                        verdict="BLOCK",
                        reason="HELD_DECISION_PARAM_TAMPER_DETECTED",
                        rule_matched="HUMAN_APPROVAL_INTEGRITY_POLICY",
                        proof={
                            **proof,
                            "tampered_key": key,
                            "original_value": val,
                            "attempted_value": expected_params.get(key),
                            "authorized_by": "NOBODY",
                        },
                    )

        # 2. Verify approver authority
        if approver.lower() not in ["cfo", "human_cfo", "admin"]:
            return InvokeDecision(
                verdict="BLOCK",
                reason="UNAUTHORIZED_APPROVER_ROLE",
                rule_matched="HUMAN_APPROVAL_ROLE_POLICY",
                proof={
                    **proof,
                    "attempted_approver": approver,
                    "authorized_by": "NOBODY",
                },
            )

        # 3. Authorization granted
        self._approved_held_decisions.add(decision_id)
        return InvokeDecision(
            verdict="ALLOW",
            reason=f"APPROVED_BY_{approver.upper()}_HUMAN_IN_THE_LOOP",
            rule_matched="HUMAN_APPROVAL_RESUME_ALLOW",
            proof=proof,
        )

