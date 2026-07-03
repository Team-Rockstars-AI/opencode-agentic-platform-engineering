# Value-Adds Implementation Plan — Testing, Update Path, Policy Baseline

**Status:** ⏳ PENDING
**Source:** Repository review performed 2026-07-03, identifying the top 3 missing value adds.
**Audience:** This document is self-contained. It is written for an agent with no memory of the review conversation — it does not assume you have read anything except this file and the repo itself.

---

## 0. Context you need before starting

### What this repo is

This repo (`opencode-agentic-platform-engineering`) is a **template/generator repository**. Its product is not itself — its product is the *scaffolded output*: running [`scripts/scaffold.py`](scripts/scaffold.py) generates a new platform-engineering workspace by copying and rendering:

- **Reusable, versioned IaC modules** from `modules/terraform/<name>/v1/` and `modules/bicep/<name>/v1/`. There are currently 4 modules per stack: `azure-keyvault`, `azure-network-baseline`, `azure-oidc-bootstrap`, `azure-private-runner`. Both stacks are kept at **feature parity** — the same platform implemented twice.
- **Composed templates** from `templates/terraform/` and `templates/bicep/` (these contain `{{placeholder}}` tokens like `{{project_name}}` that are substituted at scaffold time — they are *not* valid standalone HCL/JSON and are deliberately excluded from most CI validation).
- **Pipeline templates** from `templates/github/` (→ target `.github/`) and `templates/azure-devops/`.
- **The OpenCode agent team config** from `templates/opencode-config/` (→ target `.opencode/skills/`, `.opencode/prompts/`, `opencode.json`, `manifest.yaml`, `agent_config.py`, and `scripts/validate-skills.py` + `scripts/select-models.py` copied from `templates/opencode-config/scripts/`).
- `templates/AGENTS.md` (→ target `AGENTS.md`), `templates/docs/` (→ target `docs/`).

### Repo conventions you MUST follow

1. **Dual-stack parity:** any capability added to the Terraform stack must also be added to the Bicep stack, and vice versa.
2. **Root/template parity:** the repo has a "root" agent config (`opencode.json`, `.opencode/prompts/`, `skills/`) used to work *on this repo*, and a "template" agent config (`templates/opencode-config/…`) shipped *into scaffolded repos*. New skills get a master copy at `skills/<name>/SKILL.md` **and** a template copy at `templates/opencode-config/skills/<name>/SKILL.md` (see `skills/optimise/` for the format — YAML frontmatter with `name`, `description`, `license: MIT`, `compatibility: opencode`).
3. **Dual CI parity:** Azure DevOps ([`azure-pipelines.yml`](azure-pipelines.yml)) is canonical; GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml), [`.github/workflows/security.yml`](.github/workflows/security.yml)) mirror it. Every CI change must be made **in both** in equivalent form.
4. **Validators must stay green:** `python3 scripts/validate-skills.py` and `python3 scripts/validate-team.py` run in CI and must pass. `validate-team.py` cross-checks agents ↔ prompts ↔ skills ↔ commands ↔ AGENTS.md for both root and template sides. Notably:
   - A command's `template` string containing ``use the `X` skill`` counts as a reference to skill `X` (regex-based).
   - A skill directory not referenced anywhere produces a **warning** (non-fatal); a skill whose `SKILL.md` contains the word "unused" in its first 200 characters is skipped from the orphan check.
   - Both `AGENTS.md` and `templates/AGENTS.md` must mention every agent name in backticks.
5. **Commits:** Conventional Commits (`feat:`, `fix:`, `ci:`, `test:`, `docs:`). Branch off `main` as `feature/<id>-<description>`; never commit to `main` directly.
6. **Backlog tracking:** [`BUILD_PLAN.md`](BUILD_PLAN.md) holds a status table of epics (Epic 2 `/drift` and Epic 3 `/compliance` are pending — do **not** implement those; they are out of scope here). Completed work is journaled in [`BUILD_JOURNAL.md`](BUILD_JOURNAL.md). Add the three value adds below as **Epic 4, Epic 5, Epic 6** rows in the BUILD_PLAN status table when you start, and update statuses/journal as you complete them.
7. **Python:** stdlib-only where possible (scaffold.py is deliberately zero-dependency), Python 3.12 target, ruff with default F+E rules, line length 120 (see [`ruff.toml`](ruff.toml)). Runtime deps go in [`requirements.txt`](requirements.txt) (currently only PyYAML).

### Coordination with the existing remediation plan

[`REMEDIATION_PLAN.md`](REMEDIATION_PLAN.md) (pending) modifies the keyvault, network-baseline, private-runner modules and their tests. **If it has not been executed yet, execute it first** — Work Item 1C below adds tests to the same modules and would otherwise conflict. If it is already done (check: does `modules/terraform/azure-keyvault/v1/main.tf` contain an `azurerm_monitor_diagnostic_setting`?), just proceed.

### CI facts that will bite you if ignored

