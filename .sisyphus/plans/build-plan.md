# Session Continuity Tracker & Build Plan

This file serves as the strict source of truth for session continuity and remaining platform engineering milestones.

---

## 📊 Current Status

| Epic | Feature | Status | Completed Date | Commits |
|---|---|---|---|---|
| **Epic 1** | `/optimise` — Static Cost & Resource Optimization Engine | ✅ **COMPLETED** | 2026-06-15 | `e82c815`, `4207b70` |
| **Epic 2** | `/drift` — Automated Drift Detection & Reconciliation Assistant | ⏳ **PENDING** | — | — |
| **Epic 3** | `/compliance` — Regulatory Mapping & Audit Readiness Reporter | ⏳ **PENDING** | — | — |

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

## 🔄 Epic 2: `/drift` — Automated Drift Detection & Reconciliation Assistant (Next Up)

### 1. Objectives
Enable the operator to run `/drift` to execute a dry-run plan against their live Azure subscription, parse the output to identify manual changes ("clickops"), and generate the exact IaC code or import commands needed to reconcile the drift.

### 2. Step-by-Step Implementation Plan
1.  **`@explorer` (Discovery):**
    *   Analyze how the `@verifier` currently runs `terraform plan` and `bicep what-if`.
    *   Review the `plan-tracking` skill to understand how plan outputs are parsed.
2.  **`@builder-infra-tf` & `@builder-infra-bicep` (Implementation):**
    *   Create the master skill file: `skills/drift/SKILL.md`.
    *   Create the template skill file: `templates/opencode-config/skills/drift/SKILL.md`.
    *   Define parsing rules for `terraform show -json` and `az deployment sub what-if` outputs to isolate drifted properties.
3.  **`@builder-pipelines` (Workflow Integration):**
    *   Add the `/drift` command and workflow definition to `opencode.json` and `templates/opencode-config/opencode.json`.
    *   Configure the workflow to orchestrate `@verifier` (to run the plan), `@plan-validator` (to parse drift), and `@docs-writer` (to write the report).
4.  **`@verifier` (Validation):**
    *   Verify JSON syntax of `opencode.json`.
    *   Run `python3 scripts/validate-skills.py` to validate the new `drift` skill reference.
5.  **`@plan-validator` (Safety Gate):**
    *   Define strict rules in the `drift` skill to ensure that reconciliation plans *never* accidentally destroy stateful resources (e.g., if a database was manually modified, the reconciliation must modify the IaC, not recreate the database).
6.  **`@security-auditor` (Security Gate):**
    *   Ensure that the drift detection process flags manual changes that degrade security (e.g., if someone manually opened port 3389 on an NSG, flag this as a **CRITICAL** security drift).
7.  **`@test-writer` (Testing):**
    *   Write a mock plan JSON containing a drifted property (e.g., an updated tag) and verify that the `@plan-validator` correctly parses and reports it.
8.  **`@docs-writer` (Documentation):**
    *   Create a markdown template for the report: `templates/docs/reports/drift-reconciliation-template.md`.
    *   Update `AGENTS.md` and `templates/AGENTS.md` to document the new `/drift` command and skill.

### 3. Acceptance Criteria
*   Running `/drift` triggers a dry-run plan against Azure.
*   Generates a structured `DRIFT_REPORT.md` detailing:
    *   **Drifted Resources:** List of resources with differences between live state and IaC.
    *   **Risk Assessment:** Flags if drift introduced security vulnerabilities (e.g., public IPs, open ports).
    *   **Reconciliation Path:** Provides the exact `terraform import` commands or Bicep parameter updates to sync the state.

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
