# Example Workflow

Start in a Git repository:

```powershell
agenttrace init
```

Begin auditing an AI coding session:

```powershell
agenttrace start "add CSV export to billing report" --tool Codex --model gpt-5
```

Run the AI coding tool and make the code changes. Then capture the repository evidence:

```powershell
agenttrace snapshot
```

Record test evidence:

```powershell
agenttrace add-test "python -m unittest discover -s tests"
```

Create review notes in a local file:

```markdown
# Review Notes

- Checked CSV escaping.
- Confirmed tests cover empty reports.
- Residual risk: large exports are not performance tested.
```

Append the review:

```powershell
agenttrace add-review review-notes.md
```

Generate the report:

```powershell
agenttrace report
```

The generated `report.md` includes the task, run id, timestamps, git metadata, changed files, test evidence, review evidence, risk notes, and final checklist.
