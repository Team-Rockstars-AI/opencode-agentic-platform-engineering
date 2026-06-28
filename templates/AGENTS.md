# Azure Platform & Workload Operations — Agent Instructions

## Purpose

This repository manages the deployment, security compliance, and automated operation of the organization's Azure Landing Zone infrastructure and application workloads.

Development and deployments in this repository are managed collaboratively by an OpenCode multi-agent automation team. All changes must be planned, compiled, audited, and safety-checked prior to deployment.

## Repository Structure

Based on your scaffolding selection, this repository contains:
- **`terraform/`**: Standard parameterized modules and deployment environments.
- **`bicep/`**: Subscription/Resource Group-scoped templates and parameter maps.
- **`.github/` or `pipelines/`**: Secure, OIDC-federated automated workflows.
- **`.opencode/`**: The local multi-agent configuration, specialized subagent prompts, and custom validation rules.

## Mandatory Workflow

Every non-trivial infrastructure, pipeline, or architecture change MUST follow this lifecycle in order. Steps 4–7 cannot be skipped for any infra or pipeline change:

| Stage | Agent | Output |
|-------|-------|--------|
| 1. research | `explorer` | `## Research summary` |
| 2. plan | `orchestrator` | `## Milestone plan` |
| 3. build | `builder-infra-tf` / `builder-infra-bicep` / `builder-pipelines` | `## Build summary` |
| 4. verify | `verifier` | `Verification: PASSED\|FAILED` |
| 5. review | `code-reviewer` | `Quality gate: PASSED\|FAILED` |
| 6. security | `security-auditor` | `Security gate: PASSED\|FAILED` |
| 7. safety | `plan-validator` | `Plan safety gate: PASSED\|FAILED` |
| 8. test | `test-writer` | `## Test summary` |
| 9. docs | `docs-writer` | `## Documentation summary` |

## Multi-Agent Operations Topology

### Strategic Planning
*   **`orchestrator`**: The entry point for all operations. Decouples requirements, reviews the backlog (`BUILD_PLAN.md`), schedules rollout phases, and delegates to specialized builders. Never implements code directly.

### Specialized Implementation Builders
*   **`builder-infra-tf`**: Authors secure, parameterized, modular Terraform. Enforces diagnostic streams, soft delete, and asserts unit tests via `.tftest.hcl`.
*   **`builder-infra-bicep`**: Authors multi-scope Bicep templates with diagnostic and governance integrations.
*   **`builder-pipelines`**: Designs automated workflows with zero long-lived credentials, strictly enforcing passwordless OIDC authentication.

### Read-Only Discovery
*   **`explorer`**: Fast codebase navigator for tracing modules, resource references, and folder structures. No file modifications.

### Continuous Verification Gates (Read-Only)
*   **`verifier`**: Compiles modified code (`terraform validate` / `bicep build`), runs linters, and outputs dry-run logs.
*   **`code-reviewer`**: Reviews for all five WAF pillars — maintainability/correctness, reliability/availability, performance efficiency, cost optimization, and operational excellence. No file modifications.
*   **`security-auditor`**: Scans configuration files for compliance deviations, exposed parameters, or overly broad permissions. No file modifications.
*   **`plan-validator`**: **BLAST RADIUS SAFETY GATE.** Parses dry-run logs. Immediately blocks any deployment if databases, networking hubs, or vaults are scheduled for deletion or recreation. No file modifications.

### Post-Gate Agents
*   **`test-writer`**: Writes sprint-appropriate infrastructure unit and validation tests.
*   **`docs-writer`**: Updates module READMEs, ADRs, runbooks, BUILD_JOURNAL.md, and DISCOVERIES_LOG.md.

## WAF Ownership

| WAF Pillar | Owner |
|------------|-------|
| Security & Compliance | `security-auditor` |
| Reliability / Availability | `code-reviewer` |
| Cost Optimization | `code-reviewer` (via `optimise` skill) |
| Operational Excellence | `orchestrator` + `docs-writer` |
| Performance Efficiency | `code-reviewer` |

## Secure Governance & Security Guardrails

All infrastructure and application workloads must adhere to the following secure baseline standards, which are codified and enforced via the `security-checklist` skill:
- **Federated Login (OIDC)**: No long-lived client secrets. All pipelines must authenticate using Azure Federated Credentials.
- **State Resiliency**: Storage accounts, databases, and Key Vaults must enable soft-delete and purge protection.
- **Network Isolation**: Restrict stateful resources behind Private Endpoints and Network Security Groups with no open management ports (no 22/3389 open to `0.0.0.0/0`).
- **Diagnostic Logging**: Route all active diagnostic streams to the central Log Analytics Workspace.
- **Strict Environment Isolation**: Dev pipelines must not have access to Prod subscriptions or Prod state files.
- **Strict Error Propagation**: Pipeline scripts must use `set -e` (or equivalent) to ensure failures stop the pipeline.
- **Continuous Validation**: Every commit/PR must run `terraform validate` / `bicep build` and security scanners (Checkov/tfsec).
- **Strict Typing**: Avoid `type = any` in Terraform or loose parameter types in Bicep. Enforce variable validation blocks and decorators.

