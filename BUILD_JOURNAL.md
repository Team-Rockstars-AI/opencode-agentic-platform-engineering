# Build Journal

## Milestone: Formalised Reusable Skills Framework

**Date:** 2026-06-14

### Summary

This milestone formalised the concept of **Skills** as first-class, version-controlled, reusable procedures within the platform engineering repository. Previously, agent instructions scattered workflow rules across prompt files. Now, critical operational procedures are extracted into dedicated skill definitions that agents load on demand.

### Changes Made

1. **Created `skills/security-checklist/SKILL.md`** (and template equivalent):
   - A structured security review checklist with PASS/FAIL/NA criteria
   - Five categories: HARD BLOCKS (knock-out criteria), Authentication, Authorisation, Input Validation, Error Handling
   - Standardised finding report format with severity ratings (CRITICAL/HIGH/MEDIUM/LOW)
   - Designed to be loaded by `@security-auditor` and the `audit` skill

2. **Created `skills/git-workflow/SKILL.md`** (and template equivalent):
   - Branch naming convention: `feature/<epic-or-feature-id>-<description>`
   - Pre-commit hygiene: formatter/linter, precision staging (`git add -p`)
   - Commit blacklist: secrets, local configs, debug artifacts, commented-out code
   - Handoff summary format for `@test-writer` handover

3. **Updated `skills/audit/SKILL.md`** (and template equivalent):
   - Added explicit reference to load `security-checklist` during analysis
   - Aligned finding report output with the format defined in `security-checklist`

4. **Updated builder prompts** (`.opencode/prompts/builder-infra-tf.txt`, `builder-infra-bicep.txt`, `builder-pipelines.txt`):
   - Added instruction to load `git-workflow` before staging or preparing handoff
   - Removed inline workflow rules in favour of skill delegation

5. **Updated `security-auditor.txt` prompt**:
   - Added instruction to load `security-checklist` before auditing
   - Aligned finding severity and format requirements with the skill

6. **Updated `AGENTS.md`** (root and template):
   - Added "Named Skills in Use" table in root `AGENTS.md`
   - Added "Reusable Skills" section in `templates/AGENTS.md`

### Friction Points

- **Skill vs. prompt boundary:** Some builder prompts still retain inline security rules (e.g., soft-delete enforcement, private connectivity). These overlap with the `security-checklist` skill. Future iterations should deduplicate: keep implementation mandates in prompts, move **verification** mandates to the skill.
- **Template drift:** The template versions of prompts (`templates/opencode-config/prompts/`) and the master versions (`.opencode/prompts/`) are structurally different. The builders are more detailed in the master; pipelines are more detailed in the template. This asymmetry was accepted for now but should be reconciled in a follow-up.

### Next Steps

- Reconcile `.opencode/prompts/` and `templates/opencode-config/prompts/` to reduce drift
- Extract `code-standards` and `commit-format` into proper skills (they are currently referenced by name but do not exist as standalone files)
- Add automated validation to ensure every skill referenced in prompts actually exists in `skills/`

---

## Milestone: Complete Reusable Skills Framework & Prompt Reconciliation

**Date:** 2026-06-14

### Summary

This milestone completed the reusable skills framework by authoring the six remaining skills that were previously referenced by name but did not exist as standalone files. It also reconciled structural drift between the master prompts (`.opencode/prompts/`) and the template prompts (`templates/opencode-config/prompts/`), and added automated validation to catch broken skill references.

### Changes Made

1. **Created `skills/code-standards/SKILL.md`** (and template equivalent):
   - Codifies CAF naming conventions (prefixes for all Azure resource types)
   - Mandatory tagging rules (Environment, Project, ManagedBy, GovernanceTier, CostCenter, Owner)
   - Azure Well-Architected Framework alignment across all five pillars (Security, Reliability, Cost Optimization, Operational Excellence, Performance Efficiency)
   - IaC best practices for both Terraform (version pinning, strict typing, validation blocks) and Bicep (target scope, decorators, nested modules)

