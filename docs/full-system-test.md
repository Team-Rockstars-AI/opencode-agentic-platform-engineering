# Full System Test — opencode Agentic Platform Engineering

> Execute this document as your working prompt in opencode. Work through each phase in order. Treat every ✅ / ❌ marker as a live pass/fail gate — stop and fix before continuing if a gate fails. At the end, clean up all artefacts so the repo is left in its pre-test state (modulo any bug-fixes made during the test).

---

## Context

You are performing a full end-to-end validation of the **opencode-agentic-platform-engineering** scaffolding platform. This is a *repository-only* test — no Azure subscription is available, so nothing is deployed. Subscription/tenant IDs used below are **placeholder values only**.

The goals are:
1. Confirm all tooling and pre-conditions are met.
2. Exercise the `/scaffold` workflow and verify its output is structurally and semantically correct.
3. Smoke-test each of the 11 agents individually.
4. Run all built-in validation scripts.
5. Exercise the remaining slash commands (`/audit`, `/debug`, `/expand`, `/optimise`, `/select-models`) in dry-run / read-only mode.
6. Clean up every artefact created during the test.

> **Note:** This document now also records actual test runs at the end (see **Execution record**). The run described below was executed without any live Azure subscription; all plans and what-if checks were local or synthetic.

---

## Phase 0 — Pre-flight checks

Run these bash commands and confirm all pass before proceeding.

```bash
# 1. JSON config is valid
python3 -m json.tool opencode.json > /dev/null && echo "✅ opencode.json valid"

# 2. All skill references resolve
python3 scripts/validate-skills.py && echo "✅ Skill references valid"

# 3. Full team consistency check (agents, prompts, skills, commands, topology parity)
python3 scripts/validate-team.py && echo "✅ Team topology valid"

# 4. Terraform modules syntactically validate
for d in modules/terraform/*/; do
  echo "Validating $d …"
  (cd "$d" && terraform init -backend=false -no-color 2>&1 | tail -1 && terraform validate -no-color) || echo "❌ $d failed"
done

# 5. Bicep modules build cleanly
for f in modules/bicep/**/main.bicep; do
  echo "Building $f …"
  bicep build "$f" --stdout > /dev/null && echo "✅ $f" || echo "❌ $f failed"
done
```

**Gate:** all five checks must produce no errors. If any fail, fix the underlying issue and re-run the check before continuing.

---

## Phase 1 — Scaffold a test repository

### 1.1  Run the scaffold script

```bash
python3 scripts/scaffold.py \
  --iac-framework both \
  --devops-platform github \
  --governance-tier enterprise \
  --project-name platform-test \
  --target-dir /tmp/platform-test \
  --azure-location westeurope \
  --subscription-id 00000000-0000-0000-0000-000000000001 \
  --tenant-id 00000000-0000-0000-0000-000000000002 \
  --github-org testorg \
  --github-repo platform-test \
  --non-interactive
```

**Gate:** script exits 0 and `/tmp/platform-test/` is created.

### 1.2  Verify output structure

Check that the following paths exist in `/tmp/platform-test/`:

- [ ] `opencode.json`
- [ ] `AGENTS.md`
- [ ] `.opencode/prompts/` (at least one `.txt` file)
- [ ] `terraform/` directory
- [ ] `bicep/` directory
- [ ] `.github/` directory
- [ ] `scripts/validate-skills.py`

Run:
```bash
find /tmp/platform-test -maxdepth 3 -type f | sort
```

**Gate:** all paths above are present.

### 1.3  Verify placeholder substitution

Run:
```bash
grep -r '{{' /tmp/platform-test/ --include='*.json' --include='*.tf' --include='*.bicep' --include='*.yml' --include='*.yaml' --include='*.md'
```

**Gate:** zero matches. Any `{{placeholder}}` still present means substitution failed — identify which placeholder and fix `scripts/scaffold.py` before continuing.

### 1.4  Security audit of generated output

Invoke the `@security-auditor` agent:

