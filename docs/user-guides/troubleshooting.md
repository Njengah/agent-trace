# Troubleshooting

This guide explains common problems and how to fix them.

## Problem: AgentTrace Says It Must Run Inside A Git Repository

Message:

```text
AgentTrace must be run inside a Git repository. Run `git init` first.
```

Fix:

Go to your project folder and run:

```powershell
git init
```

Then run:

```powershell
agenttrace init
```

## Problem: AgentTrace Is Not Initialized

Message:

```text
AgentTrace is not initialized in this workspace. Run `agenttrace init` first.
```

Fix:

```powershell
agenttrace init
```

## Problem: No Active Run

Message:

```text
No active AgentTrace run. Run `agenttrace start "<task>"` first.
```

Fix:

Start a run:

```powershell
agenttrace start "describe your task"
```

## Problem: Review File Does Not Exist

Message:

```text
Review file does not exist
```

Fix:

Create the review file first.

Example:

```powershell
notepad review-notes.md
```

Then run:

```powershell
agenttrace add-review review-notes.md
```

## Problem: PR Number Does Not Work

Message:

```text
Could not infer GitHub repository from remote `origin`.
```

This happens when AgentTrace cannot tell which GitHub repository your project belongs to.

Fix option 1: pass the full pull request URL:

```powershell
agenttrace pr https://github.com/acme/widgets/pull/42
```

Fix option 2: add a GitHub remote to your Git repo:

```powershell
git remote add origin https://github.com/acme/widgets.git
```

Then:

```powershell
agenttrace pr 42
```

## Problem: Tests Fail

If you run:

```powershell
agenttrace add-test "your test command"
```

and the test command fails, AgentTrace still records the result.

That is useful because the report can show that a test failed.

Fix the code or test setup, then run the test command again:

```powershell
agenttrace add-test "your test command"
```

## Problem: PowerShell Shows A Profile Script Warning

You may see a warning like:

```text
running scripts is disabled on this system
```

This warning comes from PowerShell trying to load a profile script. It is usually separate from AgentTrace.

If the AgentTrace command still runs, you can continue.

If PowerShell blocks your work, ask someone who manages your machine before changing execution policy.