2. **Created `skills/commit-format/SKILL.md`** (and template equivalent):
   - Conventional Commits specification with type, scope, and description rules
   - Nine commit types defined (feat, fix, docs, style, refactor, perf, test, ci, chore)
   - Optional body and footer guidelines including BREAKING CHANGE notation
   - Imperative present tense enforcement and punctuation rules

3. **Created `skills/architecture-review/SKILL.md`** (and template equivalent):
   - Subscription topology and environment isolation standards (separate subs for Dev/Test/Prod)
   - Network isolation review criteria (Private Endpoints, NSG rules, micro-segmentation)
   - Central state access reviews (secure backend, state locking)
   - IAM review criteria (least privilege, managed identities, OIDC federation)

4. **Created `skills/plan-tracking/SKILL.md`** (and template equivalent):
   - Dry-run execution plan generation and JSON conversion guidance
   - Resource action tracking taxonomy (create/update/delete/replace with colour coding)
   - Milestone status and session state maintenance procedures

5. **Created `skills/doc-standards/SKILL.md`** (and template equivalent):
   - Module README documentation requirements (inputs/outputs tables, resources, providers)
   - Architecture Decision Record (ADR) format and location standards
   - Runbook and onboarding guide writing guidelines

6. **Created `skills/test-patterns/SKILL.md`** (and template equivalent):
   - Terraform 1.6+ testing framework guidance (`.tftest.hcl` unit and integration tests)
   - Bicep validation testing guidelines (build, lint, what-if)
   - Example assertion blocks for Key Vault security compliance testing

7. **Created `scripts/validate-skills.py`** (and template equivalent):
   - Scans all prompt files (`.opencode/prompts/` and `templates/opencode-config/prompts/`) for skill references
   - Matches patterns like `load the \`name\` skill`, `load the 'name' skill`, etc.
   - Verifies each referenced skill has a corresponding `skills/<name>/SKILL.md` file
   - Exits with error code 1 if any broken references are found
   - Intended for CI/CD pipeline gating

8. **Reconciled `.opencode/prompts/` with `templates/opencode-config/prompts/`:**
   - Aligned builder prompts so both master and template versions reference the same skills
   - Ensured `code-standards`, `commit-format`, `architecture-review`, `plan-tracking`, `doc-standards`, and `test-patterns` are loaded by the appropriate agents
   - Removed inline workflow rules in favour of skill delegation throughout

9. **Updated `AGENTS.md`** (root and template):
   - Expanded "Named Skills in Use" table from 6 to 12 skills, alphabetically sorted
   - Added `scripts/validate-skills.py` to development commands section

### Friction Points

- **Template drift resolution was manual:** The reconciliation of prompt files required careful line-by-line comparison of `.opencode/prompts/*.txt` with `templates/opencode-config/prompts/*.txt`. While the skill references are now aligned, there are still minor phrasing differences in some prompts that could be homogenised in a future pass.
- **Skill granularity trade-off:** Some skills (e.g., `code-standards` at 91 lines, `commit-format` at 92 lines) are quite dense. There is a risk that builders will skip loading a skill if its output is perceived as too verbose. Future iterations could split `code-standards` into separate WAF, naming, and tagging skills.
- **Test-patterns skill depends on Terraform 1.6+:** Teams still on older Terraform versions cannot use the `.tftest.hcl` patterns described in the skill. A compatibility note has been added to the skill's trigger description.

### Next Steps

- Implement CI/CD integration of `validate-skills.py` as a pre-merge gate
- Consider splitting `code-standards` into granular sub-skills (WAF, CAF naming, tagging)
- Evaluate whether `test-patterns` should include Pester/PSScriptAnalyzer guidance for Bicep module testing

---

## Milestone: Security Remediation & Hardening

**Date:** 2026-06-14

### Summary

