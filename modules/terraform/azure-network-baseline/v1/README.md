# Azure Network Baseline Module

This module establishes a highly secure **Secure-by-Design Hub/Spoke ready Network Baseline** for Azure Landing Zones.

## Components
- **Virtual Network** with micro-segmented subnets (Workloads, Inbound App Gateway, Endpoints, and scale-to-zero Runners).
- **NAT Gateway** for outbound-only internet connectivity (no public IPs on workloads).
- **Application Gateway v2 + WAF v2** for secure inbound reverse proxying.
