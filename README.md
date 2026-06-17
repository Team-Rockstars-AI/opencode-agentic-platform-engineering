# Azure Platform Engineering Template Repository

[![CI](https://github.com/Team-Rockstars-AI/opencode-agentic-platform-engineering/actions/workflows/ci.yml/badge.svg)](https://github.com/Team-Rockstars-AI/opencode-agentic-platform-engineering/actions/workflows/ci.yml)
[![Security Scan](https://github.com/Team-Rockstars-AI/opencode-agentic-platform-engineering/actions/workflows/security.yml/badge.svg)](https://github.com/Team-Rockstars-AI/opencode-agentic-platform-engineering/actions/workflows/security.yml)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://www.conventionalcommits.org)

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

Your newly generated repository comes pre-loaded with an elite platform operations team defined inside `.opencode/opencode.json`. Rather than pinning a fixed model to each agent, the team is **dynamically optimized against the live OpenCode Zen bundle** — the `/select-models` command discovers which Zen models are currently available, reads their **current per-1M-token pricing**, and — *hardware allowing* — folds in your locally installed **Ollama** models, then reasons over each agent's prompt and skills to assign the best *available* model per role.

Each agent maps to a **selection tier** that determines the class of model chosen for it:

| Subagent | Selection Tier | Operational Purpose |
|---|---|---|
| **`orchestrator`** | High-Reasoning | The strategic lead. Parses backlogs, schedules rollouts, and delegates milestones. |
| **`builder-infra-tf`** | Code-Generation | Authors secure, modular, parameterized Terraform resources. |
| **`builder-infra-bicep`** | Code-Generation | Authors multi-scope Bicep templates. |
| **`builder-pipelines`** | Code-Generation | Configures OIDC-federated automated workflows. |
| **`verifier`** | Task-Execution | Compiles code (`terraform validate` / `bicep build`) and generates dry-run logs. |
| **`security-auditor`** | Task-Execution | Audits configurations for compliance and security gaps. |
| **`plan-validator`** | Task-Execution | **Blast Radius Valve.** Scans plan logs and blocks destruction of critical resources. |
| **`code-reviewer`** | Task-Execution | Reviews code naming conventions and tagging rules. |
| **`explorer`** | Task-Execution | Traces dependencies and indexes the local directories. |
| **`test-writer`** | Task-Execution | Writes unit and integration tests (`.tftest.hcl`). |
| **`docs-writer`** | Task-Execution | Maintains markdown runbooks, variables tables, and ADRs. |

### How models are selected

Run `/select-models` (see below) and choose your preferences; the team is then optimized accordingly:

*   **Jurisdiction policy** — `EU` (EU/Sovereign-only), `EU+US`, or `Global`. Each Zen model's jurisdiction is inferred from its id and filtered to your policy, so sovereignty is enforced by construction.
*   **Optimization focus** — `Cost` prefers free / ultra-low-cost tiers; `Quality` prefers maximum reasoning and code-generation capability. Decisions use the **live pricing** scraped from the Zen docs (with a clearly-flagged cached fallback if pricing can't be fetched).
*   **Local models (Ollama)** — *hardware allowing*, locally installed Ollama models can be assigned to suitable roles for zero-cost, fully sovereign execution. You declare your hardware tier (`Low-end` ≤8B, `Mid-range` ≤27B, `High-end` 70B+) and the optimizer only picks local models that fit.

> **Shipped default:** out of the box the team is configured sovereign-friendly — `opencode/gemini-3.5-flash` for the `orchestrator` and `opencode/north-mini-code-free` for all subagents. Re-run `/select-models` at any time to re-optimize against the *current* live catalog, pricing, and your hardware.

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
| **`model-optimiser`** | Discovers the live OpenCode ZEN catalog and locally installed Ollama models, then reasons over each agent's prompt and skills to select the optimal *available* model per agent — honouring jurisdiction, cost/quality focus, and local hardware capabilities. Used by `@orchestrator` during model optimization. |
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
*   **`/select-models`**: After gathering your jurisdiction, local-model, focus, and hardware preferences, fetches a fresh OpenCode ZEN model list and your installed Ollama models, then reasons over each agent's prompt and skills to assign the optimal *available* model per agent. Leverages the `model-optimiser` skill to update configurations and run verification tests.


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

To help you operate, maintain, and govern this platform, we have authored a comprehensive suite of human-facing documentation guides:

### Operator Manuals
*   **[Provisioning Platform Operator Manual (THIS Platform)](docs/operator-manual-provisioning-platform.md)** — A detailed guide on how to install, set up, and operate this generator repository to scaffold new workspaces.
*   **[Provisioned Platform Operator Manual (The Generated Workspace)](docs/operator-manual-provisioned-platform.md)** — A detailed guide on how to operate, maintain, and expand your newly generated repository using the integrated OpenCode multi-agent team and secure-by-design workflows.

### Architecture & Governance Guides
*   **[Architecture Blueprint & Network Topology](docs/architecture-blueprint.md)** — A detailed blueprint of the secure-by-design Hub-Spoke network topology, Private Link integration, and micro-segmentation.
*   **[Regulatory Compliance Mapping Guide](docs/compliance-mapping-guide.md)** — Maps the technical controls of the landing zone directly to European and Dutch regulatory articles (DORA, GDPR, BIO, NEN 7510).
*   **[Disaster Recovery & State Reconstruction Runbook](docs/disaster-recovery-runbook.md)** — Step-by-step instructions for recovering from state locks, state corruption, or accidental resource deletions.
*   **[Workload Developer Onboarding Guide](docs/onboarding-guide-workloads.md)** — Guides application development teams on how to securely request subnets, configure Private Endpoints, and set up OIDC-federated pipelines.
*   **[Cost Governance & Sizing Guide](docs/cost-governance-guide.md)** — Outlines the cost-saving strategies, sizing guidelines, and optimization rules enforced by the platform.

Once scaffolded, you can also refer to the **`AGENTS.md`** file created at the root of your new target directory. It outlines the specific developer workflows and exact operational standards required to manage your live workloads.

---

## 🤝 Contributing & Collaboration

This repository is built to be **shared and worked on together** — for cooperation
on code, bugs, fixes, and pull requests, and as a learning resource for the team.

**Start here:** read the **[Contributing Guide](CONTRIBUTING.md)**. In short:

1.  **Branch** off `main` using `feature/<id>-<description>` — never commit to `main` directly.
2.  **Commit** using [Conventional Commits](https://www.conventionalcommits.org) (`feat:`, `fix:`, `docs:`, `ci:`, …).
3.  **Open a PR** against `main` using the [pull request template](.github/PULL_REQUEST_TEMPLATE.md); a [code owner](.github/CODEOWNERS) is auto-requested for review.
4.  **Get one approval**, resolve conversations, and **squash-merge**.

Use the issue forms to **[report a bug](.github/ISSUE_TEMPLATE/bug_report.yml)** or
**[request a feature](.github/ISSUE_TEMPLATE/feature_request.yml)**. Please be kind
and constructive — see the **[Code of Conduct](CODE_OF_CONDUCT.md)**.

### Automated checks on every pull request

Continuous integration and security scanning run automatically on each PR (and weekly):

| Workflow | Job | Purpose |
|:---|:---|:---|
| **CI** | Python lint & skill validation | `ruff`, byte-compile, and `validate-skills.py` |
| **CI** | Config validation (JSON/YAML) | Parse all repo JSON/YAML config |
| **CI** | Terraform format check | `terraform fmt -check` on `modules/` |
| **CI** | Secret scan (gitleaks) | Block leaked credentials |
| **Security Scan** | Bandit (Python SAST) | Block on HIGH-severity findings |
| **Security Scan** | Checkov (IaC) | Report Terraform/Bicep misconfigurations |
| **Dependabot** | — | Weekly dependency & GitHub Actions update PRs + security advisories |

> **Plan note:** This repository is **private on the GitHub Free plan**, where
> server-side branch protection, required checks, and GitHub Advanced Security
> (CodeQL, secret scanning, the code-scanning dashboard) are unavailable. The
> checks above therefore run and report on every PR but are enforced as **team
> conventions** rather than hard merge gates. Enabling **GitHub Team** (private)
> or making the repo **public** would unlock branch protection and CodeQL; see
> [SECURITY.md](SECURITY.md) for details.

### Security

Report vulnerabilities **privately** — never in a public issue. See the
**[Security Policy](SECURITY.md)** for the process and the full list of automated
controls.
