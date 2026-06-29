# Workflow: Automated Troubleshooting & Debugging

- **Name:** Automated Troubleshooting & Debugging
- **Command:** `/debug`
- **Trigger:** Explicit user invocation via `/debug` or triggered by pipeline failure
- **Primary Agent:** `verifier`
- **Supporting Skills:** `debug` (primary), `git-workflow`, `code-standards`

## Overview

The `/debug` workflow automates the identification and resolution of compilation errors, linter warnings, and pipeline failures. The `verifier` agent leads the process, using the `debug` skill to trace errors back to their source and coordinating with builder agents to apply precise fixes.

## Steps

1. **Error Capture (`verifier`)**
   - Load the `debug` skill.
   - Capture error logs from the local environment (`terraform validate`, `bicep build`) or from a failed CI/CD pipeline run.
   - Parse the logs to identify the affected files, line numbers, and error codes.

2. **Root Cause Analysis (`verifier`)**
   - Analyze the captured errors against the codebase.
   - Determine if the issue is a syntax error, a missing dependency, a variable mismatch, or a violation of `code-standards`.

3. **Fix Proposal (`verifier` + `builder-infra-*`)**
   - Coordinate with the relevant builder agent (`@builder-infra-tf`, `@builder-infra-bicep`, or `@builder-pipelines`) to design a fix.
   - Generate the required code changes (e.g., string replacements, variable additions).

4. **Verification (`verifier`)**
   - Apply the proposed fix to a temporary state or directly to the workspace.
   - Re-run the validation commands to confirm the error is resolved and no regressions were introduced.

5. **Commit & Handoff (`builder-infra-*`)**
   - Load the `git-workflow` and `commit-format` skills.
   - Stage the changes and commit them using the appropriate conventional commit type (e.g., `fix(core): resolve terraform syntax error`).
   - Provide a summary of the fix to the `orchestrator`.

## Agent output contracts

| Stage | Agent | Expected output |
|-------|-------|----------------|
| Error Analysis | `@verifier` | `Verification: FAILED` with error trace |
| Resolution | `@verifier` | `Verification: PASSED` after applying fixes |
| Implementation | `@builder-infra-*` | Commit hash and summary of changes |

## Artifacts produced

- Debug logs and trace files (temporary).
- Git commits resolving the identified issues.