## Reusable Skills (`.opencode/skills/`)

Your workspace includes a set of reusable **Skills** — codified procedures that agents invoke via the `skill` tool. Skills standardise common operations across the codebase:

| Skill | Consumed By | Purpose |
|-------|-------------|---------|
| **`architecture-review`** | `@code-reviewer`, `@orchestrator` | Architectural change review covering subscription topology, network isolation, central state access, and IAM least-privilege standards. |
| **`audit`** | `/audit` command | Workspace compliance scan — codebase secrets check, NSG/public-endpoint audit, Private Endpoint verification. Loads `security-checklist` for structured reporting. |
| **`code-standards`** | `@code-reviewer`, `@builder-infra-tf`, `@builder-infra-bicep` | CAF naming conventions, Azure Well-Architected Framework alignment, tagging standards, and IaC best practices for Terraform and Bicep. |
| **`commit-format`** | `@builder-infra-tf`, `@builder-infra-bicep`, `@builder-pipelines` | Conventional Commits specification enforcing structured commit types, scopes, and description format for automated changelog generation. |
| **`debug`** | `/debug` command | Compilation error tracing and resolution. |
| **`doc-standards`** | `@docs-writer` | Documentation standards for module READMEs, ADR format, runbooks, and onboarding guides. |
| **`drift`** | `/drift` command | Detect, classify, and reconcile infrastructure drift against the desired IaC state. |
| **`expand`** | `/expand` command | Guided rollout of new IaC resource modules under governance guardrails. |
| **`git-workflow`** | `@builder-infra-tf`, `@builder-infra-bicep`, `@builder-pipelines` | Branch naming, pre-commit hygiene (formatter, precision staging), commit blacklist (no secrets, debug artifacts, commented-out code), and standardised handoff summary for `@test-writer`. |
| **`model-optimiser`** | `/select-models` command | Discovers the live OpenCode ZEN catalog + installed Ollama models and reasons over each agent's prompt and skills to select the optimal available model per agent (jurisdiction, cost/quality focus, local hardware). |
| **`optimise`** | `/optimise` command, `@code-reviewer` | Static cost and resource optimization review checklist and finding report format. |
| **`plan-tracking`** | `@plan-validator`, `@docs-writer` | Execution plan JSON conversion, resource action tracking, milestone status updates, and session state maintenance. |
| **`security-checklist`** | `@security-auditor`, `audit` skill | Structured PASS/FAIL/NA review checklist covering OIDC, network isolation, soft-delete, least-privilege IAM, diagnostic logging, and strict typing. Produces findings with severity ratings and remediation blocks. |
| **`test-patterns`** | `@test-writer`, `@builder-infra-tf` | Unit and validation test guidelines for Terraform (.tftest.hcl) and Bicep modules, including plan assertions and what-if validation patterns. |

## Developer Commands & Slash Actions

*   **`/audit`**: Scans your entire workspace for credentials leaks, compliance defects, and network isolation failures. Outputs a comprehensive compliance report.
*   **`/debug`**: Directs the verifier and builder agents to inspect failing pipeline logs, trace resource syntax issues, and propose/implement fixes.
*   **`/drift`**: Executes a dry-run plan against the live Azure subscription to identify, classify, and reconcile manual "clickops" changes. Outputs a reconciliation report with remediation guidance.
*   **`/expand`**: Initiates a guided rollout to deploy new resource components under strict organization governance.
*   **`/optimise`**: Scans your entire workspace for cost leaks, oversized SKUs, and resource sizing inefficiencies. Outputs a comprehensive cost optimization report.
*   **`/select-models`**: Fetches a fresh OpenCode ZEN model list and your installed Ollama models, then assigns the optimal available model per agent (jurisdiction, cost/quality focus, local hardware).

## Adding New Content

| What | Where | Also update |
|------|-------|-------------|
| New agent | `.opencode/prompts/<name>.txt` | `opencode.json` → `agent[name]`, `AGENTS.md` |
| New skill | `.opencode/skills/<name>/SKILL.md` | `opencode.json` → `skills.paths`, `AGENTS.md` skills table |
| New command | `opencode.json` → `command[name]` | `AGENTS.md` commands section |
| New module | `terraform/<name>/` or `bicep/<name>/` | — (referenced by pipelines) |

```bash
# Validate Terraform structures
cd terraform && terraform init -backend=false && terraform validate

# Compile and validate Bicep configurations
bicep build main.bicep --stdout > /dev/null

# Verify all skill references resolve
python3 scripts/validate-skills.py

# Run full team validation (agents, prompts, skills, commands)
python3 scripts/validate-team.py
```
