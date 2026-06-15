---
name: optimise
description: Static cost and resource optimization review checklist and finding report format
license: MIT
compatibility: opencode
---

## Review checklist

Work through every item. Mark each PASS / FAIL / N/A.

### Cost and Resource Optimization Rules
- [ ] **Key Vault SKU Gate:** Flag Premium SKU in dev/test environments; standard should be used unless HSM backing is explicitly required.
- [ ] **Key Vault Retention Trim:** In dev/test environments, recommend `soft_delete_retention_days = 30` (do not go below 7, which is the Azure minimum). **Purge protection (`purge_protection_enabled = true`) MUST remain enabled in all environments.** This is a non-negotiable security baseline — cost savings from disabling purge protection are never acceptable.
- [ ] **AppGW Capacity Tiers:** Validate capacity = 1 in dev/test environments to minimize baseline hourly gateway costs.
- [ ] **AppGW SKU Toggle:** Recommend Standard_v2 only if the gateway is *internal-only* (no public IP) AND the application does not process user-supplied data. Any internet-facing AppGW or gateway fronting a web application MUST retain WAF_v2 SKU regardless of environment. Cost savings from removing WAF on public endpoints are never acceptable.
- [ ] **Runner Scale-to-Zero:** Enforce scale-to-zero queue monitoring (`min_replicas = 0`) in non-production environments to avoid idle container runtime costs.
- [ ] **Runner Max Replicas Cap:** Enforce a maximum cap on runner replica scaling (`max_replicas <= 3`) in dev/test environments to prevent run-away autoscaling cost spikes.
- [ ] **Runner CPU/Memory Right-Sizing:** Recommend conservative CPU and Memory allocations (recommend `cpu = 0.5`, `memory = 1.0Gi` in dev/test environments) to align with lighter non-production workload demands.
- [ ] **Diagnostic Logging Cost Gate:** Warn about *verbose/debug-level* AppGW logging and excessive Log Analytics retention (>30 days) in non-production environments. **Security-critical diagnostic streams (Key Vault audit logs, NSG flow logs, Entra ID sign-in logs) MUST NOT be disabled for cost reasons.** Cost optimization for logging should target log level (e.g., `Error` instead of `Verbose`) and retention, not complete removal.

## Finding report format

For each failure:

```
### [COST SAVING] Short title
File: path/to/file.ext Line: N
Description: What the cost leak is and how it can be optimized.
Remediation: Exact code or config change required to fix it.
Estimated Monthly Savings: $X.XX
```

End with one of:
- Cost optimization gate: PASSED
- Cost optimization gate: FAILED — N cost leaks found, estimated monthly savings: $X.XX
