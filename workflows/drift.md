# Workflow: Drift Detection & Reconciliation

- **Name:** Automated Drift Detection & Reconciliation
- **Command:** `/drift`
- **Trigger:** Explicit user invocation via `/drift`
- **Primary Agent:** `orchestrator`
- **Supporting Skills:** `drift` (primary), `plan-tracking`, `security-checklist`, `doc-standards`

## Overview

The `/drift` workflow executes a non-destructive Terraform plan and/or Bicep what-if against the live Azure environment, classifies any manual configuration changes, and produces an actionable reconciliation report. The `orchestrator` coordinates `@verifier`, `@plan-validator`, `@security-auditor`, and `@docs-writer` to ensure drift is surfaced, risk-ranked, and accompanied by precise import/update guidance.

## Steps

1. **Preparation (`orchestrator`)**
   - Load the `drift` skill and capture scope details (framework, deployment target, variables, credentials context).
   - Identify which IaC stacks need drift analysis and what plan artifacts must be generated.

2. **Validation & Plan Capture (`@verifier`)**
   - Run the required validation commands (e.g., `terraform fmt`, `terraform validate`, `bicep build`).
   - Execute read-only drift discovery commands: `terraform plan -out=tfplan` + `terraform show -json tfplan`, or `az deployment sub what-if --result-format json`.
   - Store the JSON outputs in the workspace and summarize the artifact paths for downstream agents.

3. **Blast-Radius & Drift Classification (`@plan-validator`)**
   - Load the `plan-tracking` skill and parse the plan/what-if JSON.
   - Flag destructive actions immediately (BLOCKER) and classify all other drift as WARNING or INFO with remediation context (update IaC vs import).
   - Produce a concise table of drifted resources, actions, and reconciliation paths for the report.

4. **Security Drift Review (`@security-auditor`)**
   - Load the `security-checklist` skill and review the same plan data plus relevant IaC files.
   - Highlight regressions such as newly opened ports, disabled diagnostics, or broadened IAM assignments as CRITICAL/HIGH findings.

5. **Documentation & Report (`@docs-writer`)**
   - Load `doc-standards` (and `plan-tracking` if milestone logs need updates).
   - Generate `DRIFT_REPORT.md` using `templates/docs/reports/drift-reconciliation-template.md`, incorporating:
     - Drift metrics and tables from `@plan-validator`.
     - Security findings from `@security-auditor`.
     - Recommended reconciliation commands (imports, parameter changes) and task owners.

6. **Handoff**
   - Provide the report and plan artifacts back to the `orchestrator` for scheduling remediation work or dispatching follow-up commands (/expand, manual hotfix, etc.).

## Agent output contracts

| Stage | Agent | Expected output |
|-------|-------|----------------|
| Validation & plan capture | `@verifier` | `Verification: PASSED\|FAILED` plus artifact paths |
| Plan safety & drift classification | `@plan-validator` | `Plan safety gate: PASSED\|FAILED` with drift table |
| Security drift review | `@security-auditor` | `Security gate: PASSED\|FAILED` with remediation blocks |
| Documentation | `@docs-writer` | `## Documentation summary` referencing `DRIFT_REPORT.md` |

## Artifacts produced

- `tfplan`, `terraform-show.json`, or `what-if.json` — stored plan outputs for auditing.
- `DRIFT_REPORT.md` — generated from `templates/docs/reports/drift-reconciliation-template.md`.
- Optional milestone updates in `BUILD_JOURNAL.md` / `DISCOVERIES_LOG.md` depending on orchestration needs.
