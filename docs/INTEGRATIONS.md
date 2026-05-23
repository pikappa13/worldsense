# WorldSense Integrations

WorldSense is framework-agnostic. The integration pattern is always the same:

1. Let the LLM or agent produce a response or plan a tool action.
2. Pass it through WorldSense.
3. Act on the structured result — continue, warn, ask for confirmation, or block.

This document shows complete, runnable integration examples for each supported framework.

---

## MCP — Claude Code, Cursor, Claude Desktop

The easiest integration. No code required. WorldSense ships a built-in MCP server.

**Install:**
```bash
pip install worldsense
```

**Register in `.claude/settings.json`:**
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

**Same config works for Cursor** (`~/.cursor/mcp.json`) **and Claude Desktop** (`claude_desktop_config.json`).

Three tools become available to the AI:

| Tool | Use it for |
|------|-----------|
| `worldsense_analyze` | Check a user message for hidden risks before replying |
| `worldsense_evaluate_action` | Gate a destructive tool call before executing |
| `worldsense_check_response` | Check a draft response before sending |

**Add to `CLAUDE.md` for automatic safety policy:**
```markdown
## Safety policy

Before executing any destructive action (file deletion, shell commands, database writes,
API calls with side effects), call `worldsense_evaluate_action`.
- `should_block: true` → do not proceed, explain why
- `requires_confirmation: true` → ask the user before proceeding
- `should_warn: true` → show the warning, then proceed if confirmed

Before answering questions with real-world risk (medical, legal, financial, physical safety),
call `worldsense_analyze` and incorporate the `rewrite_guidance` into your response.
```

Full MCP documentation: [MCP_SERVER.md](MCP_SERVER.md)

---

## OpenAI — Function Calling / Tool Use

Use WorldSense to gate tool calls before OpenAI executes them.

**Install:**
```bash
pip install worldsense openai
```

**Example — intercept tool calls in a loop:**
```python
import openai
from worldsense import RealityEngine

client = openai.OpenAI()
engine = RealityEngine()

tools = [
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Delete a file from disk",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    }
]

def run_agent(user_message: str):
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=tools,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content

        for tool_call in msg.tool_calls:
            args = dict(tool_call.function.arguments_json())

            # WorldSense gate — runs before any tool executes
            decision = engine.evaluate_action(
                action={
                    "tool": tool_call.function.name,
                    "target": args.get("path", ""),
                    "description": str(args),
                },
                context={"user_confirmation": False},
            )

            if decision.should_block:
                tool_result = (
                    f"Action blocked: {decision.recommended_confirmation_prompt}"
                )
            elif decision.requires_confirmation:
                # In a real app, prompt the user here
                tool_result = (
                    f"Confirmation required: {decision.recommended_confirmation_prompt}"
                )
            else:
                tool_result = execute_tool(tool_call.function.name, args)

            messages.append(msg)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result,
            })
```

**Example — check response before returning it:**
```python
def safe_complete(user_message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": user_message}],
    )
    draft = response.choices[0].message.content

    analysis = engine.check_response(
        user_message=user_message,
        proposed_response=draft,
    )

    if analysis.risk.risk_level in ("high", "critical"):
        # Log the risk and return the guidance instead
        print(f"[WorldSense] Risk: {analysis.risk.risk_level}")
        print(f"[WorldSense] Rewrite: {analysis.rewrite_guidance}")

    return draft
```

---

## LangChain

WorldSense integrates at two levels: as a tool guard and as a response checker.

**Install:**
```bash
pip install worldsense langchain langchain-openai
```

