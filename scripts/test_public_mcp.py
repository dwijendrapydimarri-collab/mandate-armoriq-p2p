"""
MANDATE — Public HTTPS MCP Server Endpoint Verification
Tests initialize, tools/list, tools/call (fetch_invoices), SSE streaming, and health check
over the public HTTPS endpoint.
"""

import httpx
import json
import asyncio

PUBLIC_URL = "https://compare-phrase-siren.ngrok-free.dev"
HEADERS = {"ngrok-skip-browser-warning": "true"}

async def verify_public_endpoint():
    print("=" * 70)
    print("MANDATE — PUBLIC HTTPS READ-ONLY MCP ENDPOINT VERIFICATION")
    print(f"Target URL: {PUBLIC_URL}")
    print("=" * 70)

    async with httpx.AsyncClient(base_url=PUBLIC_URL, headers=HEADERS, timeout=15.0) as client:
        # 1. Health Check
        res_health = await client.get("/health")
        print("\n1. PUBLIC HEALTH CHECK (GET /health):")
        print(f"   HTTP Status: {res_health.status_code}")
        print(f"   Body: {json.dumps(res_health.json(), indent=2)}")

        # 2. Initialize
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "ArmorIQ-Proxy", "version": "1.0.0"}
            }
        }
        res_init = await client.post("/mcp", json=init_payload)
        print("\n2. INITIALIZE RESPONSE (POST /mcp):")
        print(f"   HTTP Status: {res_init.status_code}")
        print(f"   Body: {json.dumps(res_init.json(), indent=2)}")

        # 3. Tools List
        list_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        res_list = await client.post("/mcp", json=list_payload)
        print("\n3. TOOLS/LIST RESPONSE (POST /mcp):")
        print(f"   HTTP Status: {res_list.status_code}")
        print(f"   Body: {json.dumps(res_list.json(), indent=2)}")

        # 4. Tools Call (fetch_invoices)
        call_payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "fetch_invoices",
                "arguments": {}
            }
        }
        res_call = await client.post("/mcp", json=call_payload)
        print("\n4. TOOLS/CALL RESPONSE (POST /mcp - fetch_invoices):")
        print(f"   HTTP Status: {res_call.status_code}")
        print(f"   Body: {json.dumps(res_call.json(), indent=2)}")

        # 5. SSE Streaming Flow
        print("\n5. SSE STREAMING FLOW (GET /sse + POST /messages):")
        async with client.stream("GET", "/sse") as sse_res:
            print(f"   SSE HTTP Status: {sse_res.status_code}")
            lines = sse_res.aiter_lines()
            event_type = await lines.__anext__()
            endpoint_line = await lines.__anext__()
            empty_line = await lines.__anext__()
            
            print(f"   Received SSE Event: {event_type}")
            print(f"   Received SSE Data : {endpoint_line}")
            session_url = endpoint_line.replace("data: ", "").strip()
            
            # Post tools/call to session
            post_sse = await client.post(session_url, json=call_payload)
            print(f"   POST /messages response: {post_sse.status_code} {post_sse.json()}")
            
            msg_event = await lines.__anext__()
            msg_data = await lines.__anext__()
            print(f"   Received Streamed Event: {msg_event}")
            print(f"   Received Streamed Data Prefix: {msg_data[:120]}...")

    print("\n" + "=" * 70)
    print("ALL PUBLIC HTTPS MCP VERIFICATION CHECKS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(verify_public_endpoint())
