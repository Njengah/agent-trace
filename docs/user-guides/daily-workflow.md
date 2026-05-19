# Daily Workflow

This is the normal way to use AgentTrace during real work.

## One Time Per Project

Run this once:

```powershell
agenttrace init
```

You do not need to run `init` before every task.

## Every Time You Start A New Task

Run:

```powershell
agenttrace start "describe the task here" --tool Codex --model gpt-5
```

Examples:

```powershell
agenttrace start "fix checkout page error" --tool Codex --model gpt-5
```

```powershell
agenttrace start "add CSV export to reports" --tool Cursor --model claude-sonnet
```

## After Code Changes

Run:

```powershell
agenttrace snapshot
```

This saves the current Git evidence for the active task.

## After Tests

Run your test through AgentTrace:

```powershell
agenttrace add-test "npm test"
```

or:

```powershell
agenttrace add-test "python -m unittest discover -s tests"
```

or, if the test was manual:

```powershell
agenttrace add-test "manual QA" --no-execute --note "Checked the main user flow in the browser."
```

## After Review

Write review notes in a file:

```text
review-notes.md
```

Then run:

```powershell
agenttrace add-review review-notes.md
```

## At The End

Generate the final report:

```powershell
agenttrace report
```

Generate or refresh the dashboard:

```powershell
agenttrace dashboard
```

## Simple Habit

For each task, try to capture at least:

1. one snapshot
2. one test result
3. one report

That is enough for a useful audit trail.

