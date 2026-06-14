# Build Journal

## Milestone: Formalised Reusable Skills Framework

**Date:** 2026-06-14

### Summary

This milestone formalised the concept of **Skills** as first-class, version-controlled, reusable procedures within the platform engineering repository. Previously, agent instructions scattered workflow rules across prompt files. Now, critical operational procedures are extracted into dedicated skill definitions that agents load on demand.

### Changes Made

1. **Created `skills/security-checklist/SKILL.md`** (and template equivalent):
   - A structured security review checklist with PASS/FAIL/NA criteria
   - Five categories: HARD BLOCKS (knock-out criteria), Authentication, Authorisation, Input Validation, Error Handling
   - Standardised finding report format with severity ratings (CRITICAL/HIGH/MEDIUM/LOW)
   - Designed to be loaded by `@security-auditor` and the `audit` skill

2. **Created `skills/git-workflow/SKILL.md`** (and template equivalent):
   - Branch naming convention: `feature/<epic-or-feature-id>-<description>`
   - Pre-commit hygiene: formatter/linter, precision staging (`git add -p`)
   - Commit blacklist: secrets, local configs, debug artifacts, commented-out code
   - Handoff summary format for `@test-writer` handover

3. **Updated `skills/audit/SKILL.md`** (and template equivalent):
   - Added explicit reference to load `security-checklist` during analysis
   - Aligned finding report output with the format defined in `security-checklist`

4. **Updated builder prompts** (`.opencode/prompts/builder-infra-tf.txt`, `builder-infra-bicep.txt`, `builder-pipelines.txt`):
   - Added instruction to load `git-workflow` before staging or preparing handoff
   - Removed inline workflow rules in favour of skill delegation

5. **Updated `security-auditor.txt` prompt**:
   - Added instruction to load `security-checklist` before auditing
   - Aligned finding severity and format requirements with the skill

6. **Updated `AGENTS.md`** (root and template):
   - Added "Named Skills in Use" table in root `AGENTS.md`
   - Added "Reusable Skills" section in `templates/AGENTS.md`

### Friction Points

- **Skill vs. prompt boundary:** Some builder prompts still retain inline security rules (e.g., soft-delete enforcement, private connectivity). These overlap with the `security-checklist` skill. Future iterations should deduplicate: keep implementation mandates in prompts, move **verification** mandates to the skill.
- **Template drift:** The template versions of prompts (`templates/opencode-config/prompts/`) and the master versions (`.opencode/prompts/`) are structurally different. The builders are more detailed in the master; pipelines are more detailed in the template. This asymmetry was accepted for now but should be reconciled in a follow-up.

### Next Steps

- Reconcile `.opencode/prompts/` and `templates/opencode-config/prompts/` to reduce drift
- Extract `code-standards` and `commit-format` into proper skills (they are currently referenced by name but do not exist as standalone files)
- Add automated validation to ensure every skill referenced in prompts actually exists in `skills/`

---

## Milestone: Complete Reusable Skills Framework & Prompt Reconciliation

**Date:** 2026-06-14

### Summary

This milestone completed the reusable skills framework by authoring the six remaining skills that were previously referenced by name but did not exist as standalone files. It also reconciled structural drift between the master prompts (`.opencode/prompts/`) and the template prompts (`templates/opencode-config/prompts/`), and added automated validation to catch broken skill references.

### Changes Made

1. **Created `skills/code-standards/SKILL.md`** (and template equivalent):
   - Codifies CAF naming conventions (prefixes for all Azure resource types)
   - Mandatory tagging rules (Environment, Project, ManagedBy, GovernanceTier, CostCenter, Owner)
   - Azure Well-Architected Framework alignment across all five pillars (Security, Reliability, Cost Optimization, Operational Excellence, Performance Efficiency)
   - IaC best practices for both Terraform (version pinning, strict typing, validation blocks) and Bicep (target scope, decorators, nested modules)

2. **Created `skills/commit-format/SKILL.md`** (and template equivalent):
   - Conventional Commits specification with type, scope, and description rules
   - Nine commit types defined (feat, fix, docs, style, refactor, perf, test, ci, chore)
   - Optional body and footer guidelines including BREAKING CHANGE notation
   - Imperative present tense enforcement and punctuation rules

3. **Created `skills/architecture-review/SKILL.md`** (and template equivalent):
   - Subscription topology and environment isolation standards (separate subs for Dev/Test/Prod)
   - Network isolation review criteria (Private Endpoints, NSG rules, micro-segmentation)
   - Central state access reviews (secure backend, state locking)
   - IAM review criteria (least privilege, managed identities, OIDC federation)

4. **Created `skills/plan-tracking/SKILL.md`** (and template equivalent):
   - Dry-run execution plan generation and JSON conversion guidance
   - Resource action tracking taxonomy (create/update/delete/replace with colour coding)
   - Milestone status and session state maintenance procedures

5. **Created `skills/doc-standards/SKILL.md`** (and template equivalent):
   - Module README documentation requirements (inputs/outputs tables, resources, providers)
   - Architecture Decision Record (ADR) format and location standards
   - Runbook and onboarding guide writing guidelines

6. **Created `skills/test-patterns/SKILL.md`** (and template equivalent):
   - Terraform 1.6+ testing framework guidance (`.tftest.hcl` unit and integration tests)
   - Bicep validation testing guidelines (build, lint, what-if)
   - Example assertion blocks for Key Vault security compliance testing

7. **Created `scripts/validate-skills.py`** (and template equivalent):
   - Scans all prompt files (`.opencode/prompts/` and `templates/opencode-config/prompts/`) for skill references
   - Matches patterns like `load the \`name\` skill`, `load the 'name' skill`, etc.
   - Verifies each referenced skill has a corresponding `skills/<name>/SKILL.md` file
   - Exits with error code 1 if any broken references are found
   - Intended for CI/CD pipeline gating

8. **Reconciled `.opencode/prompts/` with `templates/opencode-config/prompts/`:**
   - Aligned builder prompts so both master and template versions reference the same skills
   - Ensured `code-standards`, `commit-format`, `architecture-review`, `plan-tracking`, `doc-standards`, and `test-patterns` are loaded by the appropriate agents
   - Removed inline workflow rules in favour of skill delegation throughout

9. **Updated `AGENTS.md`** (root and template):
   - Expanded "Named Skills in Use" table from 6 to 12 skills, alphabetically sorted
   - Added `scripts/validate-skills.py` to development commands section

### Friction Points

- **Template drift resolution was manual:** The reconciliation of prompt files required careful line-by-line comparison of `.opencode/prompts/*.txt` with `templates/opencode-config/prompts/*.txt`. While the skill references are now aligned, there are still minor phrasing differences in some prompts that could be homogenised in a future pass.
- **Skill granularity trade-off:** Some skills (e.g., `code-standards` at 91 lines, `commit-format` at 92 lines) are quite dense. There is a risk that builders will skip loading a skill if its output is perceived as too verbose. Future iterations could split `code-standards` into separate WAF, naming, and tagging skills.
- **Test-patterns skill depends on Terraform 1.6+:** Teams still on older Terraform versions cannot use the `.tftest.hcl` patterns described in the skill. A compatibility note has been added to the skill's trigger description.

### Next Steps

- Implement CI/CD integration of `validate-skills.py` as a pre-merge gate
- Consider splitting `code-standards` into granular sub-skills (WAF, CAF naming, tagging)
- Evaluate whether `test-patterns` should include Pester/PSScriptAnalyzer guidance for Bicep module testing
