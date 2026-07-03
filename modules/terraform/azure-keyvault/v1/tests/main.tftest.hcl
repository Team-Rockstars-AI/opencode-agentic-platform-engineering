# Modern Terraform 1.6+ Test File

# Mocked provider so tests run offline (no Azure credentials in CI).
mock_provider "azurerm" {}

variables {
  name                = "kv-test-vault"
  resource_group_name = "rg-test-vault"
  location            = "eastus2"
  tenant_id           = "00000000-0000-0000-0000-000000000000"
}

run "validate_key_vault_names" {
  command = plan

  assert {
    condition     = azurerm_key_vault.kv.name == var.name
    error_message = "Key Vault name did not match expected value"
  }

  assert {
    condition     = azurerm_key_vault.kv.enable_rbac_authorization == true
    error_message = "Key Vault must have RBAC authorization enabled by default"
  }

  assert {
    condition     = length(azurerm_monitor_diagnostic_setting.kv) == 0
    error_message = "No diagnostic setting expected when log_analytics_workspace_id is unset"
  }
}

run "diagnostics_created_with_workspace" {
  command = plan

  variables {
    log_analytics_workspace_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-x/providers/Microsoft.OperationalInsights/workspaces/law-x"
  }

  assert {
    condition     = length(azurerm_monitor_diagnostic_setting.kv) == 1
    error_message = "Diagnostic setting expected when log_analytics_workspace_id is set"
  }
}
