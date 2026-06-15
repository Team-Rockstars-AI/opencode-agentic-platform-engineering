# Provisioned Platform Operator Manual (The Generated Workspace)

Welcome to the Operator Manual for your **Provisioned Azure Platform Engineering Workspace**. This manual describes how to operate, maintain, and expand your newly generated repository using the integrated OpenCode multi-agent team and secure-by-design workflows.

---

## 1. Introduction & Purpose

Your provisioned repository is a fully independent, secure-by-design workspace configured to manage your live Azure workloads. It enforces strict compliance with European and Dutch regulatory baselines (such as **GDPR, DORA, BIO, and NEN 7510**) by combining secure infrastructure blueprints with an automated, read-only verification gate system.

---

## 2. Repository Structure

Your generated repository contains the following core directories and files:

```text
├── terraform/ or bicep/     # Landing zone skeletons and deployment environments
├── .github/ or pipelines/   # OIDC-federated, passwordless CI/CD pipelines
├── .opencode/               # Local agent team configuration, prompts, and skills
│   ├── prompts/             # Specialized system prompts for each subagent
│   ├── skills/              # Codified operational procedures (skills)
│   └── opencode.json        # Central agentic configuration manifest
├── docs/
│   └── adr/                 # Pre-populated Architecture Decision Records (ADRs 0001-0005)
├── .pre-commit-config.yaml  # Local compliance hooks (Gitleaks, Checkov, formatters)
└── AGENTS.md                # Root-level agent operations guide
```

---

## 3. Prerequisites for the Operator

To operate the provisioned workspace, ensure you have the following tools set up:

1.  **OpenCode CLI:** Connected to OpenCode Zen:
    ```bash
    opencode connect --provider zen
    ```
2.  **Azure CLI (`az`):** Authenticated to your Azure subscription:
    ```bash
    az login
    ```
3.  **Git:** Configured with your developer identity:
    ```bash
    git config --global user.name "Your Name"
    git config --global user.email "your.email@company.com"
    ```

---

## 4. Multi-Agent Operations Topology

Your workspace utilizes an **Orchestration-Led multi-agent paradigm** optimized for secure platform-engineering operations. The team consists of 11 specialized agents configured to run on cost-effective, sovereign-friendly models:

*   **`orchestrator`** (`opencode/gemini-3.5-flash`): The strategic lead. Parses requirements, reviews the backlog, and delegates tasks to builders.
*   **`builder-infra-tf`** (`opencode/north-mini-code-free`): Authors secure, modular, parameterized Terraform resources.
*   **`builder-infra-bicep`** (`opencode/north-mini-code-free`): Authors multi-scope Bicep templates.
*   **`builder-pipelines`** (`opencode/north-mini-code-free`): Configures OIDC-federated automated workflows.
*   **`verifier`** (`opencode/north-mini-code-free`): Compiles code (`terraform validate` / `bicep build`) and generates dry-run logs.
*   **`security-auditor`** (`opencode/north-mini-code-free`): Audits configurations for compliance and security gaps.
*   **`plan-validator`** (`opencode/north-mini-code-free`): **Blast Radius Valve.** Scans plan logs and blocks destruction of critical resources.
*   **`code-reviewer`** (`opencode/north-mini-code-free`): Reviews code naming conventions and tagging rules.
*   **`explorer`** (`opencode/north-mini-code-free`): Traces dependencies and indexes local directories.
*   **`test-writer`** (`opencode/north-mini-code-free`): Writes unit and integration tests (`.tftest.hcl`).
*   **`docs-writer`** (`opencode/north-mini-code-free`): Maintains markdown runbooks, variables tables, and ADRs.

---

## 5. Operational Slash Commands

You can interact with your multi-agent platform team directly from the OpenCode terminal using these four custom slash commands:

### 1. `/audit` (Compliance Scanning)
*   **Purpose:** Scans your entire workspace (IaC templates, subnets, NSGs, and pipelines) for credential leaks, compliance defects, and network isolation failures.
*   **How it works:** Launches the `security-auditor` agent, which loads the `security-checklist` skill. It scans for raw secrets, public endpoints, and missing diagnostic logs, producing a structured PASS/FAIL compliance report.
*   **Usage:**
    ```bash
    /audit
    ```

