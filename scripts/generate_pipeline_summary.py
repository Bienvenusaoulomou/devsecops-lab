from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET


STATUS_DIR = Path("reports/status")
RAW_DIR = Path("reports/raw")
OUTPUT = STATUS_DIR / "pipeline-summary.json"


# ============================================================
# EXPECTED CONTROLS
# ============================================================

EXPECTED_CONTROLS = [
    "Application_Tests",
    "SAST_Semgrep",
    "SAST_Bandit",
    "SAST_SonarQube",
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
    "SAST_SonarQube": "SAST",
    "SCA_Pip_Audit": "SCA",
    "SCA_OWASP_Dependency_Check": "SCA",
    "Gitleaks": "Secret Scanning",
    "Docker_Build": "Build",
    "Trivy": "Container Security",
    "Application_Start": "Runtime",
    "DAST_OWASP_ZAP": "DAST",
}


# ============================================================
# HELPERS
# ============================================================

def read_json(path):
    if not path.exists():
        return None

    try:
        return json.loads(
            path.read_text(encoding="utf-8")
        )
    except Exception:
        return None


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ============================================================
# APPLICATION TESTS
# ============================================================

def parse_application_tests():
    metrics = {
        "tests": 0,
        "passed": 0,
        "failed": 0,
        "warnings": 0,
        "coverage_percent": 0.0,
        "lines_covered": 0,
        "lines_valid": 0,
    }

    path = RAW_DIR / "application-tests.log"

    if not path.exists():
        return metrics

    text = path.read_text(
        encoding="utf-8",
        errors="replace"
    )

    # --------------------------------------------------------
    # Pytest summary
    #
    # Example:
    # 6 passed, 2 warnings in 0.79s
    # --------------------------------------------------------

    passed_match = re.search(
        r"(\d+)\s+passed\b",
        text,
        re.IGNORECASE
    )

    failed_match = re.search(
        r"(\d+)\s+failed\b",
        text,
        re.IGNORECASE
    )

    warning_match = re.search(
        r"(\d+)\s+warnings?\b",
        text,
        re.IGNORECASE
    )

    passed = (
        safe_int(passed_match.group(1))
        if passed_match
        else 0
    )

    failed = (
        safe_int(failed_match.group(1))
        if failed_match
        else 0
    )

    warnings = (
        safe_int(warning_match.group(1))
        if warning_match
        else 0
    )

    metrics["passed"] = passed
    metrics["failed"] = failed
    metrics["tests"] = passed + failed
    metrics["warnings"] = warnings

    # --------------------------------------------------------
    # Coverage XML
    # --------------------------------------------------------

    coverage_path = (
        RAW_DIR
        / "coverage"
        / "coverage.xml"
    )

    if coverage_path.exists():
        try:
            root = ET.parse(
                coverage_path
            ).getroot()

            line_rate = root.attrib.get(
                "line-rate"
            )

            metrics["coverage_percent"] = round(
                safe_float(line_rate) * 100,
                2
            )

            metrics["lines_valid"] = safe_int(
                root.attrib.get(
                    "lines-valid"
                )
            )

            metrics["lines_covered"] = safe_int(
                root.attrib.get(
                    "lines-covered"
                )
            )

        except Exception:
            pass

    return metrics


# ============================================================
# SEMGREP
# ============================================================

def parse_semgrep():
    metrics = {
        "findings": 0,
        "error": 0,
        "warning": 0,
        "info": 0,
    }

    data = read_json(
        RAW_DIR
        / "semgrep"
        / "semgrep.json"
    )

    if not data:
        return metrics

    results = data.get(
        "results",
        []
    )

    metrics["findings"] = len(results)

    for result in results:
        severity = str(
            result.get(
                "extra",
                {}
            ).get(
                "severity",
                ""
            )
        ).lower()

        if severity == "error":
            metrics["error"] += 1

        elif severity == "warning":
            metrics["warning"] += 1

        elif severity == "info":
            metrics["info"] += 1

    return metrics


# ============================================================
# BANDIT
# ============================================================

