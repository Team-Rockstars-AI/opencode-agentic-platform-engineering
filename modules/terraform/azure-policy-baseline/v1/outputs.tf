output "policy_assignment_ids" {
  description = "Map of policy short-name to assignment resource ID"
  value = merge(
    {
      allowed_locations         = azurerm_subscription_policy_assignment.allowed_locations.id
      storage_secure_transfer   = azurerm_subscription_policy_assignment.storage_secure_transfer.id
      storage_no_public_access  = azurerm_subscription_policy_assignment.storage_no_public_access.id
      keyvault_no_public_access = azurerm_subscription_policy_assignment.keyvault_no_public_access.id
      keyvault_purge_protection = azurerm_subscription_policy_assignment.keyvault_purge_protection.id
    },
    var.enable_deny_public_ip_nics ? {
      nic_no_public_ip = azurerm_subscription_policy_assignment.nic_no_public_ip[0].id
    } : {}
  )
}
