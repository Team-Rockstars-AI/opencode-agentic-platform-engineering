# Workflow: Scaffold

- **Name:** Scaffold Platform Engineering Repository
- **Command:** `/scaffold`
- **Trigger:** Explicit user invocation or running `/scaffold`
- **Agent:** architect

## Steps

1. **Option Selection (Interactive Wizard):**
   - The `architect` agent invokes the `question` tool to gather deployment parameters.
   - Prompt the user to select the IaC Framework (`terraform`, `bicep`, `both`).
   - Prompt the user to select the DevOps flow (`github`, `azure-devops`).
   - Prompt the user to select the Governance tier (`basic`, `enterprise`).
   - Prompt the user to define the Project Name and target directory location.

2. **File & Template Generation:**
   - The `platform-engineer` agent is summoned to handle the copying of templates from `templates/` to the target directory.
   - The `platform-engineer` uses the `scaffold` skill to execute copy-verbatim operations on:
     - `templates/terraform` (if Terraform selected)
     - `templates/bicep` (if Bicep selected)
     - `templates/github` (if GitHub selected)
     - `templates/azure-devops` (if Azure DevOps selected)
     - `templates/opencode-config` (to prepopulate `opencode.json`, agent `prompts/`, and operational `skills/` inside `.opencode/` under the target repo)
     - `templates/AGENTS.md` (to copy the platform operations instructions `AGENTS.md` to the target repo root)

3. **Substitution and Customization:**
   - The `platform-engineer` replaces all double-brace placeholders (`{{project_name}}`, `{{azure_location}}`, `{{governance_tier}}`, etc.) with user responses.

4. **Security Audit & Review:**
   - The `security-engineer` agent reviews the generated templates to ensure no secrets are exposed, RBAC profiles are correct, and security policies are appropriately assigned.

5. **Initial Git Commit:**
   - Initialize git in the target repository directory, stage all files, and commit:
     `git init && git add . && git commit -m "feat: initial platform-engineering template"`
