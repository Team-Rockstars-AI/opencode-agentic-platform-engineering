# Compliance Readiness Report — {{project_name}}

| Field | Value |
|---|---|
| **Project** | {{project_name}} |
| **Environment** | {{environment}} |
| **Date** | {{date}} |
| **Prepared by** | {{author}} |
| **Frameworks in scope** | {{frameworks}} |
| **Artifacts referenced** | {{artifact_refs}} |

---

## Executive Summary

Summarize the overall compliance posture for **{{project_name}}** ({{environment}}). Include readiness percentage, key risks, and any gating blockers in 2–3 sentences.

### Readiness Snapshot

| Metric | Value |
|---|---|
| Controls evaluated | {{controls_total}} |
| Controls PASS | {{controls_pass}} |
| Controls FAIL | {{controls_fail}} |
| Controls AT RISK | {{controls_at_risk}} |
| Overall readiness (%) | {{readiness_percent}} |

---

## Evidence Inputs

- **Security checklist:** {{security_checklist_path}}
- **Audit artifacts:** {{audit_artifacts}}
- **Drift report:** {{drift_report_path}}
- **Pipeline evidence (OIDC, permissions):** {{pipeline_evidence}}
- **Additional notes:** {{evidence_notes}}

> Retain all referenced artifacts for at least {{retention_days}} days to satisfy audit traceability requirements.

---

## Regulatory Control Matrix

| Control | Technical Evidence | Status | DORA Ref | BIO Ref | GDPR Ref | Notes |
|---|---|---|---|---|---|---|
| {{control_name}} | {{evidence_path}} | {{status}} | {{dora_ref}} | {{bio_ref}} | {{gdpr_ref}} | {{notes}} |
| {{control_name}} | {{evidence_path}} | {{status}} | {{dora_ref}} | {{bio_ref}} | {{gdpr_ref}} | {{notes}} |

### Status Legend

- **PASS** — Control implemented and validated via IaC/pipeline evidence.
- **AT RISK** — Control defined in IaC but drift or manual change prevents enforcement.
- **FAIL** — Control missing or non-compliant; remediation required before go-live.

---

## Non-Compliance Findings

List each FAILED or AT RISK control with actionable remediation guidance.

#### {{finding_title}}
- **Control:** {{control_name}}
- **Severity:** {{severity}}
- **Evidence:** {{evidence_path}}
- **Issue:** {{issue_description}}
- **Regulatory impact:** DORA {{dora_ref}} / BIO {{bio_ref}} / GDPR {{gdpr_ref}}
- **Remediation:** {{remediation_steps}}
- **Owner / target date:** {{owner_target_date}}

---

## Remediation Plan

| Priority | Control | Action | Owner | Effort | Due Date | Status |
|---|---|---|---|---|---|---|
| {{priority}} | {{control_name}} | {{action}} | {{owner}} | {{effort}} | {{due_date}} | {{status}} |

### Effort Scale

| Effort | Description |
|---|---|
| **Low** | Documentation or configuration update; no resource recreation. |
| **Medium** | Requires resource re-deployment or multiple file changes. |
| **High** | Multi-team coordination or change window required. |

---

## Attachments & References

- `DRIFT_REPORT.md`: {{drift_report_path}}
- Security checklist: {{security_checklist_path}}
- Audit evidence: {{audit_artifacts}}
- Compliance mapping guide: `docs/compliance-mapping-guide.md`
- Additional attachments: {{additional_attachments}}

---

## Decision & Sign-off

| Role | Name | Decision | Date |
|---|---|---|---|
| Security Lead | {{security_lead}} | {{security_decision}} | {{security_decision_date}} |
| Compliance Owner | {{compliance_owner}} | {{compliance_decision}} | {{compliance_decision_date}} |
| Platform Engineering | {{platform_owner}} | {{platform_decision}} | {{platform_decision_date}} |

- **Compliance gate result:** {{gate_result}}
- **Next actions:** {{next_actions}}

---

*Template version {{template_version}} · Generated from `templates/docs/reports/compliance-readiness-template.md`*
