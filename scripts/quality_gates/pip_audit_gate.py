#!/usr/bin/env python3

import json
import sys
from pathlib import Path


REPORT = Path("reports/raw/pip-audit/pip-audit.json")


def main():
    print("=== PIP-AUDIT QUALITY GATE ===")

    if not REPORT.exists():
        print(f"[ERROR] Report not found: {REPORT}")
        return 2

    try:
        with REPORT.open() as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[ERROR] Unable to read pip-audit report: {exc}")
        return 2

    dependencies = data.get("dependencies", [])

    vulnerabilities = [
        vuln
        for dependency in dependencies
        for vuln in dependency.get("vulns", [])
    ]

    print(f"Dependencies      : {len(dependencies)}")
    print(f"Vulnerabilities   : {len(vulnerabilities)}")

    if vulnerabilities:
        print(
            f"[BLOCK] {len(vulnerabilities)} known "
            "vulnerability(s) detected."
        )

        for dependency in dependencies:
            for vuln in dependency.get("vulns", []):
                print(
                    f"- {dependency.get('name')} "
                    f"{dependency.get('version')} | "
                    f"{vuln.get('id')} | "
                    f"{vuln.get('fix_versions')}"
                )

        return 1

    print("[PASS] No known vulnerabilities detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