- The JSON/YAML validation job **skips `templates/`** (placeholder tokens). New files under `templates/` may contain `{{tokens}}`; new files elsewhere must parse cleanly.
- `terraform fmt -check -recursive modules` runs in CI — run `terraform fmt -recursive modules` before committing.
- `python -m compileall -q scripts agent_config.py templates` runs in CI — every `.py` you add under `scripts/` or `templates/` must byte-compile on 3.12.
- Bandit gates on HIGH severity over `scripts`, `agent_config.py`, `templates`. `subprocess` use is fine (scaffold.py already uses it) but avoid `shell=True`.
- Terraform version in CI is **1.9.5** (supports `terraform test` and `mock_provider`, both used below).
- Bicep builds run via `az bicep build`.
- CI module validation is glob-driven (`modules/terraform/*/v*/` and `modules/bicep/**/main.bicep`), so **new modules are picked up automatically** for validate/build — but *test* execution steps do not exist yet (Work Item 1C adds them).

### Verification commands (run after each work item, and again at the end)

```bash
ruff check .
python -m compileall -q scripts agent_config.py templates
python3 scripts/validate-skills.py
python3 scripts/validate-team.py
python3 -m json.tool opencode.json > /dev/null
python3 -m pytest tests/ -v                # exists after Work Item 1A
terraform fmt -check -recursive modules
for d in modules/terraform/*/v1/; do (cd "$d" && terraform init -backend=false -input=false >/dev/null && terraform validate); done
for d in modules/terraform/*/v1/; do if [ -d "$d/tests" ]; then (cd "$d" && terraform test); fi; done
for f in modules/bicep/*/v1/main.bicep; do az bicep build --file "$f" --stdout > /dev/null; done
for f in modules/bicep/*/v1/tests/*.test.bicep; do az bicep build --file "$f" --stdout > /dev/null; done
```

---

# VALUE ADD 1 (Epic 4): Test the actual product

**Problem:** CI validates this repo statically but never (a) unit-tests the ~1,600 lines of Python tooling, (b) generates a scaffolded workspace to prove the product works, or (c) runs the IaC module tests that exist. 3 of 4 modules have no tests at all, despite `AGENTS.md` claiming modules are tested independently.

This splits into three work items. Do them in order 1A → 1C → 1B.

## Work Item 1A: pytest suite for the Python tooling

**Read first:** `scripts/scaffold.py`, `scripts/validate-skills.py`, `scripts/validate-team.py`, `scripts/select-models.py` (all in full).

**Deliverables:**

1. **`requirements-dev.txt`** (new, repo root):
   ```
   # Development/test dependencies (not shipped to scaffolded repos)
   pytest>=8.0,<9.0
   PyYAML>=6.0.3,<7.0
   ```

2. **`tests/`** directory at repo root containing:
   - `tests/__init__.py` (empty)
   - `tests/conftest.py` — shared helpers:
     ```python
     import importlib.util
     import sys
     from pathlib import Path

     REPO_ROOT = Path(__file__).resolve().parent.parent

     def load_script(filename: str):
         """Import a scripts/*.py file despite hyphens in its name."""
         path = REPO_ROOT / "scripts" / filename
         mod_name = filename.replace("-", "_").removesuffix(".py")
         spec = importlib.util.spec_from_file_location(mod_name, path)
         module = importlib.util.module_from_spec(spec)
         sys.modules[mod_name] = module
         spec.loader.exec_module(module)
         return module
     ```
     Plus a `scaffold(tmp_path, **overrides)` fixture/helper that runs scaffold.py as a **subprocess** (do not import-and-call `main()` — it reads `sys.argv`):
     ```python
     import subprocess, sys

     def run_scaffold(target_dir, *extra_args):
         cmd = [sys.executable, str(REPO_ROOT / "scripts" / "scaffold.py"),
                "--non-interactive", "--target-dir", str(target_dir), *extra_args]
         return subprocess.run(cmd, capture_output=True, text=True, check=False)
     ```

   - `tests/test_scaffold.py` — the highest-value tests. Scaffold into `tmp_path` and assert on the output. All CLI flags exist already: `-i/--iac-framework {terraform,bicep,both}`, `-d/--devops-platform {github,azure-devops}`, `-g/--governance-tier {basic,enterprise}`, `-p/--project-name`, `-t/--target-dir`, `-l/--azure-location`, `-s/--subscription-id`, `--tenant-id`, `--github-org-repo`, `--github-runner-pool`, `--ado-runner-pool`, `--non-interactive`. With `--non-interactive`, defaults are: `both`/`github`/`basic`/`platform-core`/`eastus2`/zero-GUIDs/`placeholder-org`/`ubuntu-latest`. Cover at minimum:
     - terraform+github+basic: target contains `terraform/`, `modules/terraform/`, `.github/`, `.opencode/skills/`, `.opencode/prompts/`, `opencode.json`, `manifest.yaml`, `AGENTS.md`, `agent_config.py`, `scripts/validate-skills.py`, `.gitignore`, `.pre-commit-config.yaml`; and does **not** contain `bicep/` or `azure-pipelines.yml`.
     - bicep+azure-devops+basic: contains `bicep/`, `modules/bicep/`, azure-devops pipeline files; no `terraform/`, no `.github/`.
     - Placeholder resolution: no file in the target contains a scaffold token. Check with regex `\{\{[a-z_]+\}\}` (NOT a bare `{{` search — generated GitHub workflows legitimately contain `${{ github.… }}` expressions, which the `[a-z_]+`-only pattern does not match because of spaces/dots). Also assert a known substitution landed, e.g. the project name appears in `terraform/variables.tf` or `opencode.json`.
     - Module path rewrite: files referencing `../../modules/` in templates are rewritten to `../modules/` in the target (see `replace_placeholders_and_paths`).
     - `.opencode-scaffold.json` metadata files are removed from the target (see `cleanup_unused`).
     - Git init: target contains `.git/` and `git -C <target> log --oneline` shows the initial commit.
     - `--github-org-repo org/name` splits correctly; bare `org` (no slash) uses project name as repo.
     - Generated `opencode.json` parses as JSON; generated YAML pipeline files parse with `yaml.safe_load_all`.
   - `tests/test_validate_skills.py` and `tests/test_validate_team.py` — two kinds of tests:
     - Run each script as a subprocess against the real repo and assert exit code 0 (they are read-only). This doubles as a regression net.
     - Unit-test pure functions via `load_script`: e.g. `validate-team.py`'s `find_skill_refs("Please use the `audit` skill") == {"audit"}` and `skill_exists(...)` against a `tmp_path` fixture tree.
   - `tests/test_select_models.py` — **no network calls in tests.** Read `scripts/select-models.py` first and unit-test its pure functions only (jurisdiction inference from model ids, tier/agent mapping, pricing-cache parsing of `scripts/.zen-pricing-cache.json` — pick whatever pure helpers actually exist). If a function fetches URLs, do not call it; test the parsing layer with fixture data instead.

