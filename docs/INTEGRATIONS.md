# Integrations

WorldSense is framework-agnostic. The integration pattern is always the same:

1. Let the LLM or agent propose a response or tool action.
2. Pass the response or action through WorldSense.
3. Continue, warn, ask for confirmation, or block based on the structured result.

## OpenAI Tool Calling

Use WorldSense before executing a tool call.

```python
from worldsense import RealityEngine

engine = RealityEngine()

def execute_tool(tool_call):
    decision = engine.evaluate_action(
        action={
            "tool": tool_call.name,
            "target": tool_call.arguments.get("target"),
            "description": str(tool_call.arguments),
        },
        context={"user_confirmation": False},
    )
    if decision.should_block:
        return {"error": decision.recommended_confirmation_prompt}
    return run_tool(tool_call)
```

## LangChain

Wrap tool execution with a WorldSense check.

```python
from worldsense import RealityEngine

engine = RealityEngine()

def guarded_tool(tool_name, args):
    decision = engine.evaluate_action(
        {"tool": tool_name, "target": args.get("target"), "description": str(args)},
        context=args.get("context", {}),
    )
    if decision.should_block:
        raise RuntimeError(decision.recommended_confirmation_prompt)
    return call_langchain_tool(tool_name, args)
```

## LlamaIndex

Use WorldSense before a query engine or tool writes externally.

```python
analysis = engine.check_response(
    user_message=user_query,
    proposed_response=draft_response,
)
if analysis.risk.risk_level in {"high", "critical"}:
    draft_response = apply_rewrite_guidance(draft_response, analysis.rewrite_guidance)
```

## AutoGen

Add a guard before agents execute code or tools.

```python
decision = engine.evaluate_action(
    {"tool": "shell.run", "description": proposed_command},
    context={"command_reviewed": False},
)
if decision.should_block:
    return decision.recommended_confirmation_prompt
```

## CrewAI

Use WorldSense as a task pre-hook for actions with side effects.

```python
def before_tool_use(tool, args):
    decision = engine.evaluate_action({"tool": tool.name, "description": str(args)})
    if decision.requires_confirmation:
        return {"requires_confirmation": decision.model_dump()}
```

## MCP Servers

WorldSense can run inside an MCP server as a safety tool exposed to agents.

```python
def worldsense_check_action(action: dict, context: dict | None = None) -> dict:
    return engine.evaluate_action(action, context).model_dump(mode="json")
```

Recommended MCP tools:

- `worldsense.analyze`
- `worldsense.check_response`
- `worldsense.evaluate_action`
- `worldsense.validate`

## Ollama

Use Ollama for optional LLM-assisted analysis while keeping rule-based fallback.

```python
from worldsense.adapters.ollama_adapter import OllamaAdapter

adapter = OllamaAdapter(client=ollama_client, model="llama3.1")
```

## FastAPI

Expose WorldSense as a local service.

```python
from fastapi import FastAPI
from worldsense import RealityEngine

app = FastAPI()
engine = RealityEngine()

@app.post("/analyze")
def analyze(payload: dict):
    return engine.analyze(**payload).model_dump(mode="json")

@app.post("/action")
def action(payload: dict):
    return engine.evaluate_action(
        payload["action"],
        payload.get("context"),
    ).model_dump(mode="json")
```

## Middleware

The simplest production shape:

```text
user -> LLM -> WorldSense response check -> final response
agent planned action -> WorldSense action gate -> tool execution
```

Use stricter thresholds for:

- destructive file or database operations
- public communication
- financial purchases
- privacy-sensitive data
- medical or physical safety risk
- irreversible actions

