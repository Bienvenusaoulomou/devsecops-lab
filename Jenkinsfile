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

        // ============================================================
        // CHECKOUT
        // ============================================================

        stage('Checkout') {
            steps {
                echo '=== CHECKOUT ==='

                checkout scm
            }
        }


        // ============================================================
        // ENVIRONMENT VALIDATION
        // ============================================================

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


        // ============================================================
        // APPLICATION TESTS
        // ============================================================

        stage('Application - Tests') {
            steps {
                echo '=== APPLICATION TESTS ==='

                sh '''
                    set -e

                    mkdir -p reports/raw
                    mkdir -p reports/raw/coverage

                    rm -rf .venv-ci

                    python3 -m venv .venv-ci
                    . .venv-ci/bin/activate

                    python -m pip install --upgrade pip
                    python -m pip install -r application/requirements.txt
                    python -m pip install pytest pytest-cov

                    echo "===== PYTHON VERSION ====="
                    python --version

                    echo "===== PYTEST VERSION ====="
                    python -m pytest --version

                    echo "===== RUNNING APPLICATION TESTS ====="

                    python -m pytest \
                        application/tests \
                        -v \
                        --cov=application/app \
                        --cov-report=term-missing \
                        --cov-report=xml:reports/raw/coverage/coverage.xml \
                        > reports/raw/application-tests.log 2>&1

                    cat reports/raw/application-tests.log

                    echo "===== APPLICATION TESTS PASSED ====="

                    echo "===== COVERAGE REPORT ====="

                    test -f reports/raw/coverage/coverage.xml

                    ls -lh reports/raw/coverage/coverage.xml

                    echo "===== COVERAGE REPORT GENERATED SUCCESSFULLY ====="
                '''

                sh '''
                    python3 scripts/write_status.py \
                        Application_Tests \
                        Tests \
                        PASS \
                        "Application tests completed successfully." \
                        true
                '''
            }

            post {
                always {
                    archiveArtifacts(
                        artifacts: 'reports/raw/application-tests.log,reports/raw/coverage/coverage.xml',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                }
            }
        }


        // ============================================================
        // SAST - SEMGREP
        // ============================================================

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

                    test -f reports/raw/semgrep/semgrep.json

                    echo "===== SEMGREP QUALITY GATE ====="

                    python3 scripts/quality_gates/semgrep_gate.py

                    echo "===== SEMGREP QUALITY GATE PASSED ====="
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

            post {
                always {
                    archiveArtifacts(
                        artifacts: 'reports/raw/semgrep/semgrep.json',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                }
            }
        }


        // ============================================================
        // SAST - BANDIT
        // ============================================================

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

                    test -f reports/raw/bandit/bandit.json

                    echo "===== BANDIT QUALITY GATE ====="

                    python3 scripts/quality_gates/bandit_gate.py

                    echo "===== BANDIT QUALITY GATE PASSED ====="
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

            post {
                always {
                    archiveArtifacts(
                        artifacts: 'reports/raw/bandit/bandit.json',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                }
            }
        }


        // ============================================================
        // SAST - SONARQUBE
        // ============================================================

        stage('SAST - SonarQube') {
            steps {
                echo '=== SAST - SONARQUBE ==='

                script {

                    withSonarQubeEnv('sonarqube-local') {

                        sh '''
                            set -e

                            mkdir -p reports/raw/sonarqube

                            echo "===== CHECKING COVERAGE REPORT ====="

                            if [ ! -f reports/raw/coverage/coverage.xml ]; then
                                echo "[ERROR] coverage.xml not found."
                                exit 1
                            fi

                            echo "[OK] Coverage report found."

                            ls -lh reports/raw/coverage/coverage.xml

                            echo "===== RUNNING SONARQUBE ANALYSIS ====="

                            sonar-scanner \
                                -Dsonar.projectKey=devsecops-lab \
                                -Dsonar.projectName=devsecops-lab \
                                -Dsonar.sources=application \
                                -Dsonar.exclusions="**/node_modules/**,**/.venv/**,**/venv/**,**/tests/**" \
                                -Dsonar.python.coverage.reportPaths=reports/raw/coverage/coverage.xml \
                                > reports/raw/sonarqube/sonar.log 2>&1

                            cat reports/raw/sonarqube/sonar.log

                            echo "===== SONARQUBE ANALYSIS COMPLETED ====="
                        '''
                    }

                    echo '=== WAITING FOR SONARQUBE QUALITY GATE ==='

                    timeout(
                        time: 5,
                        unit: 'MINUTES'
                    ) {

                        def qualityGate = waitForQualityGate()

                        echo "SonarQube Quality Gate status: ${qualityGate.status}"

                        if (qualityGate.status != 'OK') {
                            error("SonarQube Quality Gate failed: ${qualityGate.status}")
                        }
                    }
                }

                sh '''
                    python3 scripts/write_status.py \
                        SAST_SonarQube \
                        SAST \
                        PASS \
                        "SonarQube analysis completed and Quality Gate passed." \
                        true
                '''
            }

            post {
                always {
                    archiveArtifacts(
                        artifacts: 'reports/raw/sonarqube/sonar.log,reports/raw/coverage/coverage.xml',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                }
            }
        }


        // ============================================================
        // SCA - PIP-AUDIT
        // ============================================================

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

                    test -f reports/raw/pip-audit/pip-audit.json

                    echo "===== PIP-AUDIT QUALITY GATE ====="

                    python3 scripts/quality_gates/pip_audit_gate.py

                    echo "===== PIP-AUDIT QUALITY GATE PASSED ====="
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

            post {
                always {
                    archiveArtifacts(
                        artifacts: 'reports/raw/pip-audit/pip-audit.json',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                }
            }
        }


        // ============================================================
        // SCA - OWASP DEPENDENCY-CHECK
        // ============================================================

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

                        test -f reports/raw/dependency-check/dependency-check-report.json

                        echo "===== OWASP DEPENDENCY-CHECK QUALITY GATE ====="

                        python3 scripts/quality_gates/dependency_check_gate.py

                        echo "===== DEPENDENCY-CHECK QUALITY GATE PASSED ====="
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

            post {
                always {
                    archiveArtifacts(
                        artifacts: 'reports/raw/dependency-check/dependency-check-report.json,reports/raw/dependency-check/dependency-check-report.html',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                }
            }
        }


        // ============================================================
        // SECRETS - GITLEAKS
        // ============================================================

        stage('Secrets - Gitleaks') {
            steps {
                echo '=== SECRETS SCAN - GITLEAKS ==='

                sh '''
                    set -e

                    mkdir -p reports/raw/gitleaks

                    rm -f reports/raw/gitleaks/gitleaks.json

                    echo "===== RUNNING GITLEAKS ====="

                    gitleaks detect \
                        --source . \
                        --report-format json \
                        --report-path reports/raw/gitleaks/gitleaks.json \
                        --redact \
                        --no-banner

                    echo "===== VALIDATING GITLEAKS REPORT ====="

                    test -f reports/raw/gitleaks/gitleaks.json

                    echo "===== GITLEAKS RESULTS ====="

                    cat reports/raw/gitleaks/gitleaks.json

                    echo "===== GITLEAKS COMPLETED SUCCESSFULLY ====="
                '''

                sh '''
                    python3 scripts/write_status.py \
                        Gitleaks \
                        Secrets \
                        PASS \
                        "Gitleaks secrets scan completed successfully with no secrets detected." \
                        true
                '''
            }

            post {
                always {
                    archiveArtifacts(
                        artifacts: 'reports/raw/gitleaks/gitleaks.json',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                }
            }
        }


        // ============================================================
        // DOCKER BUILD
        // ============================================================

        stage('Docker - Build Image') {
            steps {
                echo '=== DOCKER BUILD ==='

                sh '''
                    set -e

                    echo "===== DOCKER BUILD ====="

                    docker build \
                        --pull \
                        -t "$APP_IMAGE:$BUILD_NUMBER" \
                        ./application

                    echo "===== VERIFYING IMAGE ====="

                    docker image inspect \
                        "$APP_IMAGE:$BUILD_NUMBER" \
                        --format 'Image ID: {{.Id}}'

                    docker image inspect \
                        "$APP_IMAGE:$BUILD_NUMBER" \
                        --format 'Created: {{.Created}}'

                    echo "===== DOCKER BUILD COMPLETED SUCCESSFULLY ====="
                '''

                sh '''
                    python3 scripts/write_status.py \
                        Docker_Build \
                        Container \
                        PASS \
                        "Docker application image built successfully." \
                        true
                '''
            }
        }


        // ============================================================
        // CONTAINER SECURITY - TRIVY
        // ============================================================

        stage('Container Security - Trivy') {
            steps {
                echo '=== CONTAINER SECURITY - TRIVY ==='

                sh '''
                    set -e

                    mkdir -p reports/raw/trivy

                    rm -f reports/raw/trivy/trivy.json

                    echo "===== TRIVY VERSION ====="

                    trivy --version

                    echo "===== TRIVY FULL VULNERABILITY REPORT ====="

                    trivy image \
                        --scanners vuln \
                        --ignore-unfixed \
                        --format json \
                        --output reports/raw/trivy/trivy.json \
                        "$APP_IMAGE:$BUILD_NUMBER"

                    test -f reports/raw/trivy/trivy.json

                    echo "===== TRIVY SECURITY QUALITY GATE ====="

                    trivy image \
                        --scanners vuln \
                        --severity HIGH,CRITICAL \
                        --ignore-unfixed \
                        --exit-code 1 \
                        "$APP_IMAGE:$BUILD_NUMBER"

                    echo "===== TRIVY QUALITY GATE PASSED ====="
                '''

                sh '''
                    python3 scripts/write_status.py \
                        Trivy \
                        Container_Security \
                        PASS \
                        "Trivy container scan completed and quality gate passed." \
                        true
                '''
            }

            post {
                always {
                    archiveArtifacts(
                        artifacts: 'reports/raw/trivy/trivy.json',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                }
            }
        }


        // ============================================================
        // APPLICATION START
        // ============================================================

        stage('Application - Start') {
            steps {
                echo '=== APPLICATION START ==='

                sh '''
                    set -e

                    echo "===== CLEANING PREVIOUS CONTAINER ====="

                    docker rm -f "$APP_CONTAINER" 2>/dev/null || true

                    echo "===== STARTING APPLICATION ====="

                    docker run -d \
                        --name "$APP_CONTAINER" \
                        --network devsecops-net \
                        -p "$APP_PORT:8081" \
                        "$APP_IMAGE:$BUILD_NUMBER"

                    echo "===== WAITING FOR APPLICATION ====="

                    for i in $(seq 1 30); do

                        if docker run --rm \
                            --network devsecops-net \
                            curlimages/curl:latest \
                            --fail --silent --show-error \
                            "http://$APP_CONTAINER:8081/health"; then

                            echo "[OK] Application is healthy."
                            exit 0
                        fi

                        echo "Waiting for application... attempt $i/30"

                        sleep 2
                    done

                    echo "[ERROR] Application did not become healthy."

                    docker logs "$APP_CONTAINER" || true

                    exit 1
                '''

                sh '''
                    python3 scripts/write_status.py \
                        Application_Start \
                        Deployment \
                        PASS \
                        "Application container started successfully and health check passed." \
                        true
                '''
            }
        }


        // ============================================================
        // DAST - OWASP ZAP
        // ============================================================

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

                    echo "===== DAST: CHECKING ZAP CONFIG ====="

                    test -f zap-test/zap-ci.yaml

                    echo "[OK] zap-ci.yaml found in Jenkins workspace."

                    echo "===== DAST: VERIFYING ZAP DOCKER MOUNT ====="

                    docker run --rm \
                        -v "/var/lib/docker/volumes/devsecops_jenkins_home/_data/workspace/devsecops-lab/zap-test:/zap/wrk:ro" \
                        alpine:3.20 \
                        test -f /zap/wrk/zap-ci.yaml

                    echo "[OK] ZAP configuration is visible from Docker."

                    echo "===== DAST: RUNNING OWASP ZAP ====="

                    docker run --rm \
                        --network devsecops-net \
                        -v "/var/lib/docker/volumes/devsecops_jenkins_home/_data/workspace/devsecops-lab/zap-test:/zap/wrk:rw" \
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
                    archiveArtifacts(
                        artifacts: 'reports/raw/zap/*,reports/security/zap.*',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                }
            }
        }
    }


    // ================================================================
    // PIPELINE POST
    // ================================================================

    post {

    always {

        script {

            // ============================================================
            // 1. GENERATION DU RESUME CENTRALISE
            // ============================================================
            echo '=== GENERATING PIPELINE SECURITY SUMMARY ==='

            sh '''
                python3 scripts/generate_pipeline_summary.py
            '''

            // ============================================================
            // 2. ARCHIVAGE DU RESUME
            // ============================================================
            echo '=== ARCHIVING SECURITY SUMMARY ==='

            archiveArtifacts(
                artifacts: 'reports/status/**',
                allowEmptyArchive: true,
                fingerprint: true
            )

            // ============================================================
            // 3. CLEANUP APPLICATION CONTAINER
            // ============================================================
            echo '=== CLEANUP ==='

            sh '''
                docker rm -f "$APP_CONTAINER" 2>/dev/null || true
            '''

            echo '=== CLEANUP COMPLETED ==='

            // ============================================================
            // 4. SLACK SECURITY REPORT
            // ============================================================
            echo '=== SENDING DEVSECOPS SLACK REPORT ==='

            try {

                retry(count: 2, conditions: [nonresumable()]) {

                    script {

                        if (!fileExists('reports/status/pipeline-summary.json')) {

                            echo 'Security summary not found. Slack notification skipped.'

                        } else {

                            def summaryText = readFile(
                                'reports/status/pipeline-summary.json'
                            )

                            def summary =
                                new groovy.json.JsonSlurperClassic()
                                    .parseText(summaryText)

                            // ====================================================
                            // CONTROL INFORMATION
                            // ====================================================
                            def controlInfo = [

                                'Application_Tests': [
                                    label: 'Application Tests',
                                    role: 'Validation fonctionnelle',
                                    icon: '🧪'
                                ],

                                'SAST_Semgrep': [
                                    label: 'Semgrep',
                                    role: 'Analyse statique — SAST',
                                    icon: '🔍'
                                ],

                                'SAST_Bandit': [
                                    label: 'Bandit',
                                    role: 'Analyse de sécurité Python — SAST',
                                    icon: '🐍'
                                ],

                                'SAST_SonarQube': [
                                    label: 'SonarQube',
                                    role: 'Analyse statique et Quality Gate — SAST',
                                    icon: '📊'
                                ],

                                'SCA_Pip_Audit': [
                                    label: 'pip-audit',
                                    role: 'Analyse des dépendances Python — SCA',
                                    icon: '📦'
                                ],

                                'SCA_OWASP_Dependency_Check': [
                                    label: 'Dependency-Check',
                                    role: 'Analyse des dépendances Java — SCA',
                                    icon: '📦'
                                ],

                                'Gitleaks': [
                                    label: 'Gitleaks',
                                    role: 'Détection de secrets',
                                    icon: '🔐'
                                ],

                                'Docker_Build': [
                                    label: 'Docker Build',
                                    role: 'Construction de l’image conteneur',
                                    icon: '🐳'
                                ],

                                'Trivy': [
                                    label: 'Trivy',
                                    role: 'Sécurité de l’image conteneur',
                                    icon: '🛡️'
                                ],

                                'Application_Start': [
                                    label: 'Application Start',
                                    role: 'Démarrage et validation runtime',
                                    icon: '🚀'
                                ],

                                'DAST_OWASP_ZAP': [
                                    label: 'OWASP ZAP',
                                    role: 'Analyse dynamique — DAST',
                                    icon: '🌐'
                                ]
                            ]

                            // ====================================================
                            // STATUS HELPERS
                            // ====================================================
                            def statusEmoji = { status ->
                                switch (status) {
                                    case 'PASS':
                                        return '🟢'
                                    case 'FAIL':
                                        return '🔴'
                                    case 'PENDING':
                                        return '⏳'
                                    default:
                                        return '⚪'
                                }
                            }

                            def statusLabel = { status ->
                                switch (status) {
                                    case 'PASS':
                                        return 'PASS'
                                    case 'FAIL':
                                        return 'FAIL'
                                    case 'PENDING':
                                        return 'PENDING'
                                    default:
                                        return status ?: 'UNKNOWN'
                                }
                            }

                            // ====================================================
                            // GLOBAL PIPELINE DATA
                            // ====================================================
                            def result =
                                currentBuild.currentResult ?: 'SUCCESS'

                            def total =
                                summary.total ?: 0

                            def passed =
                                summary.pass ?: 0

                            def failed =
                                summary.fail ?: 0

                            def pending =
                                summary.pending ?: 0

                            def blockingFailures =
                                summary.blocking_failures ?: 0

                            def score =
                                summary.control_score ?: 0

                            def coverage =
                                summary.evaluation_coverage ?: 0

                            // ====================================================
                            // PIPELINE DECISION
                            // ====================================================
                            def pipelineApproved = (
                                result == 'SUCCESS' &&
                                blockingFailures == 0 &&
                                failed == 0 &&
                                pending == 0
                            )

                            def decisionTitle
                            def decisionMessage

                            if (pipelineApproved) {

                                decisionTitle =
                                    '🟢 PIPELINE APPROUVÉ'

                                decisionMessage =
                                    'Tous les contrôles de sécurité sont passés. Aucun gate bloquant en échec.'

                            } else {

                                decisionTitle =
                                    '🔴 PIPELINE BLOQUÉ'

                                decisionMessage =
                                    'Au moins un contrôle bloquant a échoué ou reste en attente. Le pipeline ne peut pas être considéré comme sécurisé.'
                            }

                            // ====================================================
                            // BUILD STATUS
                            // ====================================================
                            def buildEmoji

                            switch (result) {
                                case 'SUCCESS':
                                    buildEmoji = '🟢'
                                    break

                                case 'FAILURE':
                                    buildEmoji = '🔴'
                                    break

                                case 'UNSTABLE':
                                    buildEmoji = '🟠'
                                    break

                                default:
                                    buildEmoji = '⚪'
                            }

                            // ====================================================
                            // SLACK MESSAGE — COMPACT / SINGLE MESSAGE
                            // ====================================================
                            def message = """
🤖 *PIPELINE DEVSECOPS — BUILD #${env.BUILD_NUMBER}*

📋 *EXÉCUTION*
Projet : ${env.JOB_NAME} | Branche : ${env.GIT_BRANCH ?: 'main'} | Commit : ${(env.GIT_COMMIT ?: 'N/A').take(8)}
Résultat : ${buildEmoji} ${result}

🛡️ *SCORECARD SÉCURITÉ*
Score : *${score}%* | Couverture : *${coverage}%*
Total : ${total} | ✅ PASS : ${passed} | ❌ FAIL : ${failed} | ⏳ PENDING : ${pending} | 🚫 Bloquants : ${blockingFailures}

🔎 *CONTRÔLES DE SÉCURITÉ*
"""

                            // ====================================================
                            // DYNAMIC CONTROL DETAILS
                            // ====================================================
                            summary.results.each { control ->

                                def name = control.control
                                def status = control.status ?: 'UNKNOWN'
                                def metrics = control.metrics ?: [:]

                                def info = controlInfo[name] ?: [
                                    label: name,
                                    role: 'Contrôle de sécurité',
                                    icon: '🔹'
                                ]

                                // Tous les contrôles sont des gates bloquants
                                def gateLabel = 'GATE BLOQUANT'

                                def metricsText = ''

                                switch (name) {

                                    case 'Application_Tests':

                                        metricsText =
                                            "${metrics.passed ?: 0}/${metrics.tests ?: 0} tests · " +
                                            "Coverage ${metrics.coverage_percent ?: 0}% · " +
                                            "${metrics.lines_covered ?: 0}/${metrics.lines_valid ?: 0} lignes · " +
                                            "${metrics.warnings ?: 0} warning(s)"

                                        break

                                    case 'SAST_Semgrep':

                                        metricsText =
                                            "${metrics.findings ?: 0} findings · " +
                                            "Error ${metrics.error ?: 0} · " +
                                            "Warning ${metrics.warning ?: 0}"

                                        break

                                    case 'SAST_Bandit':

                                        metricsText =
                                            "${metrics.findings ?: 0} findings · " +
                                            "High ${metrics.high ?: 0} · " +
                                            "Medium ${metrics.medium ?: 0} · " +
                                            "Low ${metrics.low ?: 0}"

                                        break

                                    case 'SAST_SonarQube':

                                        metricsText =
                                            "Quality Gate : ${metrics.quality_gate ?: 'UNKNOWN'}"

                                        break

                                    case 'SCA_Pip_Audit':

                                        metricsText =
                                            "${metrics.dependencies ?: 0} dépendances · " +
                                            "${metrics.vulnerable_dependencies ?: 0} vulnérable(s) · " +
                                            "${metrics.vulnerabilities ?: 0} CVE"

                                        break

                                    case 'SCA_OWASP_Dependency_Check':

                                        metricsText =
                                            "${metrics.artifacts ?: 0} artifact(s) · " +
                                            "${metrics.vulnerabilities ?: 0} vulnérabilité(s) · " +
                                            "Critical ${metrics.critical ?: 0} · " +
                                            "High ${metrics.high ?: 0}"

                                        break

                                    case 'Gitleaks':

                                        metricsText =
                                            "${metrics.secrets ?: 0} secret(s) détecté(s)"

                                        break

                                    case 'Docker_Build':

                                        def imageName =
                                            metrics.image ?: env.APP_IMAGE

                                        def imageTag =
                                            metrics.tag ?: env.BUILD_NUMBER

                                        metricsText =
                                            "Image ${imageName}:${imageTag}"

                                        break

                                    case 'Trivy':

                                        metricsText =
                                            "Critical ${metrics.critical ?: 0} · " +
                                            "High ${metrics.high ?: 0} · " +
                                            "Medium ${metrics.medium ?: 0} · " +
                                            "Low ${metrics.low ?: 0}"

                                        break

                                    case 'Application_Start':

                                        metricsText =
                                            "Health check : ${metrics.health_check ?: 'UNKNOWN'}"

                                        break

                                    case 'DAST_OWASP_ZAP':

                                        metricsText =
                                            "${metrics.alerts ?: 0} alert(s) · " +
                                            "High ${metrics.high ?: 0} · " +
                                            "Medium ${metrics.medium ?: 0} · " +
                                            "Low ${metrics.low ?: 0}"

                                        break

                                    default:

                                        metricsText =
                                            'Métriques disponibles dans le rapport centralisé'
                                }

                                message +=
                                    "${info.icon} *${info.label}* — _${info.role}_\n" +
                                    "${statusEmoji(status)} *${statusLabel(status)} · ${gateLabel}* · ${metricsText}\n"
                            }

                            // ====================================================
                            // FINAL DECISION + EVIDENCE
                            // ====================================================
                            message += """

🚦 *DÉCISION DU PIPELINE*
${decisionTitle}
${decisionMessage}

📊 *PREUVES DE SÉCURITÉ*
Rapports : reports/status/ | reports/raw/ | reports/security/
Synthèse : reports/status/pipeline-summary.json

🔗 *JENKINS BUILD*
${env.BUILD_URL}

🤖 Généré automatiquement par *DevsecopsAI*
"""

                            // ====================================================
                            // SLACK SEND
                            // ====================================================
                            def slackColor

                            switch (result) {
                                case 'SUCCESS':
                                    slackColor = 'good'
                                    break

                                case 'FAILURE':
                                    slackColor = 'danger'
                                    break

                                case 'UNSTABLE':
                                    slackColor = 'warning'
                                    break

                                default:
                                    slackColor = '#808080'
                            }

                            slackSend(
                                channel: 'devsecops-alerts',
                                color: slackColor,
                                message: message
                            )

                            echo '=== SLACK REPORT SENT SUCCESSFULLY ==='
                        }
                    }
                }

            } catch (Exception e) {

                echo "Slack notification failed: ${e.message}"

                if (!currentBuild.currentResult ||
                    currentBuild.currentResult == 'SUCCESS') {

                    currentBuild.result = 'UNSTABLE'
                }
            }

            echo '=== PIPELINE EXECUTION FINISHED ==='
        }
    }
}