from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = str(ROOT / "src")
        self.run_git("init")
        self.run_git("config", "user.email", "agenttrace@example.test")
        self.run_git("config", "user.name", "AgentTrace Test")
        (self.repo / "README.md").write_text("# temp\n", encoding="utf-8")
        self.run_git("add", "README.md")
        self.run_git("commit", "-m", "initial")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "agenttrace", *args],
            cwd=cwd or self.repo,
            env=self.env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_init_start_snapshot_report_smoke(self) -> None:
        result = self.run_cli("init")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.repo / ".agenttrace" / "config.json").exists())

        result = self.run_cli("start", "change readme", "--tool", "Codex", "--model", "gpt-test")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Started AgentTrace run:", result.stdout)

        (self.repo / "README.md").write_text("# temp\n\nchanged\n", encoding="utf-8")
        result = self.run_cli("snapshot")
        self.assertEqual(result.returncode, 0, result.stderr)

        result = self.run_cli("add-test", f'"{sys.executable}" -c "print(123)"')
        self.assertEqual(result.returncode, 0, result.stderr)

        review = self.repo / "review.md"
        review.write_text("Looks reasonable.\n", encoding="utf-8")
        result = self.run_cli("add-review", str(review))
        self.assertEqual(result.returncode, 0, result.stderr)

        result = self.run_cli("report")
        self.assertEqual(result.returncode, 0, result.stderr)
        report_path = Path(result.stdout.strip())
        self.assertTrue(report_path.exists())
        text = report_path.read_text(encoding="utf-8")
        self.assertIn("AgentTrace Report", text)
        self.assertIn("change readme", text)
        self.assertIn("Test Evidence", text)

    def test_start_requires_init(self) -> None:
        result = self.run_cli("start", "missing init")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Run `agenttrace init` first", result.stderr)

    def test_snapshot_requires_active_run(self) -> None:
        self.assertEqual(self.run_cli("init").returncode, 0)
        result = self.run_cli("snapshot")
        self.assertEqual(result.returncode, 2)
        self.assertIn("No active AgentTrace run", result.stderr)

    def test_add_review_requires_existing_file(self) -> None:
        self.assertEqual(self.run_cli("init").returncode, 0)
        self.assertEqual(self.run_cli("start", "review missing").returncode, 0)
        result = self.run_cli("add-review", "missing.md")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Review file does not exist", result.stderr)

    def test_init_requires_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("init", cwd=Path(tmp))
        self.assertEqual(result.returncode, 2)
        self.assertIn("inside a Git repository", result.stderr)


if __name__ == "__main__":
    unittest.main()
