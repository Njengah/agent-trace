from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agenttrace.core import (
    changed_files_from_status,
    evaluate_evidence_policy,
    generate_run_id,
    normalize_evidence_policy,
    parse_github_pr_identifier,
    parse_github_remote_url,
    read_json,
    write_json,
)


class CoreTests(unittest.TestCase):
    def test_generate_run_id_uses_timestamp_and_slug(self) -> None:
        now = datetime(2026, 5, 18, 12, 30, 5, tzinfo=timezone.utc)
        self.assertEqual(
            generate_run_id("Add API validation!", now=now),
            "20260518-123005-add-api-validation",
        )

    def test_generate_run_id_falls_back_for_empty_slug(self) -> None:
        now = datetime(2026, 5, 18, 12, 30, 5, tzinfo=timezone.utc)
        self.assertEqual(generate_run_id("!!!", now=now), "20260518-123005-run")

    def test_json_helpers_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "data.json"
            write_json(path, {"b": 2, "a": 1})
            self.assertEqual(read_json(path), {"a": 1, "b": 2})
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(raw["a"], 1)

    def test_changed_files_from_status_handles_renames(self) -> None:
        status = " M src/app.py\n?? notes.md\nR  old.txt -> new.txt\n"
        self.assertEqual(changed_files_from_status(status), ["new.txt", "notes.md", "src/app.py"])

    def test_normalize_evidence_policy_uses_defaults(self) -> None:
        self.assertEqual(
            normalize_evidence_policy({"require_reviews": True}),
            {
                "require_tests": True,
                "require_reviews": True,
                "require_clean_snapshot": False,
                "fail_on_failed_tests": True,
            },
        )

    def test_evaluate_evidence_policy_reports_required_failures(self) -> None:
        result = evaluate_evidence_policy(
            {
                "latest_snapshot": {"dirty": True},
                "tests": [{"exit_code": 1}],
                "reviews": [],
            },
            {
                "require_tests": True,
                "require_reviews": True,
                "require_clean_snapshot": True,
                "fail_on_failed_tests": True,
            },
        )
        self.assertFalse(result["passed"])
        self.assertEqual(
            [failure["name"] for failure in result["failures"]],
            ["review evidence recorded", "latest snapshot clean", "recorded tests passed"],
        )

    def test_parse_github_pr_identifier_accepts_number_or_url(self) -> None:
        self.assertEqual(parse_github_pr_identifier("42"), {"number": 42})
        self.assertEqual(
            parse_github_pr_identifier("https://github.com/acme/widgets/pull/42"),
            {
                "owner": "acme",
                "repo": "widgets",
                "number": 42,
                "url": "https://github.com/acme/widgets/pull/42",
            },
        )

    def test_parse_github_remote_url_supports_common_formats(self) -> None:
        self.assertEqual(parse_github_remote_url("https://github.com/acme/widgets.git"), ("acme", "widgets"))
        self.assertEqual(parse_github_remote_url("git@github.com:acme/widgets.git"), ("acme", "widgets"))
        self.assertEqual(parse_github_remote_url("ssh://git@github.com/acme/widgets.git"), ("acme", "widgets"))
        self.assertIsNone(parse_github_remote_url("https://example.com/acme/widgets.git"))


if __name__ == "__main__":
    unittest.main()