> **@security-auditor** — Please use the `security-checklist` skill to review the scaffolded output at `/tmp/platform-test/`. Verify: (1) no raw secrets or credentials in any file, (2) OIDC federated credential patterns are used (no `client_secret` literals), (3) NSG rules in any `.tf` or `.bicep` files do not open port 22 or 3389 to `0.0.0.0/0`, (4) soft-delete/purge protection is enabled on Key Vault and Storage resources. Output: `Security gate: PASSED|FAILED` with a finding list.

**Gate:** `Security gate: PASSED`

### 1.5  Validate generated opencode.json topology

```bash
cd /tmp/platform-test
python3 -m json.tool opencode.json > /dev/null && echo "✅ Generated opencode.json valid"
python3 scripts/validate-skills.py && echo "✅ Generated skill refs valid"
```

**Gate:** both pass.

---

## Phase 2 — Individual agent smoke tests

For each agent below, send the specified minimal prompt and verify the expected output contract is met. These are read-only or dry-run probes — no Azure calls, no real deployment.

### 2.1  `@orchestrator`

> **@orchestrator** — Without taking any actions, describe in one paragraph how you would decompose the following request into milestones: "Add a new Azure SQL module to the Terraform track with private endpoint and diagnostic logging." List which agents you would delegate to and in which order. Output: `## Milestone plan`

**Gate:** response contains `## Milestone plan` and mentions at least `builder-infra-tf`, `verifier`, `security-auditor`, and `test-writer`.

### 2.2  `@explorer`

> **@explorer** — Map the folder structure of `modules/terraform/` and list every `.tf` file found. Report which modules expose `subscription_id` as an input variable. Output: `## Research summary`

**Gate:** response contains `## Research summary` and lists at least one module.

### 2.3  `@builder-infra-tf`

> **@builder-infra-tf** — Draft a minimal Terraform variable block (variables only, no resources) for a new `azure-log-analytics` module. Follow the `code-standards` skill for CAF naming and strict typing (`type = any` is forbidden). Write the block to `/tmp/platform-test/terraform/modules/azure-log-analytics/variables.tf`. Do not create any other files.

**Gate:** file `/tmp/platform-test/terraform/modules/azure-log-analytics/variables.tf` is created; `grep 'any' /tmp/platform-test/terraform/modules/azure-log-analytics/variables.tf` returns nothing.

### 2.4  `@builder-infra-bicep`

> **@builder-infra-bicep** — Draft a minimal Bicep parameter file (`variables.bicepparam` equivalent — a `using` statement + three typed parameters: location, projectName, subscriptionId) for a hypothetical `azure-log-analytics` module. Write to `/tmp/platform-test/bicep/modules/azure-log-analytics/params.bicepparam`. Do not create any other files.

**Gate:** file is created; `grep -i 'any\|object\b' /tmp/platform-test/bicep/modules/azure-log-analytics/params.bicepparam` is empty (no loose types).

### 2.5  `@builder-pipelines`

> **@builder-pipelines** — Draft a minimal GitHub Actions workflow (YAML) that runs `terraform validate` on push to any branch. The job must authenticate via OIDC (no `CLIENT_SECRET`). Write to `/tmp/platform-test/.github/workflows/tf-validate-test.yml`. Do not create any other files.

**Gate:** file is created; `grep -i 'client_secret\|password' /tmp/platform-test/.github/workflows/tf-validate-test.yml` returns nothing; `grep 'id-token: write' /tmp/platform-test/.github/workflows/tf-validate-test.yml` returns a match.

### 2.6  `@verifier`

> **@verifier** — Run `terraform validate` on the module at `/tmp/platform-test/terraform/modules/azure-log-analytics/` (init with `-backend=false` first). Also run `terraform fmt -check`. Output: `Verification: PASSED|FAILED`

**Gate:** response contains `Verification: PASSED` or a clear failure description that identifies a fixable issue. If FAILED, fix the file written in 2.3 and re-run.

### 2.7  `@code-reviewer`

