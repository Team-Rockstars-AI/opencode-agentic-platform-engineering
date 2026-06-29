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

---

## Milestone: Security Audit Remediation & Hardening (June 2026)

### 🔍 Discoveries
*   **Implicit Environment Access:** Pipeline templates that use a single set of credentials or service connections across all branches/stages create a risk of accidental cross-environment access (e.g., a dev branch deploying to a prod subscription).
*   **Bicep Type Safety Gaps:** Using `any()` in Bicep templates bypasses compile-time type checking, which can mask configuration errors and lead to runtime deployment failures.
*   **PAT Rotation Burden:** Accepting a GitHub Personal Access Token (PAT) for self-hosted runner registration creates a manual rotation burden and security risk compared to auto-rotating GitHub App installation tokens.

### ⚠️ Findings
*   **Single Credential Set in Pipelines:** Both GitHub Actions and Azure DevOps templates used a single set of credentials/service connections, lacking explicit environment-specific isolation.
*   **Bicep `any()` Bypass:** The private runner module used `any('1.0')` for the container CPU resource, bypassing Bicep's type system.
*   **PAT Rotational Risk:** The private runner modules accepted a PAT for runner registration without explicitly documenting the preferred GitHub App-based approach.

### 💡 Solutions
*   **Environment-Specific Pipeline Isolation:**
    - **GitHub Actions:** Configured the `validate` job to dynamically target the `development` or `production` environment based on the branch, and bound the `deploy` job explicitly to the `production` environment.
    - **Azure DevOps:** Removed the global `azureServiceConnection` variable and defined it at the stage level, using `'sc-{{project_name}}-dev-deploy'` for validation and `'sc-{{project_name}}-prod-deploy'` for deployment.
*   **Strongly-Typed Bicep Parameters:** Added parameterized `runnerCpu` and `runnerMemory` variables with strict `@allowed` decorators, replacing the `any()` bypass with strongly-typed parameters.
*   **GitHub App-Based Runner Registration Documentation:** Expanded the variable descriptions across all modules and templates to explicitly document the GitHub App-based runner registration approach as the preferred, secure, and auto-rotating path.

---

## Milestone: EU-Sovereignty Agentic Configuration Layer (June 2026)

### 🔍 Discoveries
*   **Geopolitical Compliance Risks:** Relying on non-EU model endpoints (specifically those in China or the US) for sensitive platform engineering tasks introduces geopolitical compliance risks and potential violations of EU data sovereignty regulations (such as GDPR, DORA, and BIO).
*   **Sovereign Model Alternatives:** High-quality EU-sourced models (such as Mistral API via Le Chat/Mistral Enterprise or local Ollama endpoints running codestral-24b or ministral-8b) provide excellent sovereign alternatives for code generation and task execution.

### ⚠️ Findings
*   **Non-EU Model Dependencies:** Active agent configurations and manifests contained references to non-EU model endpoints (such as DeepSeek based in China, or Gemini/Claude based in the US).
*   **Lack of Jurisdiction Enforcement:** No mechanism existed to enforce model jurisdiction policies or alert operators when a non-EU model was selected for restricted tasks.

### 💡 Solutions
*   **EU-Sovereign Manifest (`manifest.yaml`):** Created a centralized agentic configuration manifest that maps all active sub-agents to EU-sovereign model endpoints (Mistral API and local Ollama endpoints) while maintaining Claude 4 as an authorized high-reasoning fallback for the orchestrator.
*   **Sovereignty Policy Enforcement (`agent_config.py`):** Implemented a robust Python configuration layer with a strict `SECURITY_POLICY` constant that automatically overrides non-EU models for Code-Generation and Task-Execution roles with EU-sovereign defaults.
*   **Jurisdiction Validation Hook:** Added a validation hook that logs the origin jurisdiction of every model used in the orchestration loop and triggers a critical alert/exception if a non-EU, non-authorized model is selected for a 'RESTRICTED' task.

---

## Milestone: Sovereign-Friendly Model Migration & Verification (June 2026)

### 🔍 Discoveries
*   **Model Availability Gaps:** Configuring agents to use models that are not available in the active OpenCode environment (such as `mistral/codestral-24b` or `ollama/ministral-8b` when Ollama is not installed) breaks the entire agentic orchestration loop.
*   **Sovereign-Friendly Alternatives:** Cohere's newly released **North Mini Code** (`opencode/north-mini-code-free`) is a highly capable, sovereign-friendly (Canadian-based, Apache 2.0), non-US, non-Chinese model that is available and free on OpenCode, making it the perfect engine for subagent code generation and task execution.

