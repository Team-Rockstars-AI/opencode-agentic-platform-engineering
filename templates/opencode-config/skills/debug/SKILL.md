---
name: debug
description: Debugs compilation warnings, syntax errors, or failing pipeline runs in the current workspace. Trigger when the user runs /debug.
---

# Debug Pipeline and Deployment Failures Skill

This skill helps diagnose and resolve syntactic compiler warnings, deployment failures, or linter complaints.

## Trigger
Use this skill when the user shares a pipeline error log, reports an Azure CLI error, or runs the `/debug` slash command.

## Steps
1. **Error Extraction:**
   - Prompt the user to provide the exact compiler warning, Azure CLI failure trace, or deployment error log.
2. **Configuration Inspection:**
   - Trace files and associated modules to identify potential misconfigurations, parameter mismatches, or syntax errors.
3. **Syntactic Check:**
   - Summon the `@verifier` to review compiler errors and construct a safe debugging correction plan.
4. **Resolution implementation:**
   - Request the appropriate builder agent (`@builder-infra-tf`, `@builder-infra-bicep`, or `@builder-pipelines`) to rewrite or edit files.
   - Run compilation checks (`terraform validate` or `bicep build`) to confirm the fix is successful.
