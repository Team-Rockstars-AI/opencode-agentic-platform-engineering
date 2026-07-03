# Modern Terraform 1.6+ Test File

# Mocked provider so tests run offline (no Azure credentials in CI).
mock_provider "azurerm" {}

variables {
  project_name        = "testproj"
  location            = "westeurope"
  resource_group_name = "rg-test-runner"
  subnet_runners_id   = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-x/providers/Microsoft.Network/virtualNetworks/vnet-x/subnets/snet-runners"
}

run "scale_to_zero_enforced_by_default" {
  command = plan

  assert {
    condition     = azurerm_container_app.runner_app.template[0].min_replicas == 0
    error_message = "Runners must scale to zero when idle (min_replicas = 0)"
  }
}

run "runner_environment_is_internal_only" {
  command = plan

  assert {
    condition     = azurerm_container_app_environment.runner_env.internal_load_balancer_enabled == true
    error_message = "Runner environment must use an internal load balancer (no public exposure)"
  }
}

run "no_diagnostics_without_workspace" {
  command = plan

  assert {
    condition     = length(azurerm_monitor_diagnostic_setting.runner_env) == 0
    error_message = "No environment diagnostic setting expected when log_analytics_workspace_id is unset"
  }
}

run "diagnostics_created_with_workspace" {
  command = plan

  variables {
    log_analytics_workspace_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-x/providers/Microsoft.OperationalInsights/workspaces/law-x"
  }

  assert {
    condition     = length(azurerm_monitor_diagnostic_setting.runner_env) == 1
    error_message = "Environment diagnostic setting expected when log_analytics_workspace_id is set"
  }

  assert {
    condition     = length(azurerm_monitor_diagnostic_setting.runner_app) == 1
    error_message = "Container app diagnostic setting expected when log_analytics_workspace_id is set"
  }
}
