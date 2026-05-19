# What AgentTrace Does

AgentTrace helps you answer one simple question:

```text
What happened during this AI-assisted coding task?
```

When you use AI tools to change code, it can be hard to remember exactly what changed, what tests were run, and what evidence proves the work is ready. AgentTrace creates a local record of that information.

## What It Records

AgentTrace can record:

- the task you worked on
- the Git branch and commit where the task started
- changed files
- Git diff output
- test or build command results
- review notes
- GitHub pull request details
- evaluation or benchmark results
- a final Markdown report
- a local HTML dashboard

## Where The Information Goes

AgentTrace creates a folder named `.agenttrace` in your project:

```text
.agenttrace/
  config.json
  dashboard.html
  runs/
    one-run-folder/
      run.json
      status.txt
      diff.patch
      tests.md
      review.md
      report.md
      pr-description.md
```

You do not need to edit most of these files by hand.

The most useful files are:

- `report.md`: the final report for one task
- `pr-description.md`: a report you can use in a pull request
- `dashboard.html`: a local page that summarizes recorded runs

## What It Does Not Do

AgentTrace does not upload your code anywhere.

It does not call GitHub for you.

It does not decide if the code is good by itself.

It records evidence so a person can review the work more easily.