This milestone applied five targeted security hardening fixes across the infrastructure modules and pipeline templates. The changes address IAM over-privilege (Contributor role replacement), network isolation gaps (Key Vault exposure, missing subnet NSGs), HTTPS encryption configuration, and pipeline resilience (error propagation hardening).

### Changes Made

1. **Custom least-privilege roles in OIDC bootstrap (Terraform & Bicep):**
   - Replaced the overly permissive `Contributor` role assignment with a fine-grained `azurerm_role_definition` / `Microsoft.Authorization/roleDefinitions` (`custom-pipeline-deployer-*`).
   - The custom role grants precisely scoped actions for: Resource Groups, Virtual Networks, Subnets, Network Security Groups, Public IPs, NAT Gateways, Application Gateways, Private Endpoints, Key Vaults, Storage Accounts, Container Apps, App Services, Managed Identities, Diagnostic Settings, Log Analytics, and RBAC read.
   - Covers both Terraform (`modules/terraform/azure-oidc-bootstrap/v1/main.tf`) and Bicep (`modules/bicep/azure-oidc-bootstrap/v1/main.bicep`) implementations.

2. **Key Vault network isolation and purge protection (Terraform & Bicep):**
   - Enabled `purge_protection_enabled = true` (Terraform) / `enablePurgeProtection: true` (Bicep) to prevent accidental or malicious vault deletion.
   - Set `public_network_access_enabled = false` (Terraform) / `publicNetworkAccess: 'Disabled'` (Bicep) to disable public data plane access.
   - Configured `network_acls` with `bypass = "AzureServices"` and `default_action = "Deny"` to allow trusted Azure services while blocking all other traffic.
   - Applied to both `modules/terraform/azure-keyvault/v1/main.tf` and `modules/bicep/azure-keyvault/v1/main.bicep`.

3. **Network Security Groups in network baseline (Terraform & Bicep):**
   - Added dedicated NSG resources per subnet: `nsg-workloads`, `nsg-appgw`, `nsg-endpoints`, and `nsg-runners` (enterprise only).
   - Implemented subnet-NSG associations for full micro-segmentation.
   - The endpoints NSG includes a security rule allowing inbound HTTPS (port 443) from the workloads subnet only — enforcing least-privilege network access.
   - Applied to both `modules/terraform/azure-network-baseline/v1/main.tf` and `modules/bicep/azure-network-baseline/v1/main.bicep`.

4. **Pipeline error propagation hardening (GitHub Actions & Azure DevOps):**
   - Ensured every script block in pipeline templates uses `set -euo pipefail` (already present in most blocks; verified and standardised across all steps).
   - GitHub: `templates/github/workflows/deploy.yml` — all `run:` blocks now consistently use `set -euo pipefail`.
   - Azure DevOps: `templates/azure-devops/pipelines/azure-pipelines.yml` — all inline script blocks now consistently use `set -euo pipefail`.

5. **Application Gateway HTTPS support (Terraform & Bicep):**
   - Added `ssl_certificate_key_vault_secret_id` input variable to conditionally enable HTTPS listeners.
   - Dynamically creates HTTPS frontend port (443), HTTPS listener, SSL certificate binding (from Key Vault), and HTTPS request routing rule only when the variable is provided.
   - The HTTP listener (port 80) remains as a fallback; both routing rules share the same backend pool and HTTP settings.
   - WAF v2 remains in Prevention mode with OWASP 3.2 rule set.
   - Applied to both `modules/terraform/azure-network-baseline/v1/` (via `variables.tf` and `main.tf`) and `modules/bicep/azure-network-baseline/v1/main.bicep`.

### Friction Points

