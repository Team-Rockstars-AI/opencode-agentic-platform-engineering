# Regulatory Compliance Mapping Guide

This document maps the technical configurations and security guardrails of this platform directly to European and Dutch regulatory controls, including **DORA (Digital Operational Resilience Act), GDPR (General Data Protection Regulation), Dutch BIO (Baseline Informatiebeveiliging Overheid), and NEN 7510 (Healthcare Information Security)**.

---

## 1. Regulatory Compliance Matrix

The following matrix maps specific technical controls implemented in this platform to official regulatory articles and controls:

| Technical Control | Implemented Resource / Configuration | DORA Article | GDPR Article | Dutch BIO Control | NEN 7510 Control |
|---|---|---|---|---|---|
| **Zero-Secrets Authentication** | OIDC Federated Credentials (no client secrets) | Art. 9 (ICT Security) | Art. 32 (Security of Processing) | Control 9.2 (User Registration) | Control 9.2 (User Access) |
| **Data Loss Prevention** | Key Vault Purge Protection & 90-Day Soft-Delete | Art. 12 (Backup & Recovery) | Art. 32 (Availability & Resilience) | Control 12.3 (Backup) | Control 12.3 (Backup) |
| **Network Isolation** | Private Endpoints & Disabled Public Access | Art. 9 (Network Security) | Art. 32 (Confidentiality) | Control 13.1 (Network Controls) | Control 13.1 (Network Security) |
| **Micro-segmentation** | Subnet-level NSGs with Default-Deny Posture | Art. 9 (Network Segmentation) | Art. 32 (Confidentiality) | Control 13.1 (Network Segregation) | Control 13.1 (Network Segregation) |
| **Inbound Protection** | Application Gateway + WAF v2 (Prevention Mode) | Art. 9 (Vulnerability Management) | Art. 32 (Security of Processing) | Control 12.6 (Technical Vulnerabilities) | Control 12.6 (Vulnerability Management) |
| **Audit Trails** | Centralized Diagnostic Logging to Log Analytics | Art. 10 (Monitoring & Logging) | Art. 30 (Records of Processing) | Control 12.4 (Logging & Monitoring) | Control 12.4 (Logging & Monitoring) |
| **Environment Isolation** | Separate Subscriptions for Dev/Test/Prod | Art. 9 (System Isolation) | Art. 32 (Security of Processing) | Control 12.1 (Operational Procedures) | Control 12.1 (Operational Procedures) |
| **Local Compliance Gating** | Pre-commit Hooks (Gitleaks, Checkov SAST) | Art. 9 (Secure Development) | Art. 25 (Data Protection by Design) | Control 14.2 (Security in Development) | Control 14.2 (Secure Development) |

---

## 2. Detailed Control Mappings

### 1. Zero-Secrets Authentication (OIDC Federation)
*   **Technical Implementation:** Replaced long-lived client secrets and connection strings in deployment pipelines with OpenID Connect (OIDC) Federated Credentials. Pipelines exchange short-lived JWT tokens with Entra ID to authenticate.
*   **DORA Art. 9 Alignment:** Enforces strict identity and access management (IAM) policies, preventing credential theft and unauthorized infrastructure modifications.
*   **GDPR Art. 32 Alignment:** Minimizes the risk of credential exposure in source code, protecting personal data processing environments from unauthorized access.
*   **Dutch BIO Control 9.2 Alignment:** Enforces secure, auditable, and automated identity registration and authentication for deployment workflows.

### 2. Data Loss Prevention (Key Vault Hardening)
*   **Technical Implementation:** Enabled `purge_protection_enabled = true` (Terraform) / `enablePurgeProtection: true` (Bicep) and configured a strict **90-day soft-delete retention window** on all Azure Key Vaults.
*   **DORA Art. 12 Alignment:** Guarantees the ability to recover critical cryptographic keys, secrets, and certificates in the event of accidental deletion or a malicious ransomware attack.
*   **GDPR Art. 32 Alignment:** Ensures the continuous availability and resilience of processing systems and services by preventing permanent data loss.
*   **NEN 7510 Control 12.3 Alignment:** Meets healthcare-grade data backup and recovery requirements for critical security assets.

### 3. Network Isolation & Micro-segmentation
*   **Technical Implementation:** Stateful resources are isolated behind Private Endpoints with public network access disabled. Subnets are micro-segmented using dedicated Network Security Groups (NSGs) with default-deny rules.
*   **DORA Art. 9 Alignment:** Enforces network boundary protection and segmentation, restricting lateral movement and isolating critical data assets from untrusted zones.
*   **Dutch BIO Control 13.1 Alignment:** Restricts network communication to explicitly authorized paths, ensuring secure data transmission across boundaries.
*   **NEN 7510 Control 13.1 Alignment:** Protects sensitive patient data processing environments from unauthorized network-level access.

### 4. Audit Trails & Continuous Monitoring
*   **Technical Implementation:** Wired up all network security groups, Key Vaults, and Application Gateways to stream diagnostic logs (including NSG flow logs and Key Vault access audits) to a centralized Log Analytics Workspace.
*   **DORA Art. 10 Alignment:** Establishes continuous monitoring and logging of ICT systems to detect, identify, and report security incidents in real time.
*   **Dutch BIO Control 12.4 Alignment:** Enforces comprehensive logging of security events, system access, and administrative actions to support forensic investigations.

---

## 3. Auditor Presentation Guide

When presenting this platform engineering repository to external compliance auditors, highlight the following automated governance features:

1.  **Compliance-as-Code:** Point to `skills/security-checklist/SKILL.md` to show that your security baseline is codified and automatically enforced during every audit pass.
2.  **Local Gating:** Show the `.pre-commit-config.yaml` file to demonstrate that Gitleaks (secret scanning) and Checkov (SAST compliance) are enforced locally on every developer's machine before code can be committed.
3.  **Blast Radius Safety:** Explain the role of the `@plan-validator` agent, which automatically parses dry-run execution plans and blocks any deployment that schedules critical stateful resources (databases, vaults) for destruction or replacement.
4.  **Zero-Secrets Trail:** Demonstrate that your deployment pipelines contain zero long-lived credentials, relying entirely on short-lived, auditable OIDC federated tokens.

---

## 4. Automated Compliance Workflow

This platform includes an automated **[/compliance workflow](../workflows/compliance.md)** that can be triggered at any time to generate a real-time mapping of your technical state to these regulatory controls.

Run the following command in the OpenCode console:
```bash
/compliance
```

The agent team will scan your IaC, pipelines, and drift reports, and produce a **Compliance Readiness Report** based on the mappings defined in this guide.

