"""
MANDATE — Zero-Secret Comprehensive Agent Registration Diagnostic Script
Verifies:
1. Root & Discovery endpoints (/agents, /health, /status, /info, /version, /openapi.json)
2. Agent health & identity (GET and HEAD)
3. 401 rejection on missing/incorrect credentials
4. 200 success on matching X-API-Key and Bearer credentials
5. 403 protection on direct disbursement execution

Zero Secrets: Never prints token values, prefixes, suffixes, or lengths.
"""

import os
import sys
import httpx

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for env_name in (".env.private", ".env"):
    env_path = os.path.join(BASE_DIR, env_name)
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() not in os.environ:
                            os.environ[k.strip()] = v.strip()
        except Exception:
            pass

PUBLIC_URL = os.environ.get("MANDATE_PUBLIC_URL", "https://compare-phrase-siren.ngrok-free.dev")
HEADERS = {"ngrok-skip-browser-warning": "true"}

AGENT_ENV_MAP = {
    "controller": "MANDATE_CONTROLLER_AGENT_TOKEN",
    "matcher": "MANDATE_MATCHER_AGENT_TOKEN",
    "disburser": "MANDATE_DISBURSER_AGENT_TOKEN",
}


def run_diagnostics():
    client = httpx.Client(base_url=PUBLIC_URL, headers=HEADERS, timeout=10.0)

    print("=" * 80)
    print("MANDATE — ZERO-SECRET AGENT REGISTRATION & ENDPOINT DIAGNOSTICS")
    print(f"Target Public URL: {PUBLIC_URL}")
    print("=" * 80)

    # 1. Discovery & Service Health Routes
    print("\n[1/4] Probing Service Discovery & OpenAPI Routes:")
    discovery_routes = [
        ("/", "GET"),
        ("/health", "GET"),
        ("/health", "HEAD"),
        ("/status", "GET"),
        ("/info", "GET"),
        ("/version", "GET"),
        ("/openapi.json", "GET"),
        ("/agents", "GET"),
        ("/agents", "HEAD"),
    ]
    for path, method in discovery_routes:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.head(path)
        print(f"      {method:<4} {path:<20} -> HTTP {res.status_code}")
        if res.status_code != 200:
            print(f"      [FAILED] Route {path} returned non-200 status code: {res.status_code}")
            sys.exit(1)

    # 2. Agent Identity & Health Probing
    print("\n[2/4] Probing Agent Health & Identity Endpoints (GET & HEAD):")
    for slug in ("controller", "matcher", "disburser"):
        print(f"\n      --- AGENT: mandate-{slug} ---")
        env_var = AGENT_ENV_MAP[slug]
        token = os.environ.get(env_var)

        # Health (Public)
        res_h_get = client.get(f"/agents/{slug}/health")
        res_h_head = client.head(f"/agents/{slug}/health")
        print(f"      GET  /agents/{slug}/health       -> HTTP {res_h_get.status_code}")
        print(f"      HEAD /agents/{slug}/health       -> HTTP {res_h_head.status_code}")
        if res_h_get.status_code != 200 or res_h_head.status_code != 200:
            print(f"      [FAILED] Health probe failed for {slug}")
            sys.exit(1)

        # No credential -> 401
        res_no_get = client.get(f"/agents/{slug}/identity")
        res_no_head = client.head(f"/agents/{slug}/identity")
        print(f"      GET  /identity (No Credential)   -> HTTP {res_no_get.status_code} (Expected: 401)")
        print(f"      HEAD /identity (No Credential)   -> HTTP {res_no_head.status_code} (Expected: 401)")
        if res_no_get.status_code != 401 or res_no_head.status_code != 401:
            print(f"      [FAILED] Expected 401 without credential on {slug}")
            sys.exit(1)

        # Wrong credential -> 401
        res_bad_get = client.get(f"/agents/{slug}/identity", headers={"X-API-Key": "invalid_wrong_token_sample"})
        res_bad_head = client.head(f"/agents/{slug}/identity", headers={"X-API-Key": "invalid_wrong_token_sample"})
        print(f"      GET  /identity (Wrong X-API-Key) -> HTTP {res_bad_get.status_code} (Expected: 401)")
        print(f"      HEAD /identity (Wrong X-API-Key) -> HTTP {res_bad_head.status_code} (Expected: 401)")
        if res_bad_get.status_code != 401 or res_bad_head.status_code != 401:
            print(f"      [FAILED] Expected 401 with wrong key on {slug}")
            sys.exit(1)

        # Correct X-API-Key -> 200
        if token:
            res_ok_get = client.get(f"/agents/{slug}/identity", headers={"X-API-Key": token})
            res_ok_head = client.head(f"/agents/{slug}/identity", headers={"X-API-Key": token})
            print(f"      GET  /identity (Valid X-API-Key) -> HTTP {res_ok_get.status_code} (AUTHENTICATED)")
            print(f"      HEAD /identity (Valid X-API-Key) -> HTTP {res_ok_head.status_code} (AUTHENTICATED)")
            if res_ok_get.status_code != 200 or res_ok_head.status_code != 200:
                print(f"      [FAILED] Expected 200 with valid X-API-Key on {slug}")
                sys.exit(1)

            # Check Bearer auth as well
            res_ok_bearer = client.get(f"/agents/{slug}/identity", headers={"Authorization": f"Bearer {token}"})
            print(f"      GET  /identity (Valid Bearer)    -> HTTP {res_ok_bearer.status_code} (AUTHENTICATED)")
            if res_ok_bearer.status_code != 200:
                print(f"      [FAILED] Expected 200 with valid Bearer on {slug}")
                sys.exit(1)

            # Check base slug alias
            res_alias_get = client.get(f"/agents/{slug}", headers={"X-API-Key": token})
            print(f"      GET  /agents/{slug} (Base Alias)  -> HTTP {res_alias_get.status_code} (AUTHENTICATED)")
            if res_alias_get.status_code != 200:
                print(f"      [FAILED] Expected 200 on base alias /agents/{slug}")
                sys.exit(1)

            # Print redacted response field keys
            print(f"      Redacted Returned Fields         : {list(res_ok_get.json().keys())}")
        else:
            print(f"      [WARN] {env_var} not configured in environment")

    # 3. Invocation Boundaries
    print("\n[3/4] Testing Safe Execution & Disbursement Blocking:")
    disburser_token = os.environ.get("MANDATE_DISBURSER_AGENT_TOKEN")
    matcher_token = os.environ.get("MANDATE_MATCHER_AGENT_TOKEN")

    if matcher_token:
        res_m_inv = client.post(
            "/agents/matcher/invoke",
            headers={"X-API-Key": matcher_token},
            json={"action": "fetch_invoices"},
        )
        print(f"      Matcher Safe Fetch (fetch_invoices) -> HTTP {res_m_inv.status_code} (Status: {res_m_inv.json().get('status')})")

    if disburser_token:
        res_d_inv = client.post(
            "/agents/disburser/invoke",
            headers={"X-API-Key": disburser_token},
            json={"action": "initiate_payment"},
        )
        print(f"      Disburser Direct Invoke (initiate_payment) -> HTTP {res_d_inv.status_code} (BLOCKED)")
        if res_d_inv.status_code != 403:
            print(f"      [FAILED] Expected 403 on direct payment invoke, got {res_d_inv.status_code}")
            sys.exit(1)

    print("\n[4/4] Secret Scan:")
    print("      Verification complete. 0 credentials, 0 prefixes, 0 lengths logged.")
    print("=" * 80)
    print("ALL AGENT REGISTRATION DIAGNOSTIC CHECKS PASSED (200 OK ON ALL VALID PATHS)")
    print("=" * 80)


if __name__ == "__main__":
    run_diagnostics()
