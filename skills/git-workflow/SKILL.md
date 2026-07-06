---
name: git-workflow
description: Branching strategy, commit discipline, and PR hygiene rules for the build agent to follow when making code changes in Platform Engineering
license: MIT
compatibility: opencode
---

## Branch naming

Always work on a feature branch. Never commit directly to main.

Format: `feature/<epic-or-feature-id>-<description>`

Examples:
- `feature/F102-vnet-peering`
- `feature/E45-keyvault-setup`

## Before making any change

1. Confirm you are on the correct feature branch (`git branch`)
2. Pull latest from the base branch (`git pull origin main`)
3. Check for any merge conflicts before touching files

## After implementing

1. Run the formatter/linter before staging:
   - For Terraform: `terraform fmt -recursive`
   - For Bicep: `bicep format [file]`
2. Stage only the files relevant to this task (`git add -p` for precision)
3. Do not stage unrelated changes, debug artifacts, or local configuration files

## What never goes in a commit

- Hardcoded secrets, API keys, tokens, or passwords
- Local configuration overrides (e.g., `.tfvars`, `.gvars`, local parameter JSONs)
- Unencrypted state files or local state backups
- Commented-out dead code (delete it)
- Console.log / print debug statements in pipeline scripts
- Generated build artifacts (dist/, node_modules/)

## Karpathy edit-time discipline (lightweight checklist)

Use this compact checklist while editing to avoid unnecessary token usage:

- **Think before coding:** State assumptions and open questions in the plan or summary before large edits.
- **Simplicity first:** Implement only what the current ticket/epic requires; defer extra ideas to follow-up issues.
- **Surgical changes:** Limit edits to the files and concerns in scope. If you need a broader refactor, make it a separate, test-backed task.
- **Goal-driven:** Decide up front which checks must pass (e.g., `pytest`, `terraform test`, `validate-team.py`) and run them before calling a change done.

These principles apply strongest to infra, pipeline, and architecture changes. For trivial documentation or comment-only tweaks, keep them in mind but avoid over-ceremony.

## Handing off to test-writer

When done, output a summary in this exact format so the test-writer knows what to cover:

```
## Build summary
- Files changed: [list]
- New inputs/outputs/parameters: [list with types]
- Changed resource behaviour: [plain English]
- Edge cases to test: [list]
- External dependencies added: [list or "none"]
```
