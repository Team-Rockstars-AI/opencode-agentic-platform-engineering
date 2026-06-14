---
name: expand
description: Onboards new application workloads, expands landing zones, or deploys new cloud resources. Trigger when the user runs /expand.
---

# Expand Infrastructure and Workloads Skill

This skill coordinates the safe expansion of landing zones and onboarding of new workload resources under strict governance policies.

## Trigger
Use this skill when the user requests a new spoke subnet, onboards a new containerized app, or runs the `/expand` slash command.

## Steps
1. **Specification Gathering:**
   - Ask the user to clarify the resource requirements, workload types, and desired isolation configurations.
2. **Governance Enforcement:**
   - Align the design with secure-by-design baselines (disable public access, set up Private Endpoints, configure NAT Gateway routing, enable resource logging, and set up Entra ID managed identities).
3. **Drafting Blueprint:**
   - Summon the `@builder-infra-tf` (or `@builder-infra-bicep`) to implement the resource, and `@builder-pipelines` to update OIDC workflows.
4. **Validation Check:**
   - Trigger `@verifier` and `@security-auditor` to check format and compliance before finalizing the rollout.