> **@code-reviewer** — Review the file `/tmp/platform-test/terraform/modules/azure-log-analytics/variables.tf` using the `code-standards` skill. Check CAF naming compliance, tagging, strict typing, and variable validation blocks. Output: `Quality gate: PASSED|FAILED`

**Gate:** response contains `Quality gate: PASSED` or identifies specific remediable findings.

### 2.8  `@security-auditor`

> **@security-auditor** — Use the `security-checklist` skill to audit `/tmp/platform-test/.github/workflows/tf-validate-test.yml`. Confirm: OIDC is used, no secrets are hard-coded, `permissions` are minimal (`id-token: write`, `contents: read`). Output: `Security gate: PASSED|FAILED`

**Gate:** `Security gate: PASSED`

### 2.9  `@plan-validator`

> **@plan-validator** — Use the `plan-tracking` skill to evaluate the following synthetic plan JSON (no real Terraform run). Confirm it is safe — no stateful resource is being destroyed or replaced:
>
> ```json
> {
>   "resource_changes": [
>     {"address": "azurerm_resource_group.main", "change": {"actions": ["create"]}},
>     {"address": "azurerm_log_analytics_workspace.main", "change": {"actions": ["create"]}}
>   ]
> }
> ```
>
> Output: `Plan safety gate: PASSED|FAILED`

**Gate:** `Plan safety gate: PASSED`

### 2.10  `@test-writer`

> **@test-writer** — Use the `test-patterns` skill to write a minimal `.tftest.hcl` file for `/tmp/platform-test/terraform/modules/azure-log-analytics/`. The test should assert that the module can be planned without errors using mock provider data. Write to `/tmp/platform-test/terraform/modules/azure-log-analytics/tests/main.tftest.hcl`. Output: `## Test summary`

**Gate:** file is created; response contains `## Test summary`.

### 2.11  `@docs-writer`

> **@docs-writer** — Use the `doc-standards` skill to write a `README.md` for `/tmp/platform-test/terraform/modules/azure-log-analytics/`. Include: purpose, inputs table (from the variables file written in 2.3), outputs (empty for now), and usage example. Write to `/tmp/platform-test/terraform/modules/azure-log-analytics/README.md`. Output: `## Documentation summary`

**Gate:** file is created; response contains `## Documentation summary`.

---

## Phase 3 — Slash command smoke tests

### 3.1  `/audit` — workspace compliance scan

> `/audit`

When the `security-auditor` runs, it should scan the current workspace (the platform repo itself, not `/tmp`).

**Gate:** audit completes and outputs a compliance report. Any HIGH-severity findings must be investigated and either remediated or documented as accepted risk.

### 3.2  `/debug` — synthetic failure probe

Introduce a deliberate syntax error, then invoke debug, then clean up.

```bash
echo 'resource "azurerm_broken" "x" {' >> modules/terraform/azure-keyvault/main.tf
```

> `/debug` — The Terraform module at `modules/terraform/azure-keyvault/` is failing to validate. Diagnose and fix the issue.

**Gate:** the `@verifier` identifies the injected syntax error; the `@builder-infra-tf` fixes it; running `terraform validate` on that module passes afterwards. Verify the file is restored to a clean state.

```bash
# Confirm clean
terraform -chdir=modules/terraform/azure-keyvault validate
```

### 3.3  `/expand` — dry-run design only

> `/expand` — Design (do not implement) the expansion of the landing zone to include a new `azure-storage-account` Terraform module with private endpoint and soft-delete enabled. Produce a `## Milestone plan` and list all files that would be created. Stop before writing any files.

**Gate:** response contains `## Milestone plan` and no new files are written to `modules/` (confirm with `git status`).

### 3.4  `/optimise` — read-only cost scan

> `/optimise` — Scan the current workspace for cost optimisation opportunities. Focus on SKU sizes in the Terraform modules and any hard-coded retention settings. Produce a cost optimisation report. Do not modify any files.

**Gate:** report is produced; `git status` shows no file changes.

