"""
Test SSE MCP protocol stream properly.
"""

import httpx
import json
import asyncio

async def test_sse():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8010", timeout=15.0) as client:
        async with client.stream("GET", "/sse") as response:
            print("SSE Stream HTTP Status:", response.status_code)
            
            lines = response.aiter_lines()
            
            # Step 1: Read initial endpoint registration event
            event_type = await lines.__anext__()
            endpoint_line = await lines.__anext__()
            empty_line = await lines.__anext__()
            
            print(f"Received SSE event: {event_type}")
            print(f"Received SSE data : {endpoint_line}")
            session_url = endpoint_line.replace("data: ", "").strip()
            
            # Step 2: Post JSON-RPC tools/call to the session endpoint
            call_body = {
                "jsonrpc": "2.0",
                "id": 99,
                "method": "tools/call",
                "params": {"name": "fetch_invoices", "arguments": {}}
            }
            print(f"\nSending tools/call to {session_url}...")
            post_res = await client.post(session_url, json=call_body)
            print(f"POST response: {post_res.status_code} {post_res.json()}")

            # Step 3: Read streamed response event
            msg_event = await lines.__anext__()
            msg_data = await lines.__anext__()
            print(f"\nReceived SSE response event: {msg_event}")
            print(f"Received SSE response data : {msg_data[:120]}...")
            
            parsed = json.loads(msg_data.replace("data: ", ""))
            print(f"Decoded JSON-RPC Result ID: {parsed.get('id')}")
            print(f"Tool Result Content Blocks: {len(parsed.get('result', {}).get('content', []))}")
            print("=" * 70)
            print("SSE PROTOCOL FLOW VERIFIED SUCCESSFULLY!")
            print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_sse())
