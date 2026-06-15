# Architecture Blueprint & Network Topology

This document provides a detailed architectural blueprint and network topology of the secure-by-design landing zone baseline scaffolded by this platform. It outlines the network isolation, inbound/outbound traffic routing, and private connectivity standards enforced by default.

---

## 1. Hub-Spoke Network Topology

The platform enforces a secure, micro-segmented **Hub-Spoke network topology** designed to isolate workloads, centralize shared services, and eliminate public internet exposure.

```text
                                 [ Internet ]
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Application Gateway     │
                         │ (WAF v2 - Prevention)   │
                         └────────────┬────────────┘
                                      │ (Inbound HTTPS)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Virtual Network (Hub)                                                   │
│                                                                         │
│  ┌────────────────────────┐                                             │
│  │ Subnet: appgw          │                                             │
│  │ (App Gateway Frontend) │                                             │
│  └───────────┬────────────┘                                             │
│              │                                                          │
│              │ (Inbound HTTP/HTTPS)                                     │
│              ▼                                                          │
│  ┌────────────────────────┐                                             │
│  │ Subnet: workloads      ├──────────┐                                  │
│  │ (Container Apps/VMs)   │          │                                  │
│  └───────────┬────────────┘          │ (Private Traffic)                │
│              │                       ▼                                  │
│              │ (Outbound Traffic) ┌──────────────────────────────┐      │
│              ▼                    │ Subnet: endpoints            │      │
│  ┌────────────────────────┐       │ (Private Endpoints)          │      │
│  │ Subnet: runners        ├──────►└──────────────┬───────────────┘      │
│  │ (Self-Hosted Runners)  │                      │                      │
│  └───────────┬────────────┘                      │ (Private Link)       │
└──────────────┼───────────────────────────────────┼──────────────────────┘
               │                                   ▼
               │                            ┌──────────────────────────────┐
               │                            │ Stateful Resources           │
               │                            │ (Key Vault, Storage, etc.)   │
               │                            └──────────────────────────────┘
               │ (Outbound SNAT)
               ▼
┌───────────────────────────┐
│ Azure NAT Gateway         │
│ (Standard Public IP)      │
└───────────────────────────┘
```

---

## 2. Inbound Traffic Routing (Application Gateway + WAF v2)

All inbound application traffic is routed through a centralized **Azure Application Gateway (WAF v2)** to protect workloads against OWASP Top 10 web vulnerabilities.

*   **WAF Prevention Mode:** The Web Application Firewall (WAF) is configured in **Prevention Mode** utilizing the OWASP 3.2 rule set. It actively blocks malicious traffic (SQL injection, cross-site scripting, etc.) before it reaches the workloads subnet.
*   **HTTPS Enforcement:** The Application Gateway enforces HTTPS (port 443) for all frontend listeners. SSL certificates are securely bound from a centralized Azure Key Vault.
*   **HTTP Fallback/Redirect:** An HTTP listener (port 80) is configured to automatically redirect all inbound HTTP traffic to the secure HTTPS listener.
*   **Backend Pool Routing:** Traffic is routed from the Application Gateway to the private IP addresses of the workloads (e.g., Container Apps or Virtual Machines) residing in the `workloads` subnet.

---

## 3. Outbound Traffic Routing (Azure NAT Gateway)

To prevent workloads and container runtimes from requiring public IP addresses, all outbound internet traffic is routed through a centralized **Azure NAT Gateway**.

*   **Standard Public IP:** The NAT Gateway is associated with a standard Public IP address, providing a single, predictable outbound SNAT IP for all subnets.
*   **Subnet Association:** The NAT Gateway is associated with the `workloads`, `runners`, and `endpoints` subnets.
*   **Security Benefits:** Workloads can securely fetch package updates, container images, and external API data without being directly exposed to inbound internet probes.

---

## 4. Private Link Integration (Private Endpoints)

Stateful resources (such as Azure Key Vaults, Storage Accounts, and Databases) are completely isolated from the public internet using **Azure Private Endpoints**.

*   **Public Access Disabled:** Public network access is explicitly disabled (`public_network_access_enabled = false` in Terraform / `publicNetworkAccess: 'Disabled'` in Bicep) on all stateful resources.
*   **Private DNS Zones:** Private DNS Zones (e.g., `privatelink.vaultcore.azure.net`) are deployed and linked to the Virtual Network to resolve resource hostnames to their private IP addresses inside the `endpoints` subnet.
*   **Trusted Service Bypass:** Key Vaults are configured with network ACLs that bypass default-deny rules for trusted Azure services (`bypass = "AzureServices"`, `default_action = "Deny"`), allowing secure platform-level integrations (such as Application Gateway certificate fetching) while blocking all other traffic.

---

## 5. Subnet-Level Micro-segmentation (NSGs)

To enforce a zero-trust posture, every subnet is associated with a dedicated **Network Security Group (NSG)** enforcing strict micro-segmentation:

1.  **`nsg-appgw` (App Gateway Subnet):**
    *   Allows inbound HTTPS (443) and HTTP (80) from the internet.
    *   Allows inbound Gateway Manager traffic (ports 65200-65535) for Azure health probes.
    *   Denies all other inbound traffic.
2.  **`nsg-workloads` (Workloads Subnet):**
    *   Allows inbound HTTP/HTTPS from the `appgw` subnet only.
    *   Denies all other inbound traffic.
3.  **`nsg-endpoints` (Private Endpoints Subnet):**
    *   Allows inbound HTTPS (443) from the `workloads` and `runners` subnets only.
    *   Denies all other inbound traffic (preventing lateral movement from untrusted zones).
4.  **`nsg-runners` (Self-Hosted Runners Subnet - Enterprise Tier):**
    *   Allows outbound HTTPS (443) to the internet (via NAT Gateway) to communicate with GitHub/Azure DevOps.
    *   Denies all inbound traffic.

---

## 6. Centralized Diagnostic Logging

All network and infrastructure components are wired up to stream diagnostic logs and metrics to a centralized **Log Analytics Workspace**:

*   **NSG Flow Logs:** Network Security Groups stream `NetworkSecurityGroupEvent` and `NetworkSecurityGroupRuleCounter` logs to audit network traffic and rule evaluations.
*   **Key Vault Audit Logs:** Key Vault streams `AuditEvent` logs to track all secret, key, and certificate access operations.
*   **Application Gateway Logs:** Streams access logs, WAF firewall logs, and performance metrics to monitor application health and security events.
