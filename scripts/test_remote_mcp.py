"""
Tests the standalone MCP HTTP/SSE server endpoints directly.
"""

import httpx
import json
import asyncio

BASE_URL = "http://127.0.0.1:8010"

def test_endpoints():
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    print("=" * 70)
    print("MANDATE — REMOTE READ-ONLY MCP SERVER VERIFICATION")
    print("=" * 70)

    # 1. Health Check
    res_health = client.get("/health")
    print("[1/5] Health Check (GET /health):")
    print(f"      Status Code: {res_health.status_code}")
    print(f"      Response   : {res_health.json()}")
    print("-" * 70)

    # 2. Initialize
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "ArmorIQ-Proxy", "version": "1.0.0"}
        }
    }
    res_init = client.post("/mcp", json=init_req)
    print("[2/5] MCP Initialize (POST /mcp):")
    print(f"      Status Code: {res_init.status_code}")
    print(f"      Response   : {json.dumps(res_init.json(), indent=2)}")
    print("-" * 70)

    # 3. Tools List
    tools_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    res_tools = client.post("/mcp", json=tools_req)
    print("[3/5] MCP Tools List (POST /mcp):")
    print(f"      Status Code: {res_tools.status_code}")
    print(f"      Response   : {json.dumps(res_tools.json(), indent=2)}")
    print("-" * 70)

    # 4. Tools Call (fetch_invoices)
    call_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "fetch_invoices",
            "arguments": {}
        }
    }
    res_call = client.post("/mcp", json=call_req)
    print("[4/5] MCP Tools Call - fetch_invoices (POST /mcp):")
    print(f"      Status Code: {res_call.status_code}")
    print(f"      Response   : {json.dumps(res_call.json(), indent=2)}")
    print("-" * 70)

    # 5. Tools Call (Disabled initiate_payment)
    disabled_req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "initiate_payment",
            "arguments": {"paise": 100}
        }
    }
    res_disabled = client.post("/mcp", json=disabled_req)
    print("[5/5] MCP Tools Call - Disabled Payment Tool (POST /mcp):")
    print(f"      Status Code: {res_disabled.status_code}")
    print(f"      Response   : {json.dumps(res_disabled.json(), indent=2)}")
    print("=" * 70)


if __name__ == "__main__":
    test_endpoints()