**Example — guarded tool in a LangChain agent:**
```python
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from worldsense import RealityEngine

engine = RealityEngine()


def worldsense_guard(tool_name: str, args: dict, context: dict | None = None) -> str | None:
    """Return an error message if the action should be blocked, else None."""
    decision = engine.evaluate_action(
        {"tool": tool_name, "target": args.get("target", ""), "description": str(args)},
        context=context or {},
    )
    if decision.should_block:
        return f"Blocked: {decision.recommended_confirmation_prompt}"
    if decision.requires_confirmation:
        return f"Confirmation required: {decision.recommended_confirmation_prompt}"
    return None


@tool
def delete_file(path: str) -> str:
    """Delete a file from disk."""
    error = worldsense_guard("filesystem.delete", {"target": path})
    if error:
        return error
    import os
    os.remove(path)
    return f"Deleted: {path}"


@tool
def run_shell(command: str) -> str:
    """Run a shell command."""
    error = worldsense_guard("shell.run", {"command": command})
    if error:
        return error
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout


llm = ChatOpenAI(model="gpt-4.1-mini")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
agent = create_openai_tools_agent(llm, [delete_file, run_shell], prompt)
executor = AgentExecutor(agent=agent, tools=[delete_file, run_shell])
```

**Example — response checker in a LangChain chain:**
```python
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from worldsense import RealityEngine

engine = RealityEngine()


def check_with_worldsense(inputs: dict) -> dict:
    user_message = inputs["question"]
    draft_response = inputs["response"]

    analysis = engine.check_response(
        user_message=user_message,
        proposed_response=draft_response,
    )

    return {
        "response": draft_response,
        "risk_level": analysis.risk.risk_level,
        "recommendations": [r.action for r in analysis.recommendations],
        "rewrite_guidance": analysis.rewrite_guidance.model_dump() if analysis.rewrite_guidance else None,
    }


llm = ChatOpenAI(model="gpt-4.1-mini")
chain = (
    {"question": lambda x: x, "response": llm | StrOutputParser()}
    | RunnableLambda(check_with_worldsense)
)

result = chain.invoke("Ho dormito 2 ore ma devo guidare 3 ore. Cosa faccio?")
print(result["risk_level"])       # "high"
print(result["recommendations"])  # ["warn_and_suggest_alternatives"]
```

---

## LlamaIndex

Use WorldSense as a post-generation safety filter.

**Install:**
```bash
pip install worldsense llama-index llama-index-llms-openai
```

**Example — safe query engine wrapper:**
```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from worldsense import RealityEngine

engine = RealityEngine()

# Build your index as usual
documents = SimpleDirectoryReader("data/").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(llm=OpenAI(model="gpt-4.1-mini"))


def safe_query(user_question: str) -> str:
    response = query_engine.query(user_question)
    draft = str(response)

    analysis = engine.check_response(
        user_message=user_question,
        proposed_response=draft,
    )

    if analysis.risk.risk_level in ("high", "critical"):
        guidance = analysis.rewrite_guidance
        if guidance and guidance.must_include:
            # Append mandatory context to the response
            additions = " ".join(guidance.must_include)
            return f"{draft}\n\nImportant: {additions}"

    return draft


answer = safe_query("Is it safe to drive after only 2 hours of sleep?")
print(answer)
```

**Example — agent tool with WorldSense gate:**
```python
from llama_index.core.tools import FunctionTool
from worldsense import RealityEngine

engine = RealityEngine()


def delete_document(doc_id: str) -> str:
    """Delete a document from the index."""
    decision = engine.evaluate_action(
        {"tool": "filesystem.delete", "target": doc_id, "description": f"Delete doc {doc_id}"},
        context={"user_confirmation": False},
    )
    if decision.should_block:
        return f"Cannot delete: {decision.recommended_confirmation_prompt}"
    # ... actual deletion logic
    return f"Deleted document {doc_id}"


delete_tool = FunctionTool.from_defaults(fn=delete_document)
```

---

## AutoGen

Gate tool use in AutoGen agents before execution.

**Install:**
```bash
pip install worldsense pyautogen
```

