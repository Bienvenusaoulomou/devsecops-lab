#!/usr/bin/env python3

import json
import sys
from pathlib import Path


REPORT = Path("reports/raw/bandit/bandit.json")


def main():
    if not REPORT.exists():
        print(f"[ERROR] Bandit report not found: {REPORT}")
        return 2

    try:
        with REPORT.open() as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] Cannot read Bandit report: {exc}")
        return 2

    errors = data.get("errors", [])
    results = data.get("results", [])

    print("=== BANDIT QUALITY GATE ===")
    print(f"Results : {len(results)}")
    print(f"Errors  : {len(errors)}")

    if errors:
        print("[BLOCK] Bandit reported scan errors.")
        return 1

    blocking = []
    warnings = []

    for result in results:
        severity = str(
            result.get("issue_severity", "")
        ).upper()

        if severity == "HIGH":
            blocking.append(result)
        elif severity in {"MEDIUM", "LOW"}:
            warnings.append(result)

    if blocking:
        print(f"[BLOCK] {len(blocking)} HIGH finding(s) detected.")

        for result in blocking:
            print(
                f"- {result.get('test_id')} | "
                f"{result.get('filename')}:{result.get('line_number')} | "
                f"severity={result.get('issue_severity')} | "
                f"confidence={result.get('issue_confidence')} | "
                f"{result.get('issue_text')}"
            )

        if warnings:
            print(
                f"[WARNING] {len(warnings)} additional "
                "non-blocking finding(s) detected."
            )

        return 1

    if warnings:
        print(
            f"[WARNING] {len(warnings)} finding(s) detected, "
            "but none are classified as blocking."
        )

        for result in warnings:
            print(
                f"- {result.get('test_id')} | "
                f"{result.get('filename')}:{result.get('line_number')} | "
                f"severity={result.get('issue_severity')} | "
                f"confidence={result.get('issue_confidence')}"
            )

        return 0

    print("[PASS] No Bandit findings detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
