#!/usr/bin/env python3

import json
import sys
from pathlib import Path


REPORT = Path("reports/raw/dependency-check/dependency-check-report.json")


def main():
    print("=== OWASP DEPENDENCY-CHECK QUALITY GATE ===")

    if not REPORT.exists():
        print(f"[ERROR] Report not found: {REPORT}")
        return 2

    try:
        with REPORT.open(encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[ERROR] Unable to read Dependency-Check report: {exc}")
        return 2

    dependencies = data.get("dependencies", [])

    vulnerabilities = []

    for dependency in dependencies:
        for vulnerability in dependency.get("vulnerabilities", []):
            vulnerabilities.append(
                (dependency, vulnerability)
            )

    print(f"Dependencies      : {len(dependencies)}")
    print(f"Vulnerabilities   : {len(vulnerabilities)}")

    if vulnerabilities:
        print(
            f"[BLOCK] {len(vulnerabilities)} known "
            "vulnerability(s) detected."
        )

        for dependency, vulnerability in vulnerabilities:
            cvssv3 = vulnerability.get("cvssv3") or {}
            cvss_score = cvssv3.get("baseScore")

            print(
                f"- {dependency.get('fileName')} | "
                f"{vulnerability.get('name')} | "
                f"severity={vulnerability.get('severity')} | "
                f"CVSS={cvss_score}"
            )

        return 1

    print("[PASS] No known vulnerabilities detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
