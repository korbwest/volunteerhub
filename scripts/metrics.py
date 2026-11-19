"""Collect report-based measurements; missing evidence is null, never a false zero."""

import argparse
import json
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

FIELDS = (
    "lint_errors",
    "lint_warnings",
    "line_coverage_percent",
    "tests_passed",
    "tests_failed",
    "tests_skipped",
    "test_duration_seconds",
)


def test_duration(root):
    """Use reported suite elapsed time; never sum nested suites twice."""
    if root.get("time") is not None:
        return round(float(root.get("time")), 4)
    suites = root.findall("testsuite")
    if suites and all(suite.get("time") is not None for suite in suites):
        return round(sum(float(suite.get("time")) for suite in suites), 4)
    return None


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else None


def percent(covered, total):
    return round(100 * covered / total, 2) if total else None


def collect(root: Path, stage: str, commit: str):
    now = datetime.now(UTC)
    result = {
        "schema_version": 2,
        "stage": stage,
        "commit": commit,
        "measured_at": now.isoformat(),
        "sources": [],
        "automated_metric_groups": 4,
        "commit_frequency": {
            "source": "GitHub Insights",
            "collection": "manual",
            "value": None,
        },
    }
    for side in ("backend", "frontend"):
        metrics = dict.fromkeys(FIELDS)
        folder = root / side
        lint_path = folder / ("ruff.json" if side == "backend" else "eslint.json")
        lint = read_json(lint_path)
        if lint is not None:
            metrics["lint_errors"] = (
                len(lint)
                if side == "backend"
                else sum(row["errorCount"] for row in lint)
            )
            metrics["lint_warnings"] = (
                0 if side == "backend" else sum(row["warningCount"] for row in lint)
            )
            result["sources"].append(str(lint_path.relative_to(root)))
        coverage_path = folder / (
            "coverage.json" if side == "backend" else "coverage-summary.json"
        )
        coverage = read_json(coverage_path)
        if coverage is not None:
            if side == "backend":
                totals = coverage["totals"]
                metrics["line_coverage_percent"] = percent(
                    totals["covered_lines"], totals["num_statements"]
                )
            else:
                totals = coverage["total"]
                metrics["line_coverage_percent"] = percent(
                    totals["lines"]["covered"], totals["lines"]["total"]
                )
            result["sources"].append(str(coverage_path.relative_to(root)))
        junit = folder / "junit.xml"
        if junit.exists():
            xml_root = ET.parse(junit).getroot()
            cases = list(xml_root.iter("testcase"))
            failed = sum(
                case.find("failure") is not None or case.find("error") is not None
                for case in cases
            )
            skipped = sum(case.find("skipped") is not None for case in cases)
            metrics.update(
                tests_passed=len(cases) - failed - skipped,
                tests_failed=failed,
                tests_skipped=skipped,
                test_duration_seconds=test_duration(xml_root),
            )
            result["sources"].append(str(junit.relative_to(root)))
        result[side] = metrics
    result["complete"] = False  # Fifth metric requires separate manual evidence.
    result["automated_complete"] = all(
        result[side][field] is not None
        for side in ("backend", "frontend")
        for field in FIELDS
    )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", type=Path, default=Path("reports"))
    parser.add_argument("--stage", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", type=Path, default=Path("reports/metrics.json"))
    args = parser.parse_args()
    result = collect(args.reports, args.stage, args.commit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["automated_complete"]:
        raise SystemExit("Required lint, coverage or test report is missing")


if __name__ == "__main__":
    main()
