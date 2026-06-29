# Build Plan & Backlog

This file is the **strict source of truth** for session continuity and the remaining
platform-engineering milestones. The orchestrator reads it at the start of every session to
decide what to do next, and the `plan-tracking` skill keeps its milestone statuses current.
Completed milestones are archived in [`BUILD_JOURNAL.md`](BUILD_JOURNAL.md).

---

## 📊 Current Status

| Epic / Enabler | Feature | Status | Completed Date | Commits |
|---|---|---|---|---|
| **Enabler** | Azure DevOps canonical CI (`azure-pipelines.yml`) | ✅ **COMPLETED (CODE)** | 2026-06-18 | `c7d0bd2` |
| **Epic 1** | `/optimise` — Static Cost & Resource Optimization Engine | ✅ **COMPLETED** | 2026-06-15 | `e82c815`, `4207b70` |
| **Epic 2** | `/drift` — Automated Drift Detection & Reconciliation Assistant | ✅ **COMPLETED (CODE)** | 2026-06-28 | `f7a2b1c` |
| **Epic 3** | `/compliance` — Regulatory Mapping & Audit Readiness Reporter | ✅ **COMPLETED** | 2026-06-28 | `d3a4b5c` |

> **Note:** The ADO CI enabler and Epic 2 `/drift` are "code complete" but have outstanding **manual operational steps** or **live validation** (see below) before they are fully enforced or verified against live Azure subscriptions.

---

## 🔧 Enabler: Azure DevOps Canonical CI (`azure-pipelines.yml`)

This enabler underpins Epics 2 and 3 by ensuring static validation runs in the canonical Azure DevOps environment.

### Remaining manual steps (to be done in Azure DevOps / Git tooling)

1. **Wire up the ADO pipeline**
   - [ ] In Azure DevOps, create a new pipeline for this repo using the existing `azure-pipelines.yml` at the root of the `main` branch.
   - [ ] Verify a successful run on `main` (all DevSecOps and Validate stage jobs succeed).
   - [ ] Optionally configure branch policies so that this pipeline must succeed for PRs into `main`.

2. **GitHub mirror management**
   - [ ] When ready to open-source, push the current `main` branch from the ADO-canonical repo to the GitHub mirror remote.
   - [ ] Confirm that `.github/workflows/ci.yml` and `.github/workflows/security.yml` run successfully on the mirror.
   - [ ] Document the mirror remote name and update cadence in internal runbooks if needed.

3. **Template pipeline alignment (backlog item)**
   - [ ] Review `templates/github/workflows/deploy.yml` and `templates/azure-devops/pipelines/azure-pipelines.yml` for parity with the root CI expectations (validate-skills, validate-team, Checkov, gitleaks, Bandit).
   - [ ] Decide on any minimal adjustments needed so scaffolded repos inherit the same baseline checks.
   - [ ] Update documentation in `templates/AGENTS.md` to clearly describe how template pipelines differ from the control repo CI.

---

## 📦 Epic 1: `/optimise` (Completed)
- **Deliverables:**
  - `skills/optimise/SKILL.md` (Master skill with 8 cost-optimization rules and security guardrails)
  - `templates/opencode-config/skills/optimise/SKILL.md` (Template skill)
  - Parameterized `modules/terraform/azure-private-runner/v1/variables.tf` and `main.tf` with `runner_cpu` and `runner_memory`
  - Parameterized `templates/terraform/variables.tf` and `templates/terraform/main.tf`
  - Added `optimise` command to `opencode.json` and `templates/opencode-config/opencode.json`
  - Created `templates/docs/reports/cost-optimisation-template.md`
  - Updated `AGENTS.md` and `templates/AGENTS.md`
  - Updated `BUILD_JOURNAL.md`

---

## 🔄 Epic 2: `/drift` — Automated Drift Detection & Reconciliation Assistant (Completed)

### 1. Objectives
Enable the operator to run `/drift` to execute a dry-run plan against their live Azure subscription, parse the output to identify manual changes ("clickops"), and generate the exact IaC code or import commands needed to reconcile the drift.

### 2. Implementation Summary
- **Deliverables:**
  - `skills/drift/SKILL.md` (Master skill for drift detection and reconciliation)
  - `templates/opencode-config/skills/drift/SKILL.md` (Template skill)
  - Added `drift` command to `opencode.json` and `templates/opencode-config/opencode.json`
  - Created `templates/docs/reports/drift-reconciliation-template.md`
  - Updated `AGENTS.md` and `templates/AGENTS.md`
  - Updated `BUILD_JOURNAL.md`
  - Static validation and mock tests implemented.

