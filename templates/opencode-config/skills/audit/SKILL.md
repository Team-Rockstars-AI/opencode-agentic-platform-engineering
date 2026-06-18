---
name: audit
description: Audits the current workspace configurations, files, modules, and pipelines for security, credentials, and compliance. Trigger when the user runs /audit.
---

# Audit Workspace Compliance Skill

This skill handles automated auditing of the workspace against European regulatory and secure-by-design standards (GDPR, DORA, BIO, and NEN 7510).

## Trigger
Use this skill when the user initiates a security review, asks to inspect files for credentials, or runs the `/audit` slash command.

## Steps
1. **Codebase Scanning:**
   - Scan all IaC code files (Terraform/Bicep) for hardcoded secrets, connection strings, or password definitions.
   - Trace subnets, Network Security Groups, and virtual network associations to identify open administrative ports or public internet exposures.
   - Verify if Key Vault, Storage Accounts, and databases have public access disabled and rely on Private Endpoints.
   - Run the skill validation script (`./scripts/validate-skills.py`) to ensure all referenced skills exist and are valid.
2. **Analysis Execution:**
   - Load the `security-checklist` skill to evaluate the workspace against the platform engineering security baseline.
   - Summon the `@security-auditor` to review these configuration aspects.
   - Audit diagnostic setting configurations to ensure active event logs are streamed to a central workspace.
3. **Produce Report:**
   - Generate a detailed compliance markdown report with clear lists of pass criteria, security recommendations, and flagged risks using the finding report format from the `security-checklist` skill.
