---
name: debug
description: Debugs compilation warnings, syntax errors, or failing pipeline runs in the current workspace. Trigger when the user runs /debug.
---

# Debug Pipeline and Deployment Failures Skill

This skill helps diagnose and resolve syntactic compiler warnings, deployment failures, or linter complaints.

## Trigger
Use this skill when the user shares a pipeline error log, reports an Azure CLI error, or runs the `/debug` slash command.

## Steps

1. **Error Extraction (debugging discipline):**
   - Prompt the user to provide the full compiler warning, Azure CLI failure trace, or deployment error log (avoid acting on partial snippets).
2. **Configuration Inspection:**
   - Trace files and associated modules to identify potential misconfigurations, parameter mismatches, or syntax errors.
3. **Syntactic Check:**
   - Summon the `@verifier` to review compiler errors and construct a safe debugging correction plan.
4. **Resolution implementation (reproduce-before-fix):**
   - Where feasible, ensure the failure is reproducible (locally or in CI) and prefer adding or updating a test that captures the bug before applying fixes.
   - Request the appropriate builder agent (`@builder-infra-tf`, `@builder-infra-bicep`, or `@builder-pipelines`) to rewrite or edit files.
   - Run compilation checks (`terraform validate` or `bicep build`) to confirm the fix is successful.

**Pragmatic exceptions:** For trivial typos or comment-only fixes where reproduction is obvious and low-risk, it is acceptable to skip adding a new test, but existing suites must still pass. For emergency hotfixes, patch first and then capture a follow-up task to add a regression test.
