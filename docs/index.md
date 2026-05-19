# AgentTrace

AgentTrace is a local-first command-line tool for recording audit trails of AI-assisted coding work.

It helps you answer:

```text
What changed, what tests ran, what review happened, and what evidence supports the final result?
```

## Start Here

If you are new to AgentTrace, read these first:

1. [What AgentTrace Does](user-guides/what-agenttrace-does.md)
2. [Install And Run](user-guides/install-and-run.md)
3. [Your First Trace](user-guides/your-first-trace.md)
4. [Daily Workflow](user-guides/daily-workflow.md)

## Basic Workflow

```text
init -> start -> snapshot -> add-test -> add-review -> report
```

In plain English:

1. Set up AgentTrace in your Git project.
2. Start tracking a coding task.
3. Capture the changed files and diff.
4. Record tests or manual QA.
5. Add review notes.
6. Generate a final report.

## What AgentTrace Creates

AgentTrace writes local evidence into a `.agenttrace` folder in your project.

The most useful outputs are:

- `report.md`: the final report for one task
- `pr-description.md`: a pull-request-ready summary
- `dashboard.html`: a local dashboard across recorded runs

