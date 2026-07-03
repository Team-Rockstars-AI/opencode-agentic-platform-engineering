# Azure Network Baseline Module (Bicep)

This module deploys a secure subnet network topology integrating an Azure NAT Gateway and an Application Gateway with WAF v2.

## Application Gateway Autoscaling Inputs

| Name | Type | Description | Default | Required |
|------|------|-------------|---------|:--------:|
| appgwAutoscaleMinCapacity | int | Minimum instance count for Application Gateway autoscaling (0–100) | `1` | no |
| appgwAutoscaleMaxCapacity | int | Maximum instance count for Application Gateway autoscaling (2–125) | `3` | no |

The gateway uses `autoscaleConfiguration` instead of a fixed `capacity`, per the cost-governance guide (dev/test: 1–2 instances, prod: 2–10).
