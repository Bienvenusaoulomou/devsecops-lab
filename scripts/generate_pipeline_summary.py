from pathlib import Path
import json

STATUS_DIR = Path("reports/status")
OUTPUT = STATUS_DIR / "pipeline-summary.json"

EXPECTED_CONTROLS = [
    "Application_Tests",
    "SAST_Semgrep",
    "SAST_Bandit",
    "SCA_Pip_Audit",
    "SCA_OWASP_Dependency_Check",
    "Gitleaks",
    "Docker_Build",
    "Trivy",
    "Application_Start",
    "DAST_OWASP_ZAP",
]

total = len(EXPECTED_CONTROLS)
passed = 0
failed = 0
pending = 0
blocking_failures = 0

for control in EXPECTED_CONTROLS:
    path = STATUS_DIR / f"{control}.json"

    if not path.exists():
        pending += 1
        continue

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pending += 1
        continue

    status = str(data.get("status", "")).upper()
    blocking = bool(data.get("blocking", False))

    if status == "PASS":
        passed += 1
    elif status == "FAIL":
        failed += 1
        if blocking:
            blocking_failures += 1
    else:
        pending += 1

evaluated = passed + failed

control_score = round(
    (passed / total) * 100,
    2
) if total else 0

evaluation_coverage = round(
    (evaluated / total) * 100,
    2
) if total else 0

summary = {
    "total": total,
    "pass": passed,
    "fail": failed,
    "pending": pending,
    "blocking_failures": blocking_failures,
    "control_score": control_score,
    "evaluation_coverage": evaluation_coverage
}

OUTPUT.write_text(
    json.dumps(summary, indent=2),
    encoding="utf-8"
)

print("===== PIPELINE SECURITY SUMMARY =====")
print(json.dumps(summary, indent=2))
print(f"Summary written: {OUTPUT}")