def parse_bandit():
    metrics = {
        "findings": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    data = read_json(
        RAW_DIR
        / "bandit"
        / "bandit.json"
    )

    if not data:
        return metrics

    results = data.get(
        "results",
        []
    )

    metrics["findings"] = len(results)

    for result in results:
        severity = str(
            result.get(
                "issue_severity",
                ""
            )
        ).lower()

        if severity == "high":
            metrics["high"] += 1

        elif severity == "medium":
            metrics["medium"] += 1

        elif severity == "low":
            metrics["low"] += 1

    return metrics


# ============================================================
# SONARQUBE
# ============================================================

def parse_sonarqube(status_data):
    status = str(
        status_data.get(
            "status",
            ""
        )
    ).upper()

    message = str(
        status_data.get(
            "message",
            ""
        )
    )

    quality_gate = status

    message_lower = message.lower()

    if "quality gate" in message_lower:

        if "pass" in message_lower:
            quality_gate = "PASS"

        elif "fail" in message_lower:
            quality_gate = "FAIL"

    return {
        "quality_gate": quality_gate
    }


# ============================================================
# PIP-AUDIT
# ============================================================

def parse_pip_audit():
    metrics = {
        "dependencies": 0,
        "vulnerable_dependencies": 0,
        "vulnerabilities": 0,
    }

    data = read_json(
        RAW_DIR
        / "pip-audit"
        / "pip-audit.json"
    )

    if not data:
        return metrics

    dependencies = data.get(
        "dependencies",
        []
    )

    metrics["dependencies"] = len(
        dependencies
    )

    for dependency in dependencies:

        vulnerabilities = dependency.get(
            "vulns",
            []
        )

        if vulnerabilities:
            metrics["vulnerable_dependencies"] += 1

            metrics["vulnerabilities"] += len(
                vulnerabilities
            )

    return metrics


# ============================================================
# OWASP DEPENDENCY-CHECK
# ============================================================

def parse_dependency_check():
    metrics = {
        "artifacts": 0,
        "vulnerabilities": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    data = read_json(
        RAW_DIR
        / "dependency-check"
        / "dependency-check-report.json"
    )

    if not data:
        return metrics

    dependencies = data.get(
        "dependencies",
        []
    )

    metrics["artifacts"] = len(
        dependencies
    )

    for dependency in dependencies:

        vulnerabilities = dependency.get(
            "vulnerabilities",
            []
        )

        metrics["vulnerabilities"] += len(
            vulnerabilities
        )

        for vulnerability in vulnerabilities:

            severity = str(
                vulnerability.get(
                    "severity",
                    ""
                )
            ).lower()

            if severity == "critical":
                metrics["critical"] += 1

            elif severity == "high":
                metrics["high"] += 1

            elif severity == "medium":
                metrics["medium"] += 1

            elif severity == "low":
                metrics["low"] += 1

    return metrics


# ============================================================
# GITLEAKS
# ============================================================

def parse_gitleaks():
    metrics = {
        "secrets": 0,
    }

    data = read_json(
        RAW_DIR
        / "gitleaks"
        / "gitleaks.json"
    )

    if isinstance(data, list):

        metrics["secrets"] = len(data)

    elif isinstance(data, dict):

        findings = data.get(
            "findings",
            []
        )

        if isinstance(findings, list):
            metrics["secrets"] = len(
                findings
            )

    return metrics


# ============================================================
# DOCKER BUILD
# ============================================================

def parse_docker_build(status_data):
    message = str(
        status_data.get(
            "message",
            ""
        )
    )

    image = "devsecops-demo-app"
    tag = None

    tag_match = re.search(
        r"([A-Za-z0-9_.-]+):([A-Za-z0-9_.-]+)",
        message
    )

    if tag_match:
        image = tag_match.group(1)
        tag = tag_match.group(2)

    return {
        "image": image,
        "tag": tag,
    }


# ============================================================
# TRIVY
# ============================================================

def parse_trivy():
    metrics = {
        "total": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "unknown": 0,
    }

    data = read_json(
        RAW_DIR
        / "trivy"
        / "trivy.json"
    )

    if not data:
        return metrics

    results = data.get(
        "Results",
        []
    )

    for result in results:

        vulnerabilities = result.get(
            "Vulnerabilities",
            []
        )

        if not isinstance(
            vulnerabilities,
            list
        ):
            continue

        for vulnerability in vulnerabilities:

            metrics["total"] += 1

            severity = str(
                vulnerability.get(
                    "Severity",
                    "UNKNOWN"
                )
            ).upper()

            if severity == "CRITICAL":
                metrics["critical"] += 1

            elif severity == "HIGH":
                metrics["high"] += 1

            elif severity == "MEDIUM":
                metrics["medium"] += 1

            elif severity == "LOW":
                metrics["low"] += 1

            else:
                metrics["unknown"] += 1

    return metrics


# ============================================================
# APPLICATION START
# ============================================================

def parse_application_start(status_data):
    status = str(
        status_data.get(
            "status",
            ""
        )
    ).upper()

    message = str(
        status_data.get(
            "message",
            ""
        )
    )

    return {
        "health_check": (
            "PASS"
            if status == "PASS"
            else "FAIL"
        ),
        "message": message,
    }


# ============================================================
# ZAP
# ============================================================

def parse_zap():
    metrics = {
        "alerts": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "informational": 0,
    }

    data = read_json(
        RAW_DIR
        / "zap"
        / "zap.json"
    )

    if not data:
        return metrics

    sites = data.get(
        "site",
        []
    )

    if isinstance(sites, dict):
        sites = [sites]

    if not isinstance(sites, list):
        return metrics

    for site in sites:

        if not isinstance(site, dict):
            continue

        alerts = site.get(
            "alerts",
            []
        )

        if isinstance(alerts, dict):
            alerts = [alerts]

        if not isinstance(alerts, list):
            continue

        for alert in alerts:

            if not isinstance(alert, dict):
                continue

            metrics["alerts"] += 1

            risk_code = str(
                alert.get(
                    "riskcode",
                    ""
                )
            )

            if risk_code == "3":
                metrics["high"] += 1

            elif risk_code == "2":
                metrics["medium"] += 1

            elif risk_code == "1":
                metrics["low"] += 1

            elif risk_code == "0":
                metrics["informational"] += 1

    return metrics


# ============================================================
# METRICS DISPATCHER
# ============================================================

def extract_metrics(
    control_name,
    status_data
):
    if control_name == "Application_Tests":
        return parse_application_tests()

    if control_name == "SAST_Semgrep":
        return parse_semgrep()

    if control_name == "SAST_Bandit":
        return parse_bandit()

    if control_name == "SAST_SonarQube":
        return parse_sonarqube(
            status_data
        )

    if control_name == "SCA_Pip_Audit":
        return parse_pip_audit()

    if control_name == "SCA_OWASP_Dependency_Check":
        return parse_dependency_check()

    if control_name == "Gitleaks":
        return parse_gitleaks()

    if control_name == "Docker_Build":
        return parse_docker_build(
            status_data
        )

    if control_name == "Trivy":
        return parse_trivy()

    if control_name == "Application_Start":
        return parse_application_start(
            status_data
        )

    if control_name == "DAST_OWASP_ZAP":
        return parse_zap()

    return {}


# ============================================================
# BUILD SUMMARY
# ============================================================

total = len(
    EXPECTED_CONTROLS
)

passed = 0
failed = 0
pending = 0
blocking_failures = 0

results = []


for control_name in EXPECTED_CONTROLS:

    path = STATUS_DIR / (
        f"{control_name}.json"
    )

    # --------------------------------------------------------
    # CONTROL NOT EVALUATED
    # --------------------------------------------------------

    if not path.exists():

        pending += 1

        results.append({
            "control": control_name,
            "category": CONTROL_CATEGORIES.get(
                control_name,
                "Security"
            ),
            "status": "PENDING",
            "message": (
                "Control was not evaluated."
            ),
            "blocking": False,
            "metrics": {},
        })

        continue

    # --------------------------------------------------------
    # INVALID CONTROL REPORT
    # --------------------------------------------------------

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
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
            "message": (
                "Unable to read control "
                f"report: {exc}"
            ),
            "blocking": False,
            "metrics": {},
        })

        continue

    # --------------------------------------------------------
    # READ CONTROL RESULT
    # --------------------------------------------------------

    status = str(
        data.get(
            "status",
            ""
        )
    ).upper()

    blocking = bool(
        data.get(
            "blocking",
            False
        )
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

    # --------------------------------------------------------
    # COUNT RESULT
    # --------------------------------------------------------

    if status == "PASS":

        passed += 1

    elif status == "FAIL":

        failed += 1

        if blocking:
            blocking_failures += 1

    else:

        pending += 1
        status = "PENDING"

    # --------------------------------------------------------
    # EXTRACT REAL METRICS
    # --------------------------------------------------------

    metrics = extract_metrics(
        control_name,
        data
    )

    # --------------------------------------------------------
    # STORE RESULT
    # --------------------------------------------------------

    results.append({
        "control": control,
        "category": category,
        "status": status,
        "message": message,
        "blocking": blocking,
        "metrics": metrics,
    })


# ============================================================
# GLOBAL METRICS
# ============================================================

evaluated = passed + failed

control_score = (
    round(
        (passed / total) * 100,
        2
    )
    if total
    else 0
)

evaluation_coverage = (
    round(
        (evaluated / total) * 100,
        2
    )
    if total
    else 0
)


# ============================================================
# FINAL SUMMARY
# ============================================================

summary = {
    "total": total,
    "pass": passed,
    "fail": failed,
    "pending": pending,
    "blocking_failures": blocking_failures,
    "control_score": control_score,
    "evaluation_coverage": evaluation_coverage,
    "results": results,
}


STATUS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT.write_text(
    json.dumps(
        summary,
        indent=2
    ),
    encoding="utf-8"
)


print(
    "===== PIPELINE SECURITY SUMMARY ====="
)

print(
    json.dumps(
        summary,
        indent=2
    )
)

print(
    f"Summary written: {OUTPUT}"
)
