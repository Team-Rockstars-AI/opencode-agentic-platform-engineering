# Azure Platform Engineering Template Repository

Welcome! This repository scaffolds secure, opinionated, **Secure-by-Design**, and compliant Azure platform infrastructures. By cloning this repo and running a few simple commands, you can generate a brand-new target repository fully pre-populated with a highly sophisticated **OpenCode Multi-Agent Team**, workflows, and secure infrastructure blueprints.

---

## 🌟 Solution Architecture & Key Standards

This template is designed specifically for organizations operating under strict European and Dutch regulatory baselines (such as **GDPR, DORA, BIO, and NEN 7510**), enforcing **Defense-in-Depth** by default:

*   **Secure-by-Design Network Baseline:**
    *   **NAT Gateway:** All outbound internet traffic is routed through an Azure NAT Gateway with standard Public IPs, providing outbound SNAT and removing public IP needs on workloads or container runtimes.
    *   **Application Gateway + WAF v2:** Secure, monitored inbound application load-balancing protecting workloads against OWASP Top 10 web vulnerabilities.
    *   **Zero High-Cost Overheads:** Replaces costly Azure Firewall configurations in standard setups with highly competitive, micro-segmented network configurations.
*   **Zero-Secrets Pipelines (OIDC):** Fully passwordless deployments using OpenID Connect (OIDC) Federated Credentials, eliminating long-lived credentials, Client Secrets, and connection strings from source code.
*   **Private PaaS Isolation (Private Link):** Disables public internet access to Key Vault and Storage Accounts, restricting routing to **Private Endpoints** inside micro-segmented subnets.
*   **Scale-to-Zero Private Runner Pools (Enterprise Tier):** Automatically deploys transient, KEDA-scaled, **Ubuntu-based self-hosted runners** inside Azure Container Apps (ACA). Runners scale up on pipeline demand to execute secure private deployments and scale to zero when idle, saving all operational costs.
*   **Continuous DevSecOps Validation:**
    *   **Gitleaks & Checkov:** Automatic pipeline gates scanning for leaked credentials or IaC misconfigurations.
    *   **Plan Validator Safety Gate:** The verifier generates execution logs and triggers the `@plan-validator` agent. The run is **instantly terminated** if databases, Key Vaults, or Hub networking are slated for destruction or replacement.

---

## 🚀 Quick Start: Setup Your Environment

Follow this step-by-step walkthrough to scaffold your secure platform-engineering workspace:

### Step 1: Clone the Repository
Clone this generator repository to your local workspace:
```bash
git clone https://github.com/your-org/platform-engineer.git
cd platform-engineer
```

### Step 2: Connect to OpenCode Zen
OpenCode Zen provides optimized models at cost-price. Start OpenCode, log in, and register your API key:
```bash
# Connect to OpenCode Zen via TUI
opencode connect --provider zen
```

### Step 3: Run the Scaffolding Wizard
Run the interactive scaffolding command inside the OpenCode console or run:
```bash
# Execute the scaffolding slash command
/scaffold
```

This starts the interactive wizard which will prompt you to select your desired parameters:
1.  **IaC Framework:** `terraform`, `bicep`, or `both`.
2.  **DevOps Pipeline Platform:** `github` (GitHub Actions) or `azure-devops` (Azure Pipelines).
3.  **Governance Tier:** `basic` (standard network baseline) or `enterprise` (enables scale-to-zero ACA private runner pools and enterprise policies).
4.  **Project Name:** e.g., `sovereign-core`
5.  **Azure Region Location:** e.g., `westeurope`
6.  **Target Directory:** The absolute path where your new workspace will be generated.

The platform agent team will automatically:
*   Copy your selected landing zone skeletons.
*   Inject the complete, pre-configured **11-Agent Team** and prompts into `.opencode/`.
*   Replace all variable placeholders (`{{project_name}}`, `{{azure_location}}`, etc.) across modules and pipelines.
*   Initialize Git and run compliance validates.

---

## 🤖 Deployed Multi-Agent Team Structure

Your newly generated repository comes pre-loaded with an elite platform operations team defined inside `.opencode/opencode.json` and optimized via cost-effective **OpenCode Zen models**:

| Subagent | Assigned Model | Operational Purpose |
|---|---|---|
| **`orchestrator`** | `opencode/gemini-3.5-flash` | The strategic lead. Parses backlogs, schedules rollouts, and delegates milestones. |
| **`builder-infra-tf`** | `opencode/north-mini-code-free` | Authors secure, modular, parameterized Terraform resources. |
| **`builder-infra-bicep`** | `opencode/north-mini-code-free` | Authors multi-scope Bicep templates. |
| **`builder-pipelines`** | `opencode/north-mini-code-free` | Configures OIDC-federated automated workflows. |
| **`verifier`** | `opencode/north-mini-code-free` | Compiles code (`terraform validate` / `bicep build`) and generates dry-run logs. |
| **`security-auditor`** | `opencode/north-mini-code-free` | Audits configurations for compliance and security gaps. |
| **`plan-validator`** | `opencode/north-mini-code-free` | **Blast Radius Valve.** Scans plan logs and blocks destruction of critical resources. |
| **`code-reviewer`** | `opencode/north-mini-code-free` | Reviews code naming conventions and tagging rules. |
| **`explorer`** | `opencode/north-mini-code-free` | Traces dependencies and indexes the local directories. |
| **`test-writer`** | `opencode/north-mini-code-free` | Writes unit and integration tests (`.tftest.hcl`). |
| **`docs-writer`** | `opencode/north-mini-code-free` | Maintains markdown runbooks, variables tables, and ADRs. |

