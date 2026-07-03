# Azure Network Baseline Module

This module establishes a highly secure **Secure-by-Design Hub/Spoke ready Network Baseline** for Azure Landing Zones.

## Components
- **Virtual Network** with micro-segmented subnets (Workloads, Inbound App Gateway, Endpoints, and scale-to-zero Runners).
- **NAT Gateway** for outbound-only internet connectivity (no public IPs on workloads).
- **Application Gateway v2 + WAF v2** for secure inbound reverse proxying.

## Application Gateway Autoscaling Inputs

| Name | Type | Description | Default | Required |
|------|------|-------------|---------|:--------:|
| appgw_autoscale_min_capacity | number | Minimum instance count for Application Gateway autoscaling (0–100) | `1` | no |
| appgw_autoscale_max_capacity | number | Maximum instance count for Application Gateway autoscaling (2–125) | `3` | no |

The gateway uses `autoscale_configuration` instead of a fixed `capacity`, per the cost-governance guide (dev/test: 1–2 instances, prod: 2–10).
