---
name: scaffold
description: Scaffolds a new secure and compliant platform-engineering repository on Azure using selected options (IaC framework, DevOps pipeline, governance tier).
---

# Scaffold Platform Engineering Repository

This skill handles the interactive option gathering, template copying, and post-processing required to spin up a new platform-engineering repository.

## Trigger
Use this skill when the user initiates a repository setup request, clones a repository to generate a new workspace, or invokes a scaffolding slash command such as `/scaffold`.

## Steps

1. **Option Gathering:** Use the `question` tool to prompt the user to make choices:
   - **IaC Framework:** `terraform`, `bicep`, or `both`
   - **DevOps Platform:** `github` (GitHub Actions) or `azure-devops` (Azure Pipelines)
   - **Governance Tier:** `basic` (standard resource groups, subscription-scoped IAM) or `enterprise` (management group hierarchy, enterprise-scale landing zones, custom Azure Policies)
   - **Project Name:** Lowercase alphanumeric string with hyphens
   - **Target Directory:** Absolute path to generate the new repository in
   - **Azure Primary Location:** e.g., `eastus2`, `westeurope`, etc.

2. **Directory Initialization:**
   - Verify the target directory path. Create the directory if it does not exist.
   - Initialize git in the target directory (`git init`).

3. **Template Copying:**
   - If IaC framework includes `terraform`, copy `templates/terraform/` files to the target directory root.
   - If IaC framework includes `bicep`, copy `templates/bicep/` files to the target directory root.
   - If DevOps platform is `github`, copy `templates/github/` files to the target directory under `.github/`.
   - If DevOps platform is `azure-devops`, copy `templates/azure-devops/` files to the target directory root.
    - Copy `templates/opencode-config/opencode.json`, the `templates/opencode-config/prompts/` folder, the `templates/opencode-config/skills/` folder, and the `templates/opencode-config/scripts/` folder to the target directory under `.opencode/`.
   - Copy `templates/AGENTS.md` to the target directory root as `AGENTS.md`.

4. **Placeholder Substitution:**
   - Recursively process all copied files.
   - Identify placeholders like `{{project_name}}`, `{{azure_location}}`, `{{governance_tier}}`, and replace them with the user's answers.
   - Remove any unused folders (e.g., if `terraform` was selected and `bicep` was not, ensure no bicep templates/modules are left in the target directory).

5. **Post-Scaffold Verification:**
   - Execute the appropriate linter/builder validation based on the chosen framework (e.g., `bicep build` or `terraform validate` if dependencies are available, or do a dry run).
   - Commit the scaffolded structure as an initial commit (`git add . && git commit -m "feat: initial scaffolding from platform-engineer template"`).

## Output
A fully structured, customized, and initialized target repository containing the requested IaC framework, DevOps pipeline config, a custom `opencode.json` configuration, and the necessary agent/skill instructions.