### 3.5  `/select-models` — model discovery and proposal

> `/select-models` — Jurisdiction: EU. Focus: cost/quality balance. No local Ollama models available. Discover the live ZEN catalog and propose the optimal model per agent. Present the proposal but do NOT apply it — stop before running `scripts/select-models.py apply`.

**Gate:** proposal table is presented; no changes are written to `opencode.json`.

---

## Phase 4 — End-to-end integrated workflow

This phase exercises the full orchestration chain on a real (but trivial) task.

> **@orchestrator** — I need to add a minimal `azure-storage-account` Terraform module to `modules/terraform/azure-storage-account/`. Requirements: (1) soft-delete enabled, (2) private endpoint input variable (`enable_private_endpoint`, type bool), (3) no `type = any`. Coordinate the full pipeline: delegate implementation to `@builder-infra-tf`, then run `@verifier`, `@code-reviewer`, `@security-auditor`, `@plan-validator`, `@test-writer`, and `@docs-writer` in the correct order. Apply fixes from gate failures before moving to the next gate. After all gates pass, use `@docs-writer` to update `BUILD_JOURNAL.md` with a brief entry for this test run. Output: `## Milestone plan` followed by each gate result.

**Gates (in order):**
- `Verification: PASSED`
- `Quality gate: PASSED`
- `Security gate: PASSED`
- `## Test summary` present
- `## Documentation summary` present
- `BUILD_JOURNAL.md` updated (confirm with `git diff BUILD_JOURNAL.md`)

> **Note:** In the canonical repo, this module is created only as a **temporary system-test artifact** and removed in Phase 5 cleanup so that the main repo state remains unchanged.

---

## Phase 5 — Clean-up

All test artefacts must be removed so the repo returns to its pre-test state.

### 5.1  Remove scaffolded test repo

```bash
rm -rf /tmp/platform-test
echo "✅ /tmp/platform-test removed"
```

### 5.2  Revert any changes to tracked files

```bash
git diff --stat
```

Revert all tracked-file modifications introduced solely for testing (not bug-fixes):

```bash
```

> **Note:** Do NOT revert files that were intentionally fixed during the test (e.g., the syntax error repair in Phase 3.2, or any real bugs discovered). Those should be committed with a conventional commit message.

### 5.3  Remove any new test-only files

```bash
# List untracked files created during the test
```

Remove any files added solely for the test that are not legitimate bug-fixes. Commit any real fixes:

```bash
```

### 5.4  Final validation

```bash
python3 -m json.tool opencode.json > /dev/null && echo "✅ opencode.json valid"
python3 scripts/validate-skills.py && echo "✅ Skills valid"
python3 scripts/validate-team.py && echo "✅ Team topology valid"
```

**Gate:** all three validation scripts pass and `git status` shows only the intentional fix commits (if any). Working tree is clean.

---

## Test result summary

After completing all phases, report results in this table:

| Phase | Description | Result |
|-------|-------------|--------|
| 0 | Pre-flight checks | ✅ |
| 1 | Scaffold + output validation | ✅ |
| 2.1 | `@orchestrator` smoke test | ✅ |
| 2.2 | `@explorer` smoke test | ✅ |
| 2.3 | `@builder-infra-tf` smoke test | ✅ |
| 2.4 | `@builder-infra-bicep` smoke test | ✅ |
| 2.5 | `@builder-pipelines` smoke test | ✅ |
| 2.6 | `@verifier` smoke test | ✅ |
| 2.7 | `@code-reviewer` smoke test | ✅ |
| 2.8 | `@security-auditor` smoke test | ✅ |
| 2.9 | `@plan-validator` smoke test | ✅ |
| 2.10 | `@test-writer` smoke test | ✅ |
| 2.11 | `@docs-writer` smoke test | ✅ |
| 3.1 | `/audit` command | ✅ (HIGH findings investigated; placeholders accepted as test-only risk) |
| 3.2 | `/debug` command | ✅ (injected syntax error detected and repaired, module validates cleanly) |
| 3.3 | `/expand` command | ✅ (design-only, no files written) |
| 3.4 | `/optimise` command | ✅ (read-only cost scan, no file changes) |
| 3.5 | `/select-models` command | ✅ (proposal only, no config changes) |
| 4 | End-to-end orchestrated workflow | ✅ (temporary `azure-storage-account` module passed all gates, then removed in cleanup) |
| 5 | Clean-up — repo in clean state | ✅ |

