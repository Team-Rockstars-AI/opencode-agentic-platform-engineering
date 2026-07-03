# Drift Detection & Reconciliation Runbook

This runbook describes how to run the `/drift` workflow against a **live Azure subscription** in scaffolded repositories generated from this project. It assumes the `/drift` command, `drift` skill, and supporting agents are already in place (as provided by this generator).

> Scope: This runbook is **operator-facing**. It does not change IaC or pipelines; it documents how to safely use the existing `/drift` engine.

---

## 1. Prerequisites

For a scaffolded repo (Terraform or Bicep):

- You have authenticated to Azure (`az login`) and selected the correct subscription.
- The repo is configured to talk to the appropriate backend (Terraform state / Bicep deployment scope).
- You have the following tools installed:
  - Terraform (for Terraform-based repos)
  - Azure CLI (`az`)

> **Governance reminder:** All remediation must still pass through the 9-stage lifecycle (research → plan → build → verify → review → security → safety → test → docs) before being merged or applied.

---

## 2. Terraform-based repos

### 2.1 Generate a drift plan

From the scaffolded repo root:

```bash
# Initialise providers/backend (no apply)
terraform init

# Create a binary plan file (no apply)
terraform plan -out=tfplan

# Convert the plan to JSON for the drift engine
mkdir -p artifacts/drift
terraform show -json tfplan > artifacts/drift/tfplan.json
```

### 2.2 Run `/drift`

Invoke the `/drift` workflow (via the OpenCode CLI or orchestrator UI) from the same repo. The orchestrator will:

1. Use `@verifier` + `plan-tracking` to ingest `artifacts/drift/tfplan.json`.
2. Use `@plan-validator` + `drift` to classify each change as **Benign**, **Operational**, or **Critical**:
   - **Delete / Replace** of stateful resources (Key Vaults, storage accounts, databases, VNets, VPN gateways, etc.) are **BLOCKERS**.
3. Use `@security-auditor` to flag security regressions (e.g., newly opened ports, re-enabled public endpoints, disabled diagnostics).
4. Use `@docs-writer` to generate `DRIFT_REPORT.md` from the drift report template.

Always commit `DRIFT_REPORT.md` alongside the change set so reviewers see:

- Which resources are changing (create/update/delete/replace).
- Drift classification (Benign/Operational/Critical).
- Any BLOCKED actions and rationale.

---

## 3. Bicep-based repos

Terraform exposes a rich JSON plan; Bicep relies on `what-if` output, which is less structured. Treat the Bicep path as a best-effort, still guarded by the same safety rules.

### 3.1 Generate a what-if

From the Bicep-based repo root (adjust scope/parameters as needed):

```bash
mkdir -p artifacts/drift

az deployment sub what-if \
  --name drift-check \
  --location <azure-location> \
  --template-file main.bicep \
  --parameters @main.parameters.json \
  --result-format json \
  > artifacts/drift/bicep-whatif.json
```

### 3.2 Run `/drift`

Invoke `/drift` and provide `artifacts/drift/bicep-whatif.json` as the drift artifact. The orchestrator will:

1. Use `@verifier` + `plan-tracking` / `drift` to parse what-it-can from the what-if JSON.
2. Classify obvious creates/updates and highlight any suspected security regressions (NSG rules, public endpoints, disabled diagnostics).
3. Produce `DRIFT_REPORT.md` with explicit notes where manual operator judgement is required.

---

## 4. Remediation via the 9-stage lifecycle

Any change you make in response to drift must **follow the platform lifecycle**:

1. **research** – Understand the drift (what changed, why, and whether it is acceptable).
2. **plan** – Decide whether to:
   - Update IaC to match the live state, or
   - Revert live state to match IaC (using imports or corrective deployments).
3. **build** – Implement changes in IaC modules/templates (no clickops-only fixes).
4. **verify** – Run validation and fresh plans/what-if to confirm the new desired state.
5. **review** – Have `@code-reviewer` confirm maintainability and WAF alignment.
6. **security** – Have `@security-auditor` re-check IAM, network isolation, and logging.
7. **safety** – Have `@plan-validator` re-review JSON plans and block any unsafe changes.
8. **test** – Add/adjust smoke-level tests for the module(s) involved.
9. **docs** – Update `DRIFT_REPORT.md`, `BUILD_JOURNAL.md`, and any relevant ADRs/runbooks.

> **Stateful resources:** For stateful resources (datastores, Key Vaults, VNets, VPN gateways), destructive or replacement actions must remain **blocked** until an explicit, documented exception is approved.

---

## 5. Recording a drift run

When you complete a `/drift` run for an environment (e.g., `dev`):

1. Capture `DRIFT_REPORT.md` in version control.
2. Add a short entry to the target repo’s `BUILD_JOURNAL.md` noting:
   - Date and environment.
   - Whether Critical/Operational drift was found.
   - Whether remediation was applied or deferred.
3. If the run exposed systemic issues (e.g., recurring clickops), consider adding an ADR or updating operational runbooks.

This ensures `/drift` usage is auditable and aligns with the platform’s governance model.
