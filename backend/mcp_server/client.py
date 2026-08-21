"""
MANDATE — MCP Client (Official FastMCP Protocol Interface)
Provides standard interface for invoking the 5 MCP tools using the official MCP Python SDK.
Architecture Decision (SPEC.md 1.6 Option B):
Uses the official SDK's FastMCP protocol layer in-process for deterministic local execution
reliability on Windows, avoiding subprocess pipe deadlocks.
MCP is strictly transport; no authorization or business logic resides here.
"""

import json
from typing import List, Dict, Any
from backend.mcp_server.server import mcp



class MandateMCPClient:
    """Thin MCP Client interface."""

    async def list_tools(self) -> List[str]:
        """Returns list of tool names exposed by the MCP server."""
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Invokes an MCP tool and extracts the structured return data."""
        # FastMCP call_tool returns (content_list, metadata)
        raw_result = await mcp.call_tool(tool_name, arguments)
        if isinstance(raw_result, tuple) and len(raw_result) == 2:
            content, meta = raw_result
            if isinstance(meta, dict) and "result" in meta:
                return meta["result"]
            # Fallback parse from text content
            if content and hasattr(content[0], "text"):
                try:
                    return json.loads(content[0].text)
                except Exception:
                    return content[0].text
        return raw_result


# Singleton instance for transport
default_mcp_client = MandateMCPClient()
