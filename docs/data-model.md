# Data Model

Schema version: `0.1`

AgentTrace stores machine-readable run metadata in `run.json` and human-readable artifacts in sibling Markdown/text files.

## Workspace Config

`.agenttrace/config.json`

```json
{
  "schema_version": "0.1",
  "project_name": "agenttrace",
  "project_root": "C:/path/to/repo",
  "created_at": "2026-05-18T12:00:00Z",
  "active_run_id": "20260518-120001-add-cli"
}
```

## Run Metadata

`.agenttrace/runs/<run-id>/run.json`

```json
{
  "schema_version": "0.1",
  "run_id": "20260518-120001-add-cli",
  "task": "add cli",
  "created_at": "2026-05-18T12:00:01Z",
  "updated_at": "2026-05-18T12:01:00Z",
  "git": {
    "branch": "main",
    "commit": "abc123"
  },
  "agent_tool": "Codex",
  "model": "gpt-5",
  "mcp_tools_used": [],
  "prompt_contract_id": null,
  "review_score": null,
  "benchmark_task_id": null,
  "snapshots": [],
  "tests": [],
  "reviews": []
}
```

## Evidence Artifacts

- `status.txt`: output from `git status --short`.
- `diff.patch`: output from `git diff --no-ext-diff`.
- `tests.md`: executed or manual test evidence.
- `review.md`: appended review notes with source file references.
- `report.md`: generated summary for PRs or audit records.

## Evidence Definition

For the MVP, evidence means a timestamped artifact that can be inspected later:

- Git status at snapshot time.
- Git diff at snapshot time.
- Test or build command.
- Test or build output and exit code.
- Manual test note when command execution is not practical.
- Review note copied from an explicit local file.
- Report generation timestamp and checklist.
