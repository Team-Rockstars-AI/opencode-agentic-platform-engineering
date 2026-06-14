# ADR 0003: Private Endpoints and Network Isolation for Stateful Resources

## Status
Accepted

## Context
By default, Azure stateful resources such as Azure Key Vaults, Azure Storage Accounts, and Azure SQL Databases expose public IP addresses. Although protected by Microsoft Entra ID authentication and firewall rules, public endpoints are exposed to the public internet, leaving them open to potential scanning, DDoS attempts, and misconfiguration risks.

In enterprise and secure-by-design architectures, public exposure of data planes must be blocked entirely. Stateful services must be isolated from the public internet and accessible only via internal private networks.

We need a standardized network architecture to securely connect workloads to stateful resources.

## Decision
We will enforce network isolation and the use of Azure Private Endpoints for all stateful resources deployed by this platform.

- **Disable Public Access**: All Key Vaults, Storage Accounts, and Database resources must set the network access policy to block public network traffic (e.g., `public_network_access_enabled = false` in Terraform or equivalent in Bicep).
- **Private Endpoints**: We will deploy an Azure Private Endpoint for each stateful resource. This assigns a private IP address from a designated subnet within our Virtual Network (VNet) to the resource's data plane.
- **Private DNS Integration**: Private Endpoints require proper DNS resolution. We will deploy and configure Azure Private DNS Zones (e.g., `privatelink.vaultcore.azure.net`) and link them to our workload VNets.
- **Bypass for Trusted Services**: Where necessary, we will configure firewall rules to allow trusted Microsoft services (such as Azure Backup or Azure Monitor) to access the stateful resource securely.

## Consequences

### Positive
- **Eliminated Internet Threat Vector**: Stateful resources have no public IP, preventing internet-based scanning, enumeration, or brute force attacks.
- **Data Exfiltration Prevention**: Private Endpoints restrict communication to specific resource instances. This prevents compromised virtual machines or containers from sending data to arbitrary external storage accounts.
- **Compliance Alignment**: Meets strict enterprise compliance standards (ISO 27001, PCI-DSS, SOC 2, HIPAA) regarding network isolation and database security.

### Negative / Neutral
- **Networking Cost**: Azure charges a nominal hourly fee for each Private Endpoint and for private DNS zone queries, which can scale up in large environments.
- **DNS Configuration Overhead**: Requires robust Private DNS Zone management to avoid resolution failures between VNets.
- **Pipeline Deployment Access**: Because resources are isolated on private networks, standard public CI/CD runners cannot directly query or update database schemas, Key Vault secrets, or storage containers. This necessitates private networking routing or self-hosted runners.

## References
- [ADR 0001: Record Architecture Decisions](0001-record-architecture-decisions.md)
- [ADR 0005: Self-Hosted Runners with KEDA Scaling for Enterprise Deployments](0005-self-hosted-runners-with-keda-scaling-for-enterprise-deployments.md)
- [What is an Azure Private Endpoint?](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview)
- [Azure Private Endpoint DNS Integration](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns)
