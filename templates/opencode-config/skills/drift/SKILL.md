---
name: drift
description: Automated Terraform drift detection and reconciliation assistant
license: MIT
compatibility: opencode
---

# Drift Detection & Reconciliation Skill (Terraform Templates)

## Trigger
- Invoke whenever the platform operator runs `/drift` inside a scaffolded repository or requests verification that Azure resources match the Terraform code under `terraform/`.
- Run immediately after change freezes, before promoting infrastructure releases, or any time `terraform plan` returns exit code `2` (drift detected).

## Steps

1. **Prepare the workspace**
   - From the repository root, change into the relevant Terraform environment (for example `cd terraform/envs/dev`).
   - Ensure the remote backend (Azure Storage Account) is reachable and that you authenticated via OIDC or `az login`.
   - Export `TF_CLI_ARGS_plan="-lock=true -lock-timeout=5m"` to enforce state locking.

2. **Produce a refresh-only plan**
   - `terraform init -upgrade`
   - `mkdir -p reports/drift && timestamp=$(date -u +"%Y%m%dT%H%M%SZ")`
   - `terraform plan -refresh-only -input=false -detailed-exitcode -out=reports/drift/${timestamp}.tfplan`
   - Exit code meanings: `0` → no drift, `2` → drift found (continue), other codes → fail fast.

3. **Export the JSON plan**
   - `terraform show -json reports/drift/${timestamp}.tfplan > reports/drift/${timestamp}.tfplan.json`
   - Keep both files so downstream agents (plan-validator, security-auditor, docs-writer) can reuse them without re-running the plan.

4. **Parse & classify drift**
   - Iterate over `.resource_changes[]` in the JSON plan and classify actions per the plan-tracking skill (Create/Update/Delete/Replace).
   - Capture `resource_address`, `actions`, Azure resource ID, and property-level diffs by comparing `change.before` vs `change.after`.
   - Build a structured summary file (e.g., `reports/drift/${timestamp}.matrix.json`) containing severity, impacted tags, and recommended remediation for each resource.

5. **Plan reconciliation**
   - **Create actions:** Either delete rogue resources in Azure or import them: `terraform import <address> <resource-id>`.
   - **Update actions:** Decide between rolling Azure back to match code (rerun `terraform apply`) or adopting an approved manual change by editing Terraform. Document the choice.
   - **Delete actions:** Confirm whether Azure owners intentionally removed the resource. If still required, recreate/import it so Terraform does not destroy stateful infrastructure.
   - **Replace actions on critical services (Key Vault, Storage, SQL, Private Endpoints, Firewall policies):** Escalate to the Orchestrator; never allow unattended recreation.

6. **Security drift detection**
   - Flag as **CRITICAL** whenever the plan shows: NSG rules opening ports `22/3389` to the internet, `public_network_access_enabled = true` on private services, `allow_blob_public_access = true`, `enable_https_traffic_only = false`, `soft_delete_enabled` or `purge_protection_enabled` disabled, or diagnostic settings removed.
   - Document each CRITICAL item with the violated policy and owner.

7. **Coordinate safety gates**
   - Provide the plan JSON and drift matrix to `@plan-validator` so it can enforce the blast-radius policy (no deletes/replaces for stateful assets).
   - Share the same artefacts with `@security-auditor` for security regression checks.

8. **Publish `DRIFT_REPORT.md`**
   - Include: overview (timestamp, subscription, workspace), drifted resources table, CRITICAL security drift callouts, reconciliation commands (`terraform import`, code diffs), and next steps/owners.

## Outputs
- `reports/drift/<timestamp>.tfplan` — Refresh-only plan artefact.
- `reports/drift/<timestamp>.tfplan.json` — JSON representation for parsers/tests.
- `reports/drift/<timestamp>.matrix.json|yaml` — Normalized drift summary.
- `DRIFT_REPORT.md` — Human-readable reconciliation plan shared with operators and auditors.
- Escalation notifications to `@plan-validator` (blast radius) and `@security-auditor` (security drift).
