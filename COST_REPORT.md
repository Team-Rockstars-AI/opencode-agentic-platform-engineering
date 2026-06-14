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

---

## Milestone: Security Remediation & Hardening

**Date:** 2026-06-14

### Infrastructure Cost Impact

**No net Azure spend change.** All five security fixes were implemented in existing modules without introducing new billable Azure resource categories:

| Change | Resource Type | Cost Classification |
|--------|---------------|---------------------|
| OIDC bootstrap custom roles | `azurerm_role_definition` | Free (Azure RBAC management plane) |
| Key Vault purge protection + network ACLs | Property changes on existing Key Vault | Free (configuration change, no new resource) |
| Key Vault public network access disabled | Property change | Free (no data transfer change — denies unwanted traffic) |
| Network Security Groups | `azurerm_network_security_group` (4 subnets) | **Free** (NSG resource itself has no hourly cost) |
| NSG subnet associations | `azurerm_subnet_network_security_group_association` | Free (control plane binding) |
| Application Gateway HTTPS parameterisation | Dynamic `ssl_certificate` + `http_listener` blocks | **No cost change** — existing Application Gateway supports multiple listeners on the same WAF_v2 SKU at no extra charge |
| Pipeline `set -euo pipefail` hardening | YAML script flag | Free (syntax change) |

**Key takeaway:** The only resource that could incur cost is the Application Gateway WAF_v2 itself, which was already deployed in the network baseline. Adding an HTTPS listener, frontend port, and SSL certificate to an existing WAF_v2 instance does not change the billing meter.

### Model Optimisation Cost Impact

**No model changes in this milestone.** The security remediation was implemented by the existing builder agents (`@builder-infra-tf`, `@builder-infra-bicep`, `@builder-pipelines`) using their current model assignments (all on `opencode/claude-sonnet-4-6`). No new skills were created, so there is no additional skill-loading token overhead.

### Token Consumption Notes

No additional token overhead was introduced. The security changes were authored as direct modifications to existing Terraform and Bicep modules — no new skills or prompt files were created. Token consumption for this milestone is attributable to the normal module authoring workflow.

### Summary

| Category | Change | Cost Delta |
|----------|--------|------------|
| Azure resource footprint | No new billable resources | ±$0.00/month |
| Model inference per milestone | Standard module authoring | < $0.05 (estimated) |
| Security posture | Moved from Contributor → custom role; KV isolated; NSGs in place; HTTPS parameterised | Significant qualitative improvement |
| Pipeline resilience | `set -euo pipefail` everywhere | ±$0.00 |

---

## Milestone: Optimal Platform Hardening & Micro-segmentation

**Date:** 2026-06-14

### Infrastructure Cost Impact

**No Azure spend change.** All five fixes were applied to existing modules without introducing new billable Azure resource categories:

| Change | Resource Type | Cost Classification |
|--------|---------------|---------------------|
| App Gateway Resource ID Bug fix | Bicep variable logic change | Free (syntax/logic change) |
| Removal of `listKeys/action` from deployer role | Role definition permission change | Free (RBAC management plane — no cost impact) |
| Input validation blocks and parameter decorators | `validation {}` blocks (Terraform) + decorators (Bicep) | Free (compile-time/plan-time validation only) |
| Diagnostic settings for NSGs | `Microsoft.Insights/diagnosticSettings` (4 NSGs) | **Free** (diagnostic setting resources have no hourly cost; only the Log Analytics data ingestion is billable, and NSG logs are typically low-volume) |
| Key Vault soft-delete retention 7 → 90 days | Property change on existing Key Vault | Free (configuration change, no new resource) |

**Key takeaway:** The diagnostic settings are the only change with a potential downstream cost implication — if consumers enable NSG flow log streaming to Log Analytics, data ingestion charges apply based on volume. The diagnostic setting resource itself is free, and NSG NetworkSecurityGroupEvent/NetworkSecurityGroupRuleCounter logs are typically low-volume relative to other telemetry sources.

### Model Optimisation Cost Impact

**No model changes in this milestone.** All work was executed by the existing builder agents (`@builder-infra-tf`, `@builder-infra-bicep`) using their current model assignments (`opencode/claude-sonnet-4-6`). No new skills were created, so there is no additional skill-loading token overhead.

### Token Consumption Notes

No additional token overhead was introduced. Changes were authored as direct modifications to existing Terraform and Bicep modules — no new skills, prompt files, or agent definitions were created. Token consumption is attributable to standard module authoring workflow.

### Summary

| Category | Change | Cost Delta |
|----------|--------|------------|
| Azure resource footprint | No new billable resources | ±$0.00/month |
| Model inference per milestone | Standard module authoring | < $0.05 (estimated) |
| Security posture | Zero-trust micro-segmentation via NSG deny-all rules; least-privilege role without `listKeys`; input validation guardrails; centralised diagnostics; 90-day KV soft-delete | Significant qualitative improvement |
| Operational observability | NSG diagnostic logs streamed to Log Analytics | ±$0.00 (setting resource free; nominal ingestion cost if volume is low)
