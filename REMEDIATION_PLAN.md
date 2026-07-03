# Remediation Plan — Governance Audit Findings

**Status:** ✅ COMPLETED (2026-07-03 — all 5 findings fixed in both stacks; see BUILD_JOURNAL.md)
**Source:** Manual audit of `modules/`, `templates/terraform/`, `templates/bicep/` against this repo's own governance docs, performed 2026-07-02.
**Audience:** This document is self-contained. It is written for an agent with no memory of the audit conversation — it does not assume you have read anything except this file and the repo itself.

---

## 0. Context you need before starting

This repo (`opencode-agentic-platform-engineering`) scaffolds platform-engineering repositories. It ships **reusable, versioned IaC modules** under `modules/terraform/<name>/v1/` and `modules/bicep/<name>/v1/`, and **composed templates** under `templates/terraform/` and `templates/bicep/` that wire those modules together into a full scaffold output. Both stacks (Terraform and Bicep) are meant to be kept at feature parity — they implement the same platform twice, once per IaC framework.

Governance for this repo is codified in:
- [`AGENTS.md`](AGENTS.md) — see "Secure Governance & Security Guardrails" (§119-129) and "Enforced structure" (§14-38, module/template conventions).
- [`skills/security-checklist/SKILL.md`](skills/security-checklist/SKILL.md) — hard-block security checklist (item E: "Central Log Analytics diagnostic stream deployed for all infrastructure components").
- [`skills/code-standards/SKILL.md`](skills/code-standards/SKILL.md) — WAF 5-pillar rules, CAF naming/tagging.
- [`docs/compliance-mapping-guide.md`](docs/compliance-mapping-guide.md) — claims Key Vault audit logs are wired to Log Analytics as an implemented control (§4 "Audit Trails & Continuous Monitoring").
- [`docs/cost-governance-guide.md`](docs/cost-governance-guide.md) — "The 8 Rules" (§1) and the per-environment "Right-Sizing Guidelines" table (§3).

A prior audit pass found 5 concrete discrepancies between these docs and the actual IaC. This plan fixes all 5. **Do not fix anything not listed here** — this is a scoped remediation, not a general cleanup pass.

Read the governance docs above in full before making changes — this plan quotes the relevant lines but the docs have more context (e.g. exact severity conventions, full rule lists) that should inform judgment calls not explicitly covered below.

---

## 1. Key Vault module has no diagnostic logging

**Rule violated:** AGENTS.md §125 "Audit Trails: Central Log Analytics diagnostic stream must be deployed for all infrastructure components." Also `skills/security-checklist/SKILL.md` item E, and `docs/compliance-mapping-guide.md` §4 which explicitly claims Key Vault audit logs stream to Log Analytics as an implemented control.

**Current state:**
- [`modules/terraform/azure-keyvault/v1/main.tf`](modules/terraform/azure-keyvault/v1/main.tf) defines only `azurerm_key_vault.kv` — no `azurerm_monitor_diagnostic_setting`.
- [`modules/bicep/azure-keyvault/v1/main.bicep`](modules/bicep/azure-keyvault/v1/main.bicep) defines only the `kv` resource — no `Microsoft.Insights/diagnosticSettings`.
- Compare with [`modules/terraform/azure-network-baseline/v1/main.tf`](modules/terraform/azure-network-baseline/v1/main.tf) and [`modules/terraform/azure-private-runner/v1/main.tf`](modules/terraform/azure-private-runner/v1/main.tf), which both accept a `log_analytics_workspace_id` variable (default `null`) and emit a conditional `azurerm_monitor_diagnostic_setting` (`count = var.log_analytics_workspace_id != null ? 1 : 0`). The Bicep equivalents use `param logAnalyticsWorkspaceId string = ''` and `resource ... = if (!empty(logAnalyticsWorkspaceId))`. The Key Vault module is the only one of the four modules that doesn't follow this pattern, so it is not self-contained/independently correct per AGENTS.md's module conventions ("Modules are tested independently").
- Note: the composition layer (`templates/terraform/main.tf` §71-84 and `templates/bicep/modules/keyvault.bicep` §69-88) already manually re-implements a `AuditEvent`/`AllMetrics` diagnostic setting for Key Vault — that's *why* the compliance doc's claim happens to be true at the composed-repo level today, but it's not true of the reusable module in isolation, and it means the diagnostic logic is duplicated instead of owned by the module.

