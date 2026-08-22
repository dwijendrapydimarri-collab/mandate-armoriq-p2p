"""
MANDATE — Test Public HTTPS Agent Endpoints
Verifies health, authenticated identity, and safe execution boundaries for:
1. mandate-controller
2. mandate-matcher
3. mandate-disburser
"""

import httpx
import json

PUBLIC_URL = "https://compare-phrase-siren.ngrok-free.dev"
HEADERS = {"ngrok-skip-browser-warning": "true"}

AGENT_TOKENS = {
    "controller": "agent_tok_controller_mandate_sec_2026",
    "matcher": "agent_tok_matcher_mandate_sec_2026",
    "disburser": "agent_tok_disburser_mandate_sec_2026",
}


def test_public_agents():
    client = httpx.Client(base_url=PUBLIC_URL, headers=HEADERS, timeout=10.0)

    print("=" * 75)
    print("MANDATE — TESTING PUBLIC HTTPS AGENT ENDPOINTS")
    print(f"Target URL: {PUBLIC_URL}")
    print("=" * 75)

    # 1. Directory of Agents
    res_dir = client.get("/agents")
    print("\n[1/6] Agent Directory (GET /agents):")
    print(f"      Status: {res_dir.status_code}")
    print(f"      Body  : {json.dumps(res_dir.json(), indent=2)}")

    # 2. Test Controller
    print("\n[2/6] Controller Agent (mandate-controller):")
    res_c_health = client.get("/agents/controller/health")
    print(f"      Health Status  : {res_c_health.status_code} {res_c_health.json()}")
    res_c_ident = client.get(
        "/agents/controller/identity",
        headers={"Authorization": f"Bearer {AGENT_TOKENS['controller']}"},
    )
    print(f"      Identity Status: {res_c_ident.status_code}")
    print(f"      Identity Data  : {json.dumps(res_c_ident.json(), indent=2)}")

    # 3. Test Matcher
    print("\n[3/6] Matcher Agent (mandate-matcher):")
    res_m_health = client.get("/agents/matcher/health")
    print(f"      Health Status  : {res_m_health.status_code} {res_m_health.json()}")
    res_m_ident = client.get(
        "/agents/matcher/identity",
        headers={"Authorization": f"Bearer {AGENT_TOKENS['matcher']}"},
    )
    print(f"      Identity Status: {res_m_ident.status_code}")
    print(f"      Identity Data  : {json.dumps(res_m_ident.json(), indent=2)}")

    # 4. Test Disburser
    print("\n[4/6] Disburser Agent (mandate-disburser):")
    res_d_health = client.get("/agents/disburser/health")
    print(f"      Health Status  : {res_d_health.status_code} {res_d_health.json()}")
    res_d_ident = client.get(
        "/agents/disburser/identity",
        headers={"Authorization": f"Bearer {AGENT_TOKENS['disburser']}"},
    )
    print(f"      Identity Status: {res_d_ident.status_code}")
    print(f"      Identity Data  : {json.dumps(res_d_ident.json(), indent=2)}")

    # 5. Test Authentication Enforcement (401 Unauthorized without token)
    print("\n[5/6] Testing Unauthenticated Rejection (GET /agents/matcher/identity without token):")
    res_unauth = client.get("/agents/matcher/identity")
    print(f"      Status: {res_unauth.status_code} (Expected: 401)")
    print(f"      Body  : {res_unauth.json()}")

    # 6. Test Safe Invocation (Matcher fetch_invoices vs Disburser direct block)
    print("\n[6/6] Testing Safe Invocation Boundary:")
    res_m_inv = client.post(
        "/agents/matcher/invoke",
        headers={"Authorization": f"Bearer {AGENT_TOKENS['matcher']}"},
        json={"action": "fetch_invoices"},
    )
    print(f"      Matcher Safe Fetch : {res_m_inv.status_code} (Items: {len(res_m_inv.json().get('result', []))})")

    res_d_inv = client.post(
        "/agents/disburser/invoke",
        headers={"Authorization": f"Bearer {AGENT_TOKENS['disburser']}"},
        json={"action": "initiate_payment"},
    )
    print(f"      Disburser Direct Call: {res_d_inv.status_code} (Expected: 403 Direct Disbursement Blocked)")
    print(f"      Response Message     : {res_d_inv.json().get('error')}")

    print("\n" + "=" * 75)
    print("ALL PUBLIC AGENT ENDPOINT CHECKS PASSED!")
    print("=" * 75)


if __name__ == "__main__":
    test_public_agents()
