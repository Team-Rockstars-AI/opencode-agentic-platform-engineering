---
name: update
description: Template-update workflow shipped to provisioned repos (unused in this provisioning repo itself) — syncs a scaffolded workspace with a newer upstream template version
license: MIT
compatibility: opencode
---

## Purpose

Drive the `/update` command in a **scaffolded (provisioned) repository**: pull upstream platform-template improvements (module fixes, new skills, security patches, pipeline updates) into the workspace without losing local changes.

> This master copy lives in the provisioning/template repository for maintenance and parity only — the skill is *executed* inside provisioned repos, where `scripts/update.py` and the `.platform-scaffold.json` stamp exist.

## How the mechanism works

- At scaffold time, `scaffold.py` wrote `.platform-scaffold.json` at the repo root: the template repo/commit, the exact scaffold inputs, and a sha256 manifest of every generated file.
- `scripts/update.py --template-path <local-clone>` re-renders the templates at the new version with the recorded inputs and classifies every file three-way (original render vs. current file vs. new render):
  - **auto-update / new-file / removed-upstream** — applied automatically (file was never modified locally).
  - **user-modified / user-deleted** — local state wins; nothing is touched.
  - **conflict** — both sides changed the file; left untouched and listed for manual merge.
- Exit codes: `0` success/up-to-date, `1` fatal error, `2` success with conflicts.
- The tool never commits; staging and committing stay with the operator/agents.

## Procedure

1. **Fetch the template.** Ask the user for the local path of the upstream template repository (or a git URL — then `git clone`/`git pull` it yourself). `update.py` does no network I/O.
2. **Dry run.** Run `python3 scripts/update.py --template-path <path> --dry-run` and present the classification summary to the user for approval before changing anything.
3. **Apply.** Re-run without `--dry-run`. A report is written to `docs/reports/update-report-<date>.md`.
4. **Merge conflicts (exit code 2).** For each conflicted file:
   - `@explorer` diffs the three versions (original scaffold, local, new template).
   - The matching builder merges upstream changes into the locally modified file: `@builder-infra-tf` (Terraform), `@builder-infra-bicep` (Bicep), `@builder-pipelines` (pipelines/workflows).
   - `@verifier` re-runs `terraform validate` / `bicep build` on merged IaC.
   - `@security-auditor` reviews every merged security-relevant file (NSGs, Key Vault, OIDC, pipeline permissions).
5. **Verify.** Run `python3 scripts/validate-skills.py` and the standard compile checks.
6. **Document.** `@docs-writer` completes the update report (use `docs/reports/update-report-template.md` as the structure for the final report) and records the outcome.
7. **Commit.** Stage and commit per the `git-workflow` skill (conventional commit, e.g. `chore: sync with platform template <short-commit>`).

## Safety rules

- **Never auto-merge conflicts in `*.tfvars`, `backend.tf`, or pipeline credential/OIDC configuration** — always surface those to the human operator.
- Never run `update.py` with uncommitted local changes; require a clean `git status` first so the update is reviewable and revertible.
- If the update touches stateful-resource IaC (databases, Key Vaults, state storage), trigger `@plan-validator` on the next plan before any deployment.

## Output format

Report the classification counts, the conflict list with per-file resolutions, verification results, and the report path.
