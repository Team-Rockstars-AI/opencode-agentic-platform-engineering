# Workflow: Security & Compliance Audit

- **Name:** Security & Compliance Audit
- **Command:** `/audit`
- **Trigger:** Explicit user invocation via `/audit`
- **Primary Agent:** `security-auditor`
- **Supporting Skills:** `audit` (primary), `security-checklist`, `doc-standards`

## Overview

The `/audit` workflow performs a comprehensive scan of the workspace to identify security vulnerabilities, credential leaks, and compliance deviations. The `security-auditor` agent coordinates the process, leveraging the `audit` skill to perform technical scans and the `security-checklist` skill to evaluate findings against the platform's secure-by-design baseline.

## Steps

1. **Preparation (`security-auditor`)**
   - Load the `audit` skill and define the scan scope (IaC modules, pipeline definitions, configuration files).
   - Initialize the `security-checklist` to track PASS/FAIL findings.

2. **Static Analysis & Secret Scanning (`security-auditor`)**
   - Execute secret scanning (e.g., Gitleaks) to detect hardcoded credentials or tokens.
   - Run IaC static analysis (e.g., Checkov, tfsec) to identify misconfigurations like public endpoints or missing encryption.

3. **Network & Identity Audit (`security-auditor`)**
   - Trace Network Security Group (NSG) rules to ensure no management ports (22, 3389) are open to the internet.
   - Verify that all stateful resources (Key Vaults, Storage, Databases) have public access disabled and use Private Endpoints.
   - Confirm that pipelines are configured for OIDC-federated authentication.

4. **Finding Consolidation (`security-auditor`)**
   - Map technical findings to the `security-checklist` criteria.
   - Classify findings by severity (CRITICAL, HIGH, MEDIUM, LOW).
   - Generate remediation blocks (code snippets or CLI commands) for each failure.

5. **Documentation (`@docs-writer`)**
   - Load `doc-standards`.
   - Format the audit findings into a structured markdown report.
   - Update `BUILD_JOURNAL.md` or `DISCOVERIES_LOG.md` if required by the orchestration context.

6. **Handoff**
   - Provide the audit report and remediation backlog to the `orchestrator` for scheduling fixes or triggering the `/debug` workflow.

## Agent output contracts

| Stage | Agent | Expected output |
|-------|-------|----------------|
| Security Audit | `@security-auditor` | `Security gate: PASSED\|FAILED` with structured findings |
| Documentation | `@docs-writer` | `## Documentation summary` referencing audit artifacts |

## Artifacts produced

- `reports/security/audit-<timestamp>.md` — Detailed audit report with remediation blocks.
- Updated `security-checklist.md` (if maintained as a persistent artifact).
