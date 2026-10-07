# 🛡️ DevSecOps Lab

## Sécurisation d'un pipeline CI/CD avec une approche DevSecOps

[![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D24939?logo=jenkins&logoColor=white)](https://www.jenkins.io/)
[![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![SonarQube](https://img.shields.io/badge/SonarQube-SAST-4E9BCD?logo=sonarqube&logoColor=white)](https://www.sonarsource.com/products/sonarqube/)
[![Semgrep](https://img.shields.io/badge/Semgrep-SAST-FF6F00?logo=semgrep&logoColor=white)](https://semgrep.dev/)
[![Trivy](https://img.shields.io/badge/Trivy-Container%20Scanning-1904DA?logo=aqua&logoColor=white)](https://trivy.dev/)
[![OWASP%20ZAP](https://img.shields.io/badge/OWASP%20ZAP-DAST-00549E?logo=owasp&logoColor=white)](https://www.zaproxy.org/)
[![Gitleaks](https://img.shields.io/badge/Gitleaks-Secret%20Scanning-000000?logo=git&logoColor=white)](https://gitleaks.io/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github&logoColor=white)](https://github.com/)

---

## 📌 1. Présentation

Ce projet met en œuvre une approche **DevSecOps** visant à intégrer la sécurité directement dans le cycle CI/CD.

L'objectif est de détecter automatiquement les vulnérabilités et les problèmes de sécurité le plus tôt possible, puis d'utiliser des **Quality Gates** pour empêcher la validation d'une version lorsqu'un contrôle de sécurité bloquant échoue.

Le pipeline couvre plusieurs dimensions de la sécurité :

- **SAST** — analyse statique du code ;
- **SCA** — analyse des dépendances ;
- **Secret Scanning** — détection des secrets ;
- **Container Scanning** — analyse de l'image Docker ;
- **DAST** — analyse dynamique de l'application ;
- **Quality Gates** — décision de validation ou de blocage ;
- **Reporting** — centralisation des résultats ;
- **Alerting** — notifications.

---

# 🏗️ 2. Architecture du système

> Cette représentation textuelle sera remplacée par un diagramme d'architecture SVG/PNG professionnel dans une prochaine étape.

```text
Developer
    │
    ▼
Pre-commit Security
    │
    ▼
GitHub Repository
    │
    ▼
Jenkins CI/CD
    │
    ├── SAST
   'b��── SCA
   'b��── Secret Scanning
   'b��
    ▼
Docker Build
    │
    ▼
Trivy Container Scan
   'b��
    ▼
Running Application
   'b��
    ▼
OWASP ZAP / DAST
   'b��
    ▼
Centralized Reporting
    │
    ▼
Quality Gate
    │
   'b��── PASS
    └── BLOCK
   'b��
    ▼
Slack Notification
```

---

# 🔄 3. Flux CI/CD

Le pipeline Jenkins suit le flux suivant :

```text
1. Checkout
      ↓
2. Environment Validation
      ↓
3. Build & Tests
      ↓
4. SAST
      ↓
5. SCA
      ↓
6. Secret Scanning
      ↓
7. Docker Image Build
      ↓
8. Container Scanning
      ↓
9. Application Start
      ↓
10. DAST
      ↓
11. Centralized Reporting
      ↓
12. Quality Gate
      ↓
   PASS / BLOCK
      ↓
13. Notification
```

---

# 🛡️ 4. Contrôles de sécurité

## 4.1 SAST — Static Application Security Testing

Le SAST analyse le code source sans exécuter l'application.

### SonarQube

SonarQube est utilisé pour l'analyse statique et la qualité du code.

### Semgrep

Semgrep analyse le code à partir de règles de sécurité afin d'identifier des patterns potentiellement dangereux.

### Bandit

Bandit réalise une analyse de sécurité spécifique du code Python.

---

## 4.2 SCA — Software Composition Analysis

Le SCA analyse les dépendances utilisées par l'application.

### OWASP Dependency-Check

Dependency-Check recherche les vulnérabilités connues dans les dépendances du projet.

### pip-audit

pip-audit vérifie les packages Python utilisés par l'application et recherche les vulnérabilités connues.

---

## 4.3 Secret Scanning

### Gitleaks

Gitleaks recherche les informations sensibles potentiellement exposées dans le dépôt, notamment :

- API keys ;
- tokens ;
- credentials ;
- mots de passe ;
- secrets.

Des contrôles **pre-commit** permettent également d'effectuer des vérifications avant l'envoi du code dans le dépôt distant.

---

## 4.4 Container Security

### Trivy

Après la construction de l'image Docker, Trivy analyse l'image afin d'identifier les vulnérabilités présentes dans ses composants.

Le scan porte notamment sur :

- packages système ;
- dépendances ;
- composants de l'image ;
- vulnérabilités connues.

---

## 4.5 DAST — Dynamic Application Security Testing

### OWASP ZAP

OWASP ZAP intervient après le démarrage de l'application.

Il analyse l'application **en fonctionnement** afin d'identifier des problèmes de sécurité détectables dynamiquement.

La cible utilisée dans le pipeline est :

```text
http://devsecops-demo-app:8000
```

Les résultats sont ensuite récupérés dans les répertoires de reporting.

---

# 🚦 5. Quality Gate

La Quality Gate constitue le mécanisme de décision final du pipeline.

Les résultats des différents contrôles sont centralisés afin de déterminer si le pipeline peut être considéré comme conforme.

Le résumé contient notamment :

```text
total
pass
fail
pending
blocking_failures
control_score
evaluation_coverage
```

La logique de décision est :

```text
              Security Controls
                      │
                     'b��
              Result Evaluation
                      │
                     'b��
             blocking_failures
                 /                          /                          > 0            = 0
               │               │
              'b��              'b��
          ❌ BLOCK           ✅ PASS
```

Lorsqu'un contrôle identifié comme bloquant échoue, le pipeline est considéré comme non conforme.

---

# 📊 6. Reporting

Les résultats des contrôles sont centralisés dans :

```text
reports/
├── raw/
├── security/
└── status/
```

Les données brutes des différents outils sont conservées dans `reports/raw/`.

Les résultats de sécurité consolidés sont stockés dans `reports/security/`.

Les informations relatives aux status sont conservées dans `reports/status/`.

Le fichier de synthèse principal est :

```text
reports/security/pipeline-summary.json
```

---

# 🔠 7. Notifications

Les résultats du pipeline peuvent être transmis è **Slack** afin de fournir une visibilité rapide sur :

- le résultat du build ;
- l'état des contrôles ;
- les �chncs ;
- les contrôles bloquants ;
- le résultat final du pipeline.

---

# 🪠 8. Stack technique

| Domaine | Outil | Fonction |
|---|---|---|
| Source Control | GitHub | Gestion du code source |
| CI/CD | Jenkins | Orchestration du pipeline |
| Containerisation | Docker | Construction et exécution de l'application |
| SAST | SonarQube | Analyse statique |
| SAST | Semgrep | Analyse de sécurité |
| SAST | Bandit | Analyse Python |
| SCA | OWASP Dependency-Check | Analyse des dépendances |
| SCA | pip-audit | Audit des packages Python |
| Secret Scanning | Gitleaks | Détection des secrets |
| Container Security | Trivy | Scan de l'image Docker |
| DAST | OWASP ZAP | Analyse dynamique |
| Pre-commit | Security Git Hooks | Contrôles locaux |
| Notification | Slack | Alertes du pipeline |

---

# 🐐 9. Organisation du projet

```text
devsecops-lab/
│
├── app/
│
├── tests/
│
   ├── cslint-test/
│
   ├── gitleaks-test/
│   ├── semgrep-test/
│   ├── zap-test/
│   ├── sca-test-java/
│
├── reports/
│   ├── raw/
│   ├── security/
│   └── status/
│
├── Dockerfile
├── Dockerfile.jenkins
├── docker-compose.yml
├── .pre-commit-config.yaml
├── README.md
└── ...
```

---

# �� 10. Approche Shift Left

La sécurité commence dès le poste du développeur et se poursuit dans le pipeline CI/CD.

```text
Developer
    │
    ▼
Pre-commit Security
    │
    ▼
GitHub
    │
    ▼
Jenkins
    │
    ├── SAST
    ├── SCA
    ├── Secret Scanning
    ├── Container Scanning
    └── DAST
             │
             ▼
        Quality Gate
          │     │
        PASS   BLOCK
```

Cette approche permet de déplacer progressivement les contrôles de sécurité vers les premières étapes du cycle de développement.

---

# 🎯 11. Objectifs du projet

Le projet vise à :

- intégrer la sécurité dans le processus CI/CD ;
- appliquer le principe **Shift Left** ;
- automatiser les contrôles de sécurité ;
- détecter les vulnérabilités avant la livraison ;
- bloquer les résultats non conformes ;
- centraliser les résultats ;
- améliorer la traçabilité ;
- fournir des notifications sur l'état du pipeline.

---

# ✅ 12. Synthèse

Le pipeline combine :

```text
SAST
 │
 ├── SonarQube
 ├── Semgrep
 └── Bandit

SCA
 │
 ├── OWASP Dependency-Check
 └── pip-audit

Secret Scanning
 │
 └── Gitleaks

Container Security
 │
 └── Trivy

DAST
 │
 └── OWASP ZAP

        ↓

Centralized Reporting

        ↓

Quality Gate

   ┌────┴────┐
   ▼         ▼
 PASS      BLOCK

        ↓

      Slack
```

L'ensemble forme une chaîne de sécurité intégrée au processus CI/CD, permettant de contrôler le code, les dépendances, les secrets, l'image Docker et l'application en fonctionnement avant la validation finale.
