# Platform Engineering — Discoveries, Findings & Solutions Log

This log serves as a persistent, in-project memory of discoveries, findings, and solutions identified during the platform's development. It is designed to help both human and agentic engineers understand the build process, trace architectural decisions, and prevent the repetition of earlier mistakes.

---

## Milestone: Formalised Reusable Skills Framework (June 2026)

### 🔍 Discoveries
*   **Scattered Workflow Rules:** Scattered workflow rules across individual agent prompt files create structural drift, duplicate instructions, and make it difficult to maintain a single source of truth.
*   **Implicit Skills:** Operational procedures (such as branch naming, commit hygiene, and security checklists) are better managed as first-class, version-controlled, and discoverable abstractions rather than implicit prompt instructions.

### ⚠️ Findings
*   **No Single Source of Truth:** No single source of truth existed for branch naming, commit hygiene, or security checklists, leading to inconsistent agent behaviors and manual review overhead.
*   **Prompt Duplication:** Duplication of workflow rules between root prompts and template prompts increased maintenance complexity and the risk of configuration drift.

### 💡 Solutions
*   **Reusable Skills Framework:** Extracted operational procedures into dedicated `skills/<name>/SKILL.md` files, each with a standard frontmatter header, a trigger description, a step-by-step procedure, and a defined output format.
*   **Flagship Skills:** Authored the `security-checklist` skill (distilling eight hard-block security criteria into a structured PASS/FAIL/NA checklist) and the `git-workflow` skill (enforcing consistent branch naming, pre-commit hygiene, and commit blacklist rules).
*   **Skill Delegation:** Retrofitted the `audit` skill to load `security-checklist` and updated builder prompts (`builder-infra-tf`, `builder-infra-bicep`, `builder-pipelines`) to delegate workflow rules to the `git-workflow` skill.

---

## Milestone: Complete Reusable Skills Framework & Prompt Reconciliation (June 2026)

### 🔍 Discoveries
*   **Manual Reconciliation Friction:** Manual prompt reconciliation is highly error-prone and leads to structural drift between master prompts (`.opencode/prompts/`) and template prompts (`templates/opencode-config/prompts/`).
*   **Orphaned References:** Prompt files can easily accumulate broken or orphaned skill references (e.g., "load the X skill" when `X` does not exist) if not validated automatically.

### ⚠️ Findings
*   **Unwritten Skills:** Several skills (such as `code-standards` and `commit-format`) were referenced by name in agent prompts but did not exist as standalone files.
*   **Prompt Drift:** Significant structural drift had accumulated between the master prompts and the template prompts, leading to inconsistent agent capabilities.

### 💡 Solutions
*   **Skills Completion:** Authored the six remaining skills: `code-standards` (codifying CAF naming, Azure WAF five-pillar alignment, and IaC best practices), `commit-format` (standardising Conventional Commits), `architecture-review` (subscription topology and network isolation), `plan-tracking` (execution plan conversion), `doc-standards` (module README and ADR guidelines), and `test-patterns` (Terraform 1.6+ and Bicep testing patterns).
*   **Prompt Alignment:** Performed a comprehensive reconciliation pass to align master prompts with their template counterparts, ensuring both trees reference the same skills.
*   **Automated Validation:** Introduced `scripts/validate-skills.py` to scan all prompt files for skill references and verify that each referenced skill exists under `skills/`, gating the CI pipeline on failures.

---

## Milestone: Security Remediation & Hardening (June 2026)

### 🔍 Discoveries
*   **Over-Privileged Defaults:** Using broad, built-in roles like `Contributor` and `User Access Administrator` at the subscription scope for pipeline identities is a severe privilege-escalation vector and violates the Principle of Least Privilege (PoLP).
*   **Default Public Exposure:** Azure resources (such as Key Vaults) and subnets are deployed with public network access enabled and no subnet-level access controls by default, requiring explicit secure-by-design overrides.

### ⚠️ Findings
*   **Subscription-Scoped Contributor + User Access Admin:** The pipeline identity was granted both roles at subscription scope, allowing unrestricted control and privilege escalation.
*   **Key Vault Public Exposure:** The Key Vault module lacked network isolation and had purge protection disabled by default.
*   **Missing Subnet-Level Controls:** The virtual network and subnets were deployed without any Network Security Groups (NSGs), allowing unrestricted lateral movement.
*   **Silent Pipeline Failures:** Pipeline templates lacked strict error propagation, allowing intermediate command failures to go unnoticed.

