"""
MANDATE — P2 Verification Script
Verifies that:
1. Tool listing returns exactly 5 tools.
2. list_open_purchase_orders returns all 7 seeded POs.
3. get_vendor_master returns all 5 seeded approved vendors.
"""

import sys
import os
import asyncio

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.mcp_server.client import default_mcp_client
from backend.seed import reset_to_seed


async def run_p2_verification():
    print("Resetting database to seed state...")
    reset_to_seed()

    print("\n--- 1. Listing Tools ---")
    tools = await default_mcp_client.list_tools()
    print(f"Discovered {len(tools)} tools: {tools}")
    expected_tools = {
        "list_open_purchase_orders",
        "get_vendor_master",
        "fetch_invoices",
        "initiate_payment",
        "write_ap_record",
    }
    assert set(tools) == expected_tools, f"Expected {expected_tools}, got {set(tools)}"
    print("[PASS] Tool listing contains exactly the 5 specified tools.")

    print("\n--- 2. Calling Trusted Read: list_open_purchase_orders ---")
    pos = await default_mcp_client.call_tool("list_open_purchase_orders", {})
    print(f"Retrieved {len(pos)} open purchase orders.")
    assert len(pos) == 7, f"Expected 7 POs, got {len(pos)}"
    print(f"Sample PO: {pos[0]['id']} -> Vendor {pos[0]['vendor_id']} for {pos[0]['amount_paise']} paise")
    print("[PASS] list_open_purchase_orders returned all seeded POs.")

    print("\n--- 3. Calling Trusted Read: get_vendor_master ---")
    vendors = await default_mcp_client.call_tool("get_vendor_master", {})
    print(f"Retrieved {len(vendors)} vendors.")
    assert len(vendors) == 5, f"Expected 5 vendors, got {len(vendors)}"
    print(f"Sample Vendor: {vendors[0]['id']} - {vendors[0]['name']} (A/C: {vendors[0]['bank_account']})")
    print("[PASS] get_vendor_master returned all seeded vendors.")

    print("\n==========================================")
    print("PHASE P2 GATE PASSED: 5 tools listed & trusted reads return seed fixtures.")
    print("==========================================")


if __name__ == "__main__":
    asyncio.run(run_p2_verification())
