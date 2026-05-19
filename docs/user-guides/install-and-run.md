# Install And Run

This guide shows how to run AgentTrace on your computer.

## Requirements

You need:

- Python 3.10 or newer
- Git
- a project that is already a Git repository

To check Python:

```powershell
python --version
```

To check Git:

```powershell
git --version
```

## Install From This Project Folder

Open PowerShell in the AgentTrace project folder:

```powershell
cd C:\Users\User\codex\profile\agenttrace
```

Install AgentTrace for development:

```powershell
python -m pip install -e .
```

After that, this command should work:

```powershell
agenttrace --help
```

## Run Without Installing

If you do not want to install it yet, you can run it like this from the project folder:

```powershell
$env:PYTHONPATH='src'
python -m agenttrace --help
```

When using this method, replace `agenttrace` with `python -m agenttrace` in the examples.

For example:

```powershell
python -m agenttrace init
```

## Run The Project Tests

From the AgentTrace project folder:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests
```

If everything is working, you should see output ending with:

```text
OK
```

