resource "azurerm_key_vault" "kv" {
  name                        = var.name
  location                    = var.location
  resource_group_name         = var.resource_group_name
  tenant_id                   = var.tenant_id
  sku_name                    = var.sku_name
  soft_delete_retention_days  = var.soft_delete_retention_days
  purge_protection_enabled    = var.purge_protection_enabled
  enable_rbac_authorization   = true
  enabled_for_disk_encryption = true
  public_network_access_enabled = var.public_network_access_enabled

  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny"
  }

  tags = {
    Module = "terraform-azure-keyvault"
    Version = "v1"
  }
}
