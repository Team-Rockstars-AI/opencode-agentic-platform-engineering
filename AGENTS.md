# Platform Engineer — Agent Instructions

## Purpose

This repo scaffolds opinionated platform-engineering repositories. A user clones it, answers prompts (IaC framework, repo source, DevOps flow, governance model), and out comes a new repo pre-populated with an OpenCode agent team, workflows, and docs for building/running/hosting on Azure securely.

## Canonical CI/CD & Git Hosting

Azure DevOps (ADO) is the canonical home for this repository.
- **Git Host:** The primary repository resides in Azure DevOps. GitHub is maintained as a manually updated mirror.
- **CI/CD:** The root-level `azure-pipelines.yml` is the authoritative CI pipeline. It performs static validation only (Python linting, config validation, Terraform/Bicep linting, secret scanning, and SAST). It does **not** perform Azure login, plan/apply, or deployments.
- **GitHub Mirroring:** GitHub continues to run `.github/workflows/ci.yml` and `.github/workflows/security.yml` for visibility and mirror health. Contributors must not push directly to the GitHub mirror; all changes must flow through the Azure DevOps repository.

## Enforced structure

```
opencode.json              # Entry point — defines agents, skills, MCP servers
AGENTS.md                  # This file
.opencode/prompts/         # Adapted system prompt files (.txt) loaded by agents
skills/                    # Reusable skill definitions invoked by agents
workflows/                 # Slash-command workflow definitions
templates/                 # Scaffold output — copied into the target repo
  terraform/               # Terraform project skeleton
  bicep/                   # Bicep project skeleton
  opencode-config/         # Generated opencode.json for the target repo
  github/                  # GitHub workflows, issue templates
  azure-devops/            # Azure DevOps pipelines
modules/                   # Reusable, versioned IaC modules
  terraform/               #   modules/terraform/<module-name>/
  bicep/                   #   modules/bicep/<module-name>/
docs/                      # Repo-level docs (user-facing README, roadmap, etc.)
```

**Rules:**
- `opencode.json` is the sole entry point. Do not scatter config outside it.
- Every file under `.opencode/prompts/`, `skills/`, `workflows/` must be referenced from `opencode.json`.
- Templates mirror the target repo's final layout. They are **copied verbatim**, then post-processed by a workflow.
- `modules/` content is versioned (semver via folder name or git tag) and independently testable.

## Agents & Orchestration Topology

This environment utilizes an advanced **Orchestration-Led multi-agent paradigm** specifically optimized for platform engineering safety, governance, and static compliance analysis.

### Primary Agent
*   **`orchestrator`**: The strategic platform lead. Decouples backlogs, creates architectural blueprints, and delegates task milestones to builders.

### Specialized Implementation Builders
*   **`builder-infra-tf`**: Focuses on high-quality, parameterized Terraform design and modern unit testing via `.tftest.hcl`.
*   **`builder-infra-bicep`**: Handles multi-scope (Tenant, Subscription, Management Group) Bicep resource structures.
*   **`builder-pipelines`**: Responsible for designing secure GitHub Actions workflows and Azure DevOps Pipelines.

### Read-Only Discovery
*   **`explorer`**: Fast read-only codebase navigator for tracing modules, resource references, and folder structures. No file modifications. Output: `## Research summary`

### Read-Only Verification Gates
*   **`verifier`**: Syntactical validation executor (`terraform validate`, `bicep build`, `tflint`). Runs execution plan dry-runs (`terraform plan`, `bicep what-if`). Output: `Verification: PASSED|FAILED`
*   **`code-reviewer`**: Quality gate covering all five WAF pillars: maintainability/correctness, reliability/availability, performance efficiency, cost optimization, and operational excellence. Output: `Quality gate: PASSED|FAILED`
*   **`security-auditor`**: Compliance policy scanner (audits Checkov outputs, TLS standards, private connectivity, and OIDC setups). Output: `Security gate: PASSED|FAILED`
*   **`plan-validator`**: **BLAST RADIUS SAFETY GATE.** Evaluates dry-run execution plan outputs. Blocks immediately if any critical stateful resource (databases, storage networks, keyvaults) is marked for destruction or replacement. Output: `Plan safety gate: PASSED|FAILED`

