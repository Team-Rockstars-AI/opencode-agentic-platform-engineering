# Cost Governance & Sizing Guide

This document outlines the cost-saving strategies, sizing guidelines, and optimization rules enforced by this platform to prevent cost leaks while maintaining a strict security posture.

---

## 1. Cost Optimization Rules (The 8 Rules)

The platform enforces **8 static cost and resource optimization rules** (codified in the `optimise` skill) to ensure maximum resource efficiency:

1.  **Key Vault SKU Gating:** Standard Key Vaults must be used instead of Premium Key Vaults unless hardware security modules (HSM) or advanced cryptographic keys are explicitly required.
2.  **Soft-Delete Retention Trim:** Soft-delete retention must be set to the minimum required by compliance (typically 7 to 90 days) to avoid excessive storage reservation costs.
3.  **Application Gateway Capacity Limits:** Application Gateways must be configured with autoscale limits (e.g., `min_capacity = 1`, `max_capacity = 3`) instead of high fixed capacities.
4.  **Selective WAF Tier Toggles:** WAF v2 must be disabled on internal-only, non-public subnets to save on licensing costs, while remaining strictly enabled on public-facing endpoints.
5.  **Private Runner Scale-to-Zero:** Self-hosted runner pools must be hosted on Azure Container Apps with KEDA-based autoscaling, allowing them to scale to zero instances when no pipeline jobs are active.
6.  **Max Replicas Scaling Caps:** Container Apps and App Services must have strict `max_replicas` scaling caps (e.g., `max_replicas = 5` in non-production) to prevent runaway scaling costs.
7.  **Right-Sized CPU/Memory Variables:** CPU and Memory allocations for container runtimes must be parameterized and set to conservative defaults (e.g., `0.5 CPU` and `1.0 GiB Memory` for runners).
8.  **Logging Retention Controls:** Log Analytics workspace data retention must be set to the minimum required by compliance (typically 30 to 90 days) with older logs archived to low-cost cold storage.

---

## 2. Security Guardrails (Non-Negotiable Costs)

While cost optimization is critical, **security must never be compromised to save costs**. The following security features are non-negotiable and must remain enabled regardless of environment-tier:

*   **Purge Protection:** Must remain enabled on all Key Vaults to prevent malicious or accidental deletion of cryptographic assets.
*   **Public Endpoint WAF:** WAF v2 must remain enabled in Prevention Mode on all public-facing Application Gateways.
*   **Diagnostic Logging:** Critical security log streams (including NSG flow logs and Key Vault audit logs) must remain enabled and stream to Log Analytics.
*   **Private Link Isolation:** Stateful resources must remain isolated behind Private Endpoints, even in development environments.

---

## 3. Right-Sizing Guidelines

Use the following guidelines to right-size your infrastructure components across different environments:

### 1. Self-Hosted Runner Pools (ACA)
*   **Development/Test:**
    *   `runner_cpu`: `0.5`
    *   `runner_memory`: `1.0Gi`
    *   `min_replicas`: `0` (scale-to-zero enabled)
    *   `max_replicas`: `2`
*   **Production:**
    *   `runner_cpu`: `1.0`
    *   `runner_memory`: `2.0Gi`
    *   `min_replicas`: `0` (scale-to-zero enabled)
    *   `max_replicas`: `5`

### 2. Application Gateway (WAF v2)
*   **Development/Test:**
    *   `sku_name`: `WAF_v2`
    *   `tier`: `WAF_v2`
    *   `autoscale_min_capacity`: `1`
    *   `autoscale_max_capacity`: `2`
*   **Production:**
    *   `sku_name`: `WAF_v2`
    *   `tier`: `WAF_v2`
    *   `autoscale_min_capacity`: `2`
    *   `autoscale_max_capacity`: `10`

### 3. Log Analytics Workspace
*   **Development/Test:**
    *   `retention_in_days`: `30`
    *   `daily_quota_gb`: `1` (cap daily ingestion to prevent runaway costs)
*   **Production:**
    *   `retention_in_days`: `90` (or as required by compliance)
    *   `daily_quota_gb`: `-1` (no cap to ensure complete audit trails)

---

## 4. Running Cost Audits

To identify cost leaks and sizing inefficiencies in your workspace, run the `/optimise` slash command:
```bash
/optimise
```
This command will:
1.  Scan your IaC templates, subnets, and container configurations.
2.  Evaluate them against the 8 cost optimization rules.
3.  Generate a structured `COST_OPTIMISATION_REPORT.md` detailing exact files, lines, recommended remediations, and estimated monthly savings.
