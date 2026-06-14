# Core resource group
resource "azurerm_resource_group" "core" {
  name     = "rg-${var.project_name}-${var.environment}-${var.location}"
  location = var.location
  tags = {
    Environment    = var.environment
    ManagedBy      = "OpenCode-Platform-Engineer"
    Project        = var.project_name
    GovernanceTier = var.governance_tier
  }
}

# Centralized Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "ops" {
  name                = "law-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.core.location
  resource_group_name = azurerm_resource_group.core.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# Secure Network Baseline Subnets, NAT Gateway & App Gateway
module "network" {
  source              = "../../modules/terraform/azure-network-baseline/v1"
  project_name        = var.project_name
  environment         = var.environment
  location            = var.location
  resource_group_name = azurerm_resource_group.core.name
  is_enterprise       = var.governance_tier == "enterprise"
  tags                = azurerm_resource_group.core.tags
}

# Secure Key Vault for Platform Secrets (Private Endpoint enabled)
resource "azurerm_key_vault" "kv" {
  name                        = "kv-${var.project_name}-${var.environment}"
  location                    = azurerm_resource_group.core.location
  resource_group_name         = azurerm_resource_group.core.name
  enabled_for_disk_encryption = true
  tenant_id                   = var.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = true # Secure-by-design baseline
  enable_rbac_authorization   = true

  sku_name = "standard"

  # Secure-by-design: Restrict public network access
  public_network_access_enabled = false

  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny"
  }
}

# Private Endpoint for Key Vault inside snet-endpoints
resource "azurerm_private_endpoint" "kv_pe" {
  name                = "pe-kv-${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = azurerm_resource_group.core.name
  subnet_id           = module.network.subnet_endpoints_id

  private_service_connection {
    name                           = "psc-kv-${var.project_name}-${var.environment}"
    private_connection_resource_id = azurerm_key_vault.kv.id
    is_manual_connection           = false
    subresource_names              = ["vault"]
  }
}

# Key Vault Diagnostic settings streaming to Law Workspace
resource "azurerm_monitor_diagnostic_setting" "kv_diagnostics" {
  name                       = "ds-kv-${var.project_name}-${var.environment}"
  target_resource_id         = azurerm_key_vault.kv.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.ops.id

  enabled_log {
    category = "AuditEvent"
  }

  metric {
    category = "AllMetrics"
  }
}

# Self-Hosted KEDA-scaled Container App Runner (Enterprise Tier Only)
module "runners" {
  count               = var.governance_tier == "enterprise" ? 1 : 0
  source              = "../../modules/terraform/azure-private-runner/v1"
  project_name        = var.project_name
  environment         = var.environment
  location            = var.location
  resource_group_name = azurerm_resource_group.core.name
  subnet_runners_id   = module.network.subnet_runners_id
  github_org_name     = var.github_org_name
  github_repo_name    = var.github_repo_name
  runner_token        = var.runner_token
  tags                = azurerm_resource_group.core.tags
}
