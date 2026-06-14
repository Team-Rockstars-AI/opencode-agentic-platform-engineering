# Azure Private Runner Module

This module provisions an event-driven, scale-to-zero **Self-Hosted Runner Pool** using **Azure Container Apps** and **KEDA** within a private subnet.

## Features
- Runs standard **Ubuntu** base environments.
- Integrates KEDA scales to **zero** when idle.
- Uses User-Assigned Managed Identity for secure connection.