### ⚠️ Findings
*   **Broken Agent Loop:** All subagents were configured to use unavailable Mistral and Ollama models, causing immediate `ProviderModelNotFoundError` and connection failures.
*   **Chinese Model Risks:** Historical recommendations in `.opencode/memory.md` suggested Chinese-based models (such as DeepSeek, GLM/Big Pickle, and Xiaomi MiMo), which violate strict data sovereignty requirements.

### 💡 Solutions
*   **Sovereign-Friendly Migration:** Migrated all subagents in `opencode.json` and `manifest.yaml` (both root and templates) to use **`opencode/north-mini-code-free`** (Cohere North Mini Code), restoring 100% functionality to the agent team.
*   **Orchestrator Alignment:** Maintained **`opencode/gemini-3.5-flash`** (US-based) as the authorized high-reasoning fallback for the orchestrator.
*   **Sovereignty Policy Update:** Updated `agent_config.py` to allow `Sovereign` jurisdictions (Canada/Cohere) alongside `EU` jurisdictions, keeping the policy enforcement layer fully synchronized.
*   **Automated Verification:** Successfully ran the automated skill reference validator (`validate-skills.py`), JSON syntax checks, and live agent orchestration tests to verify that the entire team is fully functional.

---

## Milestone: Model Optimization & Selection Engine (June 2026)

### 🔍 Discoveries
*   **Dynamic Model Optimization:** Hardcoding model configurations in `opencode.json` and `manifest.yaml` prevents operators from easily adapting their agent team to changing cost, quality, and sovereignty requirements.
*   **Local Model Cost Savings:** Utilizing local Ollama models (such as `ollama/codestral:22b` and `ollama/mistral:7b`) on mid-range or high-end hardware can completely eliminate cloud API costs for high-volume subagent tasks (code generation, verification, auditing) while maintaining strict data sovereignty.

### ⚠️ Findings
*   **Lack of Model Flexibility:** No mechanism existed to easily switch between EU-sovereign, EU+US, and Global model configurations, or to integrate local models based on the operator's hardware capabilities.
*   **Manual Configuration Overhead:** Manually updating model IDs, endpoints, and jurisdictions across `opencode.json`, `manifest.yaml`, and `agent_config.py` is highly error-prone and can easily break the agent orchestration loop.

### 💡 Solutions
*   **Model Optimiser Skill (`skills/model-optimiser/SKILL.md`):** Authored a new skill and template equivalent that codifies a comprehensive Model Mapping Matrix covering EU, EU+US, and Global jurisdictions with Cost and Quality optimization focuses.
*   **Interactive Selection Script (`scripts/select-models.py`):** Developed a robust Python script that handles interactive and non-interactive model selection, proposal generation, configuration updates, verification testing, and automatic rollback on failure.
*   **Slash Command Integration (`/select-models`):** Registered the `select-models` command in `opencode.json` and its template equivalent, directing the orchestrator to run the model optimization workflow.
*   **EU Cost-Focused Implementation:** Successfully ran the optimization engine to configure the workspace for EU cost-focused operations using local Ollama models (`ollama/codestral:22b` and `ollama/mistral:7b`) on mid-range hardware, verifying that all configuration files are syntactically valid and all self-tests passed.

---

## Milestone: Dynamic Model Discovery (June 2026)

### 🔍 Discoveries
*   **Static matrices drift from reality:** The hardcoded model-mapping matrix referenced ZEN ids that are not in the live catalog (e.g. `opencode/mistral-large-latest`, `opencode/codestral-latest`) and Ollama ids that are not installed (`ollama/mistral:latest`). The active ZEN catalog (`opencode models opencode`) exposes 45 models and, at the time of writing, **no Mistral models**.
*   **Live Ollama metadata is richer via HTTP:** The Ollama `/api/tags` endpoint returns `details.parameter_size`, enabling hardware-tier matching that `ollama list` alone cannot provide.

### ⚠️ Findings
*   **Availability must be enforced at apply time:** Trusting an agent-proposed mapping without re-checking the live environment can silently re-introduce the model-availability breakage that takes down the entire orchestration loop.

### 💡 Solutions
*   **Discovery + apply split (`scripts/select-models.py`):** The script now only fetches live catalogs (`discover`) and validates + writes a mapping (`apply`); selection reasoning moved to the orchestrator agent via the rewritten `model-optimiser` skill.
*   **Prefix-based jurisdiction inference:** Model jurisdiction is inferred from the id prefix (mistral→EU, claude/gpt/gemini→US, cohere/north→Sovereign, deepseek/glm/qwen/minimax→Global), with unknown ids defaulting to Global so they can never leak into an EU-only configuration.
*   **Hard availability guard:** `apply` rejects any mapping whose models are absent from the freshly discovered ZEN/Ollama catalogs, and rolls back on any verification failure.

---

## Milestone: Automated Drift Detection & Reconciliation Engine (June 2026)

