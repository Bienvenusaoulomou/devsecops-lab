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
                        "Application tests passed successfully with coverage report." \
                        true
                '''
            }

            post {
                always {
                    archiveArtifacts artifacts: 'reports/raw/application-tests.log,reports/raw/coverage/coverage.xml',
                                     allowEmptyArchive: true,
                                     fingerprint: true
                }
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

        stage('SAST - SonarQube') {
            steps {
                echo '=== SAST - SONARQUBE ==='

                script {

                    // 1. Exécuter l'analyse SonarQube
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

                    // 2. Attendre le Quality Gate APRÈS la fermeture de withSonarQubeEnv
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

                // 3. Enregistrer le résultat uniquement si tout est passé
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
                    archiveArtifacts artifacts: 'reports/raw/sonarqube/sonar.log,reports/raw/coverage/coverage.xml',
                                     allowEmptyArchive: true,
                                     fingerprint: true
                }
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
                    archiveArtifacts artifacts: 'reports/raw/gitleaks/gitleaks.json',
                                     allowEmptyArchive: true,
                                     fingerprint: true
                }
            }
        }

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

        stage('Container Security - Trivy') {
            steps {
                echo '=== CONTAINER SECURITY - TRIVY ==='

                sh '''
                    set -e

                    mkdir -p reports/raw/trivy

                    rm -f reports/raw/trivy/trivy.json

                    echo "===== TRIVY VERSION ====="

                    trivy --version

                    echo "===== TRIVY IMAGE SCAN ====="

                    trivy image \
                        --severity HIGH,CRITICAL \
                        --ignore-unfixed \
                        --format json \
                        --output reports/raw/trivy/trivy.json \
                        "$APP_IMAGE:$BUILD_NUMBER"

                    echo "===== TRIVY SECURITY QUALITY GATE ====="

                    trivy image \
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
                        "Trivy container scan completed with no blocking HIGH or CRITICAL vulnerabilities." \
                        true
                '''
            }

            post {
                always {
                    archiveArtifacts artifacts: 'reports/raw/trivy/trivy.json',
                                     allowEmptyArchive: true,
                                     fingerprint: true
                }
            }
        }

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
                    archiveArtifacts artifacts: 'reports/raw/zap/*,reports/security/zap.*',
                                     allowEmptyArchive: true,
                                     fingerprint: true
                }
            }
        }
    }

post {

    always {

        // ============================================================
        // GENERATE PIPELINE SECURITY SUMMARY
        // ============================================================

        echo '=== GENERATING PIPELINE SECURITY SUMMARY ==='

        sh '''
            python3 scripts/generate_pipeline_summary.py
        '''

        // ============================================================
        // ARCHIVE SECURITY REPORTS
        // ============================================================

        archiveArtifacts(
            artifacts: 'reports/status/*.json',
            allowEmptyArchive: true,
            fingerprint: true
        )

        // ============================================================
        // CLEANUP APPLICATION CONTAINER
        // ============================================================

        echo '=== CLEANUP ==='

        sh '''
            echo "===== REMOVING APPLICATION CONTAINER ====="

            docker rm -f "$APP_CONTAINER" 2>/dev/null || true

            echo "===== CLEANUP COMPLETED ====="
        '''

        // ============================================================
        // SLACK DEVSECOPS REPORT
        // ============================================================

        script {

            echo '=== SENDING DEVSECOPS SLACK REPORT ==='

            if (!fileExists('reports/status/pipeline-summary.json')) {

                echo 'Slack notification skipped: pipeline summary not found.'

            } else {

                try {

                    // ------------------------------------------------
                    // READ CENTRALIZED SECURITY SUMMARY
                    // ------------------------------------------------

                    def summaryText = readFile(
                        file: 'reports/status/pipeline-summary.json'
                    )

                    def summary =
                        new groovy.json.JsonSlurper().parseText(summaryText)

                    // ------------------------------------------------
                    // GLOBAL PIPELINE INFORMATION
                    // ------------------------------------------------

                    def buildResult =
                        currentBuild.currentResult ?: 'UNKNOWN'

                    def total =
                        (summary.total ?: 0) as int

                    def passed =
                        (summary.pass ?: 0) as int

                    def failed =
                        (summary.fail ?: 0) as int

                    def pending =
                        (summary.pending ?: 0) as int

                    def blocking =
                        (summary.blocking_failures ?: 0) as int

                    def score =
                        summary.control_score != null
                            ? summary.control_score.toString()
                            : 'N/A'

                    def coverage =
                        summary.evaluation_coverage != null
                            ? summary.evaluation_coverage.toString()
                            : 'N/A'

                    // ------------------------------------------------
                    // PIPELINE RESULT
                    // ------------------------------------------------

                    def resultEmoji

                    if (
                        blocking > 0 ||
                        buildResult == 'FAILURE'
                    ) {

                        resultEmoji = ':x:'

                    } else if (
                        failed > 0 ||
                        buildResult == 'UNSTABLE'
                    ) {

                        resultEmoji = ':warning:'

                    } else if (
                        buildResult == 'SUCCESS'
                    ) {

                        resultEmoji = ':white_check_mark:'

                    } else {

                        resultEmoji = ':grey_question:'
                    }

                    // ------------------------------------------------
                    // SLACK HEADER
                    // ------------------------------------------------

                    def message = """
${resultEmoji} *DEVSECOPS PIPELINE — BUILD #${env.BUILD_NUMBER}*

*Project:* `${env.JOB_NAME}`
*Branch:* `${env.BRANCH_NAME ?: 'main'}`
*Commit:* `${env.GIT_COMMIT ?: 'N/A'}`
*Result:* *${buildResult}*

━━━━━━━━━━━━━━━━━━━━

*SECURITY SUMMARY*

:shield: *Control Score:* ${score}%
:bar_chart: *Evaluation Coverage:* ${coverage}%

:white_check_mark: *PASS:* ${passed}
:x: *FAIL:* ${failed}
:hourglass_flowing_sand: *PENDING:* ${pending}
:no_entry: *Blocking failures:* ${blocking}

*Controls evaluated:* ${total}

━━━━━━━━━━━━━━━━━━━━

*SECURITY CONTROLS*
"""

                    // ------------------------------------------------
                    // DYNAMIC SECURITY CONTROLS
                    // ------------------------------------------------

                    def results =
                        summary.results ?: []

                    results.each { control ->

                        def name =
                            control.control ?:
                            control.name ?:
                            control.id ?:
                            'Unknown'

                        def status =
                            (
                                control.status ?: 'UNKNOWN'
                            ).toString().toUpperCase()

                        def isBlocking =
                            control.blocking == true

                        def statusEmoji

                        switch (status) {

                            case 'PASS':

                                statusEmoji =
                                    ':white_check_mark:'

                                break

                            case 'FAIL':

                                statusEmoji =
                                    isBlocking
                                        ? ':no_entry:'
                                        : ':x:'

                                break

                            case 'PENDING':

                                statusEmoji =
                                    ':hourglass_flowing_sand:'

                                break

                            default:

                                statusEmoji =
                                    ':grey_question:'
                        }

                        def gateLabel =
                            isBlocking
                                ? ' — *GATE*'
                                : ''

                        message +=
                            "${statusEmoji} *${name}* — ${status}${gateLabel}\n"
                    }

                    // ------------------------------------------------
                    // BLOCKING FAILURES
                    // ------------------------------------------------

                    def blockingControls =
                        results.findAll { control ->

                            control.status
                                ?.toString()
                                ?.toUpperCase() == 'FAIL' &&

                            control.blocking == true
                        }

                    if (blockingControls) {

                        message += """

━━━━━━━━━━━━━━━━━━━━

:no_entry: *BLOCKING FAILURES*
"""

                        blockingControls.each { control ->

                            def name =
                                control.control ?:
                                control.name ?:
                                control.id ?:
                                'Unknown'

                            def reason =
                                control.message ?:
                                control.description ?:
                                'No reason provided.'

                            message +=
                                "• *${name}*: ${reason}\n"
                        }
                    }

                    // ------------------------------------------------
                    // REPORT EVIDENCE
                    // ------------------------------------------------

                    message += """

━━━━━━━━━━━━━━━━━━━━

:page_facing_up: *REPORTS*

• `reports/status/`
• `reports/raw/`
• `reports/security/`
"""

                    // ------------------------------------------------
                    // JENKINS BUILD LINK
                    // ------------------------------------------------

                    message += """

━━━━━━━━━━━━━━━━━━━━

:link: *Jenkins Build*

${env.BUILD_URL}

:robot_face: *Generated automatically by DevsecopsAI*
"""

                    // ------------------------------------------------
                    // SEND SLACK MESSAGE
                    // ------------------------------------------------

                    slackSend(
                        channel: '#devsecops-alerts',
                        message: message
                    )

                    echo 'Slack DevSecOps report sent successfully.'

                } catch (Exception e) {

                    echo "WARNING: Slack notification failed: ${e}"
                }
            }
        }

        // ============================================================
        // PIPELINE FINISHED
        // ============================================================

        echo '=== PIPELINE EXECUTION FINISHED ==='
    }
}