### Post-Gate Agents
*   **`test-writer`**: Writes sprint-appropriate infrastructure unit and validation tests (`.tftest.hcl`, `tests/main.test.bicep`). Output: `## Test summary`
*   **`docs-writer`**: Updates module READMEs, ADRs, runbooks, BUILD_JOURNAL.md, and DISCOVERIES_LOG.md. Output: `## Documentation summary`

## Reusable Skills (`skills/`)

Reusable capability invoked via `skill` tool. Each skill is a Markdown file with:
1. **Trigger** — what kind of task activates it
2. **Steps** — ordered procedure the agent executes
3. **Output** — what the agent produces (files, decisions)

Skills are the atomic unit of reuse. Prefer extracting a skill when the same procedure appears in two+ agents or workflows.

### Named Skills in Use

| Skill | Directory | Consumed By | Purpose |
|-------|-----------|-------------|---------|
| **`architecture-review`** | `skills/architecture-review/SKILL.md` | `@code-reviewer`, `@orchestrator` | Architectural change review covering subscription topology, network isolation, central state access patterns, and IAM least-privilege standards. |
| **`audit`** | `skills/audit/SKILL.md` | `/audit` workflow | Workspace compliance scan — codebase secrets check, NSG/public-endpoint audit, Private Endpoint verification. Loads `security-checklist` for structured reporting. |
| **`code-standards`** | `skills/code-standards/SKILL.md` | `@code-reviewer`, `@builder-infra-tf`, `@builder-infra-bicep` | CAF naming conventions, Azure Well-Architected Framework alignment (5 pillars), tagging standards, and IaC best practices for Terraform and Bicep. |
| **`commit-format`** | `skills/commit-format/SKILL.md` | `@builder-infra-tf`, `@builder-infra-bicep`, `@builder-pipelines` | Conventional Commits specification enforcing structured commit types, scopes, and description format for automated changelog generation. |
| **`debug`** | `skills/debug/SKILL.md` | `/debug` workflow | Compilation error tracing and resolution. |
| **`doc-standards`** | `skills/doc-standards/SKILL.md` | `@docs-writer` | Documentation standards for module READMEs, ADR format, runbooks, and onboarding guides targeting operations teams and developers. |
| **`drift`** | `skills/drift/SKILL.md` | `@orchestrator`, `@plan-validator` | Detect, classify, and reconcile infrastructure drift against the desired IaC state. |
| **`expand`** | `skills/expand/SKILL.md` | `/expand` workflow | Guided rollout of new IaC resource modules. |
| **`git-workflow`** | `skills/git-workflow/SKILL.md` | `@builder-infra-tf`, `@builder-infra-bicep`, `@builder-pipelines` | Branch naming, pre-commit hygiene (formatter, precision staging), commit blacklist (no secrets, debug artifacts, commented-out code), and standardised handoff summary for `@test-writer`. |
| **`model-optimiser`** | `skills/model-optimiser/SKILL.md` | `/select-models` workflow | Discovers the live OpenCode ZEN catalog + installed Ollama models and reasons over each agent's prompt/skills to select the optimal available model per agent (jurisdiction, cost/quality focus, local hardware). |
| **`optimise`** | `skills/optimise/SKILL.md` | `/optimise` workflow | Static cost and resource optimization review checklist and finding report format. |
| **`plan-tracking`** | `skills/plan-tracking/SKILL.md` | `@plan-validator`, `@docs-writer` | Execution plan JSON conversion, resource action tracking (create/update/delete/replace), milestone status updates, and session state maintenance. |
| **`scaffold`** | `skills/scaffold/SKILL.md` | `/scaffold` workflow | Template selection, copy, placeholder substitution, git init. |
| **`security-checklist`** | `skills/security-checklist/SKILL.md` | `@security-auditor`, `audit` skill | Structured PASS/FAIL/NA review checklist covering OIDC, network isolation, soft-delete, least-privilege IAM, diagnostic logging, strict typing. Produces findings with severity ratings and remediation blocks. |
| **`test-patterns`** | `skills/test-patterns/SKILL.md` | `@test-writer`, `@builder-infra-tf` | Unit and validation test guidelines for Terraform (.tftest.hcl) and Bicep modules, including plan assertions and what-if validation patterns. |

## Workflows (`workflows/`)