3. **CI wiring (both files):**
   - `azure-pipelines.yml`, job `PythonLintAndSkills`: extend the install step with `pip install -r requirements-dev.txt`, and add after the validate-team step:
     ```yaml
     - bash: |
         set -euo pipefail
         python -m pytest tests/ -v
       displayName: Python unit tests (pytest)
     ```
   - `.github/workflows/ci.yml`, job `python`: same two additions in GitHub Actions form.

4. **Housekeeping:** ensure `.gitignore` covers `.pytest_cache/` (it likely already does — check); update the README "Verification & Quality Checks" section to include `python3 -m pytest tests/`.

**Acceptance:** `python3 -m pytest tests/ -v` passes locally with ≥ 15 tests; `ruff check .` clean; both CI files updated.

## Work Item 1C: IaC module test parity + run the tests in CI

**Read first:** each module's `main.tf` / `main.bicep` in full (assertions below must be adapted to the actual resource names you find), plus the existing test pattern files `modules/terraform/azure-keyvault/v1/tests/main.tftest.hcl` and `modules/bicep/azure-keyvault/v1/tests/main.test.bicep`, and `skills/test-patterns/SKILL.md`.

**Critical technique — provider mocking:** CI has no Azure credentials. A plain `terraform test` with `command = plan` will fail because the `azurerm` provider tries to authenticate. Terraform ≥ 1.7 (CI uses 1.9.5) supports `mock_provider`. Every `.tftest.hcl` file (including the **existing keyvault one — update it too**) must start with:

```hcl
mock_provider "azurerm" {}
```

Then `run` blocks with `command = plan` work offline. Verify locally with `cd modules/terraform/azure-keyvault/v1 && terraform init -backend=false && terraform test` before writing the others.

**Deliverables:**

1. **`modules/terraform/azure-network-baseline/v1/tests/main.tftest.hcl`** — variables block needs at least `project_name`, `location`, `resource_group_name` (see `variables.tf`; `environment` defaults to `dev`, `is_enterprise` to `false`). Assert (adapt to actual resource addresses in `main.tf`):
   - The Application Gateway SKU is `WAF_v2` (security baseline; grep `main.tf` for the `sku` block to get the exact address).
   - The runners subnet / KEDA resources are created only when `is_enterprise = true` (two run blocks: default expects count/length 0, `is_enterprise = true` expects ≥ 1).
   - With `log_analytics_workspace_id` set to a fake id (`/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-x/providers/Microsoft.OperationalInsights/workspaces/law-x`), the diagnostic-setting count is 1; unset, 0.
