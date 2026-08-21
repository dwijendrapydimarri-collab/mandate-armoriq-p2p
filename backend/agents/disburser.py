"""
MANDATE — Disburser Agent (SPEC.md 1.7)
Payment subagent holding capability: ['initiate_payment'].
Enforces per-invoice ceiling (Rs 50,000) and approved payee whitelist.
Handles Attack A (payee deviation), Attack C (parameter shift), and HOLD scenarios.
"""

from typing import Dict, Any, List
from backend import gateway


class DisburserAgent:
    def __init__(self, agent_id: str = "disburser-agent"):
        self.agent_id = agent_id

    async def execute_payment(
        self,
        invoice_id: str,
        payee_account: str,
        amount_paise: int,
        mission_id: str,
        intent_token: str,
    ) -> gateway.ToolResult:
        # Route through gateway
        return await gateway.call(
            self.agent_id,
            "initiate_payment",
            {
                "invoice_id": invoice_id,
                "payee_account": payee_account,
                "amount_paise": amount_paise,
            },
            mission_id=mission_id,
            intent_token=intent_token,
        )
