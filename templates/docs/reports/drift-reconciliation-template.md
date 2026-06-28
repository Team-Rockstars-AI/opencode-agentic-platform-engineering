# Drift Reconciliation Report — {{project_name}}

| Field | Value |
|---|---|
| **Project** | {{project_name}} |
| **Environment** | {{environment}} |
| **Date** | {{date}} |
| **Prepared by** | {{author}} |
| **IaC reference** | {{iac_reference}} |
| **Drift run ID** | {{run_id}} |

---

## Executive Summary

Summarize the overall drift outcome for **{{project_name}}** ({{environment}}). Call out material risks, security regressions, and next steps in 2–3 sentences.

### Drift Snapshot

| Metric | Value |
|---|---|
| Resources evaluated | {{resources_evaluated}} |
| Resources with drift | {{drifted_resource_count}} |
| Security drifts detected | {{security_drift_count}} |
| BLOCKER actions | {{blocker_count}} |
| WARNING actions | {{warning_count}} |
| INFO actions | {{info_count}} |

---

## Validation Inputs

- **Commands executed:** `{{commands_executed}}`
- **Plan artifacts:** `{{plan_artifact_paths}}`
- **Variables / parameter files:** `{{variable_inputs}}`
- **Notes:** {{validation_notes}}

> Plans and what-if outputs are read-only and must be retained for audit at least {{retention_days}} days.

---

## Drifted Resources

| Resource | Type | Scope | Action | Drift Type | Risk | Reconciliation Strategy |
|---|---|---|---|---|---|---|
| {{resource_name}} | {{resource_type}} | {{scope}} | {{action}} | {{drift_type}} | {{risk_level}} | {{reconciliation_strategy}} |
| {{resource_name}} | {{resource_type}} | {{scope}} | {{action}} | {{drift_type}} | {{risk_level}} | {{reconciliation_strategy}} |

### Detailed Findings

#### {{resource_name}}
- **Action:** {{action}}
- **Live state:** {{live_state}}
- **IaC state:** {{iac_state}}
- **Drift classification:** {{drift_classification}}
- **Risk assessment:** {{risk_assessment}}
- **Required remediation:** {{remediation_steps}}
- **Owner / due date:** {{owner_due_date}}

---

## Security Drift Analysis

| Resource | Issue | Severity | Recommended Fix |
|---|---|---|---|
| {{resource_name}} | {{issue}} | {{severity}} | {{fix}} |

- **Security gate result:** {{security_gate_result}}
- **Notes:** {{security_notes}}

---

## Reconciliation Plan

### Terraform Import Commands
```
{{terraform_import_commands}}
```

### Bicep Parameter / Template Corrections
```
{{bicep_patch_instructions}}
```

### Task Tracker

| Priority | Resource | Action | Effort | Owner | Target Date |
|---|---|---|---|---|---|
| {{priority}} | {{resource_name}} | {{action}} | {{effort}} | {{owner}} | {{target_date}} |

---

## Decision & Next Steps

- **Plan safety gate:** {{plan_safety_status}}
- **Blast radius approval:** {{blast_radius_result}}
- **Follow-up commands:** {{follow_up_commands}}
- **Additional notes:** {{additional_notes}}

---

*Template version {{template_version}} · Generated from `templates/docs/reports/drift-reconciliation-template.md`*