**Required fix:**

Terraform (`modules/terraform/azure-keyvault/v1/`):
1. In `variables.tf`, add:
   ```hcl
   variable "log_analytics_workspace_id" {
     type        = string
     description = "The resource ID of the central Log Analytics workspace for diagnostics"
     default     = null
   }
   ```
2. In `main.tf`, add (matching the category used by the existing composition-level duplicate — `AuditEvent`, plus `AllMetrics`):
   ```hcl
   resource "azurerm_monitor_diagnostic_setting" "kv" {
     count                      = var.log_analytics_workspace_id != null ? 1 : 0
     name                       = "ds-kv-${var.name}"
     target_resource_id         = azurerm_key_vault.kv.id
     log_analytics_workspace_id = var.log_analytics_workspace_id

     enabled_log {
       category = "AuditEvent"
     }

     metric {
       category = "AllMetrics"
     }
   }
   ```
3. Update `README.md` Inputs table to add the `log_analytics_workspace_id` row (`string`, description, default `null`, not required) — follow the existing table format in that file.

Bicep (`modules/bicep/azure-keyvault/v1/`):
1. In `main.bicep`, add a parameter:
   ```bicep
   @description('The resource ID of the central Log Analytics workspace for diagnostics')
   param logAnalyticsWorkspaceId string = ''
   ```
2. Add a diagnostic resource, matching the pattern already used in `modules/bicep/azure-network-baseline/v1/main.bicep` (`appgwDiagnostics`) and `modules/bicep/azure-private-runner/v1/main.bicep` (`runnerEnvDiagnostics`):
   ```bicep
   resource kvDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (!empty(logAnalyticsWorkspaceId)) {
     name: 'ds-kv-${name}'
     scope: kv
     properties: {
       workspaceId: logAnalyticsWorkspaceId
       logs: [
         {
           category: 'AuditEvent'
           enabled: true
         }
       ]
       metrics: [
         {
           category: 'AllMetrics'
           enabled: true
         }
       ]
     }
   }
   ```
3. Update `modules/bicep/azure-keyvault/v1/README.md` (if it has an inputs table — check first) to document the new param.

Tests to update:
- [`modules/terraform/azure-keyvault/v1/tests/main.tftest.hcl`](modules/terraform/azure-keyvault/v1/tests/main.tftest.hcl): add a `run` block that sets `log_analytics_workspace_id` to a fake resource ID and asserts the diagnostic setting resource count is 1; the existing default (unset) case should still plan cleanly with 0 diagnostic settings.
- [`modules/bicep/azure-keyvault/v1/tests/main.test.bicep`](modules/bicep/azure-keyvault/v1/tests/main.test.bicep): add a second `module` invocation passing `logAnalyticsWorkspaceId`, confirming the file still builds.

