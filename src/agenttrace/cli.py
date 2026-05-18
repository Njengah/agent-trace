from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import (
    AgentTraceError,
    add_project_root,
    add_review,
    add_test,
    git_root,
    init_workspace,
    report,
    snapshot,
    start_run,
    workspace_repo_from_cwd,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agenttrace",
        description="Create local audit trails for AI-assisted coding runs.",
    )
    parser.add_argument("--version", action="version", version=f"agenttrace {__version__}")
    subcommands = parser.add_subparsers(dest="command", required=True)

    init_parser = subcommands.add_parser("init", help="Initialize .agenttrace storage in the current Git repository.")
    init_parser.set_defaults(func=cmd_init)

    start_parser = subcommands.add_parser("start", help="Start a new AgentTrace run for a task.")
    start_parser.add_argument("task", help="Task description to audit.")
    start_parser.add_argument("--tool", dest="agent_tool", help="AI coding tool name to record.")
    start_parser.add_argument("--model", help="Model name to record.")
    start_parser.set_defaults(func=cmd_start)

    snapshot_parser = subcommands.add_parser("snapshot", help="Capture git status and diff for the active run.")
    snapshot_parser.set_defaults(func=cmd_snapshot)

    test_parser = subcommands.add_parser("add-test", help="Run or record a test/build command for the active run.")
    test_parser.add_argument("test_command", help="Command to execute or record. Quote multi-word commands.")
    test_parser.add_argument("--no-execute", action="store_true", help="Record manual evidence without running the command.")
    test_parser.add_argument("--note", help="Optional note for manual or contextual evidence.")
    test_parser.set_defaults(func=cmd_add_test)

    review_parser = subcommands.add_parser("add-review", help="Append review notes from a file to the active run.")
    review_parser.add_argument("file", help="Path to a Markdown/text review file.")
    review_parser.set_defaults(func=cmd_add_review)

    report_parser = subcommands.add_parser("report", help="Generate a Markdown report for the active run.")
    report_parser.set_defaults(func=cmd_report)
    return parser


def cmd_init(args: argparse.Namespace) -> int:
    repo = git_root(Path.cwd())
    path = init_workspace(repo)
    add_project_root(repo)
    print(f"Initialized AgentTrace workspace: {path}")
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    repo = workspace_repo_from_cwd()
    run_id, run_dir = start_run(repo, args.task, agent_tool=args.agent_tool, model=args.model)
    print(f"Started AgentTrace run: {run_id}")
    print(run_dir)
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    repo = workspace_repo_from_cwd()
    run_dir = snapshot(repo)
    print(f"Snapshot captured: {run_dir}")
    return 0


def cmd_add_test(args: argparse.Namespace) -> int:
    repo = workspace_repo_from_cwd()
    run_dir = add_test(repo, args.test_command, no_execute=args.no_execute, note=args.note)
    print(f"Test evidence recorded: {run_dir / 'tests.md'}")
    return 0


def cmd_add_review(args: argparse.Namespace) -> int:
    repo = workspace_repo_from_cwd()
    run_dir = add_review(repo, Path(args.file))
    print(f"Review evidence recorded: {run_dir / 'review.md'}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    repo = workspace_repo_from_cwd()
    path = report(repo)
    print(path)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except AgentTraceError as exc:
        print(f"agenttrace: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
