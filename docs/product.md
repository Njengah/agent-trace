# Product Definition

## Product Thesis

AgentTrace is the local audit layer for AI-assisted coding. It records the task, repository state, code changes, tests, reviews, and final evidence behind an AI coding run.

## User Persona

The primary user is an engineering lead or senior developer adopting coding agents in a professional software team. They want the productivity benefits of AI assistance without losing accountability, review discipline, or operational visibility.

## Enterprise Problem

AI coding tools can make meaningful changes quickly, but teams often lack durable answers to basic governance questions:

- Which tool was used?
- What task did it attempt?
- What files changed?
- Were tests or builds run?
- Was the diff reviewed?
- What evidence supports the final claim?

AgentTrace gives teams a lightweight local record before they invest in centralized dashboards or enterprise integrations.

## MVP Scope

The MVP is a CLI that creates a structured run folder under `.agenttrace/runs/<run-id>/` and captures:

- task description
- branch and commit metadata
- git status
- git diff
- test/build commands and outputs
- review notes
- a Markdown report

## Non-Goals

- No hosted service.
- No remote repository creation or pushing.
- No automatic source control commits for user code.
- No policy enforcement engine.
- No dashboard in the MVP.
- No claims about whether AI-generated code is correct beyond recorded evidence.

## Future Expansion Paths

- GitHub PR comment/report integration.
- MCPGuard integration for tool-use policy and safety evidence.
- EvalOps integration for benchmark and regression tracking.
- PromptOps contract validation.
- Risk scoring for sensitive files and failing evidence.
- Team dashboard for aggregated run history.