### 2. `/debug` (Automated Troubleshooting)
*   **Purpose:** Directs the verifier and builder agents to inspect failing pipeline execution logs, trace resource syntax compiler warnings, and propose/implement automated code fixes.
*   **How it works:** Launches the `verifier` agent, which loads the `debug` skill. It parses compiler errors and coordinates with the builders to apply exact string replacements.
*   **Usage:**
    ```bash
    /debug
    ```

### 3. `/expand` (Landing Zone Expansion)
*   **Purpose:** Initiates a guided rollout to deploy new resource components (e.g., Virtual Networks, Databases, Containers, Private Endpoints) and secure-by-design pipelines under strict organization governance.
*   **How it works:** Launches the `orchestrator` agent, which loads the `expand` skill. It gathers requirements, designs the architecture, and delegates implementation to the builders.
*   **Usage:**
    ```bash
    /expand
    ```

### 4. `/optimise` (Cost & Sizing Analysis)
*   **Purpose:** Scans your entire workspace (IaC templates, subnets, and container apps) for cost leaks, oversized SKUs, and resource sizing inefficiencies.
*   **How it works:** Launches the `orchestrator` agent, which loads the `optimise` skill. It scans for oversized SKUs (e.g., Premium Key Vaults, multi-instance App Gateways) and generates a structured cost optimization report with estimated monthly savings.
*   **Usage:**
    ```bash
    /optimise
    ```

---

## 6. Secure Governance Guardrails

All platform operations and deployments must adhere to the following strict security constraints, which are codified and enforced via the `security-checklist` skill:

*   **Federated Login (OIDC):** Long-lived secrets (such as Client Secrets or connection strings) must never be used in pipeline configurations. All pipelines must authenticate using Azure Federated Credentials.
*   **State Resiliency:** Key Vaults, Storage Accounts, and databases must enable soft-delete and purge protection (90-day retention window).
*   **Private Connectivity:** Stateful resources must be isolated behind Private Endpoints. Public network access must be disabled.
*   **Subnet Micro-segmentation:** Network Security Groups (NSGs) must be configured with no open management ports (no 22/3389 open to `0.0.0.0/0`). Workloads must be isolated in dedicated subnets.
*   **Audit Trails:** Central Log Analytics diagnostic streams must be deployed and wired up for all infrastructure components.
*   **Strict Environment Isolation:** Dev pipelines must not have access to Prod subscriptions or Prod state files.
*   **Strict Error Propagation:** Pipeline scripts must use `set -euo pipefail` to ensure intermediate failures stop the pipeline immediately.

---

## 7. Developer Workflows & Git Discipline

To maintain repository hygiene and ensure automated changelog generation, all operators must follow these git discipline rules (codified in the `git-workflow` and `commit-format` skills):

### Branch Naming Convention
All work must be performed on a feature branch named according to the following pattern:
```text
feature/<epic-or-feature-id>-<short-description>
```
*Example:* `feature/drift-detection-engine`

### Pre-Commit Hygiene
Before committing any code, run the local pre-commit hooks to scan for secrets and run SAST compliance checks:
```bash
# Install pre-commit hooks (run once)
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```
*Note: The pre-commit pipeline runs Gitleaks (secret scanning), Checkov (IaC SAST compliance), and framework-specific formatters/validators.*

### Commit Message Format (Conventional Commits)
All commit messages must follow the Conventional Commits specification:
```text
<type>(<scope>): <description>
```
*   **Types:** `feat` (new feature), `fix` (bug fix), `docs` (documentation), `style` (formatting), `refactor` (code change), `perf` (performance), `test` (testing), `ci` (pipeline), `chore` (maintenance).
*   **Format:** Use imperative present tense, lowercase, and no period at the end.
*   *Example:* `feat(kv): enable purge protection and disable public network access`
