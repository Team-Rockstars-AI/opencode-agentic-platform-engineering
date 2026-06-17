# Contributing

Welcome! This repository is a **cooperative, learning-focused** scaffold for
building secure-by-design, EU-compliant Azure platform infrastructure with
[OpenCode](https://opencode.ai) agentic development. Contributions of all sizes
are encouraged — bug reports, fixes, new modules, docs, and questions.

This guide explains how we work together so that changes stay reviewable, safe,
and easy to learn from.

## Table of contents

- [Code of conduct](#code-of-conduct)
- [Ways to contribute](#ways-to-contribute)
- [Getting started](#getting-started)
- [Branching model](#branching-model)
- [Commit messages](#commit-messages)
- [Before you open a pull request](#before-you-open-a-pull-request)
- [Pull request process](#pull-request-process)
- [Coding standards](#coding-standards)
- [Security](#security)

## Code of conduct

By participating you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).
Be kind, assume good intent, and help colleagues learn.

## Ways to contribute

- **Report a bug** — open a [bug report](.github/ISSUE_TEMPLATE/bug_report.yml).
- **Request a feature** — open a [feature request](.github/ISSUE_TEMPLATE/feature_request.yml).
- **Fix or build something** — pick up an issue, or open one first to discuss.
- **Improve docs** — documentation PRs are first-class contributions.
- **Report a vulnerability** — privately, per our [Security Policy](SECURITY.md).

## Getting started

```bash
# Clone and enter the repo
git clone https://github.com/Team-Rockstars-AI/opencode-agentic-platform-engineering.git
cd opencode-agentic-platform-engineering

# Python tooling (select-models, scaffold, skill validation)
python3 -m pip install -r requirements.txt
python3 -m pip install ruff   # linter used in CI

# Optional but recommended local checks
ruff check .
python3 scripts/validate-skills.py
terraform fmt -recursive          # if you touch Terraform
```

A repository walkthrough lives in the [README](README.md). Operator and
architecture documentation lives under [`docs/`](docs/).

## Branching model

Always work on a feature branch — **never commit directly to `main`**.

Branch naming (per the repo's `git-workflow` skill):

```
feature/<id>-<short-description>
```

Examples: `feature/F102-vnet-peering`, `feature/E45-keyvault-private-endpoint`.

Keep branches focused on a single change so reviews stay small and educational.

## Commit messages

We follow [Conventional Commits](https://www.conventionalcommits.org/) (see the
repo's `commit-format` skill):

```
<type>(<scope>): <description>
```

- **Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `ci`, `chore`.
- **Scope:** the module or component (e.g. `keyvault`, `network`, `runner`,
  `opencode`, `readme`).
- **Description:** imperative mood, lower-case, no trailing period.

Examples:

```
feat(keyvault): add private endpoint
fix(vnet): correct subnet mask
ci(github): add checkov scanning gate
docs(readme): document onboarding flow
```

## Before you open a pull request

Run the same checks CI runs, locally:

| Check | Command |
|:---|:---|
| Python lint | `ruff check .` |
| Python compiles | `python3 -m compileall scripts agent_config.py templates` |
| Skill references valid | `python3 scripts/validate-skills.py` |
| Terraform formatted | `terraform fmt -check -recursive` |
| No secrets committed | review your diff; push protection also guards this |

## Pull request process

1. Push your `feature/...` branch and open a PR against `main`.
2. Fill in the [pull request template](.github/PULL_REQUEST_TEMPLATE.md).
3. Ensure all CI checks pass — they run automatically on every PR
   (Python, config, Terraform, secret scan, security scan).
4. A [code owner](.github/CODEOWNERS) is automatically requested for review.
   Get at least **one approval** and resolve all conversations before merging.
5. Prefer **squash merge** to keep `main` history clean and Conventional.
6. Bandit, Checkov, gitleaks, and Dependabot run automatically; address any new findings.

> **Note on enforcement:** This repository is private on the GitHub Free plan,
> where branch protection / required checks cannot be enforced server-side. The
> review and green-CI steps above are therefore **team conventions we hold each
> other to**, not hard gates. If the org upgrades to GitHub Team (or the repo is
> made public), branch protection on `main` should be enabled to enforce them.

Because the goal is also learning: explain *why* in your PR description, not just
*what*. Reviewers should leave constructive, teaching-oriented comments.

## Coding standards

The repository ships its own opinionated skills under [`skills/`](skills/) that
encode our standards. The most relevant for contributors:

- `code-standards` — general code quality.
- `commit-format` — Conventional Commits (summarised above).
- `git-workflow` — branching and PR hygiene.
- `doc-standards` — module READMEs, ADRs, and runbooks.
- `security-checklist` — secure-by-design defaults.
- `test-patterns` — how to validate IaC and tooling.

When adding a Terraform/Bicep module, include a `README.md` documenting inputs,
outputs, providers, and resources, following the `doc-standards` skill.

## Security

Never commit secrets, tokens, `.tfvars`, or unencrypted state. Report
vulnerabilities privately — see [SECURITY.md](SECURITY.md). Automated scanning
(Bandit, Checkov, gitleaks, Dependabot) runs on every PR.