**Example — safety check in a ConversableAgent tool:**
```python
import autogen
from worldsense import RealityEngine

engine = RealityEngine()


def safe_shell_exec(command: str) -> str:
    """Execute a shell command with WorldSense safety gate."""
    decision = engine.evaluate_action(
        {"tool": "shell.run", "description": command},
        context={"command_reviewed": False},
    )
    if decision.should_block:
        return f"[BLOCKED] {decision.recommended_confirmation_prompt}"
    if decision.requires_confirmation:
        return f"[CONFIRM REQUIRED] {decision.recommended_confirmation_prompt}"

    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout or result.stderr


config_list = [{"model": "gpt-4.1-mini", "api_key": "..."}]

assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={"config_list": config_list},
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    function_map={"safe_shell_exec": safe_shell_exec},
)

user_proxy.initiate_chat(
    assistant,
    message="Clean up the /tmp directory by deleting files older than 7 days.",
)
```

**Example — response safety check as a custom AutoGen reply function:**
```python
from worldsense import RealityEngine

engine = RealityEngine()


def worldsense_check_reply(
    recipient, messages, sender, config
) -> tuple[bool, str | None]:
    """AutoGen custom reply function — checks the last assistant message for risks."""
    last = messages[-1] if messages else {}
    content = last.get("content", "")
    user_msg = messages[0].get("content", "") if messages else ""

    if not content:
        return False, None

    analysis = engine.check_response(
        user_message=user_msg,
        proposed_response=content,
    )

    if analysis.risk.risk_level in ("high", "critical"):
        warning = f"\n\n⚠️ WorldSense: risk_level={analysis.risk.risk_level}"
        if analysis.rewrite_guidance and analysis.rewrite_guidance.must_include:
            warning += f" | Must include: {', '.join(analysis.rewrite_guidance.must_include)}"
        return True, content + warning

    return False, None


assistant.register_reply(
    trigger=autogen.ConversableAgent,
    reply_func=worldsense_check_reply,
    position=0,
)
```

---

## CrewAI

Use WorldSense as a task pre-hook and tool guard.

**Install:**
```bash
pip install worldsense crewai
```

**Example — guarded BaseTool:**
```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from worldsense import RealityEngine

engine = RealityEngine()


class DeleteFileInput(BaseModel):
    path: str = Field(description="Path of the file to delete")


class SafeDeleteFileTool(BaseTool):
    name: str = "safe_delete_file"
    description: str = "Delete a file from disk (WorldSense-guarded)"
    args_schema: type[BaseModel] = DeleteFileInput

    def _run(self, path: str) -> str:
        decision = engine.evaluate_action(
            {"tool": "filesystem.delete", "target": path, "description": f"Delete {path}"},
            context={"user_confirmation": False},
        )
        if decision.should_block:
            return f"Blocked: {decision.recommended_confirmation_prompt}"
        if decision.requires_confirmation:
            return f"Needs confirmation: {decision.recommended_confirmation_prompt}"

        import os
        os.remove(path)
        return f"Deleted: {path}"


class SafeShellTool(BaseTool):
    name: str = "safe_shell"
    description: str = "Run a shell command (WorldSense-guarded)"

    def _run(self, command: str) -> str:
        decision = engine.evaluate_action(
            {"tool": "shell.run", "description": command},
            context={"command_reviewed": False},
        )
        if decision.should_block:
            return f"Blocked: {decision.recommended_confirmation_prompt}"

        import subprocess
        return subprocess.check_output(command, shell=True, text=True)
```

**Example — WorldSense as a CrewAI task callback:**
```python
from crewai import Task, Crew, Agent
from worldsense import RealityEngine

engine = RealityEngine()


def worldsense_task_callback(output):
    """Run after each task to flag high-risk outputs."""
    analysis = engine.check_response(
        user_message="",
        proposed_response=str(output),
    )
    if analysis.risk.risk_level in ("high", "critical"):
        print(f"[WorldSense WARNING] Task output risk: {analysis.risk.risk_level}")
        for rec in analysis.recommendations:
            print(f"  → {rec.action}: {rec.rationale}")


agent = Agent(
    role="DevOps Engineer",
    goal="Manage server infrastructure",
    backstory="Expert in cloud and server management",
    tools=[SafeDeleteFileTool(), SafeShellTool()],
)

task = Task(
    description="Clean up old log files from /var/log/app/",
    agent=agent,
    callback=worldsense_task_callback,
)

crew = Crew(agents=[agent], tasks=[task])
crew.kickoff()
```

