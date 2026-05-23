from __future__ import annotations

import argparse
import json
from typing import Any

from worldsense.engine import RealityEngine
from worldsense.evaluation import run_benchmark
from worldsense.validation import validate_project


def _json_arg(value: str | None) -> dict[str, Any] | None:
    if not value:
        return None
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError("Expected a JSON object")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="worldsense", description="Reality-check AI outputs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze a user message and optional response.")
    analyze.add_argument("message")
    analyze.add_argument("--response", default=None)
    analyze.add_argument("--context", type=_json_arg, default=None)

    action = subparsers.add_parser("action", help="Evaluate an agent action before execution.")
    action.add_argument("action", type=_json_arg, nargs="?", default=None)
    action.add_argument("--tool", default=None)
    action.add_argument("--target", default=None)
    action.add_argument("--description", default=None)
    action.add_argument("--context", type=_json_arg, default=None)

    benchmark = subparsers.add_parser("benchmark", help="Run a JSONL benchmark dataset.")
    benchmark.add_argument("path")
    benchmark.add_argument("--fail-under", type=float, default=None)

    validate = subparsers.add_parser("validate", help="Validate bundled rules and benchmark data.")
    validate.add_argument("--dataset", default="data/seed_scenarios.jsonl")

    subparsers.add_parser(
        "mcp",
        help="Start the WorldSense MCP server (stdin/stdout JSON-RPC 2.0).",
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "mcp":
        from worldsense.mcp_server import run_stdio
        run_stdio()
        return

    engine = RealityEngine()

    if args.command == "analyze":
        result = engine.analyze(
            user_message=args.message,
            proposed_response=args.response,
            context=args.context,
        )
    elif args.command == "action":
        action = args.action or {
            "tool": args.tool,
            "target": args.target,
            "description": args.description,
        }
        result = engine.evaluate_action(action=action, context=args.context)
    elif args.command == "benchmark":
        result = run_benchmark(args.path, engine=engine)
        if args.fail_under is not None and result.pass_rate < args.fail_under:
            print(result.model_dump_json(indent=2))
            raise SystemExit(1)
    else:
        result = validate_project(args.dataset)
        if not result.passed:
            print(result.model_dump_json(indent=2))
            raise SystemExit(1)

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
