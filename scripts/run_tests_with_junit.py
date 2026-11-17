"""Run the unittest suite once and write one combined JUnit XML report.

The report contains one <testcase> per unittest method, including pass, failure,
error, and skipped outcomes. It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import time
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


class JUnitTextTestResult(unittest.TextTestResult):
    """Collect unittest outcomes while preserving normal console output."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.case_records: list[dict[str, object]] = []
        self._started_at: dict[unittest.case.TestCase, float] = {}
        self._outcomes: dict[unittest.case.TestCase, tuple[str, str, str]] = {}

    def startTest(self, test):
        self._started_at[test] = time.perf_counter()
        self._outcomes[test] = ("success", "", "")
        super().startTest(test)

    def addSuccess(self, test):
        super().addSuccess(test)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._outcomes[test] = (
            "failure",
            self._exception_message(err),
            self._exc_info_to_string(err, test),
        )

    def addError(self, test, err):
        super().addError(test, err)
        self._outcomes[test] = (
            "error",
            self._exception_message(err),
            self._exc_info_to_string(err, test),
        )

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._outcomes[test] = ("skipped", reason, "")

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._outcomes[test] = (
            "skipped",
            "Expected failure",
            self._exc_info_to_string(err, test),
        )

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._outcomes[test] = (
            "failure",
            "Unexpected success",
            "Test was marked expected-to-fail but passed.",
        )

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self._outcomes[test] = (
                "failure",
                self._exception_message(err),
                self._exc_info_to_string(err, subtest),
            )

    @staticmethod
    def _exception_message(err) -> str:
        exception_type, exception_value, _ = err
        return f"{exception_type.__name__}: {exception_value}"

    def stopTest(self, test):
        outcome, message, details = self._outcomes.pop(
            test, ("success", "", "")
        )
        started = self._started_at.pop(test, time.perf_counter())
        self.case_records.append(
            {
                "classname": (
                    f"{test.__class__.__module__}."
                    f"{test.__class__.__qualname__}"
                ),
                "name": getattr(test, "_testMethodName", str(test)),
                "time": max(0.0, time.perf_counter() - started),
                "outcome": outcome,
                "message": message,
                "details": details,
            }
        )
        super().stopTest(test)


def write_junit_report(records: list[dict[str, object]], output: Path) -> None:
    """Write a single JUnit-compatible XML file for the complete suite."""
    output.parent.mkdir(parents=True, exist_ok=True)

    failures = sum(record["outcome"] == "failure" for record in records)
    errors = sum(record["outcome"] == "error" for record in records)
    skipped = sum(record["outcome"] == "skipped" for record in records)
    duration = sum(float(record["time"]) for record in records)

    suite = ET.Element(
        "testsuite",
        {
            "name": "Voice Assistant automated tests",
            "tests": str(len(records)),
            "failures": str(failures),
            "errors": str(errors),
            "skipped": str(skipped),
            "time": f"{duration:.6f}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    for record in records:
        case = ET.SubElement(
            suite,
            "testcase",
            {
                "classname": str(record["classname"]),
                "name": str(record["name"]),
                "time": f"{float(record['time']):.6f}",
            },
        )
        outcome = record["outcome"]
        if outcome == "failure":
            node = ET.SubElement(
                case,
                "failure",
                {"message": str(record["message"])},
            )
            node.text = str(record["details"])
        elif outcome == "error":
            node = ET.SubElement(
                case,
                "error",
                {"message": str(record["message"])},
            )
            node.text = str(record["details"])
        elif outcome == "skipped":
            node = ET.SubElement(
                case,
                "skipped",
                {"message": str(record["message"])},
            )
            node.text = str(record["details"])

    tree = ET.ElementTree(suite)
    ET.indent(tree, space="  ")
    tree.write(output, encoding="utf-8", xml_declaration=True)

    print(
        f"JUnit report: {output} "
        f"({len(records)} tests, {failures} failures, "
        f"{errors} errors, {skipped} skipped)"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="test-results/junit-results.xml",
        help="Path for the single combined JUnit XML report.",
    )
    args = parser.parse_args()

    suite = unittest.defaultTestLoader.discover(
        start_dir="tests",
        top_level_dir=".",
    )
    runner = unittest.TextTestRunner(
        verbosity=2,
        resultclass=JUnitTextTestResult,
    )
    result = runner.run(suite)

    write_junit_report(result.case_records, Path(args.output))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
