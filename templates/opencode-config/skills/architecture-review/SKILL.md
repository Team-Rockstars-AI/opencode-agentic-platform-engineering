---
name: architecture-review
description: Guidelines for reviewing architectural changes, subscription topologies, firewall rules, private endpoints, and central state access patterns
license: MIT
compatibility: opencode
---

## Architectural Review Guidelines

All architectural changes must be reviewed against the following standards to ensure security, reliability, and compliance:

### 1. Subscription Topology & Environment Isolation
- **Strict Isolation:** Ensure that Dev, Test, and Prod environments are deployed in separate Azure Subscriptions or Management Groups.
- **No Cross-Environment Access:** Dev pipelines must never have access to Prod subscriptions or Prod state files.
- **Shared Services:** Centralize shared services (e.g., Log Analytics, Container Registry, Private DNS Zones) in a dedicated Hub or Shared Services subscription.

### 2. Network Isolation & Firewall Rules
- **Private Link Integration:** Stateful resources (Key Vaults, Storage Accounts, Databases) must use Private Endpoints and Private DNS Zones.
- **NSG Rules:** Network Security Groups (NSGs) must be configured with no open management ports (no 22/3389 open to `0.0.0.0/0`).
- **Micro-segmentation:** Workloads must be isolated in dedicated subnets with strict NSG rules governing inbound and outbound traffic.

### 3. Central State Access & State Locking
- **Secure Backend:** Terraform state files must be stored in a secure, remote Azure Blob Storage backend with encryption-at-rest and restricted access.
- **State Locking:** State locking must be enabled to prevent concurrent modifications and state corruption.

### 4. Identity & Access Management (IAM)
- **Least Privilege:** Apply the Principle of Least Privilege (PoLP) for all Azure RBAC assignments.
- **Managed Identities:** Use System-Assigned or User-Assigned Managed Identities for resource-to-resource authentication.
- **OIDC Federation:** Use OpenID Connect (OIDC) Federated Credentials for pipeline authentication instead of long-lived client secrets.
