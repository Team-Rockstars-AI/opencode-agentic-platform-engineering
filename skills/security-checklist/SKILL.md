---
name: security-checklist
description: Structured security review checklist and finding report format for the security-auditor agent in Platform Engineering
license: MIT
compatibility: opencode
---

## Review checklist

Work through every item. Mark each PASS / FAIL / N/A.

### A. HARD BLOCKS (Knock-out Criteria)
- [ ] **NO secrets in code or repo.** No hardcoded client secrets, passwords, or PATs in IaC or pipeline YAMLs. Use OIDC + Key Vault.
- [ ] **NO public network access to stateful resources.** Key Vaults, Storage Accounts, and Databases must have public access disabled.
- [ ] **NO broad IAM roles.** Apply Principle of Least Privilege (PoLP). No `Owner` or `Contributor` roles assigned to pipeline service principals.
- [ ] **NO stateful resources without soft-delete.** Key Vaults, Storage Accounts, and Databases must enable soft-delete and purge protection.
- [ ] **NO cross-environment access.** Dev pipelines must not have access to Prod subscriptions or Prod state files.
- [ ] **NO ignored pipeline failures.** Pipeline scripts must use `set -e` (or equivalent) to ensure failures stop the pipeline.
- [ ] **NO skipping validation.** Every commit/PR must run `terraform validate` / `bicep build` and security scanners (Checkov/tfsec).
- [ ] **NO untyped variables.** Avoid `type = any` in Terraform or loose parameter types in Bicep.

### B. Authentication and Session
- [ ] OIDC (Federated Credentials) used for pipeline authentication (no client secrets).
- [ ] Managed Identities (System/User-Assigned) used for resource-to-resource authentication.
- [ ] Remote state backend (Azure Blob Storage) configured with encryption-at-rest and restricted access.

### C. Authorisation
- [ ] Data-plane access uses Microsoft Entra ID authentication instead of connection strings or access keys.
- [ ] Network Security Groups (NSGs) configured with no open management ports (no 22/3389 open to `0.0.0.0/0`).

### D. Input Validation
- [ ] Terraform variables use `validation {}` blocks to enforce naming conventions, IP ranges, or allowed values.
- [ ] Bicep parameters use decorators like `@allowed`, `@minLength`, `@maxLength`, and `@secure`.

### E. Error Handling and Diagnostics
- [ ] Central Log Analytics diagnostic stream deployed for all infrastructure components.
- [ ] Diagnostic logs do not leak sensitive data (PII, secrets, connection strings).

## Finding report format

For each failure:

```
### [SEVERITY] Short title

File: path/to/file.ext  Line: N
Description: What the vulnerability is and how it can be exploited.
Remediation: Exact code or config change required to fix it.
```

SEVERITY: CRITICAL | HIGH | MEDIUM | LOW

End with one of:
- Security gate: PASSED
- Security gate: FAILED — N critical, N high findings