### 💡 Solutions
*   **Custom Least-Privilege Roles:** Replaced subscription-scoped `Contributor` and `User Access Administrator` with a custom, scoped role (`custom-pipeline-deployer-*`) granting only required actions.
*   **Key Vault Hardening:** Enabled purge protection, disabled public network access, and configured default-deny network ACLs (`bypass = "AzureServices"`, `default_action = "Deny"`) in the Key Vault module.
*   **Subnet Micro-segmentation:** Deployed four dedicated NSGs associated with each subnet, and added a security rule to the endpoints NSG restricting inbound HTTPS traffic exclusively to the workloads subnet prefix.
*   **Strict Error Propagation:** Standardised all pipeline script blocks to use `set -euo pipefail` to ensure immediate failure propagation.
*   **Parameterized HTTPS:** Added an optional `ssl_certificate_key_vault_secret_id` parameter to the Application Gateway to dynamically provision HTTPS listeners and SSL bindings only when provided.

---

## Milestone: Optimal Platform Hardening & Micro-segmentation (June 2026)

### 🔍 Discoveries
*   **Built-in Role Hard Blocks:** Even when scoped to a single resource group, assigning the built-in `Contributor` role to a pipeline service principal violates the security baseline because it still grants broad write permissions and data-plane access.
*   **Bicep Child Resource ID Scope:** In Bicep, referencing `${vnet.id}` for Application Gateway child resources (listeners, ports, routing rules) is incorrect and causes runtime deployment failures because these are child resources of the Application Gateway, not the VNet.
*   **Template Wiring Gaps:** Having diagnostic settings inside reusable modules is useless if the template-level compositions do not pass the `log_analytics_workspace_id` / `logAnalyticsWorkspaceId` parameters to wire them up.

### ⚠️ Findings
*   **Resource-Group-Scoped Contributor:** The pipeline identity still held the built-in `Contributor` role, violating the security baseline.
*   **Bicep App Gateway Resource ID Bug:** Incorrect resource ID references in `main.bicep` would cause runtime deployment failures.
*   **Unwired Diagnostics:** Diagnostic settings inside the network and runner modules were never created because the templates failed to pass the Log Analytics workspace ID.
*   **Missing Input Validation:** Several modules and template variables lacked input validation blocks and parameter decorators, allowing invalid inputs to pass planning.

### 💡 Solutions
*   **Custom Least-Privilege Roles (No listKeys):** Replaced the built-in `Contributor` role with custom least-privilege roles and removed the `listKeys/action` permission to enforce strict Entra ID data-plane authentication.
*   **Bicep Resource ID Fix:** Defined a local variable `appGatewayId` prefix to correctly construct child resource IDs, completely resolving the runtime deployment bug.
*   **Wired Diagnostics:** Passed the Log Analytics workspace ID from the templates to the network and runner modules, successfully enabling diagnostic settings for the Application Gateway, all four NSGs, the Container App Environment, and the Container App.
*   **Comprehensive Input Validation:** Added robust `validation {}` blocks to all remaining Terraform variables and matching `@minLength`, `@maxLength`, `@allowed`, and `@secure` decorators to all Bicep parameters across all modules and templates.
*   **90-Day Soft-Delete Retention:** Increased Key Vault soft-delete retention from 7 days to 90 days across all modules and templates to align with the Microsoft Cloud Security Benchmark.

---

## Milestone: High-Value Provisioning System Enhancements (June 2026)

### 🔍 Discoveries
*   **Manual Scaffolding Overhead:** Manual template copying is slow, error-prone, and token-expensive for agentic workflows. An automated, zero-dependency script is the optimal solution.
*   **Pre-Commit Hook Location:** Pre-commit hooks must reside in the **root** of the git repository (`.pre-commit-config.yaml`) to work out of the box. Placing them inside `terraform/` or `bicep/` subdirectories prevents them from being discovered.
*   **Architecture Traceability:** Newly scaffolded repositories benefit immensely from pre-populated Architecture Decision Records (ADRs) to establish immediate governance and document the "why" behind the platform's security choices.

### ⚠️ Findings
*   **No Executable Scaffolder:** Scaffolding was purely descriptive, relying on the agent to manually copy files and replace placeholders.
*   **No Local Compliance Enforcement:** No pre-commit hooks existed to scan for secrets or run SAST compliance checks locally before commits.
*   **No Architecture Decision Trail:** Scaffolded repositories lacked documented architectural decisions, requiring manual knowledge transfer.

### 💡 Solutions
*   **Automated Scaffolding Script (`scripts/scaffold.py`):** Authored a self-contained, zero-dependency Python script supporting both interactive CLI wizard and non-interactive CLI modes. It automates copying templates, copying modules (making the repo completely self-contained), performing placeholder substitutions, correcting relative paths, and initializing git.
*   **Pre-Commit Hook Configurations:** Created `.pre-commit-config.yaml` configurations for both Terraform and Bicep templates (enforcing standard hygiene, Gitleaks secret scanning, Checkov SAST, and Terraform formatting/validation). The scaffolding script automatically moves the correct config to the repository root.
*   **Pre-Populated ADRs:** Created five core ADRs under `templates/docs/adr/` (documenting ADR practice, OIDC federation, Private Endpoints, NSG micro-segmentation, and self-hosted runners) which are automatically copied to the target repository root during scaffolding.
