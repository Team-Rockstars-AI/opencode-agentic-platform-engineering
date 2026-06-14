# ADR 0004: Subnet-Level Micro-Segmentation via Network Security Groups

## Status
Accepted

## Context
In monolithic or legacy virtual networks, all subnets and workloads often share unrestricted communication with one another. If a single workload or virtual machine is compromised, attackers can easily move laterally across the network to access sensitive databases, storage layers, or management interfaces.

To enforce a Zero Trust architecture, we must apply the principle of least privilege to our network topology. Every network path must be explicitly evaluated and restricted to authorized traffic.

We need a consistent approach to restrict network traffic within our Virtual Networks (VNets).

## Decision
We will enforce subnet-level micro-segmentation across all virtual networks using Network Security Groups (NSGs).

- **Dedicated NSGs**: Every single subnet deployed within our platform (e.g., frontend, backend, database, private endpoints, runner subnets) must be associated with a dedicated Network Security Group (NSG). No subnet may be left without an associated NSG.
- **Explicit Default Deny**: While Azure subnets allow internal VNet communication by default, we will design our NSG rules to explicitly restrict inbound traffic to only the required sources and ports.
- **Port and Source Hardening**:
  - Administrative ports (such as `22` for SSH or `3389` for RDP) are strictly prohibited from being exposed to the public internet (`0.0.0.0/0`).
  - Workloads must communicate only with adjacent architectural layers (e.g., Frontend subnet can talk to Backend subnet, but Frontend cannot talk directly to Database subnet).
- **Application Security Groups (ASGs)**: Where applicable, we will utilize Application Security Groups to group virtual machine interfaces and define rules based on application roles rather than static IP addresses.

## Consequences

### Positive
- **Reduced Lateral Movement**: If a frontend container or virtual machine is compromised, the NSG blocks any direct network access to the database subnet or other unrelated workloads.
- **Infrastructure-as-Code Compliance**: Network security policies are codified in IaC (Terraform/Bicep), making network policies easily auditable during Pull Request reviews.
- **Defense-in-Depth**: Complements host-level firewalls and web application firewalls (WAF) to provide multi-layered security.

### Negative / Neutral
- **Rules Management Overhead**: Managing numerous NSGs and associated rules can lead to configuration complexity and potential errors.
- **Strict Network Planning**: Developers must understand and declare network dependencies beforehand, which can slow down rapid prototyping of highly distributed microservices.

## References
- [ADR 0001: Record Architecture Decisions](0001-record-architecture-decisions.md)
- [Azure Network Security Groups Overview](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview)
- [Azure Best Practices for Network Security](https://learn.microsoft.com/en-us/azure/security/fundamentals/network-best-practices)
