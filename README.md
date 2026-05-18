# AgentTrace

Observability and audit trails for AI coding agents.

AgentTrace is a local-first CLI that records what an AI coding agent attempted, what changed, what tests ran, what review happened, and what evidence supports the final result. It is designed for teams using tools such as Codex, Claude Code, Cursor, Copilot, and similar coding agents.

## MVP Scope

The MVP creates structured audit trails in a local Git workspace:

- task description
- git branch and commit at run start
- git status and diff snapshots
- test/build command evidence
- review notes
- Markdown report suitable for a PR description

## Install for Development

```powershell
python -m pip install -e .
```

You can also run without installation:

```powershell
python -m agenttrace --help
```

## Commands

Initialize AgentTrace in a Git repository:

```powershell
agenttrace init
```

Start a run:

```powershell
agenttrace start "add input validation to the CLI" --tool Codex --model gpt-5
```

Capture current Git evidence:

```powershell
agenttrace snapshot
```

Run and record a test/build command:

```powershell
agenttrace add-test "python -m unittest"
```

Record manual test evidence without executing a command:

```powershell
agenttrace add-test "manual QA in staging" --no-execute --note "Reviewer confirmed happy path."
```

Append review notes:

```powershell
agenttrace add-review review-notes.md
```

Generate the final report:

```powershell
agenttrace report
```

## Output Structure

```text
.agenttrace/
  config.json
  runs/
    20260518-120000-add-input-validation/
      run.json
      diff.patch
      status.txt
      tests.md
      review.md
      report.md
```

## MVP Limitations

- Evidence is local to the repository and not uploaded anywhere.
- Test commands execute with the current user's shell environment.
- The report truncates very large diffs for readability.
- There is no dashboard, PR integration, or policy engine yet.

## Development

Run the test suite:

```powershell
python -m unittest discover -s tests
```

See `docs/workflow.md` for a complete example workflow.