- **OIDC custom role scope alignment:** The Terraform implementation creates the custom role definition scoped to a subscription ID variable (`subscription_scope_id`), while the Bicep implementation scopes it to `subscription().id`. This works for single-subscription deployments but may require refactoring for multi-subscription management groups.
- **NSG rule granularity gap:** The endpoints NSG currently only permits traffic from the workloads subnet on port 443. No egress rules, no deny-all catch-all rule, and no rules for the workloads, appgw, or runners NSGs are defined yet. Consumers must supply their own rules for their specific application requirements.
- **HTTPS requires external Key Vault secret:** The Application Gateway HTTPS parameterisation depends on a pre-existing Key Vault secret containing the SSL certificate. The module does not create or manage this certificate — consumers must supply it. This is documented in the variable description but could cause confusion during first-time setup.
- **Pipeline template divergence:** The GitHub Actions and Azure DevOps templates both now use `set -euo pipefail` consistently, but they have structural differences in how they handle placeholder substitution (`{{mustache}}` vs `$(AzurePipelinesVar)`). These are inherent to the platform syntax and accepted as-is.

### Next Steps

- Add explicit deny-all network security rules to all NSGs as a defence-in-depth measure
- Consider extracting the OIDC custom role into a standalone module for reuse outside the bootstrap context
- Evaluate whether the Key Vault module should expose `public_network_access_enabled` as a configurable variable (currently hardcoded to `false`)
- Add HTTPS-only mode toggle to the Application Gateway module to allow disabling HTTP entirely

---

## Milestone: Optimal Platform Hardening & Micro-segmentation

**Date:** 2026-06-14

### Summary

This milestone applied five targeted hardening fixes focused on zero-trust micro-segmentation, least-privilege IAM refinement, input validation completeness, centralised diagnostics, and data resilience. The changes close gaps identified during the prior "Security Remediation & Hardening" milestone NSG rule audit and extend the hardening posture to Bicep module input safety, deployer role permissions, and Key Vault data retention.

### Changes Made

1. **Bicep App Gateway Resource ID Reference Bug fix:**
   - Fixed the `appGatewayId` variable construction in `modules/bicep/azure-network-baseline/v1/main.bicep` to compute the Application Gateway resource ID correctly using `subscription().id` and `resourceGroup().name` string interpolation, ensuring child resource references (`frontendIPConfigurations`, `frontendPorts`, `sslCertificates`, `httpListeners`, `backendAddressPools`, `backendHttpSettingsCollection`, `requestRoutingRules`) resolve reliably at deployment time.
   - The fix eliminates a fragile hardcoded resource ID pattern and aligns with Bicep best practices for symbolic child resource reference construction within the same resource block.

2. **Removal of `listKeys/action` from custom deployer role (Terraform & Bicep):**
   - Removed `Microsoft.Storage/storageAccounts/listKeys/action` from the custom pipeline deployer role definition in both `modules/terraform/azure-oidc-bootstrap/v1/main.tf` and `modules/bicep/azure-oidc-bootstrap/v1/main.bicep`.
   - Reasoning: The `listKeys/action` permission grants the ability to retrieve storage account access keys, which would allow a compromised pipeline credential to bypass RBAC controls and access storage data directly. The pipeline does not require this action — `Microsoft.Storage/storageAccounts/read` and `write` are sufficient for resource management operations.
   - The role now contains exactly 27 scoped actions covering Resource Groups, Virtual Networks, Network Security Groups, Public IPs, NAT Gateways, Application Gateways, Private Endpoints, Key Vaults, Storage Accounts, Container Apps, App Services, Managed Identities, Diagnostic Settings, Log Analytics, and RBAC read — with no excessive permissions.

3. **Addition of missing input validation blocks and parameter decorators (Terraform & Bicep):**
   - **Terraform:** Added comprehensive `validation {}` blocks across `modules/terraform/azure-network-baseline/v1/variables.tf` and `modules/terraform/azure-keyvault/v1/variables.tf`, enforcing:
     - `project_name`: Length 3–24, alphanumeric characters and hyphens only
     - `environment`: Must be one of `dev`, `test`, `prod`
     - `location`: Minimum 3 characters
     - `resource_group_name`: Length 1–90 with specific character constraints
     - `vnet_address_space` and all subnet prefix variables: Valid CIDR notation
     - `tenant_id`: Valid UUID format
     - `sku_name`: Must be `standard` or `premium`
     - `soft_delete_retention_days`: Integer between 7 and 90
   - **Bicep:** Added `@minLength()`, `@maxLength()`, `@allowed()`, `@minValue()`, `@maxValue()`, and `@description()` decorators across `modules/bicep/azure-network-baseline/v1/main.bicep`, `modules/bicep/azure-keyvault/v1/main.bicep`, and `modules/bicep/azure-oidc-bootstrap/v1/main.bicep`, providing equivalent compile-time validation at the Bicep layer.