### 🔍 Discoveries
*   **Structured vs. Unstructured Plan Data:** Terraform provides a robust, machine-readable JSON representation of its execution plan (`terraform show -json`), which is ideal for automated drift analysis. In contrast, Bicep's `what-if` output is primarily designed for human consumption, requiring more complex regex-based parsing to isolate drifted properties.
*   **Drift Classification is Context-Dependent:** Not all drift is equal. Manual tag updates are often benign, while changes to NSG rules or Public IP configurations are critical security regressions. A structured classification system (Benign, Operational, Critical) is essential for prioritizing reconciliation efforts.

### ⚠️ Findings
*   **Stateful Resource Vulnerability:** Drift reconciliation workflows can accidentally trigger resource replacement (destruction and recreation) if the IaC change required to sync with live state is considered a "replacement" action by the provider. This is unacceptable for stateful resources like databases or Key Vaults.
*   **Security Regression Visibility:** Manual "clickops" changes often bypass standard security gates, potentially introducing vulnerabilities that remain hidden until the next full deployment or audit.

### 💡 Solutions
*   **Drift Detection Engine (`/drift`):** Implemented a coordinated workflow that orchestrates the `@verifier` to generate plans, the `@plan-validator` to parse and classify drift, and the `@security-auditor` to flag security regressions.
*   **Drift Skill (`skills/drift/SKILL.md`):** Authored a new skill that codifies drift classification rules and enforces strict safety gates, ensuring that reconciliation guidance never defaults to resource replacement for stateful components.
*   **Actionable Reconciliation Guidance:** The engine produces a structured `DRIFT_REPORT.md` (based on a new template) that provides the exact `terraform import` commands or Bicep parameter updates needed to sync the IaC state with reality, reducing manual remediation effort.
*   **Static Validation & Mock Testing:** Verified the parsing and classification logic using mock plan JSONs to ensure reliability before live Azure subscription testing.

---

## Milestone: Azure DevOps Canonical CI (June 2026)

### 🔍 Discoveries
*   **Dual-Platform Visibility:** Maintaining a GitHub mirror is essential for public visibility and community engagement, but using it as the primary CI/CD host can conflict with internal enterprise standards that mandate Azure DevOps for authoritative platform governance.
*   **Static-Only CI Resilience:** Decoupling the root-level CI pipeline from Azure environment access (no login, no plan/apply) provides a robust, low-privilege safety net that validates code quality and security compliance without requiring complex OIDC bootstrap or secret management for the main repository itself.

### ⚠️ Findings
*   **Lack of Authoritative CI:** Prior to this milestone, the repository relied on GitHub Actions for CI, which did not align with the "Azure-first" platform engineering philosophy and lacked an authoritative presence in the canonical Azure DevOps environment.
*   **Mirroring Ambiguity:** Without explicit documentation, contributors might push directly to the GitHub mirror, leading to branch divergence and bypassing the authoritative Azure DevOps governance flow.

### 💡 Solutions
*   **Azure DevOps Canonicalization:** Established Azure DevOps as the canonical git host and CI platform, with GitHub maintained as a manually updated mirror.
*   **Root-Level ADO CI (`azure-pipelines.yml`):** Implemented a root-level Azure DevOps pipeline that performs authoritative static validation (Python linting, config validation, Terraform/Bicep linting, secret scanning, and SAST) on every commit.
*   **Governance Documentation:** Updated `AGENTS.md` to explicitly define the dual-platform relationship and mandate that all changes flow through Azure DevOps, ensuring the GitHub mirror remains a read-only reflection of the authoritative source.

---

## Milestone: Regulatory Compliance Mapping Engine (June 2026)

### 🔍 Discoveries
*   **Regulatory-Technical Gap:** There is often a significant gap between high-level regulatory requirements (DORA, BIO, GDPR) and the technical configurations in IaC. Bridging this gap requires a codified mapping matrix that translates technical controls into regulatory articles.
*   **Continuous Audit Readiness:** Moving from point-in-time audits to continuous compliance mapping reduces the "compliance tax" on engineering teams and provides immediate visibility into the regulatory impact of infrastructure changes.

### ⚠️ Findings
*   **Manual Mapping Overhead:** Manually mapping every NSG rule or Key Vault setting to a regulatory article is time-consuming and prone to error, especially as infrastructure scales.
*   **Lack of Auditor-Ready Artifacts:** While the platform was "secure-by-design," it lacked a single, automated artifact that could be presented to an auditor to prove compliance across multiple frameworks.

### 💡 Solutions
*   **Compliance Mapping Engine (`/compliance`):** Implemented a coordinated workflow that maps technical findings from `@security-auditor` and `@code-reviewer` directly to DORA, BIO, and GDPR articles.
*   **Codified Mapping Matrix:** Authored the `compliance` skill which contains the source-of-truth mapping between Azure resource configurations and regulatory articles.
*   **Automated Readiness Reporting:** Created a structured `COMPLIANCE_READINESS_REPORT.md` template that provides an executive summary and a detailed regulatory control matrix, significantly reducing audit preparation effort.
*   **Architecture Decision Record (ADR 0006):** Formalized the decision to implement continuous regulatory mapping as a core platform capability.

