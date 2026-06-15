# Provisioning Platform Operator Manual (THIS Platform)

Welcome to the Operator Manual for the **Azure Platform Engineering Provisioning Platform**. This manual describes how to install, set up, and operate the generator repository (this platform) to scaffold secure, compliant, and opinionated Azure landing zones.

---

## 1. Introduction & Purpose

This provisioning platform is a **Secure-by-Design generator** designed for organizations operating under strict European and Dutch regulatory baselines (such as **GDPR, DORA, BIO, and NEN 7510**). 

Instead of manually copying files and risking configuration drift, this platform automates the generation of new, fully independent repositories. Each generated repository comes pre-loaded with:
1.  **Sovereign-Friendly Multi-Agent Team:** An elite 11-agent team pre-configured to run on cost-effective, sovereign-friendly models.
2.  **Secure Landing Zone Skeletons:** Parameterized Terraform or Bicep modules enforcing private connectivity, soft-delete, and micro-segmentation.
3.  **Zero-Secrets Pipelines:** GitHub Actions or Azure DevOps pipelines utilizing passwordless OIDC authentication.
4.  **Pre-Populated Governance:** Pre-written Architecture Decision Records (ADRs) establishing immediate compliance.

---

## 2. Prerequisites

Before operating the provisioning platform, ensure the following tools are installed and configured on the host machine:

*   **Python 3.10+:** Required to run the scaffolding and validation scripts.
*   **Git:** Required for version control and repository initialization.
*   **OpenCode CLI:** The agentic execution engine. Install via:
    ```bash
    curl -fsSL https://opencode.ai/install | bash
    ```
*   **SSH Authentication to GitHub:** Ensure your SSH key is added to your GitHub account. Verify using:
    ```bash
    ssh -T git@github.com
    ```
*   **GitHub CLI (`gh`):** Required for repository and release management. Ensure it is authenticated:
    ```bash
    gh auth status
    ```

---

## 3. Installation & Setup

### Step 1: Clone the Repository
Clone this generator repository to your local workspace:
```bash
git clone git@github.com:Team-Rockstars-AI/opencode-agentic-platform-engineering.git
cd platform-engineer
```

### Step 2: Connect to OpenCode Zen
OpenCode Zen provides optimized models at cost-price. Connect your OpenCode CLI to the Zen provider:
```bash
opencode connect --provider zen
```

### Step 3: Verify Model Availability
Verify that the required sovereign-friendly models are available in your OpenCode environment:
```bash
opencode models
```
*Note: The platform is configured to use `opencode/north-mini-code-free` (Cohere North Mini Code) for all subagents and `opencode/gemini-3.5-flash` for the orchestrator.*

---

## 4. Scaffolding a New Repository

The scaffolding process can be executed in two ways: interactively via the OpenCode TUI, or programmatically via the Python scaffolding script.

### Method A: Interactive Slash Command (Recommended)
Open the OpenCode console and run the `/scaffold` command:
```bash
/scaffold
```
This launches an interactive wizard that will prompt you for:
1.  **IaC Framework:** `terraform`, `bicep`, or `both`.
2.  **DevOps Pipeline Platform:** `github` (GitHub Actions) or `azure-devops` (Azure Pipelines).
3.  **Governance Tier:** `basic` (standard network baseline) or `enterprise` (enables scale-to-zero ACA private runner pools and enterprise policies).
4.  **Project Name:** e.g., `sovereign-core`
5.  **Azure Region Location:** e.g., `westeurope`
6.  **Target Directory:** The absolute path where your new workspace will be generated.

### Method B: Programmatic CLI (Automation/CI)
For automated or scripted scaffolding, run the Python script directly with command-line flags:
```bash
python3 scripts/scaffold.py \
  --framework terraform \
  --pipeline github \
  --tier enterprise \
  --project sovereign-core \
  --location westeurope \
  --target /absolute/path/to/target-repo
```

