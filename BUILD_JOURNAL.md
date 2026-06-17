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

---

## Milestone: High-Value Provisioning System Enhancements

**Date:** 2026-06-14

### Summary

This milestone delivered three high-value provisioning system enhancements that improve the repository scaffolding experience, enforce local compliance during development, and provide pre-built architectural governance documentation. The additions target the template layer — the output that consumers receive after running the scaffold workflow.

### Changes Made

1. **Created `scripts/scaffold.py` — automated scaffolding script:**
   - A self-contained Python script (zero external dependencies, standard library only) that orchestrates the entire repository generation process.
   - Supports both **interactive mode** (prompts the user for IaC framework, DevOps platform, governance tier, project name, Azure configuration) and **non-interactive/CLI mode** (all options passed via command-line flags for CI/CD or scripted automation).
   - Handles all scaffold operations: directory creation, template file copying, module inclusion from `modules/`, OpenCode config deployment (prompts, skills, `opencode.json`), `AGENTS.md` copy, documentation template copy, `.gitignore` generation, placeholder substitution (`{{project_name}}`, `{{azure_location}}`, `{{subscription_id}}`, etc.).
   - Automatically resolves and moves `.pre-commit-config.yaml` from the IaC template directory to the target root.
   - Performs post-copy cleanup (removes `.opencode-scaffold.json` scaffolding metadata files) and executes `git init` with an initial Conventional Commits commit (`feat: initial platform-engineering template`).
   - Sets executable permissions on copied scripts (`validate-skills.py`).

2. **Created `.pre-commit-config.yaml` in IaC templates (Terraform & Bicep):**
   - **Terraform variant** (`templates/terraform/.pre-commit-config.yaml`): Configures five pre-commit hooks:
     - `check-yaml`, `end-of-file-fixer`, `trailing-whitespace`, `check-added-large-files` (from `pre-commit-hooks` v4.6.0)
     - `gitleaks` (v8.18.2) for secret scanning
     - `checkov` (v3.2.216) with `--framework terraform` for SAST compliance scanning
     - `terraform_fmt`, `terraform_validate`, `terraform_tflint` (from `pre-commit-terraform` v1.92.0)
   - **Bicep variant** (`templates/bicep/.pre-commit-config.yaml`): Configures five pre-commit hooks:
     - Same generic hooks as Terraform variant (`check-yaml`, `end-of-file-fixer`, `trailing-whitespace`, `check-added-large-files`)
     - `gitleaks` (v8.18.2) for secret scanning
     - `checkov` (v3.2.216) with `--framework bicep` and `.bicep` file filter for SAST compliance scanning
   - Both configurations use `fail_fast: false` so all hooks run and report all violations in a single pass.
   - The `scaffold.py` script automatically moves the relevant config to the target repository root during scaffolding, removing the unused variant.

3. **Created pre-populated Architecture Decision Records (ADRs) under `templates/docs/adr/`:**
   - **ADR 0001: Record Architecture Decisions** — Establishes the ADR practice itself: sequential numbering (`NNNN-title.md`), standard template (Status, Context, Decision, Consequences, References), and storage under `docs/adr/`. References Michael Nygard's ADR methodology.
   - **ADR 0002: OIDC Federated Credentials for Pipeline Authentication** — Mandates OIDC with Azure Federated Credentials for all pipeline authentication, eliminating long-lived client secrets. Documents the JWT exchange flow, federated trust scoping (org/repo/branch), and zero-secrets configuration pattern.
   - **ADR 0003: Private Endpoints and Network Isolation for Stateful Resources** — Enforces Azure Private Endpoints for all stateful resources (Key Vaults, Storage Accounts, Databases) with public access disabled. Documents Private DNS Zone integration and trusted service bypass patterns.
   - **ADR 0004: Subnet-Level Micro-Segmentation via Network Security Groups** — Codifies dedicated NSGs per subnet with explicit default-deny posture. Prohibits public exposure of management ports (22/3389) and establishes application-tier communication rules.
   - **ADR 0005: Self-Hosted Runners with KEDA Scaling for Enterprise Deployments** — For enterprise-tier deployments, specifies AKS-hosted ephemeral self-hosted runners with KEDA-based autoscaling (scale-to-zero when idle). Documents Managed Identity integration for credential-free runner authentication.
   - All ADRs follow the standard template, reference related ADRs via relative paths, and link to external Microsoft/Azure documentation for further reading.

