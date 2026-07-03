# Drift Detection & Reconciliation Runbook

This runbook is copied into scaffolded repositories to document how to run the `/drift` workflow against a **live Azure subscription**.

---

## 1. Prerequisites

- Azure CLI (`az`) installed and logged in (`az login`).
- Correct subscription selected (`az account set --subscription <id>`).
- Terraform (for Terraform-based templates) or the Bicep CLI/`az` what-if workflow (for Bicep templates).
- Backend configured so plans/what-if operate against the correct environment.

> All drift remediation must follow the mandatory 9-stage lifecycle (research → plan → build → verify → review → security → safety → test → docs).

---

## 2. Terraform-based repos

```bash
terraform init
terraform plan -out=tfplan
mkdir -p artifacts/drift
terraform show -json tfplan > artifacts/drift/tfplan.json
```

Then invoke `/drift` (via the OpenCode CLI or orchestrator) so the agents can:

- Parse `artifacts/drift/tfplan.json` (`@verifier` + `plan-tracking`).
- Classify drift and enforce blast-radius safety (`@plan-validator` + `drift`).
- Flag security regressions (`@security-auditor`).
- Generate `DRIFT_REPORT.md` (`@docs-writer`).

Commit `DRIFT_REPORT.md` with your change set.

---

## 3. Bicep-based repos

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

Then invoke `/drift` and provide `artifacts/drift/bicep-whatif.json` so the agents can classify drift and produce `DRIFT_REPORT.md`.

---

## 4. Remediation & journaling

- Implement fixes in IaC (no clickops-only fixes) and route them through the 9-stage lifecycle.
- Keep `DRIFT_REPORT.md` updated.
- Add a short entry to `BUILD_JOURNAL.md` summarising each drift run (environment, date, high-level outcome).
