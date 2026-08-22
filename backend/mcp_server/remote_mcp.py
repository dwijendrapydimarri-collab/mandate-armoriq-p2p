"""
MANDATE — Remote Read-Only MCP HTTP/SSE Server
Exposes a standards-compliant Model Context Protocol (MCP) server over HTTP and SSE.
Specifically exposes ONLY `fetch_invoices` (read-only) for initial cloud proxy verification.
Payment tools (initiate_payment) are disabled until read authorization is proven.
"""

import os
import sys
import json
import uuid
import asyncio
import logging
from typing import Dict, Any, List, Optional
from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Ensure repository root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.domain import domain_fetch_invoices, DB_PATH

# Load local environment variables from gitignored .env / .env.private if present
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


logger = logging.getLogger("remote_mcp")
logging.basicConfig(level=logging.INFO)

# Active SSE sessions: session_id -> asyncio.Queue
active_sessions: Dict[str, asyncio.Queue] = {}

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {
    "name": "mandate-mcp",
    "version": "1.0.0",
}

FETCH_INVOICES_TOOL = {
    "name": "fetch_invoices",
    "description": "Fetch routine incoming vendor invoices pending three-way matching (Read-Only)",
    "inputSchema": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Optional invoice status filter (e.g. 'pending')",
                "default": "pending",
            }
        },
        "required": [],
    },
}


def handle_jsonrpc_request(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Processes an incoming JSON-RPC 2.0 MCP message."""
    req_id = body.get("id")
    method = body.get("method")
    params = body.get("params", {})

    if not method:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32600, "message": "Invalid Request: Missing 'method' field"},
        }

    # 1. MCP initialize
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {"listChanged": False},
                },
                "serverInfo": SERVER_INFO,
            },
        }

    # 2. MCP initialized notification
    if method in ("notifications/initialized", "initialized"):
        return None  # Notifications do not require a response

    # 3. MCP ping
    if method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {},
        }

    # 4. tools/list
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [FETCH_INVOICES_TOOL],
            },
        }

    # 5. tools/call
    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "fetch_invoices":
            try:
                invoices = domain_fetch_invoices(db_path=DB_PATH)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(invoices, indent=2),
                            }
                        ],
                        "isError": False,
                    },
                }
            except Exception as e:
                logger.error("Error executing fetch_invoices: %s", e)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error fetching invoices: {str(e)}",
                            }
                        ],
                        "isError": True,
                    },
                }

        # Any unauthorized / unexposed tool (including payment tools)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Tool '{tool_name}' is not registered or disabled on read-only MCP verification endpoint",
            },
        }

    # Unknown method
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method '{method}' not found"},
    }


async def health_check(request):
    """Health check endpoint for ArmorIQ dashboard and cloud probes."""
    return JSONResponse({
        "status": "ok",
        "service": "mandate-mcp",
        "protocol": "mcp-http-sse",
        "version": SERVER_INFO["version"],
        "exposed_tools": ["fetch_invoices"],
        "auth_state": "READ_ONLY_ACTIVE",
    })


async def handle_http_mcp(request):
    """Direct HTTP POST JSON-RPC endpoint (POST /mcp or POST /)."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
            status_code=400,
        )

    # Handle batch or single request
    if isinstance(body, list):
        responses = [res for item in body if (res := handle_jsonrpc_request(item)) is not None]
        return JSONResponse(responses)
    else:
        res = handle_jsonrpc_request(body)
        if res is None:
            return Response(status_code=204)
        return JSONResponse(res)