### Friction Points

- **Pre-commit hook version pinning:** Both config files pin specific tool versions (`v4.6.0`, `v8.18.2`, `v3.2.216`, `v1.92.0`). These will need regular updates to stay current with upstream releases. There is no automated Dependabot/Renovate configuration for pre-commit hooks yet.
- **Bicep vs. Terraform pre-commit parity:** The Bicep variant lacks the `terraform_*` hooks (expected), but also lacks a `bicep build` / `bicep lint` hook. Bicep consumers must remember to run validation manually or configure their own hook.
- **ADR sequence gap:** ADR 0001 references the ADR methodology itself, ADRs 0002–0005 cover the four core architectural pillars. There is no ADR 0006+ placeholder for future consumers to extend. The next consumer-authored ADR should start at 0006 without confusion.
- **Scaffold.py is framework-aware but not idempotent:** Running `scaffold.py` against an existing target directory will overwrite files without warning. There is no `--dry-run` or `--force` safety check. A safety confirmation prompt exists in interactive mode but not in non-interactive mode.

### Next Steps

- Add `bicep build` validation hook to the Bicep pre-commit configuration
- Implement `--dry-run` mode in `scaffold.py` to preview changes before writing
- Add Dependabot/Renovate configuration to auto-update pre-commit hook revisions
- Draft ADR 0006 placeholder to guide consumers on extending the ADR log
- Integrate `scaffold.py` as the backend for the `/scaffold` slash command workflow

---

## Milestone: Security Audit Remediation & Hardening

**Date:** 2026-06-14

### Summary

This milestone remediated three security findings identified during the `@security-auditor`'s workspace compliance scan. The changes address pipeline environment isolation, Bicep type safety, and self-hosted runner credential rotation risks.

### Changes Made

1. **Pipeline Environment Isolation (GitHub & Azure DevOps):**
   - **GitHub Actions (`templates/github/workflows/deploy.yml`):** Configured environment-specific credential mappings. The `validate` job now dynamically targets the `development` or `production` environment based on the branch (`environment: ${{ github.ref == 'refs/heads/main' && 'production' || 'development' }}`), and the `deploy` job is explicitly bound to the `production` environment.
   - **Azure DevOps (`templates/azure-devops/pipelines/azure-pipelines.yml`):** Removed the global `azureServiceConnection` variable and defined it at the stage level. The `Validate` stage now uses `'sc-{{project_name}}-dev-deploy'` and the `Deploy` stage uses `'sc-{{project_name}}-prod-deploy'`, ensuring strict environment isolation.

2. **Bicep Type Safety Hardening:**
   - **Bicep Private Runner Module (`modules/bicep/azure-private-runner/v1/main.bicep`):** Added parameterized `runnerCpu` and `runnerMemory` variables with strict `@allowed` decorators. Replaced the `cpu: any('1.0')` bypass with the strongly-typed `runnerCpu` parameter, restoring full compile-time type safety.

3. **GitHub PAT Rotational Risk Mitigation:**
   - Expanded the variable descriptions in `modules/terraform/azure-private-runner/v1/variables.tf`, `modules/bicep/azure-private-runner/v1/main.bicep`, `templates/terraform/variables.tf`, and `templates/bicep/main.bicep` to explicitly document the GitHub App-based runner registration approach as the preferred, secure, and auto-rotating path.

### Friction Points

- **Bicep vs. Terraform validation parity:** While both frameworks now have input validation, Bicep's decorator system is compile-time only and does not support custom error messages as rich as Terraform's `error_message` field in `validation {}` blocks.
- **GitHub App-based runner registration complexity:** While documented as the preferred path, implementing GitHub App-based runner registration requires additional setup steps (creating the App, installing it, and generating private keys) compared to a simple PAT.

