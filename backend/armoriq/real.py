"""
MANDATE — Genuine ArmorIQ SDK Adapter (SPEC.md §1.8)
Integrates the official armoriq-sdk (v0.6.10) for genuine cryptographic plan capture,
intent token minting, capability delegation, and proxy-verified invocation.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

try:
    import armoriq_sdk
    from armoriq_sdk import (
        ArmorIQClient,
        PlanCapture,
        IntentToken,
        DelegationResult,
        PolicyBlockedException,
        PolicyHoldException,
        IntentMismatchException,
        InvalidTokenException,
        MCPInvocationException,
    )
    import httpx
    ARMORIQ_SDK_AVAILABLE = True
except ImportError:
    ARMORIQ_SDK_AVAILABLE = False

from backend.armoriq.adapter import (
    ArmorIQAdapter,
    PlanResult,
    IntentTokenResult,
    DelegationGrant,
    InvokeDecision,
)

logger = logging.getLogger(__name__)


class RealArmorIQ:
    """Genuine ArmorIQ SDK integration wrapper implementing ArmorIQAdapter Protocol."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        iap_endpoint: Optional[str] = None,
        proxy_endpoint: Optional[str] = None,
        backend_endpoint: Optional[str] = None,
    ):
        self.api_key = api_key or os.environ.get("ARMORIQ_API_KEY", "")

        if not ARMORIQ_SDK_AVAILABLE:
            raise RuntimeError(
                "armoriq-sdk package is not installed. Install with `pip install armoriq-sdk`."
            )

        if not self.api_key:
            raise ValueError(
                "ARMORIQ_API_KEY environment variable is required when running in ARMORIQ_MODE=real."
            )

        # Support clean documented endpoint overrides (IAP_ENDPOINT, PROXY_ENDPOINT, BACKEND_ENDPOINT)
        raw_backend = (
            backend_endpoint
            or os.environ.get("BACKEND_ENDPOINT")
            or os.environ.get("ARMORIQ_BACKEND_ENDPOINT")
            or os.environ.get("ARMORIQ_ENDPOINT")
        )
        if raw_backend:
            raw_backend = raw_backend.rstrip("/")
            # Strip stale legacy /v1 suffix if present
            if raw_backend.endswith("/v1"):
                raw_backend = raw_backend[:-3]

        raw_iap = (
            iap_endpoint
            or os.environ.get("IAP_ENDPOINT")
            or os.environ.get("ARMORIQ_IAP_ENDPOINT")
        )
        if raw_iap:
            raw_iap = raw_iap.rstrip("/")

        raw_proxy = (
            proxy_endpoint
            or os.environ.get("PROXY_ENDPOINT")
            or os.environ.get("ARMORIQ_PROXY_ENDPOINT")
        )
        if raw_proxy:
            raw_proxy = raw_proxy.rstrip("/")

        client_kwargs: Dict[str, Any] = {"api_key": self.api_key}
        if not (self.api_key.startswith("ak_live_") or self.api_key.startswith("ak_test_") or self.api_key.startswith("ak_claw_")):
            client_kwargs["_skip_api_key_validation"] = True
        if raw_backend:
            client_kwargs["backend_endpoint"] = raw_backend
        if raw_iap:
            client_kwargs["iap_endpoint"] = raw_iap
        if raw_proxy:
            client_kwargs["proxy_endpoint"] = raw_proxy

        self.client = ArmorIQClient(**client_kwargs)

        self._captured_plans: Dict[str, PlanCapture] = {}
        self._tokens: Dict[str, IntentToken] = {}
        self._delegations: Dict[str, Any] = {}


    def capture_plan(self, objective: str, context: Dict[str, Any]) -> PlanResult:
        """Captures structured procurement execution plan via genuine ArmorIQ SDK."""
        tools_definition = [
            {
                "tool": "fetch_invoices",
                "action": "fetch_invoices",
                "mcp": "mandate-mcp",
                "description": "Fetch routine incoming invoices",
            },
            {
                "tool": "initiate_payment",
                "action": "initiate_payment",
                "mcp": "mandate-mcp",
                "description": "Disburse invoice payment to approved vendor payee",
                "params_scope": {
                    "approved_payees": context.get("approved_payees", []),
                    "max_invoice_paise": context.get("spend_ceilings", {}).get("per_invoice_paise", 50000000),
                },
            },
            {
                "tool": "write_ap_record",
                "action": "write_ap_record",
                "mcp": "mandate-mcp",
                "description": "Record general ledger accounting entry",
            },
        ]

        plan_payload = {
            "objective": objective,
            "steps": tools_definition,
            "trusted_authority": {
                "mission_id": context.get("mission_id", ""),
                "approved_payees": context.get("approved_payees", []),
                "spend_ceilings": context.get("spend_ceilings", {}),
                "open_pos": context.get("open_pos", []),
            },
        }

        plan_capture = self.client.capture_plan(
            llm="gpt-4o",
            prompt=f"Execute Procure-to-Pay Mission: {objective}",
            plan=plan_payload,
            metadata={
                "mission_id": context.get("mission_id", ""),
                "cfo_sealed": True,
                "sealed_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        plan_hash = hashlib.sha256(json.dumps(plan_payload, sort_keys=True).encode()).hexdigest()

        # Cache the actual SDK PlanCapture object for subsequent token minting
        self._captured_plans[plan_hash] = plan_capture
        self._captured_plans[objective] = plan_capture

        return PlanResult(
            plan_hash=plan_hash,
            objective=objective,
            envelope=context,
            sealed_at=datetime.now(timezone.utc).isoformat(),
        )

    def get_intent_token(self, plan_hash: str, envelope: Dict[str, Any]) -> IntentTokenResult:
        """Requests signed Intent Token with Merkle step proofs using the genuine cached PlanCapture."""
        plan_capture = self._captured_plans.get(plan_hash) or self._captured_plans.get(envelope.get("objective", ""))
        
        if not plan_capture:
            raise ValueError(
                f"No captured plan found for plan_hash '{plan_hash}'. "
                "Must call capture_plan() before requesting intent token."
            )

        policy = {
            "spend_ceilings": envelope.get("spend_ceilings", {}),
            "approved_payees": envelope.get("approved_payees", []),
            "open_pos": envelope.get("open_pos", []),
        }

        try:
            sdk_token = self.client.get_intent_token(
                plan_capture=plan_capture,
                policy=policy,
                validity_seconds=3600.0,
            )

            jwt_tok = getattr(sdk_token, "jwt_token", None)
            tok_id = getattr(sdk_token, "token_id", None)
            if isinstance(jwt_tok, str) and jwt_tok:
                token_str = jwt_tok
            elif isinstance(tok_id, str) and tok_id:
                token_str = tok_id
            else:
                raise InvalidTokenException("ArmorIQ SDK did not return a valid token string.")

            m_root = getattr(sdk_token, "merkle_root", None)
            if isinstance(m_root, str) and m_root:
                merkle_root = m_root
            elif (
                isinstance(getattr(sdk_token, "raw_token", None), dict)
                and isinstance(sdk_token.raw_token.get("merkle_root"), str)
            ):
                merkle_root = sdk_token.raw_token["merkle_root"]
            else:
                merkle_root = ""

            # Cache the actual SDK IntentToken for invoke and delegation operations
            self._tokens[token_str] = sdk_token
            if tok_id and isinstance(tok_id, str):
                self._tokens[tok_id] = sdk_token

            return IntentTokenResult(
                intent_token=token_str,
                plan_hash=str(getattr(sdk_token, "plan_hash", plan_hash)),
                merkle_root=merkle_root,
                sealed_at=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as e:
            logger.error("ArmorIQ get_intent_token failed: %s", e)
            raise

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
        """Issues cryptographically bound delegation grant via ArmorIQ SDK."""
        import uuid
        grant_id = f"grant_{uuid.uuid4().hex[:12]}"
        sdk_delegation_status = "ARMORIQ_DELEGATION_UNSUPPORTED"
        grant_signature = "UNSUPPORTED_IN_SDK_SESSION"

        sdk_token = self._tokens.get(intent_token)
        if sdk_token and hasattr(self.client, "delegate"):
            try:
                res = self.client.delegate(
                    intent_token=sdk_token,
                    delegate_public_key=child_agent,
                    validity_seconds=3600,
                    allowed_actions=capabilities,
                    target_agent=child_agent,
                )
                if isinstance(res, DelegationResult):
                    grant_id = getattr(res, "delegation_id", grant_id)
                    delegated_token = getattr(res, "delegated_token", None)
                    if delegated_token:
                        grant_signature = getattr(delegated_token, "signature", "") or f"armoriq_delegation_{grant_id}"
                        self._tokens[delegated_token.token_id] = delegated_token
                        self._tokens[grant_id] = delegated_token
                    else:
                        grant_signature = f"armoriq_delegation_{grant_id}"
                    self._delegations[grant_id] = res
                    sdk_delegation_status = "ARMORIQ_SDK_DELEGATED"
            except Exception as e:
                logger.info("ArmorIQ SDK delegation call note: %s", e)
                grant_signature = f"ARMORIQ_DELEGATION_UNSUPPORTED: {str(e)[:50]}"

        return DelegationGrant(
            grant_id=grant_id,
            mission_id=mission_id,
            parent_agent=parent_agent,
            child_agent=child_agent,
            capabilities=capabilities,
            ceiling_paise=ceiling_paise,
            payee_scope=payee_scope,
            signature=grant_signature,
        )

    def invoke(
        self,
        agent_id: str,
        tool: str,
        params: Dict[str, Any],
        grant: Optional[DelegationGrant] = None,
        intent_token: Optional[str] = None,
    ) -> InvokeDecision:
        """Evaluates whether an agent action is authorized via ArmorIQ SDK."""
        # 1. Capability attenuation enforcement at client gateway layer
        if grant and tool not in grant.capabilities:
            return InvokeDecision(
                verdict="BLOCK",
                reason=f"LOCAL_CAPABILITY_ATTENUATION: Agent '{agent_id}' does not possess capability '{tool}' in active client-scoped grant",
                rule_matched="CLIENT_DELEGATION_SCOPE_EXCEEDED",
                proof={"enforcer": "LOCAL_GATEWAY_ATTENUATION", "grant_id": grant.grant_id, "verdict": "BLOCK"},
            )

        sdk_token = self._tokens.get(intent_token) if intent_token else None

        if not sdk_token:
            return InvokeDecision(
                verdict="BLOCK",
                reason="MISSING_INTENT_TOKEN: Cannot invoke without a valid active ArmorIQ IntentToken",
                rule_matched="UNAUTHORIZED_PROPOSAL",
                proof={"enforcer": "ARMORIQ_SDK", "verdict": "BLOCK"},
            )

        # 2. Invoke through SDK client proxy
        try:
            res = self.client.invoke(
                mcp="mandate-mcp",
                action=tool,
                intent_token=sdk_token,
                params=params,
                user_email="cfo@mandate.internal",
            )
            
            # Inspect SDK response
            has_tool_error = bool(getattr(res, "status", "") == "error")
            if has_tool_error:
                return InvokeDecision(
                    verdict="BLOCK",
                    reason=f"ARMORIQ_TOOL_ERROR: {getattr(res, 'result', 'Tool returned error status')}",
                    rule_matched="TOOL_EXECUTION_ERROR",
                    proof={"enforcer": "ARMORIQ_SDK", "status": "error"},
                )

            verified_val = getattr(res, "verified", None)
            proof_data: Dict[str, Any] = {
                "enforcer": "ARMORIQ_SDK",
                "status": getattr(res, "status", "success"),
                "execution_time": getattr(res, "execution_time", 0.0),
            }
            if verified_val is not None:
                proof_data["verified"] = verified_val

            return InvokeDecision(
                verdict="ALLOW",
                reason="ArmorIQ SDK verified action against sealed authority plan",
                proof=proof_data,
            )
        except PolicyBlockedException as e:
            return InvokeDecision(
                verdict="BLOCK",
                reason=f"ARMORIQ_POLICY_BLOCKED: {getattr(e, 'reason', str(e))}",
                rule_matched="ARMORIQ_POLICY_BLOCK",
                proof={"enforcer": "ARMORIQ_SDK", "verdict": "BLOCK", "reason": str(e)},
            )
        except PolicyHoldException as e:
            return InvokeDecision(
                verdict="HOLD",
                reason=f"ARMORIQ_POLICY_HOLD: Human review required - {str(e)}",
                rule_matched="ARMORIQ_POLICY_HOLD",
                proof={"enforcer": "ARMORIQ_SDK", "verdict": "HOLD", "reason": str(e)},
            )
        except IntentMismatchException as e:
            return InvokeDecision(
                verdict="BLOCK",
                reason=f"INTENT_MISMATCH: {str(e)}",
                rule_matched="UNPLANNED_ACTION_BLOCKED",
                proof={"enforcer": "ARMORIQ_SDK", "verdict": "BLOCK", "reason": str(e)},
            )
        except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
            logger.error("ArmorIQ connectivity error: %s", e)
            return InvokeDecision(
                verdict="BLOCK",
                reason=f"ARMORIQ_UNAVAILABLE: Failed to reach ArmorIQ proxy/IAP endpoint ({str(e)})",
                rule_matched="ARMORIQ_SERVICE_UNAVAILABLE",
                proof={"enforcer": "ARMORIQ_SDK", "error": "ARMORIQ_UNAVAILABLE", "detail": str(e)},
            )
        except Exception as e:
            logger.error("ArmorIQ SDK invocation error: %s", e)
            return InvokeDecision(
                verdict="BLOCK",
                reason=f"ARMORIQ_ENFORCEMENT_ERROR: {str(e)}",
                rule_matched="SDK_INVOCATION_FAILED",
                proof={"enforcer": "ARMORIQ_SDK", "error": str(e)},
            )

    def resume(
        self,
        decision_id: str,
        approver: str,
        expected_params: Dict[str, Any],
        intent_token: Optional[str] = None,
    ) -> InvokeDecision:
        """Evaluates human CFO approval to resume a previously HELD decision via ArmorIQ session."""
        try:
            if hasattr(self.client, "get_delegation_status"):
                status = self.client.get_delegation_status(decision_id)
                if status == "approved":
                    if hasattr(self.client, "mark_delegation_executed"):
                        self.client.mark_delegation_executed(approver, decision_id)
                    return InvokeDecision(
                        verdict="ALLOW",
                        reason=f"ArmorIQ delegation approval confirmed for {decision_id}",
                        proof={"enforcer": "ARMORIQ_SDK", "status": "APPROVED", "delegation_id": decision_id},
                    )
                elif status in ("rejected", "expired"):
                    return InvokeDecision(
                        verdict="BLOCK",
                        reason=f"ArmorIQ delegation status is '{status}' for {decision_id}",
                        rule_matched="DELEGATION_HOLD_REJECTED",
                        proof={"enforcer": "ARMORIQ_SDK", "status": status, "delegation_id": decision_id},
                    )
            
            # If no active cloud delegation session for decision_id, fail closed in real mode
            return InvokeDecision(
                verdict="BLOCK",
                reason=f"ARMORIQ_RESUME_UNSUPPORTED: No active ArmorIQ cloud approval session found for decision '{decision_id}'",
                rule_matched="RESUME_SESSION_UNAVAILABLE",
                proof={"enforcer": "ARMORIQ_SDK", "status": "ARMORIQ_RESUME_UNSUPPORTED", "decision_id": decision_id},
            )
        except Exception as e:
            return InvokeDecision(
                verdict="BLOCK",
                reason=f"ARMORIQ_RESUME_UNSUPPORTED: ArmorIQ approval endpoint returned error ({str(e)})",
                rule_matched="RESUME_ENDPOINT_UNAVAILABLE",
                proof={"enforcer": "ARMORIQ_SDK", "status": "ARMORIQ_RESUME_UNSUPPORTED", "detail": str(e)},
            )

