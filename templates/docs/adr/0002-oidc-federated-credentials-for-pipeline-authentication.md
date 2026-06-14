# ADR 0002: Use OIDC Federated Credentials for Pipeline Authentication

## Status
Accepted

## Context
Deploying infrastructure-as-code (IaC) templates to Azure from automated CI/CD pipelines (such as GitHub Actions or Azure DevOps) requires authorization. Traditionally, this is achieved by creating a Service Principal (App Registration) in Azure Active Directory (Microsoft Entra ID) and storing its generated client secret or certificate as a repository/pipeline secret.

This approach presents several security and operational risks:
1. **Secret Leakage**: Hardcoded secrets can accidentally be printed to pipeline logs, checked into source control, or exposed through unauthorized workflow modifications.
2. **Rotation Overhead**: Secrets have expiration dates. Rotating them manually or via script across dozens of repositories introduces significant maintenance overhead and potential pipeline outages if secrets expire.
3. **Broad Privilege Scope**: Stored secrets have static permissions that are active 24/7, making them high-value targets if compromised.

We need a secure, passwordless authentication method that eliminates long-lived credentials in pipelines.

## Decision
We will enforce OpenID Connect (OIDC) with Azure Federated Credentials for all pipeline authentication across the platform.

- **Mechanics**: The pipeline workflow requests a short-lived JSON Web Token (JWT) from the OIDC provider (GitHub Actions or Azure DevOps). This JWT is presented to Microsoft Entra ID, which validates the trust relationship and exchanges it for a short-lived Azure Access Token (typically valid for 1 hour).
- **Federated Trust Definition**: Federated identity credentials will be configured in Microsoft Entra ID to establish trust explicitly scoped to:
  - The organization/username.
  - The repository name.
  - The specific environment, branch, or pull request context.
- **Zero Secrets**: No Azure client secrets or certificates will be stored inside pipeline settings. The only configuration values stored will be the public identifiers (Tenant ID, Subscription ID, and Client/Application ID).

## Consequences

### Positive
- **No Long-Lived Secrets**: Eliminates credential leak vectors. Even if pipeline public configurations are exposed, they cannot be used outside the context of the running, federated runner.
- **Zero Rotation Management**: Because no client secrets are generated, there are no expiration dates to track, eliminating credential rotation chores.
- **Tight Resource Scoping**: Entra ID only issues Azure tokens for requests originating from the matched branch or environment, ensuring strict security boundaries.
- **Enhanced Auditing**: Azure Activity logs will capture the token exchange flow, tracking actions back to the specific workflow execution.

### Negative / Neutral
- **Initial Setup Configuration**: Requires configuring federated credentials on Azure Service Principals, which can be automated via IaC or scripts.
- **Platform-Specific Trust**: Requires both the OIDC provider and Microsoft Entra ID to be available during the authentication phase.

## References
- [ADR 0001: Record Architecture Decisions](0001-record-architecture-decisions.md)
- [Microsoft Entra ID Workload Identity Federation](https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation)
- [GitHub Actions: Configuring OpenID Connect in Azure](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-cloud-providers)
