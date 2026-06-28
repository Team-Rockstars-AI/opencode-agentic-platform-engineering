# v0.9-prerelease — OpenCode Agentic Platform Engineering

## Summary

This is a **starter prerelease** of the OpenCode Agentic Platform Engineering template repository. It is suitable for public sharing and cooperative development and is designed to scaffold secure, agentically-maintained Azure platform-engineering repos.

> **IMPORTANT:** This prerelease has **NOT yet been validated against a live Azure subscription**. All drift (`/drift`) and compliance (`/compliance`) behaviours are implemented and statically validated using local/mocked artefacts only.

## Key capabilities

- Hardened landing zone modules in **Terraform** and **Bicep**:
  - Network baseline (Hub-Spoke, NAT Gateway, Application Gateway + WAF v2, subnet NSGs, micro-segmentation)
  - Key Vault with private endpoints, soft-delete (90 days), purge protection, RBAC authorization, network ACLs (`deny` by default)
  - OIDC bootstrap for pipelines with **least-privilege custom deployer roles** (no Contributor/Owner, no wildcards)
  - Enterprise private runners with right-sized CPU/memory and KEDA-style scale-to-zero behaviour (conceptually documented)

- Agentic team integrated via **OpenCode**:
  - `orchestrator` — strategic planner, backlog-driven.
  - `builder-infra-tf`, `builder-infra-bicep`, `builder-pipelines` — IaC and pipeline builders.
  - `verifier` — validation and dry-run plans.
  - `security-auditor` — security & compliance scans.
  - `plan-validator` — blast-radius safety gate.
  - `code-reviewer` — WAF review (maintainability, reliability, performance, cost, operations).
  - `explorer` — codebase navigator.
  - `test-writer` — IaC tests.
  - `docs-writer` — READMEs, ADRs, runbooks, journals.

- Slash commands and workflows:
  - `/scaffold` — generate a new platform-engineering repo (Terraform/Bicep, GitHub/Azure DevOps, governance tier) with templates and modules.
  - `/audit` — workspace security and compliance scan using `security-checklist`.
  - `/optimise` — static cost and resource optimisation engine.
  - `/drift` — **new** automated drift detection & reconciliation assistant.
  - `/compliance` — **new** regulatory mapping & compliance readiness reporter.
  - `/select-models` — model optimisation across OpenCode Zen + optional local (Ollama) models.

## Alignment between control repo and templates

- `opencode.json` (root) and `templates/opencode-config/opencode.json` are **fully aligned**:
  - Same agent set, prompts, skills.
  - Same commands, including **`/drift`** and **`/compliance`**.

- Skills have master + template copies:
  - `skills/*/SKILL.md` and `templates/opencode-config/skills/*/SKILL.md` pairs for: `architecture-review`, `audit`, `code-standards`, `commit-format`, `compliance`, `debug`, `doc-standards`, `drift`, `expand`, `git-workflow`, `model-optimiser`, `optimise`, `plan-tracking`, `scaffold`, `security-checklist`, `test-patterns`.

- Prompts are drift- and compliance-aware in both trees:
  - `.opencode/prompts/*.txt` and `templates/opencode-config/prompts/*.txt` aligned for:
    - `verifier`, `plan-validator`, `security-auditor`, `docs-writer`, `code-reviewer`, `orchestrator`, builders.
  - Template prompts include `/drift` JSON artefact emission, reconciliation annotation, security drift classification, and DRIFT_REPORT generation.
  - Template prompts and skills include `/compliance` behaviour for security-auditor, code-reviewer, docs-writer.

- Validation:
  - `scripts/validate-team.py` PASSES: JSON validity, agent↔prompt mapping, skill references, command wiring, root↔template parity.
  - `scripts/validate-skills.py` PASSES: no broken skill references across prompts.

## Documentation for human operators

