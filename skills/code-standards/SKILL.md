---
name: code-standards
description: Coding standards, naming conventions (CAF), tagging rules, and Azure Well-Architected Framework (WAF) guidelines for IaC development
license: MIT
compatibility: opencode
---

## Azure Well-Architected Framework (WAF) Alignment

All Infrastructure as Code (IaC) must align with the five pillars of the Azure Well-Architected Framework:

### 1. Security (WAF-SEC)
- **Private Connectivity:** Isolate all stateful resources (Key Vaults, Storage Accounts, Databases) behind Private Endpoints. Disable public network access.
- **Least Privilege IAM:** Scope RBAC roles as tightly as possible. Avoid assigning `Owner` or `Contributor` to pipeline service principals; use specific roles (e.g., `Key Vault Secrets Officer`, `Storage Blob Data Contributor`).
- **Encryption:** Enforce TLS 1.2+ minimum on all endpoints. Enable encryption-at-rest with platform-managed or customer-managed keys.

### 2. Reliability (WAF-REL)
- **State Resiliency:** Enable soft-delete and purge protection on Key Vaults. Enable soft-delete, versioning, and container immutability on Storage Accounts.
- **High Availability:** Deploy resources across multiple Availability Zones where supported.
- **Backup & Retention:** Configure automated backups and retention policies for all databases and stateful services.

### 3. Cost Optimization (WAF-COST)
- **Right-Sizing:** Select appropriate SKUs and sizes based on environment requirements (e.g., use standard/basic SKUs for Dev/Test, premium/production SKUs for Prod).
- **Scale-to-Zero:** Leverage scale-to-zero capabilities (e.g., KEDA-scaled Container Apps for runners) to eliminate idle compute costs.
- **Resource Lifecycle:** Implement auto-shutdown or deletion schedules for non-production environments.

### 4. Operational Excellence (WAF-OPS)
- **Diagnostic Logging:** Stream all resource diagnostic logs and metrics to a central Log Analytics Workspace immediately.
- **Infrastructure as Code:** All infrastructure must be defined declaratively. No manual "click-ops" modifications in the Azure Portal.
- **Continuous Validation:** Run syntax validation, linting, and security scanning on every commit/PR.

### 5. Performance Efficiency (WAF-PERF)
- **Caching & CDN:** Use Azure Front Door or CDN for static content delivery.
- **Resource Scaling:** Configure autoscale rules for compute resources (VMSS, App Services, AKS) based on metrics like CPU/Memory.

---

## Cloud Adoption Framework (CAF) Naming Conventions

All resources must follow the standard CAF naming convention:

Format: `<resource-type-prefix>-<project-name>-<environment>-<location>`

### Common Resource Prefixes:
- Resource Group: `rg-`
- Virtual Network: `vnet-`
- Subnet: `snet-`
- Network Security Group: `nsg-`
- Key Vault: `kv-`
- Storage Account: `st` (no hyphens, max 24 chars, alphanumeric only)
- Log Analytics Workspace: `law-`
- Private Endpoint: `pe-`
- Private DNS Zone: `pdnsz-`
- Application Gateway: `agw-`
- Container App: `ca-`
- Container App Environment: `cae-`

*Example:* `rg-sovereign-core-dev-westeurope`

---

## CAF Tagging Rules

Every resource must be deployed with the following mandatory tags:

| Tag Name | Description | Example |
|:---|:---|:---|
| `Environment` | Deployment environment | `dev`, `test`, `prod` |
| `Project` | Name of the project/workload | `sovereign-core` |
| `ManagedBy` | Automation tool managing the resource | `OpenCode-Platform-Engineer` |
| `GovernanceTier` | Governance level applied | `basic`, `enterprise` |
| `CostCenter` | Cost center for billing | `CC-1024` |
| `Owner` | Team or individual responsible | `platform-team` |

---

## IaC Best Practices

### Terraform Standards
- **Version Pinning:** Pin Terraform core version and all provider versions in `providers.tf`.
- **Strict Typing:** Avoid `type = any` for variables. Define explicit object types, lists, or maps.
- **Variable Validation:** Use `validation {}` blocks to enforce naming conventions, IP ranges, or allowed values.
- **Outputs:** Always output resource IDs, URIs, or connection endpoints needed by downstream modules.
- **Remote State:** Store state files in a secure, remote Azure Blob Storage backend with state locking enabled.

### Bicep Standards
- **Target Scope:** Explicitly define the target scope (e.g., `targetScope = 'subscription'` or `targetScope = 'resourceGroup'`).
- **Strict Typing:** Use explicit parameter types. Avoid loose types.
- **Decorators:** Use `@allowed`, `@minLength`, `@maxLength`, and `@secure` (for passwords/secrets) decorators.
- **Nested Modules:** Break complex deployments into reusable, nested Bicep modules.
- **Outputs:** Define clear outputs for resource properties needed by other deployments.
