# AgentTrace MVP Architecture

AgentTrace is a standard-library Python CLI. The package is split into:

- `agenttrace.cli`: argument parsing, command routing, and user-facing errors.
- `agenttrace.core`: Git inspection, JSON persistence, evidence capture, and report generation.

The CLI stores all audit data in `.agenttrace/` inside the current Git repository. Machine-readable state lives in JSON files. Human-readable evidence lives in Markdown or text files so it can be inspected, copied into a PR, or archived without AgentTrace.

The MVP avoids background services, remote APIs, databases, and nonessential dependencies. That keeps the trust boundary clear: AgentTrace observes the local repository and writes local audit artifacts.