2. **`modules/terraform/azure-oidc-bootstrap/v1/tests/main.tftest.hcl`** — requires `project_name`, `location`, `resource_group_name`, and `subscription_scope_id` matching `^/subscriptions/<guid>$` (use the zero GUID). Assert the user-assigned identity name derives from `project_name`, and federated credential resources reference `github_org_name`/`github_repo_name` when set.
3. **`modules/terraform/azure-private-runner/v1/tests/main.tftest.hcl`** — requires `project_name`, `location`, `resource_group_name`, `subnet_runners_id` (fake resource id). Assert scale-to-zero (`min_replicas`/minimum replica setting is 0 by default) and that `runner_token` is marked sensitive (assert on a plan value or simply that the container app env wiring exists — adapt to `main.tf`).
4. **Bicep test files** — `modules/bicep/azure-network-baseline/v1/tests/main.test.bicep`, `…/azure-oidc-bootstrap/v1/tests/main.test.bicep`, `…/azure-private-runner/v1/tests/main.test.bicep`, following the keyvault pattern (a `module` invocation of `../main.bicep` with plausible params; the "test" is that it compiles). Read each `main.bicep` for its required params first. Include a second module invocation exercising a non-default path (e.g. `isEnterprise: true`, or a `logAnalyticsWorkspaceId`).
5. **CI wiring (both files):**
   - `azure-pipelines.yml`, stage `Validate`, job `IaCValidate`: after the "Terraform module validation" step add:
     ```yaml
     - bash: |
         set -euo pipefail
         shopt -s nullglob
         for module_dir in modules/terraform/*/v*/; do
           if [ -d "${module_dir}tests" ]; then
             echo "Testing Terraform module: ${module_dir%/}"
             (cd "$module_dir" && terraform init -backend=false -input=false && terraform test)
           fi
         done
       displayName: Terraform module tests (terraform test)
     ```
     And after the Bicep build step:
     ```yaml
     - bash: |
         set -euo pipefail
         shopt -s globstar nullglob
         for file in modules/bicep/**/tests/*.test.bicep; do
           echo "Building Bicep test: $file"
           az bicep build --file "$file" --stdout >/dev/null
         done
       displayName: Bicep module test builds
     ```
   - `.github/workflows/ci.yml`: the GitHub CI currently has **no** terraform-validate/bicep job at all (only fmt). Add a new job `iac-tests` mirroring the ADO `IaCValidate` job (module validate + terraform test + bicep build + bicep test builds), using `hashicorp/setup-terraform@v3` with `terraform_version: "1.9.5"` and `az bicep install`.
6. **Docs:** update the README "Automated checks on every pull request" table with a "IaC module tests" row; mention `terraform test` in the Verification section.

**Acceptance:** all 4 terraform modules pass `terraform test` offline; all bicep test files build; CI runs them on both platforms.

## Work Item 1B: End-to-end scaffold verification in CI

**Goal:** CI generates real workspaces and validates them — proving the *product* works, not just the template source.

**Deliverables:**