### Next Steps

- Implement automated rotation scripts or GitHub App integration examples for self-hosted runner registration.
- Add `bicep build` validation hook to the Bicep pre-commit configuration.

---

## Milestone: Static Cost & Resource Optimization Engine

**Date:** 2026-06-15

### Summary

This milestone implemented Epic 1 (Static Cost & Resource Optimization Engine), introducing cost-governance and resource sizing analysis directly into the platform engineering repository. This was achieved by authoring the `optimise` skill and its template equivalent, parameterizing the Terraform private runner module for conservative resource sizing, and registering the `/optimise` command in both the local and template configurations of `opencode.json`. The engine scans IaC templates, subnets, and container apps for oversized SKUs, cost leaks, and sizing inefficiencies while enforcing strict security baselines.

### Changes Made

1. **Created `skills/optimise/SKILL.md`** (and template equivalent):
   - Defined 8 static cost and resource optimization rules (Key Vault SKU gating, soft-delete retention trim, Application Gateway capacity limits, selective WAF tier toggles, private runner scale-to-zero, max replicas scaling caps, right-sized CPU/Memory variables, and logging retention controls).
   - Embedded non-negotiable security guardrails (e.g., keeping purge protection enabled, retaining WAF on public endpoints, and protecting critical log streams like NSG flow logs and Key Vault audits).
   - Specified a structured findings report format indicating exact files, lines, remediations, and estimated monthly savings.

2. **Parameterised Terraform Private Runner Module (`modules/terraform/azure-private-runner/v1/`):**
   - Added parameterized `runner_cpu` and `runner_memory` variables with strict description blocks and default values to `variables.tf` and `main.tf` to allow right-sizing of self-hosted runners.
   - Propagated these right-sizing variables to `templates/terraform/main.tf` and `templates/terraform/variables.tf`.

3. **Integrated `/optimise` slash command (`opencode.json`):**
   - Registered the `optimise` command in `opencode.json` and its template equivalent (`templates/opencode-config/opencode.json`), directing the agent to run a static cost optimization check, collaborate with the `@code-reviewer` and `@security-auditor` to ensure safety, and summon `@docs-writer` to generate the report.
   - Created `templates/docs/reports/cost-optimisation-template.md` as the standardized report template format.

4. **Updated Documentation (`AGENTS.md` & `templates/AGENTS.md`):**
   - Added the `optimise` skill and `/optimise` workflow to the central agents and workflows reference tables in both local and template AGENTS markdown files.

### Friction Points

- **Security vs. Cost Compromise:** A major risk in cost optimization is recommending downgrades that introduce security vulnerabilities (e.g., disabling Key Vault purge protection, shutting off the Application Gateway WAF to save on WAF_v2 licensing, or disabling security log streams). This was resolved by codifying strict security guardrails inside the `optimise` skill checklist—mandating that critical security features remain enabled regardless of environment-tier.
- **Parametrization & Typing Synchronization:** Synchronizing right-sizing parameters between Bicep (`runnerCpu`/`runnerMemory` with `@allowed` decorators) and Terraform (`runner_cpu`/`runner_memory` variables) required careful alignment to maintain strict input validation and compile-time type safety across both IaC dialects, preventing loose/untyped parameter definitions.

### Next Steps

- **Epic 2: Drift Detection Engine (`/drift`)** to identify out-of-band changes between live Azure resources and the declared IaC state.
- **Epic 3: Compliance Gating Engine (`/compliance`)** to enforce organization-specific Azure Policy and security baselines pre-deployment.

---

## Milestone: EU-Sovereignty Agentic Configuration Layer

**Date:** 2026-06-15

### Summary