async def sse_endpoint(request):
    """SSE connection endpoint (GET /sse)."""
    session_id = str(uuid.uuid4())
    queue: asyncio.Queue = asyncio.Queue()
    active_sessions[session_id] = queue

    logger.info("New SSE MCP connection established: session_id=%s", session_id)

    async def event_generator():
        # 1. Send initial endpoint registration event
        yield f"event: endpoint\ndata: /messages?session_id={session_id}\n\n"

        try:
            while True:
                try:
                    # Wait for message with 15s heartbeat keepalive
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"event: message\ndata: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            active_sessions.pop(session_id, None)
            logger.info("SSE connection closed: session_id=%s", session_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def sse_messages(request):
    """Message ingestion for active SSE session (POST /messages)."""
    session_id = request.query_params.get("session_id")
    if not session_id or session_id not in active_sessions:
        return JSONResponse({"error": "Invalid or missing session_id"}, status_code=400)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    res = handle_jsonrpc_request(body)
    if res is not None:
        await active_sessions[session_id].put(res)

    return JSONResponse({"status": "accepted"}, status_code=202)


# -------------------------------------------------------------
# Dedicated Agent Identity & Health Endpoints
# -------------------------------------------------------------

import hmac
import secrets

AGENT_REGISTRY = {
    "controller": {
        "agent_id": "mandate-controller",
        "name": "Mandate Controller Root Orchestrator",
        "version": "1.0.0",
        "role": "ROOT_MISSION_ORCHESTRATOR",
        "capabilities": ["capture_plan", "get_intent_token", "delegate", "seal_authority"],
        "description": "Root orchestrator responsible for trusted authority sealing and capability delegation",
    },
    "matcher": {
        "agent_id": "mandate-matcher",
        "name": "Mandate Matcher Specialist Agent",
        "version": "1.0.0",
        "role": "SPECIALIST_SUBAGENT_READ_ONLY",
        "capabilities": ["fetch_invoices", "verify_match"],
        "spend_ceiling_paise": 0,
        "description": "Specialist subagent strictly bounded to read-only invoice fetching and 3-way matching",
    },
    "disburser": {
        "agent_id": "mandate-disburser",
        "name": "Mandate Disburser Specialist Agent",
        "version": "1.0.0",
        "role": "SPECIALIST_SUBAGENT_DISBURSER",
        "capabilities": ["initiate_payment"],
        "spend_ceiling_paise": 50000000,
        "description": "Disbursement subagent bounded by CFO spend ceilings and approved payee accounts",
    },
}


def _get_agent_token(agent_slug: str) -> str:
    """Retrieves agent token from environment or generates a secure ephemeral token in memory."""
    env_var_map = {
        "controller": "MANDATE_CONTROLLER_AGENT_TOKEN",
        "matcher": "MANDATE_MATCHER_AGENT_TOKEN",
        "disburser": "MANDATE_DISBURSER_AGENT_TOKEN",
    }
    env_key = env_var_map.get(agent_slug.lower())
    if env_key and os.environ.get(env_key):
        return os.environ[env_key]

    if not hasattr(_get_agent_token, "_ephemeral_tokens"):
        _get_agent_token._ephemeral_tokens = {}  # type: ignore
    if agent_slug not in _get_agent_token._ephemeral_tokens:  # type: ignore
        _get_agent_token._ephemeral_tokens[agent_slug] = secrets.token_urlsafe(32)  # type: ignore
    return _get_agent_token._ephemeral_tokens[agent_slug]  # type: ignore


def _verify_agent_auth(request, agent_slug: str) -> bool:
    """Validates X-API-Key, Bearer token, or X-Agent-Key header using constant-time comparison."""
    expected_token = _get_agent_token(agent_slug)
    if not expected_token:
        return False

    auth_header = request.headers.get("authorization", "")
    x_api_key = request.headers.get("x-api-key", "")
    x_agent_key = request.headers.get("x-agent-key", "")

    provided_token = None
    if x_api_key:
        provided_token = x_api_key.strip()
    elif auth_header.lower().startswith("bearer "):
        provided_token = auth_header.split(" ", 1)[1].strip()
    elif x_agent_key:
        provided_token = x_agent_key.strip()

    if not provided_token:
        return False

    return hmac.compare_digest(provided_token, expected_token)




async def list_agents(request):
    """Returns directory of all registered Mandate agents."""
    agents_summary = [
        {
            "agent_id": info["agent_id"],
            "name": info["name"],
            "role": info["role"],
            "capabilities": info["capabilities"],
            "health_endpoint": f"/agents/{slug}/health",
            "identity_endpoint": f"/agents/{slug}/identity",
        }
        for slug, info in AGENT_REGISTRY.items()
    ]
    return JSONResponse({"status": "ok", "service": "mandate-agents", "agents": agents_summary})


async def agent_health(request):
    """Health check for an individual registered agent."""
    agent_slug = request.path_params.get("agent_slug", "").lower()
    if agent_slug not in AGENT_REGISTRY:
        return JSONResponse({"error": f"Agent '{agent_slug}' not found"}, status_code=404)

    agent_info = AGENT_REGISTRY[agent_slug]
    return JSONResponse({
        "status": "ok",
        "agent_id": agent_info["agent_id"],
        "name": agent_info["name"],
        "role": agent_info["role"],
        "uptime": "HEALTHY",
        "governance_mode": "GATEWAY_ENFORCED",
    })


async def agent_identity(request):
    """Authenticated agent identity & capability inspection."""
    agent_slug = request.path_params.get("agent_slug", "").lower()
    if agent_slug not in AGENT_REGISTRY:
        return JSONResponse({"error": f"Agent '{agent_slug}' not found"}, status_code=404)

    agent_info = AGENT_REGISTRY[agent_slug]

    # Verify authentication
    if not _verify_agent_auth(request, agent_slug):
        return JSONResponse(
            {
                "error": "Unauthorized: Valid Agent Bearer Token or X-Agent-Key required",
                "agent_id": agent_info["agent_id"],
                "auth_scheme": "Bearer <agent_token>",
            },
            status_code=401,
        )

    return JSONResponse({
        "status": "ok",
        "agent_id": agent_info["agent_id"],
        "name": agent_info["name"],
        "role": agent_info["role"],
        "capabilities": agent_info["capabilities"],
        "spend_ceiling_paise": agent_info.get("spend_ceiling_paise", 0),
        "auth_status": "AUTHENTICATED",
        "mcp_server": "mandate-mcp",
    })


async def agent_invoke(request):
    """Safe agent invocation entrypoint for test queries."""
    agent_slug = request.path_params.get("agent_slug", "").lower()
    if agent_slug not in AGENT_REGISTRY:
        return JSONResponse({"error": f"Agent '{agent_slug}' not found"}, status_code=404)

    agent_info = AGENT_REGISTRY[agent_slug]

    # Verify authentication
    if not _verify_agent_auth(request, agent_slug):
        return JSONResponse({"error": "Unauthorized"}, status_code=401)


    try:
        body = await request.json()
    except Exception:
        body = {}

    action = body.get("action", "")

    # Matcher can only execute fetch_invoices
    if agent_slug == "matcher":
        if action in ("fetch_invoices", ""):
            invoices = domain_fetch_invoices(db_path=DB_PATH)
            return JSONResponse({
                "agent_id": agent_info["agent_id"],
                "action": "fetch_invoices",
                "result": invoices,
                "status": "COMPLETED",
            })
        else:
            return JSONResponse(
                {
                    "error": f"CAPABILITY_ATTENUATION_BLOCKED: Matcher is not authorized to execute '{action}'",
                    "allowed_capabilities": agent_info["capabilities"],
                },
                status_code=403,
            )

    # Disburser and Controller require full Gateway Intent Token — direct tool calls blocked
    return JSONResponse(
        {
            "error": "DIRECT_DISBURSEMENT_BLOCKED: Money-moving tools cannot be invoked directly via agent endpoints; must pass through gateway.py with ArmorIQ IntentToken.",
            "agent_id": agent_info["agent_id"],
        },
        status_code=403,
    )


async def openapi_schema(request):
    """Standard OpenAPI 3.0 descriptor for agent registration discovery."""
    schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "MANDATE Agent Service & MCP Bridge",
            "version": "1.0.0",
            "description": "ArmorIQ Bounded Autonomous Procure-to-Pay Agent Service",
        },
        "paths": {
            "/agents/controller/identity": {
                "get": {
                    "summary": "Mandate Controller Identity",
                    "security": [{"ApiKeyAuth": []}, {"BearerAuth": []}],
                    "responses": {"200": {"description": "Authenticated Agent Identity"}},
                }
            },
            "/agents/matcher/identity": {
                "get": {
                    "summary": "Mandate Matcher Identity",
                    "security": [{"ApiKeyAuth": []}, {"BearerAuth": []}],
                    "responses": {"200": {"description": "Authenticated Agent Identity"}},
                }
            },
            "/agents/disburser/identity": {
                "get": {
                    "summary": "Mandate Disburser Identity",
                    "security": [{"ApiKeyAuth": []}, {"BearerAuth": []}],
                    "responses": {"200": {"description": "Authenticated Agent Identity"}},
                }
            },
            "/mcp": {
                "post": {
                    "summary": "Model Context Protocol JSON-RPC Endpoint",
                    "responses": {"200": {"description": "MCP JSON-RPC response"}},
                }
            },
        },
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
                "BearerAuth": {"type": "http", "scheme": "bearer"},
            }
        },
    }
    return JSONResponse(schema)


