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

CONTROL_CATEGORIES = {
    "Application_Tests": "Testing",
    "SAST_Semgrep": "SAST",
    "SAST_Bandit": "SAST",
    "SCA_Pip_Audit": "SCA",
    "SCA_OWASP_Dependency_Check": "SCA",
    "Gitleaks": "Secret Scanning",
    "Docker_Build": "Build",
    "Trivy": "Container Security",
    "Application_Start": "Runtime",
    "DAST_OWASP_ZAP": "DAST",
}

total = len(EXPECTED_CONTROLS)

passed = 0
failed = 0
pending = 0
blocking_failures = 0

results = []

for control_name in EXPECTED_CONTROLS:

    path = STATUS_DIR / f"{control_name}.json"

    # ------------------------------------------------------------
    # CONTROL NOT EVALUATED
    # ------------------------------------------------------------

    if not path.exists():

        pending += 1

        results.append({
            "control": control_name,
            "category": CONTROL_CATEGORIES.get(
                control_name,
                "Security"
            ),
            "status": "PENDING",
            "message": "Control was not evaluated.",
            "blocking": False
        })

        continue

    # ------------------------------------------------------------
    # INVALID CONTROL REPORT
    # ------------------------------------------------------------

    try:
        data = json.loads(
            path.read_text(encoding="utf-8")
        )

    except Exception as exc:

        pending += 1

        results.append({
            "control": control_name,
            "category": CONTROL_CATEGORIES.get(
                control_name,
                "Security"
            ),
            "status": "PENDING",
            "message": f"Unable to read control report: {exc}",
            "blocking": False
        })

        continue

    # ------------------------------------------------------------
    # READ CONTROL RESULT
    # ------------------------------------------------------------

    status = str(
        data.get("status", "")
    ).upper()

    blocking = bool(
        data.get("blocking", False)
    )

    category = data.get(
        "category",
        CONTROL_CATEGORIES.get(
            control_name,
            "Security"
        )
    )

    message = data.get(
        "message",
        "No additional information."
    )

    control = data.get(
        "control",
        control_name
    )

    # ------------------------------------------------------------
    # COUNT RESULT
    # ------------------------------------------------------------

    if status == "PASS":

        passed += 1

    elif status == "FAIL":

        failed += 1

        if blocking:
            blocking_failures += 1

    else:

        pending += 1
        status = "PENDING"

    # ------------------------------------------------------------
    # STORE DYNAMIC RESULT
    # ------------------------------------------------------------

    results.append({
        "control": control,
        "category": category,
        "status": status,
        "message": message,
        "blocking": blocking
    })


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
    "evaluation_coverage": evaluation_coverage,
    "results": results
}


OUTPUT.write_text(
    json.dumps(
        summary,
        indent=2
    ),
    encoding="utf-8"
)


print("===== PIPELINE SECURITY SUMMARY =====")
print(json.dumps(summary, indent=2))
print(f"Summary written: {OUTPUT}")
