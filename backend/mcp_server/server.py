"""
MANDATE — MCP Server (SPEC.md 1.6)
Exposes exactly five tools using the official MCP Python SDK (FastMCP protocol layer).
Wraps the domain functions from P1 — contains no authorization or business logic.
"""


import sys
import os
from typing import List, Dict, Any, Optional

# Ensure repository root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from mcp.server.fastmcp import FastMCP
from backend.domain import (
    domain_list_open_purchase_orders,
    domain_get_vendor_master,
    domain_fetch_invoices,
    domain_initiate_payment,
    domain_write_ap_record,
    DB_PATH,
)


mcp = FastMCP("mandate-mcp-server")


@mcp.tool()
def list_open_purchase_orders(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all open purchase orders in the system (Trusted Read)."""
    return domain_list_open_purchase_orders(db_path=db_path or DB_PATH)


@mcp.tool()
def get_vendor_master(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch the approved vendor master directory (Trusted Read)."""
    return domain_get_vendor_master(db_path=db_path or DB_PATH)


@mcp.tool()
def fetch_invoices(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch incoming vendor invoices to be processed (UNTRUSTED Read)."""
    return domain_fetch_invoices(db_path=db_path or DB_PATH)


@mcp.tool()
def initiate_payment(
    invoice_id: str,
    payee_account: str,
    amount_paise: int,
    decision_id: Optional[str] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Initiate disbursement for a vendor invoice (Moves Money).
    Debits ACC-MANDATE-01, credits payee, appends ledger entry.
    """
    return domain_initiate_payment(
        invoice_id=invoice_id,
        payee_account=payee_account,
        amount_paise=amount_paise,
        decision_id=decision_id,
        db_path=db_path or DB_PATH,
    )


@mcp.tool()
def write_ap_record(
    invoice_id: str,
    outcome: str,
    note: str,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Write an accounts-payable outcome record for an invoice."""
    return domain_write_ap_record(
        invoice_id=invoice_id,
        outcome=outcome,
        note=note,
        db_path=db_path or DB_PATH,
    )



if __name__ == "__main__":
    mcp.run()