**Do not** change the composition-layer duplicates in `templates/terraform/main.tf` / `templates/bicep/modules/keyvault.bicep` — they are out of scope for this finding (they already satisfy the rule; fixing the module is about the module's own correctness in isolation).

---

## 2. Application Gateway uses fixed capacity instead of autoscale

**Rule violated:** `docs/cost-governance-guide.md` Rule 3 (§13): "Application Gateway Capacity Limits: Application Gateways must be configured with autoscale limits (e.g., `min_capacity = 1`, `max_capacity = 3`) instead of high fixed capacities." The same doc's §3.2 sizing table specifies dev/test `autoscale_min_capacity: 1, autoscale_max_capacity: 2` and prod `autoscale_min_capacity: 2, autoscale_max_capacity: 10`.

**Current state:**
- [`modules/terraform/azure-network-baseline/v1/main.tf:270-274`](modules/terraform/azure-network-baseline/v1/main.tf:270):
  ```hcl
  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 1
  }
  ```
  No `autoscale_configuration` block, and `capacity` is hardcoded with no variable.
- [`modules/bicep/azure-network-baseline/v1/main.bicep:328-332`](modules/bicep/azure-network-baseline/v1/main.bicep:328):
  ```bicep
  sku: {
    name: 'WAF_v2'
    tier: 'WAF_v2'
    capacity: 1
  }
  ```
  Same issue — no `autoscaleConfiguration`.

**Required fix:**

Terraform (`modules/terraform/azure-network-baseline/v1/`):
1. In `variables.tf`, add:
   ```hcl
   variable "appgw_autoscale_min_capacity" {
     type        = number
     description = "Minimum instance count for Application Gateway autoscaling"
     default     = 1

     validation {
       condition     = var.appgw_autoscale_min_capacity >= 0 && var.appgw_autoscale_min_capacity <= 100
       error_message = "The appgw_autoscale_min_capacity must be between 0 and 100."
     }
   }

   variable "appgw_autoscale_max_capacity" {
     type        = number
     description = "Maximum instance count for Application Gateway autoscaling"
     default     = 3

     validation {
       condition     = var.appgw_autoscale_max_capacity >= 2 && var.appgw_autoscale_max_capacity <= 125
       error_message = "The appgw_autoscale_max_capacity must be between 2 and 125."
     }
   }
   ```
2. In `main.tf`, replace the `sku` block (remove `capacity = 1`, azurerm requires you not set fixed `capacity` when `autoscale_configuration` is present) and add the autoscale block:
   ```hcl
   sku {
     name = "WAF_v2"
     tier = "WAF_v2"
   }

   autoscale_configuration {
     min_capacity = var.appgw_autoscale_min_capacity
     max_capacity = var.appgw_autoscale_max_capacity
   }
   ```
   (Place `autoscale_configuration` inside the `azurerm_application_gateway.app_gateway` resource block, alongside `sku`.)

Bicep (`modules/bicep/azure-network-baseline/v1/`):
1. Add params near the other appgw-related params:
   ```bicep
   @minValue(0)
   @maxValue(100)
   @description('Minimum instance count for Application Gateway autoscaling')
   param appgwAutoscaleMinCapacity int = 1

   @minValue(2)
   @maxValue(125)
   @description('Maximum instance count for Application Gateway autoscaling')
   param appgwAutoscaleMaxCapacity int = 3
   ```
2. In the `appGateway` resource, replace:
   ```bicep
   sku: {
     name: 'WAF_v2'
     tier: 'WAF_v2'
     capacity: 1
   }
   ```
   with:
   ```bicep
   sku: {
     name: 'WAF_v2'
     tier: 'WAF_v2'
   }
   autoscaleConfiguration: {
     minCapacity: appgwAutoscaleMinCapacity
     maxCapacity: appgwAutoscaleMaxCapacity
   }
   ```
   (`autoscaleConfiguration` is a top-level property alongside `sku` inside `properties`, not nested inside `sku`.)

Composition layer — wire environment-aware values (per the cost-governance-guide §3.2 table):

3. [`templates/terraform/main.tf`](templates/terraform/main.tf) `module "network"` block (§23-32): add
   ```hcl
   appgw_autoscale_min_capacity = var.environment == "prod" ? 2 : 1
   appgw_autoscale_max_capacity = var.environment == "prod" ? 10 : 2
   ```
4. [`templates/bicep/main.bicep`](templates/bicep/main.bicep) `module network` block (§54-65): add
   ```bicep
   appgwAutoscaleMinCapacity: (environment == 'prod') ? 2 : 1
   appgwAutoscaleMaxCapacity: (environment == 'prod') ? 10 : 2
   ```

Update `modules/terraform/azure-network-baseline/v1/README.md` and the Bicep module's README (if present) to document the two new inputs.

Tests: update `modules/terraform/azure-network-baseline/v1/tests/*` and the Bicep test file if they assert anything about the `sku`/capacity of the Application Gateway (check first — they may not reference it at all, in which case no test change is required beyond confirming `terraform validate` / `bicep build` still pass).

---

## 3. Container App `max_replicas` is hardcoded, not parameterized

**Rule violated:** `docs/cost-governance-guide.md` Rule 6 (§16): "Max Replicas Scaling Caps: Container Apps and App Services must have strict `max_replicas` scaling caps (e.g., `max_replicas = 5` in non-production) to prevent runaway scaling costs." — the rule presumes this is a parameter, and §3.1's sizing table gives different values per environment (dev/test: `max_replicas: 2`, prod: `max_replicas: 5`).

**Current state:**
- [`modules/terraform/azure-private-runner/v1/main.tf:65-66`](modules/terraform/azure-private-runner/v1/main.tf:65):
  ```hcl
  min_replicas = 0
  max_replicas = 5
  ```
  `max_replicas` is a literal; [`modules/terraform/azure-private-runner/v1/variables.tf`](modules/terraform/azure-private-runner/v1/variables.tf) has no `max_replicas` variable.
- [`modules/bicep/azure-private-runner/v1/main.bicep:133-135`](modules/bicep/azure-private-runner/v1/main.bicep:133):
  ```bicep
  scale: {
    minReplicas: 0
    maxReplicas: 5
    ...
  ```
  Same — no `maxReplicas` param exists.

**Required fix:**

Terraform (`modules/terraform/azure-private-runner/v1/`):
1. In `variables.tf`, add:
   ```hcl
   variable "max_replicas" {
     type        = number
     description = "Maximum replica count for the runner Container App"
     default     = 5

     validation {
       condition     = var.max_replicas >= 1 && var.max_replicas <= 25
       error_message = "The max_replicas variable must be between 1 and 25."
     }
   }
   ```
2. In `main.tf`, change `max_replicas = 5` to `max_replicas = var.max_replicas`.

Bicep (`modules/bicep/azure-private-runner/v1/`):
1. Add param:
   ```bicep
   @minValue(1)
   @maxValue(25)
   @description('Maximum replica count for the runner Container App')
   param maxReplicas int = 5
   ```
2. Change `maxReplicas: 5` to `maxReplicas: maxReplicas`.

Composition layer — wire environment-aware values (per cost-governance-guide §3.1: dev/test 2, prod 5):

3. [`templates/terraform/main.tf`](templates/terraform/main.tf) `module "runners"` block (§87-102): add
   ```hcl
   max_replicas = var.environment == "prod" ? 5 : 2
   ```
4. [`templates/bicep/main.bicep`](templates/bicep/main.bicep) `module runners` block (§92-106): add
   ```bicep
   maxReplicas: (environment == 'prod') ? 5 : 2
   ```

Update `modules/terraform/azure-private-runner/v1/README.md` (currently just a features list, no Inputs table — check the keyvault module's README for the table format and add one, or at minimum add a line documenting the new variable) and the Bicep module README if present.

Tests: update `modules/terraform/azure-private-runner/v1/tests/*` and the Bicep test file to pass a non-default `max_replicas`/`maxReplicas` and assert it's reflected on the resource, if the test files already assert resource properties (check current test content first).

---

## 4. Log Analytics Workspace ignores per-environment retention/quota guidance

**Rule violated:** `docs/cost-governance-guide.md` §3.3 sizing table (dev/test: `retention_in_days: 30, daily_quota_gb: 1`; prod: `retention_in_days: 90, daily_quota_gb: -1`) and Rule 8 (§18): "Logging Retention Controls: Log Analytics workspace data retention must be set to the minimum required by compliance (typically 30 to 90 days) with older logs archived to low-cost cold storage."

**Current state:**
- [`templates/terraform/main.tf:14-20`](templates/terraform/main.tf:14):
  ```hcl
  resource "azurerm_log_analytics_workspace" "ops" {
    name                = "law-${var.project_name}-${var.environment}"
    location            = azurerm_resource_group.core.location
    resource_group_name = azurerm_resource_group.core.name
    sku                 = "PerGB2018"
    retention_in_days   = 30
  }
  ```
  `retention_in_days` is hardcoded to 30 regardless of `var.environment`, and there's no `daily_quota_gb` argument at all — no ingestion cost cap for dev/test, and prod won't get 90-day retention as the compliance doc requires.
- [`templates/bicep/modules/logging.bicep:19-28`](templates/bicep/modules/logging.bicep:19): same issue — `retentionInDays: 30` hardcoded, no `workspaceCapping.dailyQuotaGb`.

**Required fix:**

Terraform (`templates/terraform/main.tf`):
```hcl
resource "azurerm_log_analytics_workspace" "ops" {
  name                = "law-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.core.location
  resource_group_name = azurerm_resource_group.core.name
  sku                 = "PerGB2018"
  retention_in_days   = var.environment == "prod" ? 90 : 30
  daily_quota_gb      = var.environment == "prod" ? -1 : 1
}
```

Bicep (`templates/bicep/modules/logging.bicep`):
```bicep
resource workspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' = {
  name: 'law-${projectName}-${environment}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: (environment == 'prod') ? 90 : 30
    workspaceCapping: {
      dailyQuotaGb: (environment == 'prod') ? -1 : 1
    }
  }
}
```
(`environment` is already a param of `logging.bicep` — no signature change needed. Same for `templates/terraform/main.tf`, which already has `var.environment` in scope.)

No changes needed to `modules/` — this workspace is only defined at the composition/template layer, not as a standalone versioned module.

Verify: `templates/terraform/` and `templates/bicep/` contain scaffold placeholders (`{{ }}`) and are intentionally excluded from `terraform validate` / `bicep build` in `azure-pipelines.yml` (see comments at lines 243 and 268). You will not be able to run automated validation against these files directly — sanity-check by hand-substituting placeholder values into a scratch copy and running `terraform validate` / `az bicep build` against that copy, or just careful visual review, since CI won't catch mistakes here.

---

## 5. Runner CPU/memory defaults match Production sizing, not Dev/Test

**Rule violated:** `docs/cost-governance-guide.md` Rule 7 (§17): "Right-Sized CPU/Memory Variables: CPU and Memory allocations for container runtimes must be parameterized and set to conservative defaults (e.g., `0.5 CPU` and `1.0 GiB Memory` for runners)." §3.1's table: dev/test `runner_cpu: 0.5, runner_memory: 1.0Gi`; prod `runner_cpu: 1.0, runner_memory: 2.0Gi`.

**Current state:** the module-level defaults are set to the **production** values even though `environment` itself defaults to `"dev"` throughout the codebase:
- [`modules/terraform/azure-private-runner/v1/variables.tf:88-108`](modules/terraform/azure-private-runner/v1/variables.tf:88): `runner_cpu` default `"1.0"`, `runner_memory` default `"2.0Gi"`.
- [`modules/bicep/azure-private-runner/v1/main.bicep:41,52`](modules/bicep/azure-private-runner/v1/main.bicep:41): `runnerCpu` default `'1.0'`, `runnerMemory` default `'2.0Gi'`.
- [`templates/terraform/variables.tf:81-101`](templates/terraform/variables.tf:81): same defaults, exposed to end users of the scaffold.

**Required fix:**

1. In `modules/terraform/azure-private-runner/v1/variables.tf`, change the defaults to the conservative dev/test values:
   ```hcl
   variable "runner_cpu" {
     ...
     default = "0.5"
     ...
   }

   variable "runner_memory" {
     ...
     default = "1.0Gi"
     ...
   }
   ```
   (Keep the existing `validation` blocks — the allowed-values lists already include `"0.5"` and `"1.0Gi"`, no change needed there.)

2. In `modules/bicep/azure-private-runner/v1/main.bicep`, change:
   ```bicep
   param runnerCpu string = '0.5'
   ...
   param runnerMemory string = '1.0Gi'
   ```

3. In `templates/terraform/variables.tf`, change the same two defaults to `"0.5"` / `"1.0Gi"` (this is the top-level scaffold default a new user gets before choosing an environment).

4. In the composition layer, make the values environment-aware instead of relying on the (now conservative) module default — this ensures prod actually gets prod-sized runners instead of silently inheriting the dev default:
   - [`templates/terraform/main.tf`](templates/terraform/main.tf) `module "runners"` block (§87-102): currently passes `runner_cpu = var.runner_cpu` / `runner_memory = var.runner_memory` straight through from the top-level variables. Change to:
     ```hcl
     runner_cpu    = var.environment == "prod" ? "1.0" : var.runner_cpu
     runner_memory = var.environment == "prod" ? "2.0Gi" : var.runner_memory
     ```
   - [`templates/bicep/main.bicep`](templates/bicep/main.bicep) `module runners` block (§92-106): it does not currently pass `runnerCpu`/`runnerMemory` at all (relying on the Bicep module's own defaults). Add:
     ```bicep
     runnerCpu: (environment == 'prod') ? '1.0' : '0.5'
     runnerMemory: (environment == 'prod') ? '2.0Gi' : '1.0Gi'
     ```

Update the README/Inputs docs for both `modules/terraform/azure-private-runner/v1/README.md` and the Bicep module's README (if present) to reflect the new default values.

---

## Execution order

Do the fixes in the order listed (1 → 5) — findings 2, 3, and 5 all touch the same composition files (`templates/terraform/main.tf`, `templates/bicep/main.bicep`), so doing them in sequence avoids merge conflicts within your own edits. Finding 4 is independent and can be done any time.

## Verification (run after each finding, and again at the end)

```bash
# Terraform format check
terraform fmt -check -recursive -diff modules

# Terraform module validation (per touched module)
cd modules/terraform/azure-keyvault/v1 && terraform init -backend=false && terraform validate && cd -
cd modules/terraform/azure-network-baseline/v1 && terraform init -backend=false && terraform validate && cd -
cd modules/terraform/azure-private-runner/v1 && terraform init -backend=false && terraform validate && cd -

# Terraform native tests (if `terraform test` is available — Terraform >= 1.6)
cd modules/terraform/azure-keyvault/v1 && terraform test && cd -
cd modules/terraform/azure-network-baseline/v1 && terraform test && cd -
cd modules/terraform/azure-private-runner/v1 && terraform test && cd -

# Bicep build validation (per touched module)
az bicep build --file modules/bicep/azure-keyvault/v1/main.bicep --stdout > /dev/null
az bicep build --file modules/bicep/azure-network-baseline/v1/main.bicep --stdout > /dev/null
az bicep build --file modules/bicep/azure-private-runner/v1/main.bicep --stdout > /dev/null

# Repo-wide consistency checks
python3 scripts/validate-skills.py
python3 scripts/validate-team.py
python3 -m json.tool opencode.json > /dev/null
```

Note: `templates/terraform` and `templates/bicep` contain `{{ }}` scaffold placeholders and are **not** validated by `terraform validate` / `bicep build` in CI (see `azure-pipelines.yml`) — review those edits by hand as described in Finding 4.

## Acceptance criteria

- [ ] All 5 findings fixed in both the Terraform and Bicep stacks (parity maintained).
- [ ] All new variables/params have sensible defaults and validation consistent with existing style in the same file.
- [ ] All new/changed module inputs documented in the relevant `README.md`.
- [ ] All commands in the Verification section pass with no errors.
- [ ] No unrelated files changed — this is a scoped fix, not a refactor.
- [ ] Update this file's status line at the top from `⏳ PENDING` to `✅ COMPLETED`, and add a dated entry to [`BUILD_JOURNAL.md`](BUILD_JOURNAL.md) summarizing what changed (follow the existing entry format in that file), matching how Epic 1 was logged in [`BUILD_PLAN.md`](BUILD_PLAN.md).