---

## Milestone: Agent Team Packs & Model Profiles (June 2026)

### 🔍 Discoveries
*   **Combinatorial Complexity:** Manually selecting and balancing models for a multi-agent team (considering cost, quality, and jurisdiction) creates significant cognitive load and brittle configurations.
*   **Need for Presets:** Platform engineers require "known good" configurations (Team Packs) that can be easily shared, versioned, and applied across different projects or environments.

### ⚠️ Findings
*   **Brittle Configurations:** Manually tuned agent teams are difficult to reproduce and upgrade safely, leading to inconsistencies across the platform.
*   **Policy Enforcement Gaps:** While `agent_config.py` enforces jurisdiction, there is no high-level mechanism to bundle these policies with specific agent/model combinations.

### 💡 Solutions
*   **Agent Team Packs:** Introduced the concept of versioned manifests (`pack.yaml`) that bundle agents, models, prompts, and policies into sharable presets.
*   **Layered Selection Logic:** Designed packs to work on top of the existing `/select-models` discovery engine, providing the strategic blueprint while maintaining dynamic resilience.
*   **Lifecycle Management:** Defined core operations (`pack list`, `pack apply`, `pack validate`) to manage the lifecycle of agent configurations.
*   **ADR 0007:** Formalized the decision to implement Team Packs to standardize agent environments and reduce operational complexity.

### 📝 Narrative Summary
Layering static team pack blueprints over the dynamic model discovery engine (`select-models.py`) proved to be a critical architectural breakthrough. By separating the strategic intent (the "blueprint" in `pack.yaml`) from the tactical availability (the live ZEN/Ollama catalogs), we achieved a resilient and governed model configuration system. This approach allows platform engineers to define "known good" agent teams that automatically adapt to the specific models available in a given environment while strictly enforcing sovereignty and cost policies, effectively eliminating the "model not found" failures that previously plagued the orchestration loop. Codifying the full lifecycle (discover → select → apply → validate → share) ensures that packs are not just static files, but active, governed components of the platform's security and operational posture. The subsequent documentation hardening pass further matured the system by clarifying the trade-offs between cost and reasoning quality in the default packs and establishing a clear, governed workflow for pack authorship and contribution. The final implementation of validation and export workflows (Milestone 4.3) completed the cycle, providing operators with the tools to verify pack health against live catalogs and snapshot successful configurations into new, versioned assets, thereby ensuring that the platform's agentic intelligence remains both portable and verifiable.

---

## Milestone: Pack Validation, Export & Sharing (June 2026)

### 🔍 Discoveries
*   **Dry-Run Validation Value:** Validating a pack against the live environment *before* application is essential for preventing orchestration failures. It allows operators to identify missing models or policy violations without risking the stability of the current agent team.
*   **Configuration Capture:** Manually authoring `pack.yaml` manifests is tedious and error-prone. Capturing the active, verified configuration directly from the workspace (`opencode.json`, `manifest.yaml`, `agent_config.py`) is the most reliable way to create new, "known good" presets.

### ⚠️ Findings
*   **Stale Presets:** Without a validation mechanism, shipped packs can easily become stale as model catalogs evolve (e.g., a model is deprecated or renamed in ZEN).
*   **Sharing Friction:** The lack of an export mechanism created a high barrier to entry for sharing successful agent configurations, limiting the growth of the platform's preset ecosystem.

### 💡 Solutions
*   **Live Validation Engine:** Implemented `pack validate`, which performs a live discovery of model catalogs and verifies pack compatibility against both availability and jurisdiction policies.
*   **Automated Export Engine:** Implemented `pack-create-from-current`, which captures the active agent/model configuration and automatically generates a versioned `pack.yaml` manifest.
*   **Dual-Tree Export:** Configured the export engine to write to both the local `packs/` directory and the `templates/` tree, ensuring that new presets are immediately available for both the current project and future scaffolded repositories.

### 📝 Narrative Summary
The final documentation hardening pass focused on refining the platform's entry-point experience, ensuring that the root `README.md` clearly communicates the repository's dual nature as both a generator and a governed operational environment. By explicitly defining the 'repo that stamps other repos' paradigm and elevating the visibility of the Agent Team Packs ecosystem, we've reduced the cognitive load for new operators and provided a clear map of the platform's advanced automation capabilities. This alignment between technical implementation and documentation ensures that the platform's sophisticated multi-agent orchestration and regulatory mapping features are immediately discoverable and actionable for teams operating under high-compliance mandates.