This milestone executed a systematic refactor of the agentic configuration layer to achieve EU-sovereignty. We scanned and refactored the agentic configuration manifest (`manifest.yaml`) and implemented a robust Python configuration layer (`agent_config.py`) that enforces a strict `SECURITY_POLICY` requiring all Code-Generation and Task-Execution sub-agents to utilize EU-sourced models (Mistral API or local Ollama endpoints running codestral-24b or ministral-8b) by default. We also added a validation hook that logs the origin jurisdiction of every model used in the orchestration loop and triggers a critical alert/exception if a non-EU, non-authorized model is selected for a 'RESTRICTED' task.

### Changes Made

1. **Created `manifest.yaml` (EU-Sovereign Manifest):**
   - Defined active agents, roles, and model endpoints.
   - Replaced all non-EU model endpoints (US/China) with EU-sovereign alternatives (Mistral API or local Ollama endpoints running codestral-24b or ministral-8b).
   - Maintained Claude 4 as the authorized high-reasoning fallback for the orchestrator.

2. **Created `agent_config.py` (Sovereignty Policy Enforcement):**
   - Defined a strict `SECURITY_POLICY` constant that forces all 'Code-Generation' and 'Task-Execution' sub-agents to utilize EU-sourced models by default.
   - Implemented a validation hook that logs the origin jurisdiction of every model used in the orchestration loop.
   - Configured the validation hook to trigger a critical alert/exception if a non-EU, non-authorized model is selected for a 'RESTRICTED' task.
   - Added a self-test suite to verify policy enforcement, fallback handling, and restricted task validation.

### Friction Points

- **High-Reasoning Fallback Trade-off:** While EU-sovereignty is strictly enforced for Code-Generation and Task-Execution sub-agents, the orchestrator still relies on Claude 4 (US-based) as a high-reasoning fallback. This was accepted as a necessary trade-off for complex planning tasks, but is explicitly logged and monitored.

### Next Steps

- Integrate the `agent_config.py` validation hook directly into the main OpenCode orchestration loop.
- Explore hosting a local high-reasoning model (e.g., Mixtral-8x22B) to completely eliminate the US-based fallback dependency.

---

## Milestone: Sovereign-Friendly Model Migration & Verification

**Date:** 2026-06-15

### Summary