### 3. Outstanding Validation
- [ ] **Live Azure Subscription Validation:** The `/drift` workflow has been implemented and statically validated with mock plan JSONs. However, it has **not yet been tested against a live Azure subscription**. This requires a connected environment with active drift to verify the end-to-end reconciliation guidance.

---

## 🛡️ Epic 3: `/compliance` — Regulatory Mapping & Audit Readiness Reporter

### 1. Objectives
Enable the operator to run `/compliance` to scan their IaC, pipelines, and drift reports, mapping their technical configurations directly to regulatory controls (DORA, BIO, GDPR) to generate an auditor-ready compliance report.

### 2. Step-by-Step Implementation Plan
1.  **`@explorer` (Discovery):**
    *   Review `skills/security-checklist/SKILL.md` to see the existing security checks.
    *   Research the specific mapping of Azure controls to **DORA** (Digital Operational Resilience Act) and Dutch **BIO** (Baseline Informatiebeveiliging Overheid).
2.  **`@builder-infra-tf` & `@builder-infra-bicep` (Implementation):**
    *   Create the master skill file: `skills/compliance/SKILL.md`.
    *   Create the template skill file: `templates/opencode-config/skills/compliance/SKILL.md`.
    *   Codify the **Regulatory Mapping Matrix** (e.g., mapping Key Vault Soft-Delete to DORA Article 12, mapping NSG micro-segmentation to BIO Control 12.4).
3.  **`@builder-pipelines` (Workflow Integration):**
    *   Add the `/compliance` command and workflow definition to `opencode.json` and `templates/opencode-config/opencode.json`.
    *   Configure the workflow to orchestrate `@security-auditor` (to run the checklist), `@code-reviewer` (to check tagging/naming), and `@docs-writer` (to compile the regulatory report).
4.  **`@verifier` (Validation):**
    *   Verify JSON syntax of `opencode.json`.
    *   Run `python3 scripts/validate-skills.py` to validate the new `compliance` skill reference.
5.  **`@security-auditor` (Compliance Gate):**
    *   Review the mapping matrix to ensure absolute accuracy against official DORA and BIO baselines.
6.  **`@test-writer` (Testing):**
    *   Verify that running `/compliance` on a compliant workspace produces a 100% PASS matrix, and running it on a workspace with public Key Vault access produces a targeted FAIL mapping to DORA Article 12.
7.  **`@docs-writer` (Documentation):**
    *   Create a markdown template for the report: `templates/docs/reports/compliance-readiness-template.md`.
    *   Create a new ADR: `templates/docs/adr/0006-continuous-regulatory-compliance-mapping.md` to document the decision to map IaC directly to DORA/BIO.
    *   Update `AGENTS.md` and `templates/AGENTS.md` to document the new `/compliance` command and skill.

### 3. Acceptance Criteria
*   Running `/compliance` scans the workspace and maps findings to DORA, BIO, and GDPR.
*   Generates a structured `COMPLIANCE_READINESS_REPORT.md` detailing:
    *   **Executive Summary:** Overall compliance percentage.
    *   **Regulatory Control Matrix:** A table mapping Azure resources ➔ Technical Controls ➔ Regulatory Articles (e.g., `kv-vault` ➔ Purge Protection ➔ DORA Art. 12).
    *   **Non-Compliance Findings:** List of failed controls with severity and remediation steps.

---

## 🎛️ Epic 4: Agent Team Packs & Model Profiles

### 1. Objectives
Introduce curated, versioned “team packs” that bundle agents, models, prompts, skills, and policies into sharable, validated configurations. This reduces the combinatorial complexity of per-agent model selection and provides a safer, more predictable upgrade path for platform teams.

### 2. Step-by-Step Implementation Plan
1.  **Milestone 4.1: Pack concept, manifest schema, and lifecycle (design only).**
    *   Objective: Define the `pack.yaml` schema and the lifecycle of a pack (discovery, application, validation).
2.  **Milestone 4.2: Core pack manifest files and pack list/apply commands integrated with `select-models`.**
    *   Objective: Implement the CLI logic to list available packs and apply a pack's model/agent configuration to `opencode.json`.
3.  **Milestone 4.3: Pack creation/validation and PR-sharing workflow.**
    *   Objective: Enable engineers to export their current working configuration as a new pack and validate it against the live model catalog.
4.  **Milestone 4.4 (optional): CI integration and governance for packs.**
    *   Objective: Automate pack validation in the CI pipeline to ensure packs remain compatible with the evolving model catalog.
