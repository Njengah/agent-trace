# Your First Trace

This guide walks through one simple AgentTrace run.

## Step 1: Open A Git Project

Go to the project you want to track:

```powershell
cd path\to\your\project
```

AgentTrace must be used inside a Git repository.

If your project is not a Git repository yet, run:

```powershell
git init
```

## Step 2: Initialize AgentTrace

Run this once per project:

```powershell
agenttrace init
```

This creates the `.agenttrace` folder.

## Step 3: Start A Task

Start tracking a coding task:

```powershell
agenttrace start "add input validation to the login form" --tool Codex --model gpt-5
```

The task text should describe the work in normal language.

The `--tool` and `--model` fields are optional, but useful later when reviewing what happened.

## Step 4: Do The Coding Work

Use your normal coding tool or AI assistant.

AgentTrace does not change the code for you. It records what happened around the work.

## Step 5: Capture The Code Changes

After files have changed, run:

```powershell
agenttrace snapshot
```

This records:

- Git status
- changed files
- Git diff

## Step 6: Record Test Evidence

Run a test command and save the result:

```powershell
agenttrace add-test "python -m unittest discover -s tests"
```

If you tested manually, record that instead:

```powershell
agenttrace add-test "manual browser test" --no-execute --note "Checked login with valid and invalid passwords."
```

## Step 7: Add Review Notes

Create a small file called `review-notes.md`:

```markdown
# Review Notes

- Checked the changed files.
- Tests passed.
- No obvious risk found.
```

Then add it to the trace:

```powershell
agenttrace add-review review-notes.md
```

## Step 8: Generate The Report

Run:

```powershell
agenttrace report
```

AgentTrace prints the path to the generated report.

The report is saved as:

```text
.agenttrace/runs/<run-id>/report.md
```

## Step 9: Generate The Dashboard

Run:

```powershell
agenttrace dashboard
```

This creates:

```text
.agenttrace/dashboard.html
```

Open that file in a browser to see a summary of your recorded runs.