Any ❌ row must include a one-line description of the failure and the fix applied (or a link to the commit if a code fix was made).

---

## Execution record

**Latest run:**
- **Date:** 2026-06-18
- **Executor:** OpenCode multi-agent team (orchestrator + builders + reviewers) running inside the `opencode-agentic-platform-engineering` repo.
- **Azure connectivity:** No live Azure subscription used. All `terraform init/validate` and `bicep build` steps ran locally with `-backend=false`; any plan evaluations in Phases 2.9 and 4 used **synthetic JSON** rather than real `terraform plan`/`what-if` against Azure.
- **Tooling adjustments during run:**
  - Bicep CLI was installed part-way through Phase 0 to satisfy the Bicep build gate.
  - A temporary `modules/terraform/azure-storage-account/v1` module was created in Phase 4, passed all gates, and was then **removed** in Phase 5 so the repo returned to its pre-test state.
- **Cost/usage:** The run was intentionally designed to be **very low-cost**:
  - No cloud resource creation, no Azure API calls, and no remote backend operations.
  - All work was local compute (editor/CLI + model tokens via OpenCode), which is what the usage graph on the OpenCode workspace reflects.

You can re-run this test end-to-end at any time by following the phases above. Ensure you restore the repo to a clean state at the end to keep subsequent development runs deterministic.

### Example usage & cost (from `opencode stats`)

The following numbers are from a **real run** of this system test, using:

```bash
opencode stats --days 1 --project '' --models
```

> **Important:** These figures are for **all work in this project over the last 1 day** (including this full-system test and any other sessions), not for the test run in isolation. They still give a good sense of the order-of-magnitude cost.

**Overview (last 1 day, current project)**

| Metric                    | Value |
|---------------------------|-------|
| Sessions                  | 57    |
| Messages                  | 440   |
| Days                      | 1     |
| Total Cost                | **$4.71** |
| Avg Cost/Day              | $4.71 |
| Avg Tokens/Session        | 192.3K |
| Median Tokens/Session     | 48.9K |
| Input Tokens              | ~1.2M |
| Output Tokens             | ~98.4K |
| Cache Read Tokens         | ~9.4M |
| Cache Write Tokens        | ~180.3K |

**Top model usage (same window)**

| Model                         | Messages | Input Tokens | Output Tokens | Cache Read | Cost    |
|-------------------------------|----------|--------------|---------------|------------|---------|
| `github-copilot/gpt-5.4`      | 82       | 456.1K       | 40.7K         | 2.4M       | $2.3505 |
| `opencode/gpt-5.1`            | 74       | 233.4K       | 55.1K         | 4.3M       | $1.1751 |
| `opencode/claude-haiku-4-5`   | 71       | 311          | 22.9K         | 1.3M       | $0.4676 |
| `opencode/gpt-5.1-codex`      | 64       | 109.9K       | 25.7K         | 796.7K     | $0.4216 |
| `opencode/gemini-3-flash`     | 57       | 387.2K       | 14.9K         | 500.7K     | $0.2633 |
| `opencode/gpt-5.4-nano`       | 14       | 34.1K        | 7.9K          | 120.3K     | $0.0191 |
| `opencode/gpt-5.1-codex-mini` | 2        | 11.0K        | 5.9K          | 15.6K      | $0.0150 |

Even with multiple agents, smoke tests, and the full end-to-end workflow, the **total model cost for the day stayed under $5**, with no Azure resource costs (no live plans or deployments). This is the expected cost envelope for re-running the full system test periodically.
