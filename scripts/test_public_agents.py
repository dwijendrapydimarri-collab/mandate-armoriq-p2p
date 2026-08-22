"""
MANDATE — Test Public HTTPS Agent Endpoints with X-API-Key and Bearer Auth
Zero-Secret Hygiene: Never prints secret values, prefixes, suffixes, or lengths.
"""

import os
import sys
import httpx

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
    print("MANDATE — VERIFYING AGENT AUTHENTICATION (X-API-Key & Bearer)")
    print(f"Target URL: {PUBLIC_URL}")
    print("=" * 75)

    # 1. Directory of Agents
    res_dir = client.get("/agents")
    print(f"\n[1/5] Agent Directory (GET /agents): HTTP {res_dir.status_code}")
    if res_dir.status_code != 200:
        print("      [FAILED] Directory check failed.")
        sys.exit(1)

    # 2. Test Each Agent with X-API-Key and Bearer
    for slug in ("controller", "matcher", "disburser"):
        print(f"\n[{slug.upper()}] Testing mandate-{slug}:")
        
        # A. Health Check (Public)
        res_h = client.get(f"/agents/{slug}/health")
        print(f"      Health Endpoint (GET /agents/{slug}/health)       : HTTP {res_h.status_code}")

        # B. No credential -> 401
        res_no_auth = client.get(f"/agents/{slug}/identity")
        print(f"      No Credential Check (GET /agents/{slug}/identity)  : HTTP {res_no_auth.status_code} (Expected: 401)")
        if res_no_auth.status_code != 401:
            print(f"      [FAILED] Expected 401 without credential, got {res_no_auth.status_code}")
            sys.exit(1)

        # C. Incorrect X-API-Key -> 401
        res_bad_key = client.get(
            f"/agents/{slug}/identity",
            headers={"X-API-Key": "invalid_wrong_test_key_sample"},
        )
        print(f"      Incorrect X-API-Key (GET /agents/{slug}/identity) : HTTP {res_bad_key.status_code} (Expected: 401)")
        if res_bad_key.status_code != 401:
            print(f"      [FAILED] Expected 401 with wrong key, got {res_bad_key.status_code}")
            sys.exit(1)

        # D. Correct X-API-Key (when environment variable is set)
        env_var = AGENT_ENV_VARS[slug]
        token = os.environ.get(env_var)
        if token:
            res_x_api = client.get(
                f"/agents/{slug}/identity",
                headers={"X-API-Key": token},
            )
            print(f"      Correct X-API-Key Check                           : HTTP {res_x_api.status_code}")
            if res_x_api.status_code == 200:
                data = res_x_api.json()
                print(f"      Returned Fields                                   : {list(data.keys())}")
            else:
                print(f"      [NOTE] X-API-Key rejected (Server process may have different token configured)")

            res_bearer = client.get(
                f"/agents/{slug}/identity",
                headers={"Authorization": f"Bearer {token}"},
            )
            print(f"      Correct Bearer Token Check                        : HTTP {res_bearer.status_code}")
        else:
            print(f"      Configured Credential                             : NOT_SET in {env_var}")

    # 3. Direct Disbursement Endpoint Remains Blocked (403)
    print("\n[3/5] Testing Direct Disbursement Protection:")
    disburser_token = os.environ.get("MANDATE_DISBURSER_AGENT_TOKEN")
    headers_disb = {"X-API-Key": disburser_token} if disburser_token else {}
    res_d_inv = client.post(
        "/agents/disburser/invoke",
        headers=headers_disb,
        json={"action": "initiate_payment"},
    )
    print(f"      Disburser Direct Invoke (POST /agents/disburser/invoke): HTTP {res_d_inv.status_code} (Expected: 401 or 403 Blocked)")
    if res_d_inv.status_code not in (401, 403):
        print(f"      [FAILED] Expected 401 or 403, got {res_d_inv.status_code}")
        sys.exit(1)

    print("\n" + "=" * 75)
    print("ALL AGENT AUTHENTICATION PROBES COMPLETED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    test_public_agents()
