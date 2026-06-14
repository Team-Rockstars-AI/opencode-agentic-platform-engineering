output "resource_group_name" {
  value       = azurerm_resource_group.core.name
  description = "The name of the core resource group"
}

output "log_analytics_workspace_id" {
  value       = azurerm_log_analytics_workspace.ops.id
  description = "The workspace ID of the Log Analytics workspace"
}

output "key_vault_uri" {
  value       = azurerm_key_vault.kv.vault_uri
  description = "The URI of the key vault"
}