---

---

## 🛠️ Reusable Skills

In addition to the agent team, the platform includes reusable **Skills** — codified, version-controlled procedures that agents invoke via the `skill` tool. Skills standardise common operations across the codebase:

| Skill | Purpose |
|-------|---------|
| **`architecture-review`** | Guidelines for reviewing architectural changes, subscription topologies, firewall rules, private endpoints, and central state access patterns. Used by `@code-reviewer` and `@orchestrator` during design reviews. |
| **`audit`** | Drives the `/audit` slash command — scans IaC code for secrets, traces NSG rules, verifies Private Endpoint usage, and loads the `security-checklist` skill to produce a structured compliance report. |
| **`code-standards`** | CAF naming conventions, Azure Well-Architected Framework alignment (5 pillars), tagging standards, and IaC best practices for Terraform and Bicep. Used by `@code-reviewer`, `@builder-infra-tf`, and `@builder-infra-bicep`. |
| **`commit-format`** | Conventional Commits specification enforcing structured commit types, scopes, and description format for automated changelog generation. Used by `@builder-infra-tf`, `@builder-infra-bicep`, and `@builder-pipelines` before staging commits. |
| **`debug`** | Powers `/debug` — directs verifier and builder agents to trace and fix compilation errors. |
| **`doc-standards`** | Documentation standards for module READMEs, ADR format, runbooks, and onboarding guides targeting operations teams and developers. Used by `@docs-writer`. |
| **`expand`** | Powers `/expand` — guides the rollout of new resource modules under governance guardrails. |
| **`git-workflow`** | Branch naming conventions (`feature/<id>-<desc>`), pre-commit hygiene (formatter, `git add -p`), commit blacklist rules (no secrets, no debug artifacts, no commented-out code), and handoff summary format for the `@test-writer`. Enforced by all builder agents before staging or committing. |
| **`plan-tracking`** | Execution plan JSON conversion, resource action tracking (create/update/delete/replace), milestone status updates, and session state maintenance. Used by `@plan-validator` and `@docs-writer`. |
| **`scaffold`** | Powers the `/scaffold` workflow — copies template sets, resolves placeholders, initialises git. |
| **`security-checklist`** | Structured security review checklist with PASS/FAIL/NA criteria, covering OIDC enforcement, network isolation, soft-delete, least-privilege IAM, diagnostic logging, and strict typing. Used by the `@security-auditor` agent during every audit pass. |
| **`test-patterns`** | Unit and validation test guidelines for Terraform (.tftest.hcl) and Bicep modules, including plan assertions and what-if validation patterns. Used by `@test-writer` and `@builder-infra-tf`. |

## 🛠️ Local Workspace Operations & Slash Actions

In addition to scaffolding, this repository contains active local OpenCode configurations. You can run compliance audits, debug compilation errors, or expand templates directly on this repository using these custom slash actions:

*   **`/audit`**: Scans our local landing zone modules, templates, and configurations for secure-by-design baseline compliance (credentials, public IPs, and logging). Leverages the `security-checklist` skill to produce structured PASS/FAIL findings with remediation blocks.
*   **`/debug`**: Instructs our verifier and builders to identify and resolve any linter warnings or syntax compile errors in our module codebase.
*   **`/expand`**: Assists in adding new resource modules or expanding existing Bicep and Terraform landing zone skeletons.
*   **`/optimise`**: Scans our local landing zone modules, templates, and configurations for cost-saving opportunities and resource sizing inefficiencies. Leverages the `optimise` skill to produce a structured cost optimization report.

---

## 🛡️ Verification & Quality Checks

Run the following commands within your directory to manually compile and check configurations:

```bash
# Validate all Terraform modules
for d in modules/terraform/*/; do (cd "$d" && terraform init -backend=false && terraform validate); done

# Compile and syntax check all Bicep modules
for f in modules/bicep/**/main.bicep; do bicep build "$f" --stdout > /dev/null; done

# Validate that your OpenCode configuration remains 100% compliant
python3 -m json.tool opencode.json > /dev/null

# Verify all skill references in prompts resolve to existing skill files
python3 scripts/validate-skills.py
```

---

## 📖 Deployed Documentation

To help you operate and maintain this platform, we have authored comprehensive, human-facing operator manuals:

*   **[Provisioning Platform Operator Manual (THIS Platform)](docs/operator-manual-provisioning-platform.md)** — A detailed guide on how to install, set up, and operate this generator repository to scaffold new workspaces.
*   **[Provisioned Platform Operator Manual (The Generated Workspace)](docs/operator-manual-provisioned-platform.md)** — A detailed guide on how to operate, maintain, and expand your newly generated repository using the integrated OpenCode multi-agent team and secure-by-design workflows.

Once scaffolded, you can also refer to the **`AGENTS.md`** file created at the root of your new target directory. It outlines the specific developer workflows and exact operational standards required to manage your live workloads.