---

## FastAPI — REST API / Middleware

Expose WorldSense as a microservice or use it as request/response middleware.

**Install:**
```bash
pip install worldsense fastapi uvicorn
```

**Example — REST API endpoints:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from worldsense import RealityEngine
from worldsense.schemas import RealityAnalysis, ActionAssessment

app = FastAPI(title="WorldSense API", version="0.1.0")
engine = RealityEngine()


class AnalyzeRequest(BaseModel):
    user_message: str
    proposed_response: str | None = None
    context: dict | None = None


class ActionRequest(BaseModel):
    tool: str
    target: str | None = None
    description: str | None = None
    context: dict | None = None


@app.post("/analyze", response_model=RealityAnalysis)
def analyze(req: AnalyzeRequest):
    return engine.analyze(
        user_message=req.user_message,
        proposed_response=req.proposed_response,
        context=req.context,
    )


@app.post("/action", response_model=ActionAssessment)
def evaluate_action(req: ActionRequest):
    action = {
        "tool": req.tool,
        "target": req.target or "",
        "description": req.description or "",
    }
    return engine.evaluate_action(action=action, context=req.context)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
```

**Run:**
```bash
uvicorn myapp:app --reload
```

**Example — middleware that checks every response:**
```python
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import json
from worldsense import RealityEngine

engine = RealityEngine()


class WorldSenseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Intercept the response
        response = await call_next(request)

        # Only check JSON responses from /chat or /complete endpoints
        if request.url.path not in ("/chat", "/complete"):
            return response

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        try:
            data = json.loads(body)
            user_message = data.get("user_message", "")
            ai_response = data.get("response", "")

            if user_message and ai_response:
                analysis = engine.check_response(
                    user_message=user_message,
                    proposed_response=ai_response,
                )
                data["worldsense"] = {
                    "risk_level": analysis.risk.risk_level,
                    "categories": analysis.risk.categories,
                }
                body = json.dumps(data).encode()
        except (json.JSONDecodeError, KeyError):
            pass

        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type="application/json",
        )


app = FastAPI()
app.add_middleware(WorldSenseMiddleware)
```

---

## Ollama — Local LLM backend

Use a local Ollama model as the WorldSense analysis backend.
No external API keys required.

**Install:**
```bash
pip install "worldsense[ollama]"
# Make sure Ollama is running: https://ollama.com
```

**Example:**
```python
from worldsense import RealityEngine, get_ollama_adapter

engine = RealityEngine(adapter=get_ollama_adapter(model="llama3.1"))

analysis = engine.analyze(
    user_message="Ho dormito 2 ore ma devo guidare 3 ore.",
    proposed_response="Bevi un caffe e fai attenzione.",
)

print(analysis.risk.risk_level)
print(analysis.rewrite_guidance)
```

The rule-based engine always runs first. Ollama enriches the context extraction and
consequence simulation on top. If Ollama is unavailable, the engine falls back to rules
silently.

**Useful models for WorldSense:**
- `llama3.1` — good general reasoning
- `mistral` — fast, good structured JSON output
- `phi3` — lightweight, runs on CPU

---

## Generic middleware pattern

The simplest shape for any integration:

```
User message
    ↓
LLM generates response
    ↓
worldsense.check_response(user_message, draft_response)
    ↓
risk_level == "high" or "critical"?
    YES → apply rewrite_guidance or ask user to confirm
    NO  → return response as-is
```

```
Agent plans tool action
    ↓
worldsense.evaluate_action(action, context)
    ↓
should_block?       → return error, do not execute
requires_confirmation? → ask user, then execute if confirmed
should_warn?        → log warning, execute
allow?              → execute
```

Apply stricter thresholds for:
- Destructive file or database operations
- Public communication (emails, posts, messages)
- Financial transactions
- Privacy-sensitive data handling
- Medical or physical safety advice
- Any irreversible action
