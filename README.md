# 🛡️ DevSecOps Lab

## Sécurisation d'un pipeline CI/CD avec une approche DevSecOps

[![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D24939?logo=jenkins&logoColor=white)](https://www.jenkins.io/)
[![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![SonarQube](https://img.shields.io/badge/SonarQube-SAST-4E9BCD?logo=sonarqube&logoColor=white)](https://www.sonarsource.com/products/sonarqube/)
[![Semgrep](https://img.shields.io/badge/Semgrep-SAST-FF6F00?logo=semgrep&logoColor=white)](https://semgrep.dev/)
[![Trivy](https://img.shields.io/badge/Trivy-Container%20Scanning-1904DA?logo=aqua&logoColor=white)](https://trivy.dev/)
[![OWASP ZAP](https://img.shields.io/badge/OWASP%20ZAP-DAST-00549E?logo=owasp&logoColor=white)](https://www.zaproxy.org/)
[![Gitleaks](https://img.shields.io/badge/Gitleaks-Secret%20Scanning-000000?logo=git&logoColor=white)](https://gitleaks.io/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github&logoColor=white)](https://github.com/)


## 📌 1. Présentation du projet

Ce projet consiste à intégrer la sécurité directement dans un pipeline CI/CD selon une approche **DevSecOps** et **Shift Left**.

L'objectif est d'automatiser plusieurs contrôles de sécurité tout au long du cycle de développement afin de détecter les vulnérabilités le plus tôt possible et de bloquer automatiquement une livraison lorsqu'un contrôle de sécurité bloquant échoue.

Le pipeline combine :

- analyse statique du code (**SAST**) ;
- analyse des dépendances (**SCA**) ;
- détection des secrets ;
- analyse de sécurité de l'image Docker ;
- analyse dynamique de l'application (**DAST**) ;
- Quality Gates ;
- reporting centralisé ;
- notifications.

---

# 🏗️ 2. Architecture globale

```text
                         ┌─────────────────────┐
                         │     DEVELOPER       │
                         │  Code / Commit      │
                         └──────────┬──────────┘
                                    │
                          Pre-commit Security
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       GitHub        │
                         │   Source Repository │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ╔══════════════════════════════╗
                    ║          JENKINS             ║
                    ║        CI/CD PIPELINE        ║
                    ╚════════════════╤═════════════╝
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
    ┌────────────┐             ┌────────────┐             ┌────────────┐
    │    SAST    │             │    SCA     │             │  SECRETS   │
    │            │             │            │             │            │
    │ SonarQube  │             │ Dependency │             │  Gitleaks  │
    │ Semgrep    │             │   Check    │             │            │
    │ Bandit     │             │ pip-audit  │             │            │
    └──────┬─────┘             └──────┬─────┘             └──────┬─────┘
           │                          │                          │
           └──────────────────────────┼──────────────────────────┘
                                      │
                                      ▼
                             ┌─────────────────┐
                             │ Build & Tests   │
                             └────────┬────────┘
                                      │
                                      ▼
                             ┌─────────────────┐
                             │   Docker Image   │
                             │ devsecops-demo-  │
                             │      app         │
                             └────────┬────────┘
                                      │
                                      ▼
                               ┌─────────────┐
                               │    TRIVY    │
                               │ Image Scan  │
                               └──────┬──────┘
                                      │
                                      ▼
                             ┌─────────────────┐
                             │ Running Docker  │
                             │   Application   │
                             └────────┬────────┘
                                      │
                                      ▼
                               ┌─────────────┐
                               │  OWASP ZAP  │
                               │    DAST     │
                               └──────┬──────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │     QUALITY GATE        │
                          │                        │
                          │ Blocking failures > 0  │
                          │          ↓             │
                          │       ❌ BLOCK          │
                          │                        │
                          │ No blocking failure    │
                          │          ↓             │
                          │       ✅ PASS           │
                          └───────────┬────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │ CENTRALIZED REPORTING  │
                          │                        │
                          │ reports/raw/            │
                          │ reports/security/       │
                          │ reports/status/         │
                          │                        │
                          │ pipeline-summary.json   │
                          └───────────┬────────────┘
                                      │
                                      ▼
                               ┌─────────────┐
                               │    Slack    │
                               │ Notification│
                               └─────────────┘
```

---

# 🔄 3. Flux du pipeline

Le pipeline Jenkins suit les principales étapes suivantes :

```text
Checkout
   ↓
Environment Validation
   ↓
Build & Tests
   ↓
SAST
   ↓
SCA
   ↓
Secret Scanning
   ↓
Docker Image Build
   ↓
Container Scanning
   ↓
Application Start
   ↓
DAST
   ↓
Centralized Reporting
   ↓
Quality Gate
   ↓
PASS / BLOCK
   ↓
Notification
```

---

# 🛡️ 4. Contrôles de sécurité

## 4.1 SAST — Static Application Security Testing

Le SAST permet d'analyser le code source sans exécuter l'application.

### SonarQube

Analyse du code source et de sa qualité afin d'identifier notamment les problèmes de sécurité, les vulnérabilités et les mauvaises pratiques.

### Semgrep

Analyse statique basée sur des règles permettant d'identifier des patterns de code potentiellement dangereux.

### Bandit

Analyse spécifique du code Python afin d'identifier des problèmes de sécurité courants.

---

## 4.2 SCA — Software Composition Analysis

L'analyse SCA permet d'identifier les vulnérabilités présentes dans les dépendances utilisées par l'application.

### OWASP Dependency-Check

Analyse des dépendances et recherche de vulnérabilités connues.

### pip-audit

Audit des dépendances Python afin d'identifier les packages présentant des vulnérabilités connues.

---

## 4.3 Secret Scanning

### Gitleaks

Recherche de secrets potentiellement exposés dans le dépôt :

- API keys ;
- tokens ;
- credentials ;
- mots de passe ;
- autres informations sensibles.

Des contrôles **pre-commit** sont également utilisés afin de détecter certains problèmes avant leur arrivée dans le pipeline.

---

## 4.4 Container Security

### Trivy

Après la construction de l'image Docker, Trivy analyse l'image afin d'identifier les vulnérabilités présentes dans :

- les packages système ;
- les dépendances ;
- les composants de l'image ;
- les configurations concernées.

---

## 4.5 DAST — Dynamic Application Security Testing

### OWASP ZAP

Après le démarrage de l'application dans un conteneur Docker, OWASP ZAP réalise une analyse dynamique de l'application en fonctionnement.

La cible utilisée par le pipeline est :

```text
http://devsecops-demo-app:8000
```

Les résultats ZAP sont ensuite récupérés dans les répertoires de reporting du projet.

---

# 🚦 5. Quality Gate

La Quality Gate constitue le mécanisme de décision du pipeline.

Les différents contrôles produisent des résultats qui sont ensuite centralisés.

Le pipeline calcule notamment :

```text
total
pass
fail
pending
blocking_failures
control_score
evaluation_coverage
```

Le principe de décision est :

```text
                Security Controls
                       │
                       ▼
                Result Evaluation
                       │
                       ▼
              blocking_failures
                 /           \
                /             \
              > 0              = 0
               │                │
               ▼                ▼
          ❌ PIPELINE       ✅ PIPELINE
             BLOCK              PASS
```

Un contrôle identifié comme **bloquant** et en échec empêche la validation finale du pipeline.

---

# 📊 6. Centralisation des rapports

Les résultats sont organisés afin de séparer les données brutes, les résultats de sécurité et les statuts.

```text
reports/
│
├── raw/
│   ├── sonarqube/
│   ├── zap/
│   └── ...
│
├── security/
│   ├── pipeline-summary.json
│   └── ...
│
└── status/
    └── ...
```

Le fichier principal de synthèse est :

```text
reports/security/pipeline-summary.json
```

Il permet de disposer d'une vue globale de l'état des contrôles de sécurité exécutés pendant le pipeline.

---

# 🔔 7. Notifications

Les résultats du pipeline peuvent être communiqués via **Slack** afin de fournir une visibilité rapide sur :

- le résultat du build ;
- l'état des contrôles de sécurité ;
- les échecs bloquants ;
- le statut final du pipeline.

---

# 🧰 8. Stack technique

| Domaine | Technologie | Fonction |
|---|---|---|
| Source Control | GitHub | Gestion du code source |
| CI/CD | Jenkins | Orchestration du pipeline |
| Containerisation | Docker | Build et exécution de l'application |
| SAST | SonarQube | Analyse statique |
| SAST | Semgrep | Analyse de patterns de sécurité |
| SAST | Bandit | Analyse de sécurité Python |
| SCA | OWASP Dependency-Check | Analyse des dépendances |
| SCA | pip-audit | Audit des packages Python |
| Secrets | Gitleaks | Détection des secrets |
| Container Security | Trivy | Scan de l'image Docker |
| DAST | OWASP ZAP | Analyse dynamique |
| Pre-commit | Security Git Hooks | Contrôles locaux |
| Notification | Slack | Alertes du pipeline |

---

# 📁 9. Organisation du projet

```text
devsecops-lab/
│
├── app/
│   └── ...
│
├── tests/
│   ├── eslint-test/
│   ├── gitleaks-test/
│   ├── semgrep-test/
│   ├── zap-test/
│   └── sca-test-java/
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

# 🔐 10. Approche Shift Left

La sécurité est intégrée progressivement dans le cycle de développement :

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
    ├── Secret Scan
    ├── Container Scan
    └── DAST
             │
             ▼
       Quality Gate
             │
       ┌─────┴─────┐
       ▼           ▼
     PASS         BLOCK
```

L'objectif est de détecter les problèmes de sécurité **le plus tôt possible**, avant qu'une version non conforme ne soit considérée comme valide.

---

# 🎯 11. Objectifs atteints

Le projet met en œuvre les principaux principes d'une démarche DevSecOps :

- ✅ Intégration de la sécurité dans le pipeline CI/CD
- ✅ Approche Shift Left
- ✅ SAST automatisé
- ✅ SCA automatisé
- ✅ Secret Scanning
- ✅ Container Scanning
- ✅ DAST automatisé
- ✅ Quality Gate
- ✅ Blocage des contrôles critiques
- ✅ Centralisation des rapports
- ✅ Notifications
- ✅ Traçabilité des résultats

---

# 🚀 12. Exécution

Le pipeline est exécuté avec Jenkins.

Les différents contrôles sont automatisés et leurs résultats sont regroupés dans les répertoires de reporting du projet.

La validation finale dépend de la Quality Gate :

```text
Security Analysis
       │
       ▼
   Evaluation
       │
       ▼
 Quality Gate
   │       │
 PASS     BLOCK
```

---

## 📌 Résumé de l'architecture

```text
GitHub
   │
   ▼
Jenkins
   │
   ├── SonarQube ──┐
   ├── Semgrep ────┤
   ├── Bandit ─────┤
   ├── Dependency ─┤
   ├── pip-audit ──┤
   └── Gitleaks ───┤
                   │
                   ▼
             Security Results
                   │
                   ▼
              Docker Build
                   │
                   ▼
                 Trivy
                   │
                   ▼
             Running App
                   │
                   ▼
               OWASP ZAP
                   │
                   ▼
             Quality Gate
              /         \
           PASS          BLOCK
             │
             ▼
       Reports + Slack


**DevSecOps Lab — Security integrated into CI/CD from code to deployment.**