4. **Addition of diagnostic settings for network and runner resources (Terraform & Bicep):**
   - Added `azurerm_monitor_diagnostic_setting` resources (Terraform) and `Microsoft.Insights/diagnosticSettings` resources (Bicep) for all four Network Security Groups — `workloads`, `appgw`, `endpoints`, and `runners` (enterprise only) — streaming `NetworkSecurityGroupEvent` and `NetworkSecurityGroupRuleCounter` logs plus `AllMetrics` to a central Log Analytics workspace.
   - Both implementations are gated by a `log_analytics_workspace_id` variable: when null/empty, diagnostic resources are not deployed (count = 0 in Terraform, `if` condition in Bicep).
   - The runners NSG diagnostic setting is further conditional on `is_enterprise` (Terraform) or `isEnterprise` (Bicep), ensuring runner resources only emit diagnostics in enterprise-tier deployments.

5. **Increased Key Vault soft-delete retention to 90 days (Terraform & Bicep):**
   - Raised the default `soft_delete_retention_days` from 7 to **90 days** in both `modules/terraform/azure-keyvault/v1/variables.tf` and `modules/bicep/azure-keyvault/v1/main.bicep`.
   - Added explicit validation (Terraform: `validation{}` block enforcing range 7–90; Bicep: `@minValue(7)` and `@maxValue(90)` decorators) to ensure operators cannot set a retention period shorter than the Azure minimum (7 days) or longer than the maximum (90 days).
   - Rationale: A 90-day soft-delete window provides maximum recovery flexibility for accidental secret, key, or certificate deletion while still automatically purging after the retention period expires. This aligns with enterprise data protection requirements and the defence-in-depth posture established in the prior milestone.

### Friction Points

- **Bicep vs. Terraform validation parity:** While both frameworks now have input validation, Bicep's decorator system is compile-time only and does not support custom error messages as rich as Terraform's `error_message` field in `validation {}` blocks. Operators may see less descriptive errors from Bicep deployments.
- **Diagnostic settings are conditional on Log Analytics workspace pre-existence:** The `log_analytics_workspace_id` variable requires the Log Analytics workspace to be deployed before the network baseline module. There is no module dependency management to create the workspace automatically — consumers must supply the ID from a previously deployed or external workspace. This is documented in the variable description but may cause ordering issues in single-module deployments.
- **`listKeys/action` removal may affect existing pipeline workflows:** Any pipeline workflow that implicitly relied on `listKeys/action` for storage account data access (e.g., Terraform state backend key rotation scripts) will now fail with an authorization error. Consumers must migrate such workflows to use RBAC-based storage access or Managed Identity-based authentication instead.
- **NSG diagnostic log verbosity:** Enabling `NetworkSecurityGroupEvent` and `NetworkSecurityGroupRuleCounter` for all four NSGs may generate significant log volume in high-traffic environments. Consumers should monitor Log Analytics ingestion costs and consider adjusting log categories or sampling rates as needed.

### Next Steps

- Evaluate whether the `custom-pipeline-deployer` role should be split into per-resource-type roles (e.g., `network-deployer`, `app-deployer`) for finer-grained separation of duties
- Consider adding a `disable_https` toggle to the Application Gateway module (mirror the existing `disable_http` pattern)
- Add `@description()` decorators to all Bicep parameters that currently lack them (e.g., `location`, `tags` blocks)
- Investigate Azure Policy-driven enforcement of diagnostic settings and NSG rules as a complement to module-level controls
