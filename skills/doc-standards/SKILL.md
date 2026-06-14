---
name: doc-standards
description: Standards for writing clear, descriptive, and accurate documentation, module READMEs, ADRs, and runbooks
license: MIT
compatibility: opencode
---

## Documentation Standards

All documentation must be written clearly, accurately, and logically for consumption by operations teams and developers:

### 1. Module READMEs
Every IaC module must include a `README.md` file documenting:
- **Description:** A clear explanation of what the module does and its architectural context.
- **Requirements:** Minimum versions of Terraform/Bicep and providers.
- **Providers:** List of providers used by the module.
- **Inputs:** Table of input variables, including names, descriptions, types, default values, and whether they are required.
- **Outputs:** Table of output values, including names and descriptions.
- **Resources:** List of resources deployed by the module.

### 2. Architecture Decision Records (ADRs)
Use ADRs to document key platform design and governance choices:
- **Format:** Use a standard ADR template (e.g., Title, Date, Status, Context, Decision, Consequences).
- **Location:** Store ADRs in a dedicated `docs/adr/` directory.
- **Clarity:** Explain the technical context, the alternatives considered, and the rationale for the chosen decision.

### 3. Runbooks & Onboarding Guides
Provide clear, step-by-step instructions for operations and onboarding:
- **Runbooks:** Document common operational tasks (e.g., rotating keys, scaling runners, troubleshooting pipeline failures).
- **Onboarding Guides:** Document how workload teams can onboard onto the landing zone and deploy their applications.
- **Clarity:** Use code blocks, tables, and clear headings to make instructions easy to follow.