### What the Scaffolder Does
When executed, the scaffolding engine performs the following operations:
1.  **Directory Creation:** Creates the target directory structure.
2.  **Template Copying:** Copies the selected landing zone skeletons (Terraform/Bicep) and pipeline templates.
3.  **Module Inclusion:** Copies the required reusable modules from `modules/` directly into the target repository, making it completely self-contained.
4.  **OpenCode Configuration:** Deploys the complete agent team, prompts, and skills into the target's `.opencode/` directory.
5.  **Placeholder Substitution:** Replaces all `{{project_name}}`, `{{azure_location}}`, and other placeholders across all files.
6.  **Pre-Commit Setup:** Moves the relevant `.pre-commit-config.yaml` to the target root.
7.  **Git Initialization:** Initializes a new Git repository and commits the initial template using Conventional Commits (`feat: initial platform-engineering template`).

---

## 5. Operating the Generator Workspace

As an operator of the provisioning platform, you can run local checks and slash commands directly on this generator repository to maintain and expand it.

### Local Slash Commands
*   **`/scaffold`**: Launches the repository generation wizard.
*   **`/audit`**: Scans the local landing zone modules and configurations for secure-by-design compliance (credentials, public IPs, and logging).
*   **`/debug`**: Instructs the verifier and builders to resolve any linter warnings or syntax compile errors in the module codebase.
*   **`/expand`**: Assists in adding new resource modules or expanding existing skeletons.
*   **`/optimise`**: Scans the local landing zone modules and configurations for cost-saving opportunities and resource sizing inefficiencies.

### Manual Quality & Verification Checks
Run these commands to manually verify the integrity of the generator repository before making changes or creating releases:

```bash
# 1. Validate all Terraform modules
for d in modules/terraform/*/; do (cd "$d" && terraform init -backend=false && terraform validate); done

# 2. Compile and check all Bicep modules
for f in modules/bicep/**/main.bicep; do bicep build "$f" --stdout > /dev/null; done

# 3. Verify that the OpenCode configuration is valid JSON
python3 -m json.tool opencode.json > /dev/null

# 4. Verify all skill references in prompts resolve to existing skill files
python3 scripts/validate-skills.py
```

---

## 6. Sovereignty Policy Enforcement

This platform enforces a strict **Sovereignty Policy** to ensure that no sensitive code generation or task execution is sent to non-compliant jurisdictions (such as China).

### How it Works
1.  **`manifest.yaml`:** Defines the active agents and their model endpoints. All subagents are mapped to `opencode/north-mini-code-free` (Sovereign-based, Cohere), and the orchestrator is mapped to `opencode/gemini-3.5-flash` (US-based authorized fallback).
2.  **`agent_config.py`:** A Python configuration layer that intercepts agent execution. It enforces a strict `SECURITY_POLICY` that automatically overrides any non-compliant model with sovereign-friendly defaults.
3.  **Validation Hook:** Logs the origin jurisdiction of every model and triggers a critical exception if a non-compliant model is selected for a restricted task.

### Running the Sovereignty Self-Test
Verify that the sovereignty policy is active and enforcing correctly:
```bash
python3 agent_config.py
```
*Expected Output:*
```text
Validating agent 'orchestrator' using model 'opencode/gemini-3.5-flash' (Jurisdiction: US) for task type 'STANDARD'
Authorized fallback model 'opencode/gemini-3.5-flash' used for standard task.
Validating agent 'builder-infra-tf' using model 'opencode/north-mini-code-free' (Jurisdiction: Sovereign) for task type 'RESTRICTED'
Validating agent 'verifier' using model 'opencode/north-mini-code-free' (Jurisdiction: Sovereign) for task type 'STANDARD'
Validating agent 'malicious-agent' using model 'openai/gpt-4o' (Jurisdiction: US) for task type 'RESTRICTED'
CRITICAL SECURITY VIOLATION: Non-EU, non-authorized model 'openai/gpt-4o' (Jurisdiction: US) selected for RESTRICTED task!
```
