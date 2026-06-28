# Workflow: Compliance Readiness & Regulatory Mapping

- **Name:** Compliance Readiness Assessment
- **Command:** `/compliance`
- **Trigger:** Explicit user invocation via `/compliance`
- **Primary Agent:** `orchestrator`
- **Supporting Skills:** `compliance` (primary), `security-checklist`, `code-standards`, `doc-standards`

## Overview

The `/compliance` workflow assembles evidence from recent audits, drift runs, and IaC sources to prove adherence to regulatory frameworks (DORA, BIO, GDPR). The `orchestrator` uses the `compliance` skill to coordinate `@security-auditor`, `@code-reviewer`, and `@docs-writer`, ensuring every technical control is backed by concrete Terraform or pipeline references and captured inside an auditor-ready report.

## Steps

1. **Preparation (`orchestrator`)**
   - Load the `compliance` skill and capture scope (environments, frameworks, evidence locations).
   - Collect prior artifacts (`reports/security/security-checklist.md`, `/audit` outputs, `DRIFT_REPORT.md`, recent plan files) for reuse instead of re-running scans.

2. **Security & Control Evidence (`@security-auditor`)**
   - Load `security-checklist`; review IaC and pipeline definitions for OIDC, private connectivity, diagnostic coverage, and secrets exposure.
   - Normalize findings into control status entries (PASS/FAIL/AT RISK) with remediation guidance and regulatory references supplied by the `compliance` skill.

3. **Governance & WAF Validation (`@code-reviewer`)**
   - Load `code-standards` (and `architecture-review` if scope touches networking/service topology).
   - Confirm CAF naming, mandatory tagging, soft-delete, diagnostics, and reliability controls across the affected modules/pipelines.
   - Provide MUST/SHOULD/NOTE findings that feed the control matrix.

4. **Regulatory Mapping (`orchestrator` + `compliance` skill)**
   - Join the evidence from security/code reviews with `docs/compliance-mapping-guide.md` to align each technical control to DORA/BIO/GDPR citations.
   - Produce a structured matrix (JSON/YAML) noting control, evidence path, framework mapping, and status.

5. **Documentation (`@docs-writer`)**
   - Load `doc-standards` (and `plan-tracking` if milestone logs are updated).
   - Generate `COMPLIANCE_READINESS_REPORT.md` from `templates/docs/reports/compliance-readiness-template.md`, embedding:
     - Executive summary and readiness metrics.
     - Regulatory control matrix with evidence references.
     - Non-compliance findings plus remediation owners/dates.
     - Appendices referencing `DRIFT_REPORT.md`, security checklist, and `/audit` artifacts.

6. **Handoff**
   - Return the report, matrix, and remediation backlog to the `orchestrator` for scheduling follow-up work (/expand, /optimise, etc.).

## Agent output contracts

| Stage | Agent | Expected output |
|-------|-------|----------------|
| Security evidence | `@security-auditor` | `Security gate: PASSED\|FAILED` with control status table |
| Governance review | `@code-reviewer` | `Quality gate: PASSED\|FAILED` referencing CAF/WAF findings |
| Documentation | `@docs-writer` | `## Documentation summary` referencing `COMPLIANCE_READINESS_REPORT.md` |

## Artifacts produced

- `reports/compliance/<timestamp>-matrix.json` (or `.yaml`) — regulatory control matrix.
- `COMPLIANCE_READINESS_REPORT.md` — generated from `templates/docs/reports/compliance-readiness-template.md`.
- Optional updates to `BUILD_JOURNAL.md` / `DISCOVERIES_LOG.md` capturing compliance status snapshots.
