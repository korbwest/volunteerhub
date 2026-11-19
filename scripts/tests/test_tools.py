import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_commits import valid_message
from scripts.metrics import collect


class ToolTests(unittest.TestCase):
    def test_conventional_commits(self):
        self.assertTrue(valid_message("feat(auth): add login"))
        self.assertTrue(
            valid_message(
                "fix!: reject unsafe requests\n\nBREAKING CHANGE: authentication"
            )
        )
        self.assertFalse(valid_message("update files"))
        self.assertFalse(valid_message("feat: "))
        self.assertFalse(valid_message("Merge branch 'feature'"))

    def test_missing_reports_are_not_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            result = collect(Path(folder), "prototype", "abc123")
            self.assertIsNone(result["backend"]["lint_errors"])
            self.assertIsNone(result["backend"]["tests_passed"])
            self.assertEqual(result["commit"], "abc123")
            self.assertFalse(result["complete"])
            self.assertEqual(result["commit_frequency"]["collection"], "manual")
            self.assertIsNone(result["commit_frequency"]["value"])

    def test_failures_skips_coverage_and_lint(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "backend").mkdir()
            (root / "frontend").mkdir()
            (root / "backend/ruff.json").write_text(
                '[{"code":"F401"}]', encoding="utf-8"
            )
            (root / "backend/coverage.json").write_text(
                json.dumps(
                    {
                        "totals": {
                            "covered_lines": 8,
                            "num_statements": 10,
                            "covered_branches": 1,
                            "num_branches": 2,
                        }
                    }
                ),
                encoding="utf-8",
            )
            (root / "backend/junit.xml").write_text(
                '<testsuites><testsuite time="2.5"><testcase time="0.5"/><testcase time="1"><failure/></testcase><testcase time="0.1"><skipped/></testcase></testsuite></testsuites>',
                encoding="utf-8",
            )
            (root / "frontend/eslint.json").write_text(
                '[{"errorCount":2,"warningCount":3}]', encoding="utf-8"
            )
            result = collect(root, "prototype", "abc")
            self.assertEqual(result["backend"]["tests_passed"], 1)
            self.assertEqual(result["backend"]["tests_failed"], 1)
            self.assertEqual(result["backend"]["tests_skipped"], 1)
            self.assertEqual(result["backend"]["line_coverage_percent"], 80)
            self.assertNotIn("branch_coverage_percent", result["backend"])
            self.assertEqual(result["backend"]["test_duration_seconds"], 2.5)
            self.assertEqual(result["backend"]["lint_errors"], 1)
            self.assertEqual(result["frontend"]["lint_warnings"], 3)

    def test_nested_junit_does_not_double_count_duration(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "frontend").mkdir()
            (root / "frontend/junit.xml").write_text(
                '<testsuites time="4"><testsuite time="4"><testsuite time="2"><testcase time="1"/></testsuite></testsuite></testsuites>',
                encoding="utf-8",
            )
            result = collect(root, "prototype", "invalid")
            self.assertEqual(result["frontend"]["test_duration_seconds"], 4)

    def test_missing_suite_time_is_not_fabricated(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "backend").mkdir()
            (root / "backend/junit.xml").write_text(
                '<testsuite><testcase time="1"/></testsuite>', encoding="utf-8"
            )
            result = collect(root, "prototype", "invalid")
            self.assertIsNone(result["backend"]["test_duration_seconds"])


if __name__ == "__main__":
    unittest.main()
