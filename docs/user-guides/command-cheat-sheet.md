# Command Cheat Sheet

This page lists the common AgentTrace commands.

## Show Help

```powershell
agenttrace --help
```

## Initialize A Project

```powershell
agenttrace init
```

Use this once in a Git project.

## Start A Run

```powershell
agenttrace start "task description"
```

With tool and model:

```powershell
agenttrace start "task description" --tool Codex --model gpt-5
```

## Capture Git Evidence

```powershell
agenttrace snapshot
```

This records Git status and Git diff for the active run.

## Record A Test Command

```powershell
agenttrace add-test "test command here"
```

Examples:

```powershell
agenttrace add-test "npm test"
```

```powershell
agenttrace add-test "python -m unittest discover -s tests"
```

## Record Manual Testing

```powershell
agenttrace add-test "manual QA" --no-execute --note "Checked the feature in the browser."
```

## Add Review Notes

```powershell
agenttrace add-review review-notes.md
```

## Link A GitHub Pull Request

With a PR number:

```powershell
agenttrace pr 42
```

With more details:

```powershell
agenttrace pr 42 --title "Add validation" --base main --head feature/validation
```

With a full URL:

```powershell
agenttrace pr https://github.com/acme/widgets/pull/42
```

## Record Evaluation Evidence

```powershell
agenttrace eval benchmark-123 --score 91.5 --regression passed --note "No regression."
```

## Show Current Evidence Policy

```powershell
agenttrace policy
```

## Change Evidence Policy

Require review notes:

```powershell
agenttrace policy --require-reviews
```

Require a clean latest snapshot:

```powershell
agenttrace policy --require-clean-snapshot
```

Allow failed tests in the policy result:

```powershell
agenttrace policy --allow-failed-tests
```

## Generate A Report

```powershell
agenttrace report
```

## Generate The Dashboard

```powershell
agenttrace dashboard
```

