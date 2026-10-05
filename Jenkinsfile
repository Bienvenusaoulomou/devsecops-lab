pipeline {

    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        APP_IMAGE = 'devsecops-demo-app'
        APP_CONTAINER = 'devsecops-demo-app'
        APP_PORT = '8000'
        TARGET_PORT = "${APP_PORT}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo '=== CHECKOUT ==='
                checkout scm
            }
        }

        stage('Environment - Validation') {
            steps {
                echo '=== ENVIRONMENT VALIDATION ==='

                sh '''
                    set -e

                    echo "===== ENVIRONMENT ====="

                    echo "Python:"
                    python3 --version

                    echo "Java:"
                    java -version

                    echo "Maven:"
                    mvn --version

                    echo "Node:"
                    node --version

                    echo "npm:"
                    npm --version

                    echo "Docker:"
                    docker --version

                    echo "===== SECURITY TOOLS ====="

                    echo "Semgrep:"
                    semgrep --version

                    echo "Bandit:"
                    bandit --version

                    echo "pip-audit:"
                    pip-audit --version

                    echo "Gitleaks:"
                    gitleaks version

                    echo "Trivy:"
                    trivy --version

                    echo "Dependency-Check:"
                    dependency-check.sh --version

                    echo "SonarScanner:"
                    sonar-scanner --version

                    echo "===== VALIDATION COMPLETE ====="
                '''
            }
        }

        stage('Application - Tests') {
            steps {
                echo '=== APPLICATION TESTS ==='

                sh '''
                    set -e

                    rm -rf .venv-ci

                    python3 -m venv .venv-ci
                    . .venv-ci/bin/activate

                    python -m pip install --upgrade pip
                    python -m pip install -r application/requirements.txt
                    python -m pip install pytest

                    echo "===== PYTHON VERSION ====="
                    python --version

                    echo "===== PYTEST VERSION ====="
                    python -m pytest --version

                    echo "===== RUNNING APPLICATION TESTS ====="

                    python -m pytest \
                        application/tests \
                        -v \
                        > reports/raw/application-tests.log 2>&1

                    cat reports/raw/application-tests.log

                    echo "===== APPLICATION TESTS PASSED ====="
                '''

                sh '''
                    python3 scripts/write_status.py \
                        Application_Tests \
                        Tests \
                        PASS \
                        "Application tests passed successfully." \
                        true
                '''
            }
        }

        stage('SAST - Semgrep') {
            steps {
                echo '=== SAST - SEMGREP ==='

                sh '''
                    set -e

                    mkdir -p reports/raw/semgrep

                    echo "===== RUNNING SEMGREP ====="

                    semgrep scan \
                        --config auto \
                        application \
                        --json \
                        > reports/raw/semgrep/semgrep.json

                    echo "===== SEMGREP QUALITY GATE ====="

                    python3 scripts/quality_gates/semgrep_gate.py
                '''

                sh '''
                    python3 scripts/write_status.py \
                        SAST_Semgrep \
                        SAST \
                        PASS \
                        "Semgrep scan completed and quality gate passed." \
                        true
                '''
            }
        }

        stage('SAST - Bandit') {
            steps {
                echo '=== SAST - BANDIT ==='

                sh '''
                    set -e

                    mkdir -p reports/raw/bandit

                    echo "===== RUNNING BANDIT ====="

                    bandit \
                        -r application/app \
                        -f json \
                        -o reports/raw/bandit/bandit.json

                    echo "===== BANDIT QUALITY GATE ====="

                    python3 scripts/quality_gates/bandit_gate.py
                '''

                sh '''
                    python3 scripts/write_status.py \
                        SAST_Bandit \
                        SAST \
                        PASS \
                        "Bandit scan completed and quality gate passed." \
                        true
                '''
            }
        }

        stage('SCA - pip-audit') {
            steps {
                echo '=== SCA - PIP-AUDIT ==='

                sh '''
                    set -e

                    mkdir -p reports/raw/pip-audit

                    echo "===== RUNNING PIP-AUDIT ====="

                    pip-audit \
                        -r application/requirements.txt \
                        --format json \
                        --output reports/raw/pip-audit/pip-audit.json

                    echo "===== PIP-AUDIT QUALITY GATE ====="

                    python3 scripts/quality_gates/pip_audit_gate.py
                '''

                sh '''
                    python3 scripts/write_status.py \
                        SCA_Pip_Audit \
                        SCA \
                        PASS \
                        "pip-audit scan completed and quality gate passed." \
                        true
                '''
            }
        }
        stage('SCA - OWASP Dependency-Check') {
    steps {
        echo '=== SCA - OWASP DEPENDENCY-CHECK ==='

        withCredentials([
            string(
                credentialsId: 'nvd-api-key',
                variable: 'NVD_API_KEY'
            )
        ]) {
            sh '''
                set -e

                mkdir -p reports/raw/dependency-check

                echo "===== NVD API KEY VALIDATION ====="

                if [ -z "$NVD_API_KEY" ]; then
                    echo "[ERROR] NVD_API_KEY is empty or was not injected by Jenkins."
                    exit 1
                fi

                echo "[OK] NVD_API_KEY is injected by Jenkins."

                echo "===== BUILDING JAVA TEST PROJECT ====="

                mvn -f sca-test-java/pom.xml clean package -DskipTests

                echo "===== RUNNING OWASP DEPENDENCY-CHECK ====="

                dependency-check.sh \
                    --project "devsecops-sca-java" \
                    --scan sca-test-java \
                    --nvdApiKey "$NVD_API_KEY" \
                    --format JSON \
                    --format HTML \
                    --out reports/raw/dependency-check

                echo "===== OWASP DEPENDENCY-CHECK QUALITY GATE ====="

                python3 scripts/quality_gates/dependency_check_gate.py
            '''
        }

        sh '''
            python3 scripts/write_status.py \
                SCA_OWASP_Dependency_Check \
                SCA \
                PASS \
                "OWASP Dependency-Check scan completed and quality gate passed." \
                true
        '''
    }
}
stage('DAST - OWASP ZAP') {
    steps {
        echo '=== DAST - OWASP ZAP ==='

        sh '''
            set -e

            echo "===== DAST: APPLICATION AVAILABILITY ====="

            docker run --rm \
                --network devsecops-net \
                curlimages/curl:latest \
                --fail --silent --show-error \
                http://devsecops-demo-app:8081/health

            echo "===== DAST: PREPARING DIRECTORIES ====="

            mkdir -p reports/raw/zap
            mkdir -p reports/security

            rm -f zap-test/zap.json
            rm -f zap-test/zap.html
            rm -f reports/raw/zap/zap.json
            rm -f reports/raw/zap/zap.html

            echo "===== DAST: RUNNING OWASP ZAP ====="

            docker run --rm \
                --network devsecops-net \
                -v "$PWD/zap-test:/zap/wrk:rw" \
                ghcr.io/zaproxy/zaproxy:stable \
                zap.sh -cmd \
                -autorun /zap/wrk/zap-ci.yaml

            echo "===== DAST: VALIDATING ZAP OUTPUT ====="

            test -f zap-test/zap.json
            test -f zap-test/zap.html

            echo "[OK] ZAP JSON report generated."
            echo "[OK] ZAP HTML report generated."

            echo "===== DAST: COPYING REPORTS ====="

            cp zap-test/zap.json reports/raw/zap/zap.json
            cp zap-test/zap.html reports/raw/zap/zap.html

            echo "===== DAST: ZAP QUALITY GATE ====="

            python3 scripts/quality_gates/zap_gate.py

            echo "===== DAST: PUBLISHING SECURITY REPORTS ====="

            cp reports/raw/zap/zap.json reports/security/zap.json
            cp reports/raw/zap/zap.html reports/security/zap.html

            echo "===== DAST COMPLETED SUCCESSFULLY ====="
        '''

        sh '''
            python3 scripts/write_status.py \
                DAST_OWASP_ZAP \
                DAST \
                PASS \
                "OWASP ZAP DAST scan completed and security quality gate passed." \
                true
        '''
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/raw/zap/*,reports/security/zap.*',
                             allowEmptyArchive: true,
                             fingerprint: true
        }
    }
}
    }

    post {
        always {
            echo '=== PIPELINE EXECUTION FINISHED ==='
        }
    }
}
