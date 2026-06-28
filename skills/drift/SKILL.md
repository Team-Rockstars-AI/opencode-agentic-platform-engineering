---
name: drift
description: Automated Terraform drift detection and reconciliation assistant
license: MIT
compatibility: opencode
---

# Drift Detection & Reconciliation Skill (Terraform)

## Trigger
- Run this skill whenever the operator invokes the `/drift` command or requests proof that no "clickops" changes exist in a Terraform deployment.
- Execute after any manual change window, before promoting Terraform code to higher environments, or when `terraform plan` exits with code `2` (drift detected).

## Steps

1. **Workspace preparation & state safety**
   - Confirm you are inside the target Terraform root (module or environment) and that the remote Azure Storage Account backend is reachable.
   - Export required Azure auth variables (OIDC or `az login`) and pin Terraform to the version declared in `required_version`.
   - Enable state locking: `export TF_CLI_ARGS_plan="-lock=true -lock-timeout=5m"`.
   - Capture the subscription, resource group, and state container names for later reconciliation notes.

2. **Generate a refresh-only plan artifact**
   - `terraform init -upgrade`
   - `terraform plan -refresh-only -input=false -detailed-exitcode -out=artifacts/drift/tfplan.refresh`
   - Treat exit codes: `0 = no drift`, `2 = drift present`, any other code = fail.
   - Never apply from this plan. Its sole purpose is to snapshot differences between the current Azure state and the committed IaC.

3. **Convert the plan to JSON for parsing**
   - `terraform show -json artifacts/drift/tfplan.refresh > artifacts/drift/tfplan-refresh.json`
   - Store both binary and JSON artefacts under `artifacts/drift/<timestamp>/` so `@plan-validator`, `@security-auditor`, and `@docs-writer` can ingest them.

4. **Parse and classify drift using plan-tracking conventions**
   - Iterate over `.resource_changes[]` within `tfplan-refresh.json`.
   - Map `change.actions` to the plan-tracking color semantics:
     | Terraform actions | Classification |
     | --- | --- |
     | `["create"]` | **Create (green)** — IaC never saw the resource; confirm whether it needs importing or deletion.
     | `["update"]` | **Update (yellow)** — Manual change to an existing resource. List property-level diffs.
     | `["delete"]` | **Delete (red)** — Resource missing from Azure but present in state. Requires investigation before remediation.
     | `["delete","create"]` | **Replace (red+green)** — Terraform would recreate. Block for stateful resources.
   - For each entry, record: address, Azure resource ID, action, tags, and property deltas (`change.before` vs `change.after`).
   - Produce a `drift_matrix.yaml` (or JSON) summarizing every drifted attribute with keys: `resource_address`, `action`, `severity`, `before_value`, `after_value`, `recommended_fix`.
   - Use tools such as `jq` or a short Python script to generate lists of changed attributes:
     ```bash
     jq -r '.resource_changes[] | select(.change.actions|index("update")) | "\(.address): \(.change.before.tags // {}) -> \(.change.after.tags // {})"' artifacts/drift/tfplan-refresh.json
     ```

5. **Derive reconciliation guidance**
   - **Create actions (resource exists outside Terraform):** Inspect Azure to confirm the resource truly exists. If Terraform must adopt it, craft `terraform import <address> <resource-id>` commands (resource IDs can be captured via `terraform state show` or `az resource show`). If the resource is shadow infrastructure that should not exist, document the delete instruction for the owning team instead of importing.
   - **Update actions:** Decide whether to revert Azure to match code (`terraform apply`) or adjust IaC to match an approved manual change. Document the property deltas and the chosen remediation (code change vs. manual rollback).
   - **Delete actions:** Confirm whether the resource was intentionally removed in Azure. If it should still exist, re-create/import it before planning again. Never let Terraform destroy stateful services as part of drift reconciliation.
   - **Replace actions on critical stateful resources (Key Vault, Storage Accounts, Databases, Private Endpoints, Firewall policies):** Stop immediately, escalate to the Orchestrator, and instruct teams to reconcile via code/import rather than recreation.

6. **Flag security drift as CRITICAL**
   - Automatically raise severity to **CRITICAL** when the JSON plan shows any of the following:
     - NSG rules opening ports `22` or `3389` to `*` / `0.0.0.0/0`.
     - `public_network_access_enabled = true` on Key Vault, Storage Account, or Database resources that should be private.
     - `allow_blob_public_access = true`, `enable_https_traffic_only = false`, or `min_tls_version` downgraded below `TLS1_2`.
     - `soft_delete_enabled = false` or `purge_protection_enabled = false` on Key Vault / stateful services.
     - Diagnostic settings removed or log targets changed away from the central Log Analytics workspace.
   - Document why each finding is CRITICAL and reference the violated security baseline.

7. **Coordinate with safety and security gates**
   - Provide the `drift_matrix` and raw `tfplan-refresh.json` to `@plan-validator` so it can enforce the blast-radius gate (no deletes/replaces for stateful components).
   - Share the same artifacts with `@security-auditor` so it can cross-check against the `security-checklist` skill. Highlight any CRITICAL drifts and link to Azure resources for verification.

8. **Compile the drift report**
   - Create `DRIFT_REPORT.md` with the structure:
     1. **Overview:** Timestamp, subscription, workspace, plan exit code.
     2. **Drifted Resources Table:** Columns for resource address, action, severity, key properties changed, recommended reconciliation (import, code change, manual rollback).
     3. **Security Drift:** Dedicated section listing CRITICAL findings with remediation instructions and owners.
     4. **Reconciliation Commands:** Inline code blocks containing `terraform import` or `terraform state` commands and any required code diffs.
     5. **Next Steps:** Assign follow-up tasks (e.g., "Update NSG module to restrict SSH", "Add storage account private endpoint back").

## Outputs
- `artifacts/drift/tfplan.refresh` — Binary Terraform plan generated with `-refresh-only`.
- `artifacts/drift/tfplan-refresh.json` — Machine-readable plan for downstream parsers.
- `artifacts/drift/drift_matrix.yaml` (or `.json`) — Normalized list of drifted resources/actions.
- `DRIFT_REPORT.md` — Human-readable summary with reconciliation guidance and `terraform import` commands.
- Escalation notes for `@plan-validator` (blast radius) and `@security-auditor` (security drift).

## Reference artifacts
- A minimal sample plan demonstrating drift classification lives at `tests/artifacts/drift/sample-tfplan.json`. Use it to unit-test parsers and to guide `@test-writer` when building `.tftest.hcl` validations for `/drift`.