Documentation-only markdown files that describe the intent and steps of slash commands defined in `opencode.json`. These files are reference material for humans and agents — the actual commands are registered under `command` in `opencode.json`.

**Scaffold workflow** (`/scaffold`) is the primary user-facing command. It:
1. Asks the user to pick options (IaC → terraform/bicep/both, repo source, DevOps platform, governance tier)
2. Runs `python3 scripts/scaffold.py` via the `scaffold` skill to copy matching templates into a target directory
3. Post-processes placeholders (`{{project_name}}`, `{{azure_location}}`, etc.)
4. Initializes git and creates the initial commit

**Drift workflow** (`/drift`) detects and reconciles infrastructure drift. It:
1. Triggers a dry-run plan against the live Azure subscription.
2. Classifies manual changes (Benign, Operational, Critical).
3. Generates a reconciliation report with `terraform import` or Bicep parameter updates.

## Templates (`templates/`)

- Use `{{mustache}}` or `{{handlebars}}` placeholders for all user-provided values.
- Every template directory must include `.opencode-scaffold.json` with:
  - `placeholders` — list of variables and their prompts/defaults
  - `processor` — the skill or workflow that handles post-copy substitution
  - `depends_on` — optional list of modules to fetch
- A template may reference modules from `modules/` by path; the scaffold workflow resolves and copies them in.

## Modules (`modules/`)

- Each module is self-contained: `main.tf`/`main.bicep`, `variables`, `outputs`, `README.md`, and a `tests/` dir.
- Module path convention: `modules/<framework>/<namespace>-<name>/v<major>/`
- Modules are tested independently with `terraform validate` / `bicep build`.
- Modules must not hardcode Azure subscription/tenant — they accept `subscription_id`, `tenant_id`, `location` as variables.

## Secure Governance & Security Guardrails

All platform development and generated templates must adhere to strict security constraints, which are codified and enforced via the `security-checklist` skill:
- **OIDC/Federated Login Over Client Secrets:** Long-lived secrets must never be used in pipeline configurations. Use OIDC.
- **State Resiliency:** Key Vaults, Storage Accounts, and databases must enable soft-delete and purge protection.
- **Private Connectivity:** Isolate stateful databases and Key Vaults behind Private Endpoints. Configure Network Security Groups with no open management ports (no 22/3389 open to `0.0.0.0/0`).
- **Audit Trails:** Central Log Analytics diagnostic stream must be deployed for all infrastructure components.
- **Strict Environment Isolation:** Dev pipelines must not have access to Prod subscriptions or Prod state files.
- **Strict Error Propagation:** Pipeline scripts must use `set -e` (or equivalent) to ensure failures stop the pipeline.
- **Continuous Validation:** Every commit/PR must run `terraform validate` / `bicep build` and security scanners (Checkov/tfsec).
- **Strict Typing:** Avoid `type = any` in Terraform or loose parameter types in Bicep. Enforce variable validation blocks and decorators.

## Development commands

```bash
# Validate all Terraform modules
for d in modules/terraform/*/; do (cd "$d" && terraform init -backend=false && terraform validate); done

# Validate all Bicep modules
for f in modules/bicep/**/main.bicep; do bicep build "$f" --stdout > /dev/null; done

# Check opencode.json is valid JSON
python3 -m json.tool opencode.json > /dev/null

# Verify all skill references in prompts resolve to existing skill files
python3 scripts/validate-skills.py

# Full team consistency validation (agents, prompts, skills, commands, docs, root/template parity)
python3 scripts/validate-team.py

# Scaffold a new platform-engineering repository
python3 scripts/scaffold.py --help
```

## Adding new content

| What | Where | Also update |
|------|-------|-------------|
| New agent | `.opencode/prompts/<name>.txt` | `opencode.json` → `agent[name]` |
| New skill | `skills/<name>/SKILL.md` | `opencode.json` → `skills[]`, `AGENTS.md` → Named Skills table |
| New command | `workflows/<name>.md` (docs) | `opencode.json` → `command[name]` |
| New template | `templates/<category>/` | `.opencode-scaffold.json` inside template dir |
| New module | `modules/<framework>/<name>/` | — (referenced by templates) |

Every addition must be referenced where it needs to be discovered. Orphan files are deleted.
