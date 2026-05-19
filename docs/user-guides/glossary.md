# Glossary

These are simple explanations of words used in AgentTrace.

## Active Run

The task AgentTrace is currently recording.

You create one with:

```powershell
agenttrace start "task description"
```

## Audit Trail

A record of what happened.

In AgentTrace, this means task details, changed files, test results, review notes, and reports.

## Dashboard

An HTML page that summarizes AgentTrace runs.

Create it with:

```powershell
agenttrace dashboard
```

## Diff

A Git view of exact code changes.

AgentTrace saves this in:

```text
diff.patch
```

## Evidence

Information that helps prove what happened.

Examples:

- Git status
- Git diff
- test output
- review notes
- benchmark results

## Evidence Policy

Rules AgentTrace uses to decide whether a run has enough evidence.

For example, the policy can require test evidence or review evidence.

Show the policy with:

```powershell
agenttrace policy
```

## Git Repository

A project folder tracked by Git.

AgentTrace must run inside a Git repository.

## Report

A Markdown file that summarizes one AgentTrace run.

Create it with:

```powershell
agenttrace report
```

## Run

One recorded task.

Example:

```text
fix checkout page error
```

## Snapshot

A saved copy of current Git evidence.

Create one with:

```powershell
agenttrace snapshot
```