This milestone resolved critical model availability and data sovereignty issues across the agentic configuration layer. While the previous milestone configured agents to use EU-based models (`mistral/codestral-24b` and `ollama/ministral-8b`), these models are not available in the active OpenCode environment, and Ollama is not installed. This caused all subagents to fail. To restore full functionality while strictly avoiding Chinese-based models (such as DeepSeek, GLM/Big Pickle, or Xiaomi MiMo), we migrated all subagents to **`opencode/north-mini-code-free`** (Cohere's newly released North Mini Code model, which is a sovereign-friendly, non-US, non-Chinese model optimized for agentic coding and free on OpenCode).

### Changes Made

1. **Migrated Agent Configurations (`opencode.json` & `templates/opencode-config/opencode.json`):**
   - Updated all 10 subagents (builders, verifier, security-auditor, plan-validator, code-reviewer, explorer, test-writer, docs-writer) to use **`opencode/north-mini-code-free`**.
   - Maintained **`opencode/gemini-3.5-flash`** (US-based) as the authorized high-reasoning fallback for the orchestrator.

2. **Updated Sovereign Manifest (`manifest.yaml` & `templates/opencode-config/manifest.yaml`):**
   - Replaced unavailable Mistral and Ollama models with **`opencode/north-mini-code-free`** for all Code-Generation and Task-Execution subagents.
   - Mapped the orchestrator to **`opencode/gemini-3.5-flash`** as the authorized high-reasoning fallback.

3. **Updated Sovereignty Policy Enforcement (`agent_config.py` & `templates/opencode-config/agent_config.py`):**
   - Updated the `SECURITY_POLICY` constant to allow `Sovereign` jurisdictions (Canada/Cohere) alongside `EU` jurisdictions.
   - Mapped the default code generation and task execution models to `opencode/north-mini-code-free`.
   - Updated the validation hook and self-test suite to verify the new sovereign-friendly configurations.

4. **Verified Agent Functionality:**
   - Successfully ran the automated skill reference validator (`validate-skills.py`) to verify that all 22 prompt files have valid skill references.
   - Verified that `opencode.json` and `templates/opencode-config/opencode.json` are 100% valid JSON.
   - Successfully ran live agent orchestration tests using the OpenCode CLI to verify that the orchestrator and subagents are fully functional and executing tasks successfully.

### Friction Points

- **Sovereign Jurisdiction Scope:** While Cohere is Canadian-based and sovereign-friendly, it is technically non-EU. This required expanding the `allowed_jurisdictions` policy to include `Sovereign` alongside `EU` to keep the policy enforcement layer fully synchronized.
- **Orchestrator US-Dependency:** The orchestrator still relies on `opencode/gemini-3.5-flash` (US-based) as a high-reasoning fallback. This is a necessary trade-off for complex planning tasks but is explicitly logged and monitored.

### Next Steps

- Explore hosting a local high-reasoning model (e.g., Mixtral-8x22B or Llama-3-70B) to completely eliminate the US-based fallback dependency.
- Integrate the `agent_config.py` validation hook directly into the main OpenCode orchestration loop.

---

## Milestone: Model Optimization & Selection Engine

**Date:** 2026-06-15

### Summary

This milestone implemented the Model Optimization & Selection Engine, introducing a new skill (`model-optimiser`), an accompanying slash command (`/select-models`), and an interactive Python script (`scripts/select-models.py`) to select and configure optimized models for each agent based on jurisdiction, cost/quality focus, and local hardware capabilities. The engine is designed to work exclusively with the OpenCode ZEN provider and supports strict EU-sovereignty, EU+US, and Global model mappings, including local Ollama models for cost-sensitive environments.

### Changes Made

1. **Created `skills/model-optimiser/SKILL.md`** (and template equivalent):
   - Defined a structured workflow to verify the OpenCode ZEN provider, gather user preferences, map agent roles to optimized models, present a proposal, implement configurations, and run verification tests.
   - Codified a comprehensive Model Mapping Matrix covering EU, EU+US, and Global jurisdictions with Cost and Quality optimization focuses.

2. **Created `scripts/select-models.py`** (and template equivalent):
   - Developed a robust Python script that handles interactive and non-interactive model selection, proposal generation, configuration updates (for `opencode.json`, `manifest.yaml`, and `agent_config.py`), verification testing, and automatic rollback on failure.

3. **Registered `/select-models` slash command (`opencode.json`):**
   - Registered the `select-models` command in `opencode.json` and its template equivalent (`templates/opencode-config/opencode.json`), directing the orchestrator to run the model optimization workflow.

4. **Implemented Option 4 (EU Cost-Focused with Local Models):**
   - Successfully ran the optimization engine to configure the workspace for EU cost-focused operations using local Ollama models (`ollama/codestral:22b` and `ollama/mistral:7b`) on mid-range hardware.
   - Verified that all configuration files are syntactically valid and all self-tests passed.

5. **Updated Documentation (`AGENTS.md` & `templates/AGENTS.md`):**
   - Added the `model-optimiser` skill and `/select-models` command to the central agents, skills, and workflows reference tables.

### Friction Points

- **Local Model Runtime Dependency:** While local models are highly cost-effective and sovereign-friendly, they depend on a running Ollama instance on the operator's machine. If Ollama is not running or the specified models are not pulled, the subagents will fail. This is documented in the skill and handled gracefully by the rollback mechanism.

### Next Steps

- Integrate the `select-models` script into the scaffolding post-processor to allow operators to choose their model configuration during initial repository setup.
- Add automated checks to verify if local Ollama models are pulled and available before applying local model configurations.


---

## Milestone: Dynamic Model Discovery for the Selection Engine

**Date:** 2026-06-17

### Summary

This milestone replaced the static, hardcoded model-mapping matrix in the model-optimiser
engine with **live discovery and agent-driven selection**. The previous implementation pinned
model ids from a lookup table (e.g. `opencode/mistral-large-latest`, `ollama/mistral:latest`),
many of which do not exist in the active environment — directly reproducing the model-availability
failure mode recorded in `DISCOVERIES_LOG.md`. The engine now fetches the live OpenCode ZEN
catalog and the live Ollama catalog, and the orchestrator reasons over each agent's prompt and
skills to assign the optimal *available* model per agent.

### Changes Implemented

1. **Rewrote `scripts/select-models.py` into a discovery + apply tool** (and template equivalent):
   - `discover` subcommand: runs `opencode models opencode`, queries the Ollama `/api/tags`
     endpoint (with an `ollama list` fallback), scrapes live per-1M-token pricing from the ZEN
     docs page, infers each model's jurisdiction from its id prefix, filters to the chosen policy +
     local toggle, and prints a structured JSON catalog (each ZEN model annotated with
     `input_per_1m` / `output_per_1m`).
   - **Resilient pricing:** every successful scrape is cached to `scripts/.zen-pricing-cache.json`
     (gitignored). If a later fetch fails — the docs page is unreachable *or* its table layout
     changes so fewer than `MIN_EXPECTED_PRICES` parse — the catalog reports `pricing.status =
     "cached"` with the snapshot date and reason, and the skill clearly warns the user and asks
     whether to continue on the last-known pricing. With no cache at all it reports
     `pricing.status = "unavailable"` and offers to continue without cost figures.
   - `apply` subcommand: validates that every model in the agent-produced mapping actually exists
     in the live environment and is permitted under the policy *before* writing, then backs up,
     applies, runs verification tests, and rolls back on failure.
   - Removed the static `get_zen_*` / `get_local_task_model` lookup tables.

2. **Rewrote `skills/model-optimiser/SKILL.md`** to drive the agent: discover → read each agent's
   prompt/skills/role → reason out the best available model → propose → apply.

3. **Updated the `/select-models` command template** in `opencode.json` (and template equivalent)
   to describe the discover → reason → apply flow, and refreshed the README/AGENTS skill docs.

### Friction Points

- **EU cloud sparsity:** Live discovery revealed the active ZEN catalog currently exposes no
  Mistral models; under an EU policy the only cloud-eligible model is `north-mini-code-free`
  (classified Sovereign). This is exactly why availability must be discovered, not assumed — and
  why enabling local Ollama models is valuable for EU-sovereign cost-focused setups.

### Next Steps

- Live per-model pricing is now sourced by scraping the ZEN docs pricing tables
  (`https://opencode.ai/docs/zen/`), since neither `opencode models` nor the `/zen/v1/models`
  JSON endpoint exposes cost. If a structured pricing endpoint is published later, switch the
  `fetch_zen_prices()` scraper to consume it.

---

## Milestone: Agent Team Refactor — Self-Consistent Platform Team

**Date:** 2026-06-17

### Summary

This milestone executed the full `docs/agent-team-refactor-plan.md` refactor, making the agent team self-consistent, model-resilient, and unattended-capable. The refactor enforces the mandatory 9-stage lifecycle (`research → plan → build → verify → review → security → safety → test → docs`), installs fixed output contracts on every agent prompt, wires WAF pillar ownership explicitly, closes the template parity gap (generated repos were missing prompts and skills), and adds comprehensive team validation tooling.

### Changes Made

1. **All prompts — added explicit output contracts:**
   - `orchestrator.txt` → `## Milestone plan`
   - `explorer.txt` → `## Research summary`
   - `builder-*` → `## Build summary` (already present, confirmed)
   - `verifier.txt` → `Verification: PASSED|FAILED` (already present, confirmed)
   - `code-reviewer.txt` → `Quality gate: PASSED|FAILED`
   - `security-auditor.txt` → `Security gate: PASSED|FAILED` (already present, confirmed)
   - `plan-validator.txt` → `Plan safety gate: PASSED|FAILED` (corrected from "Plan gate:")
   - `test-writer.txt` → `## Test summary`
   - `docs-writer.txt` → `## Documentation summary`

2. **`orchestrator.txt` — rewrote to enforce mandatory lifecycle:**
   - Added explicit `## Mandatory lifecycle` section with the 9-stage sequence
   - Added `## Output contract` section requiring `## Milestone plan` output
   - Added `## WAF ownership` section mapping all 5 WAF pillars to owning agents
   - Removed ghost reference to "session-tracking sections in AGENTS.md"

3. **`code-reviewer.txt` — expanded WAF coverage:**
   - Added Reliability/Availability pillar (soft-delete, retry, availability zones, `prevent_destroy`)
   - Added Performance Efficiency pillar (SKU sizing, autoscale)
   - Added Cost Optimization pillar (oversized SKUs, `optimise` skill invocation)
   - Added Operational Excellence pillar (diagnostic settings, tagging)
   - Existing Maintainability & Correctness pillar retained

4. **`docs-writer.txt` — removed ghost reference:**
   - Removed "session-tracking sections in `AGENTS.md`" (these sections do not exist)

5. **`root AGENTS.md` — fixed stale references:**
   - Added `explorer` agent entry with output contract
   - Added `test-writer` and `docs-writer` agent entries with output contracts
   - Updated `workflows/` section to correctly describe it as documentation-only; commands are in `opencode.json → command`
   - Fixed "Adding new content" table entry from `opencode.json → workflows[]` to `opencode.json → command[name]`
   - Added `validate-team.py` to development commands

6. **`workflows/scaffold.md` — rewrote stale workflow doc:**
   - Removed references to nonexistent `architect` and `platform-engineer` agents
   - Now correctly references `orchestrator` and `security-auditor`
   - Documents actual `scripts/scaffold.py` backend and scaffold template copy paths

7. **`templates/opencode-config/prompts/`** — created (was missing):
   - All 11 agent prompt `.txt` files copied; generated repos now have the full agent team

8. **`templates/opencode-config/skills/`** — created (was missing):
   - 13 skill directories copied (excluding `scaffold` which generated repos don't need)
   - Generated repos now have the full skill set under `.opencode/skills/`

9. **`templates/opencode-config/scripts/`** — created (was missing):
   - `validate-skills.py` and `select-models.py` copied; referenced scripts now exist in template

10. **`scripts/scaffold.py`** — added `select-models.py` to copy list:
    - Generated repos now receive `scripts/select-models.py` (required by `/select-models` command)

11. **`templates/AGENTS.md`** — complete rewrite:
    - All 11 agents documented with output contracts
    - Mandatory 9-stage lifecycle table added
    - WAF ownership table added
    - Commands section corrected (uses `command` not `workflows[]`)

12. **`scripts/validate-team.py`** — new comprehensive validator:
    - Check 1: JSON validity for root and template `opencode.json`
    - Check 2+3: Every agent has an existing prompt file; every prompt is referenced by an agent
    - Check 4: Every skill referenced in a prompt resolves to an existing skill file
    - Check 5: Every command references an existing agent
    - Check 6: Root and template agent topologies match
    - Check 7: `AGENTS.md` documents all configured agents
    - Check 8: No orphan skills (command-invoked skills counted via template text scan)

### Validation Results

```
python3 -m json.tool opencode.json             → valid
python3 -m json.tool templates/opencode-config/opencode.json  → valid
python3 scripts/validate-skills.py            → 0 broken skill references (22 files scanned)
python3 scripts/validate-team.py              → ✅ All checks passed!
python3 agent_config.py                       → all self-tests passed
```

### Friction Points

- **Template prompt redundancy:** Template prompts are copies of root prompts. They will drift over time. The current approach is intentional (generated repos are self-contained) but requires updating templates whenever root prompts change. `validate-team.py` check 6 (topology parity) catches agent-level drift but not content drift.
- **Skill `scaffold` excluded from templates:** The `scaffold/SKILL.md` was deliberately excluded from `templates/opencode-config/skills/` since generated repos have no `/scaffold` command. The root `skills/scaffold/` remains for the platform repo's own use.

### Next Steps

- Wire `validate-team.py` into CI (`.github/workflows/ci.yml`) as a required pre-merge check
- Consider a content-level diff check between root and template prompts to catch semantic drift earlier
