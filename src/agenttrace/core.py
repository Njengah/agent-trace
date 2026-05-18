from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"
TRACE_DIR = ".agenttrace"
CONFIG_NAME = "config.json"
DEFAULT_EVIDENCE_POLICY = {
    "require_tests": True,
    "require_reviews": False,
    "require_clean_snapshot": False,
    "fail_on_failed_tests": True,
}


class AgentTraceError(Exception):
    """Expected CLI error with a user-facing message."""


@dataclass(frozen=True)
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str, max_length: int = 48) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return (slug or "run")[:max_length].strip("-") or "run"


def generate_run_id(task: str, now: datetime | None = None) -> str:
    current = now or datetime.now(timezone.utc)
    timestamp = current.astimezone(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{timestamp}-{slugify(task)}"


def run_command(args: list[str], cwd: Path, check: bool = False) -> CommandResult:
    completed = subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise AgentTraceError(detail or f"Command failed: {' '.join(args)}")
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def run_shell_command(command: str, cwd: Path) -> tuple[int, str, str]:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def git_root(cwd: Path | None = None) -> Path:
    start = cwd or Path.cwd()
    result = run_command(["git", "rev-parse", "--show-toplevel"], start)
    if result.exit_code != 0:
        raise AgentTraceError("AgentTrace must be run inside a Git repository. Run `git init` first.")
    return Path(result.stdout.strip()).resolve()


def git_value(repo: Path, args: list[str], default: str | None = None) -> str | None:
    result = run_command(["git", *args], repo)
    if result.exit_code != 0:
        return default
    value = result.stdout.strip()
    return value if value else default


def trace_path(repo: Path) -> Path:
    return repo / TRACE_DIR


def config_path(repo: Path) -> Path:
    return trace_path(repo) / CONFIG_NAME


def runs_path(repo: Path) -> Path:
    return trace_path(repo) / "runs"


def is_initialized(repo: Path) -> bool:
    return config_path(repo).exists()


def read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise AgentTraceError(f"Missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AgentTraceError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise AgentTraceError(f"Expected JSON object in {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def read_config(repo: Path) -> dict[str, Any]:
    if not is_initialized(repo):
        raise AgentTraceError("AgentTrace is not initialized in this workspace. Run `agenttrace init` first.")
    return read_json(config_path(repo))


def write_config(repo: Path, config: dict[str, Any]) -> None:
    write_json(config_path(repo), config)


def normalize_evidence_policy(policy: dict[str, Any] | None = None) -> dict[str, bool]:
    normalized = dict(DEFAULT_EVIDENCE_POLICY)
    if policy:
        for key in normalized:
            if key in policy:
                normalized[key] = bool(policy[key])
    return normalized


def read_evidence_policy(repo: Path) -> dict[str, bool]:
    config = read_config(repo)
    return normalize_evidence_policy(config.get("evidence_policy"))


def update_evidence_policy(repo: Path, updates: dict[str, bool]) -> dict[str, bool]:
    config = read_config(repo)
    policy = normalize_evidence_policy(config.get("evidence_policy"))
    for key, value in updates.items():
        if key not in policy:
            raise AgentTraceError(f"Unknown evidence policy setting: {key}")
        policy[key] = bool(value)
    config["evidence_policy"] = policy
    config["updated_at"] = utc_now()
    write_config(repo, config)
    return policy


def active_run(repo: Path) -> tuple[str, Path, dict[str, Any]]:
    config = read_config(repo)
    run_id = config.get("active_run_id")
    if not run_id:
        raise AgentTraceError("No active AgentTrace run. Run `agenttrace start \"<task>\"` first.")
    run_dir = runs_path(repo) / str(run_id)
    run_file = run_dir / "run.json"
    if not run_file.exists():
        raise AgentTraceError(f"Active run metadata is missing: {run_file}")
    return str(run_id), run_dir, read_json(run_file)


def changed_files_from_status(porcelain: str) -> list[str]:
    files: list[str] = []
    for line in porcelain.splitlines():
        if not line:
            continue
        path = line[3:] if len(line) > 3 else line
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        files.append(path.strip())
    return sorted(dict.fromkeys(files))


def append_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
        if not content.endswith("\n"):
            handle.write("\n")


def init_workspace(repo: Path) -> Path:
    trace_path(repo).mkdir(exist_ok=True)
    runs_path(repo).mkdir(exist_ok=True)
    path = config_path(repo)
    if path.exists():
        config = read_json(path)
        config.setdefault("schema_version", SCHEMA_VERSION)
        config.setdefault("project_name", repo.name)
        config.setdefault("created_at", utc_now())
        config.setdefault("active_run_id", None)
        config["evidence_policy"] = normalize_evidence_policy(config.get("evidence_policy"))
    else:
        config = {
            "schema_version": SCHEMA_VERSION,
            "project_name": repo.name,
            "created_at": utc_now(),
            "active_run_id": None,
            "evidence_policy": normalize_evidence_policy(),
        }
    write_config(repo, config)
    return path


def start_run(repo: Path, task: str, agent_tool: str | None = None, model: str | None = None) -> tuple[str, Path]:
    read_config(repo)
    run_id = generate_run_id(task)
    run_dir = runs_path(repo) / run_id
    counter = 2
    while run_dir.exists():
        run_id = f"{generate_run_id(task)}-{counter}"
        run_dir = runs_path(repo) / run_id
        counter += 1
    run_dir.mkdir(parents=True)
    run_data = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "task": task,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "git": {
            "branch": git_value(repo, ["branch", "--show-current"], default="HEAD"),
            "commit": git_value(repo, ["rev-parse", "HEAD"]),
        },
        "agent_tool": agent_tool,
        "model": model,
        "mcp_tools_used": [],
        "prompt_contract_id": None,
        "review_score": None,
        "benchmark_task_id": None,
        "snapshots": [],
        "tests": [],
        "reviews": [],
    }
    write_json(run_dir / "run.json", run_data)
    for name in ("status.txt", "tests.md", "review.md"):
        (run_dir / name).write_text("", encoding="utf-8", newline="\n")
    (run_dir / "diff.patch").write_text("", encoding="utf-8", newline="\n")
    config = read_config(repo)
    config["active_run_id"] = run_id
    config["updated_at"] = utc_now()
    write_config(repo, config)
    return run_id, run_dir


def snapshot(repo: Path) -> Path:
    _, run_dir, run_data = active_run(repo)
    status = run_command(["git", "status", "--short"], repo, check=True).stdout
    diff = run_command(["git", "diff", "--no-ext-diff"], repo, check=True).stdout
    changed_files = changed_files_from_status(status)
    (run_dir / "status.txt").write_text(status or "Working tree clean.\n", encoding="utf-8", newline="\n")
    (run_dir / "diff.patch").write_text(diff or "# No tracked-file diff captured.\n", encoding="utf-8", newline="\n")
    entry = {
        "timestamp": utc_now(),
        "changed_files": changed_files,
        "dirty": bool(status.strip()),
    }
    run_data.setdefault("snapshots", []).append(entry)
    run_data["updated_at"] = entry["timestamp"]
    run_data["latest_snapshot"] = entry
    write_json(run_dir / "run.json", run_data)
    return run_dir


def add_test(repo: Path, command: str, no_execute: bool = False, note: str | None = None) -> Path:
    _, run_dir, run_data = active_run(repo)
    started_at = utc_now()
    if no_execute:
        exit_code = None
        stdout = ""
        stderr = ""
        ended_at = utc_now()
    else:
        exit_code, stdout, stderr = run_shell_command(command, repo)
        ended_at = utc_now()
    entry = {
        "command": command,
        "started_at": started_at,
        "ended_at": ended_at,
        "exit_code": exit_code,
        "executed": not no_execute,
        "note": note,
    }
    run_data.setdefault("tests", []).append(entry)
    run_data["updated_at"] = ended_at
    write_json(run_dir / "run.json", run_data)
    output = [
        f"## Test Evidence - {started_at}",
        "",
        f"- Command: `{command}`",
        f"- Executed: {'yes' if not no_execute else 'no'}",
        f"- Exit code: {exit_code if exit_code is not None else 'manual/not executed'}",
    ]
    if note:
        output.extend(["", f"Note: {note}"])
    if stdout.strip():
        output.extend(["", "### stdout", "", "```text", stdout.rstrip(), "```"])
    if stderr.strip():
        output.extend(["", "### stderr", "", "```text", stderr.rstrip(), "```"])
    output.append("")
    append_markdown(run_dir / "tests.md", "\n".join(output))
    return run_dir


def add_review(repo: Path, review_file: Path) -> Path:
    _, run_dir, run_data = active_run(repo)
    source = review_file if review_file.is_absolute() else (Path.cwd() / review_file)
    source = source.resolve()
    if not source.exists() or not source.is_file():
        raise AgentTraceError(f"Review file does not exist: {review_file}")
    timestamp = utc_now()
    content = source.read_text(encoding="utf-8")
    append_markdown(
        run_dir / "review.md",
        f"## Review Evidence - {timestamp}\n\nSource: `{source}`\n\n{content.rstrip()}\n\n",
    )
    run_data.setdefault("reviews", []).append({"source_file": str(source), "timestamp": timestamp})
    run_data["updated_at"] = timestamp
    write_json(run_dir / "run.json", run_data)
    return run_dir


def report(repo: Path) -> Path:
    run_id, run_dir, run_data = active_run(repo)
    policy = read_evidence_policy(repo)
    policy_result = evaluate_evidence_policy(run_data, policy)
    status_text = _read_optional(run_dir / "status.txt", "No status snapshot recorded.")
    diff_text = _read_optional(run_dir / "diff.patch", "No diff snapshot recorded.")
    tests_text = _read_optional(run_dir / "tests.md", "No test evidence recorded.")
    review_text = _read_optional(run_dir / "review.md", "No review evidence recorded.")
    latest = run_data.get("latest_snapshot") or {}
    changed_files = latest.get("changed_files") or []
    tests = run_data.get("tests") or []
    reviews = run_data.get("reviews") or []
    report_text = "\n".join(
        [
            f"# AgentTrace Report: {run_data.get('task', run_id)}",
            "",
            f"- Run ID: `{run_id}`",
            f"- Created: {run_data.get('created_at', 'unknown')}",
            f"- Report generated: {utc_now()}",
            f"- Git branch: `{(run_data.get('git') or {}).get('branch', 'unknown')}`",
            f"- Git commit: `{(run_data.get('git') or {}).get('commit') or 'uncommitted/unborn'}`",
            f"- Agent tool: `{run_data.get('agent_tool') or 'not recorded'}`",
            f"- Model: `{run_data.get('model') or 'not recorded'}`",
            "",
            "## Changed Files",
            "",
            _bullet_list(changed_files, "No changed files captured."),
            "",
            "## Git Status Evidence",
            "",
            "```text",
            status_text.rstrip(),
            "```",
            "",
            "## Diff Evidence",
            "",
            "```diff",
            _trim(diff_text.rstrip(), 12000),
            "```",
            "",
            "## Test Evidence",
            "",
            tests_text.rstrip(),
            "",
            "## Review Evidence",
            "",
            review_text.rstrip(),
            "",
            "## Evidence Policy",
            "",
            _policy_markdown(policy_result),
            "",
            "## Risk Notes",
            "",
            _risk_notes(latest, tests, reviews, policy_result),
            "",
            "## Final Evidence Checklist",
            "",
            f"- [x] Git status captured: `{(run_dir / 'status.txt').name}`",
            f"- [x] Git diff captured: `{(run_dir / 'diff.patch').name}`",
            f"- [{'x' if tests else ' '}] Test/build evidence recorded",
            f"- [{'x' if reviews else ' '}] Review evidence recorded",
            "- [x] Report timestamp generated",
            "",
        ]
    )
    path = run_dir / "report.md"
    path.write_text(report_text, encoding="utf-8", newline="\n")
    return path


def evaluate_evidence_policy(run_data: dict[str, Any], policy: dict[str, bool] | None = None) -> dict[str, Any]:
    active_policy = normalize_evidence_policy(policy)
    latest = run_data.get("latest_snapshot") or {}
    tests = run_data.get("tests") or []
    reviews = run_data.get("reviews") or []
    checks = [
        {
            "name": "test evidence recorded",
            "required": active_policy["require_tests"],
            "passed": bool(tests),
        },
        {
            "name": "review evidence recorded",
            "required": active_policy["require_reviews"],
            "passed": bool(reviews),
        },
        {
            "name": "latest snapshot clean",
            "required": active_policy["require_clean_snapshot"],
            "passed": latest.get("dirty") is False,
        },
        {
            "name": "recorded tests passed",
            "required": active_policy["fail_on_failed_tests"] and bool(tests),
            "passed": not any(test.get("exit_code") not in (0, None) for test in tests),
        },
    ]
    failures = [check for check in checks if check["required"] and not check["passed"]]
    return {
        "policy": active_policy,
        "passed": not failures,
        "checks": checks,
        "failures": failures,
    }


def _read_optional(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    content = path.read_text(encoding="utf-8")
    return content if content.strip() else fallback


def _bullet_list(items: list[str], fallback: str) -> str:
    if not items:
        return fallback
    return "\n".join(f"- `{item}`" for item in items)


def _policy_markdown(result: dict[str, Any]) -> str:
    lines = [f"Status: `{'pass' if result['passed'] else 'fail'}`", ""]
    for check in result["checks"]:
        required = "required" if check["required"] else "optional"
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- [{'x' if check['passed'] else ' '}] {check['name']} ({required}, {status})")
    return "\n".join(lines)


def _risk_notes(
    snapshot_data: dict[str, Any],
    tests: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    policy_result: dict[str, Any] | None = None,
) -> str:
    notes: list[str] = []
    if policy_result and not policy_result.get("passed"):
        failed = ", ".join(check["name"] for check in policy_result.get("failures", []))
        notes.append(f"- Evidence policy failed: {failed}.")
    if snapshot_data.get("dirty"):
        notes.append("- Working tree had uncommitted changes when snapshot was captured.")
    if not tests:
        notes.append("- No tests or build commands have been recorded.")
    elif any(test.get("exit_code") not in (0, None) for test in tests):
        notes.append("- At least one recorded test command failed.")
    if not reviews:
        notes.append("- No review notes have been recorded.")
    if not notes:
        notes.append("- No obvious evidence gaps detected in this MVP report.")
    return "\n".join(notes)


def _trim(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + "\n... truncated by AgentTrace report ..."


def workspace_repo_from_cwd() -> Path:
    repo = git_root(Path.cwd())
    config = config_path(repo)
    if config.exists():
        configured_root = read_json(config).get("project_root")
        if configured_root and Path(configured_root).resolve() != repo:
            raise AgentTraceError("Command is outside the initialized AgentTrace workspace.")
    return repo


def add_project_root(repo: Path) -> None:
    config = read_config(repo)
    config.setdefault("project_root", str(repo))
    write_config(repo, config)
