"""WorldSense MCP server — exposes the reality-check engine as MCP tools.

Run with:
    python -m worldsense.mcp_server

Or register in claude_desktop_config.json / .claude/settings.json:
    {
      "mcpServers": {
        "worldsense": {
          "command": "python",
          "args": ["-m", "worldsense.mcp_server"]
        }
      }
    }
"""

from __future__ import annotations

import json
import sys
from typing import Any

from worldsense.engine import RealityEngine

_engine = RealityEngine()


def _schema_analyze() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "user_message": {
                "type": "string",
                "description": "The user's message or request to analyze.",
            },
            "proposed_response": {
                "type": "string",
                "description": "Optional LLM response draft to check for hidden risks.",
            },
            "planned_action": {
                "type": "object",
                "description": "Optional agent action to evaluate (e.g. {tool, target, description}).",
            },
            "context": {
                "type": "object",
                "description": "Optional extra context (user_confirmed, project_path, etc.).",
            },
        },
        "required": ["user_message"],
    }


def _schema_evaluate_action() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "tool": {
                "type": "string",
                "description": "Tool/action type, e.g. 'filesystem.delete', 'shell.run', 'email.send'.",
            },
            "target": {
                "type": "string",
                "description": "Target of the action (file path, email address, command, etc.).",
            },
            "description": {
                "type": "string",
                "description": "Human-readable description of what the action does.",
            },
            "context": {
                "type": "object",
                "description": "Optional context (user_confirmed, project_path, etc.).",
            },
        },
        "required": ["tool"],
    }


def _schema_check_response() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "user_message": {
                "type": "string",
                "description": "The original user message.",
            },
            "proposed_response": {
                "type": "string",
                "description": "The LLM response to check.",
            },
        },
        "required": ["user_message", "proposed_response"],
    }


# --- MCP protocol handlers ---

def _handle_initialize(params: dict[str, Any]) -> dict[str, Any]:
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "worldsense", "version": "0.1.0"},
    }


def _handle_tools_list() -> dict[str, Any]:
    return {
        "tools": [
            {
                "name": "worldsense_analyze",
                "description": (
                    "Analyze a user message (and optionally a proposed AI response or planned "
                    "action) for hidden risks, missing context, real-world consequences, and "
                    "practical constraint violations. Returns a structured risk assessment with "
                    "recommendations and rewrite guidance."
                ),
                "inputSchema": _schema_analyze(),
            },
            {
                "name": "worldsense_evaluate_action",
                "description": (
                    "Evaluate whether an agent action (file deletion, shell command, email send, "
                    "database write, API call, etc.) is safe to execute. Returns allow/warn/"
                    "require_confirmation/block with rationale."
                ),
                "inputSchema": _schema_evaluate_action(),
            },
            {
                "name": "worldsense_check_response",
                "description": (
                    "Check a proposed AI response against the original user message for "
                    "overconfidence, social risk, missing context, and unsafe recommendations. "
                    "Returns rewrite guidance and risk level."
                ),
                "inputSchema": _schema_check_response(),
            },
        ]
    }


def _handle_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "worldsense_analyze":
        result = _engine.analyze(
            user_message=arguments["user_message"],
            proposed_response=arguments.get("proposed_response"),
            planned_action=arguments.get("planned_action"),
            context=arguments.get("context"),
        )
        return {"content": [{"type": "text", "text": result.model_dump_json(indent=2)}]}

    if name == "worldsense_evaluate_action":
        action = {
            "tool": arguments["tool"],
            "target": arguments.get("target", ""),
            "description": arguments.get("description", ""),
        }
        context = arguments.get("context") or {}
        result = _engine.evaluate_action(action, context)
        return {"content": [{"type": "text", "text": result.model_dump_json(indent=2)}]}

    if name == "worldsense_check_response":
        result = _engine.check_response(
            user_message=arguments["user_message"],
            proposed_response=arguments["proposed_response"],
        )
        return {"content": [{"type": "text", "text": result.model_dump_json(indent=2)}]}

    return {
        "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
        "isError": True,
    }


def _dispatch(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method", "")
    req_id = request.get("id")
    params = request.get("params", {})

    if method == "notifications/initialized":
        return None

    result: dict[str, Any]
    if method == "initialize":
        result = _handle_initialize(params)
    elif method == "tools/list":
        result = _handle_tools_list()
    elif method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        try:
            result = _handle_tool_call(tool_name, tool_args)
        except Exception as exc:  # noqa: BLE001
            result = {
                "content": [{"type": "text", "text": f"WorldSense error: {exc}"}],
                "isError": True,
            }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }

    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def run_stdio() -> None:
    """Run the MCP server over stdin/stdout (JSON-RPC 2.0)."""
    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            request = json.loads(raw_line)
        except json.JSONDecodeError:
            continue

        response = _dispatch(request)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio()
