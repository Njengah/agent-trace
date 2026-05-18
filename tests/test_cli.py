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
        self.assertIn("require_tests", (self.repo / ".agenttrace" / "config.json").read_text(encoding="utf-8"))

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
        self.assertIn("Evidence Policy", text)
        self.assertIn("Status: `pass`", text)
        self.assertIn("Test Evidence", text)

    def test_policy_command_updates_requirements(self) -> None:
        self.assertEqual(self.run_cli("init").returncode, 0)

        result = self.run_cli("policy", "--require-reviews", "--require-clean-snapshot")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- require_reviews: true", result.stdout)
        self.assertIn("- require_clean_snapshot: true", result.stdout)

        result = self.run_cli("policy")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- require_tests: true", result.stdout)
        self.assertIn("- require_reviews: true", result.stdout)

    def test_report_marks_failed_policy(self) -> None:
        self.assertEqual(self.run_cli("init").returncode, 0)
        self.assertEqual(self.run_cli("policy", "--require-reviews").returncode, 0)
        self.assertEqual(self.run_cli("start", "policy failure").returncode, 0)
        result = self.run_cli("report")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = Path(result.stdout.strip()).read_text(encoding="utf-8")
        self.assertIn("Evidence Policy", text)
        self.assertIn("Status: `fail`", text)
        self.assertIn("Evidence policy failed", text)

    def test_pr_command_links_github_metadata_into_report(self) -> None:
        self.run_git("remote", "add", "origin", "git@github.com:acme/widgets.git")
        self.assertEqual(self.run_cli("init").returncode, 0)
        self.assertEqual(self.run_cli("start", "github pr").returncode, 0)

        result = self.run_cli("pr", "42", "--title", "Add widgets", "--base", "main", "--head", "feature/widgets")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("https://github.com/acme/widgets/pull/42", result.stdout)

        result = self.run_cli("pr")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("GitHub PR: https://github.com/acme/widgets/pull/42", result.stdout)
        self.assertIn("Title: Add widgets", result.stdout)

        result = self.run_cli("report")
        self.assertEqual(result.returncode, 0, result.stderr)
        report_path = Path(result.stdout.strip())
        text = report_path.read_text(encoding="utf-8")
        self.assertIn("## GitHub PR", text)
        self.assertIn("[acme/widgets#42](https://github.com/acme/widgets/pull/42)", text)
        self.assertTrue((report_path.parent / "pr-description.md").exists())

    def test_pr_number_requires_github_remote(self) -> None:
        self.assertEqual(self.run_cli("init").returncode, 0)
        self.assertEqual(self.run_cli("start", "github pr").returncode, 0)
        result = self.run_cli("pr", "42")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Could not infer GitHub repository", result.stderr)

    def test_dashboard_generates_html_summary(self) -> None:
        self.run_git("remote", "add", "origin", "https://github.com/acme/widgets.git")
        self.assertEqual(self.run_cli("init").returncode, 0)
        self.assertEqual(self.run_cli("start", "dashboard run", "--tool", "Codex").returncode, 0)
        (self.repo / "README.md").write_text("# temp\n\nchanged\n", encoding="utf-8")
        self.assertEqual(self.run_cli("snapshot").returncode, 0)
        self.assertEqual(self.run_cli("add-test", f'"{sys.executable}" -c "print(123)"').returncode, 0)
        self.assertEqual(self.run_cli("pr", "7", "--title", "Dashboard PR").returncode, 0)

        result = self.run_cli("dashboard")
        self.assertEqual(result.returncode, 0, result.stderr)
        dashboard_path = Path(result.stdout.strip())
        self.assertEqual(dashboard_path.name, "dashboard.html")
        html = dashboard_path.read_text(encoding="utf-8")
        self.assertIn("<h1>", html)
        self.assertIn("dashboard run", html)
        self.assertIn("Policy pass", html)
        self.assertIn("acme/widgets#7", html)
        self.assertIn("README.md", html)

    def test_eval_command_records_report_and_dashboard_evidence(self) -> None:
        self.assertEqual(self.run_cli("init").returncode, 0)
        self.assertEqual(self.run_cli("start", "evalops run").returncode, 0)

        result = self.run_cli("eval", "bench-123", "--score", "91.5", "--regression", "passed", "--note", "No regression.")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Recorded EvalOps evidence: bench-123", result.stdout)

        result = self.run_cli("eval")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("bench-123: score=91.5, regression=passed", result.stdout)

        result = self.run_cli("report")
        self.assertEqual(result.returncode, 0, result.stderr)
        report_text = Path(result.stdout.strip()).read_text(encoding="utf-8")
        self.assertIn("## EvalOps Evidence", report_text)
        self.assertIn("Benchmark `bench-123`", report_text)
        self.assertIn("- Score: `91.5`", report_text)

        result = self.run_cli("dashboard")
        self.assertEqual(result.returncode, 0, result.stderr)
        html = Path(result.stdout.strip()).read_text(encoding="utf-8")
        self.assertIn("Eval Runs", html)
        self.assertIn("bench-123", html)

    def test_eval_score_must_be_in_range(self) -> None:
        self.assertEqual(self.run_cli("init").returncode, 0)
        self.assertEqual(self.run_cli("start", "evalops run").returncode, 0)
        result = self.run_cli("eval", "bench-123", "--score", "101")
        self.assertEqual(result.returncode, 2)
        self.assertIn("score must be between 0 and 100", result.stderr)

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
