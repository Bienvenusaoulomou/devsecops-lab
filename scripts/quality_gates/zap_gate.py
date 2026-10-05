#!/usr/bin/env python3

import json
import sys
from pathlib import Path


REPORT_FILE = Path("reports/raw/zap/zap.json")


RISK_LEVELS = {
    "0": "Informational",
    "1": "Low",
    "2": "Medium",
    "3": "High",
}


def main():
    if not REPORT_FILE.exists():
        print(f"[ZAP GATE] ERROR: Report not found: {REPORT_FILE}")
        return 2

    try:
        with REPORT_FILE.open("r", encoding="utf-8") as file:
            report = json.load(file)
    except json.JSONDecodeError as exc:
        print(f"[ZAP GATE] ERROR: Invalid JSON: {exc}")
        return 2

    alerts = []

    for site in report.get("site", []):
        alerts.extend(site.get("alerts", []))

    counts = {
        "High": 0,
        "Medium": 0,
        "Low": 0,
        "Informational": 0,
        "Unknown": 0,
    }

    blocking_alerts = []

    for alert in alerts:
        riskcode = str(alert.get("riskcode", "")).strip()
        risk_level = RISK_LEVELS.get(riskcode, "Unknown")

        counts[risk_level] += 1

        if risk_level == "High":
            blocking_alerts.append(alert)

    print("[ZAP GATE] =============================")
    print("[ZAP GATE] OWASP ZAP Security Quality Gate")
    print("[ZAP GATE] =============================")
    print(f"[ZAP GATE] Total alerts : {len(alerts)}")
    print(f"[ZAP GATE] High        : {counts['High']}")
    print(f"[ZAP GATE] Medium      : {counts['Medium']}")
    print(f"[ZAP GATE] Low         : {counts['Low']}")
    print(f"[ZAP GATE] Informational: {counts['Informational']}")

    if counts["Unknown"] > 0:
        print(f"[ZAP GATE] Unknown     : {counts['Unknown']}")

    if blocking_alerts:
        print()
        print("[ZAP GATE] FAILED")
        print("[ZAP GATE] High-severity vulnerabilities detected:")

        for alert in blocking_alerts:
            name = alert.get("alert", "Unknown alert")
            plugin_id = alert.get("pluginid", "N/A")
            riskdesc = alert.get("riskdesc", "N/A")

            print(
                f"  - {name} "
                f"(plugin={plugin_id}, risk={riskdesc})"
            )

        return 1

    print()
    print("[ZAP GATE] PASSED")
    print("[ZAP GATE] No High-severity vulnerabilities detected.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
