---
name: commit-format
description: Conventional Commits specification and standards for platform engineering repositories
license: MIT
compatibility: opencode
---

## Conventional Commits Specification

All commits in this repository must follow the Conventional Commits specification. This ensures clean, readable, and automated changelogs.

Format:
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

---

## Commit Types

Use one of the following types for every commit:

| Type | Description | Example |
|:---|:---|:---|
| `feat` | A new feature (e.g., a new IaC module, a new pipeline) | `feat(keyvault): add private endpoint` |
| `fix` | A bug fix (e.g., fixing a syntax error, correcting an IP range) | `fix(vnet): correct subnet mask` |
| `docs` | Documentation only changes (e.g., updating READMEs, ADRs) | `docs(readme): update onboarding guide` |
| `style` | Formatting, white-space, or style changes (no code logic changes) | `style(bicep): format main.bicep` |
| `refactor` | A code change that neither fixes a bug nor adds a feature | `refactor(network): simplify subnet loops` |
| `perf` | A code change that improves performance or cost efficiency | `perf(runner): optimize scale-to-zero rules` |
| `test` | Adding missing tests or correcting existing tests | `test(keyvault): add unit assertions` |
| `ci` | Changes to CI/CD pipelines and scripts | `ci(github): add checkov scanning gate` |
| `chore` | Changes to auxiliary tools, configs, or dependencies | `chore(opencode): update model mappings` |

---

## Commit Scope

The scope is optional but highly recommended. It should specify the module, component, or environment being modified:
- `keyvault`
- `network`
- `runner`
- `pipeline`
- `opencode`
- `readme`

---

## Commit Description

- Use the **imperative, present tense**: "change" not "changed" nor "changes".
- Do not capitalize the first letter.
- Do not end the description with a period.

*Example:* `feat(keyvault): add diagnostic settings` (Correct)  
*Example:* `Feat(keyvault): Added diagnostic settings.` (Incorrect)

---

## Commit Body (Optional)

Use the body to explain the **what** and **why** of the change, especially for complex modifications. Separate the body from the description with a blank line.

*Example:*
```
feat(network): add nat gateway to public subnets

All outbound internet traffic from the application subnets must now route
through the NAT Gateway to provide outbound SNAT and remove the need for
public IPs on individual workloads.
```

---

## Commit Footer & Breaking Changes (Optional)

Use the footer to reference issue IDs, pull requests, or to document breaking changes.

- **Breaking Changes:** Must start with `BREAKING CHANGE:` followed by a space and a description of what broke and how to migrate. Alternatively, append a `!` after the type/scope (e.g., `feat(vnet)!: remove public subnets`).

*Example:*
```
refactor(network)!: remove public subnets

Public subnets are no longer supported. All workloads must deploy into private subnets.

BREAKING CHANGE: Any workload relying on public subnets must migrate to private subnets with NAT Gateway routing.
```
