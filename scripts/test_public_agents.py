"""
MANDATE — Test Public HTTPS Agent Endpoints (Zero-Secret Hygiene)
Verifies health, authenticated identity, and safe execution boundaries for:
1. mandate-controller
2. mandate-matcher
3. mandate-disburser

Reports ONLY 'CONFIGURED', 'AUTHENTICATED', or 'REJECTED'.
Never prints secret values, prefixes, suffixes, or lengths.
"""

import os
import sys
import httpx
import json

PUBLIC_URL = os.environ.get("MANDATE_PUBLIC_URL", "https://compare-phrase-siren.ngrok-free.dev")
HEADERS = {"ngrok-skip-browser-warning": "true"}

AGENT_ENV_VARS = {
    "controller": "MANDATE_CONTROLLER_AGENT_TOKEN",
    "matcher": "MANDATE_MATCHER_AGENT_TOKEN",
    "disburser": "MANDATE_DISBURSER_AGENT_TOKEN",
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
    if res_dir.status_code == 200:
        agents = [a.get("agent_id") for a in res_dir.json().get("agents", [])]
        print(f"      Registered Agents: {agents}")
    else:
        print(f"      [FAILED] Unable to list agents: HTTP {res_dir.status_code}")
        sys.exit(1)

    # 2-4. Test Each Agent
    for slug in ("controller", "matcher", "disburser"):
        print(f"\n[{slug.upper()}] Testing mandate-{slug}:")
        # Health Check (Public)
        res_h = client.get(f"/agents/{slug}/health")
        print(f"      Health Endpoint  : HTTP {res_h.status_code} ({res_h.json().get('status', 'FAIL')})")
        if res_h.status_code != 200:
            print(f"      [FAILED] Health check failed for mandate-{slug}")
            sys.exit(1)

        # Authenticated Identity Check
        env_var = AGENT_ENV_VARS[slug]
        token = os.environ.get(env_var)
        if token:
            print(f"      Agent Credential : CONFIGURED in {env_var}")
            res_ident = client.get(
                f"/agents/{slug}/identity",
                headers={"Authorization": f"Bearer {token}"},
            )
            print(f"      Identity Check   : HTTP {res_ident.status_code} ({res_ident.json().get('auth_status', 'REJECTED')})")
            if res_ident.status_code != 200:
                print(f"      [FAILED] Identity check failed for mandate-{slug}")
                sys.exit(1)
        else:
            print(f"      Agent Credential : NOT_SET in {env_var} (Skipping authenticated identity probe)")

    # 5. Test Unauthenticated Rejection (401 Unauthorized)
    print("\n[5/6] Testing Unauthenticated Rejection (GET /agents/matcher/identity without token):")
    res_unauth = client.get("/agents/matcher/identity")
    print(f"      Status: {res_unauth.status_code} (Expected: 401)")
    if res_unauth.status_code != 401:
        print(f"      [FAILED] Expected 401 for unauthenticated request, got {res_unauth.status_code}")
        sys.exit(1)

    # 6. Test Safe Invocation Boundaries
    print("\n[6/6] Testing Safe Invocation Boundary:")
    matcher_token = os.environ.get("MANDATE_MATCHER_AGENT_TOKEN")
    if matcher_token:
        res_m_inv = client.post(
            "/agents/matcher/invoke",
            headers={"Authorization": f"Bearer {matcher_token}"},
            json={"action": "fetch_invoices"},
        )
        print(f"      Matcher Safe Fetch   : HTTP {res_m_inv.status_code} (Status: {res_m_inv.json().get('status')})")
    else:
        print("      Matcher Safe Fetch   : SKIPPED (MANDATE_MATCHER_AGENT_TOKEN not set)")

    disburser_token = os.environ.get("MANDATE_DISBURSER_AGENT_TOKEN")
    if disburser_token:
        res_d_inv = client.post(
            "/agents/disburser/invoke",
            headers={"Authorization": f"Bearer {disburser_token}"},
            json={"action": "initiate_payment"},
        )
        print(f"      Disburser Direct Call: HTTP {res_d_inv.status_code} (Expected: 403 Blocked)")
        if res_d_inv.status_code != 403:
            print(f"      [FAILED] Expected 403 for direct disbursement, got {res_d_inv.status_code}")
            sys.exit(1)
    else:
        print("      Disburser Direct Call: SKIPPED (MANDATE_DISBURSER_AGENT_TOKEN not set)")

    print("\n" + "=" * 75)
    print("ALL PUBLIC AGENT ENDPOINT CHECKS PASSED (ZERO SECRETS EXPOSED)!")
    print("=" * 75)


if __name__ == "__main__":
    test_public_agents()
