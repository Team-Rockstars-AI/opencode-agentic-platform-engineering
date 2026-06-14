# Modern Terraform 1.6+ Test File

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
}
