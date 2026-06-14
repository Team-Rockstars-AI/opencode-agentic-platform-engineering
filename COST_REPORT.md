# Cost Report

## Milestone: Formalised Reusable Skills Framework

**Date:** 2026-06-14

### Infrastructure Cost Impact

**No infrastructure cost impact.** This milestone exclusively updated:
- Skill definitions (`.md` files under `skills/`)
- Agent prompt files (`.txt` files under `.opencode/prompts/`)
- Documentation files (`AGENTS.md`, `README.md`)

No new Azure resources, Terraform modules, or Bicep templates were created or modified. There is zero change to the projected monthly Azure spend.

### Model Optimisation Cost Impact

Model optimisation relating to the agents that consume these skills was handled in a prior session (see `.opencode/memory.md`):
- `@security-auditor` runs on `opencode/deepseek-v4-pro` — **4.3x cheaper on outputs vs. predecessor**
- `@builder-infra-tf`, `@builder-infra-bicep`, `@builder-pipelines` run on `opencode/claude-sonnet-4-6` — same cost as predecessor ($3.00/$15.00 per 1M tokens)

### Token Consumption Notes

The `security-checklist` skill adds approximately 1,800 tokens of structured checklist content to each audit invocation. This is negligible against typical audit runs (which process hundreds of lines of IaC) and is offset by the reduction in ad-hoc security review overhead.

### Summary

| Category | Change | Cost Delta |
|----------|--------|------------|
| Azure resource footprint | None | ±$0.00/month |
| Model inference per audit | +1,800 tokens (checklist load) | < $0.01/run |
| Developer time | Reduced manual security review | Savings (qualitative) |

---

## Milestone: Complete Reusable Skills Framework & Prompt Reconciliation

**Date:** 2026-06-14

### Infrastructure Cost Impact

**No infrastructure cost impact.** This milestone exclusively updated:
- Skill definition files (6 new `skills/<name>/SKILL.md` files and their template mirrors)
- Prompt reconciliation between `.opencode/prompts/` and `templates/opencode-config/prompts/`
- Validation script (`scripts/validate-skills.py`)
- Documentation files (`AGENTS.md`, `BUILD_JOURNAL.md`, `COST_REPORT.md`, `WHITEPAPER_LOG.md`)

No new Azure resources, Terraform modules, or Bicep templates were created or modified. There is zero change to the projected monthly Azure spend.

### Model Optimisation Cost Impact

No model changes in this milestone (model optimisations were applied in the prior milestone, documented in `.opencode/memory.md`). The six new skills are consumed by the same agents with the same model assignments.

### Token Consumption Notes

| Skill | Estimated Token Cost | Notes |
|-------|---------------------|-------|
| `code-standards` | ~1,500 tokens | Loaded by code-reviewer during architectural reviews |
| `commit-format` | ~1,200 tokens | Loaded by builders before staging commits |
| `architecture-review` | ~500 tokens | Lightweight checklist; loaded during review gates |
| `plan-tracking` | ~400 tokens | Loaded by plan-validator and docs-writer |
| `doc-standards` | ~500 tokens | Loaded by docs-writer for documentation tasks |
| `test-patterns` | ~700 tokens | Loaded by test-writer and builder-infra-tf |

The combined token overhead for all skills (~4,800 tokens per full workflow cycle) is negligible against typical execution runs and is offset by the elimination of ad-hoc manual review and duplicated instructions.

### Summary

| Category | Change | Cost Delta |
|----------|--------|------------|
| Azure resource footprint | None | ±$0.00/month |
| Model inference per full cycle | +4,800 tokens (all skills) | < $0.01/run |
| Developer time | Reduced manual review overhead | Savings (qualitative) |
| CI/CD validation | New skill-reference validation gate | ±$0.00 (local script execution) |
