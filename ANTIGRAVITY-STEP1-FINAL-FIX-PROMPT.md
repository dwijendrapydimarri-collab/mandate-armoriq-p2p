# Antigravity Prompt — Step 1 Final Fixes Before Step 2

The 14 invariant tests passing is encouraging, but Step 1 is not approved yet. The current implementation still has two defects that must be fixed and tested before Judge Mode work begins.

## Defect 1 — HOLD resume is still not an ArmorIQ authorization path

In `backend/gateway.py`, `resume_held()` currently calls the MCP client directly for `initiate_payment` and `write_ap_record`. That proves the controller no longer calls the domain function directly, but it still does not re-authorize the resumed action through ArmorIQ.

Correct the flow:

```text
Original HOLD decision
→ explicit human approval
→ supported ArmorIQ approval/resume or re-invocation with approval context
→ persist the resumed decision and original proof relationship
→ MCP dispatch only after the authorization layer returns ALLOW
```

Requirements:

1. Preserve the original mission ID, intent token, agent identity, delegation grant, tool, parameters, and audit relationship.
2. Do not mint a fresh unrestricted intent token.
3. Do not call the MCP client directly from `resume_held()` before ArmorIQ has authorized the resumed action.
4. If the real SDK exposes an approval/resume method, use it.
5. If local mode needs an approval flag, the local adapter must accept the original decision ID/token and return a new explicit `ALLOW` decision tied to the original HOLD—not bypass authorization.
6. The `write_ap_record` update must also follow the documented gateway policy or be an internal non-payment audit persistence operation clearly separated from side-effecting tools.
7. Add a regression test that spies on `enforcer.invoke()` or the supported approval/resume method and proves it is called before `initiate_payment` on approval.
8. Add a regression test proving a tampered held decision’s parameters cannot be changed before approval.

## Defect 2 — MCP transport claim must match the actual implementation

The repository currently appears to use:

```python
from mcp.server.fastmcp import FastMCP
```

and an in-process singleton client that calls the server object directly. This is not the same as a separate MCP server over stdio. Do not call it “verified stdio” unless the implementation actually spawns and connects to a stdio server process.

Choose one honest option:

### Option A — Implement true stdio

Use the official MCP Python SDK, launch the server as a subprocess, connect through stdio, list exactly five tools, call trusted reads, and add a transport smoke test.

### Option B — Explicitly document the in-process transport

If true stdio is too risky for the current environment, amend `SPEC.md` and `README.md` to state that the hackathon prototype uses the official SDK’s in-process FastMCP-compatible layer. Add an explicit architectural note that MCP transport is in-process in local mode. Do not claim stdio. Explain why this is a deliberate local reliability choice and verify it with a test.

Do not silently leave the current mismatch.

## Required completion report

Before Step 2 approval, return:

1. Exact files modified.
2. Exact before/after authorization flow for HOLD resume.
3. Verbatim test command and output.
4. Proof that the authorization layer is invoked before an approved HOLD reaches the payment tool.
5. The selected MCP transport option and its verification test.
6. Updated status: Step 1 complete only after these tests pass.

Do not implement Judge Mode endpoints or UI in this correction step. Stop after reporting the fixes and wait for human approval.
