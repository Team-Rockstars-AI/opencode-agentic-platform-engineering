# Orchestrator Workflow

The orchestrator is the strategic lead and sole entry point for every non-trivial session. It never writes infrastructure or pipeline code directly — it plans, delegates, gates, and closes.

## Session startup

At the start of every session the orchestrator:

1. Reads `AGENTS.md`, `BUILD_JOURNAL.md`, and `BUILD_PLAN.md` to orient itself
2. Uses `BUILD_PLAN.md` as the strict source of truth for what to work on next
3. Loads the `plan-tracking` skill before the first milestone begins
4. Outputs a `## Milestone plan` block (see [Output contract](#output-contract))

## Mandatory lifecycle

Every non-trivial infrastructure, pipeline, or architecture change must follow this nine-stage sequence in order. **Stages 4–7 cannot be skipped** for any infra or pipeline change.

```
research → plan → build → verify → review → security → safety → test → docs
```

| # | Stage | Agent | Required output |
|---|-------|-------|----------------|
| 1 | **research** | `@explorer` | `## Research summary` |
| 2 | **plan** | `@orchestrator` | `## Milestone plan` |
| 3 | **build** | `@builder-infra-tf` / `@builder-infra-bicep` / `@builder-pipelines` | `## Build summary` |
| 4 | **verify** | `@verifier` | `Verification: PASSED\|FAILED` |
| 5 | **review** | `@code-reviewer` | `Quality gate: PASSED\|FAILED` |
| 6 | **security** | `@security-auditor` | `Security gate: PASSED\|FAILED` |
| 7 | **safety** | `@plan-validator` | `Plan safety gate: PASSED\|FAILED` |
| 8 | **test** | `@test-writer` | `## Test summary` |
| 9 | **docs** | `@docs-writer` | `## Documentation summary` |

A failed gate at any of stages 4–7 halts the milestone. The orchestrator reports the failure and the smallest viable next step to the user before taking any further action.

## Output contract

At the start of every non-trivial milestone the orchestrator outputs:

```
## Milestone plan
- Epic: <epic name from BUILD_PLAN.md>
- Scope: <what is in and out>
- Stages: research → plan → build → verify → review → security → safety → test → docs
- Agents: <which agents are needed>
- Gates: Verification: PASSED, Quality gate: PASSED, Security gate: PASSED, Plan safety gate: PASSED required before test/docs
```

## Agent roles

### Planning
- **`orchestrator`** — decomposes backlog epics into milestone-sized slices, delegates to builders, enforces gates, tracks status

### Discovery
- **`explorer`** — read-only codebase navigator; gathers only the context needed to unblock the current milestone

### Implementation builders
- **`builder-infra-tf`** — Azure Terraform IaC modules and configurations
- **`builder-infra-bicep`** — Azure Bicep templates and parameter files
- **`builder-pipelines`** — GitHub Actions and Azure DevOps CI/CD pipelines

### Verification gates (read-only, stages 4–7)
- **`verifier`** — `terraform validate` / `bicep build` / `tflint` and dry-run plan generation
- **`code-reviewer`** — quality review across all five WAF pillars (see [WAF ownership](#waf-ownership))
- **`security-auditor`** — compliance and security gate (OIDC, network isolation, IAM, encryption)
- **`plan-validator`** — blast-radius safety gate; blocks any plan that destroys or recreates stateful resources

### Post-gate agents
- **`test-writer`** — writes `.tftest.hcl` or `tests/main.test.bicep` tests after all gates pass
- **`docs-writer`** — updates READMEs, ADRs, runbooks, `BUILD_JOURNAL.md`, and `DISCOVERIES_LOG.md`

## WAF ownership

The orchestrator explicitly assigns each Azure Well-Architected Framework pillar to an owning agent:

| WAF pillar | Owner | How |
|------------|-------|-----|
| Security & Compliance | `@security-auditor` | Stage 6 gate; `security-checklist` skill |
| Reliability / Availability | `@code-reviewer` | Stage 5 gate; checks soft-delete, availability zones, retry policies |
| Cost Optimization | `@code-reviewer` | Stage 5 gate; uses `optimise` skill for SKU and sizing review |
| Operational Excellence | `@orchestrator` + `@docs-writer` | Milestone planning; stage 9 documentation |
| Performance Efficiency | `@code-reviewer` | Stage 5 gate; checks SKU sizing, autoscale configuration |

## Delegation rules

When delegating a build task, the orchestrator:

1. References the relevant Epic from `BUILD_PLAN.md` in the delegation message
2. Instructs the builder to read that Epic's implementation plan and acceptance criteria before implementing
3. Specifies which builder to use based on the IaC framework (Terraform vs Bicep) and task type (infra vs pipelines)

The orchestrator uses `@explorer` only to gather context needed for the current milestone — not for speculative discovery.

## Gate escalation

If a gate fails (stages 4–7), the orchestrator:

- Does **not** proceed to the next stage
- Reports the failure clearly, naming the blocking agent and the specific findings
- Proposes the smallest viable remediation step to the user
- Waits for user direction before re-running the gate

## Session closure

A session is not complete until:

1. All four gates have returned `PASSED` for the milestone
2. `@test-writer` has delivered a `## Test summary`
3. `@docs-writer` has updated `README.md`, `docs/` deliverables, `DISCOVERIES_LOG.md`, and `BUILD_JOURNAL.md`
4. A builder agent has staged and committed all changes using the `git-workflow` and `commit-format` skills
5. The commit is confirmed as successful

## Descoping (schedule protection)

When time or token budget is constrained, the orchestrator cuts in this priority order — never cutting core infrastructure:

1. Non-critical resource tags
2. Automated secret rotation schedules
3. Deep compliance dashboards
4. Broad test coverage (keep smoke-level)
5. Remote OIDC (keep local state working)

Core network topology, IAM structures, and Key Vault configuration are never descoped.

## Slash commands

These commands route through the orchestrator by default:

| Command | Purpose |
|---------|---------|
| `/scaffold` | Bootstrap a new platform-engineering repository from templates |
| `/expand` | Onboard a new workload or expand landing zone infrastructure |
| `/optimise` | Scan the workspace for cost and resource sizing inefficiencies |
| `/select-models` | Discover live model catalog and assign optimal models per agent |

The `/audit` command routes directly to `@security-auditor` and the `/debug` command routes directly to `@verifier`, as both are narrow read-only operations that do not require orchestrated build/review cycles.

## Platform repo vs provisioned repo

The same orchestrator workflow runs in two distinct contexts. Understanding which context you are in determines what the team is for.

### Platform repo (this repository)

Purpose: build and maintain the scaffolding system itself — the templates, skills, prompts, modules, and tooling that other teams consume.

- The `/scaffold` command is available here. Running it generates a new provisioned repo.
- Skills live at `skills/` in the repo root.
- The session instruction set includes `.opencode/memory.md` for cross-session continuity.
- The orchestrator's `BUILD_PLAN.md` describes platform-level epics (new modules, new IaC patterns, tooling improvements).

### Provisioned repo (generated by `/scaffold`)

Purpose: operate a specific Azure Landing Zone — build, deploy, secure, and maintain the infrastructure and pipelines for one or more workloads.

- The `/scaffold` command is **not available**. A provisioned repo does not generate further repos.
- Skills live at `.opencode/skills/` (co-located with prompts under `.opencode/`).
- There is no session memory file by default; operators may add one.
- The orchestrator's `BUILD_PLAN.md` describes workload-level epics (landing zone modules, subscription vending, OIDC bootstrap, workload onboarding).

### What is identical in both contexts

Everything else — the 9-stage lifecycle, all 11 agents, all prompts, all gates, and all commands except `/scaffold` — is identical. An operator working in a provisioned repo has the same governance workflow and the same agent team as the platform engineers who maintain the tooling. The difference is purpose and scope, not capability.

| | Platform repo | Provisioned repo |
|---|---|---|
| Purpose | Build the scaffolding system | Operate a specific Azure Landing Zone |
| `/scaffold` command | ✅ | ❌ |
| Skills location | `skills/` | `.opencode/skills/` |
| Session memory | `.opencode/memory.md` included | Not included by default |
| `BUILD_PLAN.md` content | Platform epics | Workload epics |
| All other commands & agents | ✅ identical | ✅ identical |

## Related documents

- [`AGENTS.md`](../AGENTS.md) — canonical agent reference
- [`skills/plan-tracking/SKILL.md`](../skills/plan-tracking/SKILL.md) — milestone tracking procedure
- [`skills/architecture-review/SKILL.md`](../skills/architecture-review/SKILL.md) — architecture review standards
- [`workflows/scaffold.md`](../workflows/scaffold.md) — scaffold command workflow detail
- [`BUILD_PLAN.md`](../BUILD_PLAN.md) — active backlog and epics