async def openapi_info(request):
    """Basic service info descriptor."""
    return JSONResponse({
        "service": "mandate-agent-service",
        "version": "1.0.0",
        "status": "healthy",
        "agents": ["mandate-controller", "mandate-matcher", "mandate-disburser"],
        "mcp_server": "mandate-mcp",
    })


routes = [
    Route("/health", health_check, methods=["GET", "HEAD"]),
    Route("/status", health_check, methods=["GET", "HEAD"]),
    Route("/", health_check, methods=["GET", "HEAD"]),
    Route("/info", openapi_info, methods=["GET", "HEAD"]),
    Route("/version", openapi_info, methods=["GET", "HEAD"]),
    Route("/openapi.json", openapi_schema, methods=["GET", "HEAD"]),
    Route("/swagger.json", openapi_schema, methods=["GET", "HEAD"]),
    Route("/api/openapi.json", openapi_schema, methods=["GET", "HEAD"]),
    Route("/docs/openapi.json", openapi_schema, methods=["GET", "HEAD"]),
    Route("/v1/openapi.json", openapi_schema, methods=["GET", "HEAD"]),
    Route("/mcp", handle_http_mcp, methods=["POST"]),
    Route("/sse", sse_endpoint, methods=["GET"]),
    Route("/messages", sse_messages, methods=["POST"]),
    # Dedicated Agent Endpoints (supports base slug, trailing slash, and /identity)
    Route("/agents", list_agents, methods=["GET", "HEAD"]),
    Route("/agents/{agent_slug}", agent_identity, methods=["GET", "HEAD"]),
    Route("/agents/{agent_slug}/", agent_identity, methods=["GET", "HEAD"]),
    Route("/agents/{agent_slug}/health", agent_health, methods=["GET", "HEAD"]),
    Route("/agents/{agent_slug}/identity", agent_identity, methods=["GET", "HEAD"]),
    Route("/agents/{agent_slug}/invoke", agent_invoke, methods=["POST"]),
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

app = Starlette(debug=True, routes=routes, middleware=middleware)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("MCP_PORT", 8010))
    print(f"Starting Mandate Remote MCP + Agent Service server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)

