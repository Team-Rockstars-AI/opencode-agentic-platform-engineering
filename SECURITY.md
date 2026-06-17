# Security Policy

This repository scaffolds **secure-by-design, EU-compliant Azure platform
infrastructure**. We take the security of both the tooling and the infrastructure
patterns it produces seriously.

## Reporting a vulnerability

**Please do not open public issues for security vulnerabilities.**

Report privately using GitHub Security Advisories:

1. Go to the [Security tab](https://github.com/Team-Rockstars-AI/opencode-agentic-platform-engineering/security/advisories/new).
2. Click **Report a vulnerability** and provide:
   - A description of the issue and its impact.
   - Steps to reproduce or a proof of concept.
   - Affected files, modules, or templates.

If you cannot use GitHub advisories, contact the maintainers directly through
your internal Team Rockstars AI channel.

We aim to acknowledge reports within **3 business days** and to provide a
remediation plan or fix timeline within **10 business days**.

## Scope

In scope:

- The Python tooling (`scripts/`, `agent_config.py`).
- The Terraform and Bicep modules in `modules/` and `templates/`.
- The OpenCode agents, skills, and CI workflows.
- Insecure-by-default patterns produced by the scaffold.

Out of scope:

- Vulnerabilities in third-party dependencies already tracked by Dependabot
  (please let those advisories flow through automatically).
- Issues requiring physical access or a compromised maintainer account.

## Automated security controls

This repository runs several automated controls on every pull request and on a
weekly schedule:

| Control | Tool | Where results appear |
|:---|:---|:---|
| Static code analysis | CodeQL | Security → Code scanning |
| IaC misconfiguration scanning | Checkov | Security → Code scanning |
| Secret scanning | gitleaks (CI) + GitHub secret scanning + push protection | CI logs / Security |
| Dependency advisories | Dependabot alerts & security updates | Security → Dependabot |

## Handling secrets

Never commit secrets, API keys, tokens, passwords, `.tfvars`, or unencrypted
state. Push protection is enabled to block accidental secret commits. If a secret
is exposed, **rotate it immediately** and notify the maintainers.
