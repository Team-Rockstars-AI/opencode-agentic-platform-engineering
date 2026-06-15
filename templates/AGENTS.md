# Azure Platform & Workload Operations — Agent Instructions

## Purpose

This repository manages the deployment, security compliance, and automated operation of the organization's Azure Landing Zone infrastructure and application workloads. 

Development and deployments in this repository are managed collaboratively by an OpenCode multi-agent automation team. All changes must be planned, compiled, audited, and safety-checked prior to deployment.

## Repository Structure

Based on your scaffolding selection, this repository contains:
- **`terraform/`**: Standard parameterized modules and deployment environments.
- **`bicep/`**: Subscription/Resource Group-scoped templates and parameter maps.
- **`.github/` or `pipelines/`**: Secure, OIDC-federated automated workflows.
- **`.opencode/`**: The local multi-agent configuration, specialized subagent prompts, and custom validation rules.

## Multi-Agent Operations Topology

Your workspace utilizes an **Orchestration-Led multi-agent paradigm** optimized for secure platform-engineering operations.

### Strategic Planning
*   **`orchestrator`**: The entry point for all operations. Decouples requirements, reviews the backlog, schedules rollout phases, and delegates infrastructure implementation to specialized builders.

### Specialized Implementation Builders
*   **`builder-infra-tf`**: Authors secure, parameterized, modular Terraform. Enforces diagnostic streams, soft delete, and asserts unit tests via `.tftest.hcl`.
*   **`builder-infra-bicep`**: Authors multi-scope Bicep templates with diagnostic and governance integrations.
*   **`builder-pipelines`**: Designs automated workflows with zero long-lived credentials, strictly enforcing passwordless OIDC authentication.

### Continuous Verification Gates (Read-Only)
*   **`verifier`**: Compiles modified code (`terraform validate` / `bicep build`), runs linters, and outputs dry-run logs.
*   **`security-auditor`**: Scans configuration files for compliance deviations, exposed parameters, or overly broad permissions.
*   **`plan-validator`**: **BLAST RADIUS SAFETY GATE.** Parses dry-run logs. Immediately blocks any deployment if databases, networking hubs, or vaults are scheduled for deletion or recreation.
*   **`code-reviewer`**: Audits configurations for CAF naming conventions, resource tagging, and design standards.

## Secure Governance & Security Guardrails

All infrastructure and application workloads must adhere to the following secure baseline standards, which are codified and enforced via the `security-checklist` skill:
- **Federated Login (OIDC)**: No long-lived client secrets. All pipelines must authenticate using Azure Federated Credentials.
- **State Resiliency**: Storage accounts, databases, and Key Vaults must enable soft-delete and purge protection.
- **Network Isolation**: Restrict stateful resources behind Private Endpoints and Network Security Groups with no open management ports (no 22/3389 open to `0.0.0.0/0`).
- **Diagnostic Logging**: Route all active diagnostic streams to the central Log Analytics Workspace.
- **Strict Environment Isolation**: Dev pipelines must not have access to Prod subscriptions or Prod state files.
- **Strict Error Propagation**: Pipeline scripts must use `set -e` (or equivalent) to ensure failures stop the pipeline.
- **Continuous Validation**: Every commit/PR must run `terraform validate` / `bicep build` and security scanners (Checkov/tfsec).
- **Strict Typing**: Avoid `type = any` in Terraform or loose parameter types in Bicep. Enforce variable validation blocks and decorators.

## Reusable Skills (`skills/`)

Your workspace includes a set of reusable **Skills** — codified procedures that agents invoke via the `skill` tool. Skills standardise common operations across the codebase:

| Skill | Consumed By | Purpose |
|-------|-------------|---------|
| **`architecture-review`** | `@code-reviewer`, `@orchestrator` | Architectural change review covering subscription topology, network isolation, central state access, and IAM least-privilege standards. |
| **`audit`** | `/audit` workflow | Workspace compliance scan — codebase secrets check, NSG/public-endpoint audit, Private Endpoint verification. Loads `security-checklist` for structured reporting. |
| **`code-standards`** | `@code-reviewer`, `@builder-infra-tf`, `@builder-infra-bicep` | CAF naming conventions, Azure Well-Architected Framework alignment, tagging standards, and IaC best practices for Terraform and Bicep. |
| **`commit-format`** | `@builder-infra-tf`, `@builder-infra-bicep`, `@builder-pipelines` | Conventional Commits specification enforcing structured commit types, scopes, and description format for automated changelog generation. |
| **`debug`** | `/debug` workflow | Compilation error tracing and resolution. |
| **`doc-standards`** | `@docs-writer` | Documentation standards for module READMEs, ADR format, runbooks, and onboarding guides. |
| **`expand`** | `/expand` workflow | Guided rollout of new IaC resource modules under governance guardrails. |
| **`git-workflow`** | `@builder-infra-tf`, `@builder-infra-bicep`, `@builder-pipelines` | Branch naming, pre-commit hygiene (formatter, precision staging), commit blacklist (no secrets, debug artifacts, commented-out code), and standardised handoff summary for `@test-writer`. |
| **`optimise`** | `/optimise` workflow | Static cost and resource optimization review checklist and finding report format. |
| **`plan-tracking`** | `@plan-validator`, `@docs-writer` | Execution plan JSON conversion, resource action tracking, milestone status updates, and session state maintenance. |
| **`scaffold`** | `/scaffold` workflow | Template selection, copy, placeholder substitution, git init. |
| **`security-checklist`** | `@security-auditor`, `audit` skill | Structured PASS/FAIL/NA review checklist covering OIDC, network isolation, soft-delete, least-privilege IAM, diagnostic logging, and strict typing. Produces findings with severity ratings and remediation blocks. |
| **`test-patterns`** | `@test-writer`, `@builder-infra-tf` | Unit and validation test guidelines for Terraform (.tftest.hcl) and Bicep modules, including plan assertions and what-if validation patterns. |

## Developer Commands & Slash Actions

Interact with your multi-agent platform team directly from the OpenCode terminal using these custom slash commands:

*   **`/audit`**: Scans your entire workspace (IaC templates, subnets, NSGs, and pipelines) for credentials leaks, compliance defects, and network isolation failures. Outputs a comprehensive compliance report.
*   **`/debug`**: Directs the verifier and builder agents to inspect failing pipeline execution logs, trace resource syntax compiler warnings, and propose/implement automated code fixes.
*   **`/expand`**: Initiates a guided rollout to deploy new resource components (e.g., Virtual Networks, Databases, Containers, Private Endpoints) and secure-by-design pipelines under strict organization governance.
*   **`/optimise`**: Scans your entire workspace (IaC templates, subnets, and container apps) for cost leaks, oversized SKUs, and resource sizing inefficiencies. Outputs a comprehensive cost optimization report.

```bash
# Validate Terraform structures
cd terraform && terraform init -backend=false && terraform validate

# Compile and validate Bicep configurations
bicep build main.bicep --stdout > /dev/null

# Execute local multi-agent checks
opencode run verify
```
