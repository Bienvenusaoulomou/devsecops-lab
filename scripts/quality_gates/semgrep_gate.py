#!/usr/bin/env python3

import json
import sys
from pathlib import Path


REPORT = Path("reports/raw/semgrep/semgrep.json")


def main():
    if not REPORT.exists():
        print(f"[ERROR] Semgrep report not found: {REPORT}")
        return 2

    try:
        with REPORT.open() as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] Cannot read Semgrep report: {exc}")
        return 2

    errors = data.get("errors", [])
    results = data.get("results", [])

    print("=== SEMGREP QUALITY GATE ===")
    print(f"Results : {len(results)}")
    print(f"Errors  : {len(errors)}")

    if errors:
        print("[BLOCK] Semgrep reported scan errors.")
        return 1

    blocking = []

    for result in results:
        extra = result.get("extra", {})

        if extra.get("is_ignored") is True:
            continue

        severity = str(extra.get("severity", "")).upper()

        if severity in {"ERROR", "CRITICAL", "HIGH"}:
            blocking.append(result)

    if blocking:
        print(f"[BLOCK] {len(blocking)} blocking finding(s) detected.")

        for result in blocking:
            extra = result.get("extra", {})
            print(
                f"- {result.get('check_id')} | "
                f"{result.get('path')}:{result.get('start', {}).get('line')} | "
                f"severity={extra.get('severity')}"
            )

        return 1

    if results:
        print(
            f"[WARNING] {len(results)} finding(s) detected, "
            "but none are classified as blocking."
        )
        return 0

    print("[PASS] No Semgrep findings detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
