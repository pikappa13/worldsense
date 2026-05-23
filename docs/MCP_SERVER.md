# WorldSense MCP Server

WorldSense ships a built-in [MCP](https://modelcontextprotocol.io/) server.
Once registered, any MCP-compatible AI (Claude Code, Claude Desktop, Cursor, etc.)
can call WorldSense tools natively — no extra code required.

## Tools exposed

| Tool | Purpose |
|------|---------|
| `worldsense_analyze` | Analyze a user message for hidden risks, missing context, and real-world consequences |
| `worldsense_evaluate_action` | Gate an agent action (file deletion, shell command, API call…) before execution |
| `worldsense_check_response` | Check a proposed AI response for overconfidence, social risk, and unsafe advice |

---

## Quick start

### 1. Install WorldSense

```bash
pip install worldsense
```

### 2. Register in Claude Code / Claude Desktop

Add to your `.claude/settings.json` (project) or `~/.claude/settings.json` (global):

```json
{
  "mcpServers": {
    "worldsense": {
      "command": "python",
      "args": ["-m", "worldsense.mcp_server"]
    }
  }
}
```

Or use the `worldsense mcp` CLI entry point:

```json
{
  "mcpServers": {
    "worldsense": {
      "command": "worldsense",
      "args": ["mcp"]
    }
  }
}
```

Restart Claude Code. The three WorldSense tools will appear in the tool list.

### 3. Register in Cursor

In `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "worldsense": {
      "command": "python",
      "args": ["-m", "worldsense.mcp_server"]
    }
  }
}
```

### 4. Run manually (for testing)

```bash
python -m worldsense.mcp_server
# or
worldsense mcp
```

The server reads JSON-RPC 2.0 requests from stdin and writes responses to stdout.

---

## Tool reference

### `worldsense_analyze`

Analyze a user message (and optionally a proposed AI response or planned action) for
hidden risks, missing context, real-world consequences, and practical constraint violations.

**Input**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_message` | string | ✅ | The user's message or request |
| `proposed_response` | string | — | Draft LLM response to check |
| `planned_action` | object | — | Agent action to evaluate alongside the message |
| `context` | object | — | Extra context (`user_confirmed`, `project_path`, …) |

**Output** — full `RealityAnalysis` JSON with:
- `risk.risk_level` — `none / low / medium / high / critical`
- `risk.categories` — triggered risk categories
- `consequences` — list of simulated consequences with severity/probability
- `recommendations` — actions to take
- `rewrite_guidance` — how to rewrite a safer response
- `constraint_violations` — detected logical/logistical impossibilities
- `uncertainty_assessment` — missing context flags

---

### `worldsense_evaluate_action`

Evaluate whether an agent action is safe to execute.

**Input**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tool` | string | ✅ | Action type: `filesystem.delete`, `shell.run`, `email.send`, … |
| `target` | string | — | Target path, address, command, … |
| `description` | string | — | Human-readable description |
| `context` | object | — | `user_confirmed`, `backup_available`, … |

**Output** — `ActionAssessment` JSON with:
- `should_block` — true if the action must be blocked
- `requires_confirmation` — true if user confirmation is needed
- `should_warn` — true if a warning should be shown
- `risk_level` — `none / low / medium / high / critical`
- `recommended_confirmation_prompt` — suggested confirmation message
- `safer_alternative` — suggested alternative action

---

### `worldsense_check_response`

Check a proposed AI response for overconfidence, social risk, and unsafe recommendations.

**Input**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_message` | string | ✅ | Original user message |
| `proposed_response` | string | ✅ | LLM response to check |

**Output** — same as `worldsense_analyze` (full `RealityAnalysis`).

---

## Example prompts for Claude Code

Once registered, you can ask Claude:

```
Before you delete those files, run worldsense_evaluate_action with tool=filesystem.delete
and target=/project/src to make sure it's safe.
```

```
Use worldsense_analyze on the user's last message before you reply to check for hidden risks.
```

```
Check my draft response with worldsense_check_response before I send it.
```

---

## Integration with CLAUDE.md

Add this to your project's `CLAUDE.md` to make WorldSense automatic:

```markdown
## Safety policy

Before executing any destructive action (file deletion, shell commands, database writes,
API calls with side effects), call `worldsense_evaluate_action` and respect the result:
- `should_block: true` → do not proceed, explain why
- `requires_confirmation: true` → ask the user before proceeding
- `should_warn: true` → show the warning, then proceed if user confirms

Before answering questions with real-world risk (medical, legal, financial, safety),
call `worldsense_analyze` on the user message and incorporate the `rewrite_guidance`
into your response.
```

---

## Protocol details

The server implements [MCP protocol version 2024-11-05](https://spec.modelcontextprotocol.io/)
over stdin/stdout using JSON-RPC 2.0.

Supported methods:
- `initialize`
- `tools/list`
- `tools/call`
- `notifications/initialized` (no-op)
