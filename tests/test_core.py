from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agenttrace.core import changed_files_from_status, generate_run_id, read_json, write_json


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


if __name__ == "__main__":
    unittest.main()
