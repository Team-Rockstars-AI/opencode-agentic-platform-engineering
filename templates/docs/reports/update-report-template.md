# Template Update Report — {{project_name}}

| Field | Value |
|---|---|
| **Project** | {{project_name}} |
| **Date** | {{date}} |
| **Prepared by** | {{author}} |
| **Template version** | `{{old_template_commit}}` → `{{new_template_commit}}` |
| **Mode** | {{mode}} |

---

## Executive Summary

This report documents a template synchronisation run performed with `scripts/update.py`, pulling upstream platform-template improvements into **{{project_name}}**. Every file was classified by comparing its original scaffolded state, its current state in this workspace, and its state in the new template version.

| Classification | Files |
|---|---|
| Conflicts (manual merge required) | {{conflict_count}} |
| Auto-updated | {{auto_update_count}} |
| New files | {{new_file_count}} |
| Removed upstream | {{removed_upstream_count}} |
| Kept local modifications | {{user_modified_count}} |
| Skipped (deleted locally) | {{user_deleted_count}} |
| Unchanged | {{unchanged_count}} |

---

## Conflicts (manual merge required)

Both this workspace and the upstream template changed these files. `update.py` left them untouched; each needs a manual (or agent-assisted) three-way merge.

| File | Local change summary | Upstream change summary | Resolution |
|---|---|---|---|
| {{file_path}} | {{local_change}} | {{upstream_change}} | {{resolution}} |

> **Safety rule:** never auto-merge conflicts in `*.tfvars`, `backend.tf`, or pipeline credential/OIDC configuration — surface those to the human operator.

---

## Auto-updated files

Never modified locally; replaced with the new template version.

- {{file_path}}

## New files added by the template

- {{file_path}}

## Removed upstream

Deleted locally because the template no longer ships them (they were never modified here).

- {{file_path}}

---

## Verification

| Check | Result |
|---|---|
| `terraform validate` / `bicep build` | {{iac_validation_result}} |
| `python3 scripts/validate-skills.py` | {{skill_validation_result}} |
| Security review of merged files | {{security_review_result}} |

## Follow-up actions

- {{follow_up_action}}