1. **`scripts/verify-scaffold-output.sh`** (new, bash, executable) so the logic lives in one place and both CI platforms just call it. Signature: `verify-scaffold-output.sh <iac> <devops> <tier>`. It must:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   IAC="$1"; DEVOPS="$2"; TIER="$3"
   TARGET="$(mktemp -d)/out"
   python3 scripts/scaffold.py --non-interactive \
     -i "$IAC" -d "$DEVOPS" -g "$TIER" \
     -p e2e-check -l westeurope -t "$TARGET"

   # 1. No unresolved scaffold placeholders (pattern deliberately excludes ${{ github.x }} expressions)
   if grep -rnE '\{\{[a-z_]+\}\}' "$TARGET" --exclude-dir=.git; then
     echo "Unresolved placeholders found"; exit 1
   fi
   # 2. Generated config parses and its skills resolve
   python3 -m json.tool "$TARGET/opencode.json" > /dev/null
   (cd "$TARGET" && python3 scripts/validate-skills.py)
   # 3. Generated YAML parses
   python3 - "$TARGET" <<'PY'
   import pathlib, sys, yaml
   root = pathlib.Path(sys.argv[1])
   for p in list(root.rglob("*.yml")) + list(root.rglob("*.yaml")):
       if ".git" in p.parts: continue
       list(yaml.safe_load_all(p.read_text(encoding="utf-8")))
   print("YAML OK")
   PY
   # 4. IaC actually compiles after rendering
   if [ -d "$TARGET/terraform" ]; then
     (cd "$TARGET/terraform" && terraform init -backend=false -input=false && terraform validate)
   fi
   if [ -d "$TARGET/bicep" ]; then
     for f in "$TARGET"/bicep/main.bicep "$TARGET"/bicep/**/main.bicep; do
       [ -f "$f" ] && az bicep build --file "$f" --stdout > /dev/null
     done
   fi
   echo "E2E scaffold verification passed: $IAC/$DEVOPS/$TIER"
   ```
   **Before finalizing this script, run it locally for each combo and adapt:** confirm the generated `terraform/` layout (`backend.tf` has placeholders resolved; `-backend=false` avoids needing real state), confirm the bicep entrypoint path(s) by inspecting `templates/bicep/` (there is a `templates/bicep/modules/` dir; find the actual root `.bicep` entrypoint and glob accordingly), and confirm `validate-skills.py` works from inside a generated repo (it is shipped there by design). Where a check cannot pass for a legitimate structural reason, adjust the script — the four combos below **must end green with real assertions, not skipped ones**.
2. **CI matrix — 4 combos** (keeps runtime sane while covering every axis value): `terraform/github/basic`, `bicep/azure-devops/basic`, `both/github/enterprise`, `both/azure-devops/enterprise`.
   - `.github/workflows/ci.yml`: new job `scaffold-e2e` with a `strategy.matrix.include` list of the 4 combos; steps: checkout, setup-python 3.12, `pip install -r requirements.txt`, setup-terraform 1.9.5, install az bicep, `bash scripts/verify-scaffold-output.sh ${{ matrix.iac }} ${{ matrix.devops }} ${{ matrix.tier }}`. Git is preinstalled on runners; scaffold.py's `initialize_git` sets its own fallback user.name/email, so no git config step is needed.
   - `azure-pipelines.yml`: new job `ScaffoldE2E` in the `Validate` stage using a `strategy: matrix:` with the same 4 combos and equivalent steps.
3. **Docs:** add the E2E row to the README CI table.

**Acceptance:** all 4 combos pass locally and in CI on both platforms.

---

# VALUE ADD 2 (Epic 5): `/update` — template sync for already-scaffolded repos

**Problem:** once scaffolded, a workspace is orphaned. `scaffold.py` records nothing about which template version produced it, and no mechanism exists to pull upstream improvements (module fixes, new skills, security patches) into existing repos. Every fix landed here never reaches consumers.

**Design (three-way sync, stdlib-only):**
1. At scaffold time, stamp the target with the template version, the exact inputs used, and a hash manifest of every generated file.
2. Later, `update.py` in the scaffolded repo re-renders the templates at the *new* template version using the recorded inputs, and classifies each file by comparing three states: original render (hash in stamp), current file on disk, new render.

**Read first:** `scripts/scaffold.py` (in full — you will modify it), `templates/opencode-config/opencode.json` (command registration format), `skills/optimise/SKILL.md` (skill format), `scripts/validate-team.py` (to understand what the new skill/command must satisfy).

## Deliverables

### 2.1 Stamp file written by scaffold.py

Modify `scripts/scaffold.py`:

1. Add `--no-git` flag (`action="store_true"`) that skips `initialize_git` — needed so `update.py` can re-render without creating nested git repos, and useful for tests.
2. After `cleanup_unused(...)` and before git init, write **`.platform-scaffold.json`** at the target root:
   ```json
   {
     "schema_version": 1,
     "template_repo": "<git config --get remote.origin.url of this repo, or 'unknown'>",
     "template_commit": "<git rev-parse HEAD of this repo, or 'unknown'>",
     "scaffolded_at": "<UTC ISO-8601>",
     "inputs": {
       "iac_framework": "...", "devops_platform": "...", "governance_tier": "...",
       "project_name": "...", "azure_location": "...", "subscription_id": "...",
       "tenant_id": "...", "github_org_name": "...", "github_repo_name": "...",
       "github_runner_pool": "...", "ado_runner_pool": "..."
     },
     "files": { "<relative/path>": "sha256:<hex>", "...": "..." }
   }
   ```
   - Get commit/remote via `subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root, ...)` with graceful fallback to `"unknown"` (this repo may be a tarball).
   - The `files` manifest: walk the target, skip `.git/` and the stamp file itself, hash file bytes with `hashlib.sha256`. Compute **after** placeholder substitution so hashes reflect what the user actually received.
   - Use `json.dump(..., indent=2, sort_keys=True)` for deterministic output.
3. The stamp gets committed by the existing `initialize_git` step automatically (it runs `git add .`).

### 2.2 `update.py` shipped into scaffolded repos

Create **`templates/opencode-config/scripts/update.py`** (this directory is where scaffold.py already sources `validate-skills.py` and `select-models.py` from), and add a copy line in `scaffold.py` step 4 alongside those two:

```python
copy_file(os.path.join(config_src, "scripts", "update.py"), os.path.join(target_dir, "scripts", "update.py"))
```

`update.py` requirements (stdlib only, mirror scaffold.py's style):

- CLI: `python3 scripts/update.py --template-path <path-to-local-clone-of-template-repo> [--dry-run] [--report-path docs/reports]`. The template repo is fetched by the *user/agent* (git clone/pull) — update.py does no network I/O itself.
- Steps:
  1. Load `.platform-scaffold.json` from the current repo root; abort with a clear message if missing ("this repo was scaffolded before stamping existed — re-scaffold or create the stamp manually").
  2. Record the new template version: `git -C <template-path> rev-parse HEAD`. If identical to `template_commit` in the stamp, report "already up to date" and exit 0.
  3. Re-render: run `<template-path>/scripts/scaffold.py --non-interactive --no-git` into a `tempfile.mkdtemp()` target, passing every recorded input as CLI flags (`-i`, `-d`, `-g`, `-p`, `-l`, `-s`, `--tenant-id`, `--github-org-repo org/repo`, `--github-runner-pool`, `--ado-runner-pool`).
  4. Classify every path in the union of {stamp manifest, new render, current tree}:
     | Original (stamp) | Current disk | New render | Classification | Action |
     |---|---|---|---|---|
     | hash A | hash A (unmodified) | hash A | `unchanged` | none |
     | hash A | hash A (unmodified) | hash B | `auto-update` | copy new file over current |
     | hash A | hash C (user-modified) | hash A | `user-modified` | keep user's file |
     | hash A | hash C (user-modified) | hash B | **`conflict`** | do NOT touch; list for manual/agent merge |
     | absent | any/absent | present | `new-file` | copy in (unless a file already exists at that path → `conflict`) |
     | hash A | absent (user deleted) | any | `user-deleted` | skip, note in report |
     | hash A | hash A | absent | `removed-upstream` | delete file |
  5. `--dry-run` prints the classification table and changes nothing. Without it, apply `auto-update`/`new-file`/`removed-upstream`, then rewrite `.platform-scaffold.json` with the new `template_commit`, new timestamp, and a refreshed manifest in which **auto-updated files get the new hash but user-modified/conflict files keep their *original* stamp hash** (so they remain detectable as modified next run). Never `git commit` — leave staging to the operator/agents.
  6. Write a markdown report to `docs/reports/update-report-<YYYY-MM-DD>.md` listing counts and per-file classifications, with a "Conflicts requiring manual merge" section at the top.
- Exit codes: 0 = success/no-op, 1 = fatal error, 2 = success-with-conflicts (so agents can branch on it).

### 2.3 Report template

Create `templates/docs/reports/update-report-template.md` following the style of the existing `templates/docs/reports/cost-optimisation-template.md` (read it first): header with template versions (old → new commit), summary counts, then sections *Auto-updated*, *New files*, *Removed upstream*, *Conflicts (manual merge required)*, *Skipped (user-deleted)*.

### 2.4 `update` skill + `/update` command

1. **`skills/update/SKILL.md`** (master copy). Frontmatter `name: update`, and a `description` that **contains the word "unused"** phrased naturally, e.g. `description: Template-update workflow shipped to provisioned repos (unused in this provisioning repo itself)` — this keeps `validate-team.py`'s root orphan-skill check quiet, since no root prompt/command references it. Body: step-by-step operator/agent procedure — clone/pull the template repo, run `update.py --dry-run`, review the classification, run for real, then for each **conflict** instruct the agents: `@explorer` diffs the three versions, the matching builder (`@builder-infra-tf` / `@builder-infra-bicep` / `@builder-pipelines`) merges upstream changes into the user-modified file, `@verifier` re-runs `terraform validate`/`bicep build`, `@security-auditor` reviews merged security-relevant files, and `@docs-writer` finalizes the update report. Include the safety rule: **never auto-merge conflicts in `*.tfvars`, `backend.tf`, or pipeline credential/OIDC config — always surface those to the human operator.**
2. **`templates/opencode-config/skills/update/SKILL.md`** (template copy, same content minus the "unused" note — in provisioned repos it *is* used).
3. **`templates/opencode-config/opencode.json`**: add to the `command` object (match the existing entries' shape exactly — `description`, `agent`, `template`):
   ```json
   "update": {
     "description": "Sync this scaffolded repository with the latest upstream platform template version.",
     "agent": "orchestrator",
     "template": "Please use the `update` skill. Ask the user for the local path (or git URL to clone) of the upstream template repository, run `python3 scripts/update.py --dry-run` first, present the classification summary for approval, then apply and coordinate conflict merges between the builders, verifier, and security-auditor. Finish by having the docs-writer complete the update report."
   }
   ```
   Do **not** add `/update` to the root `opencode.json` — running it inside the template repo itself is meaningless.
4. **Docs:** document `/update` and the stamp file in `templates/AGENTS.md` (command list) and in `docs/operator-manual-provisioned-platform.md` (new section "Keeping your platform up to date"); add a short "Updating scaffolded repos" subsection to the root `README.md`.

### 2.5 Tests (extends Work Item 1A's suite)

`tests/test_update.py`:
- Scaffold repo A into `tmp_path` (subprocess, `--no-git` for speed where git isn't needed; at least one test WITH git to confirm the stamp is committed). Assert `.platform-scaffold.json` exists, parses, `schema_version == 1`, inputs echo the flags, and ≥ 1 manifest entry's sha256 matches a recomputation.
- Update no-op: run `update.py --template-path <this repo> --dry-run` inside a fresh scaffold → "already up to date" path requires the template commit to differ, so instead assert exit 0 and zero conflicts when nothing changed. (If HEAD equals the stamp commit, assert the up-to-date short-circuit.)
- Auto-update path: scaffold; then simulate an upstream change by scaffolding from a *modified copy* of the repo (copy this repo to `tmp_path/template2` excluding `.git`, tweak one template file, `git init && git commit` inside it so rev-parse works); run update; assert the changed file was updated and the stamp's `template_commit` moved.
- Conflict path: scaffold, modify a generated file locally, run update against the modified template; assert exit code 2, file untouched, conflict listed in the report.
- User-deleted path: delete a generated file, update, assert it is not recreated and is reported.

**Acceptance:** all validators green (`validate-team.py` shows the new command → agent and skill references resolving), pytest suite passes including `test_update.py`, and a full manual round-trip works:

```bash
python3 scripts/scaffold.py --non-interactive -p demo -t /tmp/demo-update-check
cd /tmp/demo-update-check && python3 scripts/update.py --template-path <path-to-this-repo> --dry-run
```

---

# VALUE ADD 3 (Epic 6): `azure-policy-baseline` module — runtime governance enforcement

**Problem:** the repo's GDPR/DORA/BIO/NEN 7510 compliance posture is enforced only at authoring time (agent audits, Checkov, checklists). There is not a single Azure Policy definition or assignment in `modules/` or `templates/` — nothing prevents clickops or workload teams from creating a public storage account or non-EU resource *after* deployment. Ship a policy-baseline module assigning built-in Azure policies at subscription scope, wired into both composed templates.

**Read first:** `modules/terraform/azure-keyvault/v1/` (all files — the module conventions: `main.tf`, `variables.tf`, `outputs.tf`, `README.md` with Usage/Inputs/Outputs tables), one Bicep module (`modules/bicep/azure-network-baseline/v1/main.bicep`), the composed templates `templates/terraform/main.tf` + `templates/terraform/variables.tf` and `templates/bicep/` (find its root entrypoint and how `templates/bicep/modules/keyvault.bicep` is composed), `skills/code-standards/SKILL.md` (tagging standards — informs the required-tags default), and `docs/compliance-mapping-guide.md` (you will extend it).

## Policy set (v1 scope — keep it to these six)

Assign **built-in** policy definitions only (no custom definitions in v1). Reference them by definition GUID under `/providers/Microsoft.Authorization/policyDefinitions/<guid>`.

> ⚠️ **Verify every GUID before use** against Microsoft Learn ("Azure Policy built-in definitions") or `az policy definition list --query "[?displayName=='<name>'].name" -o tsv`. The GUIDs below are from memory and may be wrong; the **display names are canonical**. `terraform validate`/`bicep build` in CI will NOT catch a wrong GUID.

| # | Built-in policy (display name) | Likely GUID (VERIFY) | Effect | Why |
|---|---|---|---|---|
| 1 | Allowed locations | `e56962a6-4747-49cd-b67b-bf8b01975c4c` | deny | Data residency (GDPR/sovereignty); parameterized list, default `["westeurope", "northeurope"]` |
| 2 | Secure transfer to storage accounts should be enabled | `404c3081-a854-4457-ae30-26a93ef643f9` | audit/deny | Encryption in transit |
| 3 | Storage accounts should disable public network access | `b2982f36-99f2-4db5-8eff-283140c09693` | audit | Private-endpoint-only posture |
| 4 | Azure Key Vault should disable public network access | `405c5871-3e91-4644-8a63-58e19d68ff5b` | audit | Matches the KV module's private-link design |
| 5 | Key vaults should have deletion protection enabled (purge protection) | `0b60c0b2-2dc2-4e1c-b5c9-abbed971de53` | audit | Matches the non-negotiable purge-protection baseline in `skills/optimise/SKILL.md` |
| 6 | Network interfaces should not have public IPs | `83a86a26-fd1f-447c-b59d-e51f44264114` | deny | Enforces the NAT-Gateway-only egress design |

## Deliverables

### 3.1 `modules/terraform/azure-policy-baseline/v1/`

- `variables.tf`: follow existing conventions exactly (validation blocks, descriptions). Variables:
  - `project_name` (same validation as other modules), `environment` (dev/test/prod, default `dev`),
  - `subscription_id` (GUID-validated; used to build the assignment scope `/subscriptions/<id>`),
  - `allowed_locations` (list(string), default `["westeurope", "northeurope"]`, validation: length ≥ 1),
  - `enforcement_mode` (bool, default `true`; description: "false sets DoNotEnforce — assignments evaluate and report but do not block"),
  - `enable_deny_public_ip_nics` (bool, default `true`) — the one policy most likely to need an opt-out (the AppGW public frontend lives in a managed context, but VERIFY during testing that assignment at subscription scope doesn't break the composed template's AppGW; if it does, default it `false` and document why),
  - `tags` (map(string), default `{}`) — note: policy assignments don't take tags, but keep the variable if metadata supports it; otherwise omit.
- `main.tf`: six `azurerm_subscription_policy_assignment` resources. Pattern:
  ```hcl
  resource "azurerm_subscription_policy_assignment" "allowed_locations" {
    name                 = "pa-allowed-locations-${var.project_name}"
    subscription_id      = "/subscriptions/${var.subscription_id}"
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/e56962a6-4747-49cd-b67b-bf8b01975c4c"
    display_name         = "Allowed locations (${var.project_name})"
    description          = "Restrict resource deployment to approved EU regions."
    enforce              = var.enforcement_mode
    parameters = jsonencode({
      listOfAllowedLocations = { value = var.allowed_locations }
    })
  }
  ```
  (Check each built-in's exact parameter names when verifying GUIDs; several of the audit policies take an `effect` parameter — pass it explicitly where available.) Assignment `name` has a 24-char limit for some scopes and 64 for subscription assignments — keep names short and static-prefix + project.
- `outputs.tf`: map of assignment ids.
- `README.md`: Usage/Inputs/Outputs in the same table format as `modules/terraform/azure-keyvault/v1/README.md`, plus a "Policies enforced" table and a warning that `enforce = true` affects the whole subscription.
- `tests/main.tftest.hcl`: `mock_provider "azurerm" {}`; run blocks asserting (a) plan succeeds with defaults and creates 6 assignments, (b) `enable_deny_public_ip_nics = false` drops to 5, (c) `allowed_locations` propagates into the `parameters` JSON of the allowed-locations assignment, (d) `enforcement_mode = false` sets `enforce = false`.

### 3.2 `modules/bicep/azure-policy-baseline/v1/`

- `main.bicep` with `targetScope = 'subscription'`, params mirroring the Terraform variables (camelCase: `projectName`, `allowedLocations`, `enforcementMode`, `enableDenyPublicIpNics`), six `Microsoft.Authorization/policyAssignments@2022-06-01` resources (use whatever API version the other bicep modules' patterns suggest is current; `az bicep build` will warn if stale), `enforcementMode: enforcementMode ? 'Default' : 'DoNotEnforce'`, conditional deploy on the NIC policy. Outputs: assignment ids.
- `README.md` mirroring the Terraform one.
- `tests/main.test.bicep`: two module invocations (defaults; and `enforcementMode: false` + `enableDenyPublicIpNics: false`). **Note:** since `main.bicep` is subscription-scoped, the test file must also set `targetScope = 'subscription'` — confirm it compiles with `az bicep build`.

### 3.3 Wire into the composed templates

- `templates/terraform/`: new `policy.tf` calling `../../modules/terraform/azure-policy-baseline/v1` (this relative path is auto-rewritten to `../modules/` at scaffold time — match how `templates/terraform/main.tf` sources the other modules; read it first). Pass `subscription_id = "{{subscription_id}}"`-derived variable (check how existing template vars consume the placeholder — likely via `variables.tf` defaults), `environment = var.environment`, and add template-level variables `policy_allowed_locations` (default `["{{azure_location}}"]` — think: the scaffold's chosen region must be allowed by default or nothing can deploy; add `westeurope`/`northeurope`? No — default to `[var.location]` composed with the existing location variable if one exists; keep it simple and correct) and `policy_enforcement_mode` (default: `true` when `var.environment == "prod"`, else expose plainly with default `false` — audit-only in dev/test, enforce in prod; implement as a plain variable with description, not magic).
- `templates/bicep/`: equivalent composition. The root deployment's scope matters — if the existing bicep template deploys at resource-group scope, the policy module needs a subscription-scope deployment; read the entrypoint first and follow whatever pattern `azure-oidc-bootstrap` composition uses (it likely also needs subscription scope for role assignments). If the composition entrypoint is already subscription-scoped, it's a plain `module` reference.
- Both compositions are placeholder-bearing template files → CI's fmt/validate skips them (correct, expected). The E2E job from Work Item 1B is what proves they render into valid IaC — after this work item, re-run the 4 E2E combos locally.

### 3.4 Docs & governance bookkeeping

- `docs/compliance-mapping-guide.md`: add a section mapping each of the six policies to the regulatory articles the guide already cites (follow its existing table structure). Only claim what is now true: assignments are audit-mode by default outside prod.
- `docs/architecture-blueprint.md`: short "Policy guardrails" subsection.
- `README.md`: add the module to the feature list.
- `AGENTS.md` + `templates/AGENTS.md`: add `azure-policy-baseline` wherever the module inventory/enforced-structure is described.
- `skills/security-checklist/SKILL.md` + template copy: add one checklist item: "Azure Policy baseline assigned at subscription scope (allowed locations, storage/KV public-access, secure transfer, purge protection, NIC public IPs)".

**Acceptance:** new module passes `terraform init/validate/test` and `az bicep build` (module + tests) locally; CI globs pick it up; E2E combos still green; GUIDs verified against Microsoft docs (note the verification source in the PR/commit body); docs updated.

---

## Execution order

1. **Prerequisite:** complete `REMEDIATION_PLAN.md` if still pending (check its Status header and the keyvault module for `azurerm_monitor_diagnostic_setting`).
2. **Epic 4a** — Work Item 1A (pytest infra). Everything later reuses it.
3. **Epic 4b** — Work Item 1C (module tests + CI test execution).
4. **Epic 4c** — Work Item 1B (E2E scaffold CI).
5. **Epic 5** — Value Add 2 (stamp + update.py + skill/command + tests).
6. **Epic 6** — Value Add 3 (policy baseline module + composition + docs). Re-run the E2E script for all 4 combos at the end.

One branch + PR per epic (`feature/epic4-test-the-product`, `feature/epic5-template-update`, `feature/epic6-policy-baseline`), conventional commits throughout. Update the `BUILD_PLAN.md` status table and `BUILD_JOURNAL.md` as each epic lands.

## Global acceptance criteria

- [ ] All commands in §0 "Verification commands" pass locally.
- [ ] Both CI definitions (`azure-pipelines.yml` and `.github/workflows/ci.yml`) updated in lockstep for every new check.
- [ ] `validate-team.py` exits 0 with no new errors (warnings acceptable only if pre-existing).
- [ ] Root/template parity: every new skill exists in both `skills/` and `templates/opencode-config/skills/`; `/update` command registered in the template `opencode.json` only.
- [ ] Dual-stack parity: Terraform and Bicep both gained the policy module, module tests, and composition wiring.
- [ ] No file outside `templates/` contains unresolved `{{placeholder}}` tokens.
- [ ] README, AGENTS.md (both), and the docs guides reflect every new capability — no doc claims anything not actually implemented.
