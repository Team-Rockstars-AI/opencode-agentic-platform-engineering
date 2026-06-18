# Workflow: Scaffold

- **Name:** Scaffold Platform Engineering Repository
- **Command:** `/scaffold`
- **Trigger:** Explicit user invocation via `/scaffold`
- **Agent:** `orchestrator`
- **Script:** `python3 scripts/scaffold.py`

## Overview

The `/scaffold` command bootstraps a new, secure, and compliant platform-engineering repository from the templates in this repo. The `orchestrator` coordinates the workflow using the `scaffold` skill.

## Steps

1. **Option Selection**

   The `orchestrator` invokes the `scaffold` skill, which gathers deployment parameters from the user:
   - IaC Framework: `terraform`, `bicep`, or `both`
   - DevOps platform: `github` or `azure-devops`
   - Governance tier: `basic` or `enterprise`
   - Project name and target directory
   - Azure location, subscription ID, tenant ID
   - GitHub org/repo (if applicable)

2. **Template Generation**

   The `orchestrator` runs `python3 scripts/scaffold.py` with the collected parameters. The script:
   - Copies `templates/terraform/` → `<target>/terraform/` (if Terraform selected)
   - Copies `templates/bicep/` → `<target>/bicep/` (if Bicep selected)
   - Copies `templates/github/` → `<target>/.github/` (if GitHub selected)
   - Copies `templates/azure-devops/` → `<target>/` (if Azure DevOps selected)
   - Copies `templates/opencode-config/prompts/` → `<target>/.opencode/prompts/`
   - Copies `templates/opencode-config/skills/` → `<target>/.opencode/skills/`
   - Copies `templates/opencode-config/opencode.json` → `<target>/opencode.json`
   - Copies `templates/opencode-config/scripts/validate-skills.py` → `<target>/scripts/validate-skills.py`
   - Copies `templates/opencode-config/scripts/select-models.py` → `<target>/scripts/select-models.py`
   - Copies `templates/AGENTS.md` → `<target>/AGENTS.md`

3. **Placeholder Substitution**

   The script replaces all `{{placeholder}}` tokens with user-provided values (project_name, azure_location, subscription_id, tenant_id, github_org_name, github_repo_name, etc.).

4. **Security Review**

   The `security-auditor` scans the generated templates to verify no credentials or secrets are present in any generated file, RBAC profiles are appropriately scoped, and NSG rules meet the security baseline.

5. **Initial Git Commit**

   The script initializes git in the target directory and creates the initial commit:
   `git init && git add . && git commit -m "feat: initial platform-engineering template"`

## Agent output contracts

| Stage | Agent | Expected output |
|-------|-------|----------------|
| Scaffold coordination | `orchestrator` | `## Milestone plan` |
| Security review | `security-auditor` | `Security gate: PASSED\|FAILED` |

## Skills used

- `scaffold` — template selection, copy, placeholder substitution, git init
- `security-checklist` — post-scaffold security verification