- Core docs:
  - `README.md` — architecture, security posture, slash commands (including `/drift` and `/compliance`), CI and validation commands.
  - `AGENTS.md` — agent roles, skills, workflows, and orchestration topology.
  - `BUILD_PLAN.md` — backlog and epics (Enabler CI, `/optimise`, `/drift`, `/compliance`).
  - `BUILD_JOURNAL.md` — milestones, changes, friction points, next steps.
  - `DISCOVERIES_LOG.md` — key discoveries and architectural decisions.

- Operator manuals under `docs/`:
  - Provisioning Platform Operator Manual (generator repo).
  - Provisioned Platform Operator Manual (scaffolded repo).
  - Orchestrator Workflow — 9-stage lifecycle and gates.
  - Architecture Blueprint & Network Topology.
  - Regulatory Compliance Mapping Guide.
  - Disaster Recovery & State Reconstruction Runbook.
  - Workload Developer Onboarding Guide.
  - Cost Governance & Sizing Guide.

- Templates for downstream repos:
  - `templates/AGENTS.md` — agent & workflow docs for scaffolded repos.
  - ADRs `0001`–`0006` under `templates/docs/adr/` (including **0006: continuous regulatory compliance mapping**).
  - Report templates under `templates/docs/reports/`:
    - `cost-optimisation-template.md`
    - `drift-reconciliation-template.md`
    - `compliance-readiness-template.md`

## Documentation & memory for agents (agentic continuity)

- Agent configuration:
  - `opencode.json` — agents, skills, commands, endpoints.
  - `templates/opencode-config/opencode.json` — same structure for scaffolded repos.

- Agent memory & governance:
  - `.opencode/memory.md` — model selection, jurisdiction policy, `/select-models` flow.
  - `BUILD_PLAN.md` — authoritative backlog and epic statuses.
  - `BUILD_JOURNAL.md` — historical milestones and rationale.
  - `DISCOVERIES_LOG.md` — operational and architectural insights.

Together, these let a cloned environment be maintained agentically via OpenCode (using `/scaffold`, `/audit`, `/drift`, `/compliance`, `/select-models`) without missing context.

## Validation status (important caveat)

- **Static validation:**
  - `scripts/validate-team.py` and `scripts/validate-skills.py` pass.
  - CI pipelines (`azure-pipelines.yml`, `.github/workflows/ci.yml`, `.github/workflows/security.yml`) run:
    - Python linting and byte-compile.
    - JSON/YAML config validation.
    - Terraform fmt/validate/tflint and Bicep build/lint.
    - Checkov (IaC SAST), gitleaks (secret scan), Bandit (Python SAST).

- **Runtime / cloud validation:**
  - `/drift` and `/compliance` are implemented, wired, and tested ***only*** against local/mocked artefacts.
  - This prerelease has **NOT been validated against a live Azure subscription**:
    - No live `terraform plan` / `terraform apply` against Azure.
    - No live `az deployment ... what-if` or deployments.
  - A TODO remains (tracked in backlog): run `/drift` and `/compliance` against a real subscription, verify DRIFT_REPORT and COMPLIANCE_READINESS_REPORT behaviour, and update documentation accordingly.

## Hosting & CI notes

- **GitHub** is currently the primary public host:**
  - Repository: https://github.com/Team-Rockstars-AI/opencode-agentic-platform-engineering
  - GitHub Actions workflows provide CI and security scanning for collaborators.

- **Azure DevOps (ADO)** remains the intended canonical CI once licensing is available:
  - Root `azure-pipelines.yml` defines authoritative CI (static validation only; no deployments).
  - Future work: wire an ADO pipeline to this repo and enforce branch policies once ADO is fully available.

## Known limitations and future work

- No live Azure validation yet for `/drift` and `/compliance` — this is the main caveat for v0.9-prerelease.
- Test suites for drift/compliance are currently based on small mock artefacts; broader `.tftest.hcl` and harness coverage can be added in later versions.
- ADO pipeline wiring and branch policies are documented but not enforced until licenses are in place.

Despite these limitations, v0.9-prerelease provides a robust, secure, and well-documented starting point for cooperative development, and for scaffolding new agentically-maintained platform-engineering repos.
