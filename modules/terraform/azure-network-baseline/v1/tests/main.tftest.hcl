# Modern Terraform 1.6+ Test File

# Mocked provider so tests run offline (no Azure credentials in CI).
mock_provider "azurerm" {}

variables {
  project_name        = "testproj"
  location            = "westeurope"
  resource_group_name = "rg-test-network"
}

run "waf_v2_and_prevention_mode_enforced" {
  command = plan

  assert {
    condition     = azurerm_application_gateway.app_gateway.sku[0].name == "WAF_v2"
    error_message = "Application Gateway must use the WAF_v2 SKU (security baseline)"
  }

  assert {
    condition     = azurerm_application_gateway.app_gateway.sku[0].tier == "WAF_v2"
    error_message = "Application Gateway must use the WAF_v2 tier (security baseline)"
  }

  assert {
    condition     = azurerm_application_gateway.app_gateway.waf_configuration[0].enabled == true
    error_message = "WAF must be enabled on the Application Gateway"
  }

  assert {
    condition     = azurerm_application_gateway.app_gateway.waf_configuration[0].firewall_mode == "Prevention"
    error_message = "WAF must run in Prevention mode, not Detection"
  }
}

run "basic_tier_has_no_runner_resources" {
  command = plan

  assert {
    condition     = length(azurerm_subnet.runners) == 0
    error_message = "Runners subnet must not exist when is_enterprise is false"
  }

  assert {
    condition     = length(azurerm_network_security_group.runners) == 0
    error_message = "Runners NSG must not exist when is_enterprise is false"
  }
}

run "enterprise_tier_creates_runner_resources" {
  command = plan

  variables {
    is_enterprise = true
  }

  assert {
    condition     = length(azurerm_subnet.runners) == 1
    error_message = "Runners subnet must exist when is_enterprise is true"
  }

  assert {
    condition     = length(azurerm_network_security_group.runners) == 1
    error_message = "Runners NSG must exist when is_enterprise is true"
  }
}

run "no_diagnostics_without_workspace" {
  command = plan

  assert {
    condition     = length(azurerm_monitor_diagnostic_setting.appgw) == 0
    error_message = "No AppGW diagnostic setting expected when log_analytics_workspace_id is unset"
  }
}

run "diagnostics_created_with_workspace" {
  command = plan

  variables {
    log_analytics_workspace_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-x/providers/Microsoft.OperationalInsights/workspaces/law-x"
  }

  assert {
    condition     = length(azurerm_monitor_diagnostic_setting.appgw) == 1
    error_message = "AppGW diagnostic setting expected when log_analytics_workspace_id is set"
  }

  assert {
    condition     = length(azurerm_monitor_diagnostic_setting.nsg_workloads) == 1
    error_message = "Workloads NSG diagnostic setting expected when log_analytics_workspace_id is set"
  }
}
